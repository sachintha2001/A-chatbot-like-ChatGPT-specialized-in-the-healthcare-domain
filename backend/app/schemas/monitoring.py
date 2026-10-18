from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.models.monitoring import MetricCategory, MetricSeverity


class DriftAlertItem(BaseModel):
    alert_id: str
    timestamp: str
    category: MetricCategory
    severity: MetricSeverity
    description: str
    metric_value: float
    threshold: float
    recommended_action: str


class GuidelineCatalogItem(BaseModel):
    guideline_id: str
    source_title: str
    issuing_authority: str
    clinical_domain: str
    evidence_level: str
    publication_year: int
    source_url: str
    icd10_codes: List[str]
    chunk_count: int
    is_active: bool
    last_reviewed_at: str


class MonitoringStatusResponse(BaseModel):
    system_health: str
    active_alerts: List[DriftAlertItem]
    retrieval_similarity_moving_avg: float
    low_confidence_query_rate: float
    hallucination_flag_rate: float
    p95_latency_ms: float
    total_guidelines_indexed: int
    guidelines_catalog: List[GuidelineCatalogItem]
