"""
El Monstruo — OpenAI-Compatible API Adapter (v2)
==================================================
Exposes /openai/v1/models and /openai/v1/chat/completions
so Open WebUI (and any OpenAI-compatible client) can talk to the kernel.

Maps "model" names to Monstruo brains and translates streaming format.

The kernel.stream() yields JSON strings in Monstruo's internal format:
  {"type": "meta", "intent": ..., "model": ..., "enriched": ...}
  {"type": "chunk", "text": "..."}
  {"type": "done", "latency_ms": ..., "model_used": ..., "tokens_in": ..., "tokens_out": ...}
  {"type": "error", "message": "..."}

This adapter translates those into OpenAI-standard SSE:
  data: {"id": "...", "object": "chat.completion.chunk", "choices": [{"delta": {"content": "..."}}]}

v2 fixes (validated 2026-04-16 by Claude Opus 4.7 + Manus real-time testing):
  - Fix #1: Multimodal content support (content as str or list)
  - Fix #2: Error sanitization (no stack traces to frontend)
  - Fix #3: System prompts passed to kernel (not ignored)
  - Fix #4: Client disconnect cancels kernel streaming + heartbeat keepalive
  - Fix #5: stream_options.include_usage for Open WebUI token count display
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from typing import Any, Optional, Union

import structlog
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

logger = structlog.get_logger("openai_adapter")

router = APIRouter(prefix="/openai/v1", tags=["openai-compat"])


# ── Model → Brain Mapping ────────────────────────────────────────────

OPENAI_MODEL_TO_BRAIN: dict[str, Optional[str]] = {
    "monstruo-auto": None,  # Router decides
    "monstruo-estratega": "estratega",  # GPT-5.4
    "monstruo-investigador": "investigador",  # Sonar Reasoning Pro
    "monstruo-arquitecto": "arquitecto",  # Claude Opus 4.6
    "monstruo-creativo": "creativo",  # Gemini 3.1 Pro
    "monstruo-critico": "critico",  # Grok 4.20
    "monstruo-rapido": "operador",  # Gemini 3.1 Flash Lite
}

MODEL_DESCRIPTIONS: dict[str, str] = {
    "monstruo-auto": "Modo automático — el router soberano decide el mejor modelo",
    "monstruo-estratega": "Estratega (GPT-5.4) — análisis profundo y razonamiento complejo",
    "monstruo-investigador": "Investigador (Sonar Pro) — búsqueda web y datos en tiempo real",
    "monstruo-arquitecto": "Arquitecto (Claude Opus) — diseño de sistemas y código complejo",
    "monstruo-creativo": "Creativo (Gemini Pro) — escritura, ideas, contenido original",
    "monstruo-critico": "Crítico (Grok) — análisis contrario, devil's advocate",
    "monstruo-rapido": "Rápido (Gemini Flash) — respuestas instantáneas, tareas simples",
}


# ── Helpers ─────────────────────────────────────────────────────────


def _extract_text(content: Any) -> str:
    """
    Normalize OpenAI content field to plain text.
    Handles both string content and multimodal list content.
    Fix #1: Open WebUI with images sends content as list of dicts.
    validated 2026-04-16
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(part.get("text", ""))
            # BACKLOG Sprint 29+: image_url support for multimodal (requires GPT-5.5 vision pipeline)
        return "\n".join(parts)
    return str(content)


def _safe_error_message(e: Exception) -> str:
    """
    Sanitize error messages before sending to frontend.
    Fix #2: Never expose stack traces, SQL, API keys, or internal paths.
    validated 2026-04-16
    """
    env = os.getenv("MONSTRUO_ENV", "production")
    if env == "dev":
        # In dev mode, show truncated error for debugging
        return str(e)[:200]
    # In production, generic message + log the real error server-side
    return "Internal error — check server logs"


# ── Request/Response Models (OpenAI format) ──────────────────────────


class StreamOptions(BaseModel):
    """OpenAI stream_options for usage reporting. validated 2026-04-16"""

    include_usage: bool = False


class OpenAIChatMessage(BaseModel):
    role: str
    content: Optional[Union[str, list]] = None  # Fix #1: str or multimodal list
    name: Optional[str] = None


class OpenAIChatRequest(BaseModel):
    model: str = "monstruo-auto"
    messages: list[OpenAIChatMessage] = Field(default_factory=list)
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream_options: Optional[StreamOptions] = None  # Fix #5: usage in streaming
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
        models.append(
            {
                "id": model_id,
                "object": "model",
                "created": 1713200000,  # 2026-04-16 approx
                "owned_by": "el-monstruo",
                "permission": [],
                "root": model_id,
                "parent": None,
                "description": description,
            }
        )
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

    # ── Fix #1 + #3: Robust message extraction ──────────────────────
    system_prompts: list[str] = []
    history: list[dict] = []
    user_message = ""

    for msg in request.messages:
        text = _extract_text(msg.content)
        if not text:
            continue
        if msg.role == "system":
            system_prompts.append(text)  # Fix #3: preserve system prompts
        else:
            history.append({"role": msg.role, "content": text})

    # The last user message is the current query
    if history and history[-1]["role"] == "user":
        user_message = history[-1]["content"]
        history = history[:-1]
    else:
        # Edge case: regeneration (last msg is assistant) — find last user msg
        for msg in reversed(history):
            if msg["role"] == "user":
                user_message = msg["content"]
                break

    if not user_message:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "message": "No user message found",
                    "type": "invalid_request_error",
                }
            },
        )

    # Map model to brain
    brain = OPENAI_MODEL_TO_BRAIN.get(request.model)

    # Build kernel context
    context: dict[str, Any] = {
        "source": "openwebui",
        "history": history,
        "system_prompts": system_prompts,  # Fix #3: kernel decides how to use them
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
        include_usage = request.stream_options.include_usage if request.stream_options else False
        return StreamingResponse(
            _stream_response(
                kernel,
                run_input,
                completion_id,
                request.model,
                raw_request,
                include_usage,  # Fix #4 + #5
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        return await _sync_response(kernel, run_input, completion_id, request.model)


def _make_sse_chunk(
    completion_id: str,
    created: int,
    model: str,
    content: Optional[str] = None,
    finish_reason: Optional[str] = None,
) -> str:
    """Build a single OpenAI-format SSE data line."""
    delta: dict[str, Any] = {}
    if content is not None:
        delta["content"] = content
    if finish_reason is not None and not delta:
        # Empty delta for final chunk
        pass

    sse_data = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": delta,
                "finish_reason": finish_reason,
            }
        ],
    }
    return f"data: {json.dumps(sse_data)}\n\n"


async def _stream_response(
    kernel,
    run_input,
    completion_id: str,
    model: str,
    raw_request: Request,
    include_usage: bool = False,  # Fix #4 + #5
):
    """
    Stream kernel response in OpenAI SSE format.

    Fix #4: Detects client disconnect and stops streaming.
    Fix #5: Emits usage chunk if stream_options.include_usage is true.
    validated 2026-04-16
    """
    created = int(time.time())
    tokens_in = 0
    tokens_out = 0

    # Send initial role delta (Open WebUI expects this)
    role_chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {"role": "assistant", "content": ""},
                "finish_reason": None,
            }
        ],
    }
    yield f"data: {json.dumps(role_chunk)}\n\n"

    try:
        stream_iter = kernel.stream(run_input).__aiter__()
        stream_done = False

        while not stream_done:
            # Fix #4: Check if client disconnected
            if await raw_request.is_disconnected():
                logger.info("client_disconnected", completion_id=completion_id)
                if hasattr(kernel, "cancel_run"):
                    await kernel.cancel_run(run_input.run_id)
                break

            try:
                # Timeout for heartbeat: if kernel takes >15s, send keepalive
                raw_chunk = await asyncio.wait_for(stream_iter.__anext__(), timeout=15.0)
            except asyncio.TimeoutError:
                # Fix #4: SSE comment keepalive — invisible to client
                yield ": keepalive\n\n"
                continue
            except StopAsyncIteration:
                break

            if not raw_chunk:
                continue

            # Parse the kernel's JSON event
            try:
                event = json.loads(raw_chunk)
            except (json.JSONDecodeError, TypeError):
                # If it's not JSON, treat as raw text
                yield _make_sse_chunk(completion_id, created, model, content=str(raw_chunk))
                continue

            event_type = event.get("type", "")

            if event_type == "chunk":
                # Text content — this is what we want to send to the user
                text = event.get("text", "")
                if text:
                    yield _make_sse_chunk(completion_id, created, model, content=text)

            elif event_type == "meta":
                # Metadata events — skip silently (don't show to user)
                logger.debug("stream_meta", **{k: v for k, v in event.items() if k != "type"})

            elif event_type == "done":
                # Stream completed — capture usage data
                tokens_in = event.get("tokens_in", 0)
                tokens_out = event.get("tokens_out", 0)
                cost_usd = event.get("cost_usd", 0.0)
                logger.info(
                    "stream_done",
                    completion_id=completion_id,
                    latency_ms=event.get("latency_ms"),
                    model_used=event.get("model_used"),
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    cost_usd=cost_usd,
                )
                # Sprint 3: Record cost for rate limiter cost caps
                if cost_usd > 0:
                    try:
                        from kernel.rate_limiter import _get_client_id, record_cost

                        client_id = _get_client_id(raw_request)
                        record_cost(client_id, cost_usd)
                    except Exception:
                        pass  # Non-fatal — don't break streaming
                stream_done = True

            elif event_type == "error":
                # Fix #2: Sanitize error before sending to user
                error_msg = event.get("message", "Unknown error")
                safe_msg = _safe_error_message(Exception(error_msg))
                yield _make_sse_chunk(completion_id, created, model, content=f"\n\n[Error: {safe_msg}]")

            else:
                # Unknown event type — log and skip
                logger.warning(
                    "unknown_stream_event",
                    event_type=event_type,
                    raw=str(raw_chunk)[:200],
                )

        # Fix #5: Emit usage chunk if requested
        if include_usage and (tokens_in or tokens_out):
            usage_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [],
                "usage": {
                    "prompt_tokens": tokens_in,
                    "completion_tokens": tokens_out,
                    "total_tokens": tokens_in + tokens_out,
                },
            }
            yield f"data: {json.dumps(usage_chunk)}\n\n"

        # Final chunk with finish_reason=stop
        yield _make_sse_chunk(completion_id, created, model, finish_reason="stop")
        yield "data: [DONE]\n\n"

    except Exception as e:
        # Fix #2: Never expose internals
        logger.error("openai_stream_error", error=str(e), exc_info=True)
        yield _make_sse_chunk(
            completion_id,
            created,
            model,
            content=f"\n\n[Error: {_safe_error_message(e)}]",
        )
        yield _make_sse_chunk(completion_id, created, model, finish_reason="stop")
        yield "data: [DONE]\n\n"


async def _sync_response(kernel, run_input, completion_id: str, model: str):
    """Non-streaming response in OpenAI format."""
    created = int(time.time())

    try:
        output = await kernel.start_run(run_input)

        return JSONResponse(
            content={
                "id": completion_id,
                "object": "chat.completion",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": output.response,
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": output.tokens_in,
                    "completion_tokens": output.tokens_out,
                    "total_tokens": output.tokens_in + output.tokens_out,
                },
                "system_fingerprint": f"monstruo-{output.model_used}",
            }
        )

    except Exception as e:
        # Fix #2: Sanitize errors in sync mode too
        logger.error("openai_sync_error", error=str(e), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": {"message": _safe_error_message(e), "type": "server_error"}},
        )
