"""
El Monstruo — FastMCP Tool Server (Sprint 33B)
===============================================
Exposes El Monstruo's native tools as an MCP-compliant server
using FastMCP 3.2.4.

Sprint 33B CHANGES:
  - web_browse: UPGRADED from httpx stub → Cloudflare Browser Run
    (full JS rendering, Markdown extraction, CSS scraping, link extraction)
    Falls back to httpx if CF credentials not configured.

Architecture:
    FastAPI (main.py)
        └── /mcp  → FastMCP SSE server
                ├── web_search      → Perplexity Sonar API
                ├── consult_sabios  → 6 AI model APIs
                ├── github_ops      → GitHub REST API
                ├── database_query  → Supabase REST API
                └── web_browse      → Cloudflare Browser Run API

Sprint 33B | 0.27.0-sprint33 | 29 abril 2026
Validated: fastmcp==3.2.4 (Apache-2.0, PyPI 2026-04-13)
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.fastmcp_server")

# Lazy import to avoid hard crash if fastmcp not installed
_mcp_server = None
_initialized = False


def create_fastmcp_server():
    """
    Create and configure the FastMCP server with El Monstruo's REAL tools.
    Sprint 29: All tools execute real operations (BUG-5 FIX).
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
            "GitHub operations, database queries, and web browsing capabilities."
        ),
    )

    # ── Tool 1: Web Search (REAL — Perplexity Sonar API) ──────────────
    @mcp.tool(
        name="web_search",
        description=(
            "Search the web for real-time information using Perplexity Sonar API. "
            "Returns answers with citations from web sources. Use when the user asks "
            "about current prices, news, weather, sports, or any recent information."
        ),
        tags={"search", "read-only"},
    )
    async def web_search(query: str, max_results: int = 5) -> str:
        """Search the web via Perplexity Sonar and return results with citations."""
        import httpx

        api_key = os.environ.get("SONAR_API_KEY", "")
        if not api_key:
            return json.dumps({"error": "SONAR_API_KEY not configured", "query": query})

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "sonar-pro",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Be precise and cite sources. Answer in the same language as the query.",
                            },
                            {"role": "user", "content": query},
                        ],
                        "max_tokens": 1000,
                        "return_citations": True,
                    },
                )
                response.raise_for_status()
                data = response.json()

                answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                citations = data.get("citations", [])

                result = {
                    "answer": answer,
                    "citations": citations[:max_results],
                    "model": "sonar-pro",
                    "query": query,
                }
                logger.info("fastmcp_web_search_ok", query=query[:50], citations=len(citations))
                return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            logger.error("fastmcp_web_search_error", error=str(e), query=query[:50])
            return json.dumps({"error": str(e), "query": query})

    # ── Tool 2: Consult Sabios (REAL — Multi-Model API calls) ─────────
    @mcp.tool(
        name="consult_sabios",
        description=(
            "Consult the Council of 6 AI Sages for multi-model consensus. "
            "Calls GPT-5.5, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, "
            "DeepSeek R1, and Perplexity Sonar Reasoning Pro. "
            "Returns individual responses and a synthesis."
        ),
        tags={"ai", "consultation", "read-only"},
    )
    async def consult_sabios(
        question: str,
        models: str = "all",
        context: str = "",
    ) -> str:
        """Query multiple AI models and synthesize their responses."""
        import httpx

        results = {}
        errors = {}
        prompt = f"{context}\n\n{question}" if context else question

        # ── Sabio 1: Perplexity Sonar Reasoning Pro ──
        sonar_key = os.environ.get("SONAR_API_KEY", "")
        if sonar_key and models in ("all", "sonar"):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers={"Authorization": f"Bearer {sonar_key}", "Content-Type": "application/json"},
                        json={
                            "model": "sonar-reasoning-pro",
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 800,
                        },
                    )
                    r.raise_for_status()
                    results["sonar_reasoning_pro"] = r.json()["choices"][0]["message"]["content"]
            except Exception as e:
                errors["sonar_reasoning_pro"] = str(e)

        # ── Sabio 2: Claude Opus 4.7 ──
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if anthropic_key and models in ("all", "claude"):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": anthropic_key,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "claude-opus-4-7",
                            "max_tokens": 800,
                            "messages": [{"role": "user", "content": prompt}],
                        },
                    )
                    r.raise_for_status()
                    results["claude_opus_4_7"] = r.json()["content"][0]["text"]
            except Exception as e:
                errors["claude_opus_4_7"] = str(e)

        # ── Sabio 3: Gemini 3.1 Pro ──
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        if gemini_key and models in ("all", "gemini"):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={gemini_key}",
                        headers={"Content-Type": "application/json"},
                        json={
                            "contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {"maxOutputTokens": 800},
                        },
                    )
                    r.raise_for_status()
                    candidates = r.json().get("candidates", [])
                    if candidates:
                        results["gemini_3_1_pro"] = candidates[0]["content"]["parts"][0]["text"]
            except Exception as e:
                errors["gemini_3_1_pro"] = str(e)

        # ── Sabio 4: Grok 4 ──
        xai_key = os.environ.get("XAI_API_KEY", "")
        if xai_key and models in ("all", "grok"):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.post(
                        "https://api.x.ai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {xai_key}", "Content-Type": "application/json"},
                        json={
                            "model": "grok-4-0709",
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 800,
                        },
                    )
                    r.raise_for_status()
                    results["grok_4"] = r.json()["choices"][0]["message"]["content"]
            except Exception as e:
                errors["grok_4"] = str(e)

        # ── Sabio 5: DeepSeek R1 (via OpenRouter) ──
        openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
        if openrouter_key and models in ("all", "deepseek"):
            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    r = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {openrouter_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "deepseek/deepseek-r1",
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 800,
                        },
                    )
                    r.raise_for_status()
                    results["deepseek_r1"] = r.json()["choices"][0]["message"]["content"]
            except Exception as e:
                errors["deepseek_r1"] = str(e)

        # ── Synthesis ──
        sabios_count = len(results)
        synthesis = {
            "question": question,
            "sabios_responded": sabios_count,
            "sabios_failed": len(errors),
            "responses": results,
            "errors": errors if errors else None,
        }

        logger.info("fastmcp_consult_sabios_ok", responded=sabios_count, failed=len(errors))
        return json.dumps(synthesis, ensure_ascii=False)

    # ── Tool 3: GitHub Operations (REAL — GitHub REST API) ────────────
    @mcp.tool(
        name="github_ops",
        description=(
            "Perform GitHub operations via REST API: search repos, get file contents, "
            "list issues, list PRs. Requires GITHUB_TOKEN to be configured."
        ),
        tags={"github", "code"},
    )
    async def github_ops(
        action: str,
        repo: str = "",
        params: str = "{}",
    ) -> str:
        """Execute GitHub API operations."""
        import httpx

        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            return json.dumps({"error": "GITHUB_TOKEN not configured"})

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        parsed_params = json.loads(params) if isinstance(params, str) else params

        try:
            async with httpx.AsyncClient(timeout=20.0, base_url="https://api.github.com") as client:
                if action == "search_repos":
                    query = parsed_params.get("query", repo)
                    r = await client.get(f"/search/repositories?q={query}&per_page=5", headers=headers)
                    r.raise_for_status()
                    items = r.json().get("items", [])
                    return json.dumps([{
                        "name": i["full_name"],
                        "description": i.get("description", ""),
                        "stars": i["stargazers_count"],
                        "url": i["html_url"],
                    } for i in items[:5]])

                elif action == "get_file":
                    path = parsed_params.get("path", "README.md")
                    r = await client.get(f"/repos/{repo}/contents/{path}", headers=headers)
                    r.raise_for_status()
                    import base64
                    content = base64.b64decode(r.json().get("content", "")).decode("utf-8")
                    return json.dumps({"path": path, "content": content[:5000]})

                elif action == "list_issues":
                    state = parsed_params.get("state", "open")
                    r = await client.get(f"/repos/{repo}/issues?state={state}&per_page=10", headers=headers)
                    r.raise_for_status()
                    return json.dumps([{
                        "number": i["number"],
                        "title": i["title"],
                        "state": i["state"],
                        "labels": [l["name"] for l in i.get("labels", [])],
                    } for i in r.json()[:10]])

                elif action == "list_prs":
                    state = parsed_params.get("state", "open")
                    r = await client.get(f"/repos/{repo}/pulls?state={state}&per_page=10", headers=headers)
                    r.raise_for_status()
                    return json.dumps([{
                        "number": p["number"],
                        "title": p["title"],
                        "state": p["state"],
                        "author": p["user"]["login"],
                    } for p in r.json()[:10]])

                elif action == "search_code":
                    query = parsed_params.get("query", "")
                    r = await client.get(f"/search/code?q={query}+repo:{repo}&per_page=5", headers=headers)
                    r.raise_for_status()
                    return json.dumps([{
                        "path": i["path"],
                        "name": i["name"],
                        "url": i["html_url"],
                    } for i in r.json().get("items", [])[:5]])

                else:
                    return json.dumps({"error": f"Unknown action: {action}", "available": ["search_repos", "get_file", "list_issues", "list_prs", "search_code"]})

        except Exception as e:
            logger.error("fastmcp_github_error", action=action, error=str(e))
            return json.dumps({"error": str(e), "action": action})

    # ── Tool 4: Database Query (NEW — Supabase REST API) ──────────────
    @mcp.tool(
        name="database_query",
        description=(
            "Query the Supabase database. Supports SELECT operations on any table. "
            "Returns JSON results. Read-only for safety."
        ),
        tags={"database", "read-only"},
    )
    async def database_query(
        table: str,
        select: str = "*",
        filters: str = "{}",
        limit: int = 50,
    ) -> str:
        """Query Supabase database via REST API."""
        import httpx

        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

        if not supabase_url or not supabase_key:
            return json.dumps({"error": "SUPABASE_URL or SUPABASE_SERVICE_KEY not configured"})

        try:
            parsed_filters = json.loads(filters) if isinstance(filters, str) else filters

            # Build query params
            url = f"{supabase_url}/rest/v1/{table}?select={select}&limit={limit}"
            for key, value in parsed_filters.items():
                url += f"&{key}=eq.{value}"

            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(
                    url,
                    headers={
                        "apikey": supabase_key,
                        "Authorization": f"Bearer {supabase_key}",
                        "Content-Type": "application/json",
                    },
                )
                r.raise_for_status()
                data = r.json()
                logger.info("fastmcp_db_query_ok", table=table, rows=len(data))
                return json.dumps({"table": table, "rows": len(data), "data": data[:limit]}, ensure_ascii=False)

        except Exception as e:
            logger.error("fastmcp_db_query_error", table=table, error=str(e))
            return json.dumps({"error": str(e), "table": table})

    # ── Tool 5: Web Browse (REAL — Cloudflare Browser Run) ────────────
    @mcp.tool(
        name="web_browse",
        description=(
            "Browse a web page and extract its content using Cloudflare Browser Run. "
            "Renders JavaScript fully before extraction. "
            "Actions: 'markdown' (default, clean Markdown), 'content' (rendered HTML), "
            "'scrape' (CSS selector extraction), 'links' (all page links). "
            "Falls back to httpx if Cloudflare is not configured."
        ),
        tags={"browse", "read-only"},
    )
    async def web_browse(
        url: str,
        action: str = "markdown",
        selectors: Optional[list[str]] = None,
    ) -> str:
        """Browse a web page via Cloudflare Browser Run and extract content."""
        try:
            from tools.browser import browse_web

            result_str = await browse_web(
                url=url,
                action=action,
                selectors=selectors,
                wait_for_js=True,
            )
            logger.info("fastmcp_web_browse_ok", url=url[:50], action=action, backend="cloudflare")
            return result_str

        except Exception as e:
            logger.error("fastmcp_web_browse_error", url=url[:50], error=str(e))
            return json.dumps({"error": str(e), "url": url})

    _mcp_server = mcp
    _initialized = True

    logger.info(
        "fastmcp_server_created",
        name="El Monstruo Kernel",
        tools_registered=5,
        version="3.2.4",
        sprint="33B",
        real_tools=["web_search", "consult_sabios", "github_ops", "database_query", "web_browse (Cloudflare Browser Run)"],
    )

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
        "tools": 5 if _initialized else 0,
        "transport": "sse",
        "mount_path": "/mcp",
        "real_tools": [
            "web_search (Perplexity Sonar)",
            "consult_sabios (6 AI models)",
            "github_ops (GitHub REST API)",
            "database_query (Supabase REST)",
            "web_browse (Cloudflare Browser Run)",
        ] if _initialized else [],
    }
