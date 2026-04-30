"""
El Monstruo — AG-UI SSE Adapter (Sprint 12 → Sprint 42 Streaming Fix)
======================================================================
Streams kernel events in AG-UI protocol format over SSE.
This adapter translates LangGraph kernel events into the
AG-UI event stream that CopilotKit/Command Center consumes.

Sprint 42 Fix: Heartbeat-enabled streaming to prevent Railway proxy buffering.
Root cause (diagnosed by Los 3 Sabios): Phase 1 pre-LLM processing yields
nothing for several seconds, causing Railway's proxy to buffer the entire
response until the first chunk arrives. Fix: emit an immediate SSE event
at connection time + periodic heartbeat comments during processing gaps.

AG-UI Events emitted:
  - RUN_STARTED       → When a new run begins
  - THINKING_STATE    → Processing status updates (new in Sprint 42)
  - TEXT_MESSAGE_START → When assistant starts responding
  - TEXT_MESSAGE_CONTENT → Streaming text chunks
  - TEXT_MESSAGE_END   → When assistant finishes
  - TOOL_CALL_START    → When a tool is invoked
  - TOOL_CALL_ARGS     → Tool arguments (streamed)
  - TOOL_CALL_END      → Tool execution complete
  - RUN_FINISHED       → When the full run completes
  - RUN_ERROR          → On error

ADR-012 Section 4: "AG-UI adapter wraps the existing /v1/chat/stream
endpoint and translates events into AG-UI protocol format."
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Optional
from uuid import uuid4

import structlog
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

logger = structlog.get_logger("agui_adapter")

router = APIRouter(prefix="/v1/agui", tags=["ag-ui"])

# ── Module-level dependency ───────────────────────────────────────
_kernel = None
_thoughts_store = None

# ── Heartbeat Configuration ───────────────────────────────────────
_HEARTBEAT_INTERVAL_S = 3.0  # Send heartbeat every 3s during silence


def set_dependencies(kernel=None, thoughts_store=None):
    """Inject dependencies from lifespan."""
    global _kernel, _thoughts_store
    _kernel = kernel
    _thoughts_store = thoughts_store


# ── Request Model ─────────────────────────────────────────────────


class AGUIRunRequest(BaseModel):
    """AG-UI run request."""

    thread_id: Optional[str] = None
    run_id: Optional[str] = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    tools: list[dict[str, Any]] = Field(default_factory=list)
    context: list[dict[str, Any]] = Field(default_factory=list)
    forwarded_props: dict[str, Any] = Field(default_factory=dict)


# ── SSE Helpers ───────────────────────────────────────────────────


def _sse_event(event_type: str, data: dict) -> str:
    """Format an SSE event string."""
    payload = json.dumps({"type": event_type, **data}, default=str)
    return f"data: {payload}\n\n"


def _heartbeat() -> str:
    """SSE heartbeat comment to keep connection alive.
    SSE comments (lines starting with ':') are ignored by clients
    but force the proxy to flush its buffer."""
    return ": heartbeat\n\n"


# ── AG-UI Event Types ────────────────────────────────────────────


class AGUIEventType:
    RUN_STARTED = "RUN_STARTED"
    THINKING_STATE = "THINKING_STATE"
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"


# ── Main SSE Endpoint ────────────────────────────────────────────


@router.post("/run")
async def agui_run(req: AGUIRunRequest, request: Request):
    """AG-UI compatible SSE endpoint.
    Accepts AG-UI protocol messages, runs through the kernel,
    and streams back AG-UI events.

    Sprint 42: Uses heartbeat-interleaved streaming to prevent
    Railway proxy buffering during pre-LLM processing phases."""
    if not _kernel:
        raise HTTPException(503, "Kernel not initialized")

    run_id = req.run_id or str(uuid4())
    thread_id = req.thread_id or str(uuid4())

    # Extract the last user message
    user_message = ""
    for msg in reversed(req.messages):
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str):
                user_message = content
            elif isinstance(content, list):
                # Handle structured content
                user_message = " ".join(p.get("text", "") for p in content if p.get("type") == "text")
            break

    if not user_message:
        raise HTTPException(400, "No user message found")

    async def event_stream():
        """Generate AG-UI SSE events from kernel execution.

        Strategy (Sprint 42 — Los 3 Sabios consensus):
        1. Emit RUN_STARTED immediately to open the stream
        2. Start a heartbeat task that sends SSE comments every 3s
        3. Each real event resets the heartbeat timer
        4. Heartbeats keep Railway's proxy in streaming mode
        """
        last_yield_time = time.monotonic()

        async def _maybe_heartbeat():
            """Yield heartbeat if we haven't sent anything recently."""
            nonlocal last_yield_time
            now = time.monotonic()
            if now - last_yield_time >= _HEARTBEAT_INTERVAL_S:
                last_yield_time = now
                return _heartbeat()
            return None

        try:
            # ── IMMEDIATE: RUN_STARTED (opens the stream) ──────────
            yield _sse_event(
                AGUIEventType.RUN_STARTED,
                {
                    "runId": run_id,
                    "threadId": thread_id,
                },
            )
            last_yield_time = time.monotonic()

            # TEXT_MESSAGE_START
            message_id = str(uuid4())
            yield _sse_event(
                AGUIEventType.TEXT_MESSAGE_START,
                {
                    "messageId": message_id,
                    "role": "assistant",
                },
            )
            last_yield_time = time.monotonic()

            # Execute through kernel
            from contracts.kernel_interface import RunInput

            run_input = RunInput(
                message=user_message,
                user_id=req.forwarded_props.get("user_id", "anonymous"),
                channel="command-center",
                context={"thread_id": thread_id, "agui": True},
            )

            # Try streaming first
            full_response = ""
            tool_calls_emitted = []

            try:
                # ── Stream with heartbeat interleaving ──────────────
                # We use asyncio.wait_for with a timeout to interleave
                # heartbeats when the kernel is slow to yield.
                kernel_stream = _kernel.stream(run_input).__aiter__()
                stream_exhausted = False

                while not stream_exhausted:
                    # Check if client disconnected
                    if await request.is_disconnected():
                        logger.info("agui_client_disconnected", run_id=run_id)
                        return

                    try:
                        # Wait for next chunk with timeout
                        raw_chunk = await asyncio.wait_for(
                            kernel_stream.__anext__(),
                            timeout=_HEARTBEAT_INTERVAL_S,
                        )
                    except asyncio.TimeoutError:
                        # No chunk received within interval — send heartbeat
                        yield _heartbeat()
                        last_yield_time = time.monotonic()
                        continue
                    except StopAsyncIteration:
                        stream_exhausted = True
                        break

                    # Process the chunk
                    if isinstance(raw_chunk, str):
                        try:
                            chunk = json.loads(raw_chunk)
                        except (json.JSONDecodeError, TypeError):
                            continue
                    else:
                        chunk = raw_chunk

                    chunk_type = chunk.get("type", "")

                    if chunk_type in ("chunk", "token"):
                        # Real LLM streaming token
                        chunk_data = chunk.get("text", chunk.get("data", ""))
                        full_response += chunk_data
                        yield _sse_event(
                            AGUIEventType.TEXT_MESSAGE_CONTENT,
                            {
                                "messageId": message_id,
                                "delta": chunk_data,
                            },
                        )
                        last_yield_time = time.monotonic()

                    elif chunk_type == "meta":
                        # Forward meta events as THINKING_STATE for Flutter
                        yield _sse_event(
                            AGUIEventType.THINKING_STATE,
                            {
                                "messageId": message_id,
                                "intent": chunk.get("intent", ""),
                                "model": chunk.get("model", ""),
                                "enriched": chunk.get("enriched", False),
                                "memoriesFound": chunk.get("memories_found", 0),
                            },
                        )
                        last_yield_time = time.monotonic()

                    elif chunk_type == "tool_start":
                        # Tool invocation started
                        chunk_data = chunk.get("data", {})
                        tool_call_id = str(uuid4())
                        tool_calls_emitted.append(tool_call_id)
                        yield _sse_event(
                            AGUIEventType.TOOL_CALL_START,
                            {
                                "toolCallId": tool_call_id,
                                "toolCallName": chunk_data.get("name", "unknown") if isinstance(chunk_data, dict) else "unknown",
                            },
                        )
                        last_yield_time = time.monotonic()
                        if isinstance(chunk_data, dict) and chunk_data.get("args"):
                            yield _sse_event(
                                AGUIEventType.TOOL_CALL_ARGS,
                                {
                                    "toolCallId": tool_call_id,
                                    "delta": json.dumps(chunk_data["args"]),
                                },
                            )
                            last_yield_time = time.monotonic()

                    elif chunk_type == "tool_end":
                        chunk_data = chunk.get("data", {})
                        if tool_calls_emitted:
                            yield _sse_event(
                                AGUIEventType.TOOL_CALL_END,
                                {
                                    "toolCallId": tool_calls_emitted[-1],
                                    "result": str(chunk_data.get("result", "") if isinstance(chunk_data, dict) else chunk_data)[:1000],
                                },
                            )
                            last_yield_time = time.monotonic()

                    elif chunk_type in ("error",):
                        yield _sse_event(
                            AGUIEventType.RUN_ERROR,
                            {
                                "message": str(chunk.get("message", chunk.get("data", "Unknown error"))),
                            },
                        )
                        last_yield_time = time.monotonic()

                    elif chunk_type == "done":
                        # Done event from kernel — stream is about to end
                        continue

            except AttributeError:
                # Kernel doesn't have stream method, fall back to sync
                logger.info("agui_fallback_sync", run_id=run_id)
                result = await _kernel.start_run(run_input)
                full_response = result.response if hasattr(result, "response") else str(result)

                # Emit full response as single chunk
                yield _sse_event(
                    AGUIEventType.TEXT_MESSAGE_CONTENT,
                    {
                        "messageId": message_id,
                        "delta": full_response,
                    },
                )

            # TEXT_MESSAGE_END
            yield _sse_event(
                AGUIEventType.TEXT_MESSAGE_END,
                {
                    "messageId": message_id,
                },
            )

            # RUN_FINISHED
            yield _sse_event(
                AGUIEventType.RUN_FINISHED,
                {
                    "runId": run_id,
                    "threadId": thread_id,
                },
            )

        except Exception as e:
            logger.error("agui_stream_error", run_id=run_id, error=str(e))
            yield _sse_event(
                AGUIEventType.RUN_ERROR,
                {
                    "message": f"Internal error: {str(e)}",
                },
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Pragma": "no-cache",
            "Expires": "0",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ── Health/Info Endpoint ──────────────────────────────────────────


@router.get("/info")
async def agui_info():
    """AG-UI adapter info and capabilities."""
    return {
        "protocol": "ag-ui",
        "version": "0.2",
        "capabilities": {
            "streaming": True,
            "heartbeat": True,
            "tool_calls": True,
            "memory": _thoughts_store is not None,
        },
        "kernel_ready": _kernel is not None,
    }
