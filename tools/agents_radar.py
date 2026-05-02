"""
El Monstruo — Agents Radar Tool
================================
Gives El Monstruo real-time access to the daily AI ecosystem digest
from agents-radar (https://github.com/duanyytop/agents-radar).

The radar aggregates 10 sources every day at 08:00 CST:
    - GitHub Trending (AI repos, 7-day window)
    - ArXiv (cs.AI, cs.CL, cs.LG — last 48h)
    - Hacker News (top 30 AI stories, last 24h)
    - Hugging Face (30 trending models by weekly likes)
    - Product Hunt (top AI products by votes)
    - Dev.to (top AI/LLM articles)
    - Lobste.rs (AI/ML tagged stories, last 7 days)
    - Anthropic + OpenAI (new articles via sitemap diff)
    - Claude Code Skills (trending skills by community engagement)
    - GitHub Repos (issues, PRs, releases from 17+ tracked AI repos)

Available report types:
    - ai-trending-en  : GitHub AI trending repos
    - ai-agents-en    : OpenClaw + agent ecosystem digest
    - ai-cli-en       : CLI tools and coding agents
    - ai-web-en       : Web AI tools and frameworks
    - ai-hn-en        : Hacker News AI stories

MCP Server: https://agents-radar-mcp.duanyytop.workers.dev

Sprint 45 — 2026-04-30
"""

from __future__ import annotations

import httpx
import structlog

logger = structlog.get_logger("tools.agents_radar")

MCP_URL = "https://agents-radar-mcp.duanyytop.workers.dev"

REPORT_TYPES = {
    "trending": "ai-trending-en",
    "agents": "ai-agents-en",
    "cli": "ai-cli-en",
    "web": "ai-web-en",
    "hn": "ai-hn-en",
    "weekly": "ai-weekly-en",
    "monthly": "ai-monthly-en",
}


async def _call_mcp(method: str, params: dict, timeout: int = 30) -> dict:
    """Llama al MCP server de agents-radar via JSON-RPC 2.0."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(MCP_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"MCP error: {data['error']}")
        return data.get("result", {})


async def get_latest_report(report_type: str = "trending") -> str:
    """
    Obtiene el reporte más reciente del tipo especificado.

    Args:
        report_type: Tipo de reporte. Opciones: trending, agents, cli, web, hn, weekly, monthly

    Returns:
        Contenido del reporte en Markdown.
    """
    mcp_type = REPORT_TYPES.get(report_type, f"ai-{report_type}-en")
    try:
        result = await _call_mcp(
            "tools/call",
            {"name": "get_latest", "arguments": {"type": mcp_type}},
        )
        content = result.get("content", [{}])[0].get("text", "")
        logger.info("agents_radar.get_latest", report_type=report_type, chars=len(content))
        return content
    except Exception as e:
        logger.error("agents_radar.get_latest.error", error=str(e))
        return f"Error al obtener reporte {report_type}: {e}"


async def search_radar(query: str, days: int = 7) -> str:
    """
    Busca una palabra clave o frase en los reportes recientes del radar.

    Args:
        query: Término de búsqueda (ej: "browser-use", "memory", "coding agent")
        days: Número de días hacia atrás para buscar (máx 14)

    Returns:
        Resultados de la búsqueda en Markdown.
    """
    try:
        result = await _call_mcp(
            "tools/call",
            {"name": "search", "arguments": {"query": query, "days": min(days, 14)}},
        )
        content = result.get("content", [{}])[0].get("text", "")
        logger.info("agents_radar.search", query=query, days=days, chars=len(content))
        return content
    except Exception as e:
        logger.error("agents_radar.search.error", error=str(e))
        return f"Error al buscar '{query}': {e}"


async def get_report_by_date(date: str, report_type: str = "trending") -> str:
    """
    Obtiene el reporte de una fecha específica.

    Args:
        date: Fecha en formato YYYY-MM-DD (ej: "2026-04-30")
        report_type: Tipo de reporte (trending, agents, cli, web, hn)

    Returns:
        Contenido del reporte en Markdown.
    """
    mcp_type = REPORT_TYPES.get(report_type, f"ai-{report_type}-en")
    try:
        result = await _call_mcp(
            "tools/call",
            {"name": "get_report", "arguments": {"date": date, "type": mcp_type}},
        )
        content = result.get("content", [{}])[0].get("text", "")
        logger.info("agents_radar.get_by_date", date=date, report_type=report_type, chars=len(content))
        return content
    except Exception as e:
        logger.error("agents_radar.get_by_date.error", error=str(e))
        return f"Error al obtener reporte de {date}: {e}"


async def get_daily_digest() -> dict[str, str]:
    """
    Obtiene el digest completo del día: trending + agents + HN.
    Ideal para el ciclo autónomo del Embrión.

    Returns:
        Dict con claves 'trending', 'agents', 'hn' y sus contenidos.
    """
    import asyncio

    trending, agents, hn = await asyncio.gather(
        get_latest_report("trending"),
        get_latest_report("agents"),
        get_latest_report("hn"),
        return_exceptions=True,
    )
    return {
        "trending": trending if isinstance(trending, str) else f"Error: {trending}",
        "agents": agents if isinstance(agents, str) else f"Error: {agents}",
        "hn": hn if isinstance(hn, str) else f"Error: {hn}",
    }


# ── Sync wrappers para uso desde código no-async ──────────────────────────────


def get_latest_report_sync(report_type: str = "trending") -> str:
    import asyncio

    return asyncio.run(get_latest_report(report_type))


def search_radar_sync(query: str, days: int = 7) -> str:
    import asyncio

    return asyncio.run(search_radar(query, days))


def get_daily_digest_sync() -> dict[str, str]:
    import asyncio

    return asyncio.run(get_daily_digest())
