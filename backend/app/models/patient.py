import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Integer, Float, Text, JSON
from sqlalchemy.orm import relationship as orm_relationship
from app.database import Base, utc_now


class RelationshipType(str, enum.Enum):
    SELF = "SELF"
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    SPOUSE = "SPOUSE"
    CHILD = "CHILD"
    SIBLING = "SIBLING"
    OTHER = "OTHER"


class BiologicalSex(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNSPECIFIED = "UNSPECIFIED"


class MedicalRecordType(str, enum.Enum):
    LAB_REPORT = "LAB_REPORT"
    TRIAGE_SESSION = "TRIAGE_SESSION"
    PHYSICAL_EXAM = "PHYSICAL_EXAM"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    relationship = Column(Enum(RelationshipType), default=RelationshipType.SELF, nullable=False, index=True)
    date_of_birth = Column(String(10), nullable=True)  # YYYY-MM-DD
    biological_sex = Column(Enum(BiologicalSex), default=BiologicalSex.UNSPECIFIED, nullable=False)
    blood_group = Column(String(10), default="UNKNOWN", nullable=False)

    allergies = Column(JSON, default=list, nullable=False)
    chronic_conditions = Column(JSON, default=list, nullable=False)
    emergency_contact_phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    records = orm_relationship(
        "PatientMedicalRecord",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="PatientMedicalRecord.record_date"
    )


class PatientMedicalRecord(Base):
    __tablename__ = "patient_medical_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("patient_profiles.id"), nullable=False, index=True)

    record_type = Column(Enum(MedicalRecordType), default=MedicalRecordType.LAB_REPORT, nullable=False, index=True)
    record_date = Column(DateTime, default=utc_now, nullable=False, index=True)
    title = Column(String(255), nullable=False)

    overall_status = Column(String(64), default="ALL_NORMAL", nullable=False)
    qualitative_verdict = Column(String(64), default="NOT_APPLICABLE", nullable=False)

    extracted_biomarkers = Column(JSON, default=list, nullable=False)
    correlated_icd11 = Column(JSON, default=list, nullable=False)

    notes = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    source_filename = Column(String(255), nullable=True)
    session_id = Column(String(36), nullable=True)

    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    profile = orm_relationship("PatientProfile", back_populates="records")
