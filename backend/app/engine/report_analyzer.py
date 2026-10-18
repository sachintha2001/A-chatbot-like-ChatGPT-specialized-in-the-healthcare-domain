import re
import io
from typing import Dict, Any, List, Optional, Tuple
from app.knowledge.lab_biomarkers import CLINICAL_BIOMARKER_REGISTRY


class MedicalReportAnalyzer:
    """
    Production-grade Clinical Laboratory Report Analysis & Interpretation Engine.
    Parses digital and textual medical laboratory reports (FBC, Lipid, Glycemic, LFT, RFT, Serology),
    identifies qualitative (Positive/Negative) and quantitative (High/Low) biomarker abnormalities,
    correlates findings with WHO ICD-11 clinical ontology, and generates bilingual clinical guidance.
    """

    def __init__(self):
        self.registry = CLINICAL_BIOMARKER_REGISTRY

    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        """
        Extracts plain text content from uploaded medical documents (PDF, plain text, or photographed images).
        Supports Optical Character Recognition (OCR) for camera captures and scans (.png, .jpg, .jpeg, .webp, .bmp).
        """
        filename_lower = filename.lower()
        image_extensions = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")

        if any(filename_lower.endswith(ext) for ext in image_extensions):
            return self.extract_text_from_image(file_bytes)

        if filename_lower.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                text_pages = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_pages.append(page_text)
                extracted = "\n".join(text_pages)
                if extracted and len(extracted.strip()) >= 15:
                    return extracted
            except Exception:
                pass

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
        qualifier_suffix = r"(?:\s*(?:count|level|result|value|reading|rate))?"

        if biomarker["is_qualitative"]:
            # Qualitative search (Positive / Negative / Reactive / Non-reactive)
            qual_pattern = (
                rf"{alias_pattern}{qualifier_suffix}[ \t.:|\-_]*(positive|negative|reactive|non-reactive|nonreactive|detected|not\s+detected|nil|\+|-|1\+|2\+|3\+)"
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
                rf"{alias_pattern}{qualifier_suffix}[ \t.:|\-_]*([0-9]+(?:[.,][0-9]+)?)"
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
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Executes complete clinical interpretation of parsed report parameters:
        - Evaluates overall positive / negative / abnormal status.
        - Identifies specific elevated (wedi) vs decreased (adu) parameters.
        - Maps correlated clinical conditions to official ICD-11 codes.
        - Generates actionable clinical recommendations and red flag alerts.
        """
        extracted_parameters = self.parse_report_text(raw_text)

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
                "parameters_found": 0
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
