"""
kernel/anti_dory/guardian.py — Attachment validator (DISTINTO de tools/cowork_guardian).

Sprint MANUS-ANTI-DORY-002 v1 FASE B.5.
Doctrina §A.6: validar el ATTACHMENT_OK antes de razonar.

NO se mezcla con tools/cowork_guardian (que valida outputs Cowork→Alfredo).
Responsabilidades distintas → módulos distintos (SRP).

Función pública: verify_attachment_contract(pack, evidence_verifier) → AttachmentVerdict.

Si verdict.passed=False → callsite debe lanzar HALT_ATTACHMENT_MISMATCH y NO
ejecutar el prompt. El recovery_mode (FASE B.6) toma desde aquí.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from kernel.anti_dory.context_broker import (
    AttachmentPack,
    CONFIDENCE_MIN_AUTO,
    STALENESS_THRESHOLD_SECONDS,
    canonical_state_hash,
)


# =============================================================================
# Excepciones canónicas
# =============================================================================

class HaltAttachmentMismatch(Exception):
    """Halt explícito: el attachment no es seguro de adjuntar.

    El agente NO debe procesar el prompt. Recovery Mode toma control.
    """

    def __init__(self, reason: str, violations: list[str]) -> None:
        super().__init__(f"HALT_ATTACHMENT_MISMATCH: {reason} | violations={violations}")
        self.reason = reason
        self.violations = violations


# =============================================================================
# Verdict
# =============================================================================

@dataclass
class AttachmentVerdict:
    """Resultado de verify_attachment_contract."""

    passed: bool
    violations: list[str] = field(default_factory=list)
    pack: Optional[AttachmentPack] = None
    suggest_recovery: bool = False

    def format_report(self) -> str:
        lines = ["=== ANTI-DORY ATTACHMENT VERDICT ==="]
        lines.append(f"passed: {self.passed}")
        lines.append(f"suggest_recovery: {self.suggest_recovery}")
        if self.pack is not None:
            lines.append(f"project_id: {self.pack.project_id}")
            lines.append(f"front_id: {self.pack.front_id}")
            lines.append(f"snapshot_id: {self.pack.snapshot_id}")
            lines.append(f"confidence_score: {self.pack.confidence_score:.2f}")
            lines.append(f"snapshot_age_seconds: {self.pack.snapshot_age_seconds}")
            lines.append(f"fallback_reason: {self.pack.fallback_reason}")
        if self.violations:
            lines.append("violations:")
            for v in self.violations:
                lines.append(f"  - {v}")
        return "\n".join(lines)


# =============================================================================
# Evidence verifier protocol
# =============================================================================

EvidenceVerifier = Callable[[dict[str, Any]], bool]
"""Callable que verifica que una evidence_ref siga vigente (PR open, commit existe, etc).

v1 acepta una versión simple. Se inyecta para no acoplar el Guardian a
clientes externos (gh CLI, Railway, Supabase) — esos los pone el callsite.
"""


def default_evidence_verifier(_ref: dict[str, Any]) -> bool:
    """Por defecto, asumir que la evidencia sigue vigente.

    Política deliberada v1: el verifier real (gh CLI, curl Railway) se
    inyecta por el callsite. El Guardian solo orquesta validaciones.
    """
    return True


# =============================================================================
# Validador principal
# =============================================================================

def verify_attachment_contract(
    pack: AttachmentPack,
    *,
    evidence_verifier: EvidenceVerifier = default_evidence_verifier,
    require_evidence: bool = False,
) -> AttachmentVerdict:
    """Valida el AttachmentPack contra el contrato ATTACHMENT_OK.

    Reglas v1:
    R1. pack.attachment_ok DEBE ser True (si False, fallback_reason cuenta la historia).
    R2. snapshot_id, state_hash, project_id, front_id no pueden ser None/vacíos.
    R3. confidence_score >= CONFIDENCE_MIN_AUTO.
    R4. snapshot_age_seconds <= STALENESS_THRESHOLD_SECONDS (o None si no aplica).
    R5. do_not_touch debe ser lista (puede estar vacía, pero presente).
    R6. evidence_refs: cada item válido si require_evidence=True.
    R7. writer_mode debe ser de los canónicos.

    Si falla → AttachmentVerdict(passed=False, suggest_recovery=True).
    """
    violations: list[str] = []

    # R1
    if not pack.attachment_ok:
        reason = pack.fallback_reason or "attachment_ok_false"
        violations.append(f"R1:attachment_ok_false:{reason}")

    # R2
    if not pack.snapshot_id:
        violations.append("R2:snapshot_id_missing")
    if not pack.state_hash:
        violations.append("R2:state_hash_missing")
    if not pack.project_id:
        violations.append("R2:project_id_missing")
    if not pack.front_id:
        violations.append("R2:front_id_missing")

    # R3
    if pack.confidence_score < CONFIDENCE_MIN_AUTO:
        violations.append(
            f"R3:confidence_below_min:got={pack.confidence_score:.2f},min={CONFIDENCE_MIN_AUTO:.2f}"
        )

    # R4
    if pack.snapshot_age_seconds is not None and pack.snapshot_age_seconds > STALENESS_THRESHOLD_SECONDS:
        violations.append(
            f"R4:stale:age={pack.snapshot_age_seconds}s,threshold={STALENESS_THRESHOLD_SECONDS}s"
        )

    # R5
    if not isinstance(pack.do_not_touch, list):
        violations.append(f"R5:do_not_touch_not_list:type={type(pack.do_not_touch).__name__}")

    # R6
    if require_evidence and pack.evidence_refs:
        for idx, ref in enumerate(pack.evidence_refs):
            if isinstance(ref, dict):
                if not evidence_verifier(ref):
                    violations.append(f"R6:evidence_invalid:index={idx},ref={ref}")
            else:
                violations.append(f"R6:evidence_not_dict:index={idx},type={type(ref).__name__}")

    # R7
    valid_writer_modes = {
        "explicit_start", "explicit_transition", "explicit_artifact",
        "explicit_final", "heartbeat", "external_polling", "recovery_scan",
    }
    if pack.writer_mode and pack.writer_mode not in valid_writer_modes:
        violations.append(f"R7:invalid_writer_mode:{pack.writer_mode}")

    passed = len(violations) == 0
    return AttachmentVerdict(
        passed=passed,
        violations=violations,
        pack=pack,
        suggest_recovery=(not passed),
    )


# =============================================================================
# Helper: verify_state_hash (integridad)
# =============================================================================

def verify_state_hash(pack: AttachmentPack, reconstructed_payload: dict[str, Any]) -> bool:
    """Recalcula hash desde payload reconstruido y compara contra pack.state_hash.

    Uso típico: Guardian llama esto cuando el writer expone el payload usado
    para construir el hash (ej. desde runtime_events).
    """
    if not pack.state_hash:
        return False
    expected = canonical_state_hash(reconstructed_payload)
    return expected == pack.state_hash
