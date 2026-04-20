"""
El Monstruo — Autonomy API Routes (Sprint 8)
==============================================
REST endpoints for managing scheduled jobs:
    POST   /v1/autonomy/schedule   → Create a scheduled job
    GET    /v1/autonomy/jobs       → List all jobs for a user
    GET    /v1/autonomy/jobs/{id}  → Get job details + executions
    POST   /v1/autonomy/cancel/{id}→ Cancel a scheduled job
    GET    /v1/autonomy/stats      → Runner statistics

These endpoints are an alternative to the schedule_task tool —
the tool is used by the LLM during conversation, while these
endpoints can be used by the bot or external clients directly.
"""

from __future__ import annotations

from typing import Any, Optional

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger("api.autonomy")

router = APIRouter(prefix="/v1/autonomy", tags=["autonomy"])

# ── Request/Response Models ─────────────────────────────────────────


class ScheduleRequest(BaseModel):
    title: str = Field(..., description="Short title for the task")
    instruction: str = Field(..., description="Full instruction for the Monstruo to execute")
    run_at: str = Field(..., description="When to execute (ISO 8601, relative, or natural)")
    timezone: str = Field(default="America/Mexico_City", description="User timezone")
    channel: str = Field(default="telegram", description="Notification channel")
    recurrence: Optional[str] = Field(default=None, description="null, 'daily', or 'weekly'")
    user_id: str = Field(default="alfredo", description="User ID")


class ScheduleResponse(BaseModel):
    success: bool
    job_id: Optional[str] = None
    title: Optional[str] = None
    run_at_utc: Optional[str] = None
    run_at_local: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class JobDetail(BaseModel):
    id: str
    title: str
    instruction: str
    run_at: str
    timezone: str
    channel: str
    status: str
    recurrence: Optional[str] = None
    created_at: str
    updated_at: str
    executions: list[dict] = []


class RunnerStats(BaseModel):
    runner_active: bool
    poll_interval_s: int
    max_concurrent: int
    jobs_executed: int
    jobs_failed: int
    pending_jobs: int
    total_jobs: int


# ── Dependency Injection ────────────────────────────────────────────
# These are set by main.py during lifespan startup
_db = None
_runner = None


def set_dependencies(db: Any, runner: Any) -> None:
    """Called by main.py to inject dependencies."""
    global _db, _runner
    _db = db
    _runner = runner


# ── Endpoints ───────────────────────────────────────────────────────


@router.post("/schedule", response_model=ScheduleResponse)
async def schedule_job(request: ScheduleRequest):
    """Create a new scheduled job via API."""
    if not _db or not _db.connected:
        raise HTTPException(status_code=503, detail="Database not available")

    from tools.schedule_task import execute_schedule_task

    result = await execute_schedule_task(
        params={
            "title": request.title,
            "instruction": request.instruction,
            "run_at": request.run_at,
            "timezone": request.timezone,
            "channel": request.channel,
            "recurrence": request.recurrence,
        },
        context={
            "user_id": request.user_id,
            "thread_id": "",
            "db": _db,
            "source": "api",
        },
    )
    return ScheduleResponse(**result)


@router.get("/jobs")
async def list_jobs(
    user_id: str = "alfredo",
    status: Optional[str] = None,
    limit: int = 50,
):
    """List scheduled jobs for a user."""
    if not _db or not _db.connected:
        raise HTTPException(status_code=503, detail="Database not available")

    filters = {"user_id": user_id}
    if status:
        filters["status"] = status

    jobs = await _db.select(
        "scheduled_jobs",
        filters=filters,
        order_by="created_at",
        order_desc=True,
        limit=limit,
    )
    return {"jobs": jobs, "count": len(jobs)}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get details of a specific job including execution history."""
    if not _db or not _db.connected:
        raise HTTPException(status_code=503, detail="Database not available")

    jobs = await _db.select(
        "scheduled_jobs",
        filters={"id": job_id},
        limit=1,
    )
    if not jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[0]

    # Get executions
    executions = await _db.select(
        "job_executions",
        filters={"scheduled_job_id": job_id},
        order_by="started_at",
        order_desc=True,
        limit=20,
    )

    job["executions"] = executions
    return job


@router.post("/cancel/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a scheduled job."""
    if not _db or not _db.connected:
        raise HTTPException(status_code=503, detail="Database not available")

    jobs = await _db.select(
        "scheduled_jobs",
        filters={"id": job_id},
        limit=1,
    )
    if not jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[0]
    if job.get("status") not in ("scheduled",):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status '{job.get('status')}'. Only 'scheduled' jobs can be cancelled.",
        )

    await _db.update(
        "scheduled_jobs",
        {"status": "cancelled"},
        {"id": job_id},
    )

    logger.info("job_cancelled", job_id=job_id)
    return {
        "success": True,
        "job_id": job_id,
        "message": f"Job '{job.get('title')}' cancelled.",
    }


@router.get("/stats", response_model=RunnerStats)
async def runner_stats():
    """Get autonomous runner statistics."""
    if not _db or not _db.connected:
        runner_stats = _runner.stats if _runner else {}
        return RunnerStats(
            runner_active=runner_stats.get("running", False),
            poll_interval_s=runner_stats.get("poll_interval_s", 60),
            max_concurrent=runner_stats.get("max_concurrent", 3),
            jobs_executed=runner_stats.get("jobs_executed", 0),
            jobs_failed=runner_stats.get("jobs_failed", 0),
            pending_jobs=0,
            total_jobs=0,
        )

    pending = await _db.count("scheduled_jobs", filters={"status": "scheduled"})
    total = await _db.count("scheduled_jobs")
    runner_data = _runner.stats if _runner else {}

    return RunnerStats(
        runner_active=runner_data.get("running", False),
        poll_interval_s=runner_data.get("poll_interval_s", 60),
        max_concurrent=runner_data.get("max_concurrent", 3),
        jobs_executed=runner_data.get("jobs_executed", 0),
        jobs_failed=runner_data.get("jobs_failed", 0),
        pending_jobs=pending,
        total_jobs=total,
    )
