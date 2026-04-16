"""
El Monstruo — OpenAI-Compatible API Adapter
=============================================
Exposes /openai/v1/models and /openai/v1/chat/completions
so Open WebUI (and any OpenAI-compatible client) can talk to the kernel.

Maps "model" names to Monstruo brains and translates streaming format.

validated 2026-04-16 — Open WebUI v0.8.12 expects standard OpenAI SSE format.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Optional

import structlog
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

logger = structlog.get_logger("openai_adapter")

router = APIRouter(prefix="/openai/v1", tags=["openai-compat"])


# ── Model → Brain Mapping ────────────────────────────────────────────

OPENAI_MODEL_TO_BRAIN: dict[str, Optional[str]] = {
    "monstruo-auto":       None,           # Router decides
    "monstruo-estratega":  "estratega",    # GPT-5.4
    "monstruo-investigador": "investigador",  # Sonar Reasoning Pro
    "monstruo-arquitecto": "arquitecto",   # Claude Opus 4.6
    "monstruo-creativo":   "creativo",     # Gemini 3.1 Pro
    "monstruo-critico":    "critico",      # Grok 4.20
    "monstruo-rapido":     "operador",     # Gemini 3.1 Flash Lite
}

MODEL_DESCRIPTIONS: dict[str, str] = {
    "monstruo-auto":       "Modo automático — el router soberano decide el mejor modelo",
    "monstruo-estratega":  "Estratega (GPT-5.4) — análisis profundo y razonamiento complejo",
    "monstruo-investigador": "Investigador (Sonar Pro) — búsqueda web y datos en tiempo real",
    "monstruo-arquitecto": "Arquitecto (Claude Opus) — diseño de sistemas y código complejo",
    "monstruo-creativo":   "Creativo (Gemini Pro) — escritura, ideas, contenido original",
    "monstruo-critico":    "Crítico (Grok) — análisis contrario, devil's advocate",
    "monstruo-rapido":     "Rápido (Gemini Flash) — respuestas instantáneas, tareas simples",
}


# ── Request/Response Models (OpenAI format) ──────────────────────────

class OpenAIChatMessage(BaseModel):
    role: str
    content: Optional[str] = None
    name: Optional[str] = None

class OpenAIChatRequest(BaseModel):
    model: str = "monstruo-auto"
    messages: list[OpenAIChatMessage] = Field(default_factory=list)
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    # Open WebUI may send these — we accept but ignore
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[list[str]] = None
    user: Optional[str] = None


# ── GET /openai/v1/models ────────────────────────────────────────────

@router.get("/models")
async def list_models():
    """Return available models in OpenAI format for Open WebUI dropdown."""
    models = []
    for model_id, description in MODEL_DESCRIPTIONS.items():
        models.append({
            "id": model_id,
            "object": "model",
            "created": 1713200000,  # 2026-04-16 approx
            "owned_by": "el-monstruo",
            "permission": [],
            "root": model_id,
            "parent": None,
            "description": description,
        })
    return {"object": "list", "data": models}


# ── POST /openai/v1/chat/completions ─────────────────────────────────

@router.post("/chat/completions")
async def chat_completions(request: OpenAIChatRequest, raw_request: Request):
    """
    OpenAI-compatible chat completions endpoint.
    Translates to kernel format, executes, and returns in OpenAI format.
    """
    # Lazy import to avoid circular deps
    from kernel.main import kernel

    if not kernel:
        return JSONResponse(
            status_code=503,
            content={"error": {"message": "Kernel not initialized", "type": "server_error"}},
        )

    # Extract the last user message
    user_message = ""
    history = []
    for msg in request.messages:
        if msg.role == "system":
            # System messages become context
            continue
        elif msg.role == "user":
            user_message = msg.content or ""
        elif msg.role == "assistant":
            pass
        # Build history for context
        if msg.content:
            history.append({"role": msg.role, "content": msg.content})

    if not user_message:
        return JSONResponse(
            status_code=400,
            content={"error": {"message": "No user message found", "type": "invalid_request_error"}},
        )

    # Map model to brain
    brain = OPENAI_MODEL_TO_BRAIN.get(request.model)

    # Build kernel context
    context: dict[str, Any] = {
        "source": "openwebui",
        "history": history[:-1] if history else [],  # Exclude last user msg (it's the main message)
    }
    if brain:
        context["brain"] = brain

    # Build RunInput
    from contracts.kernel_interface import RunInput
    run_id = uuid.uuid4()
    run_input = RunInput(
        run_id=run_id,
        user_id=request.user or "alfredo",
        channel="openwebui",
        message=user_message,
        context=context,
    )

    completion_id = f"chatcmpl-{run_id.hex[:24]}"

    if request.stream:
        return StreamingResponse(
            _stream_response(kernel, run_input, completion_id, request.model),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        return await _sync_response(kernel, run_input, completion_id, request.model)


async def _stream_response(kernel, run_input, completion_id: str, model: str):
    """Stream kernel response in OpenAI SSE format."""
    created = int(time.time())

    try:
        async for chunk in kernel.stream(run_input):
            # kernel.stream yields text chunks
            if chunk and chunk != "[DONE]":
                sse_data = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None,
                    }],
                }
                yield f"data: {json.dumps(sse_data)}\n\n"

        # Final chunk with finish_reason
        final_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop",
            }],
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error("openai_stream_error", error=str(e))
        error_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"content": f"\n\n[Error: {str(e)}]"},
                "finish_reason": "stop",
            }],
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"
        yield "data: [DONE]\n\n"


async def _sync_response(kernel, run_input, completion_id: str, model: str):
    """Non-streaming response in OpenAI format."""
    created = int(time.time())

    try:
        output = await kernel.start_run(run_input)

        return JSONResponse(content={
            "id": completion_id,
            "object": "chat.completion",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output.response,
                },
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": output.tokens_in,
                "completion_tokens": output.tokens_out,
                "total_tokens": output.tokens_in + output.tokens_out,
            },
            "system_fingerprint": f"monstruo-{output.model_used}",
        })

    except Exception as e:
        logger.error("openai_sync_error", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(e), "type": "server_error"}},
        )
