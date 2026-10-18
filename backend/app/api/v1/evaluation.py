from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db_session
from app.models.user import User, UserRole
from app.models.monitoring import MonitoringMetric, MetricCategory
from app.schemas.evaluation import EvaluationRunResult, EvaluationRunRequest
from app.evaluation.evaluator import evaluation_runner
from app.evaluation.benchmarks import CLINICAL_EVALUATION_BENCHMARKS
from app.auth.security import require_roles

router = APIRouter(prefix="/evaluation", tags=["Clinical Model Evaluation & Benchmarks"])


@router.post("/run", response_model=EvaluationRunResult)
async def trigger_evaluation_benchmark_run(
    payload: EvaluationRunRequest = EvaluationRunRequest(),
    current_user: User = Depends(require_roles([UserRole.CLINICIAN, UserRole.AUDITOR])),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Executes standardized clinical validation vignettes against the CDSS RAG pipeline.
    Calculates claim groundedness, clinical relevance, safety compliance, and hallucination rates.
    """
    # Select benchmark cases
    cases = CLINICAL_EVALUATION_BENCHMARKS[:payload.sample_size]
    result = await evaluation_runner.execute_benchmark_suite(
        session=session,
        benchmark_cases=cases
    )
    return result


@router.get("/benchmarks")
async def get_registered_benchmarks(
    current_user: User = Depends(require_roles([UserRole.CLINICIAN, UserRole.AUDITOR]))
):
    return {
        "benchmark_suite": "MedGuard Multi-Domain Clinical Vignettes",
        "total_cases": len(CLINICAL_EVALUATION_BENCHMARKS),
        "cases": CLINICAL_EVALUATION_BENCHMARKS
    }


@router.get("/history")
async def get_evaluation_history(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(require_roles([UserRole.CLINICIAN, UserRole.AUDITOR])),
    session: AsyncSession = Depends(get_db_session)
):
    stmt = (
        select(MonitoringMetric)
        .where(MonitoringMetric.metric_category == MetricCategory.RETRIEVAL_SIMILARITY)
        .order_by(MonitoringMetric.timestamp.desc())
        .limit(limit)
    )
    res = await session.execute(stmt)
    records = res.scalars().all()

    history = []
    for r in records:
        ctx = r.diagnostic_context or {}
        history.append({
            "metric_id": r.metric_id,
            "timestamp": r.timestamp.isoformat(),
            "mean_groundedness": r.metric_value,
            "safety_pass_rate": ctx.get("safety_pass_rate", 1.0),
            "relevance_score": ctx.get("relevance_score", 0.9),
            "hallucination_rate": ctx.get("hallucination_rate", 0.0),
            "severity": r.severity_level.value
        })

    return history
