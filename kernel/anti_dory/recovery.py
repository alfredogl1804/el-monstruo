"""
kernel/anti_dory/recovery.py — Recovery Mode.

Sprint MANUS-ANTI-DORY-002 v1 FASE B.6.
Doctrina §A.9: cuando Guardian devuelve HALT_ATTACHMENT_MISMATCH, el agente
NO debe pedir reexplicación humana extensa. Solo formula UNA pregunta binaria
(Sí/No) sobre la mejor reconstrucción disponible.

Frase canónica permitida:
    "Encontré snapshot X con confianza 0.YY. ¿Retomo desde ahí? Sí/No."

Frases PROHIBIDAS:
- "¿Dónde nos quedamos?"
- "¿Puedes recordarme el contexto?"
- "¿Qué frente activo tenemos?"

Funcionamiento:
1. Llama rpc_recovery_scan + rpc_get_context_head para reconstruir candidato.
2. Si hay candidato → formula pregunta binaria con confidence_score.
3. Si no hay candidato → declara HARD_FAILURE explícito (cuenta como
   evidencia de que ni heartbeat estaba escribiendo). No inventa nada.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from kernel.anti_dory.context_broker import (
    AttachmentPack,
    SupabaseRPCClient,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Resultado
# =============================================================================


@dataclass(frozen=True)
class RecoveryProposal:
    """Resultado de attempt_recovery. Decide si pregunta binaria o hard failure."""

    has_candidate: bool
    binary_question: Optional[str]  # solo si has_candidate=True
    candidate_pack: Optional[AttachmentPack]
    hard_failure_reason: Optional[str]  # solo si has_candidate=False
    scan_payload: dict[str, Any]


# =============================================================================
# Recovery Mode
# =============================================================================


class RecoveryMode:
    """Orquestador del recovery cuando Guardian falla.

    Uso típico:
        recovery = RecoveryMode(rpc_client=client)
        proposal = recovery.attempt_recovery(project_id=..., front_id=...)
        if proposal.has_candidate:
            answer = ask_user(proposal.binary_question)  # solo Sí/No
            if answer == "si":
                # re-hidratar con candidate_pack y continuar
                ...
        else:
            # HARD_FAILURE: declarar imposibilidad y parar.
            raise RuntimeError(proposal.hard_failure_reason)
    """

    def __init__(self, rpc_client: SupabaseRPCClient) -> None:
        self._rpc = rpc_client

    def attempt_recovery(
        self,
        *,
        project_id: str,
        front_id: str,
    ) -> RecoveryProposal:
        """Escanea runtime_events + heads y propone candidato si existe."""
        try:
            scan_rows = self._rpc.call_rpc(
                "rpc_recovery_scan",
                {"p_project_id": project_id, "p_front_id": front_id},
            )
        except Exception as exc:  # noqa: BLE001 — graceful
            logger.warning("RecoveryMode.rpc_recovery_scan failed: %s", exc)
            return RecoveryProposal(
                has_candidate=False,
                binary_question=None,
                candidate_pack=None,
                hard_failure_reason=f"rpc_recovery_scan_error:{exc}",
                scan_payload={},
            )

        scan = self._first_row(scan_rows)
        if scan is None or int(scan.get("event_count") or 0) == 0:
            return RecoveryProposal(
                has_candidate=False,
                binary_question=None,
                candidate_pack=None,
                hard_failure_reason="no_events_in_runtime_events_for_this_front",
                scan_payload=scan or {},
            )

        # Hay eventos: intentar leer head canónico.
        try:
            head_rows = self._rpc.call_rpc(
                "rpc_get_context_head",
                {"p_project_id": project_id, "p_front_id": front_id},
            )
        except Exception as exc:  # noqa: BLE001 — graceful
            logger.warning("RecoveryMode.rpc_get_context_head failed: %s", exc)
            head_rows = None

        head = self._first_row(head_rows) if head_rows else None

        if head is None:
            # Eventos sí, pero no hay head canónico (snapshots no se promovieron
            # o no se llamó rpc_accept_snapshot). Esto es señal de que el agente
            # crasheó antes del write_on_final. Heartbeats producen snapshots
            # 'pending' que rpc_recovery_scan puede mostrar como last_pending.
            last_pending = scan.get("last_pending_snapshot_id")
            if last_pending:
                pack = AttachmentPack(
                    attachment_ok=False,  # passed=False, va a pregunta binaria
                    snapshot_id=str(last_pending),
                    project_id=project_id,
                    front_id=front_id,
                    sprint_id=scan.get("last_sprint_id"),
                    phase=scan.get("last_phase"),
                    last_t1_decision=None,
                    next_expected_action=None,
                    do_not_touch=[],
                    evidence_refs=[],
                    confidence_score=float(scan.get("last_confidence") or 0.5),
                    state_hash=scan.get("last_state_hash"),
                    writer_mode="recovery_scan",
                    snapshot_age_seconds=int(scan.get("last_age_seconds") or 0)
                    if scan.get("last_age_seconds") is not None
                    else None,
                    fallback_reason="recovery_pending_snapshot",
                )
                question = self._format_binary_question(pack)
                return RecoveryProposal(
                    has_candidate=True,
                    binary_question=question,
                    candidate_pack=pack,
                    hard_failure_reason=None,
                    scan_payload=scan,
                )

            return RecoveryProposal(
                has_candidate=False,
                binary_question=None,
                candidate_pack=None,
                hard_failure_reason="events_exist_but_no_snapshot_pending_nor_head",
                scan_payload=scan,
            )

        # Head canónico existe: armar candidato con head + datos del scan.
        pack = AttachmentPack(
            attachment_ok=False,  # passed=False forza pregunta binaria
            snapshot_id=str(head.get("snapshot_id")) if head.get("snapshot_id") else None,
            project_id=project_id,
            front_id=front_id,
            sprint_id=head.get("sprint_id"),
            phase=head.get("phase"),
            last_t1_decision=head.get("last_t1_decision"),
            next_expected_action=head.get("next_expected_action"),
            do_not_touch=self._coerce_list(head.get("do_not_touch")),
            evidence_refs=self._coerce_list(head.get("evidence_refs")),
            confidence_score=float(head.get("confidence_score") or 0.5),
            state_hash=head.get("state_hash"),
            writer_mode="recovery_scan",
            snapshot_age_seconds=int(head.get("snapshot_age_seconds") or 0)
            if head.get("snapshot_age_seconds") is not None
            else None,
            fallback_reason="recovery_head_below_threshold",
        )

        question = self._format_binary_question(pack)
        return RecoveryProposal(
            has_candidate=True,
            binary_question=question,
            candidate_pack=pack,
            hard_failure_reason=None,
            scan_payload=scan,
        )

    # ----- helpers -----

    @staticmethod
    def _format_binary_question(pack: AttachmentPack) -> str:
        """Construye la frase canónica permitida."""
        snap_short = (pack.snapshot_id or "?")[:8]
        front = pack.front_id or "?"
        phase = pack.phase or "?"
        conf = pack.confidence_score
        return (
            f"Encontré snapshot {snap_short} (front={front}, fase={phase}) "
            f"con confianza {conf:.2f}. ¿Retomo desde ahí? Sí/No."
        )

    @staticmethod
    def _first_row(rows: Any) -> Optional[dict[str, Any]]:
        if isinstance(rows, list) and rows:
            return rows[0]
        if isinstance(rows, dict):
            return rows
        return None

    @staticmethod
    def _coerce_list(val: Any) -> list[Any]:
        if val is None:
            return []
        if isinstance(val, list):
            return val
        return [val]
