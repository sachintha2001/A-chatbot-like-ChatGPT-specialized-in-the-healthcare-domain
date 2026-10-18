from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.models.user import User, UserRole
from app.models.triage import TriageSession
from app.models.audit import AuditActionType, ComplianceStatus
from app.integrations.fhir_export import fhir_generator
from app.auth.security import require_roles
from app.compliance.audit_logger import audit_logger

router = APIRouter(prefix="/fhir", tags=["EHR Interoperability (HL7 FHIR R4)"])


@router.get("/PatientSummary/{session_id}")
async def export_fhir_patient_summary(
    session_id: str,
    current_user: User = Depends(require_roles([UserRole.CLINICIAN, UserRole.AUDITOR])),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Exports a completed clinical triage session as a standardized HL7 FHIR R4 Document Bundle.
    Includes Composition, Anonymized Patient, Observation (Acuity Level), and Guideline Citations.
    """
    stmt = (
        select(TriageSession)
        .options(selectinload(TriageSession.messages))
        .where(TriageSession.session_id == session_id)
    )
    res = await session.execute(stmt)
    triage_session = res.scalar_one_or_none()

    if not triage_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Triage session not found for FHIR export"
        )

    bundle = fhir_generator.generate_patient_summary_bundle(
        triage_session=triage_session,
        messages=triage_session.messages
    )

    await audit_logger.log_event(
        session=session,
        action_type=AuditActionType.FHIR_PATIENT_SUMMARY_ACCESS,
        resource_accessed=f"/fhir/PatientSummary/{session_id}",
        user_id=current_user.id,
        compliance_status=ComplianceStatus.COMPLIANT,
        metadata={"bundle_id": bundle["id"], "severity": triage_session.triage_severity.value}
    )

    return Response(
        content=import_json(bundle),
        media_type="application/fhir+json"
    )


def import_json(data: dict) -> str:
    import json
    return json.dumps(data, indent=2)
