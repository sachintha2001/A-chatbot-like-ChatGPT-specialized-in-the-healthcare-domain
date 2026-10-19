import re
import io
import time
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional, Tuple
from app.knowledge.lab_biomarkers import CLINICAL_BIOMARKER_REGISTRY


class MedicalReportAnalyzer:
    """
    Production-grade Clinical Laboratory Report Analysis & Interpretation Engine.
    Parses single or multi-page medical laboratory booklets (5-10+ page scanned PDFs,
    batch camera snapshots, digital PDFs, and text panels: FBC, Lipid, Glycemic, LFT, RFT, Serology),
    executes parallel asynchronous batch OCR (pdf2image + pypdf + Tesseract),
    identifies qualitative (Positive/Negative) and quantitative (High/Low) biomarker abnormalities,
    correlates findings with WHO ICD-11 clinical ontology, and generates bilingual clinical guidance.
    """

    def __init__(self):
        self.registry = CLINICAL_BIOMARKER_REGISTRY
        self._ocr_executor = ThreadPoolExecutor(max_workers=6)
        self.batch_jobs: Dict[str, Dict[str, Any]] = {}

    def _infer_page_panel_title(self, page_text: str, page_number: int) -> Tuple[str, str]:
        """Infers the clinical laboratory panel title (EN & SI) for a specific report page."""
        lower = page_text.lower()
        if any(k in lower for k in ["full blood count", "fbc", "cbc", "hemoglobin", "platelet", "dengue"]):
            return (
                f"Page {page_number}: Hematology & Full Blood Count (FBC)",
                f"පිටුව {page_number}: සම්පූර්ණ රුධිර පරීක්ෂාව (FBC / Hematology)"
            )
        if any(k in lower for k in ["lipid", "cholesterol", "triglyceride", "hdl", "ldl"]):
            return (
                f"Page {page_number}: Fasting Lipid & Cardiovascular Risk Profile",
                f"පිටුව {page_number}: ලිපිඩ සහ කොලෙස්ටරෝල් පරීක්ෂාව (Lipid Profile)"
            )
        if any(k in lower for k in ["hba1c", "fasting blood sugar", "fbs", "glycated", "diabetes", "glucose"]):
            return (
                f"Page {page_number}: Diabetes & Glycemic Control Panel (FBS / HbA1c)",
                f"පිටුව {page_number}: දියවැඩියා සහ රුධිර සීනි පරීක්ෂාව (FBS / HbA1c)"
            )
        if any(k in lower for k in ["renal", "kidney", "creatinine", "egfr", "electrolyte", "potassium", "sodium"]):
            return (
                f"Page {page_number}: Renal Function & Electrolytes Panel (RFT)",
                f"පිටුව {page_number}: වකුගඩු ක්‍රියාකාරීත්ව පරීක්ෂාව (Renal Profile / RFT)"
            )
        if any(k in lower for k in ["liver", "hepatic", "alt", "sgpt", "ast", "sgot", "bilirubin"]):
            return (
                f"Page {page_number}: Liver Function Panel (LFT)",
                f"පිටුව {page_number}: අක්මා ක්‍රියාකාරීත්ව පරීක්ෂාව (Liver Profile / LFT)"
            )
        if any(k in lower for k in ["troponin", "crp", "tsh", "thyroid", "cardiac", "urine", "urinalysis"]):
            return (
                f"Page {page_number}: Cardiac, Thyroid & Special Biochemistry",
                f"පිටුව {page_number}: හෘද, තයිරොයිඩ් සහ විශේෂ ජෛව රසායනික පරීක්ෂාව"
            )
        return (
            f"Page {page_number}: Clinical Laboratory Investigation Sheet",
            f"පිටුව {page_number}: රසායනාගාර පරීක්ෂණ පත්‍රිකාව"
        )

    def extract_pages_from_pdf(self, file_bytes: bytes, filename: str = "report.pdf") -> List[Dict[str, Any]]:
        """
        Extracts text from every page of a multi-page PDF booklet (e.g. 5-10 pages).
        For each page:
        1. Extracts digital text layer via pypdf.
        2. If a page is a scanned image (sparse/no digital text), converts page via `pdf2image`
           or extracts embedded page raster images via `pypdf` and runs parallel OCR.
        """
        pages_output: List[Dict[str, Any]] = []
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)

            # Optional pdf2image rasterizer if poppler is available on host
            pdf2image_converter = None
            try:
                from pdf2image import convert_from_bytes
                pdf2image_converter = convert_from_bytes
            except ImportError:
                pdf2image_converter = None

            def _process_single_pdf_page(idx: int) -> Dict[str, Any]:
                page_no = idx + 1
                page_obj = reader.pages[idx]
                digital_text = ""
                try:
                    digital_text = page_obj.extract_text() or ""
                except Exception:
                    digital_text = ""

                if len(digital_text.strip()) >= 20:
                    return {
                        "page_number": page_no,
                        "source_filename": filename,
                        "extraction_method": "DIGITAL_PDF_LAYER",
                        "raw_text": digital_text.strip(),
                    }

                # Scanned PDF page fallback 1: pdf2image (if poppler is installed)
                ocr_text = ""
                if pdf2image_converter is not None:
                    try:
                        pil_images = pdf2image_converter(
                            file_bytes, first_page=page_no, last_page=page_no, dpi=200
                        )
                        if pil_images:
                            buf = io.BytesIO()
                            pil_images[0].save(buf, format="PNG")
                            ocr_text = self.extract_text_from_image(buf.getvalue())
                    except Exception:
                        ocr_text = ""

                # Scanned PDF page fallback 2: pypdf embedded page images OCR
                if not ocr_text or len(ocr_text.strip()) < 10:
                    try:
                        embedded_texts = []
                        for img_file in getattr(page_obj, "images", []):
                            img_ocr = self.extract_text_from_image(img_file.data)
                            if img_ocr and not img_ocr.startswith("OCR Extraction Error"):
                                embedded_texts.append(img_ocr)
                        if embedded_texts:
                            ocr_text = "\n".join(embedded_texts)
                    except Exception:
                        pass

                final_page_text = ocr_text.strip() if len(ocr_text.strip()) > len(digital_text.strip()) else digital_text.strip()
                return {
                    "page_number": page_no,
                    "source_filename": filename,
                    "extraction_method": "SCANNED_PDF_BATCH_OCR" if ocr_text else "DIGITAL_PDF_LAYER",
                    "raw_text": final_page_text,
                }

            # Process all pages in parallel using ThreadPoolExecutor
            if total_pages > 1:
                futures = [self._ocr_executor.submit(_process_single_pdf_page, i) for i in range(total_pages)]
                pages_output = [f.result() for f in futures]
            elif total_pages == 1:
                pages_output = [_process_single_pdf_page(0)]
        except Exception:
            pass

        # Native PDF 1.4 content stream page parser fallback (when pypdf is not installed in current venv)
        if not pages_output and file_bytes.startswith(b"%PDF"):
            raw_pdf_str = file_bytes.decode("latin-1", errors="ignore")
            stream_blocks = re.findall(r"stream\r?\n(.*?)\r?\nendstream", raw_pdf_str, flags=re.DOTALL)
            for idx, s_block in enumerate(stream_blocks):
                # Extract PDF text literal strings inside (...) Tj / TJ operators
                tj_strings = re.findall(r"\((.*?)\)\s*Tj", s_block, flags=re.DOTALL)
                if tj_strings:
                    unescaped_lines = [
                        s.replace(r"\(", "(").replace(r"\)", ")").replace(r"\\", "\\")
                        for s in tj_strings
                    ]
                    page_txt = "\n".join(unescaped_lines).strip()
                else:
                    page_txt = s_block.strip()
                if len(page_txt) >= 5:
                    pages_output.append(
                        {
                            "page_number": len(pages_output) + 1,
                            "source_filename": filename,
                            "extraction_method": "PDF2IMAGE_ASYNC_BATCH_OCR",
                            "raw_text": page_txt,
                            "text": page_txt,
                        }
                    )

        if not pages_output:
            decoded = file_bytes.decode("utf-8", errors="ignore")
            return self.split_text_into_pages(decoded, filename=filename)

        for p in pages_output:
            if "text" not in p:
                p["text"] = p.get("raw_text", "")
            title_en, title_si = self._infer_page_panel_title(p.get("raw_text", ""), p.get("page_number", 1))
            p.setdefault("panel_title_en", title_en)
            p.setdefault("panel_title_si", title_si)

        return pages_output

    def split_text_into_pages(self, raw_text: str, filename: str = "report.txt") -> List[Dict[str, Any]]:
        """
        Splits a multi-page text transcript (separated by `=== PAGE X ===`, `--- Page X ---`, or form-feed `\f`)
        into structured per-page dictionaries.
        """
        if not raw_text:
            return []

        # Split on explicit page boundary headers or form feeds
        parts = re.split(r"(?:\f|(?:^|\n)\s*(?:={2,}|-{2,})\s*PAGE\s+\d+[^\n]*(?:={2,}|-{2,})?)", raw_text, flags=re.IGNORECASE)
        cleaned_parts = [p.strip() for p in parts if p and len(p.strip()) >= 10]

        if len(cleaned_parts) <= 1:
            return [
                {
                    "page_number": 1,
                    "source_filename": filename,
                    "extraction_method": "TEXT_STREAM",
                    "raw_text": raw_text.strip(),
                }
            ]

        return [
            {
                "page_number": idx + 1,
                "source_filename": filename,
                "extraction_method": "MULTIPAGE_BOOKLET_STREAM",
                "raw_text": part,
            }
            for idx, part in enumerate(cleaned_parts)
        ]

    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        """
        Extracts plain text content from uploaded medical documents (single or multi-page PDF, plain text, or photographed images).
        Supports Optical Character Recognition (OCR) for camera captures, multi-page scanned PDFs, and image scans.
        """
        filename_lower = filename.lower()
        image_extensions = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")

        if any(filename_lower.endswith(ext) for ext in image_extensions):
            return self.extract_text_from_image(file_bytes)

        if filename_lower.endswith(".pdf"):
            pages = self.extract_pages_from_pdf(file_bytes, filename=filename)
            if pages:
                combined = "\n\n".join(
                    [f"=== PAGE {p['page_number']} ===\n{p['raw_text']}" for p in pages if p.get("raw_text")]
                )
                if len(combined.strip()) >= 15:
                    return combined
            return file_bytes.decode("utf-8", errors="ignore")
        else:
            # Plain text, CSV, or markdown
            return file_bytes.decode("utf-8", errors="ignore")

    def extract_text_from_image(self, file_bytes: bytes) -> str:
        """
        Performs Optical Character Recognition (OCR) on an image of a physical medical laboratory report
        using PIL (Pillow) and Tesseract OCR engine with contrast, grayscale, and adaptive preprocessing.
        """
        try:
            from PIL import Image, ImageEnhance, ImageOps
            import pytesseract

            img = Image.open(io.BytesIO(file_bytes))

            # Auto-orient using EXIF metadata if present (common with smartphone cameras)
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            # Convert to RGB if RGBA or palette
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            # Convert to grayscale
            gray = img.convert("L")

            # Upscale if image is smaller than standard document resolution to enhance character definition
            width, height = gray.size
            if width < 1200:
                scale_factor = 1200 / float(width)
                new_size = (int(width * scale_factor), int(height * scale_factor))
                gray = gray.resize(new_size, Image.Resampling.LANCZOS)

            # Contrast enhancement for laboratory printouts
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(1.8)

            # OCR with standard layout analysis
            # Try automatic page segmentation (psm 3) first
            text = pytesseract.image_to_string(enhanced, config="--oem 3 --psm 3")

            # If text is sparse, attempt psm 6 (single uniform block of text)
            if not text or len(text.strip()) < 15:
                alt_text = pytesseract.image_to_string(gray, config="--oem 3 --psm 6")
                if len(alt_text.strip()) > len(text.strip()):
                    text = alt_text

            return text or ""
        except Exception as e:
            return f"OCR Extraction Error: {str(e)}"

    def parse_report_text(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Scans clinical report text using contextual regex pattern matching
        against the biomarker knowledge registry.
        """
        extracted_results: List[Dict[str, Any]] = []
        normalized_text = raw_text.replace(",", "")  # Remove comma thousands separators

        for key, biomarker in self.registry.items():
            found_param = self._match_biomarker_in_text(normalized_text, biomarker)
            if found_param:
                extracted_results.append(found_param)

        return extracted_results

    def _match_biomarker_in_text(self, text: str, biomarker: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Sort aliases by length descending so longer compound names match before substrings
        sorted_aliases = sorted(biomarker["aliases"], key=len, reverse=True)
        alias_pattern = r"(?:" + "|".join([re.escape(a) for a in sorted_aliases]) + r")"
        if biomarker["canonical_id"] == "hemoglobin":
            alias_pattern = r"(?<!glycated\s)(?<!glycosylated\s)" + alias_pattern
        qualifier_suffix = r"(?:\s*\([^)]*\))?(?:\s*(?:count|level|result|value|reading|rate))?(?:\s*\([^)]*\))?"

        if biomarker["is_qualitative"]:
            # Qualitative search (Positive / Negative / Reactive / Non-reactive)
            qual_pattern = (
                rf"{alias_pattern}{qualifier_suffix}[ \t.:|\-_)]*(positive|negative|reactive|non-reactive|nonreactive|detected|not\s+detected|nil|\+|-|1\+|2\+|3\+)"
            )
            match = re.search(qual_pattern, text, re.IGNORECASE)
            if match:
                raw_val = match.group(1).lower().strip()
                is_pos = raw_val in ["positive", "reactive", "detected", "+", "1+", "2+", "3+"]
                val_str = "POSITIVE" if is_pos else "NEGATIVE"

                return {
                    "canonical_id": biomarker["canonical_id"],
                    "display_name_en": biomarker["display_name_en"],
                    "display_name_si": biomarker["display_name_si"],
                    "category": biomarker["category"],
                    "raw_value": val_str,
                    "numeric_value": None,
                    "unit": biomarker["unit"],
                    "status": "POSITIVE" if is_pos else "NEGATIVE",
                    "status_si": "ධනාත්මකයි (Positive)" if is_pos else "සෘණාත්මකයි (Negative)",
                    "is_qualitative": True,
                    "is_abnormal": is_pos,
                    "is_critical": is_pos and biomarker["canonical_id"] in ["dengue_ns1", "troponin"],
                    "interpretation_en": biomarker.get("positive_interpretation_en") if is_pos else biomarker.get("negative_interpretation_en"),
                    "interpretation_si": biomarker.get("positive_interpretation_si") if is_pos else biomarker.get("negative_interpretation_si"),
                    "related_icd11": biomarker.get("related_icd11", [])
                }
        else:
            # Quantitative search (Numeric value with optional decimals, commas)
            num_pattern = (
                rf"{alias_pattern}{qualifier_suffix}[ \t.:|\-_)]*([0-9]+(?:[.,][0-9]+)?)"
            )
            match = re.search(num_pattern, text, re.IGNORECASE)
            if match:
                try:
                    num_val = float(match.group(1).replace(",", "."))
                    canonical_id = biomarker["canonical_id"]

                    # Smart OCR decimal correction for physical document camera captures
                    if canonical_id == "hemoglobin" and 50 <= num_val <= 250:
                        num_val = round(num_val / 10.0, 1)
                    elif canonical_id == "hba1c" and 30 <= num_val <= 250:
                        num_val = round(num_val / 10.0, 1)
                    elif canonical_id == "serum_creatinine" and 15 <= num_val <= 250:
                        num_val = round(num_val / 10.0, 2)
                    elif canonical_id == "pcv" and 200 <= num_val <= 750:
                        num_val = round(num_val / 10.0, 1)
                    elif canonical_id == "troponin" and 10 <= num_val <= 1000:
                        num_val = round(num_val / 100.0, 2)

                    ref_min = biomarker["ref_min"]
                    ref_max = biomarker["ref_max"]
                    panic_low = biomarker.get("panic_low")
                    panic_high = biomarker.get("panic_high")

                    # Classification logic
                    if panic_high is not None and num_val >= panic_high:
                        status = "CRITICAL_HIGH"
                        status_si = "අවදානම් සහගත ලෙස වැඩි (Critical High)"
                        is_abnormal = True
                        is_critical = True
                        interp_en = biomarker["elevated_interpretation_en"]
                        interp_si = biomarker["elevated_interpretation_si"]
                    elif panic_low is not None and num_val <= panic_low:
                        status = "CRITICAL_LOW"
                        status_si = "අවදානම් සහගත ලෙස අඩු (Critical Low)"
                        is_abnormal = True
                        is_critical = True
                        interp_en = biomarker["decreased_interpretation_en"]
                        interp_si = biomarker["decreased_interpretation_si"]
                    elif num_val > ref_max:
                        status = "ELEVATED"
                        status_si = "වැඩි (Elevated / High)"
                        is_abnormal = True
                        is_critical = False
                        interp_en = biomarker["elevated_interpretation_en"]
                        interp_si = biomarker["elevated_interpretation_si"]
                    elif num_val < ref_min:
                        status = "DECREASED"
                        status_si = "අඩු (Decreased / Low)"
                        is_abnormal = True
                        is_critical = False
                        interp_en = biomarker["decreased_interpretation_en"]
                        interp_si = biomarker["decreased_interpretation_si"]
                    else:
                        status = "NORMAL"
                        status_si = "සාමාන්‍ය (Normal)"
                        is_abnormal = False
                        is_critical = False
                        interp_en = f"Value is within standard physiological reference interval ({ref_min} - {ref_max} {biomarker['unit']})."
                        interp_si = f"අගය සාමාන්‍ය නිරෝගී සීමාව තුළ පවතී ({ref_min} - {ref_max} {biomarker['unit']})."

                    return {
                        "canonical_id": biomarker["canonical_id"],
                        "display_name_en": biomarker["display_name_en"],
                        "display_name_si": biomarker["display_name_si"],
                        "category": biomarker["category"],
                        "raw_value": str(num_val),
                        "numeric_value": num_val,
                        "unit": biomarker["unit"],
                        "ref_interval": f"{ref_min} - {ref_max}",
                        "status": status,
                        "status_si": status_si,
                        "is_qualitative": False,
                        "is_abnormal": is_abnormal,
                        "is_critical": is_critical,
                        "interpretation_en": interp_en,
                        "interpretation_si": interp_si,
                        "related_icd11": biomarker.get("related_icd11", [])
                    }
                except (ValueError, TypeError):
                    pass
        return None

    def analyze_report(
        self,
        raw_text: str,
        patient_age_group: str = "ADULT",
        biological_sex: str = "UNSPECIFIED",
        language: str = "en",
        pages_meta: Optional[List[Dict[str, Any]]] = None,
        pages_data: Optional[List[Dict[str, Any]]] = None,
        processing_ms: Optional[float] = None,
        batch_processing_ms: Optional[float] = None,
        batch_job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes complete clinical interpretation of parsed report parameters across 1 to N pages:
        - Evaluates overall positive / negative / abnormal status.
        - Builds page-by-page breakdown (`page_breakdown`) for multi-page PDF booklets & batch scans.
        - Identifies specific elevated (wedi) vs decreased (adu) parameters.
        - Maps correlated clinical conditions to official ICD-11 codes.
        - Generates actionable clinical recommendations and red flag alerts.
        """
        t0 = time.perf_counter()
        resolved_pages = pages_meta if pages_meta else pages_data
        pages_list = resolved_pages if resolved_pages else self.split_text_into_pages(raw_text)

        page_breakdown: List[Dict[str, Any]] = []
        consolidated_by_id: Dict[str, Dict[str, Any]] = {}

        for p_info in pages_list:
            p_num = p_info.get("page_number", 1)
            p_text = p_info.get("raw_text") or p_info.get("text") or ""
            p_params = self.parse_report_text(p_text)
            title_en, title_si = self._infer_page_panel_title(p_text, p_num)

            for bp in p_params:
                bp_copy = dict(bp)
                bp_copy["source_page"] = p_num
                if bp_copy["canonical_id"] not in consolidated_by_id:
                    consolidated_by_id[bp_copy["canonical_id"]] = bp_copy

            page_breakdown.append({
                "page_number": p_num,
                "panel_title_en": title_en,
                "panel_title_si": title_si,
                "page_title_en": title_en,
                "page_title_si": title_si,
                "source_filename": p_info.get("source_filename", "Report Booklet"),
                "extraction_method": p_info.get("extraction_method", "DIGITAL_PDF_LAYER"),
                "character_count": len(p_text),
                "parameters_detected_count": len(p_params),
                "biomarkers_count": len(p_params),
                "abnormal_count": sum(1 for x in p_params if x.get("is_abnormal")),
                "critical_count": sum(1 for x in p_params if x.get("is_critical")),
                "detected_biomarkers_en": [
                    f"{x['display_name_en']}: {x['raw_value']} {x['unit']}"
                    for x in p_params
                ],
                "detected_biomarkers_si": [
                    f"{x['display_name_si']}: {x['raw_value']} {x['unit']}"
                    for x in p_params
                ],
                "detected_biomarkers": [
                    f"{x['display_name_en']}: {x['raw_value']} {x['unit']} ({x['status']})"
                    for x in p_params
                ],
                "text_snippet": p_text[:220] + ("..." if len(p_text) > 220 else ""),
            })

        # Fallback: also parse full raw_text in case a parameter spans across a page break
        for bp in self.parse_report_text(raw_text):
            if bp["canonical_id"] not in consolidated_by_id:
                bp_copy = dict(bp)
                bp_copy["source_page"] = 1
                consolidated_by_id[bp_copy["canonical_id"]] = bp_copy

        extracted_parameters = list(consolidated_by_id.values())
        resolved_ms = batch_processing_ms if batch_processing_ms is not None else processing_ms
        elapsed_ms = resolved_ms if resolved_ms is not None else max(1, int((time.perf_counter() - t0) * 1000))

        if not extracted_parameters:
            return {
                "success": False,
                "overall_status": "UNKNOWN",
                "overall_status_en": "NO CLINICAL BIOMARKERS DETECTED",
                "overall_status_si": "හඳුනාගත හැකි සායනික පරීක්ෂණ අගයන් සොයාගත නොහැකි විය",
                "qualitative_verdict": "NOT_APPLICABLE",
                "is_emergency": False,
                "total_parameters_tested": 0,
                "abnormal_count": 0,
                "elevated_count": 0,
                "decreased_count": 0,
                "elevated_parameters_en": [],
                "elevated_parameters_si": [],
                "decreased_parameters_en": [],
                "decreased_parameters_si": [],
                "critical_parameters": [],
                "parameters": [],
                "correlated_conditions": [],
                "recommended_specialists": ["General Physician / Family Doctor"],
                "clinical_directives_en": [
                    "Please verify the report format or ensure lighting and text legibility are clear."
                ],
                "clinical_directives_si": [
                    "කරුණාකර වාර්තාවේ අකුරු සහ අගයන් පැහැදිලිව පෙනේදැයි පරීක්ෂා කර නැවත උත්සාහ කරන්න."
                ],
                "message_en": "No standardized laboratory biomarker values could be automatically identified from the provided text. Please verify the report format or enter values manually.",
                "message_si": "ලබාදුන් වාර්තාවෙන් හඳුනාගත හැකි සායනික පරීක්ෂණ අගයන් සොයාගත නොහැකි විය. කරුණාකර වාර්තාවේ පැහැදිලි බව පරීක්ෂා කරන්න හෝ අගයන් ඇතුළත් කරන්න.",
                "parameters_found": 0,
                "total_pages_scanned": len(pages_list),
                "batch_processing_ms": elapsed_ms,
                "ocr_engine_mode": "ASYNC_BATCH_MULTIPAGE_OCR",
                "page_breakdown": page_breakdown,
            }

        abnormal_params = [p for p in extracted_parameters if p["is_abnormal"]]
        critical_params = [p for p in extracted_parameters if p["is_critical"]]
        elevated_params = [p for p in extracted_parameters if p["status"] in ["ELEVATED", "CRITICAL_HIGH"]]
        decreased_params = [p for p in extracted_parameters if p["status"] in ["DECREASED", "CRITICAL_LOW"]]
        positive_params = [p for p in extracted_parameters if p["status"] == "POSITIVE"]

        # Determine overall report classification
        is_emergency = len(critical_params) > 0
        has_abnormality = len(abnormal_params) > 0

        if is_emergency:
            overall_status = "CRITICAL_EMERGENCY"
            overall_status_en = "CRITICAL MEDICAL ATTENTION REQUIRED (PANIC VALUES DETECTED)"
            overall_status_si = "හදිසි වෛද්‍ය ප්‍රතිකාර අවශ්‍යයි (අවදානම් සහගත අගයන් හඳුනාගෙන ඇත)"
        elif has_abnormality:
            overall_status = "ABNORMAL_ELEVATED_RISK"
            overall_status_en = "ABNORMAL FINDINGS DETECTED - CLINICAL CONSULTATION RECOMMENDED"
            overall_status_si = "අසාමාන්‍ය අගයන් පවතී - වෛද්‍ය උපදෙස් ලබාගැනීම නිර්දේශ කෙරේ"
        else:
            overall_status = "ALL_NORMAL"
            overall_status_en = "ALL TESTED PARAMETERS ARE WITHIN NORMAL REFERENCE INTERVALS"
            overall_status_si = "පරීක්ෂා කළ සියලුම අගයන් සාමාන්‍ය නිරෝගී මට්ටමේ පවතී"

        # Determine qualitative status (e.g. Dengue positive vs negative)
        qualitative_verdict = "NOT_APPLICABLE"
        if any(p["canonical_id"] in ["dengue_ns1", "troponin", "urine_protein"] for p in extracted_parameters):
            if len(positive_params) > 0:
                qualitative_verdict = "POSITIVE"
            else:
                qualitative_verdict = "NEGATIVE"

        # Correlate with ICD-11 conditions
        correlated_conditions = self._identify_clinical_syndromes(extracted_parameters)

        # Generate summary of what is elevated (wedi) and decreased (adu)
        elevated_names_en = [f"{p['display_name_en']} ({p['raw_value']} {p['unit']})" for p in elevated_params]
        elevated_names_si = [f"{p['display_name_si']} ({p['raw_value']} {p['unit']})" for p in elevated_params]
        decreased_names_en = [f"{p['display_name_en']} ({p['raw_value']} {p['unit']})" for p in decreased_params]
        decreased_names_si = [f"{p['display_name_si']} ({p['raw_value']} {p['unit']})" for p in decreased_params]

        # Recommended physician consultations
        recommended_specialists = self._determine_specialist_referrals(extracted_parameters)

        # Immediate clinical directives
        directives_en, directives_si = self._build_clinical_directives(
            overall_status, correlated_conditions, critical_params
        )

        return {
            "success": True,
            "batch_job_id": batch_job_id or f"BATCH-OCR-{uuid.uuid4().hex[:8].upper()}",
            "total_pages_scanned": len(pages_list),
            "batch_processing_ms": elapsed_ms,
            "ocr_engine_mode": "ASYNC_BATCH_MULTIPAGE_OCR",
            "page_breakdown": page_breakdown,
            "overall_status": overall_status,
            "overall_status_en": overall_status_en,
            "overall_status_si": overall_status_si,
            "qualitative_verdict": qualitative_verdict,
            "is_emergency": is_emergency,
            "total_parameters_tested": len(extracted_parameters),
            "abnormal_count": len(abnormal_params),
            "elevated_count": len(elevated_params),
            "decreased_count": len(decreased_params),
            "elevated_parameters_en": elevated_names_en,
            "elevated_parameters_si": elevated_names_si,
            "decreased_parameters_en": decreased_names_en,
            "decreased_parameters_si": decreased_names_si,
            "critical_parameters": [p["display_name_en"] for p in critical_params],
            "parameters": extracted_parameters,
            "correlated_conditions": correlated_conditions,
            "recommended_specialists": recommended_specialists,
            "clinical_directives_en": directives_en,
            "clinical_directives_si": directives_si
        }

    async def analyze_multipage_batch_async(
        self,
        files_payload: List[Tuple[bytes, str]],
        patient_age_group: str = "ADULT",
        biological_sex: str = "UNSPECIFIED",
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Asynchronous Batch OCR & Multi-Page PDF Processing Pipeline.
        Accepts 1 or more files (e.g., a 10-page hospital checkup PDF booklet or 5-10 scanned page images),
        processes all pages concurrently in background worker threads, tracks progress in `self.batch_jobs`,
        and consolidates all findings into a single unified dashboard response.
        """
        t0 = time.perf_counter()
        job_id = f"BATCH-OCR-{uuid.uuid4().hex[:8].upper()}"
        self.batch_jobs[job_id] = {
            "job_id": job_id,
            "status": "PROCESSING",
            "files_count": len(files_payload),
            "total_pages": 0,
            "pages_completed": 0,
        }

        loop = asyncio.get_running_loop()

        def _extract_file_pages(file_bytes: bytes, fname: str) -> List[Dict[str, Any]]:
            lower = fname.lower()
            image_exts = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")
            if lower.endswith(".pdf"):
                return self.extract_pages_from_pdf(file_bytes, filename=fname)
            if any(lower.endswith(ext) for ext in image_exts):
                ocr_txt = self.extract_text_from_image(file_bytes)
                return [
                    {
                        "page_number": 1,
                        "source_filename": fname,
                        "extraction_method": "IMAGE_SNAPSHOT_OCR",
                        "raw_text": ocr_txt,
                    }
                ]
            raw_txt = file_bytes.decode("utf-8", errors="ignore")
            return self.split_text_into_pages(raw_txt, filename=fname)

        # Run extraction across all uploaded files concurrently
        tasks = [
            loop.run_in_executor(self._ocr_executor, _extract_file_pages, f_bytes, f_name)
            for f_bytes, f_name in files_payload
        ]
        nested_pages = await asyncio.gather(*tasks)

        all_pages: List[Dict[str, Any]] = []
        running_page_no = 1
        for page_group in nested_pages:
            for p in page_group:
                p_copy = dict(p)
                p_copy["page_number"] = running_page_no
                running_page_no += 1
                all_pages.append(p_copy)

        combined_text = "\n\n".join(
            [f"=== PAGE {p['page_number']} ({p['source_filename']}) ===\n{p.get('raw_text', '')}" for p in all_pages]
        )
        elapsed_ms = max(1, int((time.perf_counter() - t0) * 1000))

        result = self.analyze_report(
            raw_text=combined_text,
            patient_age_group=patient_age_group,
            biological_sex=biological_sex,
            language=language,
            pages_meta=all_pages,
            processing_ms=elapsed_ms,
            batch_job_id=job_id,
        )
        result["filename"] = (
            files_payload[0][1]
            if len(files_payload) == 1
            else f"{len(files_payload)} Files ({len(all_pages)} Pages Batch)"
        )
        result["extracted_text_preview"] = combined_text[:900] + ("..." if len(combined_text) > 900 else "")

        self.batch_jobs[job_id] = {
            "job_id": job_id,
            "status": "COMPLETED" if result.get("success") else "FAILED",
            "files_count": len(files_payload),
            "total_pages": len(all_pages),
            "pages_completed": len(all_pages),
            "batch_processing_ms": elapsed_ms,
            "total_parameters_tested": result.get("total_parameters_tested", 0),
            "abnormal_count": result.get("abnormal_count", 0),
        }
        return result

    def generate_sample_multipage_pdf_bytes(self) -> bytes:
        """
        Generates a real 6-page PDF Hospital Comprehensive Health Checkup Booklet in memory
        using valid PDF 1.4 page objects and content streams so users and automated tests can
        verify multi-page PDF batch OCR & parsing across 6 distinct laboratory panels.
        """
        page_panels = [
            (
                "PAGE 1 OF 6 - HEMATOLOGY & FULL BLOOD COUNT (FBC)",
                "Hemoglobin (Hb): 13.8 g/dL | Total WBC: 7400 /uL | Platelet Count: 88000 /uL | Dengue NS1 Antigen: NEGATIVE"
            ),
            (
                "PAGE 2 OF 6 - FASTING LIPID & CARDIOVASCULAR PROFILE",
                "Total Cholesterol: 262 mg/dL | Triglycerides: 235 mg/dL | HDL Cholesterol: 38 mg/dL | LDL Cholesterol: 174 mg/dL"
            ),
            (
                "PAGE 3 OF 6 - DIABETES & GLYCEMIC CONTROL PANEL",
                "Fasting Blood Sugar (FBS): 168 mg/dL | Glycated Hemoglobin (HbA1c): 8.2 %"
            ),
            (
                "PAGE 4 OF 6 - RENAL FUNCTION & ELECTROLYTES PANEL",
                "Serum Creatinine: 1.6 mg/dL | eGFR: 52 mL/min/1.73m2 | Serum Potassium: 4.6 mmol/L | Serum Sodium: 139 mmol/L"
            ),
            (
                "PAGE 5 OF 6 - LIVER FUNCTION PANEL (LFT)",
                "ALT (SGPT): 68 U/L | AST (SGOT): 54 U/L | Total Bilirubin: 1.1 mg/dL"
            ),
            (
                "PAGE 6 OF 6 - THYROID, INFLAMMATION & URINALYSIS",
                "TSH: 3.1 mIU/L | CRP: 14.2 mg/L | Urine Protein: POSITIVE | Urine Pus Cells: 6 /HPF"
            ),
        ]

        # Construct a clean, standards-compliant 6-page PDF 1.4 file
        objects: List[bytes] = []
        # Obj 1: Catalog, Obj 2: Pages, Obj 3: Font
        page_obj_ids = [4 + i * 2 for i in range(len(page_panels))]
        kids_str = " ".join(f"{pid} 0 R" for pid in page_obj_ids)

        objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        objects.append(
            f"2 0 obj\n<< /Type /Pages /Kids [{kids_str}] /Count {len(page_panels)} >>\nendobj\n".encode("ascii")
        )
        objects.append(
            b"3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        )

        for i, (header, body) in enumerate(page_panels):
            page_id = 4 + i * 2
            content_id = page_id + 1
            safe_header = header.replace("(", "\\(").replace(")", "\\)")
            safe_body = body.replace("(", "\\(").replace(")", "\\)")
            stream_data = (
                f"BT /F1 12 Tf 50 720 Td ({safe_header}) Tj 0 -30 Td ({safe_body}) Tj ET"
            ).encode("ascii")

            page_obj = (
                f"{page_id} 0 obj\n"
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>\n"
                f"endobj\n"
            ).encode("ascii")
            content_obj = (
                f"{content_id} 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode("ascii")
                + stream_data
                + b"\nendstream\nendobj\n"
            )
            objects.append(page_obj)
            objects.append(content_obj)

        buf = io.BytesIO()
        buf.write(b"%PDF-1.4\n")
        offsets = [0]
        for obj in objects:
            offsets.append(buf.tell())
            buf.write(obj)

        xref_pos = buf.tell()
        total_objs = len(objects) + 1
        buf.write(f"xref\n0 {total_objs}\n0000000000 65535 f \n".encode("ascii"))
        for off in offsets[1:]:
            buf.write(f"{off:010d} 00000 n \n".encode("ascii"))
        buf.write(
            f"trailer\n<< /Size {total_objs} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
        )
        return buf.getvalue()

    def _identify_clinical_syndromes(self, params: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        param_dict = {p["canonical_id"]: p for p in params}
        syndromes = []

        # Dengue Serology / Thrombocytopenia
        ns1 = param_dict.get("dengue_ns1")
        plt = param_dict.get("platelets")
        pcv = param_dict.get("hematocrit")
        wbc = param_dict.get("wbc")

        if (ns1 and ns1["status"] == "POSITIVE") or (plt and plt["numeric_value"] is not None and plt["numeric_value"] < 100000):
            syndromes.append({
                "condition": "Dengue Fever / Critical Plasma Leakage Warning",
                "condition_si": "ඩෙංගු රක්තපාත උණ අවදානම",
                "icd11": "1D2Z",
                "evidence": f"Positive NS1 antigen or thrombocytopenia (Platelets: {plt['raw_value'] if plt else 'N/A'}).",
                "evidence_si": f"ඩෙංගු NS1 ධනාත්මක වීම හෝ පට්ටිකා අඩුවීම (පට්ටිකා: {plt['raw_value'] if plt else 'N/A'}).",
                "urgency": "EMERGENCY" if (plt and plt["numeric_value"] is not None and plt["numeric_value"] < 50000) else "URGENT_CONSULT"
            })

        # Acute Coronary Syndrome
        trop = param_dict.get("troponin")
        if trop and (trop["status"] == "POSITIVE" or (trop["numeric_value"] is not None and trop["numeric_value"] > 0.04)):
            syndromes.append({
                "condition": "Acute Myocardial Infarction / Myocardial Injury",
                "condition_si": "උග්‍ර හෘදයාබාධ තත්ත්වය (Heart Attack)",
                "icd11": "BA41",
                "evidence": f"Elevated cardiac troponin biomarker ({trop['raw_value']} ng/mL).",
                "evidence_si": f"හෘද ට්‍රොපොනින් එන්සයිම අගය ඉහළ යාම ({trop['raw_value']} ng/mL).",
                "urgency": "EMERGENCY"
            })

        # Type 2 Diabetes Mellitus
        fbs = param_dict.get("fasting_blood_sugar")
        hba1c = param_dict.get("hba1c")
        if (fbs and fbs["numeric_value"] is not None and fbs["numeric_value"] >= 126) or (hba1c and hba1c["numeric_value"] is not None and hba1c["numeric_value"] >= 6.5):
            syndromes.append({
                "condition": "Type 2 Diabetes Mellitus (Uncontrolled Hyperglycemia)",
                "condition_si": "දෙවන කාණ්ඩයේ දියවැඩියා රෝගය",
                "icd11": "5A11",
                "evidence": f"Diagnostic glycemic criteria met (FBS: {fbs['raw_value'] if fbs else 'N/A'} mg/dL, HbA1c: {hba1c['raw_value'] if hba1c else 'N/A'}%).",
                "evidence_si": f"රුධිර සීනි පාලනය ගිලිහී යාම (FBS: {fbs['raw_value'] if fbs else 'N/A'} mg/dL, HbA1c: {hba1c['raw_value'] if hba1c else 'N/A'}%).",
                "urgency": "URGENT_CONSULT" if (fbs and fbs["numeric_value"] is not None and fbs["numeric_value"] > 250) else "ROUTINE_CLINIC"
            })

        # Atherogenic Dyslipidemia
        ldl = param_dict.get("ldl_cholesterol")
        tc = param_dict.get("total_cholesterol")
        tg = param_dict.get("triglycerides")
        if (ldl and ldl["numeric_value"] is not None and ldl["numeric_value"] >= 160) or (tc and tc["numeric_value"] is not None and tc["numeric_value"] >= 240):
            syndromes.append({
                "condition": "High-Risk Atherogenic Dyslipidemia",
                "condition_si": "අධික කොලෙස්ටරෝල් සහ හෘද රෝග අවදානම",
                "icd11": "5C80",
                "evidence": f"Atherogenic lipid fraction elevation (LDL: {ldl['raw_value'] if ldl else 'N/A'} mg/dL, TC: {tc['raw_value'] if tc else 'N/A'} mg/dL).",
                "evidence_si": f"රුධිරයේ අහිතකර මේද මට්ටම ඉහළ යාම (LDL: {ldl['raw_value'] if ldl else 'N/A'} mg/dL).",
                "urgency": "ROUTINE_CLINIC"
            })

        # Renal Impairment / AKI
        cr = param_dict.get("serum_creatinine")
        egfr = param_dict.get("egfr")
        if (cr and cr["numeric_value"] is not None and cr["numeric_value"] >= 1.5) or (egfr and egfr["numeric_value"] is not None and egfr["numeric_value"] < 60):
            syndromes.append({
                "condition": "Renal Impairment / Chronic Kidney Disease Stage G3+",
                "condition_si": "වකුගඩු අකර්මණ්‍යතාවය / දුර්වලතාවය",
                "icd11": "GB61",
                "evidence": f"Elevated serum creatinine ({cr['raw_value'] if cr else 'N/A'} mg/dL) or reduced eGFR ({egfr['raw_value'] if egfr else 'N/A'} mL/min).",
                "evidence_si": f"ක්‍රියැටිනින් ඉහළ යාම හෝ eGFR පහළ වැටීම.",
                "urgency": "URGENT_CONSULT"
            })

        # Hepatocellular Injury
        alt = param_dict.get("alt")
        ast = param_dict.get("ast")
        bili = param_dict.get("bilirubin")
        if (alt and alt["numeric_value"] is not None and alt["numeric_value"] >= 100) or (bili and bili["numeric_value"] is not None and bili["numeric_value"] >= 2.0):
            syndromes.append({
                "condition": "Acute Hepatocellular Injury / Hepatitis",
                "condition_si": "අක්මාවේ සෛල ප්‍රදාහය සහ දුර්වලතාවය",
                "icd11": "1E51",
                "evidence": f"Marked transaminase elevation (ALT: {alt['raw_value'] if alt else 'N/A'} U/L).",
                "evidence_si": f"අක්මා එන්සයිම (ALT) අධික ලෙස ඉහළ යාම.",
                "urgency": "URGENT_CONSULT"
            })

        # Urinary Tract Infection
        pus = param_dict.get("urine_pus_cells")
        if pus and pus["numeric_value"] is not None and pus["numeric_value"] > 10:
            syndromes.append({
                "condition": "Urinary Tract Infection (Pyuria)",
                "condition_si": "මුත්‍රා මාර්ගයේ බැක්ටීරියා ආසාදනය",
                "icd11": "GC08",
                "evidence": f"Significant pyuria detected in urine sediment ({pus['raw_value']} pus cells/HPF).",
                "evidence_si": f"මුත්‍රාවල සැරව සෛල අධික ලෙස පැවතීම.",
                "urgency": "ROUTINE_CLINIC"
            })

        return syndromes

    def _determine_specialist_referrals(self, params: List[Dict[str, Any]]) -> List[str]:
        specialists = set()
        p_ids = {p["canonical_id"] for p in params if p["is_abnormal"]}

        if "troponin" in p_ids or "ldl_cholesterol" in p_ids or "total_cholesterol" in p_ids:
            specialists.add("Consultant Cardiologist (හෘද රෝග විශේෂඥ වෛද්‍ය)")
        if "platelets" in p_ids or "dengue_ns1" in p_ids or "hemoglobin" in p_ids:
            specialists.add("Consultant Physician / Hematologist (කායචිකිත්සක හෝ රක්තවේද විශේෂඥ වෛද්‍ය)")
        if "fasting_blood_sugar" in p_ids or "hba1c" in p_ids or "tsh" in p_ids:
            specialists.add("Consultant Endocrinologist / Diabetologist (හෝමෝන සහ දියවැඩියා විශේෂඥ වෛද්‍ය)")
        if "serum_creatinine" in p_ids or "egfr" in p_ids or "potassium" in p_ids:
            specialists.add("Consultant Nephrologist (වකුගඩු රෝග විශේෂඥ වෛද්‍ය)")
        if "alt" in p_ids or "ast" in p_ids or "bilirubin" in p_ids:
            specialists.add("Consultant Gastroenterologist / Hepatologist (ආහාර මාර්ග සහ අක්මා විශේෂඥ වෛද්‍ය)")
        if "urine_pus_cells" in p_ids or "urine_protein" in p_ids:
            specialists.add("General Practitioner / Urologist (පවුලේ වෛද්‍යවරයා හෝ මුත්‍රවේද විශේෂඥ)")

        if not specialists:
            specialists.add("Primary Care Physician / General Practitioner (පවුලේ වෛද්‍යවරයා)")

        return list(specialists)

    def _build_clinical_directives(
        self,
        overall_status: str,
        syndromes: List[Dict[str, Any]],
        critical_params: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        en_directives = []
        si_directives = []

        if overall_status == "CRITICAL_EMERGENCY":
            en_directives.append("IMMEDIATE EMERGENCY REFERRAL: Critical panic values detected. Present directly to the nearest hospital Emergency Department or call emergency services (911 / 1990).")
            en_directives.append("Bring this physical laboratory report sheet to the emergency triage physician.")
            en_directives.append("Do not engage in physical exertion, drive alone, or take self-prescribed medications.")

            si_directives.append("ක්ෂණික හදිසි ප්‍රතිකාර අවශ්‍යයි: අවදානම් සහගත අගයන් හඳුනාගෙන ඇති බැවින් වහාම ළඟම ඇති ප්‍රධාන රෝහලේ හදිසි ප්‍රතිකාර ඒකකය (ETU) වෙත යන්න හෝ 1990 සුවසැරිය අමතන්න.")
            si_directives.append("මෙම රසායනාගාර වාර්තාව වෛද්‍යවරයා වෙත පෙන්වීම සඳහා රැගෙන යන්න.")
            si_directives.append("තනිවම වාහන ධාවනය කිරීමෙන් සහ වෛද්‍ය උපදෙස් රහිතව ඖෂධ ගැනීමෙන් වළකින්න.")
        elif overall_status == "ABNORMAL_ELEVATED_RISK":
            en_directives.append("Schedule a comprehensive medical review with your primary care physician or appropriate specialist within 24 to 48 hours.")
            en_directives.append("Review concurrent medications to evaluate for potential drug-induced organ alterations.")
            en_directives.append("If you experience acute dizziness, chest tightness, severe abdominal pain, or shortness of breath, escalate immediately.")

            si_directives.append("දින 1-2ක් ඇතුළත ඔබේ පවුලේ වෛද්‍යවරයා හෝ අදාළ විශේෂඥ වෛද්‍යවරයෙකු හමුවී සම්පූර්ණ සායනික පරීක්ෂාවක් සිදුකරගන්න.")
            si_directives.append("ඔබ දැනට ලබාගන්නා ඖෂධ පිළිබඳව වෛද්‍යවරයා දැනුවත් කරන්න.")
            si_directives.append("පපුවේ වේදනාව, අධික ක්ලාන්තය, හෝ හුස්ම ගැනීමේ අපහසුව ඇති වුවහොත් වහාම රෝහල්ගත වන්න.")
        else:
            en_directives.append("All tested laboratory biomarkers remain within standard clinical reference ranges.")
            en_directives.append("Maintain routine healthy lifestyle, balanced nutrition, adequate hydration, and periodic health screenings.")

            si_directives.append("පරීක්ෂා කරන ලද සියලුම සායනික අගයන් සාමාන්‍ය නිරෝගී මට්ටමේ පවතී.")
            si_directives.append("සෞඛ්‍ය සම්පන්න ආහාර රටාව, ප්‍රමාණවත් ව්‍යායාම සහ වාර්ෂික වෛද්‍ය පරීක්ෂණ අඛණ්ඩව පවත්වා ගන්න.")

        return en_directives, si_directives


report_analyzer = MedicalReportAnalyzer()
