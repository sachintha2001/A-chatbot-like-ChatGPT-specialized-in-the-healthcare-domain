from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_sri_lankan_booking_gateways():
    res = client.get("/api/v1/telemedicine/gateways")
    assert res.status_code == 200
    gateways = res.json()
    gateway_ids = [g["gateway_id"] for g in gateways]
    assert "ECHANNELLING" in gateway_ids
    assert "DOC990" in gateway_ids
    assert "ODOC_TELEMED" in gateway_ids
    assert "HOSPITAL_DIRECT" in gateway_ids


def test_list_and_filter_specialists():
    # All specialists
    res_all = client.get("/api/v1/telemedicine/specialists")
    assert res_all.status_code == 200
    assert len(res_all.json()) >= 8

    # Filter by Cardiology
    res_card = client.get("/api/v1/telemedicine/specialists?specialty=CARDIOLOGY")
    assert res_card.status_code == 200
    cards = res_card.json()
    assert len(cards) >= 2
    assert all(d["specialty_code"] == "CARDIOLOGY" for d in cards)

    # Search by clinical keyword 'dengue'
    res_dengue = client.get("/api/v1/telemedicine/specialists?q=dengue")
    assert res_dengue.status_code == 200
    assert len(res_dengue.json()) >= 1


def test_recommend_specialists_from_report_and_triage():
    # 1. Hematology / Dengue Thrombocytopenia from Lab Report
    res_hema = client.post(
        "/api/v1/telemedicine/recommend",
        json={
            "specialty_hint": "Consultant Hematologist (රුධිර රෝග පිළිබඳ විශේෂඥ වෛද්‍ය)",
            "clinical_context": "Platelet count decreased to 78,000 /uL, Dengue NS1 Antigen Positive.",
            "triage_acuity": "URGENT",
            "icd11_codes": ["1D2Z", "3B64"],
            "language": "si"
        }
    )
    assert res_hema.status_code == 200
    data_hema = res_hema.json()
    assert data_hema["matched_specialty_code"] == "HEMATOLOGY"
    assert len(data_hema["specialists"]) >= 1
    assert data_hema["emergency_warning_active"] is False

    # 2. Emergency Cardiology presentation (triggers 1990 Suwa Seriya warning)
    res_emerg = client.post(
        "/api/v1/telemedicine/recommend",
        json={
            "specialty_hint": "Cardiologist",
            "clinical_context": "Troponin I elevated at 2.4 ng/mL with crushing central chest pain.",
            "triage_acuity": "EMERGENCY",
            "icd11_codes": ["BA41"]
        }
    )
    assert res_emerg.status_code == 200
    data_emerg = res_emerg.json()
    assert data_emerg["matched_specialty_code"] == "CARDIOLOGY"
    assert data_emerg["emergency_warning_active"] is True
    assert "1990" in data_emerg["emergency_directive_en"]
    assert "1990" in data_emerg["emergency_directive_si"]


def test_book_and_cancel_appointment_with_sbar_handover():
    # Book via eChannelling + Video Telemedicine
    book_res = client.post(
        "/api/v1/telemedicine/appointments",
        json={
            "doctor_id": "SL-DOC-CARD-01",
            "patient_name": "Nimal Perera",
            "patient_phone": "0771234567",
            "patient_age": 54,
            "preferred_slot": "Today • 04:30 PM - 06:30 PM",
            "consultation_mode": "VIDEO_TELEMEDICINE",
            "booking_gateway": "DOC990",
            "hospital_name": "Asiri Heart Centre",
            "clinical_context_summary": "LDL Cholesterol elevated (182 mg/dL), Total Cholesterol 265 mg/dL.",
            "recommended_specialty": "Consultant Cardiologist",
            "triage_acuity": "URGENT",
            "correlated_icd11_codes": ["5C80"],
            "language": "si"
        }
    )
    assert book_res.status_code == 201
    booking = book_res.json()
    assert booking["status"] == "CONFIRMED"
    assert booking["booking_reference"].startswith("DOC990-")
    assert booking["queue_token_number"] >= 15
    assert booking["patient_phone_masked"] == "077***567"
    assert booking["telemedicine_meeting_url"] is not None
    assert "5C80" in booking["sbar_clinical_handover_en"]
    assert "5C80" in booking["sbar_clinical_handover_si"]

    # List appointments
    list_res = client.get("/api/v1/telemedicine/appointments")
    assert list_res.status_code == 200
    assert any(b["booking_id"] == booking["booking_id"] for b in list_res.json())

    # Cancel appointment
    cancel_res = client.patch(f"/api/v1/telemedicine/appointments/{booking['booking_id']}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"
