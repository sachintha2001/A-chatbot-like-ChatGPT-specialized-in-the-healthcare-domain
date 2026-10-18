import pytest
from app.knowledge.seed_corpus import CLINICAL_PATHOLOGY_CORPUS
from app.models.pathology import MedicalSpecialty, TriageAcuityLevel
from app.engine.triage_state_machine import (
    SOCRATESTriageStateMachine,
    TriageWorkflowState,
    triage_state_machine
)
from app.knowledge.services.medical_connectors import clean_html_text, federated_knowledge_service


def test_seed_corpus_size_and_integrity():
    """Verify minimum 40+ disease threshold and clinical field completeness."""
    assert len(CLINICAL_PATHOLOGY_CORPUS) >= 40, f"Expected at least 40 pathologies, got {len(CLINICAL_PATHOLOGY_CORPUS)}"

    icd11_codes = set()
    for item in CLINICAL_PATHOLOGY_CORPUS:
        code = item["icd11_code"]
        assert code not in icd11_codes, f"Duplicate ICD-11 code detected: {code}"
        icd11_codes.add(code)

        assert item["clinical_name"], "Missing clinical_name"
        assert isinstance(item["medical_specialty"], MedicalSpecialty)
        assert isinstance(item["baseline_acuity"], TriageAcuityLevel)
        assert len(item["pathophysiology_overview"]) > 50, f"Pathophysiology too brief for {code}"

        symptoms = item["cardinal_symptoms"]
        assert "primary" in symptoms and len(symptoms["primary"]) >= 2
        assert "secondary" in symptoms

        red_flags = item["red_flag_criteria"]
        assert isinstance(red_flags, list) and len(red_flags) >= 2, f"Insufficient red flags for {code}"

        workup = item["diagnostic_workup"]
        assert "initial_labs" in workup and len(workup["initial_labs"]) >= 1

        mgmt = item["evidence_based_management"]
        assert "first_line_lifestyle" in mgmt
        assert "pharmacotherapy" in mgmt
        assert "contraindications" in mgmt

        meta = item["source_metadata"]
        assert meta["issuing_authority"]
        assert meta["guideline_title"]
        assert meta["publication_year"] >= 2020


def test_specialty_coverage():
    """Verify that all major clinical specialties are represented in the ontology."""
    specialties_found = {item["medical_specialty"] for item in CLINICAL_PATHOLOGY_CORPUS}
    required_specialties = [
        MedicalSpecialty.INFECTIOUS_DISEASES,
        MedicalSpecialty.CARDIOVASCULAR,
        MedicalSpecialty.ENDOCRINE_METABOLIC,
        MedicalSpecialty.RESPIRATORY,
        MedicalSpecialty.NEUROLOGY,
        MedicalSpecialty.PSYCHIATRY,
        MedicalSpecialty.GASTROENTEROLOGY_HEPATOLOGY,
        MedicalSpecialty.NEPHROLOGY_UROLOGY,
        MedicalSpecialty.HEMATOLOGY,
        MedicalSpecialty.DERMATOLOGY,
        MedicalSpecialty.RHEUMATOLOGY,
        MedicalSpecialty.OBSTETRICS_GYNECOLOGY,
        MedicalSpecialty.PEDIATRICS,
        MedicalSpecialty.ONCOLOGY
    ]
    for spec in required_specialties:
        assert spec in specialties_found, f"Specialty {spec} missing from seed corpus"


def test_triage_state_machine_red_flag_emergency():
    """Deterministic red-flag trigger must halt intake and return EMERGENCY."""
    sm = SOCRATESTriageStateMachine()
    
    # Cardiac red flag
    result = sm.process_turn("I have crushing chest pain radiating to my left arm and jaw")
    assert result["state"] == TriageWorkflowState.RED_FLAG_EMERGENCY
    assert result["acuity"] == TriageAcuityLevel.EMERGENCY
    assert len(result["red_flags"]) >= 1
    assert "911" in result["content"] or "1990" in result["content"]
    assert any("Emergency" in chip for chip in result["follow_up_chips"])

    # Neurological thunderclap red flag
    neuro_res = sm.process_turn("Sudden thunderclap worst headache of my life")
    assert neuro_res["state"] == TriageWorkflowState.RED_FLAG_EMERGENCY
    assert neuro_res["acuity"] == TriageAcuityLevel.EMERGENCY


def test_triage_state_machine_socrates_intake():
    """Brief, non-emergency symptom presentation must prompt for SOCRATES dimensions."""
    sm = SOCRATESTriageStateMachine()
    
    result = sm.process_turn("I have a headache")
    assert result["state"] == TriageWorkflowState.CLINICAL_INTAKE_REQUIRED
    assert result["acuity"] == TriageAcuityLevel.ROUTINE_CLINIC
    assert len(result["follow_up_chips"]) >= 3
    assert any("onset" in q.lower() or "how" in q.lower() for q in result["content"].split("\n"))


def test_triage_state_machine_structured_assessment():
    """Detailed clinical description must progress to structured assessment with ICD-11 differentials."""
    sm = SOCRATESTriageStateMachine()
    
    detailed_query = (
        "I have a throbbing headache on the right side of my head that started 2 days ago, "
        "accompanied by nausea and severe light sensitivity, rated 8/10 in severity."
    )
    result = sm.process_turn(detailed_query)
    assert result["state"] == TriageWorkflowState.STRUCTURED_ASSESSMENT
    assert "ICD-11" in result["content"]
    assert len(result["diagnostic_workup"]) >= 1
    assert len(result["citations"]) >= 1


def test_sinhala_red_flag_screening():
    """Sinhala emergency red flags must be detected accurately."""
    sm = SOCRATESTriageStateMachine()
    
    si_query = "මට පපුවේ දරුණු වේදනාවක් සමග වම් අතට විහිදෙන කැක්කුමක් තියෙනවා"
    result = sm.process_turn(si_query)
    assert result["is_sinhala"] is True
    assert result["state"] == TriageWorkflowState.RED_FLAG_EMERGENCY
    assert "1990" in result["content"]


def test_html_cleaner():
    """Verify HTML stripper sanitizes medical documentation without losing text content."""
    raw = "<div><p>Patient presents with <strong>fever &amp; chills</strong></p><br/></div>"
    clean = clean_html_text(raw)
    assert clean == "Patient presents with fever & chills"
