from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.database import get_db_session, utc_now
from app.models.patient import (
    PatientProfile,
    PatientMedicalRecord,
    RelationshipType,
    BiologicalSex,
    MedicalRecordType,
)
from app.engine.patient_history_engine import patient_history_engine

router = APIRouter(prefix="/patient", tags=["Patient Profiles & Longitudinal Health Records"])


# Pydantic Schemas
class PatientProfileCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    relationship: RelationshipType = RelationshipType.SELF
    date_of_birth: Optional[str] = "1990-01-01"
    biological_sex: BiologicalSex = BiologicalSex.UNSPECIFIED
    blood_group: Optional[str] = "UNKNOWN"
    allergies: List[str] = []
    chronic_conditions: List[str] = []
    emergency_contact_phone: Optional[str] = None
    notes: Optional[str] = None


class PatientProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    relationship: Optional[RelationshipType] = None
    date_of_birth: Optional[str] = None
    biological_sex: Optional[BiologicalSex] = None
    blood_group: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[str]] = None
    emergency_contact_phone: Optional[str] = None
    notes: Optional[str] = None


class BiomarkerMeasurement(BaseModel):
    canonical_id: str
    display_name_en: str
    display_name_si: Optional[str] = None
    numeric_value: Optional[float] = None
    raw_value: Optional[str] = None
    unit: str = ""
    ref_interval: Optional[str] = None
    status: str = "NORMAL"
    status_si: Optional[str] = None
    is_abnormal: bool = False
    is_critical: bool = False


class MedicalRecordCreate(BaseModel):
    record_type: MedicalRecordType = MedicalRecordType.LAB_REPORT
    record_date: Optional[datetime] = None
    title: str = Field(..., min_length=2, max_length=255)
    overall_status: str = "ALL_NORMAL"
    qualitative_verdict: str = "NOT_APPLICABLE"
    extracted_biomarkers: List[Dict[str, Any]] = []
    correlated_icd11: List[Dict[str, Any]] = []
    notes: Optional[str] = None
    raw_text: Optional[str] = None
    source_filename: Optional[str] = None
    session_id: Optional[str] = None


@router.get("/profiles")
async def list_patient_profiles(
    session: AsyncSession = Depends(get_db_session)
):
    """
    Retrieves all patient and family member profiles with aggregated record counts.
    """
    stmt = (
        select(PatientProfile)
        .options(selectinload(PatientProfile.records))
        .order_by(PatientProfile.created_at.asc())
    )
    res = await session.execute(stmt)
    profiles = res.scalars().all()

    result = []
    for p in profiles:
        result.append({
            "id": p.id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "full_name": f"{p.first_name} {p.last_name}",
            "relationship": p.relationship.value if hasattr(p.relationship, "value") else str(p.relationship),
            "date_of_birth": p.date_of_birth,
            "biological_sex": p.biological_sex.value if hasattr(p.biological_sex, "value") else str(p.biological_sex),
            "blood_group": p.blood_group,
            "allergies": p.allergies or [],
            "chronic_conditions": p.chronic_conditions or [],
            "emergency_contact_phone": p.emergency_contact_phone,
            "notes": p.notes,
            "total_records": len(p.records) if p.records else 0,
            "latest_record_date": p.records[0].record_date.isoformat() if (p.records and len(p.records) > 0) else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    return result


@router.post("/profiles", status_code=status.HTTP_201_CREATED)
async def create_patient_profile(
    payload: PatientProfileCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Creates a new patient profile (Self or family member: Father, Mother, Spouse, Child).
    """
    profile = PatientProfile(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        relationship=payload.relationship,
        date_of_birth=payload.date_of_birth,
        biological_sex=payload.biological_sex,
        blood_group=payload.blood_group or "UNKNOWN",
        allergies=payload.allergies,
        chronic_conditions=payload.chronic_conditions,
        emergency_contact_phone=payload.emergency_contact_phone,
        notes=payload.notes,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    return {
        "id": profile.id,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "full_name": f"{profile.first_name} {profile.last_name}",
        "relationship": profile.relationship.value if hasattr(profile.relationship, "value") else str(profile.relationship),
        "date_of_birth": profile.date_of_birth,
        "biological_sex": profile.biological_sex.value if hasattr(profile.biological_sex, "value") else str(profile.biological_sex),
        "blood_group": profile.blood_group,
        "allergies": profile.allergies,
        "chronic_conditions": profile.chronic_conditions,
        "emergency_contact_phone": profile.emergency_contact_phone,
        "notes": profile.notes,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
    }


@router.get("/profiles/{profile_id}")
async def get_patient_profile(
    profile_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Retrieves full details for a specific patient profile.
    """
    stmt = (
        select(PatientProfile)
        .options(selectinload(PatientProfile.records))
        .where(PatientProfile.id == profile_id)
    )
    res = await session.execute(stmt)
    profile = res.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient profile '{profile_id}' not found."
        )

    return {
        "id": profile.id,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "full_name": f"{profile.first_name} {profile.last_name}",
        "relationship": profile.relationship.value if hasattr(profile.relationship, "value") else str(profile.relationship),
        "date_of_birth": profile.date_of_birth,
        "biological_sex": profile.biological_sex.value if hasattr(profile.biological_sex, "value") else str(profile.biological_sex),
        "blood_group": profile.blood_group,
        "allergies": profile.allergies or [],
        "chronic_conditions": profile.chronic_conditions or [],
        "emergency_contact_phone": profile.emergency_contact_phone,
        "notes": profile.notes,
        "total_records": len(profile.records) if profile.records else 0,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
    }


@router.put("/profiles/{profile_id}")
async def update_patient_profile(
    profile_id: str,
    payload: PatientProfileUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Updates patient demographics, allergies, or chronic conditions.
    """
    stmt = select(PatientProfile).where(PatientProfile.id == profile_id)
    res = await session.execute(stmt)
    profile = res.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient profile '{profile_id}' not found."
        )

    if payload.first_name is not None:
        profile.first_name = payload.first_name.strip()
    if payload.last_name is not None:
        profile.last_name = payload.last_name.strip()
    if payload.relationship is not None:
        profile.relationship = payload.relationship
    if payload.date_of_birth is not None:
        profile.date_of_birth = payload.date_of_birth
    if payload.biological_sex is not None:
        profile.biological_sex = payload.biological_sex
    if payload.blood_group is not None:
        profile.blood_group = payload.blood_group
    if payload.allergies is not None:
        profile.allergies = payload.allergies
    if payload.chronic_conditions is not None:
        profile.chronic_conditions = payload.chronic_conditions
    if payload.emergency_contact_phone is not None:
        profile.emergency_contact_phone = payload.emergency_contact_phone
    if payload.notes is not None:
        profile.notes = payload.notes

    await session.commit()
    await session.refresh(profile)

    return {"status": "SUCCESS", "profile_id": profile.id}


@router.delete("/profiles/{profile_id}")
async def delete_patient_profile(
    profile_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Deletes a patient profile and its associated medical records.
    """
    stmt = select(PatientProfile).where(PatientProfile.id == profile_id)
    res = await session.execute(stmt)
    profile = res.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient profile '{profile_id}' not found."
        )

    await session.delete(profile)
    await session.commit()
    return {"status": "SUCCESS", "message": f"Profile '{profile_id}' deleted successfully."}


@router.get("/profiles/{profile_id}/records")
async def list_patient_records(
    profile_id: str,
    record_type: Optional[str] = Query(None, description="Filter by LAB_REPORT, TRIAGE_SESSION, etc."),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Retrieves chronological medical records for a specific patient profile.
    """
    # Verify profile exists
    p_stmt = select(PatientProfile).where(PatientProfile.id == profile_id)
    p_res = await session.execute(p_stmt)
    profile = p_res.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient profile '{profile_id}' not found."
        )

    stmt = select(PatientMedicalRecord).where(PatientMedicalRecord.profile_id == profile_id)
    if record_type:
        try:
            r_type_enum = MedicalRecordType(record_type)
            stmt = stmt.where(PatientMedicalRecord.record_type == r_type_enum)
        except ValueError:
            pass

    stmt = stmt.order_by(PatientMedicalRecord.record_date.desc())
    res = await session.execute(stmt)
    records = res.scalars().all()

    items = []
    for r in records:
        items.append({
            "id": r.id,
            "profile_id": r.profile_id,
            "record_type": r.record_type.value if hasattr(r.record_type, "value") else str(r.record_type),
            "record_date": r.record_date.isoformat() if r.record_date else None,
            "title": r.title,
            "overall_status": r.overall_status,
            "qualitative_verdict": r.qualitative_verdict,
            "extracted_biomarkers": r.extracted_biomarkers or [],
            "correlated_icd11": r.correlated_icd11 or [],
            "notes": r.notes,
            "source_filename": r.source_filename,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {
        "profile_id": profile_id,
        "patient_name": f"{profile.first_name} {profile.last_name}",
        "total_records": len(items),
        "records": items
    }


@router.post("/profiles/{profile_id}/records", status_code=status.HTTP_201_CREATED)
async def create_patient_record(
    profile_id: str,
    payload: MedicalRecordCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Appends a new medical record (e.g. analyzed lab report or triage session) to the patient profile.
    """
    p_stmt = select(PatientProfile).where(PatientProfile.id == profile_id)
    p_res = await session.execute(p_stmt)
    profile = p_res.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient profile '{profile_id}' not found."
        )

    rec_date = payload.record_date if payload.record_date else utc_now()
    if rec_date and hasattr(rec_date, "tzinfo") and rec_date.tzinfo is not None:
        rec_date = rec_date.replace(tzinfo=None)

    record = PatientMedicalRecord(
        profile_id=profile_id,
        record_type=payload.record_type,
        record_date=rec_date,
        title=payload.title,
        overall_status=payload.overall_status,
        qualitative_verdict=payload.qualitative_verdict,
        extracted_biomarkers=payload.extracted_biomarkers,
        correlated_icd11=payload.correlated_icd11,
        notes=payload.notes,
        raw_text=payload.raw_text,
        source_filename=payload.source_filename,
        session_id=payload.session_id,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)

    return {
        "id": record.id,
        "profile_id": record.profile_id,
        "title": record.title,
        "record_date": record.record_date.isoformat(),
        "overall_status": record.overall_status,
        "qualitative_verdict": record.qualitative_verdict,
        "biomarkers_count": len(record.extracted_biomarkers) if record.extracted_biomarkers else 0
    }


@router.get("/profiles/{profile_id}/trends")
async def get_patient_trends(
    profile_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Computes mathematical biomarker trajectories, deltas, and clinical direction
    across all historical laboratory records for this patient profile.
    """
    stmt = (
        select(PatientProfile)
        .options(selectinload(PatientProfile.records))
        .where(PatientProfile.id == profile_id)
    )
    res = await session.execute(stmt)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient profile '{profile_id}' not found."
        )

    trend_analysis = patient_history_engine.compute_longitudinal_trends(
        records=profile.records or [],
        patient_profile=profile
    )

    return {
        "profile": {
            "id": profile.id,
            "full_name": f"{profile.first_name} {profile.last_name}",
            "relationship": profile.relationship.value if hasattr(profile.relationship, "value") else str(profile.relationship),
            "date_of_birth": profile.date_of_birth,
            "biological_sex": profile.biological_sex.value if hasattr(profile.biological_sex, "value") else str(profile.biological_sex),
            "blood_group": profile.blood_group,
            "allergies": profile.allergies or [],
            "chronic_conditions": profile.chronic_conditions or [],
        },
        **trend_analysis
    }
