import time
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db_session, utc_now
from app.models.user import User
from app.models.triage import (
    TriageSession,
    TriageMessage,
    TriageSeverity,
    MessageSenderRole,
)
from app.models.audit import AuditActionType, ComplianceStatus
from app.schemas.triage import (
    SessionInitRequest,
    SessionResponse,
    TriagePromptRequest,
    TriageMessageResponse,
    ClinicalCitation,
    EmergencyEscalationInfo,
)
from app.auth.security import get_current_user_optional
from app.compliance.red_flag_detector import red_flag_detector
from app.compliance.phi_scrubber import phi_scrubber
from app.compliance.audit_logger import audit_logger
from app.engine.rag_pipeline import rag_engine

router = APIRouter(prefix="/triage", tags=["Clinical Triage & Patient Encounters"])


@router.post("/session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def initialize_triage_session(
    payload: SessionInitRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_db_session)
):
    # Statutory consent and assistive disclaimer are mandatory before patient intake
    if not payload.consent_acknowledged or not payload.disclaimer_acknowledged:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent acknowledgment and clinical disclaimer acceptance are legally required to initiate triage"
        )

    client_ip = request.client.host if request.client else "127.0.0.1"

    triage_sess = TriageSession(
        user_id=current_user.id if current_user else None,
        patient_age_group=payload.patient_age_group.upper(),
        biological_sex=payload.biological_sex.upper(),
        consent_acknowledged=True,
        disclaimer_acknowledged=True,
        consent_timestamp=utc_now(),
        triage_severity=TriageSeverity.ROUTINE,
        emergency_escalated=False
    )
    session.add(triage_sess)
    await session.commit()
    await session.refresh(triage_sess)

    await audit_logger.log_event(
        session=session,
        action_type=AuditActionType.AUTHENTICATION_EVENT,
        resource_accessed=f"/triage/session/{triage_sess.session_id}",
        user_id=current_user.id if current_user else None,
        client_ip=client_ip,
        compliance_status=ComplianceStatus.COMPLIANT,
        metadata={"age_group": triage_sess.patient_age_group, "sex": triage_sess.biological_sex}
    )

    return SessionResponse(
        session_id=triage_sess.session_id,
        patient_age_group=triage_sess.patient_age_group,
        biological_sex=triage_sess.biological_sex,
        consent_acknowledged=triage_sess.consent_acknowledged,
        disclaimer_acknowledged=triage_sess.disclaimer_acknowledged,
        emergency_escalated=triage_sess.emergency_escalated,
        escalation_reason=triage_sess.escalation_reason,
        triage_severity=triage_sess.triage_severity,
        created_at=triage_sess.created_at.isoformat()
    )


@router.get("/session/{session_id}")
async def get_triage_session_history(
    session_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    stmt = (
        select(TriageSession)
        .options(selectinload(TriageSession.messages))
        .where(TriageSession.session_id == session_id)
    )
    res = await session.execute(stmt)
    sess = res.scalar_one_or_none()
    if not sess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Triage session identifier not found in clinical registry"
        )

    return {
        "session_id": sess.session_id,
        "patient_age_group": sess.patient_age_group,
        "biological_sex": sess.biological_sex,
        "consent_acknowledged": sess.consent_acknowledged,
        "emergency_escalated": sess.emergency_escalated,
        "escalation_reason": sess.escalation_reason,
        "triage_severity": sess.triage_severity.value,
        "created_at": sess.created_at.isoformat(),
        "messages": [
            {
                "message_id": m.message_id,
                "sender_role": m.sender_role.value,
                "redacted_content": m.redacted_content,
                "clinical_citations": m.clinical_citations,
                "retrieval_similarity_score": m.retrieval_similarity_score,
                "groundedness_score": m.groundedness_score,
                "latency_ms": m.latency_ms,
                "created_at": m.created_at.isoformat()
            }
            for m in sess.messages
        ]
    }


@router.post("/prompt", response_model=TriageMessageResponse)
async def process_triage_prompt(
    payload: TriagePromptRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_db_session)
):
    start_total_time = time.perf_counter()
    client_ip = request.client.host if request.client else "127.0.0.1"

    # 1. Verify active session
    stmt = select(TriageSession).where(TriageSession.session_id == payload.session_id)
    res = await session.execute(stmt)
    triage_sess = res.scalar_one_or_none()

    if not triage_sess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active triage session not found. Please initiate a clinical intake session first."
        )

    # 2. PHI / PII Scrubbing prior to storage and inference
    redacted_prompt, scrubbed_entities = phi_scrubber.redact(payload.prompt_text)

    # Record patient query message in database with scrubbed text only
    patient_msg = TriageMessage(
        session_id=triage_sess.session_id,
        sender_role=MessageSenderRole.PATIENT,
        redacted_content=redacted_prompt,
        redacted_entity_types=scrubbed_entities,
        clinical_citations=[],
        retrieval_similarity_score=1.0,
        groundedness_score=1.0,
        latency_ms=0,
        safety_check_passed=True
    )
    session.add(patient_msg)

    # 3. Deterministic Pre-Inference Red-Flag Triage Evaluation (including normalized Singlish/typo tokens)
    from app.engine.llm_connector import hybrid_llm_connector
    nlu_info = hybrid_llm_connector.normalize_complex_patient_narrative(redacted_prompt)
    is_emergency, matched_flags, directive, hotlines = red_flag_detector.evaluate(
        nlu_info["normalized_clinical_query"] or redacted_prompt, preferred_language=payload.language
    )

    if is_emergency:
        triage_sess.emergency_escalated = True
        triage_sess.triage_severity = TriageSeverity.EMERGENCY
        triage_sess.escalation_reason = f"Deterministic red flags triggered: {', '.join(matched_flags)}"

        is_si = payload.language == "si" or red_flag_detector.is_sinhala(redacted_prompt)
        if is_si:
            emergency_text = (
                f"තීරණාත්මක සායනික අනතුරු ඇඟවීමයි: වහාම වෛද්‍ය ප්‍රතිකාර අවශ්‍ය වේ.\n\n"
                f"ඔබ සඳහන් කළ රෝග ලක්ෂණ ජීවිත අනතුරුදායක හදිසි තත්ත්වයන් ({', '.join(matched_flags)}) සමඟ සෘජුව ගැළපේ.\n\n"
                f"සායනික උපදෙස: {directive}\n\n"
                f"වහාම හදිසි ගිලන්රථ සේවාව අමතන්න:\n"
                f"ශ්‍රී ලංකාව: {hotlines.get('Sri_Lanka_Suwa_Seriya', '1990')} (සුවසැරිය) | ජාතික මානසික සුව සේවය: {hotlines.get('Sri_Lanka_Mental_Health', '1926')}\n"
                f"UK: {hotlines['UK_Emergency']} | US/Canada: {hotlines['US_Canada_Emergency']} | EU: {hotlines['EU_Emergency']}"
            )
        else:
            emergency_text = (
                f"CRITICAL CLINICAL ALERT: IMMEDIATE MEDICAL ATTENTION REQUIRED.\n\n"
                f"Your reported symptoms triggered high-acuity emergency red flags ({', '.join(matched_flags)}). "
                f"\n\nDirective: {directive}\n\n"
                f"Please call emergency rescue services immediately: "
                f"US/Canada: {hotlines['US_Canada_Emergency']} | UK: {hotlines['UK_Emergency']} | EU: {hotlines['EU_Emergency']}. "
                f"If in mental distress: Suicide Lifeline {hotlines['Suicide_Crisis_Lifeline']}."
            )

        total_latency = int((time.perf_counter() - start_total_time) * 1000)

        assistant_msg = TriageMessage(
            session_id=triage_sess.session_id,
            sender_role=MessageSenderRole.CLINICIAN_ASSISTANT,
            redacted_content=emergency_text,
            redacted_entity_types=[],
            clinical_citations=[],
            retrieval_similarity_score=1.0,
            groundedness_score=1.0,
            latency_ms=total_latency,
            safety_check_passed=True
        )
        session.add(assistant_msg)
        await session.commit()
        await session.refresh(assistant_msg)

        await audit_logger.log_event(
            session=session,
            action_type=AuditActionType.EMERGENCY_TRIAGE_ESCALATION,
            resource_accessed=f"/triage/prompt/{triage_sess.session_id}",
            user_id=current_user.id if current_user else None,
            client_ip=client_ip,
            compliance_status=ComplianceStatus.ESCALATED,
            metadata={"matched_red_flags": matched_flags, "severity": "EMERGENCY"}
        )

        return TriageMessageResponse(
            message_id=assistant_msg.message_id,
            session_id=triage_sess.session_id,
            sender_role=MessageSenderRole.CLINICIAN_ASSISTANT,
            redacted_content=assistant_msg.redacted_content,
            clinical_citations=[],
            retrieval_similarity_score=1.0,
            groundedness_score=1.0,
            latency_ms=total_latency,
            safety_check_passed=True,
            emergency_info=EmergencyEscalationInfo(
                is_emergency=True,
                matched_red_flags=matched_flags,
                escalation_directive=directive,
                hotline_numbers=hotlines
            ),
            triage_severity=TriageSeverity.EMERGENCY,
            created_at=assistant_msg.created_at.isoformat()
        )

    # 4. If not emergency, invoke Evidence-Grounded Hybrid RAG + Cloud LLM Pipeline
    response_text, citations, similarity_score, groundedness_score, rag_latency = await rag_engine.generate_clinical_response_async(
        patient_query=redacted_prompt,
        age_group=triage_sess.patient_age_group,
        biological_sex=triage_sess.biological_sex,
        top_k=3,
        preferred_language=payload.language
    )

    # Determine severity
    determined_severity = TriageSeverity.ROUTINE
    for c in citations:
        if "URGENT" in c.matched_snippet.upper() or "Level II" in c.evidence_level:
            determined_severity = TriageSeverity.URGENT

    triage_sess.triage_severity = determined_severity
    total_latency = int((time.perf_counter() - start_total_time) * 1000)

    assistant_msg = TriageMessage(
        session_id=triage_sess.session_id,
        sender_role=MessageSenderRole.CLINICIAN_ASSISTANT,
        redacted_content=response_text,
        redacted_entity_types=[],
        clinical_citations=[c.model_dump() for c in citations],
        retrieval_similarity_score=similarity_score,
        groundedness_score=groundedness_score,
        latency_ms=total_latency,
        safety_check_passed=True
    )
    session.add(assistant_msg)
    await session.commit()
    await session.refresh(assistant_msg)

    # Audit log scrubbing event
    if scrubbed_entities:
        await audit_logger.log_event(
            session=session,
            action_type=AuditActionType.PHI_SCRUB_EVENT,
            resource_accessed=f"/triage/prompt/{triage_sess.session_id}",
            user_id=current_user.id if current_user else None,
            client_ip=client_ip,
            compliance_status=ComplianceStatus.COMPLIANT,
            metadata={"scrubbed_entity_types": scrubbed_entities}
        )

    return TriageMessageResponse(
        message_id=assistant_msg.message_id,
        session_id=triage_sess.session_id,
        sender_role=MessageSenderRole.CLINICIAN_ASSISTANT,
        redacted_content=assistant_msg.redacted_content,
        clinical_citations=citations,
        retrieval_similarity_score=similarity_score,
        groundedness_score=groundedness_score,
        latency_ms=total_latency,
        safety_check_passed=True,
        emergency_info=None,
        triage_severity=determined_severity,
        created_at=assistant_msg.created_at.isoformat()
    )
