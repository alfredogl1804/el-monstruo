"""
Sprint 87 — E2E Orchestrator.

Maneja el ciclo de vida de un run E2E:
- create → estado='in_progress'
- ejecuta pipeline.run_e2e_pipeline en background
- expone get/list/update vía repository
- procesa veredicto humano (judgment)

Diseñado para ser inyectable en kernel/e2e/routes.py vía app.state.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import structlog

from kernel.e2e.repository import DBClient, E2ERepository
from kernel.e2e.schema import (
    DashboardSnapshot,
    E2ERun,
    EstadoRun,
    Veredicto,
)

logger = structlog.get_logger("e2e_orchestrator")


class E2EOrchestrator:
    """Coordina lifecycle de runs E2E. Stateless excepto el repository inyectado."""

    def __init__(
        self,
        db: DBClient,
        *,
        pipeline_runner=None,
    ) -> None:
        self._repo = E2ERepository(db)
        # pipeline_runner se importa lazy para evitar ciclos al cargar el módulo.
        # Se puede inyectar en tests con un fake.
        self._pipeline_runner = pipeline_runner

    @property
    def repository(self) -> E2ERepository:
        return self._repo

    @property
    def connected(self) -> bool:
        return self._repo.connected

    async def start_run(
        self,
        frase_input: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> E2ERun:
        """Crea run y dispara pipeline async (fire-and-forget)."""
        run = await self._repo.create_run(frase_input, metadata or {})
        # Lazy import del pipeline_runner para no importar dependencies pesadas en tests
        runner = self._pipeline_runner or self._default_runner
        try:
            asyncio.create_task(runner(run.id, self._repo))
        except RuntimeError:
            # No hay event loop activo (caso defensivo, no debería pasar en FastAPI)
            logger.warning("e2e_pipeline_no_loop", run_id=run.id)
        return run

    async def get_run(self, run_id: str) -> Optional[E2ERun]:
        return await self._repo.get_run(run_id)

    async def list_runs(
        self,
        *,
        estado: Optional[EstadoRun] = None,
        limit: int = 50,
    ) -> list[E2ERun]:
        return await self._repo.list_runs(estado=estado, limit=limit)

    async def emit_judgment(
        self,
        run_id: str,
        veredicto: Veredicto,
        nota: Optional[str] = None,
    ) -> Optional[E2ERun]:
        """Alfredo emite veredicto sobre un run. Lo cierra a 'completed'."""
        run = await self._repo.get_run(run_id)
        if run is None:
            return None
        # Si ya estaba completado o awaiting, lo movemos a completed con veredicto.
        new_estado = EstadoRun.COMPLETED
        completed_at = datetime.now(timezone.utc)
        metadata_patch: Dict[str, Any] = {"judgment_nota": nota} if nota else {}
        return await self._repo.update_run(
            run_id,
            estado=new_estado,
            veredicto_alfredo=veredicto,
            completed_at=completed_at,
            metadata_patch=metadata_patch or None,
        )

    async def dashboard_snapshot(self, recent_n: int = 5) -> DashboardSnapshot:
        all_runs = await self._repo.list_runs(limit=200)
        total = len(all_runs)
        in_progress = sum(1 for r in all_runs if r.estado == EstadoRun.IN_PROGRESS)
        completed = sum(1 for r in all_runs if r.estado == EstadoRun.COMPLETED)
        failed = sum(1 for r in all_runs if r.estado == EstadoRun.FAILED)
        awaiting = sum(1 for r in all_runs if r.estado == EstadoRun.AWAITING_JUDGMENT)

        veredictos: Dict[str, int] = {}
        for r in all_runs:
            if r.veredicto_alfredo is not None:
                veredictos[r.veredicto_alfredo.value] = (
                    veredictos.get(r.veredicto_alfredo.value, 0) + 1
                )

        scores = [r.critic_visual_score for r in all_runs if r.critic_visual_score is not None]
        avg = sum(scores) / len(scores) if scores else None

        last_5 = []
        for r in all_runs[:recent_n]:
            last_5.append(
                {
                    "id": r.id,
                    "frase_input": r.frase_input[:120],
                    "estado": r.estado.value,
                    "pipeline_step": r.pipeline_step,
                    "deploy_url": r.deploy_url,
                    "critic_visual_score": r.critic_visual_score,
                    "veredicto_alfredo": (
                        r.veredicto_alfredo.value if r.veredicto_alfredo else None
                    ),
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                }
            )

        return DashboardSnapshot(
            runs_total=total,
            runs_in_progress=in_progress,
            runs_completed=completed,
            runs_failed=failed,
            runs_awaiting_judgment=awaiting,
            veredictos_breakdown=veredictos,
            avg_critic_visual_score=avg,
            last_5_runs=last_5,
        )

    # ---------- runner por defecto ----------

    @staticmethod
    async def _default_runner(run_id: str, repo: E2ERepository) -> None:
        """Importa kernel.e2e.pipeline lazy para evitar ciclos."""
        try:
            from kernel.e2e.pipeline import run_e2e_pipeline

            await run_e2e_pipeline(run_id, repo)
        except Exception as exc:
            logger.error(
                "e2e_pipeline_runner_failed",
                run_id=run_id,
                error=str(exc),
            )
            try:
                await repo.update_run(
                    run_id,
                    estado=EstadoRun.FAILED,
                    completed_at=datetime.now(timezone.utc),
                    metadata_patch={"runner_error": str(exc)},
                )
            except Exception:
                logger.error("e2e_pipeline_finalize_failed", run_id=run_id)
