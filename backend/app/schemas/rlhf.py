from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.rlhf import FeedbackExportStatus


class RLHFReviewSubmission(BaseModel):
    message_id: str
    clinical_accuracy_rating: int = Field(ge=1, le=5, description="1 to 5 Likert accuracy scale")
    hallucination_flag: bool = False
    safety_guideline_violation: bool = False
    omission_of_red_flag_symptom: bool = False
    revised_completion_text: Optional[str] = None
    clinician_notes: Optional[str] = None
    export_status: FeedbackExportStatus = FeedbackExportStatus.APPROVED_FOR_FINETUNE


class RLHFReviewItem(BaseModel):
    feedback_id: str
    message_id: str
    clinician_id: str
    clinician_name: Optional[str] = None
    clinical_accuracy_rating: int
    hallucination_flag: bool
    safety_guideline_violation: bool
    omission_of_red_flag_symptom: bool
    revised_completion_text: Optional[str]
    clinician_notes: Optional[str]
    export_status: FeedbackExportStatus
    prompt_text: str
    original_model_output: str
    citations: List[dict]
    created_at: str

    class Config:
        from_attributes = True


class RLHFPendingItem(BaseModel):
    message_id: str
    session_id: str
    patient_query_redacted: str
    assistant_response: str
    clinical_citations: List[dict]
    groundedness_score: float
    retrieval_similarity_score: float
    created_at: str


class FineTuneExportFormatRequest(BaseModel):
    format_type: str = Field(default="openai_chat", description="'openai_chat' or 'llama_alpaca'")
    minimum_rating: int = Field(default=4, ge=1, le=5)
    include_system_guardrails: bool = True
