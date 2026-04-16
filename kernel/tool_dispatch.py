"""
El Monstruo — Tool Dispatch Node (Sprint 2 — Opción E)
========================================================
Executes tool calls that the LLM requested via native function calling.

Strategy (validated by Consejo de 6 Sabios, 2026-04-16):
  - LLMClient sends tool definitions to the LLM via native function calling
  - If the LLM responds with tool_calls, execute node stores them in state
  - tool_dispatch executes the tools and stores results in state
  - Graph loops back to execute, which makes a follow-up LLM call with results
  - Max 3 loops to prevent runaway tool chains

Graph topology:
    execute → should_loop_tools? → tool_dispatch → execute  (if tool_calls)
    execute → should_loop_tools? → hitl_gate → respond      (if no tool_calls)

Anti-autoboicot: validated 2026-04-16 against LangGraph 1.1.6, google-genai 1.73.0,
openai 2.30.0, anthropic 0.94.1.

Principio: Las Manos son soberanas. El dispatch es nuestro.
"""

from __future__ import annotations

import json
import time
from typing import Any

import structlog
from langchain_core.runnables import RunnableConfig

from contracts.event_envelope import EventBuilder, EventCategory, Severity
from kernel.state import MonstruoState

logger = structlog.get_logger("kernel.tool_dispatch")

# ── Max tool loop iterations ──────────────────────────────────────────
MAX_TOOL_LOOPS = 3


# ── Tool Spec Definitions (for LLM function calling) ─────────────────

def get_tool_specs():
    """
    Return ToolSpec objects for all available tools.
    These are sent to the LLM so it can decide when to use them.
    """
    from router.llm_client import ToolSpec

    return [
        ToolSpec(
            name="web_search",
            description=(
                "Search the web for current information, news, prices, facts, "
                "or anything that requires up-to-date data. Returns an answer "
                "with citations from web sources."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web",
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional additional context for the search",
                    },
                },
                "required": ["query"],
            },
            risk="low",
        ),
        ToolSpec(
            name="consult_sabios",
            description=(
                "Consult the Council of 6 AI Sabios (GPT-5.4, Claude, Gemini, "
                "Grok, DeepSeek, Perplexity) for multi-perspective expert analysis. "
                "Use for complex questions that benefit from diverse AI viewpoints."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The question or topic for the sabios to analyze",
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional background context for the consultation",
                    },
                },
                "required": ["prompt"],
            },
            risk="low",
        ),
        ToolSpec(
            name="email",
            description=(
                "Send an email to a specified recipient. Only use when the user "
                "explicitly asks to send an email."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body text (plain text)",
                    },
                },
                "required": ["to", "subject", "body"],
            },
            risk="medium",
        ),
    ]


# ── Tool Execution ─────────────────────────────────────────────────────

async def _execute_tool(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool by name and return the result."""
    try:
        if tool_name == "web_search":
            from tools.web_search import web_search
            return await web_search(
                query=args.get("query", ""),
                context=args.get("context", ""),
            )
        elif tool_name == "consult_sabios":
            from tools.consult_sabios import consult_sabios
            return await consult_sabios(
                prompt=args.get("prompt", ""),
                context=args.get("context", ""),
                sabios=args.get("sabios"),
                parallel=args.get("parallel", True),
            )
        elif tool_name == "email":
            from tools.email_sender import send_email
            return await send_email(
                to=args.get("to", ""),
                subject=args.get("subject", ""),
                body=args.get("body", ""),
                html_body=args.get("html_body"),
                cc=args.get("cc"),
            )
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        logger.error("tool_execution_failed", tool=tool_name, error=str(e))
        return {"error": str(e), "tool": tool_name}


# ── Conditional Edge: should we loop back to execute? ──────────────────

def should_loop_tools(state: MonstruoState) -> str:
    """
    Conditional edge after execute:
      - If there are pending_tool_calls AND we haven't exceeded MAX_TOOL_LOOPS → "tool_dispatch"
      - Otherwise → check HITL via hitl_gate
    """
    pending = state.get("pending_tool_calls", [])
    loop_count = state.get("tool_loop_count", 0)

    if pending and loop_count < MAX_TOOL_LOOPS:
        logger.info(
            "tool_loop_continue",
            pending_tools=len(pending),
            loop_count=loop_count,
        )
        return "tool_dispatch"

    if loop_count >= MAX_TOOL_LOOPS and pending:
        logger.warning(
            "tool_loop_max_reached",
            loop_count=loop_count,
            pending_tools=len(pending),
        )

    return "check_hitl"


# ── Tool Dispatch Node ─────────────────────────────────────────────────

async def tool_dispatch(state: MonstruoState, config: RunnableConfig) -> dict[str, Any]:
    """
    Execute pending tool calls and store results in state.

    Graph position: execute → should_loop_tools → tool_dispatch → execute
    After execution, the graph loops back to execute which will make a
    follow-up LLM call with the tool results.
    """
    pending = state.get("pending_tool_calls", [])
    run_id = state.get("run_id", "")
    loop_count = state.get("tool_loop_count", 0)

    if not pending:
        logger.debug("tool_dispatch_no_pending", run_id=run_id)
        return {}

    logger.info(
        "tool_dispatch_start",
        run_id=run_id,
        tool_count=len(pending),
        loop_count=loop_count,
    )

    # Execute all pending tool calls
    all_results = []
    all_records = []
    total_latency_ms = 0.0

    for tc in pending:
        tool_name = tc.get("name", "")
        tool_args = tc.get("arguments", {})
        tool_id = tc.get("id", "")

        start_time = time.monotonic()
        result = await _execute_tool(tool_name, tool_args)
        latency_ms = (time.monotonic() - start_time) * 1000
        total_latency_ms += latency_ms

        logger.info(
            "tool_executed",
            run_id=run_id,
            tool=tool_name,
            tool_call_id=tool_id,
            latency_ms=f"{latency_ms:.0f}",
            has_error="error" in result,
        )

        # Store result for the follow-up LLM call
        all_results.append({
            "tool_call_id": tool_id,
            "name": tool_name,
            "result": result,
        })

        # Record for audit trail
        all_records.append({
            "tool": tool_name,
            "tool_call_id": tool_id,
            "args": tool_args,
            "result_preview": str(result)[:500],
            "latency_ms": latency_ms,
            "success": "error" not in result,
        })

    # Build event
    event = EventBuilder() \
        .category(EventCategory.TOOL_CALLED) \
        .actor("kernel.tool_dispatch") \
        .action(f"Executed {len(pending)} tools in {total_latency_ms:.0f}ms") \
        .for_run_str(run_id) \
        .with_payload({
            "tools": [r["tool"] for r in all_records],
            "total_latency_ms": total_latency_ms,
            "all_success": all(r["success"] for r in all_records),
        }) \
        .build()

    existing_tool_calls = state.get("tool_calls", [])
    existing_events = state.get("events", [])

    return {
        "pending_tool_calls": [],  # Clear pending — they've been executed
        "tool_results": all_results,  # Store results for execute node
        "tool_calls": existing_tool_calls + all_records,  # Audit trail
        "tool_loop_count": loop_count + 1,  # Increment loop counter
        "latency_ms": state.get("latency_ms", 0) + total_latency_ms,
        "events": existing_events + [_event_to_dict(event)],
    }


# ── Tool-Aware Prompt Suffix ──────────────────────────────────────────

def get_tool_aware_prompt_suffix() -> str:
    """Generate a system prompt suffix that describes available tools.

    This is injected into the system prompt so the LLM knows what tools
    are available. The actual tool calling happens via native function
    calling (not prompt-based), but this helps the LLM understand
    capabilities for better decision-making.
    """
    specs = get_tool_specs()
    if not specs:
        return ""

    lines = ["\n\n## Herramientas Disponibles"]
    lines.append("Puedes usar las siguientes herramientas cuando sea necesario:")
    for spec in specs:
        risk_label = f" [riesgo: {spec.risk}]" if spec.risk != "low" else ""
        lines.append(f"- **{spec.name}**: {spec.description}{risk_label}")
    lines.append("\nPara usar una herramienta, simplemente responde normalmente — "
                 "el sistema detectará automáticamente cuándo necesitas una herramienta "
                 "y la ejecutará por ti.")
    return "\n".join(lines)


# ── Helpers ────────────────────────────────────────────────────────────

def _event_to_dict(event: Any) -> dict[str, Any]:
    """Convert an event to a serializable dict."""
    if isinstance(event, dict):
        return event
    if hasattr(event, "__dict__"):
        d = {}
        for k, v in event.__dict__.items():
            if hasattr(v, "value"):
                d[k] = v.value
            elif hasattr(v, "isoformat"):
                d[k] = v.isoformat()
            elif isinstance(v, dict):
                d[k] = v
            else:
                d[k] = str(v)
        return d
    return {"raw": str(event)}
