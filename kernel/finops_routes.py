"""
El Monstruo — FinOps Dashboard Routes (Sprint 38)
==================================================
Endpoints de observabilidad financiera con datos reales de Supabase.

Endpoints:
    GET /v1/finops/summary   — Dashboard completo: gasto hoy/semana/mes, por modelo, top jobs
    GET /v1/finops/status    — Estado del controller (ya existía en main.py)
    GET /v1/finops/history   — Historial de runs con costo (últimas N entradas)

Sprint 38 — 2026-04-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import structlog
from fastapi import APIRouter, Request

logger = structlog.get_logger("kernel.finops_routes")

router = APIRouter(prefix="/v1/finops", tags=["finops"])

# ── Dependencies (inyectadas desde main.py) ───────────────────────────
_db = None
_finops = None


def set_finops_deps(db: Any, finops: Any) -> None:
    """Inject DB and FinOps controller (called from main.py lifespan)."""
    global _db, _finops
    _db = db
    _finops = finops


# ── Helpers ───────────────────────────────────────────────────────────


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _start_of_day(dt: datetime) -> str:
    return dt.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


def _start_of_week(dt: datetime) -> str:
    monday = dt - timedelta(days=dt.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()


def _start_of_month(dt: datetime) -> str:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()


async def _query_run_costs(since_iso: str, limit: int = 1000) -> list[dict]:
    """Query run_costs table filtered by created_at >= since_iso."""
    if not _db or not _db.connected:
        return []
    try:
        rows = await _db.select(
            "run_costs",
            columns="run_id,model_used,total_cost_usd,tokens_in,tokens_out,latency_ms,tool_count,status,created_at",
            limit=limit,
        )
        # Filter client-side (Supabase select doesn't support WHERE in this client)
        return [r for r in (rows or []) if str(r.get("created_at", "")) >= since_iso]
    except Exception as e:
        logger.error("finops_query_failed", error=str(e))
        return []


async def _query_job_executions(since_iso: str, limit: int = 500) -> list[dict]:
    """Query job_executions table filtered by started_at >= since_iso."""
    if not _db or not _db.connected:
        return []
    try:
        rows = await _db.select(
            "job_executions",
            columns="id,job_id,status,cost_usd,duration_ms,started_at",
            limit=limit,
        )
        return [r for r in (rows or []) if str(r.get("started_at", "")) >= since_iso]
    except Exception as e:
        logger.error("finops_job_query_failed", error=str(e))
        return []


def _aggregate_by_model(rows: list[dict]) -> list[dict]:
    """Aggregate run_costs by model_used."""
    agg: dict[str, dict] = {}
    for r in rows:
        model = r.get("model_used", "unknown")
        if model not in agg:
            agg[model] = {"model": model, "runs": 0, "cost_usd": 0.0, "tokens_in": 0, "tokens_out": 0}
        agg[model]["runs"] += 1
        agg[model]["cost_usd"] += float(r.get("total_cost_usd", 0))
        agg[model]["tokens_in"] += int(r.get("tokens_in", 0))
        agg[model]["tokens_out"] += int(r.get("tokens_out", 0))

    result = list(agg.values())
    for item in result:
        item["cost_usd"] = round(item["cost_usd"], 6)
    return sorted(result, key=lambda x: x["cost_usd"], reverse=True)


def _top_expensive_runs(rows: list[dict], n: int = 5) -> list[dict]:
    """Return top N most expensive runs."""
    sorted_rows = sorted(rows, key=lambda r: float(r.get("total_cost_usd", 0)), reverse=True)
    return [
        {
            "run_id": r.get("run_id", ""),
            "model": r.get("model_used", ""),
            "cost_usd": round(float(r.get("total_cost_usd", 0)), 6),
            "tokens_in": r.get("tokens_in", 0),
            "tokens_out": r.get("tokens_out", 0),
            "latency_ms": r.get("latency_ms", 0),
            "tool_count": r.get("tool_count", 0),
            "status": r.get("status", ""),
            "created_at": r.get("created_at", ""),
        }
        for r in sorted_rows[:n]
    ]


# ── Endpoints ─────────────────────────────────────────────────────────


@router.get("/summary")
async def finops_summary(request: Request):
    """
    FinOps dashboard completo.

    Retorna:
    - Gasto hoy, esta semana, este mes (run_costs + job_executions)
    - Breakdown por modelo
    - Top 5 runs más caros del día
    - Burn rate y proyección diaria
    - Estado del presupuesto
    """
    now = _utc_now()
    today_start = _start_of_day(now)
    week_start = _start_of_week(now)
    month_start = _start_of_month(now)

    # Obtener datos de run_costs (chat runs)
    runs_today = await _query_run_costs(today_start, limit=500)
    runs_week = await _query_run_costs(week_start, limit=2000)
    runs_month = await _query_run_costs(month_start, limit=5000)

    # Obtener datos de job_executions (autonomous runner)
    jobs_today = await _query_job_executions(today_start, limit=200)
    jobs_week = await _query_job_executions(week_start, limit=500)
    jobs_month = await _query_job_executions(month_start, limit=1000)

    # Calcular totales
    def sum_cost(rows: list[dict], key: str = "total_cost_usd") -> float:
        return round(sum(float(r.get(key, 0)) for r in rows), 6)

    def sum_job_cost(rows: list[dict]) -> float:
        return round(sum(float(r.get("cost_usd", 0) or 0) for r in rows), 6)

    chat_today = sum_cost(runs_today)
    chat_week = sum_cost(runs_week)
    chat_month = sum_cost(runs_month)

    jobs_cost_today = sum_job_cost(jobs_today)
    jobs_cost_week = sum_job_cost(jobs_week)
    jobs_cost_month = sum_job_cost(jobs_month)

    total_today = round(chat_today + jobs_cost_today, 6)
    total_week = round(chat_week + jobs_cost_week, 6)
    total_month = round(chat_month + jobs_cost_month, 6)

    # Burn rate y presupuesto desde FinOps controller
    budget_info: dict = {}
    burn_rate: dict = {}
    if _finops:
        try:
            status = _finops.get_status()
            budget_info = status.get("budget", {})
            burn_rate = _finops.get_burn_rate()
        except Exception as e:
            logger.warning("finops_status_failed", error=str(e))

    # Breakdown por modelo (solo runs de chat, hoy)
    by_model = _aggregate_by_model(runs_today)

    # Top runs más caros del día
    top_runs = _top_expensive_runs(runs_today, n=5)

    # Métricas de jobs del día
    jobs_completed = sum(1 for j in jobs_today if j.get("status") == "completed")
    jobs_failed = sum(1 for j in jobs_today if j.get("status") == "failed")

    return {
        "generated_at": now.isoformat(),
        "period": {
            "today": today_start,
            "week_start": week_start,
            "month_start": month_start,
        },
        "spend": {
            "today_usd": total_today,
            "week_usd": total_week,
            "month_usd": total_month,
            "chat_today_usd": chat_today,
            "jobs_today_usd": jobs_cost_today,
        },
        "budget": {
            "daily_limit_usd": budget_info.get("daily_limit", 15.0),
            "remaining_usd": budget_info.get("remaining", 0.0),
            "used_pct": round(total_today / max(budget_info.get("daily_limit", 15.0), 0.01) * 100, 1),
            "hard_stop_active": not budget_info.get("allowed", True),
        },
        "burn_rate": {
            "cost_per_hour_usd": burn_rate.get("cost_per_hour", 0.0),
            "projected_daily_usd": burn_rate.get("projected_daily", 0.0),
            "runs_last_hour": burn_rate.get("runs_last_hour", 0),
        },
        "by_model": by_model,
        "top_runs_today": top_runs,
        "jobs": {
            "executed_today": len(jobs_today),
            "completed_today": jobs_completed,
            "failed_today": jobs_failed,
            "cost_today_usd": jobs_cost_today,
        },
        "totals": {
            "chat_runs_today": len(runs_today),
            "chat_runs_week": len(runs_week),
            "chat_runs_month": len(runs_month),
        },
    }


@router.get("/history")
async def finops_history(request: Request, limit: int = 50):
    """
    Historial de los últimos N runs con su costo.
    Útil para debugging y auditoría.
    """
    if not _db or not _db.connected:
        return {"runs": [], "error": "Database not connected"}

    try:
        rows = await _db.select(
            "run_costs",
            columns="run_id,model_used,total_cost_usd,tokens_in,tokens_out,latency_ms,tool_count,status,created_at",
            limit=min(limit, 200),
        )
        runs = sorted(rows or [], key=lambda r: str(r.get("created_at", "")), reverse=True)
        return {
            "runs": [
                {
                    "run_id": r.get("run_id", ""),
                    "model": r.get("model_used", ""),
                    "cost_usd": round(float(r.get("total_cost_usd", 0)), 6),
                    "tokens_in": r.get("tokens_in", 0),
                    "tokens_out": r.get("tokens_out", 0),
                    "latency_ms": r.get("latency_ms", 0),
                    "tool_count": r.get("tool_count", 0),
                    "status": r.get("status", ""),
                    "created_at": r.get("created_at", ""),
                }
                for r in runs
            ],
            "total": len(runs),
        }
    except Exception as e:
        logger.error("finops_history_failed", error=str(e))
        return {"runs": [], "error": str(e)}
