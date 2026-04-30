"""
El Monstruo — AG-UI SSE Adapter (Sprint 12)
=============================================
Streams kernel events in AG-UI protocol format over SSE.
This adapter translates LangGraph kernel events into the
AG-UI event stream that CopilotKit/Command Center consumes.

AG-UI Events emitted:
  - RUN_STARTED       → When a new run begins
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

import json
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
    """SSE heartbeat to keep connection alive."""
    return ": heartbeat\n\n"


# ── AG-UI Event Types ────────────────────────────────────────────


class AGUIEventType:
    RUN_STARTED = "RUN_STARTED"
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
    and streams back AG-UI events."""
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
        """Generate AG-UI SSE events from kernel execution."""
        try:
            # RUN_STARTED
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
                async for chunk in _kernel.stream(run_input):
                    # Check if client disconnected
                    if await request.is_disconnected():
                        logger.info("agui_client_disconnected", run_id=run_id)
                        return

                    chunk_type = chunk.get("type", "")
                    chunk_data = chunk.get("data", "")

                    if chunk_type == "token":
                        # Streaming text token
                        full_response += chunk_data
                        yield _sse_event(
                            AGUIEventType.TEXT_MESSAGE_CONTENT,
                            {
                                "messageId": message_id,
                                "delta": chunk_data,
                            },
                        )

                    elif chunk_type == "tool_start":
                        # Tool invocation started
                        tool_call_id = str(uuid4())
                        tool_calls_emitted.append(tool_call_id)
                        yield _sse_event(
                            AGUIEventType.TOOL_CALL_START,
                            {
                                "toolCallId": tool_call_id,
                                "toolCallName": chunk_data.get("name", "unknown"),
                            },
                        )
                        if chunk_data.get("args"):
                            yield _sse_event(
                                AGUIEventType.TOOL_CALL_ARGS,
                                {
                                    "toolCallId": tool_call_id,
                                    "delta": json.dumps(chunk_data["args"]),
                                },
                            )

                    elif chunk_type == "tool_end":
                        if tool_calls_emitted:
                            yield _sse_event(
                                AGUIEventType.TOOL_CALL_END,
                                {
                                    "toolCallId": tool_calls_emitted[-1],
                                    "result": str(chunk_data.get("result", ""))[:1000],
                                },
                            )

                    elif chunk_type == "error":
                        yield _sse_event(
                            AGUIEventType.RUN_ERROR,
                            {
                                "message": str(chunk_data),
                            },
                        )
                        return

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
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ── Health/Info Endpoint ──────────────────────────────────────────


@router.get("/info")
async def agui_info():
    """AG-UI adapter info and capabilities."""
    return {
        "protocol": "ag-ui",
        "version": "0.1",
        "capabilities": {
            "streaming": True,
            "tool_calls": True,
            "memory": _thoughts_store is not None,
        },
        "kernel_ready": _kernel is not None,
    }
