from typing import List, Dict, Any
from pydantic import BaseModel


class SymptomDistributionItem(BaseModel):
    symptom_category: str
    frequency_count: int
    triage_urgency_ratio: Dict[str, float]


class ClinicalDomainQueryStats(BaseModel):
    clinical_domain: str
    query_count: int
    mean_similarity_score: float
    groundedness_index: float


class IntentDistributionItem(BaseModel):
    intent_label: str
    percentage: float
    count: int


class TokenDistributionBin(BaseModel):
    token_range: str
    frequency: int


class AnalyticsOverviewResponse(BaseModel):
    total_triage_sessions: int
    total_messages_processed: int
    emergency_escalations_count: int
    emergency_escalation_rate_pct: float
    symptom_frequencies: List[SymptomDistributionItem]
    domain_breakdown: List[ClinicalDomainQueryStats]
    intent_distributions: List[IntentDistributionItem]
    query_length_distribution: List[TokenDistributionBin]
