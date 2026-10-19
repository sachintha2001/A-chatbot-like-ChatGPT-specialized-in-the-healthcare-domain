from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SpecialistDoctor(BaseModel):
    doctor_id: str
    full_name_en: str
    full_name_si: str
    qualifications: str
    slmc_reg_no: str
    specialty_code: str
    specialty_en: str
    specialty_si: str
    primary_hospital_en: str
    primary_hospital_si: str
    visiting_hospitals: List[str]
    supported_modes: List[str]
    supported_gateways: List[str]
    consultation_fee_lkr: int
    next_available_slots: List[str]
    languages_spoken: List[str]
    rating: float
    echannelling_url: str
    doc990_url: str
    odoc_url: str


class SpecialistRecommendationRequest(BaseModel):
    specialty_hint: Optional[str] = Field(
        None,
        description="Recommended specialist name or department (e.g., 'Cardiologist', 'Hematologist', 'Endocrinologist')"
    )
    clinical_context: Optional[str] = Field(
        None,
        description="Symptom narrative, triage headline, or lab report findings"
    )
    triage_acuity: Optional[str] = Field("ROUTINE", description="EMERGENCY, URGENT, or ROUTINE")
    icd11_codes: List[str] = Field(default_factory=list)
    consultation_mode: Optional[str] = Field(None, description="IN_PERSON_HOSPITAL or VIDEO_TELEMEDICINE")
    language: str = "en"


class SpecialistRecommendationResponse(BaseModel):
    matched_specialty_code: str
    matched_specialty_en: str
    matched_specialty_si: str
    triage_acuity: str
    emergency_warning_active: bool
    emergency_directive_en: Optional[str] = None
    emergency_directive_si: Optional[str] = None
    recommended_consultation_mode: str
    specialists: List[SpecialistDoctor]
    partner_gateways: List[Dict[str, str]]


class AppointmentBookingRequest(BaseModel):
    doctor_id: str
    patient_name: str = Field(..., min_length=2)
    patient_phone: str = Field(..., min_length=7)
    patient_age: Optional[int] = Field(None, ge=0, le=120)
    preferred_slot: str
    consultation_mode: str = Field("IN_PERSON_HOSPITAL", description="IN_PERSON_HOSPITAL or VIDEO_TELEMEDICINE")
    booking_gateway: str = Field("ECHANNELLING", description="ECHANNELLING, DOC990, ODOC_TELEMED, or HOSPITAL_DIRECT")
    hospital_name: Optional[str] = None
    clinical_context_summary: Optional[str] = None
    recommended_specialty: Optional[str] = None
    triage_acuity: Optional[str] = "ROUTINE"
    correlated_icd11_codes: List[str] = Field(default_factory=list)
    language: str = "en"


class AppointmentBookingResponse(BaseModel):
    booking_id: str
    booking_reference: str
    status: str
    queue_token_number: int
    doctor: SpecialistDoctor
    patient_display_name: str
    patient_phone_masked: str
    scheduled_slot: str
    consultation_mode: str
    booking_gateway: str
    hospital_or_platform: str
    estimated_fee_lkr: int
    telemedicine_meeting_url: Optional[str] = None
    external_gateway_redirect_url: str
    sbar_clinical_handover_en: str
    sbar_clinical_handover_si: str
    created_at: str
