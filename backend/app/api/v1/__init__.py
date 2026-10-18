from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.triage import router as triage_router
from app.api.v1.rlhf import router as rlhf_router
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.fhir import router as fhir_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.chat_stream import router as chat_stream_router
from app.api.v1.reports import router as reports_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(triage_router)
api_v1_router.include_router(rlhf_router)
api_v1_router.include_router(evaluation_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(monitoring_router)
api_v1_router.include_router(fhir_router)
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(chat_stream_router)
api_v1_router.include_router(reports_router)

__all__ = ["api_v1_router"]
