"""
kernel/anti_dory/writers.py — 3 Writers del black-box recorder.

Sprint MANUS-ANTI-DORY-002 v1 FASE B.4.
Doctrina §A.7 (Snapshot Writer Incremental).

Tres writers DESACOPLADOS por diseño:

1. AgentExplicitWriter — invocado por el agente activo. 4 modos:
   - write_on_start       → al iniciar sesión (writer_mode='explicit_start')
   - write_on_transition  → en cambio de fase (writer_mode='explicit_transition')
   - write_on_artifact    → tras crear PR/commit/file relevante (event-only)
   - write_on_final       → al cierre limpio (writer_mode='explicit_final')

2. HeartbeatWriter — INDEPENDIENTE del agente (cron Railway o similar).
   GPT-5.5 Pro: "el black-box recorder NO puede depender del agente."
   Corre cada 10-15min. Escribe snapshot tipo 'heartbeat' con estado reciente
   reconstruido desde runtime_events. Si el agente crashea, este writer
   sigue produciendo snapshots útiles para recovery.

3. ExternalPollingWriter — wrapper para sistemas externos (CI, Railway hooks,
   GitHub webhooks) que emiten eventos sin razonar como agente. Solo escribe
   runtime_events; nunca thread_snapshots directamente.

Todos los writers usan los RPCs canónicos de migration 0032:
- rpc_write_runtime_event
- rpc_write_thread_snapshot
- rpc_accept_snapshot (solo en write_on_start y write_on_final por defecto)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from kernel.anti_dory.context_broker import SupabaseRPCClient, canonical_state_hash

logger = logging.getLogger(__name__)


# =============================================================================
# Tipos compartidos
# =============================================================================


@dataclass(frozen=True)
class WriteResult:
    """Resultado canónico de cualquier escritura. event_id y/o snapshot_id."""

    event_id: Optional[str] = None
    snapshot_id: Optional[str] = None
    accepted: bool = False
    lock_version: Optional[int] = None
    error: Optional[str] = None


# =============================================================================
# 1. AgentExplicitWriter — 4 modos. SPEC §A.7 patch obligatorio.
# =============================================================================


class AgentExplicitWriter:
    """Writer invocado por el agente activo (Manus, Cowork, Embrion).

    NO es independiente: si el agente crashea entre write_on_start y
    write_on_final, los snapshots faltantes los repone HeartbeatWriter.
    """

    def __init__(self, rpc_client: SupabaseRPCClient, *, actor_type: str = "manus") -> None:
        if actor_type not in ("manus", "cowork", "embrion", "system"):
            raise ValueError(f"AgentExplicitWriter: invalid actor_type={actor_type}")
        self._rpc = rpc_client
        self._actor_type = actor_type

    # ----- Mode 1: write_on_start -----
    def write_on_start(
        self,
        *,
        project_id: str,
        front_id: str,
        sprint_id: Optional[str] = None,
        phase: Optional[str] = None,
        last_t1_decision: Optional[str] = None,
        next_expected_action: Optional[str] = None,
        do_not_touch: Optional[list[Any]] = None,
        evidence_refs: Optional[list[Any]] = None,
        confidence_score: float = 1.0,
        thread_id: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> WriteResult:
        """Inicio de sesión. INSERT runtime_events + thread_snapshots (start).

        NO promueve a accepted (eso lo decide rpc_accept_snapshot en write_on_final
        o ante transición explícita). Política deliberada: snapshots intermedios
        son 'pending' hasta consolidarse al cierre.
        """
        payload = {
            "project_id": project_id,
            "front_id": front_id,
            "sprint_id": sprint_id,
            "phase": phase,
            "last_t1_decision": last_t1_decision,
            "next_expected_action": next_expected_action,
            "do_not_touch": do_not_touch or [],
            "evidence_refs": evidence_refs or [],
            "writer_mode": "explicit_start",
            "actor_type": self._actor_type,
        }
        state_hash = canonical_state_hash(payload)

        snapshot_id = self._rpc_write_snapshot(
            project_id=project_id,
            front_id=front_id,
            state_hash=state_hash,
            writer_mode="explicit_start",
            parent_snapshot_id=None,
            sprint_id=sprint_id,
            phase=phase,
            last_t1_decision=last_t1_decision,
            next_expected_action=next_expected_action,
            do_not_touch=do_not_touch or [],
            evidence_refs=evidence_refs or [],
            confidence_score=confidence_score,
            summary=summary,
        )

        event_id = self._rpc_write_event(
            project_id=project_id,
            front_id=front_id,
            event_type="session_started",
            payload=payload,
            thread_id=thread_id,
            snapshot_id=snapshot_id,
        )

        return WriteResult(event_id=event_id, snapshot_id=snapshot_id)

    # ----- Mode 2: write_on_transition -----
    def write_on_transition(
        self,
        *,
        parent_snapshot_id: str,
        project_id: str,
        front_id: str,
        new_phase: str,
        previous_phase: Optional[str] = None,
        last_t1_decision: Optional[str] = None,
        next_expected_action: Optional[str] = None,
        do_not_touch: Optional[list[Any]] = None,
        evidence_refs: Optional[list[Any]] = None,
        confidence_score: float = 1.0,
        thread_id: Optional[str] = None,
        summary: Optional[str] = None,
        sprint_id: Optional[str] = None,
    ) -> WriteResult:
        """Cambio de fase (audit→spec, spec→impl, etc.). Crea snapshot hijo."""
        payload = {
            "project_id": project_id,
            "front_id": front_id,
            "previous_phase": previous_phase,
            "new_phase": new_phase,
            "last_t1_decision": last_t1_decision,
            "next_expected_action": next_expected_action,
            "do_not_touch": do_not_touch or [],
            "evidence_refs": evidence_refs or [],
            "writer_mode": "explicit_transition",
            "actor_type": self._actor_type,
            "parent_snapshot_id": parent_snapshot_id,
        }
        state_hash = canonical_state_hash(payload)

        snapshot_id = self._rpc_write_snapshot(
            project_id=project_id,
            front_id=front_id,
            state_hash=state_hash,
            writer_mode="explicit_transition",
            parent_snapshot_id=parent_snapshot_id,
            sprint_id=sprint_id,
            phase=new_phase,
            last_t1_decision=last_t1_decision,
            next_expected_action=next_expected_action,
            do_not_touch=do_not_touch or [],
            evidence_refs=evidence_refs or [],
            confidence_score=confidence_score,
            summary=summary,
        )

        event_id = self._rpc_write_event(
            project_id=project_id,
            front_id=front_id,
            event_type="phase_transition",
            payload=payload,
            thread_id=thread_id,
            snapshot_id=snapshot_id,
        )

        return WriteResult(event_id=event_id, snapshot_id=snapshot_id)

    # ----- Mode 3: write_on_artifact (event-only, NO crea snapshot) -----
    def write_on_artifact(
        self,
        *,
        snapshot_id: str,
        project_id: str,
        front_id: str,
        artifact_path: str,
        artifact_type: str,
        artifact_ref: Optional[str] = None,
        thread_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> WriteResult:
        """Tras crear/modificar artifact (PR, commit, migration, módulo).

        Por diseño, NO crea snapshot (sería ruido). Solo append a runtime_events.
        Si HeartbeatWriter detecta acumulación de artifact events, puede
        consolidar en snapshot heartbeat con state_hash actualizado.
        """
        payload = {
            "snapshot_id": snapshot_id,
            "artifact_path": artifact_path,
            "artifact_type": artifact_type,
            "artifact_ref": artifact_ref,
            "metadata": metadata or {},
            "writer_mode": "explicit_artifact",
            "actor_type": self._actor_type,
        }

        event_id = self._rpc_write_event(
            project_id=project_id,
            front_id=front_id,
            event_type="artifact_created",
            payload=payload,
            thread_id=thread_id,
            snapshot_id=snapshot_id,
        )

        return WriteResult(event_id=event_id, snapshot_id=snapshot_id)

    # ----- Mode 4: write_on_final (consolida + acepta) -----
    def write_on_final(
        self,
        *,
        parent_snapshot_id: str,
        project_id: str,
        front_id: str,
        exit_status: str,
        summary: str,
        last_t1_decision: Optional[str] = None,
        next_expected_action: Optional[str] = None,
        do_not_touch: Optional[list[Any]] = None,
        evidence_refs: Optional[list[Any]] = None,
        confidence_score: float = 1.0,
        thread_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        phase: Optional[str] = None,
        expected_lock_version: int = 0,
    ) -> WriteResult:
        """Cierre limpio. Crea snapshot final + intenta accept_snapshot (CAS).

        Si CAS falla (otro writer ya promovió un head distinto), retornamos
        accepted=False con error y NO superseamos. Es decisión consciente:
        un cierre conflictivo debe escalarse al humano, no hacer merge.
        """
        if exit_status not in ("ok", "warn", "error", "user_stop"):
            raise ValueError(f"write_on_final: invalid exit_status={exit_status}")

        payload = {
            "project_id": project_id,
            "front_id": front_id,
            "exit_status": exit_status,
            "summary": summary,
            "last_t1_decision": last_t1_decision,
            "next_expected_action": next_expected_action,
            "do_not_touch": do_not_touch or [],
            "evidence_refs": evidence_refs or [],
            "writer_mode": "explicit_final",
            "actor_type": self._actor_type,
            "parent_snapshot_id": parent_snapshot_id,
        }
        state_hash = canonical_state_hash(payload)

        snapshot_id = self._rpc_write_snapshot(
            project_id=project_id,
            front_id=front_id,
            state_hash=state_hash,
            writer_mode="explicit_final",
            parent_snapshot_id=parent_snapshot_id,
            sprint_id=sprint_id,
            phase=phase,
            last_t1_decision=last_t1_decision,
            next_expected_action=next_expected_action,
            do_not_touch=do_not_touch or [],
            evidence_refs=evidence_refs or [],
            confidence_score=confidence_score,
            summary=summary,
        )

        event_id = self._rpc_write_event(
            project_id=project_id,
            front_id=front_id,
            event_type="session_final",
            payload=payload,
            thread_id=thread_id,
            snapshot_id=snapshot_id,
        )

        # CAS sobre heads. Si falla → escalado al humano (no merge automático).
        accept_result = self._rpc_accept(
            project_id=project_id,
            front_id=front_id,
            snapshot_id=snapshot_id,
            expected_lock_version=expected_lock_version,
        )

        return WriteResult(
            event_id=event_id,
            snapshot_id=snapshot_id,
            accepted=accept_result.get("accepted", False),
            lock_version=accept_result.get("new_lock_version"),
            error=accept_result.get("conflict_reason"),
        )

    # ----- helpers RPC -----

    def _rpc_write_event(self, **kwargs: Any) -> str:
        params = {
            "p_project_id": kwargs["project_id"],
            "p_front_id": kwargs["front_id"],
            "p_actor_type": self._actor_type,
            "p_event_type": kwargs["event_type"],
            "p_payload": kwargs.get("payload") or {},
            "p_thread_id": kwargs.get("thread_id"),
            "p_snapshot_id": kwargs.get("snapshot_id"),
        }
        result = self._rpc.call_rpc("rpc_write_runtime_event", params)
        return _coerce_uuid(result)

    def _rpc_write_snapshot(self, **kwargs: Any) -> str:
        params = {
            "p_project_id": kwargs["project_id"],
            "p_front_id": kwargs["front_id"],
            "p_actor_type": self._actor_type,
            "p_state_hash": kwargs["state_hash"],
            "p_writer_mode": kwargs["writer_mode"],
            "p_parent_snapshot_id": kwargs.get("parent_snapshot_id"),
            "p_sprint_id": kwargs.get("sprint_id"),
            "p_phase": kwargs.get("phase"),
            "p_last_t1_decision": kwargs.get("last_t1_decision"),
            "p_next_expected_action": kwargs.get("next_expected_action"),
            "p_do_not_touch": kwargs.get("do_not_touch") or [],
            "p_evidence_refs": kwargs.get("evidence_refs") or [],
            "p_confidence_score": kwargs.get("confidence_score", 1.0),
            "p_summary": kwargs.get("summary"),
        }
        result = self._rpc.call_rpc("rpc_write_thread_snapshot", params)
        return _coerce_uuid(result)

    def _rpc_accept(self, **kwargs: Any) -> dict[str, Any]:
        params = {
            "p_project_id": kwargs["project_id"],
            "p_front_id": kwargs["front_id"],
            "p_snapshot_id": kwargs["snapshot_id"],
            "p_expected_lock_version": kwargs["expected_lock_version"],
        }
        rows = self._rpc.call_rpc("rpc_accept_snapshot", params)
        if isinstance(rows, list) and rows:
            return rows[0]
        if isinstance(rows, dict):
            return rows
        return {"accepted": False, "conflict_reason": "unknown_rpc_response_shape"}


# =============================================================================
# 2. HeartbeatWriter — INDEPENDIENTE del agente.
# =============================================================================


class HeartbeatWriter:
    """Black-box recorder externo. Corre vía cron (Railway o similar).

    Independencia crítica: este writer NO requiere que el agente esté vivo.
    Si el agente crashea, este writer sigue tomando snapshots útiles para
    recovery basados en runtime_events recientes.

    Frecuencia recomendada: cada 10-15 minutos.
    Deploy: cron job en Railway invoca `python -m kernel.anti_dory.cli heartbeat`.
    El cron está fuera del scope de v1 — v1 deja la clase lista y un CLI.
    """

    def __init__(self, rpc_client: SupabaseRPCClient, *, actor_type: str = "system") -> None:
        self._rpc = rpc_client
        self._actor_type = actor_type

    def tick(
        self,
        *,
        project_id: str,
        front_id: str,
    ) -> WriteResult:
        """Una iteración del heartbeat. Lee último evento + total + escribe snapshot."""
        try:
            recovery_rows = self._rpc.call_rpc(
                "rpc_recovery_scan",
                {"p_project_id": project_id, "p_front_id": front_id},
            )
        except Exception as exc:  # noqa: BLE001 — graceful
            logger.warning("HeartbeatWriter.rpc_recovery_scan failed: %s", exc)
            return WriteResult(error=f"rpc_recovery_scan:{exc}")

        recovery = self._first_row(recovery_rows)
        if recovery is None or recovery.get("event_count", 0) == 0:
            # No hay eventos para este front → nada que recordar.
            return WriteResult(error="no_events")

        payload = {
            "project_id": project_id,
            "front_id": front_id,
            "last_event_id": str(recovery.get("last_event_id")) if recovery.get("last_event_id") else None,
            "last_event_type": recovery.get("last_event_type"),
            "last_actor_type": recovery.get("last_actor_type"),
            "event_count": int(recovery.get("event_count") or 0),
            "writer_mode": "heartbeat",
        }
        state_hash = canonical_state_hash(payload)

        snapshot_id = self._rpc_write_snapshot(
            project_id=project_id,
            front_id=front_id,
            state_hash=state_hash,
            writer_mode="heartbeat",
            summary=f"heartbeat after {payload['event_count']} events",
            confidence_score=0.60,  # heartbeats tienen confianza media
        )

        event_id = self._rpc.call_rpc(
            "rpc_write_runtime_event",
            {
                "p_project_id": project_id,
                "p_front_id": front_id,
                "p_actor_type": self._actor_type,
                "p_event_type": "heartbeat",
                "p_payload": payload,
                "p_thread_id": None,
                "p_snapshot_id": snapshot_id,
            },
        )

        return WriteResult(
            event_id=_coerce_uuid(event_id),
            snapshot_id=snapshot_id,
            accepted=False,
            lock_version=None,
            error=None,
        )

    def _rpc_write_snapshot(self, **kwargs: Any) -> str:
        params = {
            "p_project_id": kwargs["project_id"],
            "p_front_id": kwargs["front_id"],
            "p_actor_type": self._actor_type,
            "p_state_hash": kwargs["state_hash"],
            "p_writer_mode": kwargs["writer_mode"],
            "p_confidence_score": kwargs.get("confidence_score", 0.6),
            "p_summary": kwargs.get("summary"),
        }
        result = self._rpc.call_rpc("rpc_write_thread_snapshot", params)
        return _coerce_uuid(result)

    @staticmethod
    def _first_row(rows: Any) -> Optional[dict[str, Any]]:
        if isinstance(rows, list) and rows:
            return rows[0]
        if isinstance(rows, dict):
            return rows
        return None


# =============================================================================
# 3. ExternalPollingWriter — eventos externos (CI, webhooks)
# =============================================================================


class ExternalPollingWriter:
    """Wrapper para sistemas externos que emiten eventos sin razonar como agente.

    Solo escribe runtime_events. Nunca thread_snapshots directamente.
    HeartbeatWriter consolida estos eventos en snapshots heartbeat.
    """

    def __init__(self, rpc_client: SupabaseRPCClient) -> None:
        self._rpc = rpc_client

    def write_external_event(
        self,
        *,
        project_id: str,
        front_id: str,
        source: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> WriteResult:
        full_payload = {**payload, "external_source": source, "writer_mode": "external_polling"}
        event_id = self._rpc.call_rpc(
            "rpc_write_runtime_event",
            {
                "p_project_id": project_id,
                "p_front_id": front_id,
                "p_actor_type": "system",
                "p_event_type": event_type,
                "p_payload": full_payload,
                "p_thread_id": None,
                "p_snapshot_id": None,
            },
        )
        return WriteResult(event_id=_coerce_uuid(event_id))


# =============================================================================
# Utilidades privadas
# =============================================================================


def _coerce_uuid(val: Any) -> str:
    """Extrae UUID string de cualquier shape razonable de respuesta RPC."""
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    if isinstance(val, UUID):
        return str(val)
    if isinstance(val, dict):
        # Postgres a veces devuelve {"rpc_write_runtime_event": "uuid"} u otra envoltura.
        for v in val.values():
            if isinstance(v, (str, UUID)):
                return str(v)
        return ""
    if isinstance(val, list) and val:
        return _coerce_uuid(val[0])
    return str(val)
