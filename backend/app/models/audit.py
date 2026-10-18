import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, JSON
from app.database import Base, utc_now


class AuditActionType(str, enum.Enum):
    PHI_SCRUB_EVENT = "PHI_SCRUB_EVENT"
    EMERGENCY_TRIAGE_ESCALATION = "EMERGENCY_TRIAGE_ESCALATION"
    CLINICIAN_RLHF_SUBMISSION = "CLINICIAN_RLHF_SUBMISSION"
    FINETUNE_DATASET_EXPORT = "FINETUNE_DATASET_EXPORT"
    AUTHENTICATION_EVENT = "AUTHENTICATION_EVENT"
    FHIR_PATIENT_SUMMARY_ACCESS = "FHIR_PATIENT_SUMMARY_ACCESS"
    EVALUATION_BATCH_RUN = "EVALUATION_BATCH_RUN"


class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "COMPLIANT"
    ESCALATED = "ESCALATED"
    SECURITY_ANOMALY = "SECURITY_ANOMALY"


class AuditLogEntry(Base):
    __tablename__ = "audit_log_entries"

    entry_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)

    action_type = Column(Enum(AuditActionType), nullable=False, index=True)
    resource_accessed = Column(String(255), nullable=False)

    # Salted SHA-256 hash of client IP address to prevent physical tracking while retaining forensic correlation
    anonymized_ip_hash = Column(String(64), nullable=False)
    compliance_status = Column(Enum(ComplianceStatus), default=ComplianceStatus.COMPLIANT, nullable=False)

    # Structured metadata for regulatory inspections
    audit_metadata = Column(JSON, default=dict, nullable=False)
