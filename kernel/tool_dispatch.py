"""
El Monstruo — Tool Dispatch Node (Sprint 19)
=============================================
Executes tool calls that the LLM requested via native function calling.
Includes MCP tool routing + Multi-Agent Dispatcher integration.

Strategy (validated by Consejo de 6 Sabios, 2026-04-16):
  - LLMClient sends tool definitions to the LLM via native function calling
  - If the LLM responds with tool_calls, execute node stores them in state
  - tool_dispatch executes the tools and stores results in state
  - Graph loops back to execute, which makes a follow-up LLM call with results
  - Max 3 loops to prevent runaway tool chains

Sprint 17 additions:
  - MCP tools are routed via MCPClientManager (kernel/mcp_client.py)
  - MCP tools are prefixed with "mcp__" (e.g., mcp__filesystem__read_file)
  - Native tools remain unchanged — MCP is additive, not a replacement

Sprint 18 additions:
  - Preset MCP server configs: github, filesystem, supabase (IVD-validated)
  - /v1/mcp/status endpoint for monitoring
  - build_mcp_configs() merges presets + env custom configs

Sprint 19 additions:
  - Multi-Agent Dispatcher (kernel/multi_agent.py) classifies tasks
  - Dispatch result enriches execute node with specialized system_prompt + tools
  - MemPalace recall enriches context in intake node

Graph topology:
    execute → should_loop_tools? → tool_dispatch → execute  (if tool_calls)
    execute → should_loop_tools? → hitl_gate → respond      (if no tool_calls)

Anti-autoboicot: validated 2026-04-20 against LangGraph 1.1.8, langchain-core 1.3.0,
langchain-openai 1.1.15, langchain-anthropic 1.4.1, langchain-google-genai 4.2.2,
mcp 1.27.0, honcho-ai 2.1.1, deepeval 3.9.7.

Principio: Las Manos son soberanas. El dispatch es nuestro. MCP es un protocolo, no un framework.
"""

from __future__ import annotations

import time
from typing import Any

import structlog
from langchain_core.runnables import RunnableConfig

from contracts.event_envelope import EventBuilder, EventCategory
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
                        "description": "The software, platform, or topic to investigate (e.g. 'Supabase', 'LangGraph', 'Vector databases')",  # noqa: E501
                    },
                    "objective": {
                        "type": "string",
                        "description": "The 10x objective — what we want to achieve or discover (e.g. 'Design a 10x faster alternative')",  # noqa: E501
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
            name="call_webhook",
            description=(
                "Call an external webhook endpoint to trigger actions in third-party "
                "services like Zapier, Make.com, n8n, or Slack. Use when the user asks "
                "to trigger an automation, send a notification to Slack, or execute "
                "an external workflow. Only HTTPS URLs on whitelisted domains are allowed. "
                "This tool ALWAYS requires human approval before execution."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The webhook URL (HTTPS only, must be on a whitelisted domain)",
                    },
                    "payload": {
                        "type": "object",
                        "description": "JSON payload to send to the webhook",
                    },
                    "method": {
                        "type": "string",
                        "description": "HTTP method: POST (default), PUT, or PATCH",
                    },
                },
                "required": ["url", "payload"],
            },
            risk="high",
        ),
        ToolSpec(
            name="github",
            description=(
                "Interact with GitHub repositories. Available actions: "
                "search_repos, search_code, get_file, list_issues, list_prs, "
                "create_issue, update_issue, create_or_update_file. "
                "Use when the user asks about code, repos, issues, PRs, or "
                "wants to create/update files in a GitHub repository. "
                "Write operations (create_issue, update_issue, create_or_update_file) "
                "require human approval."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "The GitHub action to perform: search_repos, search_code, get_file, list_issues, list_prs, create_issue, update_issue, create_or_update_file",  # noqa: E501
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters for the action. Common: repo (owner/name), query, path, title, body, labels, state, limit",  # noqa: E501
                    },
                },
                "required": ["action", "params"],
            },
            risk="high",
        ),
        ToolSpec(
            name="notion",
            description=(
                "Interact with the Notion workspace. Available actions: "
                "search, get_page, get_page_content, query_database, "
                "create_page, update_page, append_content. "
                "Use when the user asks about Notion pages, databases, notes, "
                "documents, or wants to search, read, create, or update content "
                "in Notion. Read operations are safe; write operations "
                "(create_page, update_page, append_content) require human approval."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "The Notion action to perform: search, get_page, get_page_content, query_database, create_page, update_page, append_content",  # noqa: E501
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters for the action. Common: query, page_id, database_id, filter_type (page/database), properties, content_blocks, filter_obj, sorts, limit",  # noqa: E501
                    },
                },
                "required": ["action", "params"],
            },
            risk="medium",
        ),
        ToolSpec(
            name="delegate_task",
            description=(
                "Delegate a cognitive sub-task to a specialized AI role. "
                "Available roles: estratega, investigador, razonador, critico, "
                "creativo, arquitecto, codigo, sintetizador, verificador. "
                "Use when you need a different perspective, specialized analysis, "
                "or want to break a complex task into sub-tasks handled by experts. "
                "Supports single role or parallel mode (multiple roles + synthesis). "
                "Delegates have NO access to tools — they use only their knowledge "
                "and the context you provide. This tool is auto-approved (no HITL)."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Clear description of the sub-task for the delegate",
                    },
                    "role": {
                        "type": "string",
                        "description": "The specialist role: estratega, investigador, razonador, critico, creativo, arquitecto, codigo, sintetizador, verificador",  # noqa: E501
                    },
                    "mode": {
                        "type": "string",
                        "description": "'single' (one role) or 'parallel' (multiple roles with synthesis). Default: single",  # noqa: E501
                    },
                    "relevant_context": {
                        "type": "string",
                        "description": "Curated context for the delegate (NOT full conversation — only what's relevant)",  # noqa: E501
                    },
                    "constraints": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of constraints for the delegate (e.g., 'Responde en español', 'Máximo 5 bullets')",  # noqa: E501
                    },
                    "parallel_roles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Roles to use in parallel mode (overrides 'role' param)",
                    },
                },
                "required": ["task", "role"],
            },
            risk="low",
        ),
        ToolSpec(
            name="schedule_task",
            description=(
                "Schedule a task for future autonomous execution. The Monstruo will "
                "execute the task at the specified time WITHOUT user presence. "
                "MUST be called when the user says: 'remind me', 'tomorrow at X', "
                "'in 3 hours do Y', 'schedule', 'program', 'recuérdame', 'mañana a las', "
                "'en X horas', or any request involving a future time. "
                "Supports: ISO 8601, 'tomorrow 8am', 'in 3 hours'. "
                "Max scheduling window: 30 days. One-shot by default."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short title for the scheduled task (e.g., 'Send update to Juan')",
                    },
                    "instruction": {
                        "type": "string",
                        "description": "Full instruction for the Monstruo to execute at the scheduled time. Be specific and complete.",  # noqa: E501
                    },
                    "run_at": {
                        "type": "string",
                        "description": "When to execute. Formats: ISO 8601 ('2026-04-19T08:00'), relative ('in 3 hours'), natural ('tomorrow 8am')",  # noqa: E501
                    },
                    "timezone": {
                        "type": "string",
                        "description": "User's timezone. Default: America/Mexico_City. Also accepts: 'cdmx', 'utc', 'est', 'pst'",  # noqa: E501
                    },
                    "channel": {
                        "type": "string",
                        "description": "Notification channel for results. Default: 'telegram'. Options: telegram, api, webhook",  # noqa: E501
                    },
                    "recurrence": {
                        "type": "string",
                        "description": "Optional: 'daily' for daily repeat, null/omit for one-shot execution",
                    },
                },
                "required": ["title", "instruction", "run_at"],
            },
            risk="low",
        ),
        ToolSpec(
            name="user_dossier",
            description=(
                "Read or update the user's persistent profile (dossier) and manage active missions. "
                "Actions: get_dossier (read full profile), update_dossier (update fields), "
                "list_missions (list active projects), update_mission (change status/priority), "
                "create_mission (add new project). Use this when the user mentions their profile, "
                "preferences, projects, missions, or when you need to remember something about the user."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform: get_dossier, update_dossier, list_missions, update_mission, create_mission",  # noqa: E501
                        "enum": [
                            "get_dossier",
                            "update_dossier",
                            "list_missions",
                            "update_mission",
                            "create_mission",
                        ],
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID. Default: 'alfredo'",
                    },
                    "status": {
                        "type": "string",
                        "description": "For list_missions: filter by status (active, paused, completed, all). Default: active",  # noqa: E501
                    },
                    "mission_name": {
                        "type": "string",
                        "description": "For update_mission: name of the mission to update",
                    },
                    "name": {
                        "type": "string",
                        "description": "For create_mission: name of the new mission",
                    },
                    "description": {
                        "type": "string",
                        "description": "For create_mission/update_mission: description text",
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Priority 1-10 (10=highest). For create_mission or update_mission.",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for the mission",
                    },
                    "full_name": {
                        "type": "string",
                        "description": "For update_dossier",
                    },
                    "company": {"type": "string", "description": "For update_dossier"},
                    "location": {"type": "string", "description": "For update_dossier"},
                    "role": {"type": "string", "description": "For update_dossier"},
                    "email": {"type": "string", "description": "For update_dossier"},
                    "github_username": {
                        "type": "string",
                        "description": "For update_dossier",
                    },
                },
                "required": ["action"],
            },
            risk="low",
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

# Module-level DB reference (set by main.py during startup)
_tool_db = None
_tool_broker = None
_tool_mcp_manager = None  # Sprint 17: MCPClientManager instance


def set_tool_db(db: Any) -> None:
    """Inject the SupabaseClient for tools that need persistence."""
    global _tool_db
    _tool_db = db


def set_tool_broker(broker) -> None:
    """Inject the ToolBroker instance (set by main.py during startup)."""
    global _tool_broker
    _tool_broker = broker

def set_mcp_manager(manager) -> None:
    """Inject the MCPClientManager instance (set by main.py during startup, Sprint 17)."""
    global _tool_mcp_manager
    _tool_mcp_manager = manager

def get_mcp_manager():
    """Get the current MCPClientManager instance."""
    return _tool_mcp_manager

def get_tool_broker():
    """Get the current ToolBroker instance."""
    return _tool_broker


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
        elif tool_name == "call_webhook":
            from tools.webhook import call_webhook

            return await call_webhook(
                url=args.get("url", ""),
                payload=args.get("payload", {}),
                method=args.get("method", "POST"),
                headers=args.get("headers"),
            )
        elif tool_name == "github":
            from tools.github import execute_github

            result_str = await execute_github(
                action=args.get("action", ""),
                params=args.get("params", {}),
            )
            import json as _json

            return _json.loads(result_str)
        elif tool_name == "notion":
            from tools.notion import execute_notion

            result_str = await execute_notion(
                action=args.get("action", ""),
                params=args.get("params", {}),
            )
            import json as _json

            return _json.loads(result_str)
        elif tool_name == "delegate_task":
            from tools.delegate import delegate_task

            return await delegate_task(
                task=args.get("task", ""),
                role=args.get("role", "estratega"),
                mode=args.get("mode", "single"),
                relevant_context=args.get("relevant_context", ""),
                constraints=args.get("constraints"),
                parallel_roles=args.get("parallel_roles"),
                model_hint=args.get("model_hint"),
                timeout_s=args.get("timeout_s"),
            )
        elif tool_name == "schedule_task":
            from tools.schedule_task import execute_schedule_task

            return await execute_schedule_task(
                params=args,
                context={
                    "user_id": state.get("user_id", "alfredo"),  # Sprint 27.5: extract from state with fallback
                    "thread_id": "",
                    "db": _tool_db,  # Injected by main.py via set_tool_db()
                    "source": "user",
                },
            )
        elif tool_name == "user_dossier":
            from tools.user_dossier import execute

            action = args.pop("action", "get_dossier")
            result_str = await execute(action=action, args=args, db=_tool_db)
            import json as _json

            return _json.loads(result_str)
        elif tool_name == "email":
            from tools.email_sender import send_email

            return await send_email(
                to=args.get("to", ""),
                subject=args.get("subject", ""),
                body=args.get("body", ""),
                html_body=args.get("html_body"),
                cc=args.get("cc"),
            )
        elif tool_name.startswith("mcp__"):
            # Route to MCP Client Manager (Sprint 17)
            mcp_mgr = _tool_mcp_manager
            if not mcp_mgr:
                return {"error": "MCP manager not initialized", "tool": tool_name}
            return await mcp_mgr.execute_tool(tool_name, args)
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

    # Get broker for request-scoped execution (ADR pattern)
    broker = _tool_broker
    thread_id = state.get("thread_id", "")

    for tc in pending:
        tool_name = tc.get("name", "")
        tool_args = tc.get("arguments", {})
        tool_id = tc.get("id", "")

        start_time = time.monotonic()

        # Route through ToolBroker if available (ADR pattern)
        if broker:
            result = await broker.execute(
                tool_name=tool_name,
                args=tool_args,
                run_id=run_id,
                thread_id=thread_id,
                tenant_id="alfredo",
                executor_fn=_execute_tool,
            )
            # Remove broker metadata before passing to LLM
            result.pop("_untrusted", None)
            result.pop("_broker_exec_id", None)
        else:
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
            brokered=broker is not None,
        )

        # Store result for the follow-up LLM call
        # Include 'args' so execute_with_tools can reconstruct the
        # assistant tool_calls message (required by OpenAI API)
        all_results.append(
            {
                "tool_call_id": tool_id,
                "name": tool_name,
                "args": tool_args,
                "result": result,
            }
        )

        # Record for audit trail
        all_records.append(
            {
                "tool": tool_name,
                "tool_call_id": tool_id,
                "args": tool_args,
                "result_preview": str(result)[:500],
                "latency_ms": latency_ms,
                "success": "error" not in result,
            }
        )

    # Build event
    event = (
        EventBuilder()
        .category(EventCategory.TOOL_CALLED)
        .actor("kernel.tool_dispatch")
        .action(f"Executed {len(pending)} tools in {total_latency_ms:.0f}ms")
        .for_run_str(run_id)
        .with_payload(
            {
                "tools": [r["tool"] for r in all_records],
                "total_latency_ms": total_latency_ms,
                "all_success": all(r["success"] for r in all_records),
            }
        )
        .build()
    )

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

    # ── Tool Trigger Conditions (Sprint 7: prompt engineering) ──
    lines.append("")
    lines.append("## Cuándo Usar Cada Herramienta")
    lines.append("")
    lines.append(
        "**web_search**: Datos actuales (precios, noticias, tipo de cambio, clima, "
        "eventos recientes, resultados deportivos, cualquier dato post-2025). "
        "SIEMPRE usa web_search para información que pueda haber cambiado."
    )
    lines.append(
        "**github**: Cuando el usuario mencione repositorios, código, commits, issues, "
        "PRs, o cualquier operación de GitHub. Acciones: list_repos, get_repo, "
        "list_issues, create_issue, list_commits, get_file, search_code."
    )
    lines.append(
        "**notion**: Cuando el usuario mencione notas, documentos, bases de datos, "
        "páginas, wiki, o cualquier contenido de Notion. Acciones: search, get_page, "
        "get_page_content, query_database, create_page, update_page, append_content."
    )
    lines.append(
        "**delegate_task**: Cuando necesites una perspectiva especializada, análisis "
        "profundo, o quieras dividir una tarea compleja en sub-tareas. Roles disponibles: "
        "estratega, investigador, razonador, critico, creativo, arquitecto, codigo, "
        "sintetizador, verificador. Usa mode='parallel' para consultar múltiples roles."
    )
    lines.append(
        "**user_dossier**: Cuando el usuario mencione su perfil, preferencias, "
        "proyectos activos, misiones, o cuando necesites recordar/actualizar algo sobre "
        "el usuario. También úsalo para crear nuevas misiones o cambiar prioridades."
    )
    lines.append(
        "**schedule_task**: Cuando el usuario pida hacer algo EN EL FUTURO: "
        "'recuérdame mañana', 'en 3 horas haz X', 'programa para las 8am', "
        "'tomorrow at 9am send Y'. Siempre usa schedule_task para tareas futuras. "
        "NO digas 'no puedo programar' — SÍ puedes, usa esta herramienta."
    )
    lines.append(
        "**consult_sabios**: Cuando necesites consenso de múltiples IAs sobre un tema "
        "complejo. Diferente de delegate_task: sabios consulta modelos externos, "
        "delegate_task usa roles internos del Monstruo."
    )
    lines.append("")
    lines.append(
        "REGLA CRÍTICA: Cuando el usuario pida información actual, SIEMPRE usa "
        "web_search. Cuando pida operaciones sobre GitHub o Notion, SIEMPRE usa "
        "la herramienta correspondiente. NO describas lo que harías — haz la llamada."
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
