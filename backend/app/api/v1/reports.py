from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import Response

from app.engine.report_analyzer import report_analyzer
from app.knowledge.lab_biomarkers import CLINICAL_BIOMARKER_REGISTRY
from app.compliance.security_shield import security_shield, SecurityThreatException

router = APIRouter(prefix="/reports", tags=["Clinical Laboratory Report Analysis"])


class ReportTextAnalysisRequest(BaseModel):
    report_text: str = Field(..., min_length=3, max_length=15000)
    patient_age_group: Optional[str] = "ADULT"
    biological_sex: Optional[str] = "UNSPECIFIED"
    language: Optional[str] = "en"


class ExportSummaryPdfRequest(BaseModel):
    analysis_result: Dict[str, Any]
    patient_name: Optional[str] = "Patient / Walk-in"
    patient_age_sex: Optional[str] = "Adult / Unspecified"


SAMPLE_CLINICAL_REPORTS: List[Dict[str, str]] = []


class CameraImageCaptureRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 data URL or raw base64 string of camera capture")
    filename: Optional[str] = "camera_capture.jpg"
    patient_age_group: Optional[str] = "ADULT"
    biological_sex: Optional[str] = "UNSPECIFIED"
    language: Optional[str] = "en"


ALLOWED_REPORT_EXTENSIONS = (".pdf", ".txt", ".csv", ".text", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")


@router.post("/upload")
async def upload_medical_report(
    file: UploadFile = File(...),
    patient_age_group: str = Form("ADULT"),
    biological_sex: str = Form("UNSPECIFIED"),
    language: str = Form("en")
):
    """
    Accepts single or multi-page laboratory report files (5-10+ page PDF booklets, TXT, CSV, or photographed images),
    executes parallel asynchronous batch OCR across all pages, identifies clinical biomarkers,
    and returns a consolidated clinical interpretation with page-by-page breakdown.
    """
    filename = file.filename or "report.txt"

    if not any(filename.lower().endswith(ext) for ext in ALLOWED_REPORT_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF (.pdf), document (.txt, .csv), or report photo (.png, .jpg, .jpeg, .webp)."
        )

    try:
        content = await file.read()
        if not content or len(content) < 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Uploaded file is empty."
            )

        # Zero-Trust Anti-Malware, Magic-Byte & PDF Active Exploit Inspection
        try:
            inspection = security_shield.inspect_uploaded_file(content, filename)
            safe_filename = inspection["sanitized_filename"]
        except SecurityThreatException as threat:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "security_blocked": True,
                    "threat_category": threat.threat_category,
                    "message_en": threat.message_en,
                    "message_si": threat.message_si,
                }
            )

        analysis = await report_analyzer.analyze_multipage_batch_async(
            files_payload=[(content, safe_filename)],
            patient_age_group=patient_age_group,
            biological_sex=biological_sex,
            language=language
        )
        if not analysis.get("success"):
            err_msg = analysis.get("message_si") if language == "si" else analysis.get("message_en")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=err_msg or "Unable to extract recognized laboratory biomarker values from the document."
            )

        analysis["security_inspection"] = {
            "verified": True,
            "sha256": inspection["sha256"],
            "engine": "MedGuard-ZeroTrust-AntiMalware-v2",
        }
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the clinical report."
        )


@router.post("/upload-batch")
async def upload_medical_reports_batch(
    files: List[UploadFile] = File(...),
    patient_age_group: str = Form("ADULT"),
    biological_sex: str = Form("UNSPECIFIED"),
    language: str = Form("en")
):
    """
    Asynchronous Batch Multi-Page & Multi-File OCR Endpoint.
    Accepts a multi-page PDF booklet OR 1 to 15 separate scanned report pages (PDF/PNG/JPG),
    scans all pages concurrently in background worker threads, and consolidates all biomarkers
    into a single unified dashboard with `page_breakdown`.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one report file or page image."
        )

    files_payload: List[tuple[bytes, str]] = []
    total_batch_bytes = 0
    for f in files[:15]:
        fname = f.filename or "page.png"
        if not any(fname.lower().endswith(ext) for ext in ALLOWED_REPORT_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format for '{fname}'."
            )
        f_bytes = await f.read()
        if f_bytes:
            total_batch_bytes += len(f_bytes)
            if total_batch_bytes > security_shield.MAX_BATCH_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Total batch upload exceeds the 50 MB security quota."
                )
            try:
                inspection = security_shield.inspect_uploaded_file(f_bytes, fname)
                files_payload.append((f_bytes, inspection["sanitized_filename"]))
            except SecurityThreatException as threat:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "security_blocked": True,
                        "threat_category": threat.threat_category,
                        "message_en": threat.message_en,
                        "message_si": threat.message_si,
                    }
                )

    if not files_payload:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded files are empty."
        )

    analysis = await report_analyzer.analyze_multipage_batch_async(
        files_payload=files_payload,
        patient_age_group=patient_age_group,
        biological_sex=biological_sex,
        language=language
    )
    if not analysis.get("success"):
        err_msg = analysis.get("message_si") if language == "si" else analysis.get("message_en")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err_msg or "Unable to extract recognized laboratory biomarker values across the uploaded batch."
        )
    analysis["security_inspection"] = {
        "verified": True,
        "files_scanned": len(files_payload),
        "engine": "MedGuard-ZeroTrust-AntiMalware-v2",
    }
    return analysis


@router.post("/analyze-sample-multipage-pdf")
async def analyze_sample_multipage_pdf_booklet(language: str = "en"):
    """
    Generates a real 6-page PDF Hospital Comprehensive Health Checkup Booklet in memory
    and runs it through the live Multi-Page PDF Asynchronous Batch OCR & Biomarker Engine.
    """
    pdf_bytes = report_analyzer.generate_sample_multipage_pdf_bytes()
    return await report_analyzer.analyze_multipage_batch_async(
        files_payload=[(pdf_bytes, "Asiri_Executive_Health_Checkup_6Pages.pdf")],
        patient_age_group="ADULT",
        biological_sex="UNSPECIFIED",
        language=language
    )


@router.get("/batch-status/{job_id}")
async def get_batch_ocr_job_status(job_id: str):
    """Returns real-time status and telemetry for an asynchronous multi-page batch OCR job."""
    job = report_analyzer.batch_jobs.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch OCR job '{job_id}' not found."
        )
    return job


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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 image data."
        )

    if len(image_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Captured image payload is empty or corrupted."
        )

    try:
        inspection = security_shield.inspect_uploaded_file(
            image_bytes, payload.filename or "camera_capture.jpg"
        )
    except SecurityThreatException as threat:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "security_blocked": True,
                "threat_category": threat.threat_category,
                "message_en": threat.message_en,
                "message_si": threat.message_si,
            }
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
    if not analysis.get("success"):
        err_msg = analysis.get("message_si") if payload.language == "si" else analysis.get("message_en")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err_msg or "Unable to extract recognized laboratory biomarker values from the captured photo."
        )

    analysis["filename"] = inspection["sanitized_filename"]
    analysis["extracted_text_preview"] = extracted_text[:500] + ("..." if len(extracted_text) > 500 else "")
    return analysis


@router.post("/analyze-text")
async def analyze_report_text(payload: ReportTextAnalysisRequest):
    """
    Direct text analysis for pasted laboratory values or digital OCR transcripts.
    """
    try:
        clean_text = security_shield.inspect_text_input(
            payload.report_text, context_label="lab_report_text"
        )
    except SecurityThreatException as threat:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "security_blocked": True,
                "threat_category": threat.threat_category,
                "message_en": threat.message_en,
                "message_si": threat.message_si,
            }
        )

    analysis = report_analyzer.analyze_report(
        raw_text=clean_text,
        patient_age_group=payload.patient_age_group or "ADULT",
        biological_sex=payload.biological_sex or "UNSPECIFIED",
        language=payload.language or "en"
    )
    if not analysis.get("success"):
        err_msg = analysis.get("message_si") if payload.language == "si" else analysis.get("message_en")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err_msg or "Unable to extract recognized laboratory biomarker values from the provided text."
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


@router.post("/export-summary-pdf")
async def export_clinical_summary_pdf(payload: ExportSummaryPdfRequest):
    """
    Generates an official, downloadable PDF 1.4 Medical Assessment & Physician Handover Report
    including all tested biomarkers, High/Low flags, correlated WHO ICD-11 codes, clinical directives,
    and an official cryptographic verification seal stamp.
    """
    if not payload.analysis_result or not isinstance(payload.analysis_result, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid analysis_result object is required to generate the Medical Assessment PDF."
        )

    try:
        safe_patient_name = security_shield.inspect_text_input(
            payload.patient_name or "Patient / Walk-in", context_label="pdf_patient_name"
        )
        safe_patient_age_sex = security_shield.inspect_text_input(
            payload.patient_age_sex or "Adult / Unspecified", context_label="pdf_patient_age_sex"
        )
    except SecurityThreatException as threat:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "security_blocked": True,
                "threat_category": threat.threat_category,
                "message_en": threat.message_en,
                "message_si": threat.message_si,
            }
        )

    pdf_bytes, filename, ref_id = report_analyzer.generate_clinical_assessment_pdf(
        analysis_result=payload.analysis_result,
        patient_name=safe_patient_name,
        patient_age_sex=safe_patient_age_sex,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Report-Ref-Id": ref_id,
            "Access-Control-Expose-Headers": "Content-Disposition, X-Report-Ref-Id",
        },
    )

