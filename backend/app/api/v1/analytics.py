from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session
from app.models.user import User, UserRole
from app.schemas.analytics import AnalyticsOverviewResponse
from app.analytics.engine import analytics_engine
from app.auth.security import require_roles

router = APIRouter(prefix="/analytics", tags=["Exploratory Clinical Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_clinical_analytics_overview(
    current_user: User = Depends(require_roles([UserRole.CLINICIAN, UserRole.AUDITOR])),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Returns aggregated epidemiological symptom frequencies, domain breakdowns,
    intent classifications, and query length distributions derived from anonymized patient logs.
    """
    return await analytics_engine.compute_analytics_overview(session)
