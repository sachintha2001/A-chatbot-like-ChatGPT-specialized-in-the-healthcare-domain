import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.database import Base, utc_now


class FeedbackExportStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED_FOR_FINETUNE = "APPROVED_FOR_FINETUNE"
    REJECTED = "REJECTED"
    EXPORTED = "EXPORTED"


class RLHFFeedbackRecord(Base):
    __tablename__ = "rlhf_feedback_records"

    feedback_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("triage_messages.message_id"), nullable=False, index=True)
    clinician_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Likert Scale 1-5 (1: Clinically dangerous / incorrect, 5: Fully evidence-aligned)
    clinical_accuracy_rating = Column(Integer, nullable=False)

    # Discrete error typology classifications for alignment tuning
    hallucination_flag = Column(Boolean, default=False, nullable=False)
    safety_guideline_violation = Column(Boolean, default=False, nullable=False)
    omission_of_red_flag_symptom = Column(Boolean, default=False, nullable=False)

    # Clinician rewritten ground truth for supervised fine-tuning dataset export
    revised_completion_text = Column(Text, nullable=True)
    clinician_notes = Column(Text, nullable=True)

    export_status = Column(Enum(FeedbackExportStatus), default=FeedbackExportStatus.PENDING, nullable=False, index=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    message = relationship("TriageMessage", back_populates="rlhf_reviews")
    clinician = relationship("User", back_populates="rlhf_reviews")
