from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.triage import TriageSeverity, MessageSenderRole


class SessionInitRequest(BaseModel):
    patient_age_group: str = Field(default="ADULT", description="PEDIATRIC, ADULT, GERIATRIC")
    biological_sex: str = Field(default="UNSPECIFIED", description="MALE, FEMALE, UNSPECIFIED")
    consent_acknowledged: bool = Field(..., description="Patient statutory consent")
    disclaimer_acknowledged: bool = Field(..., description="Acknowledgement that platform is an assistive CDSS, not final diagnostic practitioner")


class SessionResponse(BaseModel):
    session_id: str
    patient_age_group: str
    biological_sex: str
    consent_acknowledged: bool
    disclaimer_acknowledged: bool
    emergency_escalated: bool
    escalation_reason: Optional[str] = None
    triage_severity: TriageSeverity
    created_at: str

    class Config:
        from_attributes = True


class TriagePromptRequest(BaseModel):
    session_id: str
    prompt_text: str = Field(..., min_length=2)
    language: Optional[str] = Field(default="en", description="'en' or 'si'")


class ClinicalCitation(BaseModel):
    citation_id: str
    guideline_id: str
    source_title: str
    clinical_domain: str
    evidence_level: str
    section_header: str
    source_url: str
    publication_year: int
    matched_snippet: str
    relevance_score: float


class EmergencyEscalationInfo(BaseModel):
    is_emergency: bool
    matched_red_flags: List[str]
    escalation_directive: str
    hotline_numbers: dict


class TriageMessageResponse(BaseModel):
    message_id: str
    session_id: str
    sender_role: MessageSenderRole
    redacted_content: str
    clinical_citations: List[ClinicalCitation]
    retrieval_similarity_score: float
    groundedness_score: float
    latency_ms: int
    safety_check_passed: bool
    emergency_info: Optional[EmergencyEscalationInfo] = None
    triage_severity: TriageSeverity
    created_at: str
