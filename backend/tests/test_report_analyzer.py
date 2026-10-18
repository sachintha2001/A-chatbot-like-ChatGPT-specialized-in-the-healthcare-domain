import pytest
from app.engine.report_analyzer import MedicalReportAnalyzer


def test_fbc_thrombocytopenia_dengue():
    analyzer = MedicalReportAnalyzer()
    sample = (
        "FULL BLOOD COUNT REPORT\n"
        "Hemoglobin: 18.5 g/dL\n"
        "Total WBC: 3100 /uL\n"
        "Platelet Count: 42000 /uL\n"
        "Dengue NS1: POSITIVE\n"
    )
    result = analyzer.analyze_report(sample)
    assert result["success"] is True
    assert result["overall_status"] == "CRITICAL_EMERGENCY"
    assert result["is_emergency"] is True
    assert result["qualitative_verdict"] == "POSITIVE"

    # Platelets should be marked as CRITICAL_LOW
    param_map = {p["canonical_id"]: p for p in result["parameters"]}
    assert "platelets" in param_map
    assert param_map["platelets"]["status"] == "CRITICAL_LOW"

    # Dengue NS1 should be POSITIVE
    assert "dengue_ns1" in param_map
    assert param_map["dengue_ns1"]["status"] == "POSITIVE"

    # Correlated condition should detect Dengue (1D2Z)
    conditions = [c["icd11"] for c in result["correlated_conditions"]]
    assert "1D2Z" in conditions

    # Check elevated and decreased tracking
    assert any("Hemoglobin" in s for s in result["elevated_parameters_en"])
    assert any("Platelet" in s for s in result["decreased_parameters_en"])


def test_lipid_profile_hyperlipidemia():
    analyzer = MedicalReportAnalyzer()
    sample = (
        "LIPID PROFILE REPORT\n"
        "Total Cholesterol: 260 mg/dL\n"
        "LDL Cholesterol: 175 mg/dL\n"
        "HDL Cholesterol: 35 mg/dL\n"
        "Triglycerides: 240 mg/dL\n"
    )
    result = analyzer.analyze_report(sample)
    assert result["success"] is True
    assert result["overall_status"] == "ABNORMAL_ELEVATED_RISK"
    assert result["is_emergency"] is False

    param_map = {p["canonical_id"]: p for p in result["parameters"]}
    assert param_map["total_cholesterol"]["status"] == "ELEVATED"
    assert param_map["ldl_cholesterol"]["status"] == "ELEVATED"
    assert param_map["triglycerides"]["status"] == "ELEVATED"
    assert param_map["hdl_cholesterol"]["status"] == "DECREASED"

    # Should correlate with Atherogenic Dyslipidemia (5C80)
    conditions = [c["icd11"] for c in result["correlated_conditions"]]
    assert "5C80" in conditions


def test_normal_health_screening():
    analyzer = MedicalReportAnalyzer()
    sample = (
        "ROUTINE HEALTH CHECK\n"
        "Hemoglobin: 14.5 g/dL\n"
        "Platelet Count: 280000 /uL\n"
        "Fasting Blood Sugar: 86 mg/dL\n"
        "Serum Creatinine: 0.9 mg/dL\n"
    )
    result = analyzer.analyze_report(sample)
    assert result["success"] is True
    assert result["overall_status"] == "ALL_NORMAL"
    assert result["abnormal_count"] == 0
    assert len(result["elevated_parameters_en"]) == 0
    assert len(result["decreased_parameters_en"]) == 0


def test_acute_troponin_positive_mi():
    analyzer = MedicalReportAnalyzer()
    sample = (
        "EMERGENCY LABS\n"
        "Cardiac Troponin: 0.92 ng/mL\n"
        "Hemoglobin: 13.8 g/dL\n"
    )
    result = analyzer.analyze_report(sample)
    assert result["success"] is True
    assert result["is_emergency"] is True
    conditions = [c["icd11"] for c in result["correlated_conditions"]]
    assert "BA41" in conditions


def test_sinhala_translations_in_report_output():
    analyzer = MedicalReportAnalyzer()
    sample = (
        "පරීක්ෂණ වාර්තාව\n"
        "Fasting Blood Sugar: 165 mg/dL\n"
        "Dengue NS1: NEGATIVE\n"
    )
    result = analyzer.analyze_report(sample)
    assert result["success"] is True
    assert len(result["elevated_parameters_si"]) >= 1
    assert "නිරාහාර රුධිර සීනි" in result["elevated_parameters_si"][0]
    assert result["qualitative_verdict"] == "NEGATIVE"


def test_image_ocr_report_analysis():
    import io
    from PIL import Image, ImageDraw

    # Generate a synthetic medical report image
    img = Image.new("RGB", (700, 350), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    sample_text = (
        "CLINICAL LABORATORY REPORT\n"
        "Hemoglobin: 14.5 g/dL\n"
        "Platelet Count: 45000 /uL\n"
        "Dengue NS1 Antigen: POSITIVE"
    )
    draw.text((30, 30), sample_text, fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    analyzer = MedicalReportAnalyzer()
    extracted_text = analyzer.extract_text_from_file(image_bytes, "camera_photo.png")
    assert "Platelet" in extracted_text or "45000" in extracted_text

    result = analyzer.analyze_report(extracted_text)
    assert result["success"] is True
    assert result["overall_status"] == "CRITICAL_EMERGENCY"
    assert result["is_emergency"] is True
