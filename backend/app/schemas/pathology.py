from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.pathology import MedicalSpecialty, TriageAcuityLevel


class SymptomItem(BaseModel):
    symptom: str
    weight: float = Field(ge=0.0, le=1.0)
    clinical_note: Optional[str] = None


class CardinalSymptomsSchema(BaseModel):
    primary: List[SymptomItem]
    secondary: List[SymptomItem]


class DifferentialItem(BaseModel):
    condition: str
    icd11: str
    clinical_distinction: str


class DiagnosticWorkupSchema(BaseModel):
    initial_labs: List[str]
    imaging_ecg: List[str]
    confirmatory_tests: List[str]


class EvidenceBasedManagementSchema(BaseModel):
    first_line_lifestyle: List[str]
    pharmacotherapy: List[str]
    contraindications: List[str]


class SourceMetadataSchema(BaseModel):
    issuing_authority: str
    guideline_title: str
    publication_year: int
    source_url: Optional[str] = None
    verification_hash: str


class PathologyBase(BaseModel):
    icd11_code: str
    icd10_code: Optional[str] = None
    clinical_name: str
    common_aliases: List[str] = Field(default_factory=list)
    medical_specialty: MedicalSpecialty
    baseline_acuity: TriageAcuityLevel = TriageAcuityLevel.ROUTINE_CLINIC
    pathophysiology_overview: str
    cardinal_symptoms: Dict[str, Any]
    red_flag_criteria: List[str]
    differential_diagnoses: List[Dict[str, Any]]
    diagnostic_workup: Dict[str, Any]
    evidence_based_management: Dict[str, Any]
    source_metadata: Dict[str, Any]


class PathologyCreate(PathologyBase):
    pass


class PathologyRead(PathologyBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PathologySummary(BaseModel):
    id: int
    icd11_code: str
    clinical_name: str
    medical_specialty: MedicalSpecialty
    baseline_acuity: TriageAcuityLevel
    primary_symptoms: List[str]
    red_flag_count: int


class PathologySearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[PathologyRead]
