import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app, bootstrap_initial_state


@pytest.mark.asyncio
async def test_full_platform_lifecycle_and_endpoints():
    await bootstrap_initial_state()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Health check
        h_res = await client.get("/api/v1/health")
        assert h_res.status_code == 200
        assert h_res.json()["status"] == "OPERATIONAL"

        # 2. Clinician authentication
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "dr.evans@hospital.nhs.uk",
            "password": "Clinical2026!"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Initialize triage session
        sess_res = await client.post("/api/v1/triage/session", json={
            "patient_age_group": "ADULT",
            "biological_sex": "MALE",
            "consent_acknowledged": True,
            "disclaimer_acknowledged": True
        })
        assert sess_res.status_code == 201
        session_id = sess_res.json()["session_id"]

        # 4. Emergency escalation triage prompt
        emerg_res = await client.post("/api/v1/triage/prompt", json={
            "session_id": session_id,
            "prompt_text": "Sudden crushing chest pain radiating to left arm and jaw, profuse diaphoresis."
        })
        assert emerg_res.status_code == 200
        emerg_data = emerg_res.json()
        assert emerg_data["emergency_info"]["is_emergency"] is True
        assert emerg_data["triage_severity"] == "EMERGENCY"

        # 5. Routine RAG prompt
        routine_res = await client.post("/api/v1/triage/prompt", json={
            "session_id": session_id,
            "prompt_text": "Diabetic with blood sugar 64 mg/dL feeling lightheaded."
        })
        assert routine_res.status_code == 200
        routine_data = routine_res.json()
        assert len(routine_data["clinical_citations"]) > 0

        # 6. RLHF Queue
        queue_res = await client.get("/api/v1/rlhf/queue", headers=headers)
        assert queue_res.status_code == 200

        # 7. Analytics Overview
        analytics_res = await client.get("/api/v1/analytics/overview", headers=headers)
        assert analytics_res.status_code == 200
        assert analytics_res.json()["total_triage_sessions"] > 0

        # 8. Clinical Evaluation Run
        eval_res = await client.post("/api/v1/evaluation/run", headers=headers, json={"sample_size": 3})
        assert eval_res.status_code == 200
        assert eval_res.json()["aggregate_metrics"]["safety_pass_rate"] == 1.0

        # 9. Safety & Drift Monitoring
        mon_res = await client.get("/api/v1/monitoring/status", headers=headers)
        assert mon_res.status_code == 200
        assert mon_res.json()["total_guidelines_indexed"] >= 7

        # 10. HL7 FHIR R4 Patient Summary
        fhir_res = await client.get(f"/api/v1/fhir/PatientSummary/{session_id}", headers=headers)
        assert fhir_res.status_code == 200
        assert fhir_res.json()["resourceType"] == "Bundle"
