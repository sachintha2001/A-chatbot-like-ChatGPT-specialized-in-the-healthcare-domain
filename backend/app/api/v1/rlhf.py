from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.models.user import User, UserRole
from app.models.triage import TriageMessage, MessageSenderRole
from app.models.rlhf import RLHFFeedbackRecord, FeedbackExportStatus
from app.models.audit import AuditActionType, ComplianceStatus
from app.schemas.rlhf import (
    RLHFReviewSubmission,
    RLHFReviewItem,
    RLHFPendingItem,
    FineTuneExportFormatRequest,
)
from app.auth.security import require_roles, get_current_user
from app.compliance.audit_logger import audit_logger
from app.engine.rlhf_dataset_generator import rlhf_export_engine

router = APIRouter(prefix="/rlhf", tags=["Clinician RLHF Review & Alignment"])


@router.get("/queue", response_model=List[RLHFPendingItem])
async def get_rlhf_pending_queue(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_roles([UserRole.CLINICIAN, UserRole.AUDITOR])),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Retrieves unreviewed model assistant responses for verified clinician review.
    """
    # Fetch assistant messages that have no feedback record attached
    reviewed_msg_ids_stmt = select(RLHFFeedbackRecord.message_id)
    reviewed_res = await session.execute(reviewed_msg_ids_stmt)
    reviewed_ids = set(reviewed_res.scalars().all())

    stmt = (
        select(TriageMessage)
        .options(selectinload(TriageMessage.session).selectinload(TriageMessage.session.property.mapper.class_.messages))
        .where(
            TriageMessage.sender_role == MessageSenderRole.CLINICIAN_ASSISTANT,
            ~TriageMessage.message_id.in_(reviewed_ids) if reviewed_ids else True
        )
        .order_by(TriageMessage.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    assistant_messages = result.scalars().all()

    queue_items: List[RLHFPendingItem] = []
    for msg in assistant_messages:
        patient_query = "Clinical intake presentation"
        if msg.session_id:
            p_stmt = (
                select(TriageMessage.redacted_content)
                .where(
                    TriageMessage.session_id == msg.session_id,
                    TriageMessage.sender_role == MessageSenderRole.PATIENT,
                    TriageMessage.created_at <= msg.created_at
                )
                .order_by(TriageMessage.created_at.desc())
                .limit(1)
            )
            p_res = await session.execute(p_stmt)
            match_txt = p_res.scalar_one_or_none()
            if match_txt:
                patient_query = match_txt

        queue_items.append(
            RLHFPendingItem(
                message_id=msg.message_id,
                session_id=msg.session_id,
                patient_query_redacted=patient_query,
                assistant_response=msg.redacted_content,
                clinical_citations=msg.clinical_citations or [],
                groundedness_score=msg.groundedness_score,
                retrieval_similarity_score=msg.retrieval_similarity_score,
                created_at=msg.created_at.isoformat()
            )
        )

    return queue_items


@router.post("/review", status_code=status.HTTP_201_CREATED)
async def submit_clinician_review(
    payload: RLHFReviewSubmission,
    current_user: User = Depends(require_roles([UserRole.CLINICIAN])),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Records clinician rating (1-5 Likert), alignment error flags, and optional rewritten ground truth.
    """
    stmt = select(TriageMessage).where(TriageMessage.message_id == payload.message_id)
    res = await session.execute(stmt)
    msg = res.scalar_one_or_none()
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Triage message targeted for review does not exist"
        )

    # Check if this message was already reviewed by this clinician
    existing_stmt = select(RLHFFeedbackRecord).where(
        RLHFFeedbackRecord.message_id == payload.message_id,
        RLHFFeedbackRecord.clinician_id == current_user.id
    )
    exist_res = await session.execute(existing_stmt)
    if exist_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already submitted a clinical alignment review for this interaction"
        )

    feedback = RLHFFeedbackRecord(
        message_id=payload.message_id,
        clinician_id=current_user.id,
        clinical_accuracy_rating=payload.clinical_accuracy_rating,
        hallucination_flag=payload.hallucination_flag,
        safety_guideline_violation=payload.safety_guideline_violation,
        omission_of_red_flag_symptom=payload.omission_of_red_flag_symptom,
        revised_completion_text=payload.revised_completion_text,
        clinician_notes=payload.clinician_notes,
        export_status=payload.export_status
    )
    session.add(feedback)
    await session.commit()
    await session.refresh(feedback)

    await audit_logger.log_event(
        session=session,
        action_type=AuditActionType.CLINICIAN_RLHF_SUBMISSION,
        resource_accessed=f"/rlhf/review/{feedback.feedback_id}",
        user_id=current_user.id,
        compliance_status=ComplianceStatus.COMPLIANT,
        metadata={
            "accuracy_rating": payload.clinical_accuracy_rating,
            "hallucination": payload.hallucination_flag,
            "rewritten": bool(payload.revised_completion_text)
        }
    )

    return {
        "status": "SUCCESS",
        "feedback_id": feedback.feedback_id,
        "export_status": feedback.export_status.value
    }


@router.get("/reviews", response_model=List[RLHFReviewItem])
async def list_clinician_reviews(
    min_rating: Optional[int] = Query(default=None, ge=1, le=5),
    export_status: Optional[FeedbackExportStatus] = None,
    current_user: User = Depends(require_roles([UserRole.CLINICIAN, UserRole.AUDITOR])),
    session: AsyncSession = Depends(get_db_session)
):
    stmt = (
        select(RLHFFeedbackRecord)
        .options(
            selectinload(RLHFFeedbackRecord.clinician),
            selectinload(RLHFFeedbackRecord.message).selectinload(TriageMessage.session)
        )
    )

    if min_rating is not None:
        stmt = stmt.where(RLHFFeedbackRecord.clinical_accuracy_rating >= min_rating)
    if export_status is not None:
        stmt = stmt.where(RLHFFeedbackRecord.export_status == export_status)

    stmt = stmt.order_by(RLHFFeedbackRecord.created_at.desc())
    res = await session.execute(stmt)
    records = res.scalars().all()

    items: List[RLHFReviewItem] = []
    for r in records:
        msg = r.message
        prompt_txt = "Clinical presentation"
        if msg and msg.session_id:
            p_stmt = (
                select(TriageMessage.redacted_content)
                .where(
                    TriageMessage.session_id == msg.session_id,
                    TriageMessage.sender_role == MessageSenderRole.PATIENT,
                    TriageMessage.created_at <= msg.created_at
                )
                .order_by(TriageMessage.created_at.desc())
                .limit(1)
            )
            p_res = await session.execute(p_stmt)
            match_txt = p_res.scalar_one_or_none()
            if match_txt:
                prompt_txt = match_txt

        items.append(
            RLHFReviewItem(
                feedback_id=r.feedback_id,
                message_id=r.message_id,
                clinician_id=r.clinician_id,
                clinician_name=r.clinician.full_name if r.clinician else "Verified Clinician",
                clinical_accuracy_rating=r.clinical_accuracy_rating,
                hallucination_flag=r.hallucination_flag,
                safety_guideline_violation=r.safety_guideline_violation,
                omission_of_red_flag_symptom=r.omission_of_red_flag_symptom,
                revised_completion_text=r.revised_completion_text,
                clinician_notes=r.clinician_notes,
                export_status=r.export_status,
                prompt_text=prompt_txt,
                original_model_output=msg.redacted_content if msg else "",
                citations=msg.clinical_citations if msg else [],
                created_at=r.created_at.isoformat()
            )
        )

    return items


@router.post("/export")
async def export_rlhf_finetuning_dataset(
    payload: FineTuneExportFormatRequest,
    current_user: User = Depends(require_roles([UserRole.CLINICIAN, UserRole.AUDITOR])),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Exports verified clinician prompt-completion pairs in OpenAI Chat or Llama Alpaca JSONL fine-tuning format.
    """
    dataset = await rlhf_export_engine.export_dataset(
        session=session,
        format_type=payload.format_type,
        minimum_rating=payload.minimum_rating,
        include_system_guardrails=payload.include_system_guardrails
    )

    await audit_logger.log_event(
        session=session,
        action_type=AuditActionType.FINETUNE_DATASET_EXPORT,
        resource_accessed="/rlhf/export",
        user_id=current_user.id,
        compliance_status=ComplianceStatus.COMPLIANT,
        metadata={"record_count": len(dataset), "format": payload.format_type}
    )

    return {
        "status": "SUCCESS",
        "format": payload.format_type,
        "sample_count": len(dataset),
        "data": dataset
    }
