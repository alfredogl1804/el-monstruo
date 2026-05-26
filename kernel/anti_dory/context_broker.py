"""
kernel/anti_dory/context_broker.py — Context Broker externo.

Sprint MANUS-ANTI-DORY-002 v1 FASE B.3.
Doctrina §A.5: "El hilo nuevo no nace virgen. Nace con un attachment pack
inyectado ANTES de su primer razonamiento operativo."

Responsabilidad única: dado (project_id, front_id, prompt_usuario), producir
un attachment_pack JSON conforme al contrato ATTACHMENT_OK (SPEC §A.10) que
se PREFIJA al prompt antes de invocar manus_bridge.create_task.

NO toca cowork_runtime. NO toca cowork_guardian (módulos distintos, SRP).

Acoplamiento controlado:
- supabase_client: cliente REST inyectable. v1 acepta Mock para tests offline.
- create_task: wrapper de tools.manus_bridge.create_task, inyectable.
- now_fn: clock inyectable para tests deterministas.

Feature flag: si ANTI_DORY_ENABLED=false, hydrate_prompt() devuelve el prompt
original sin modificación + flag attachment_ok=False (graceful degradation).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional, Protocol

from kernel.anti_dory import ANTI_DORY_ENABLED

logger = logging.getLogger(__name__)


# =============================================================================
# Tipos y protocolos
# =============================================================================


class SupabaseRPCClient(Protocol):
    """Protocolo para cliente RPC Supabase. v1 acepta cualquier implementación
    compatible (httpx-based, supabase-py, mock de tests)."""

    def call_rpc(self, name: str, params: dict[str, Any]) -> Any: ...


@dataclass(frozen=True)
class AttachmentPack:
    """Contrato ATTACHMENT_OK serializado (SPEC §A.10)."""

    attachment_ok: bool
    snapshot_id: Optional[str]
    project_id: str
    front_id: str
    sprint_id: Optional[str]
    phase: Optional[str]
    last_t1_decision: Optional[str]
    next_expected_action: Optional[str]
    do_not_touch: list[Any]
    evidence_refs: list[Any]
    confidence_score: float
    state_hash: Optional[str]
    writer_mode: Optional[str]
    snapshot_age_seconds: Optional[int]
    fallback_reason: Optional[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "attachment_ok": self.attachment_ok,
            "snapshot_id": self.snapshot_id,
            "project_id": self.project_id,
            "front_id": self.front_id,
            "sprint_id": self.sprint_id,
            "phase": self.phase,
            "last_t1_decision": self.last_t1_decision,
            "next_expected_action": self.next_expected_action,
            "do_not_touch": self.do_not_touch,
            "evidence_refs": self.evidence_refs,
            "confidence_score": self.confidence_score,
            "state_hash": self.state_hash,
            "writer_mode": self.writer_mode,
            "snapshot_age_seconds": self.snapshot_age_seconds,
            "fallback_reason": self.fallback_reason,
        }


@dataclass(frozen=True)
class HydratedPrompt:
    """Resultado de hydrate_prompt: prompt prefijado + pack auditable."""

    hydrated_prompt: str
    pack: AttachmentPack


# =============================================================================
# Staleness policy (SPEC §A.6)
# =============================================================================

# Edad máxima de un snapshot accepted antes de considerarlo stale.
STALENESS_THRESHOLD_SECONDS: int = int(
    os.environ.get("ANTI_DORY_STALENESS_SECONDS", "86400")  # 24h default
)

# Confidence mínima para aceptar attachment sin recovery prompt.
CONFIDENCE_MIN_AUTO: float = float(os.environ.get("ANTI_DORY_CONFIDENCE_MIN", "0.75"))


# =============================================================================
# Context Broker
# =============================================================================


class ContextBroker:
    """Hidratador externo del prompt. Externo al agente Manus por diseño.

    Uso típico:
        broker = ContextBroker(rpc_client=client)
        hydrated = broker.hydrate_prompt(
            project_id="el-monstruo",
            front_id="manus-anti-dory-002",
            user_prompt="continuá lo de ayer con El Monstruo; no te reexplico nada.",
        )
        # hydrated.hydrated_prompt ya contiene el ATTACHMENT_OK al inicio.
        # hydrated.pack es serializable a JSON para logging/audit.
    """

    def __init__(
        self,
        rpc_client: SupabaseRPCClient,
        *,
        now_fn: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        enabled: Optional[bool] = None,
    ) -> None:
        self._rpc = rpc_client
        self._now_fn = now_fn
        self._enabled = ANTI_DORY_ENABLED if enabled is None else enabled

    def hydrate_prompt(
        self,
        *,
        project_id: str,
        front_id: str,
        user_prompt: str,
    ) -> HydratedPrompt:
        """Construye un attachment_pack y prefija el prompt.

        Política de fallback:
        - Si feature flag OFF → pack.attachment_ok=False, prompt sin cambios.
        - Si head no existe → pack.attachment_ok=False, fallback_reason='no_head'.
        - Si snapshot stale → pack.attachment_ok=False, fallback_reason='stale'.
        - Si confidence < CONFIDENCE_MIN_AUTO → attachment_ok=False, fallback_reason='low_confidence'.
        - Si RPC falla → pack.attachment_ok=False, fallback_reason='rpc_error:<msg>'.

        En todos los fallback, el prompt NO se modifica (graceful degradation).
        """
        if not self._enabled:
            return HydratedPrompt(
                hydrated_prompt=user_prompt,
                pack=self._empty_pack(project_id, front_id, "feature_flag_off"),
            )

        try:
            rows = self._rpc.call_rpc(
                "rpc_get_context_head",
                {"p_project_id": project_id, "p_front_id": front_id},
            )
        except Exception as exc:  # noqa: BLE001 — graceful degradation
            logger.warning("Anti-Dory rpc_get_context_head failed: %s", exc)
            return HydratedPrompt(
                hydrated_prompt=user_prompt,
                pack=self._empty_pack(project_id, front_id, f"rpc_error:{exc}"),
            )

        head = self._first_row(rows)
        if head is None:
            return HydratedPrompt(
                hydrated_prompt=user_prompt,
                pack=self._empty_pack(project_id, front_id, "no_head"),
            )

        snapshot_age = self._compute_age_seconds(head.get("snapshot_created_at"))
        confidence = float(head.get("confidence_score") or 0.0)

        fallback_reason: Optional[str] = None
        if snapshot_age is not None and snapshot_age > STALENESS_THRESHOLD_SECONDS:
            fallback_reason = "stale"
        elif confidence < CONFIDENCE_MIN_AUTO:
            fallback_reason = "low_confidence"

        pack = AttachmentPack(
            attachment_ok=(fallback_reason is None),
            snapshot_id=str(head.get("snapshot_id")) if head.get("snapshot_id") else None,
            project_id=project_id,
            front_id=front_id,
            sprint_id=head.get("sprint_id"),
            phase=head.get("phase"),
            last_t1_decision=head.get("last_t1_decision"),
            next_expected_action=head.get("next_expected_action"),
            do_not_touch=self._coerce_list(head.get("do_not_touch")),
            evidence_refs=self._coerce_list(head.get("evidence_refs")),
            confidence_score=confidence,
            state_hash=head.get("state_hash"),
            writer_mode=head.get("writer_mode"),
            snapshot_age_seconds=snapshot_age,
            fallback_reason=fallback_reason,
        )

        if pack.attachment_ok:
            prefix = self._render_attachment_prefix(pack)
            hydrated = f"{prefix}\n\n{user_prompt}"
        else:
            hydrated = user_prompt

        return HydratedPrompt(hydrated_prompt=hydrated, pack=pack)

    # ----- helpers -----

    @staticmethod
    def _first_row(rows: Any) -> Optional[dict[str, Any]]:
        if rows is None:
            return None
        if isinstance(rows, list):
            return rows[0] if rows else None
        if isinstance(rows, dict):
            return rows
        return None

    def _compute_age_seconds(self, created_at: Any) -> Optional[int]:
        if created_at is None:
            return None
        if isinstance(created_at, datetime):
            ts = created_at
        else:
            try:
                ts = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
            except ValueError:
                return None
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        delta = self._now_fn() - ts
        return int(delta.total_seconds())

    @staticmethod
    def _coerce_list(val: Any) -> list[Any]:
        if val is None:
            return []
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                return parsed if isinstance(parsed, list) else [parsed]
            except json.JSONDecodeError:
                return [val]
        return [val]

    def _empty_pack(self, project_id: str, front_id: str, reason: str) -> AttachmentPack:
        return AttachmentPack(
            attachment_ok=False,
            snapshot_id=None,
            project_id=project_id,
            front_id=front_id,
            sprint_id=None,
            phase=None,
            last_t1_decision=None,
            next_expected_action=None,
            do_not_touch=[],
            evidence_refs=[],
            confidence_score=0.0,
            state_hash=None,
            writer_mode=None,
            snapshot_age_seconds=None,
            fallback_reason=reason,
        )

    @staticmethod
    def _render_attachment_prefix(pack: AttachmentPack) -> str:
        """Render legible que el agente lee como primer token del prompt."""
        lines = [
            "=== ATTACHMENT_OK (sprint MANUS-ANTI-DORY-002 v1) ===",
            f"project_id: {pack.project_id}",
            f"front_id: {pack.front_id}",
            f"snapshot_id: {pack.snapshot_id}",
            f"sprint_id: {pack.sprint_id}",
            f"phase: {pack.phase}",
            f"last_t1_decision: {pack.last_t1_decision}",
            f"next_expected_action: {pack.next_expected_action}",
            f"do_not_touch: {json.dumps(pack.do_not_touch, ensure_ascii=False)}",
            f"evidence_refs: {json.dumps(pack.evidence_refs, ensure_ascii=False)}",
            f"confidence_score: {pack.confidence_score:.2f}",
            f"state_hash: {pack.state_hash}",
            f"writer_mode: {pack.writer_mode}",
            f"snapshot_age_seconds: {pack.snapshot_age_seconds}",
            "=== END ATTACHMENT_OK ===",
        ]
        return "\n".join(lines)


# =============================================================================
# Hash canónico (SPEC §A.7) — utilidad reusable por writers
# =============================================================================


def canonical_state_hash(payload: dict[str, Any]) -> str:
    """SHA-256 hex del JSON canónico (sort_keys=True, separators compactos).

    Usado por writers para state_hash y por Guardian para verify_attachment_contract.
    """
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
