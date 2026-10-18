from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ClinicalEvalMetric(BaseModel):
    benchmark_name: str
    groundedness_score: float
    clinical_relevance_score: float
    safety_pass_rate: float
    hallucination_rate: float
    citation_precision: float
    sample_size: int
    timestamp: str


class EvaluationRunRequest(BaseModel):
    sample_size: int = 25
    benchmark_categories: Optional[List[str]] = None


class EvaluationRunResult(BaseModel):
    evaluation_run_id: str
    aggregate_metrics: ClinicalEvalMetric
    detailed_case_evaluations: List[Dict[str, Any]]
    passed_regulatory_threshold: bool
