import pytest
from app.compliance.red_flag_detector import red_flag_detector
from app.compliance.phi_scrubber import phi_scrubber


def test_red_flag_detector_acute_coronary_syndrome():
    narrative = "Patient reports sudden crushing chest pain radiating to left jaw with severe diaphoresis."
    is_emergency, flags, directive, hotlines = red_flag_detector.evaluate(narrative)
    assert is_emergency is True
    assert "ACUTE_CORONARY_SYNDROME" in flags
    assert "Paramedics" in directive or "Emergency" in directive
    assert hotlines["US_Canada_Emergency"] == "911"


def test_red_flag_detector_stroke_fast():
    narrative = "Noticed sudden right facial drooping and slurred speech 20 minutes ago."
    is_emergency, flags, directive, _ = red_flag_detector.evaluate(narrative)
    assert is_emergency is True
    assert "ACUTE_ISCHEMIC_STROKE" in flags


def test_red_flag_detector_anaphylaxis():
    narrative = "After eating nuts, developed swollen tongue and throat closing with hives."
    is_emergency, flags, directive, _ = red_flag_detector.evaluate(narrative)
    assert is_emergency is True
    assert "ANAPHYLAXIS" in flags
    assert "EpiPen" in directive or "Epinephrine" in directive


def test_red_flag_detector_non_emergency():
    narrative = "Mild nasal congestion and low-grade cough for two days without fever."
    is_emergency, flags, _, _ = red_flag_detector.evaluate(narrative)
    assert is_emergency is False
    assert len(flags) == 0


def test_red_flag_detector_sinhala_emergency():
    narrative = "මට තද පපුවේ කැක්කුමක් තියෙනවා වම් අතට වේදනාව යනවා සහ අධික දහඩිය දමනවා."
    is_emergency, flags, directive, hotlines = red_flag_detector.evaluate(narrative)
    assert is_emergency is True
    assert "ACUTE_CORONARY_SYNDROME" in flags
    assert "1990" in directive or "සුවසැරිය" in directive
    assert hotlines["Sri_Lanka_Suwa_Seriya"] == "1990"


def test_phi_scrubber_redaction():
    raw_prompt = (
        "My name is Michael Scott, SSN 012-34-5678, phone (555) 234-5678, "
        "email michael.scott@dunder.com. I live at 1725 Slough Avenue, Scranton."
    )
    redacted, entity_types = phi_scrubber.redact(raw_prompt)

    # Validate that raw identifiers are completely excised
    assert "012-34-5678" not in redacted
    assert "michael.scott@dunder.com" not in redacted
    assert "(555) 234-5678" not in redacted
    assert "Michael Scott" not in redacted

    # Validate that standardized cryptographic placeholders are present
    assert "[REDACTED_SSN]" in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "SSN" in entity_types
    assert "EMAIL" in entity_types
    assert "PHONE" in entity_types


def test_phi_scrubber_sinhala_redaction():
    raw_prompt = "මගේ නම කමල් පෙරේරා, ජාතික හැඳුනුම්පත: 198923456789, දුරකථන අංකය: 0771234567. මට දියවැඩියාව තිබේ."
    redacted, entity_types = phi_scrubber.redact(raw_prompt)

    assert "කමල් පෙරේරා" not in redacted
    assert "198923456789" not in redacted
    assert "0771234567" not in redacted
    assert "[REDACTED_NAME_SI]" in redacted
    assert "[REDACTED_NHS_OR_NIC]" in redacted
