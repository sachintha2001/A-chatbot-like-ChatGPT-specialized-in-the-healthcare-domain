import json
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse

from app.engine.triage_state_machine import triage_state_machine

router = APIRouter(prefix="/chat", tags=["Clinical Conversational Streaming"])


class ChatStreamRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1500)
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    preferred_language: Optional[str] = None
    age_group: Optional[str] = "ADULT"
    biological_sex: Optional[str] = "UNSPECIFIED"


async def sse_event_stream(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    preferred_language: Optional[str] = None
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

    # Stage 1: Red-flag screening
    yield format_sse("status", {
        "stage": "screening_red_flags",
        "message": "Screening deterministic red-flag criteria and vital compromise triggers..."
    })
    await asyncio.sleep(0.04)

    # Process state machine
    result = triage_state_machine.process_turn(
        user_message=message,
        conversation_history=history
    )

    # Stage 2: Knowledge retrieval & ontology mapping
    yield format_sse("status", {
        "stage": "knowledge_retrieval",
        "message": "Querying WHO ICD-11 ontology, clinical vector store, and practice guidelines..."
    })
    await asyncio.sleep(0.04)

    # Stage 3: Immediate triage badge emission before text stream completes
    acuity_val = result["acuity"].value if hasattr(result["acuity"], "value") else str(result["acuity"])
    state_val = result["state"].value if hasattr(result["state"], "value") else str(result["state"])
    yield format_sse("triage_badge", {
        "state": state_val,
        "acuity": acuity_val,
        "headline": result["headline"],
        "is_emergency": state_val == "RED_FLAG_EMERGENCY"
    })
    await asyncio.sleep(0.02)

    # Stage 4: Synthesizing response stage
    yield format_sse("status", {
        "stage": "synthesizing_response",
        "message": "Synthesizing evidence-backed clinical response with safety netting..."
    })
    await asyncio.sleep(0.03)

    # Stage 5: Token streaming
    content = result["content"]
    # Split by words preserving punctuation for natural streaming flow
    tokens = content.split(" ")
    for idx, token in enumerate(tokens):
        suffix = " " if idx < len(tokens) - 1 else ""
        yield format_sse("token", {
            "token": token + suffix,
            "index": idx
        })
        # Ultra-low-latency 12ms delay simulates fluid neural token generation
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
        "acuity": acuity_val
    })


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
            preferred_language=request_body.preferred_language
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
