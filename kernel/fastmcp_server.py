"""
El Monstruo — FastMCP Tool Server (Sprint 26)
===============================================
Exposes El Monstruo's native tools as an MCP-compliant server
using FastMCP 3.2.4.

This is an INTERNAL server — it runs as a sub-application mounted
on the FastAPI app at /mcp. External MCP clients (Claude Desktop,
Cursor, etc.) can connect via SSE at /mcp/sse.

Architecture:
    FastAPI (main.py)
        └── /mcp  → FastMCP SSE server
                ├── web_search (read-only, open-world)
                ├── consult_sabios (read-only, open-world)
                └── ... (more tools registered dynamically)

The server auto-discovers tools from kernel/tool_dispatch.py
and wraps them as MCP tools with proper schemas and annotations.

Sprint 26 — 2026-04-24
Validated: fastmcp==3.2.4 (Apache-2.0, PyPI 2026-04-13)
Reference: https://gofastmcp.com/v2/servers/tools
"""

from __future__ import annotations

import os
from typing import Any

import structlog

logger = structlog.get_logger("kernel.fastmcp_server")

# Lazy import to avoid hard crash if fastmcp not installed
_mcp_server = None
_initialized = False


def create_fastmcp_server():
    """
    Create and configure the FastMCP server with El Monstruo's tools.

    Returns the FastMCP instance (or None if fastmcp is not installed).
    """
    global _mcp_server, _initialized

    try:
        from fastmcp import FastMCP
    except ImportError:
        logger.warning("fastmcp_not_installed", hint="pip install fastmcp==3.2.4")
        return None

    mcp = FastMCP(
        name="El Monstruo Kernel",
        instructions=(
            "El Monstruo is a sovereign AI assistant. "
            "These tools provide real-time web search, multi-model AI consultation, "
            "and other capabilities. Use them when the user needs current information "
            "or specialized processing."
        ),
    )

    # ── Tool 1: Web Search ─────────────────────────────────────────────
    @mcp.tool(
        name="web_search",
        description=(
            "Search the web for real-time information. Use when the user asks about "
            "current prices, exchange rates, news, weather, stock prices, sports scores, "
            "recent events, or ANY fact that may have changed recently."
        ),
        tags={"search", "read-only"},
    )
    async def web_search(query: str, max_results: int = 5) -> str:
        """Search the web and return results with citations."""
        try:
            from tools.web_search import execute as ws_execute

            result = await ws_execute({"query": query, "max_results": max_results})
            return result.get("answer", str(result))
        except Exception as e:
            logger.error("fastmcp_web_search_error", error=str(e))
            return f"Error performing web search: {e}"

    # ── Tool 2: Consult Sabios ─────────────────────────────────────────
    @mcp.tool(
        name="consult_sabios",
        description=(
            "Consult the Council of 6 AI Sages (GPT, Claude, Gemini, Grok, DeepSeek, "
            "Perplexity) for multi-model consensus on complex questions. Returns a "
            "synthesized answer with agreement/disagreement analysis."
        ),
        tags={"ai", "consultation", "read-only"},
    )
    async def consult_sabios(
        question: str,
        models: str = "all",
        context: str = "",
    ) -> str:
        """Query multiple AI models and synthesize their responses."""
        try:
            from tools.consult_sabios import execute as cs_execute

            result = await cs_execute(
                {
                    "question": question,
                    "models": models,
                    "context": context,
                }
            )
            return result.get("synthesis", str(result))
        except Exception as e:
            logger.error("fastmcp_consult_sabios_error", error=str(e))
            return f"Error consulting sabios: {e}"

    # ── Tool 3: GitHub Operations ──────────────────────────────────────
    @mcp.tool(
        name="github_ops",
        description=(
            "Perform GitHub operations: list repos, create issues, read files, "
            "search code. Requires GITHUB_TOKEN to be configured."
        ),
        tags={"github", "code"},
    )
    async def github_ops(
        action: str,
        repo: str = "",
        params: str = "{}",
    ) -> str:
        """Execute GitHub API operations."""
        try:
            import json

            from tools.github import execute as gh_execute

            parsed_params = json.loads(params) if isinstance(params, str) else params
            result = await gh_execute(
                {
                    "action": action,
                    "repo": repo,
                    **parsed_params,
                }
            )
            return str(result)
        except Exception as e:
            logger.error("fastmcp_github_error", error=str(e))
            return f"Error in GitHub operation: {e}"

    _mcp_server = mcp
    _initialized = True

    logger.info(
        "fastmcp_server_created",
        name="El Monstruo Kernel",
        tools_registered=3,
        version="3.2.4",
    )

    # ── Sprint 28: MCP Database Query Tool ──────────────────
    @mcp.tool(
        annotations={"title": "Database Query", "readOnlyHint": True},
    )
    async def database_query(
        query: str,
        table_hint: str = "",
    ) -> str:
        """Query the Monstruo Supabase database."""
        import json as _json

        import httpx

        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not supabase_url or not supabase_key:
            return "Error: Supabase credentials not configured"
        table_map = {
            "events": "event_store",
            "memories": "mem0_memories",
            "knowledge": "knowledge_entities",
            "conversations": "conversation_episodes",
            "tools": "tool_usage_log",
            "costs": "finops_log",
        }
        table = table_map.get(table_hint, table_hint) if table_hint else "event_store"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{supabase_url}/rest/v1/{table}?select=*&limit=10&order=created_at.desc",
                    headers={
                        "apikey": supabase_key,
                        "Authorization": f"Bearer {supabase_key}",
                    },
                )
                if resp.status_code == 200:
                    rows = resp.json()
                    if rows:
                        data = _json.dumps(
                            rows[:5],
                            indent=2,
                            default=str,
                        )
                        return f"## {table} ({len(rows)} rows)\n```json\n{data}\n```"
                    return f"No data found in {table}"
                return f"Error: HTTP {resp.status_code}"
        except Exception as e:
            return f"Database error: {e}"

    return mcp


def get_server():
    """Get the FastMCP server instance (creates it if needed)."""
    global _mcp_server
    if _mcp_server is None:
        create_fastmcp_server()
    return _mcp_server


def get_status() -> dict[str, Any]:
    """Return FastMCP server status for /health endpoint."""
    return {
        "active": _initialized and _mcp_server is not None,
        "version": "3.2.4" if _initialized else None,
        "tools": 3 if _initialized else 0,
        "transport": "sse",
        "mount_path": "/mcp",
    }
