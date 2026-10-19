import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.v1.voice import clean_medical_text_for_speech


def test_clean_medical_text_for_speech():
    raw = (
        "### Clinical Triage Assessment\n"
        "Patient exhibits acute chest pain [Ref 1: AHA Guidelines 2026].\n"
        "**Recommendation**: Please proceed to Emergency Room.\n"
        "| Parameter | Value |\n| Troponin | Positive |\n"
        "- Monitor vital signs.\n"
        "Visit https://emergency.health for details."
    )
    cleaned = clean_medical_text_for_speech(raw)
    assert "[Ref 1" not in cleaned
    assert "https://" not in cleaned
    assert "**" not in cleaned
    assert "###" not in cleaned
    assert "Patient exhibits acute chest pain" in cleaned
    assert "Please proceed to Emergency Room" in cleaned


@pytest.mark.asyncio
async def test_voice_capabilities():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/voice/capabilities")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "AVAILABLE"
        assert "si-LK" in [l["code"] for l in data["stt"]["supported_languages"]]
        assert "en-US" in [l["code"] for l in data["stt"]["supported_languages"]]
        assert "si" in [l["code"] for l in data["tts"]["supported_languages"]]
        assert "en" in [l["code"] for l in data["tts"]["supported_languages"]]


@pytest.mark.asyncio
async def test_voice_synthesize_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test Sinhala speech synthesis
        res_si = await client.post(
            "/api/v1/voice/synthesize",
            json={"text": "ඔබට කිසියම් අපහසුතාවයක් තිබේද?", "language": "si"}
        )
        assert res_si.status_code == 200
        assert res_si.headers["content-type"].startswith("audio/mpeg")
        assert len(res_si.content) > 1000

        # Test English speech synthesis
        res_en = await client.post(
            "/api/v1/voice/synthesize",
            json={"text": "How can I help assess your health symptoms today?", "language": "en"}
        )
        assert res_en.status_code == 200
        assert res_en.headers["content-type"].startswith("audio/mpeg")
        assert len(res_en.content) > 1000


@pytest.mark.asyncio
async def test_voice_transcribe_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test empty audio payload
        res = await client.post(
            "/api/v1/voice/transcribe",
            files={"audio_file": ("test.wav", b"short", "audio/wav")}
        )
        assert res.status_code == 400
