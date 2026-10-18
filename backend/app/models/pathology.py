from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, DateTime, JSON
from app.database import Base, utc_now


class MedicalSpecialty(str, Enum):
    INFECTIOUS_DISEASES = "Infectious & Tropical Diseases"
    CARDIOVASCULAR = "Cardiovascular Medicine"
    ENDOCRINE_METABOLIC = "Endocrinology & Metabolism"
    RESPIRATORY = "Respiratory Medicine"
    NEUROLOGY = "Neurology"
    PSYCHIATRY = "Psychiatry & Behavioral Health"
    GASTROENTEROLOGY_HEPATOLOGY = "Gastroenterology & Hepatology"
    NEPHROLOGY_UROLOGY = "Nephrology & Urology"
    HEMATOLOGY = "Hematology"
    ONCOLOGY = "Medical Oncology"
    DERMATOLOGY = "Dermatology"
    RHEUMATOLOGY = "Rheumatology & Clinical Immunology"
    OBSTETRICS_GYNECOLOGY = "Obstetrics & Maternal Medicine"
    PEDIATRICS = "Pediatrics & Child Health"


class TriageAcuityLevel(str, Enum):
    EMERGENCY = "EMERGENCY"
    URGENT_CONSULT = "URGENT_CONSULT"
    ROUTINE_CLINIC = "ROUTINE_CLINIC"
    SELF_CARE_MONITORING = "SELF_CARE_MONITORING"


class Pathology(Base):
    """
    Structured relational pathology ontology aligned with WHO ICD-11 standards.
    Stores comprehensive medical knowledge including pathophysiology, cardinal symptoms,
    deterministic red flags, diagnostic workups, and evidence-based clinical protocols.
    """
    __tablename__ = "clinical_pathologies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    icd11_code = Column(String(32), unique=True, index=True, nullable=False)
    icd10_code = Column(String(32), index=True, nullable=True)
    clinical_name = Column(String(255), index=True, nullable=False)
    common_aliases = Column(JSON, nullable=False, default=list)
    medical_specialty = Column(SQLEnum(MedicalSpecialty), index=True, nullable=False)
    baseline_acuity = Column(SQLEnum(TriageAcuityLevel), nullable=False, default=TriageAcuityLevel.ROUTINE_CLINIC)
    pathophysiology_overview = Column(Text, nullable=False)
    cardinal_symptoms = Column(JSON, nullable=False, default=dict)
    red_flag_criteria = Column(JSON, nullable=False, default=list)
    differential_diagnoses = Column(JSON, nullable=False, default=list)
    diagnostic_workup = Column(JSON, nullable=False, default=dict)
    evidence_based_management = Column(JSON, nullable=False, default=dict)
    source_metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
