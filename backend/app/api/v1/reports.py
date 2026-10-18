from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from app.engine.report_analyzer import report_analyzer
from app.knowledge.lab_biomarkers import CLINICAL_BIOMARKER_REGISTRY

router = APIRouter(prefix="/reports", tags=["Clinical Laboratory Report Analysis"])


class ReportTextAnalysisRequest(BaseModel):
    report_text: str = Field(..., min_length=3, max_length=15000)
    patient_age_group: Optional[str] = "ADULT"
    biological_sex: Optional[str] = "UNSPECIFIED"
    language: Optional[str] = "en"


SAMPLE_CLINICAL_REPORTS = [
    {
        "id": "dengue_fbc_critical",
        "title_en": "Dengue Fever with Severe Thrombocytopenia (Critical FBC)",
        "title_si": "ඩෙංගු රක්තපාත උණ - පට්ටිකා අඩු වූ FBC වාර්තාව",
        "sample_text": (
            "PATIENT LABORATORY INVESTIGATION REPORT\n"
            "Test: Full Blood Count (FBC / CBC)\n"
            "Hemoglobin (Hb): 15.8 g/dL\n"
            "Total WBC: 3200 /uL\n"
            "Platelet Count: 42000 /uL\n"
            "Packed Cell Volume (PCV): 49.5 %\n"
            "Dengue NS1 Antigen: POSITIVE\n"
            "Clinical Impression: Acute dengue fever critical phase monitoring."
        )
    },
    {
        "id": "lipid_cardiovascular_risk",
        "title_en": "Atherogenic Lipid Profile (High Cardiovascular Risk)",
        "title_si": "අධික කොලෙස්ටරෝල් සහ හෘද අවදානම් ලිපිඩ වාර්තාව",
        "sample_text": (
            "FASTING LIPID PROFILE REPORT\n"
            "Specimen: Serum (12-hour fast)\n"
            "Total Cholesterol: 268 mg/dL\n"
            "Triglycerides: 280 mg/dL\n"
            "HDL Cholesterol: 34 mg/dL\n"
            "LDL Cholesterol: 178 mg/dL\n"
            "Clinical Impression: Combined hyperlipidemia with elevated atherogenic index."
        )
    },
    {
        "id": "diabetic_glycemic_profile",
        "title_en": "Uncontrolled Type 2 Diabetes Glycemic Panel",
        "title_si": "පාලනය නොවූ දෙවන කාණ්ඩයේ දියවැඩියා වාර්තාව",
        "sample_text": (
            "DIABETES MONITORING PANEL\n"
            "Fasting Blood Sugar (FBS): 186 mg/dL\n"
            "Glycated Hemoglobin (HbA1c): 8.9 %\n"
            "Serum Creatinine: 1.4 mg/dL\n"
            "eGFR: 58 mL/min/1.73m2\n"
            "Urine Protein: POSITIVE\n"
            "Clinical Impression: Suboptimal glycemic control with early diabetic nephropathy."
        )
    },
    {
        "id": "acute_coronary_cardiac",
        "title_en": "Acute Myocardial Infarction Cardiac Biomarkers",
        "title_si": "හදිසි හෘදයාබාධ ට්‍රොපොනින් පරීක්ෂණ වාර්තාව",
        "sample_text": (
            "EMERGENCY CARDIAC BIOMARKER REPORT\n"
            "Test: High-Sensitivity Cardiac Troponin I\n"
            "Cardiac Troponin: 0.85 ng/mL\n"
            "Serum Potassium: 4.8 mmol/L\n"
            "Total WBC: 12400 /uL\n"
            "CRP: 18.5 mg/L\n"
            "Clinical Impression: Acute chest pain with biomarker-positive myocardial necrosis."
        )
    },
    {
        "id": "routine_normal_health_check",
        "title_en": "Standard Comprehensive Normal Health Check",
        "title_si": "සාමාන්‍ය නිරෝගී සෞඛ්‍ය පරීක්ෂණ වාර්තාව",
        "sample_text": (
            "ANNUAL COMPREHENSIVE EXECUTIVE HEALTH SCREENING\n"
            "Hemoglobin (Hb): 14.2 g/dL\n"
            "Total WBC: 6800 /uL\n"
            "Platelet Count: 265000 /uL\n"
            "Fasting Blood Sugar: 88 mg/dL\n"
            "HbA1c: 5.2 %\n"
            "Total Cholesterol: 175 mg/dL\n"
            "LDL Cholesterol: 92 mg/dL\n"
            "HDL Cholesterol: 56 mg/dL\n"
            "Serum Creatinine: 0.9 mg/dL\n"
            "ALT (SGPT): 24 U/L\n"
            "Clinical Impression: All parameters within standard reference limits."
        )
    }
]


class CameraImageCaptureRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 data URL or raw base64 string of camera capture")
    filename: Optional[str] = "camera_capture.jpg"
    patient_age_group: Optional[str] = "ADULT"
    biological_sex: Optional[str] = "UNSPECIFIED"
    language: Optional[str] = "en"


@router.post("/upload")
async def upload_medical_report(
    file: UploadFile = File(...),
    patient_age_group: str = Form("ADULT"),
    biological_sex: str = Form("UNSPECIFIED"),
    language: str = Form("en")
):
    """
    Accepts laboratory report files (PDF, TXT, CSV, or photographed images PNG/JPG/WEBP),
    extracts raw text (with OCR for images), identifies clinical biomarkers,
    and returns a structured clinical interpretation.
    """
    allowed_extensions = (".pdf", ".txt", ".csv", ".text", ".png", ".jpg", ".jpeg", ".webp", ".bmp")
    filename = file.filename or "report.txt"

    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF (.pdf), document (.txt, .csv), or report photo (.png, .jpg, .jpeg, .webp)."
        )

    try:
        content = await file.read()
        extracted_text = report_analyzer.extract_text_from_file(content, filename)
        
        if not extracted_text or len(extracted_text.strip()) < 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to extract text content from the uploaded document or image. Ensure the image has good lighting and readable text."
            )

        analysis = report_analyzer.analyze_report(
            raw_text=extracted_text,
            patient_age_group=patient_age_group,
            biological_sex=biological_sex,
            language=language
        )
        analysis["filename"] = filename
        analysis["extracted_text_preview"] = extracted_text[:500] + ("..." if len(extracted_text) > 500 else "")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the clinical report: {str(e)}"
        )


@router.post("/capture-image")
async def capture_medical_report_image(payload: CameraImageCaptureRequest):
    """
    Accepts base64 encoded photo from device camera (laptop webcam or smartphone camera),
    decodes image bytes, executes OCR, and returns complete clinical report interpretation.
    """
    import base64
    raw_b64 = payload.image_base64
    if "," in raw_b64:
        raw_b64 = raw_b64.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(raw_b64)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid base64 image data: {str(e)}"
        )

    if len(image_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Captured image payload is empty or corrupted."
        )

    extracted_text = report_analyzer.extract_text_from_image(image_bytes)
    if not extracted_text or len(extracted_text.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not detect readable text from the captured image. Please ensure good lighting and align the medical document clearly in the camera frame."
        )

    analysis = report_analyzer.analyze_report(
        raw_text=extracted_text,
        patient_age_group=payload.patient_age_group or "ADULT",
        biological_sex=payload.biological_sex or "UNSPECIFIED",
        language=payload.language or "en"
    )
    analysis["filename"] = payload.filename or "camera_capture.jpg"
    analysis["extracted_text_preview"] = extracted_text[:500] + ("..." if len(extracted_text) > 500 else "")
    return analysis


@router.post("/analyze-text")
async def analyze_report_text(payload: ReportTextAnalysisRequest):
    """
    Direct text analysis for pasted laboratory values or digital OCR transcripts.
    """
    analysis = report_analyzer.analyze_report(
        raw_text=payload.report_text,
        patient_age_group=payload.patient_age_group or "ADULT",
        biological_sex=payload.biological_sex or "UNSPECIFIED",
        language=payload.language or "en"
    )
    return analysis


@router.get("/reference-ranges")
async def get_reference_ranges():
    """
    Returns clinical biomarker reference intervals, panic cut-offs, and clinical significance.
    """
    return {
        "total_biomarkers": len(CLINICAL_BIOMARKER_REGISTRY),
        "biomarkers": CLINICAL_BIOMARKER_REGISTRY
    }


@router.get("/samples")
async def get_sample_reports():
    """
    Returns pre-configured clinical lab reports for immediate demonstration and verification.
    """
    return {
        "samples": SAMPLE_CLINICAL_REPORTS
    }
