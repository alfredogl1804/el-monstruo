"""
El Monstruo — Task Planner Routes (Sprint 40)
=============================================
Endpoints de observabilidad y control para el Task Planner.

Endpoints:
    POST /v1/planner/plan          — Crear un nuevo plan para un objetivo
    POST /v1/planner/execute/{id}  — Ejecutar un plan existente
    GET  /v1/planner/plans         — Listar planes activos
    GET  /v1/planner/plan/{id}     — Obtener estado de un plan
    POST /v1/planner/plan_and_run  — Crear y ejecutar en un solo paso
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = structlog.get_logger("kernel.planner_routes")

router = APIRouter(prefix="/v1/planner", tags=["planner"])

KERNEL_API_KEY = os.environ.get("MONSTRUO_API_KEY", "")


def _check_auth(request: Request) -> None:
    """Verify API key from headers."""
    if not KERNEL_API_KEY:
        return  # No key configured — allow all (dev mode)
    key = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").replace("Bearer ", "")
    if key != KERNEL_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ── Request/Response Models ──────────────────────────────────────────

class PlanRequest(BaseModel):
    objective: str
    context: Optional[dict[str, Any]] = None
    user_id: str = "embrion"
    max_steps: int = 10


class PlanAndRunRequest(BaseModel):
    objective: str
    context: Optional[dict[str, Any]] = None
    user_id: str = "embrion"
    max_steps: int = 10


# ── Endpoints ────────────────────────────────────────────────────────

@router.post("/plan")
async def create_plan(body: PlanRequest, request: Request) -> dict:
    """Create a new task plan for the given objective (without executing)."""
    _check_auth(request)
    try:
        from kernel.task_planner import TaskPlanner
        kernel = request.app.state.kernel if hasattr(request.app.state, "kernel") else None
        db = request.app.state.db if hasattr(request.app.state, "db") else None

        if not kernel:
            raise HTTPException(status_code=503, detail="Kernel not available")

        planner = TaskPlanner(kernel=kernel, db=db)
        plan = await planner.plan(
            objective=body.objective,
            context=body.context,
            user_id=body.user_id,
            max_steps=body.max_steps,
        )
        return {
            "success": True,
            "plan": plan.to_dict(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("planner_create_plan_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/{plan_id}")
async def execute_plan(plan_id: str, request: Request) -> dict:
    """Execute an existing plan by ID."""
    _check_auth(request)
    try:
        from kernel.task_planner import TaskPlanner
        kernel = request.app.state.kernel if hasattr(request.app.state, "kernel") else None
        db = request.app.state.db if hasattr(request.app.state, "db") else None

        if not kernel:
            raise HTTPException(status_code=503, detail="Kernel not available")

        planner = TaskPlanner(kernel=kernel, db=db)
        plan = planner.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found in active plans")

        result = await planner.execute(plan)
        return {
            "success": True,
            "result": result,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("planner_execute_plan_error", error=str(e), plan_id=plan_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan_and_run")
async def plan_and_run(body: PlanAndRunRequest, request: Request) -> dict:
    """Create and execute a plan in a single step (async — returns immediately with plan_id)."""
    _check_auth(request)
    try:
        from kernel.task_planner import TaskPlanner
        kernel = request.app.state.kernel if hasattr(request.app.state, "kernel") else None
        db = request.app.state.db if hasattr(request.app.state, "db") else None

        if not kernel:
            raise HTTPException(status_code=503, detail="Kernel not available")

        planner = TaskPlanner(kernel=kernel, db=db)
        plan = await planner.plan(
            objective=body.objective,
            context=body.context,
            user_id=body.user_id,
            max_steps=body.max_steps,
        )

        # Execute asynchronously — don't block the HTTP response
        asyncio.create_task(planner.execute(plan, user_id=body.user_id))

        return {
            "success": True,
            "plan_id": plan.plan_id,
            "steps": len(plan.steps),
            "message": f"Plan creado con {len(plan.steps)} pasos. Ejecutando en background.",
            "plan_summary": [
                {"index": s.index, "description": s.description[:100], "tool_hint": s.tool_hint}
                for s in plan.steps
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("planner_plan_and_run_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans")
async def list_plans(request: Request) -> dict:
    """List all active plans in memory."""
    _check_auth(request)
    try:
        from kernel.task_planner import TaskPlanner
        kernel = request.app.state.kernel if hasattr(request.app.state, "kernel") else None
        db = request.app.state.db if hasattr(request.app.state, "db") else None

        if not kernel:
            return {"plans": [], "total": 0}

        planner = TaskPlanner(kernel=kernel, db=db)
        plans = planner.get_active_plans()
        return {
            "plans": plans,
            "total": len(plans),
        }
    except Exception as e:
        logger.error("planner_list_plans_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plan/{plan_id}")
async def get_plan(plan_id: str, request: Request) -> dict:
    """Get the current state of a plan by ID."""
    _check_auth(request)
    try:
        from kernel.task_planner import TaskPlanner
        kernel = request.app.state.kernel if hasattr(request.app.state, "kernel") else None
        db = request.app.state.db if hasattr(request.app.state, "db") else None

        if not kernel:
            raise HTTPException(status_code=503, detail="Kernel not available")

        planner = TaskPlanner(kernel=kernel, db=db)
        plan = planner.get_plan(plan_id)
        if not plan:
            # Try to load from DB
            if db:
                try:
                    rows = await db.select(
                        table="task_plans",
                        columns="*",
                        filters={"plan_id": plan_id},
                        limit=1,
                    )
                    if rows:
                        return {"plan": rows[0], "source": "database"}
                except Exception:
                    pass
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")

        return {
            "plan": plan.to_dict(),
            "source": "memory",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("planner_get_plan_error", error=str(e), plan_id=plan_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_planner(body: PlanRequest, request: Request) -> dict:
    """Test endpoint: only checks if objective is complex and generates a plan (no execution)."""
    _check_auth(request)
    try:
        from kernel.task_planner import TaskPlanner
        kernel = request.app.state.kernel if hasattr(request.app.state, "kernel") else None
        db = request.app.state.db if hasattr(request.app.state, "db") else None

        # is_complex_objective is an instance method — create a temporary planner to call it
        _tmp_planner = TaskPlanner(kernel=None, db=None)
        is_complex = _tmp_planner.is_complex_objective(body.objective)
        if not is_complex:
            return {
                "is_complex": False,
                "message": "El objetivo no es complejo — se ejecutaría directamente sin planificador",
                "objective": body.objective,
            }

        if not kernel:
            return {
                "is_complex": True,
                "message": "Objetivo complejo detectado pero kernel no disponible para generar plan",
                "objective": body.objective,
            }

        planner = TaskPlanner(kernel=kernel, db=db)
        plan = await planner.plan(
            objective=body.objective,
            context=body.context,
            user_id=body.user_id,
            max_steps=body.max_steps,
        )
        return {
            "is_complex": True,
            "plan_id": plan.plan_id,
            "steps": len(plan.steps),
            "plan_summary": [
                {"index": s.index, "description": s.description[:120], "tool_hint": s.tool_hint}
                for s in plan.steps
            ],
            "message": f"Plan generado con {len(plan.steps)} pasos (no ejecutado)",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("planner_test_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_plan_history(request: Request, limit: int = 20) -> dict:
    """Get plan execution history from Supabase."""
    _check_auth(request)
    try:
        db = request.app.state.db if hasattr(request.app.state, "db") else None
        if not db:
            return {"plans": [], "total": 0, "message": "DB not available"}

        rows = await db.select(
            table="task_plans",
            columns="plan_id,objective,status,progress_pct,total_steps,done_steps,failed_steps,total_cost_usd,revision_count,created_at,finished_at,final_summary",
            order_by="created_at",
            order_desc=True,
            limit=limit,
        )
        return {
            "plans": rows or [],
            "total": len(rows or []),
        }
    except Exception as e:
        logger.error("planner_history_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
