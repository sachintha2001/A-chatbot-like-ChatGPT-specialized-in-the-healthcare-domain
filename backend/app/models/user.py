import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base, utc_now


class UserRole(str, enum.Enum):
    PATIENT = "PATIENT"
    CLINICIAN = "CLINICIAN"
    AUDITOR = "AUDITOR"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False, index=True)

    # Professional license identifier (e.g. NPI for US clinicians, GMC number for UK NHS clinicians)
    license_credential_id = Column(String(64), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    triage_sessions = relationship("TriageSession", back_populates="user", cascade="all, delete-orphan")
    rlhf_reviews = relationship("RLHFFeedbackRecord", back_populates="clinician")
