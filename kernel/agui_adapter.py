"""
El Monstruo — AG-UI SSE Adapter (Sprint 12 → Sprint 42 Streaming Fix v2)
=========================================================================
Streams kernel events in AG-UI protocol format over SSE.
This adapter translates LangGraph kernel events into the
AG-UI event stream that CopilotKit/Command Center consumes.

Sprint 42 Fix v2: Safe heartbeat-enabled streaming to prevent Railway
proxy buffering. Uses asyncio.Queue to decouple kernel streaming from
heartbeat emission — avoids asyncio.wait_for() which cancels the
underlying async generator and corrupts its state.

AG-UI Events emitted:
  - RUN_STARTED       → When a new run begins
  - THINKING_STATE    → Processing status updates
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
_HEARTBEAT_INTERVAL_S = 2.5  # Send heartbeat every 2.5s during silence

# ── Sentinel for stream end ───────────────────────────────────────
_STREAM_END = object()


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
    STEP = "STEP"  # Sprint 43: Structured thinking step events
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

    Sprint 42 v2: Uses asyncio.Queue to safely interleave heartbeats
    without corrupting the kernel's async generator."""
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

        Strategy (Sprint 42 v2 — safe heartbeat):
        1. Emit RUN_STARTED + TEXT_MESSAGE_START immediately
        2. Spawn a background task that reads from the kernel async generator
           and pushes chunks into an asyncio.Queue
        3. The main generator reads from the queue with a timeout
        4. On timeout → yield heartbeat; on item → process and yield SSE event
        5. This avoids asyncio.wait_for() which cancels __anext__() and
           corrupts the async generator state
        """
        try:
            # ── IMMEDIATE: RUN_STARTED (opens the stream) ──────────
            yield _sse_event(
                AGUIEventType.RUN_STARTED,
                {
                    "runId": run_id,
                    "threadId": thread_id,
                },
            )

            # TEXT_MESSAGE_START
            message_id = str(uuid4())
            yield _sse_event(
                AGUIEventType.TEXT_MESSAGE_START,
                {
                    "messageId": message_id,
                    "role": "assistant",
                },
            )

            # Execute through kernel
            from contracts.kernel_interface import RunInput

            # Build context — propagate hints from forwarded_props
            # Sprint 84.5 Bug 4 fix: intent_override and model_hint must reach
            # the engine for tests/clients that pre-classify the intent.
            run_context = {"thread_id": thread_id, "agui": True}
            dispatch_agent = req.forwarded_props.get("dispatch_agent")
            if dispatch_agent:
                run_context["dispatch_agent"] = dispatch_agent
            intent_override = req.forwarded_props.get("intent_override")
            if intent_override:
                run_context["intent_override"] = intent_override
            model_hint = req.forwarded_props.get("model_hint")
            if model_hint:
                run_context["model_hint"] = model_hint

            run_input = RunInput(
                message=user_message,
                user_id=req.forwarded_props.get("user_id", "anonymous"),
                channel="command-center",
                context=run_context,
            )

            # Try streaming first
            full_response = ""
            tool_calls_emitted = []

            try:
                # ── Queue-based heartbeat interleaving ─────────────
                # The kernel's async generator runs in a background task
                # that pushes items into a queue. The main loop reads
                # from the queue with a timeout for heartbeats.
                queue: asyncio.Queue = asyncio.Queue()

                async def _pump_kernel():
                    """Read from kernel stream and push into queue."""
                    try:
                        async for raw_chunk in _kernel.stream(run_input):
                            await queue.put(raw_chunk)
                    except Exception as pump_err:
                        await queue.put(pump_err)
                    finally:
                        await queue.put(_STREAM_END)

                # Start the kernel pump as a background task
                pump_task = asyncio.create_task(_pump_kernel())

                try:
                    while True:
                        # Check if client disconnected
                        if await request.is_disconnected():
                            logger.info("agui_client_disconnected", run_id=run_id)
                            pump_task.cancel()
                            return

                        try:
                            item = await asyncio.wait_for(
                                queue.get(),
                                timeout=_HEARTBEAT_INTERVAL_S,
                            )
                        except asyncio.TimeoutError:
                            # Queue empty for too long — send heartbeat
                            yield _heartbeat()
                            continue

                        # Check for stream end
                        if item is _STREAM_END:
                            break

                        # Check for errors from pump
                        if isinstance(item, Exception):
                            logger.error("agui_pump_error", run_id=run_id, error=str(item))
                            yield _sse_event(
                                AGUIEventType.RUN_ERROR,
                                {"message": f"Kernel stream error: {str(item)}"},
                            )
                            break

                        # Process the chunk
                        raw_chunk = item
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

                        elif chunk_type == "step":
                            # Sprint 43: Structured step events for thinking indicator
                            yield _sse_event(
                                AGUIEventType.STEP,
                                {
                                    "messageId": message_id,
                                    "stepId": chunk.get("id", ""),
                                    "status": chunk.get("status", "in_progress"),
                                    "label": chunk.get("label", ""),
                                    "icon": chunk.get("icon", ""),
                                },
                            )

                        elif chunk_type == "progress":
                            # Sprint 42: Legacy progress events (backward compat)
                            # Forward as THINKING_STATE so older Flutter versions still work
                            yield _sse_event(
                                AGUIEventType.THINKING_STATE,
                                {
                                    "messageId": message_id,
                                    "phase": chunk.get("phase", ""),
                                    "detail": chunk.get("detail", ""),
                                },
                            )

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
                            if isinstance(chunk_data, dict) and chunk_data.get("args"):
                                yield _sse_event(
                                    AGUIEventType.TOOL_CALL_ARGS,
                                    {
                                        "toolCallId": tool_call_id,
                                        "delta": json.dumps(chunk_data["args"]),
                                    },
                                )

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

                        elif chunk_type in ("error",):
                            yield _sse_event(
                                AGUIEventType.RUN_ERROR,
                                {
                                    "message": str(chunk.get("message", chunk.get("data", "Unknown error"))),
                                },
                            )

                        elif chunk_type == "done":
                            # Done event from kernel — stream is about to end
                            continue

                finally:
                    # Ensure pump task is cleaned up
                    if not pump_task.done():
                        pump_task.cancel()
                        try:
                            await pump_task
                        except (asyncio.CancelledError, Exception):
                            pass

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
