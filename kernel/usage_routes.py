"""
El Monstruo — Usage & Registry Routes (Sprint 10)
====================================================
Dashboard endpoints for cost tracking, usage stats, and tool registry.

Endpoints:
    GET  /v1/usage/today        — Today's cost and token summary
    GET  /v1/usage/period?days=N — Last N days breakdown
    GET  /v1/usage/recent?limit=N — Recent request log
    POST /v1/usage/aggregate    — Trigger daily aggregation
    GET  /v1/registry/          — Full tool registry
    GET  /v1/registry/{name}    — Single tool details
    POST /v1/registry/{name}/toggle — Enable/disable a tool
    GET  /v1/registry/stats     — Registry statistics

Sprint 10 — 2026-04-18
Sprint 10b (ADR) — 2026-04-18: Added broker stats and tool metrics endpoints
Sprint 10c — 2026-04-18: Added pricing catalog endpoint
"""

from __future__ import annotations

from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/v1", tags=["usage", "registry"])


# ─── Usage Endpoints ─────────────────────────────────────────

@router.get("/usage/today")
async def usage_today(request: Request):
    """Get today's usage summary."""
    tracker = getattr(request.app.state, "usage_tracker", None)
    if not tracker:
        return JSONResponse({"error": "Usage tracker not initialized"}, status_code=503)

    summary = await tracker.get_today_summary()
    return JSONResponse(summary)


@router.get("/usage/period")
async def usage_period(request: Request, days: int = Query(default=7, ge=1, le=365)):
    """Get usage summary for the last N days."""
    tracker = getattr(request.app.state, "usage_tracker", None)
    if not tracker:
        return JSONResponse({"error": "Usage tracker not initialized"}, status_code=503)

    summary = await tracker.get_period_summary(days=days)
    return JSONResponse(summary)


@router.get("/usage/recent")
async def usage_recent(request: Request, limit: int = Query(default=20, ge=1, le=100)):
    """Get recent usage log entries."""
    tracker = getattr(request.app.state, "usage_tracker", None)
    if not tracker:
        return JSONResponse({"error": "Usage tracker not initialized"}, status_code=503)

    entries = await tracker.get_recent_requests(limit=limit)
    return JSONResponse({"entries": entries, "count": len(entries)})


@router.post("/usage/aggregate")
async def usage_aggregate(request: Request):
    """Trigger daily aggregation of usage_log into usage_daily."""
    tracker = getattr(request.app.state, "usage_tracker", None)
    if not tracker:
        return JSONResponse({"error": "Usage tracker not initialized"}, status_code=503)

    await tracker.aggregate_today()
    return JSONResponse({"status": "aggregated"})


@router.get("/usage/stats")
async def usage_stats(request: Request):
    """Get current tracker in-memory stats."""
    tracker = getattr(request.app.state, "usage_tracker", None)
    if not tracker:
        return JSONResponse({"error": "Usage tracker not initialized"}, status_code=503)

    return JSONResponse(tracker.get_stats())


@router.get("/usage/tools")
async def usage_tools(request: Request, days: int = Query(default=7, ge=1, le=365)):
    """Get tool-level usage metrics for the last N days."""
    tracker = getattr(request.app.state, "usage_tracker", None)
    if not tracker:
        return JSONResponse({"error": "Usage tracker not initialized"}, status_code=503)

    metrics = await tracker.get_tool_metrics(days=days)
    return JSONResponse({"tools": metrics, "period_days": days})


@router.get("/usage/pricing")
async def usage_pricing(request: Request):
    """Get the current pricing catalog for all models."""
    tracker = getattr(request.app.state, "usage_tracker", None)
    if not tracker:
        return JSONResponse({"error": "Usage tracker not initialized"}, status_code=503)

    catalog = await tracker.get_pricing_catalog()
    return JSONResponse({
        "models": catalog,
        "total": len(catalog),
        "source": "supabase" if tracker._pricing_cache else "fallback",
    })


@router.get("/broker/stats")
async def broker_stats(request: Request):
    """Get ToolBroker statistics."""
    from kernel.tool_dispatch import get_tool_broker
    broker = get_tool_broker()
    if not broker:
        return JSONResponse({"error": "ToolBroker not initialized"}, status_code=503)

    return JSONResponse(broker.get_stats())


# ─── Registry Endpoints ──────────────────────────────────────

@router.get("/registry/")
async def registry_list(request: Request):
    """Get full tool registry."""
    registry = getattr(request.app.state, "tool_registry", None)
    if not registry:
        return JSONResponse({"error": "Tool registry not initialized"}, status_code=503)

    tools = registry.list_all()
    # Serialize for JSON (remove non-serializable fields)
    clean = []
    for t in tools:
        clean.append({
            "tool_name": t.get("tool_name"),
            "display_name": t.get("display_name"),
            "category": t.get("category"),
            "description": t.get("description"),
            "risk_level": t.get("risk_level"),
            "requires_hitl": t.get("requires_hitl"),
            "is_active": t.get("is_active"),
            "invocation_count": t.get("invocation_count", 0),
            "last_invoked_at": t.get("last_invoked_at"),
            "metadata": t.get("metadata", {}),
        })

    return JSONResponse({
        "tools": clean,
        "total": len(clean),
        "active": sum(1 for t in clean if t.get("is_active")),
    })


@router.get("/registry/stats")
async def registry_stats(request: Request):
    """Get registry statistics."""
    registry = getattr(request.app.state, "tool_registry", None)
    if not registry:
        return JSONResponse({"error": "Tool registry not initialized"}, status_code=503)

    return JSONResponse(registry.get_stats())


@router.get("/registry/{tool_name}")
async def registry_get_tool(request: Request, tool_name: str):
    """Get details for a specific tool."""
    registry = getattr(request.app.state, "tool_registry", None)
    if not registry:
        return JSONResponse({"error": "Tool registry not initialized"}, status_code=503)

    tool = registry.get_tool(tool_name)
    if not tool:
        return JSONResponse({"error": f"Tool '{tool_name}' not found"}, status_code=404)

    return JSONResponse({
        "tool_name": tool.get("tool_name"),
        "display_name": tool.get("display_name"),
        "category": tool.get("category"),
        "description": tool.get("description"),
        "risk_level": tool.get("risk_level"),
        "requires_hitl": tool.get("requires_hitl"),
        "is_active": tool.get("is_active"),
        "invocation_count": tool.get("invocation_count", 0),
        "last_invoked_at": tool.get("last_invoked_at"),
        "parameters": tool.get("parameters", {}),
        "metadata": tool.get("metadata", {}),
    })


@router.post("/registry/{tool_name}/toggle")
async def registry_toggle_tool(request: Request, tool_name: str):
    """Toggle a tool's active status."""
    registry = getattr(request.app.state, "tool_registry", None)
    if not registry:
        return JSONResponse({"error": "Tool registry not initialized"}, status_code=503)

    tool = registry.get_tool(tool_name)
    if not tool:
        return JSONResponse({"error": f"Tool '{tool_name}' not found"}, status_code=404)

    new_status = not tool.get("is_active", True)
    success = await registry.set_active(tool_name, new_status)

    if success:
        return JSONResponse({
            "tool_name": tool_name,
            "is_active": new_status,
            "message": f"Tool {'enabled' if new_status else 'disabled'}",
        })
    else:
        return JSONResponse({"error": "Failed to toggle tool"}, status_code=500)
