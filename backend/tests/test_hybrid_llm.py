import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.engine.llm_connector import HybridLLMConnector
from app.ingestion.vector_store import vector_store

client = TestClient(app)


def test_singlish_and_complex_narrative_normalization():
    """
    Tests that long, ungrammatical, misspelled, or Singlish (Romanized Sinhala)
    patient statements are normalized into structured clinical English cues
    and scrubbed of PHI simultaneously.
    """
    connector = HybridLLMConnector()
    raw_query = (
        "mage oluwa ridenawa dawas 3k thisse thada una ekka husma ganna amarui "
        "saha wamane yanawa, bada ridenawa"
    )
    norm = connector.normalize_complex_patient_narrative(raw_query)

    assert len(norm["expanded_terms"]) >= 4
    normalized_lower = norm["normalized_clinical_query"].lower()
    assert "headache" in normalized_lower
    assert "fever" in normalized_lower
    assert "shortness of breath" in normalized_lower
    assert "vomiting" in normalized_lower
    assert "abdominal" in normalized_lower


def test_phi_scrubbing_before_cloud_llm_transmission():
    """
    Verifies that patient PII/PHI (Singlish names, phone numbers, NIC, email)
    are scrubbed by PHIScrubber before building any Cloud LLM payload.
    """
    connector = HybridLLMConnector()
    connector.configure_runtime(provider="local")

    raw_query = (
        "Mage nama Kasun Perera, phone 0771234567, NIC 199212345678, "
        "email kasun@example.com. Mata dawas 3k thisse thada una saha oluwa ridenawa."
    )
    history = [
        {"role": "user", "content": "My name is Mr. Kasun Perera and my phone is 0771234567"},
        {"role": "assistant", "content": "How can I help you today?"},
    ]

    norm = connector.normalize_complex_patient_narrative(raw_query)
    scrubbed_history, history_entities = connector.scrub_conversation_history(history)

    assert "Kasun Perera" not in norm["redacted_text"]
    assert "0771234567" not in norm["redacted_text"]
    assert "199212345678" not in norm["redacted_text"]
    assert "kasun@example.com" not in norm["redacted_text"]
    assert len(norm["scrubbed_entities"]) >= 3
    assert "Kasun Perera" not in scrubbed_history[0]["content"]
    assert "0771234567" not in scrubbed_history[0]["content"]
    assert len(history_entities) >= 1


@pytest.mark.asyncio
async def test_hybrid_cloud_llm_with_mocked_gemini(monkeypatch):
    """
    Tests live async Cloud LLM synthesis with Google Gemini 1.5 Pro mocked,
    verifying PHI scrubbing + citation preservation + clinical safety verification.
    """
    connector = HybridLLMConnector()
    connector.configure_runtime(
        provider="gemini",
        gemini_api_key="test-gemini-api-key-12345",
        gemini_model="gemini-1.5-pro",
    )

    captured_prompt = {}

    async def mock_call_gemini_async(prompt: str, history: list) -> str:
        captured_prompt["prompt"] = prompt
        captured_prompt["history"] = history
        return (
            "### Clinical Triage & Guidance (URGENT)\n\n"
            "**Understanding Your Symptoms:** You reported a 3-day history of fever, headache, "
            "and shortness of breath.\n\n"
            "**Evidence-Based Assessment:** According to clinical guidelines [Ref 1], persistent fever "
            "accompanied by respiratory difficulty requires prompt in-person evaluation within 4-12 hours.\n\n"
            "*Disclaimer: This information is for educational and clinical triage support only and "
            "does not constitute a definitive medical diagnosis.*"
        )

    monkeypatch.setattr(connector, "_call_gemini_async", mock_call_gemini_async)

    evidence = [c for c, _ in vector_store.search("fever headache shortness of breath", top_k=2)]
    result = await connector.synthesize_hybrid_response_async(
        raw_patient_query="Mage nama Nimal Silva, phone 0712345678. Dawas 3k thisse thada una saha husma ganna amarui.",
        context_chunks=evidence,
        deterministic_fallback_text="Fallback deterministic response [Ref 1].",
        language="en",
    )

    assert result["cloud_synthesized"] is True
    assert result["provider_used"] == "gemini"
    assert result["model_used"] == "gemini-1.5-pro"
    assert "[Ref 1]" in result["response_text"]
    # Ensure raw PHI never reached the cloud prompt
    assert "Nimal Silva" not in captured_prompt["prompt"]
    assert "0712345678" not in captured_prompt["prompt"]
    # Ensure Singlish interpretation hints were injected into the prompt
    assert "shortness of breath" in captured_prompt["prompt"].lower()


@pytest.mark.asyncio
async def test_post_inference_safety_guardrail_blocks_unsafe_llm_output(monkeypatch):
    """
    Verifies that if a Cloud LLM attempts to output a definitive diagnosis or
    unauthorized prescription dosage, the post-inference safety guardrail blocks it
    and falls back to the deterministic local clinical engine.
    """
    connector = HybridLLMConnector()
    connector.configure_runtime(
        provider="openai",
        openai_api_key="test-openai-key",
        openai_model="gpt-4o",
    )

    async def mock_unsafe_openai_async(prompt: str, history: list) -> str:
        return "I diagnose you with bacterial pneumonia. Start taking 500mg amoxicillin twice a day."

    monkeypatch.setattr(connector, "_call_openai_async", mock_unsafe_openai_async)

    evidence = [c for c, _ in vector_store.search("cough fever", top_k=2)]
    fallback_text = "Deterministic safe clinical response [Ref 1]."
    result = await connector.synthesize_hybrid_response_async(
        raw_patient_query="I have a cough and fever for 2 days",
        context_chunks=evidence,
        deterministic_fallback_text=fallback_text,
        language="en",
    )

    # Should have blocked the unsafe LLM response and fallen back to local deterministic synthesis
    assert result["cloud_synthesized"] is False
    assert result["provider_used"] == "local_deterministic_fallback"
    assert result["response_text"] == fallback_text
    assert "I diagnose you with" not in result["response_text"]


def test_llm_status_and_runtime_config_endpoints():
    """
    Tests GET /api/v1/chat/llm-status and POST /api/v1/chat/llm-config endpoints.
    """
    status_res = client.get("/api/v1/chat/llm-status")
    assert status_res.status_code == 200
    data = status_res.json()
    assert "active_provider" in data
    assert data["phi_scrubber_enforced_pre_cloud"] is True
    assert data["deterministic_red_flag_gate_active"] is True

    # Configure back to local mode cleanly
    cfg_res = client.post(
        "/api/v1/chat/llm-config",
        json={"provider": "local"},
    )
    assert cfg_res.status_code == 200
    assert cfg_res.json()["active_provider"] == "local"
