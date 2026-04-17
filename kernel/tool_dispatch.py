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
                "Search the web for real-time information. MUST be called when "
                "the user asks about: current prices, exchange rates, news, weather, "
                "stock prices, sports scores, recent events, or ANY fact that may "
                "have changed after your training cutoff. Returns an answer with "
                "citations from web sources. When in doubt about freshness, call this."
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
                "MUST be called when the user explicitly asks to 'consult the sabios', "
                "'ask the council', or requests multi-model consensus on a complex topic."
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
            name="start_cidp_research",
            description=(
                "Start a deep, multi-iteration CIDP research cycle on a target "
                "technology, platform, or topic. The CIDP (Ciclo de Investigación y "
                "Descubrimiento Perpetuo) runs asynchronously as a microservice — "
                "this tool starts the job and returns a job_id for tracking. "
                "MUST be called when the user asks for deep research, investigation, "
                "technology analysis, or explicitly requests a 'CIDP cycle'. "
                "Use check_cidp_status to monitor progress after starting."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "The software, platform, or topic to investigate (e.g. 'Supabase', 'LangGraph', 'Vector databases')",
                    },
                    "objective": {
                        "type": "string",
                        "description": "The 10x objective — what we want to achieve or discover (e.g. 'Design a 10x faster alternative')",
                    },
                    "max_iterations": {
                        "type": "integer",
                        "description": "Max research iterations (default 5, max 50)",
                    },
                    "budget_usd": {
                        "type": "number",
                        "description": "Max budget in USD for API calls (default $25)",
                    },
                    "research_only": {
                        "type": "boolean",
                        "description": "If true, only research — no build/prototype phase",
                    },
                },
                "required": ["target", "objective"],
            },
            risk="medium",
        ),
        ToolSpec(
            name="check_cidp_status",
            description=(
                "Check the status of a running CIDP research cycle. "
                "Returns current iteration, stage, 10x score, cost, and artifacts. "
                "Call this after start_cidp_research to monitor progress."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "The CIDP job ID returned by start_cidp_research",
                    },
                },
                "required": ["job_id"],
            },
            risk="low",
        ),
        ToolSpec(
            name="cancel_cidp_research",
            description=(
                "Cancel a running CIDP research cycle. Triggers rollback and "
                "releases any rented GPU resources. Use when the user wants to "
                "stop an ongoing research cycle."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "The CIDP job ID to cancel",
                    },
                },
                "required": ["job_id"],
            },
            risk="medium",
        ),
        ToolSpec(
            name="email",
            description=(
                "Send an email to a specified recipient. MUST be called ONLY when "
                "the user explicitly requests to send, write, or draft an email. "
                "Never call this tool unless the user provides a recipient address."
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
        elif tool_name == "start_cidp_research":
            from tools.cidp import start_cidp_research
            return await start_cidp_research(
                target=args.get("target", ""),
                objective=args.get("objective", ""),
                max_iterations=args.get("max_iterations", 5),
                budget_usd=args.get("budget_usd", 25.0),
                research_only=args.get("research_only", False),
            )
        elif tool_name == "check_cidp_status":
            from tools.cidp import check_cidp_status
            return await check_cidp_status(
                job_id=args.get("job_id", ""),
            )
        elif tool_name == "cancel_cidp_research":
            from tools.cidp import cancel_cidp_research
            return await cancel_cidp_research(
                job_id=args.get("job_id", ""),
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
        # Include 'args' so execute_with_tools can reconstruct the
        # assistant tool_calls message (required by OpenAI API)
        all_results.append({
            "tool_call_id": tool_id,
            "name": tool_name,
            "args": tool_args,
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
    """Generate a system prompt suffix with date injection and tool directives.

    Key design decisions (validated against real-time sources 2026-04-16):
    1. Inject current date so model knows its training data is stale
    2. Explicitly tell the model to use function calling (not text)
    3. List clear trigger conditions for each tool
    4. Never tell the model to 'respond normally' — that suppresses tool calls
    """
    from datetime import datetime, timezone

    specs = get_tool_specs()
    if not specs:
        return ""

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"\n\n## Fecha y Hora Actual: {date_str}",
        "Tu conocimiento tiene fecha de corte de entrenamiento. "
        "Para cualquier información que pueda haber cambiado, "
        "DEBES usar las herramientas disponibles en vez de responder de memoria.",
        "",
        "## Herramientas Disponibles (via function calling)",
        "Tienes acceso a las siguientes herramientas. Cuando necesites usarlas, "
        "invócalas directamente via function calling — NO describas lo que harías, "
        "simplemente haz la llamada a la función.",
    ]
    for spec in specs:
        risk_label = f" [riesgo: {spec.risk}]" if spec.risk != "low" else ""
        lines.append(f"- **{spec.name}**: {spec.description}{risk_label}")
    lines.append("")
    lines.append(
        "REGLA CRÍTICA: Si el usuario pregunta por datos actuales (precios, "
        "noticias, tipo de cambio, clima, eventos recientes, resultados deportivos), "
        "SIEMPRE llama a web_search. NO respondas de memoria."
    )
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
