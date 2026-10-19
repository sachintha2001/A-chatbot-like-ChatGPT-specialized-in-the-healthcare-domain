from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.telemedicine import (
    SpecialistDoctor,
    SpecialistRecommendationRequest,
    SpecialistRecommendationResponse,
    AppointmentBookingRequest,
    AppointmentBookingResponse,
)
from app.engine.telemedicine_engine import telemedicine_engine

router = APIRouter(
    prefix="/telemedicine",
    tags=["Telemedicine & Specialist Appointment Booking (eChannelling / Doc990 / oDoc)"],
)


@router.get("/gateways", response_model=List[Dict[str, str]])
async def get_booking_gateways():
    """
    Returns integrated Sri Lankan specialist channelling and telemedicine gateways
    (eChannelling, Doc990, oDoc 24/7 Video Telemedicine, and Direct Hospital Booking).
    """
    return telemedicine_engine.PARTNER_GATEWAYS


@router.get("/specialists", response_model=List[SpecialistDoctor])
async def list_specialists(
    specialty: Optional[str] = Query(None, description="Specialty code e.g. CARDIOLOGY, HEMATOLOGY, ENDOCRINOLOGY"),
    mode: Optional[str] = Query(None, description="IN_PERSON_HOSPITAL or VIDEO_TELEMEDICINE"),
    gateway: Optional[str] = Query(None, description="ECHANNELLING, DOC990, ODOC_TELEMED, or HOSPITAL_DIRECT"),
    q: Optional[str] = Query(None, description="Search by doctor name, hospital, symptom, or specialty"),
):
    """
    Returns Sri Lankan SLMC-registered specialist consultants filtered by specialty,
    consultation mode, booking gateway, or clinical search query.
    """
    return telemedicine_engine.get_all_specialists(
        specialty_code=specialty,
        consultation_mode=mode,
        gateway=gateway,
        search_query=q,
    )


@router.post("/recommend", response_model=SpecialistRecommendationResponse)
async def recommend_specialists_for_patient(payload: SpecialistRecommendationRequest):
    """
    Automatically matches a patient's triage assessment, ICD-11 differential, or laboratory
    report abnormality (e.g., Cardiologist, Hematologist, Endocrinologist) to available
    Sri Lankan specialists across eChannelling, Doc990, and oDoc.
    """
    return telemedicine_engine.recommend_specialists(payload)


@router.post(
    "/appointments",
    response_model=AppointmentBookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def book_specialist_appointment(payload: AppointmentBookingRequest):
    """
    Books a specialist appointment or telemedicine video session and generates:
    1. Confirmed Booking Reference (ECH / DOC990 / ODOC / HOSP) & Queue Token Number
    2. Automated SBAR (Situation, Background, Assessment, Recommendation) Clinical Handover Slip
    3. Direct deep-link to eChannelling / Doc990 / oDoc or Telemedicine Video Room
    """
    return telemedicine_engine.create_appointment(payload)


@router.get("/appointments", response_model=List[AppointmentBookingResponse])
async def list_booked_appointments():
    """Returns all booked specialist appointments and SBAR clinical handover slips."""
    return telemedicine_engine.list_appointments()


@router.patch("/appointments/{booking_id}/cancel", response_model=AppointmentBookingResponse)
async def cancel_booked_appointment(booking_id: str):
    """Cancels an existing appointment booking by booking_id or booking_reference."""
    cancelled = telemedicine_engine.cancel_appointment(booking_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment '{booking_id}' not found.",
        )
    return cancelled
