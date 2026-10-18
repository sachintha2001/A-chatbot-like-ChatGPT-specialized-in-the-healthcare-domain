from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session
from app.models.user import User, UserRole
from app.schemas.monitoring import MonitoringStatusResponse
from app.monitoring.service import monitoring_service
from app.auth.security import require_roles

router = APIRouter(prefix="/monitoring", tags=["Safety, Drift & Guideline Monitoring"])


@router.get("/status", response_model=MonitoringStatusResponse)
async def get_system_monitoring_status(
    current_user: User = Depends(require_roles([UserRole.CLINICIAN, UserRole.AUDITOR])),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Returns real-time health metrics including retrieval confidence drift,
    hallucination rates, guideline currency audits, and proactive risk alerts.
    """
    return await monitoring_service.get_system_monitoring_status(session)
