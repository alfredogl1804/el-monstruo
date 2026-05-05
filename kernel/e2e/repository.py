"""
Sprint 87 — Repository (data access layer) para e2e_runs y e2e_step_log.

Abstrae todas las operaciones DB del orchestrator. Permite mock fácil en tests.
Patrón verificado contra el wrapper interno SupabaseClient (memory/supabase_client.py).

Brand DNA: errores con formato {module}_{action}_{failure_type}.
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol

import structlog

from kernel.e2e.schema import (
    E2ERun,
    E2EStepLog,
    EstadoRun,
    StepName,
    StepStatus,
    Veredicto,
)

logger = structlog.get_logger("e2e_repository")


# Protocolo mínimo que necesitamos del SupabaseClient real (testabilidad)
class DBClient(Protocol):
    @property
    def connected(self) -> bool: ...

    async def insert(
        self, table: str, data: dict[str, Any]
    ) -> Optional[dict]: ...

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
        limit: Optional[int] = None,
    ) -> list[dict]: ...

    async def update(
        self,
        table: str,
        data: dict[str, Any],
        filters: dict[str, Any],
    ) -> Optional[dict]: ...


def generate_run_id(frase_input: str) -> str:
    """Formato 'e2e_<utc_epoch>_<hash6>'. Determinístico solo en frase+epoch."""
    epoch = int(time.time())
    h = hashlib.sha256(f"{frase_input}|{epoch}".encode("utf-8")).hexdigest()[:6]
    return f"e2e_{epoch}_{h}"


def _serialize_for_db(model: Any) -> Dict[str, Any]:
    """Serializa Pydantic con formato JSON (datetime → str ISO, Enum → value)."""
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json", exclude_none=True)
    return dict(model)


class E2ERepository:
    """Acceso a las 2 tablas del Sprint 87. Uno por orchestrator instance."""

    TABLE_RUNS = "e2e_runs"
    TABLE_STEP_LOG = "e2e_step_log"

    def __init__(self, db: DBClient) -> None:
        self._db = db

    @property
    def connected(self) -> bool:
        return bool(getattr(self._db, "connected", False))

    # ---------- e2e_runs ----------

    async def create_run(self, frase_input: str, metadata: Dict[str, Any]) -> E2ERun:
        """Inserta un nuevo run con estado='in_progress'."""
        run_id = generate_run_id(frase_input)
        now = datetime.now(timezone.utc)
        row = {
            "id": run_id,
            "frase_input": frase_input,
            "estado": EstadoRun.IN_PROGRESS.value,
            "pipeline_step": 0,
            "started_at": now.isoformat(),
            "metadata": metadata or {},
        }
        result = await self._db.insert(self.TABLE_RUNS, row)
        if not result:
            logger.error("e2e_create_run_failed", run_id=run_id)
            # Devolver objeto in-memory aún si DB no respondió (modo degraded)
            return E2ERun(
                id=run_id,
                frase_input=frase_input,
                estado=EstadoRun.IN_PROGRESS,
                pipeline_step=0,
                started_at=now,
                metadata=metadata or {},
            )
        return E2ERun.model_validate(result)

    async def get_run(self, run_id: str) -> Optional[E2ERun]:
        rows = await self._db.select(
            self.TABLE_RUNS,
            filters={"id": run_id},
            limit=1,
        )
        if not rows:
            return None
        return E2ERun.model_validate(rows[0])

    async def update_run(
        self,
        run_id: str,
        *,
        estado: Optional[EstadoRun] = None,
        pipeline_step: Optional[int] = None,
        brief: Optional[Dict[str, Any]] = None,
        stack_decision: Optional[Dict[str, Any]] = None,
        deploy_url: Optional[str] = None,
        critic_visual_score: Optional[float] = None,
        veredicto_alfredo: Optional[Veredicto] = None,
        completed_at: Optional[datetime] = None,
        metadata_patch: Optional[Dict[str, Any]] = None,
    ) -> Optional[E2ERun]:
        """Patch quirúrgico de un run. Solo escribe campos no-None."""
        patch: Dict[str, Any] = {}
        if estado is not None:
            patch["estado"] = estado.value
        if pipeline_step is not None:
            patch["pipeline_step"] = pipeline_step
        if brief is not None:
            patch["brief"] = brief
        if stack_decision is not None:
            patch["stack_decision"] = stack_decision
        if deploy_url is not None:
            patch["deploy_url"] = deploy_url
        if critic_visual_score is not None:
            patch["critic_visual_score"] = float(critic_visual_score)
        if veredicto_alfredo is not None:
            patch["veredicto_alfredo"] = veredicto_alfredo.value
        if completed_at is not None:
            patch["completed_at"] = completed_at.isoformat()

        if metadata_patch:
            # Para metadata hacemos merge in-memory (Supabase no tiene JSON merge nativo simple)
            current = await self.get_run(run_id)
            current_metadata = current.metadata if current else {}
            merged = {**current_metadata, **metadata_patch}
            patch["metadata"] = merged

        if not patch:
            return await self.get_run(run_id)

        result = await self._db.update(self.TABLE_RUNS, patch, {"id": run_id})
        if not result:
            return None
        return E2ERun.model_validate(result)

    async def list_runs(
        self,
        *,
        estado: Optional[EstadoRun] = None,
        limit: int = 50,
    ) -> List[E2ERun]:
        filters: Dict[str, Any] = {}
        if estado is not None:
            filters["estado"] = estado.value
        rows = await self._db.select(
            self.TABLE_RUNS,
            filters=filters or None,
            order_by="started_at",
            order_desc=True,
            limit=limit,
        )
        return [E2ERun.model_validate(r) for r in rows]

    # ---------- e2e_step_log ----------

    async def append_step_log(
        self,
        run_id: str,
        *,
        step_number: int,
        step_name: StepName,
        status: StepStatus,
        embrion_id: Optional[str] = None,
        modelo_consultado: Optional[str] = None,
        input_payload: Optional[Dict[str, Any]] = None,
        output_payload: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Optional[E2EStepLog]:
        row = {
            "run_id": run_id,
            "step_number": step_number,
            "step_name": step_name.value,
            "status": status.value,
            "embrion_id": embrion_id,
            "modelo_consultado": modelo_consultado,
            "input_payload": input_payload,
            "output_payload": output_payload,
            "duration_ms": duration_ms,
            "error_message": error_message,
        }
        # Quitar None para que la DB use defaults donde aplique
        row = {k: v for k, v in row.items() if v is not None}
        result = await self._db.insert(self.TABLE_STEP_LOG, row)
        if not result:
            logger.warning(
                "e2e_step_log_insert_failed",
                run_id=run_id,
                step_number=step_number,
            )
            return None
        return E2EStepLog.model_validate(result)

    async def list_steps_for_run(self, run_id: str) -> List[E2EStepLog]:
        rows = await self._db.select(
            self.TABLE_STEP_LOG,
            filters={"run_id": run_id},
            order_by="step_number",
            order_desc=False,
            limit=200,
        )
        return [E2EStepLog.model_validate(r) for r in rows]
