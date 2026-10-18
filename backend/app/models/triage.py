import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Integer, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base, utc_now


class TriageSeverity(str, enum.Enum):
    ROUTINE = "ROUTINE"         # Self-care / Scheduled primary care consult
    URGENT = "URGENT"           # Same-day urgent care or clinic evaluation
    EMERGENCY = "EMERGENCY"     # Immediate ED escalation / 911 / 999 activation


class MessageSenderRole(str, enum.Enum):
    PATIENT = "PATIENT"
    CLINICIAN_ASSISTANT = "CLINICIAN_ASSISTANT"
    SYSTEM = "SYSTEM"


class TriageSession(Base):
    __tablename__ = "triage_sessions"

    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    # Demographics used purely for clinical age-bracket triage logic (e.g., pediatric vs adult fever cutoffs)
    patient_age_group = Column(String(32), default="ADULT", nullable=False)
    biological_sex = Column(String(16), default="UNSPECIFIED", nullable=False)

    # Statutory consent tracking prior to clinical conversational intake
    consent_acknowledged = Column(Boolean, default=False, nullable=False)
    disclaimer_acknowledged = Column(Boolean, default=False, nullable=False)
    consent_timestamp = Column(DateTime, nullable=True)

    # Deterministic triage escalation state
    emergency_escalated = Column(Boolean, default=False, nullable=False, index=True)
    escalation_reason = Column(String(512), nullable=True)
    triage_severity = Column(Enum(TriageSeverity), default=TriageSeverity.ROUTINE, nullable=False)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="triage_sessions")
    messages = relationship("TriageMessage", back_populates="session", cascade="all, delete-orphan", order_by="TriageMessage.created_at")


class TriageMessage(Base):
    __tablename__ = "triage_messages"

    message_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("triage_sessions.session_id"), nullable=False, index=True)
    sender_role = Column(Enum(MessageSenderRole), nullable=False)

    # Stored content MUST be scrubbed of all 18 HIPAA Safe Harbor identifiers
    redacted_content = Column(Text, nullable=False)
    redacted_entity_types = Column(JSON, default=list, nullable=False)

    # Structured citations retrieved from validated clinical literature
    clinical_citations = Column(JSON, default=list, nullable=False)

    # Real-time retrieval & evaluation metrics
    retrieval_similarity_score = Column(Float, default=0.0, nullable=False)
    groundedness_score = Column(Float, default=0.0, nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    safety_check_passed = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    session = relationship("TriageSession", back_populates="messages")
    rlhf_reviews = relationship("RLHFFeedbackRecord", back_populates="message")
