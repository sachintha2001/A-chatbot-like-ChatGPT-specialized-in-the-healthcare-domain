import json
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse

from app.engine.triage_state_machine import triage_state_machine
from app.engine.llm_connector import hybrid_llm_connector
from app.compliance.security_shield import security_shield, SecurityThreatException

router = APIRouter(prefix="/chat", tags=["Clinical Conversational Streaming"])


class ChatStreamRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1500)
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    preferred_language: Optional[str] = None
    age_group: Optional[str] = "ADULT"
    biological_sex: Optional[str] = "UNSPECIFIED"


class HybridLLMConfigRequest(BaseModel):
    provider: Optional[str] = Field(default=None, description="'auto' | 'gemini' | 'anthropic' | 'openai' | 'local'")
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    anthropic_model: Optional[str] = None
    openai_model: Optional[str] = None


async def sse_event_stream(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    preferred_language: Optional[str] = None,
    age_group: str = "ADULT",
    biological_sex: str = "UNSPECIFIED"
):
    """
    Event stream generator yielding Server-Sent Events (SSE):
    - event: status
    - event: triage_badge
    - event: token
    - event: citations
    - event: follow_up_chips
    - event: done
    """
    def format_sse(event: str, data: Any) -> str:
        data_str = json.dumps(data) if not isinstance(data, str) else json.dumps({"text": data})
        return f"event: {event}\ndata: {data_str}\n\n"

    # Stage -1: Zero-Trust WAF & Adversarial Prompt-Injection / XSS / SQLi Inspection
    try:
        sanitized_message = security_shield.inspect_text_input(message, context_label="chat_stream_prompt")
    except SecurityThreatException as threat:
        is_si = preferred_language == "si"
        sec_msg = threat.message_si if is_si else threat.message_en
        yield format_sse("triage_badge", {
            "state": "SECURITY_SHIELD_BLOCKED",
            "acuity": "ROUTINE",
            "headline": f"🛡️ MedGuard Zero-Trust Security Shield — {threat.threat_category} Blocked",
            "is_emergency": False,
            "llm_provider": "security_waf",
            "llm_model": "MedGuard-ZeroTrust-WAF-v2",
            "cloud_synthesized": False,
            "scrubbed_entities": [threat.threat_category]
        })
        yield format_sse("token", {
            "token": f"**[MedGuard Zero-Trust Security Shield — {threat.threat_category}]**\n\n{sec_msg}",
            "index": 0
        })
        yield format_sse("done", {
            "status": "blocked_by_security_shield",
            "state": "SECURITY_SHIELD_BLOCKED",
            "acuity": "ROUTINE"
        })
        return

    # Stage 0: Pre-transmission HIPAA Safe Harbor & Sinhala/Singlish PHI Scrubbing
    yield format_sse("status", {
        "stage": "scrubbing_phi",
        "message": "Enforcing HIPAA Safe Harbor PHI Scrubber & Zero-Leakage DLP..."
    })
    await asyncio.sleep(0.03)

    # Stage 1: Red-flag screening
    yield format_sse("status", {
        "stage": "screening_red_flags",
        "message": "Screening deterministic red-flag criteria and vital compromise triggers..."
    })
    await asyncio.sleep(0.03)

    # Stage 2: Knowledge retrieval & ontology mapping
    yield format_sse("status", {
        "stage": "knowledge_retrieval",
        "message": "Querying WHO ICD-11 ontology, clinical vector store, and practice guidelines..."
    })
    await asyncio.sleep(0.03)

    # Process Hybrid State Machine + Cloud LLM Connector (over PHI-scrubbed text)
    result = await triage_state_machine.process_turn_hybrid_async(
        user_message=sanitized_message,
        conversation_history=history,
        preferred_language=preferred_language,
        age_group=age_group,
        biological_sex=biological_sex
    )

    # Stage 3: Immediate triage badge emission before text stream completes
    acuity_val = result["acuity"].value if hasattr(result["acuity"], "value") else str(result["acuity"])
    state_val = result["state"].value if hasattr(result["state"], "value") else str(result["state"])
    yield format_sse("triage_badge", {
        "state": state_val,
        "acuity": acuity_val,
        "headline": result["headline"],
        "is_emergency": state_val == "RED_FLAG_EMERGENCY",
        "llm_provider": result.get("llm_provider", "local_deterministic"),
        "llm_model": result.get("llm_model", "MedGuard-Local-Deterministic-RAG"),
        "cloud_synthesized": result.get("cloud_synthesized", False),
        "scrubbed_entities": result.get("scrubbed_entities", [])
    })
    await asyncio.sleep(0.02)

    # Stage 4: Synthesizing response stage
    model_label = result.get("llm_model", "Hybrid Engine")
    yield format_sse("status", {
        "stage": "synthesizing_response",
        "message": f"Synthesizing evidence-backed clinical response ({model_label})..."
    })
    await asyncio.sleep(0.02)

    # Stage 5: Outbound DLP Scrubbing + Token streaming
    content, _ = security_shield.scrub_outbound_dlp(result["content"])
    tokens = content.split(" ")
    for idx, token in enumerate(tokens):
        suffix = " " if idx < len(tokens) - 1 else ""
        yield format_sse("token", {
            "token": token + suffix,
            "index": idx
        })
        await asyncio.sleep(0.012)

    # Stage 6: Citations emission
    yield format_sse("citations", {
        "citations": result.get("citations", [])
    })
    await asyncio.sleep(0.01)

    # Stage 7: Clickable follow-up symptom clarification chips
    yield format_sse("follow_up_chips", {
        "chips": result.get("follow_up_chips", [])
    })
    await asyncio.sleep(0.01)

    # Stage 8: Done event
    yield format_sse("done", {
        "status": "complete",
        "state": state_val,
        "acuity": acuity_val,
        "llm_provider": result.get("llm_provider", "local_deterministic"),
        "llm_model": result.get("llm_model", "MedGuard-Local-Deterministic-RAG"),
        "cloud_synthesized": result.get("cloud_synthesized", False),
        "scrubbed_entities": result.get("scrubbed_entities", [])
    })


@router.get("/llm-status")
async def get_hybrid_llm_status():
    """
    Returns current Hybrid Cloud LLM Connector configuration, active model,
    PHI scrubbing enforcement status, and available cloud providers.
    """
    return hybrid_llm_connector.get_status()


@router.post("/llm-config")
async def configure_hybrid_llm(payload: HybridLLMConfigRequest):
    """
    Dynamically updates the active Hybrid Cloud LLM provider (Google Gemini 1.5 Pro,
    Claude 3.5 Sonnet, OpenAI GPT-4o, or Local Deterministic Engine) and API keys at runtime.
    """
    return hybrid_llm_connector.configure_runtime(
        provider=payload.provider,
        gemini_api_key=payload.gemini_api_key,
        anthropic_api_key=payload.anthropic_api_key,
        openai_api_key=payload.openai_api_key,
        gemini_model=payload.gemini_model,
        anthropic_model=payload.anthropic_model,
        openai_model=payload.openai_model
    )


@router.post("/stream")
async def chat_stream_endpoint(request_body: ChatStreamRequest):
    """
    Server-Sent Events (SSE) streaming endpoint for real-time conversational clinical triage.
    Emits structured status transitions, early triage badge header, streamed tokens,
    expandable ICD-11 citation cards, and interactive SOCRATES follow-up chips.
    """
    return StreamingResponse(
        sse_event_stream(
            message=request_body.message,
            history=request_body.conversation_history,
            preferred_language=request_body.preferred_language,
            age_group=request_body.age_group or "ADULT",
            biological_sex=request_body.biological_sex or "UNSPECIFIED"
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/stream")
async def chat_stream_get_endpoint(
    message: str = Query(..., min_length=1, max_length=1500),
    preferred_language: Optional[str] = Query(None)
):
    """
    GET fallback for SSE browser EventSource compatibility.
    """
    return StreamingResponse(
        sse_event_stream(
            message=message,
            preferred_language=preferred_language
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
