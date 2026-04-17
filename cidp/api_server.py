"""
CIDP API Server — FastAPI wrapper for the CIDP microservice.
=============================================================
Exposes the CIDP (Ciclo de Investigación y Descubrimiento Perpetuo)
as a REST API that the Kernel consumes via CIDPClient.

Endpoints (per OpenAPI 3.1 spec):
    POST   /api/v1/jobs            → Start a new CIDP cycle
    GET    /api/v1/jobs/{job_id}   → Get job status
    DELETE /api/v1/jobs/{job_id}   → Cancel job (rollback)
    POST   /api/v1/jobs/{job_id}/resume → Resume from checkpoint
    GET    /health                 → Health check

Architecture:
    - Jobs run as background asyncio tasks (not blocking the API)
    - State persisted in SQLite via CIDPMemory (checkpoint-based)
    - Budget Guards enforced internally by run_cidp stages
    - Auth via Bearer token (CIDP_API_KEY env var)

Anti-autoboicot: FastAPI 0.136.0, uvicorn 0.44.0, Python 3.12-slim
CVE check: aiohttp>=3.13.4 (CVE-2026-22815 patched)
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Path setup for CIDP scripts ──────────────────────────────────────
CIDP_SCRIPTS_DIR = Path(__file__).parent / "scripts"
CIDP_CONFIG_DIR = Path(__file__).parent / "config"
CIDP_DATA_DIR = Path(__file__).parent / "data"
CIDP_DATA_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(CIDP_SCRIPTS_DIR))

logger = structlog.get_logger("cidp.api_server")

# ── Auth ──────────────────────────────────────────────────────────────

CIDP_API_KEY = os.environ.get("CIDP_API_KEY", "")


async def verify_api_key(authorization: Optional[str] = Header(None)):
    """Verify Bearer token if CIDP_API_KEY is set."""
    if not CIDP_API_KEY:
        return  # Dev mode — no auth required
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    if token != CIDP_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


# ── Models ────────────────────────────────────────────────────────────

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobRequest(BaseModel):
    target: str = Field(..., description="Software/platform to investigate")
    objective: str = Field(..., description="10x objective to achieve")
    max_iterations: int = Field(default=10, ge=1, le=50)
    budget_usd: float = Field(default=50.0, ge=1.0, le=500.0)
    enable_gpu_broker: bool = Field(default=False)
    gpu_budget_usd: float = Field(default=100.0, ge=0.0, le=1000.0)
    webhook_url: Optional[str] = Field(default=None)
    research_only: bool = Field(default=False)
    skip_calibration: bool = Field(default=False)
    convergence_threshold: float = Field(default=0.8, ge=0.1, le=1.0)


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    current_iteration: int = 0
    current_stage: str = "queued"
    cost_usd: float = 0.0
    score: float = 0.0
    artifacts: Dict[str, Any] = {}
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ── In-memory job registry ────────────────────────────────────────────

_jobs: Dict[str, Dict[str, Any]] = {}
_job_tasks: Dict[str, asyncio.Task] = {}


# ── App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="CIDP — Ciclo de Investigación y Descubrimiento Perpetuo",
    version="1.1.0",
    description="Microservicio autónomo de investigación iterativa para El Monstruo",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Background job runner ─────────────────────────────────────────────

async def _run_cidp_job(job_id: str, request: JobRequest):
    """Execute CIDP cycle as background task."""
    job = _jobs[job_id]
    job["status"] = JobStatus.RUNNING.value
    job["started_at"] = datetime.now(timezone.utc).isoformat()

    try:
        # Import CIDP runner
        from run_cidp import run_cycle
        import argparse

        # Build args namespace matching run_cidp expectations
        args = argparse.Namespace(
            target=request.target,
            objective=request.objective,
            output_dir=str(CIDP_DATA_DIR / "runs" / job_id),
            max_iterations=request.max_iterations,
            budget_usd=request.budget_usd,
            research_only=request.research_only,
            skip_calibration=request.skip_calibration,
            enable_gpu_broker=request.enable_gpu_broker,
            gpu_budget_usd=request.gpu_budget_usd,
            convergence_threshold=request.convergence_threshold,
            dimensions=None,
        )

        # Create output directory
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)

        # Run the cycle
        result = await run_cycle(args)

        # Update job state
        job["status"] = result.get("status", "completed")
        if job["status"] not in ["converged", "stopped", "aborted"]:
            job["status"] = JobStatus.COMPLETED.value
        else:
            job["status"] = JobStatus.COMPLETED.value

        job["score"] = result.get("final_score", 0.0)
        job["cost_usd"] = result.get("total_cost_usd", 0.0)
        job["current_iteration"] = result.get("iterations", 0)
        job["current_stage"] = "convergence"
        job["artifacts"] = {
            "run_id": result.get("run_id", job_id),
            "output_dir": args.output_dir,
            "final_report": result,
        }
        job["completed_at"] = datetime.now(timezone.utc).isoformat()

        logger.info(
            "cidp_job_completed",
            job_id=job_id,
            score=job["score"],
            cost=job["cost_usd"],
            iterations=job["current_iteration"],
        )

    except asyncio.CancelledError:
        job["status"] = JobStatus.CANCELLED.value
        job["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("cidp_job_cancelled", job_id=job_id)

    except Exception as e:
        job["status"] = JobStatus.FAILED.value
        job["error"] = str(e)
        job["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.error("cidp_job_failed", job_id=job_id, error=str(e))


# ── Endpoints ─────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "cidp",
        "version": "1.1.0",
        "active_jobs": len([j for j in _jobs.values() if j["status"] == "running"]),
        "total_jobs": len(_jobs),
    }


@app.post("/api/v1/jobs", response_model=JobResponse, status_code=202,
          dependencies=[Depends(verify_api_key)])
async def start_job(request: JobRequest):
    """Start a new CIDP investigation cycle."""
    job_id = f"cidp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    # Initialize job state
    _jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatus.QUEUED.value,
        "current_iteration": 0,
        "current_stage": "queued",
        "cost_usd": 0.0,
        "score": 0.0,
        "artifacts": {},
        "error": None,
        "started_at": None,
        "completed_at": None,
        "request": request.model_dump(),
    }

    # Launch background task
    task = asyncio.create_task(_run_cidp_job(job_id, request))
    _job_tasks[job_id] = task

    logger.info(
        "cidp_job_started",
        job_id=job_id,
        target=request.target,
        objective=request.objective[:80],
        budget=request.budget_usd,
    )

    return JobResponse(
        job_id=job_id,
        status="queued",
        message=f"CIDP cycle initiated for '{request.target}'. Use GET /api/v1/jobs/{job_id} to poll status.",
    )


@app.get("/api/v1/jobs/{job_id}", response_model=JobStatusResponse,
         dependencies=[Depends(verify_api_key)])
async def get_job_status(job_id: str):
    """Get the current status of a CIDP job."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = _jobs[job_id]
    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        current_iteration=job["current_iteration"],
        current_stage=job["current_stage"],
        cost_usd=job["cost_usd"],
        score=job["score"],
        artifacts=job["artifacts"],
        error=job["error"],
        started_at=job["started_at"],
        completed_at=job["completed_at"],
    )


@app.delete("/api/v1/jobs/{job_id}", response_model=JobStatusResponse,
            dependencies=[Depends(verify_api_key)])
async def cancel_job(job_id: str):
    """Cancel a running CIDP job with rollback."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = _jobs[job_id]

    if job["status"] not in ["queued", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is {job['status']}, cannot cancel",
        )

    # Cancel the asyncio task
    task = _job_tasks.get(job_id)
    if task and not task.done():
        task.cancel()

    job["status"] = JobStatus.CANCELLED.value
    job["completed_at"] = datetime.now(timezone.utc).isoformat()

    logger.info("cidp_job_cancelled_by_user", job_id=job_id)

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        current_iteration=job["current_iteration"],
        current_stage=job["current_stage"],
        cost_usd=job["cost_usd"],
        score=job["score"],
        artifacts=job["artifacts"],
        error=job["error"],
        started_at=job["started_at"],
        completed_at=job["completed_at"],
    )


@app.post("/api/v1/jobs/{job_id}/resume", response_model=JobResponse, status_code=202,
          dependencies=[Depends(verify_api_key)])
async def resume_job(job_id: str):
    """Resume a paused or failed CIDP job from the last checkpoint."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = _jobs[job_id]

    if job["status"] not in ["paused", "failed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is {job['status']}, can only resume paused/failed jobs",
        )

    # Re-launch the job (CIDPMemory handles checkpoint resume internally)
    request = JobRequest(**job["request"])
    job["status"] = JobStatus.QUEUED.value
    job["error"] = None

    task = asyncio.create_task(_run_cidp_job(job_id, request))
    _job_tasks[job_id] = task

    logger.info("cidp_job_resumed", job_id=job_id)

    return JobResponse(
        job_id=job_id,
        status="queued",
        message=f"CIDP job {job_id} resumed from last checkpoint.",
    )


# ── List all jobs ─────────────────────────────────────────────────────

@app.get("/api/v1/jobs", dependencies=[Depends(verify_api_key)])
async def list_jobs(status: Optional[str] = None, limit: int = 20):
    """List all CIDP jobs, optionally filtered by status."""
    jobs = list(_jobs.values())
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    # Sort by most recent first
    jobs.sort(key=lambda j: j.get("started_at") or "", reverse=True)
    return {"jobs": jobs[:limit], "total": len(jobs)}


# ── Entry point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "cidp.api_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
