"""
El Monstruo — Background Job Store (Sprint 35)
================================================
Persistencia de background jobs en Supabase.

Reemplaza el dict en memoria (background_jobs: dict[str, dict])
que se perdía en cada reinicio de Railway.

Responsabilidades:
    - Crear jobs en Supabase al recibirlos
    - Actualizar estado (queued → running → completed/failed)
    - Registrar progreso en tiempo real (progress_log)
    - Marcar cancelación solicitada
    - Leer estado para polling y SSE

Fallback:
    Si Supabase no está disponible, cae silenciosamente al dict
    en memoria (comportamiento anterior). El kernel nunca falla
    por un error de persistencia de jobs.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("background.store")

TABLE = "background_jobs"


class BackgroundStore:
    """
    Abstracción de persistencia para background jobs.
    Usa Supabase si está disponible, dict en memoria como fallback.
    """

    def __init__(self, db: Optional[Any] = None):
        self._db = db
        self._mem: dict[str, dict] = {}  # fallback in-memory
        self._lock = asyncio.Lock()

    def _use_db(self) -> bool:
        return self._db is not None and getattr(self._db, "_connected", False)

    # ── Create ──────────────────────────────────────────────────────

    async def create(
        self,
        job_id: str,
        message: str,
        user_id: str = "anonymous",
        channel: str = "api",
        brain: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        webhook_url: Optional[str] = None,
    ) -> str:
        """Create a new job in queued state. Returns job_id."""
        now = datetime.now(timezone.utc).isoformat()
        row = {
            "id": job_id,
            "user_id": user_id,
            "channel": channel,
            "message": message,
            "brain": brain,
            "session_id": session_id,
            "metadata": metadata,
            "webhook_url": webhook_url,
            "status": "queued",
            "progress": 0,
            "progress_log": [],
            "result": None,
            "error": None,
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "tokens_in": 0,
            "tokens_out": 0,
            "cost_usd": 0,
            "latency_ms": 0,
            "cancelled_at": None,
            "cancel_requested": False,
        }
        if self._use_db():
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._db._client.table(TABLE).insert(row).execute(),
                )
                logger.info("bg_job_created_supabase", job_id=job_id)
            except Exception as e:
                logger.warning("bg_job_create_db_failed", job_id=job_id, error=str(e))
                async with self._lock:
                    self._mem[job_id] = row
        else:
            async with self._lock:
                self._mem[job_id] = row
        return job_id

    # ── Read ─────────────────────────────────────────────────────────

    async def get(self, job_id: str) -> Optional[dict]:
        """Get job by ID."""
        if self._use_db():
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._db._client.table(TABLE).select("*").eq("id", job_id).limit(1).execute(),
                )
                if result.data:
                    return result.data[0]
            except Exception as e:
                logger.warning("bg_job_get_db_failed", job_id=job_id, error=str(e))
        async with self._lock:
            return self._mem.get(job_id)

    async def list_jobs(self, limit: int = 20, user_id: Optional[str] = None) -> list[dict]:
        """List recent jobs, optionally filtered by user_id."""
        if self._use_db():
            try:
                query = self._db._client.table(TABLE).select("*").order("created_at", desc=True).limit(limit)
                if user_id:
                    query = query.eq("user_id", user_id)
                result = await asyncio.get_event_loop().run_in_executor(None, lambda: query.execute())
                return result.data or []
            except Exception as e:
                logger.warning("bg_job_list_db_failed", error=str(e))
        async with self._lock:
            jobs = sorted(
                self._mem.values(),
                key=lambda j: j.get("created_at", ""),
                reverse=True,
            )
            if user_id:
                jobs = [j for j in jobs if j.get("user_id") == user_id]
            return jobs[:limit]

    # ── Update ───────────────────────────────────────────────────────

    async def set_running(self, job_id: str) -> None:
        """Mark job as running."""
        now = datetime.now(timezone.utc).isoformat()
        await self._patch(job_id, {"status": "running", "started_at": now})

    async def set_completed(self, job_id: str, result: dict) -> None:
        """Mark job as completed with result."""
        now = datetime.now(timezone.utc).isoformat()
        patch = {
            "status": "completed",
            "completed_at": now,
            "result": result,
            "tokens_in": result.get("tokens_in", 0),
            "tokens_out": result.get("tokens_out", 0),
            "cost_usd": result.get("cost_usd", 0),
            "latency_ms": result.get("latency_ms", 0),
            "progress": 100,
        }
        await self._patch(job_id, patch)

    async def set_failed(self, job_id: str, error: str) -> None:
        """Mark job as failed with error message."""
        now = datetime.now(timezone.utc).isoformat()
        await self._patch(
            job_id,
            {
                "status": "failed",
                "completed_at": now,
                "error": error,
            },
        )

    async def set_cancelled(self, job_id: str) -> None:
        """Mark job as cancelled."""
        now = datetime.now(timezone.utc).isoformat()
        await self._patch(
            job_id,
            {
                "status": "cancelled",
                "cancelled_at": now,
                "completed_at": now,
            },
        )

    async def request_cancel(self, job_id: str) -> bool:
        """
        Request cancellation of a running job.
        Returns True if the job exists and was in a cancellable state.
        """
        job = await self.get(job_id)
        if not job:
            return False
        if job.get("status") not in ("queued", "running"):
            return False
        await self._patch(job_id, {"cancel_requested": True})
        logger.info("bg_job_cancel_requested", job_id=job_id)
        return True

    async def is_cancel_requested(self, job_id: str) -> bool:
        """Check if cancellation has been requested for this job."""
        job = await self.get(job_id)
        return bool(job and job.get("cancel_requested", False))

    async def append_progress(self, job_id: str, pct: int, msg: str) -> None:
        """
        Append a progress entry to the job's progress_log.
        Uses Supabase RPC if available, otherwise updates in-memory.
        """
        if self._use_db():
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._db._client.rpc(
                        "bg_job_append_progress",
                        {"p_job_id": job_id, "p_pct": pct, "p_msg": msg},
                    ).execute(),
                )
                return
            except Exception as e:
                logger.warning("bg_progress_rpc_failed", job_id=job_id, error=str(e))
        # Fallback: in-memory
        async with self._lock:
            job = self._mem.get(job_id)
            if job:
                job["progress"] = pct
                if not isinstance(job.get("progress_log"), list):
                    job["progress_log"] = []
                job["progress_log"].append(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "pct": pct,
                        "msg": msg,
                    }
                )

    # ── Internal ─────────────────────────────────────────────────────

    async def _patch(self, job_id: str, fields: dict) -> None:
        """Apply a partial update to a job."""
        if self._use_db():
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._db._client.table(TABLE).update(fields).eq("id", job_id).execute(),
                )
                return
            except Exception as e:
                logger.warning("bg_job_patch_db_failed", job_id=job_id, error=str(e))
        async with self._lock:
            job = self._mem.get(job_id)
            if job:
                job.update(fields)
