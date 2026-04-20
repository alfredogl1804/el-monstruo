"""
El Monstruo — Action Validator v2.0
=====================================
Validación de schema, semántica, y reclasificación determinista de ActionEnvelopes.
Diseñado por el Consejo de 6 Sabios (Ciclo 2, 13 abril 2026).

Responsabilidades:
1. Schema validation: campos requeridos, tipos, longitudes
2. Semantic validation: coherencia entre action_type, target, operation
3. Reclasificación: READ→EXECUTE cuando target es API/TOOL/AGENT
4. Risk classification: determinista basada en reglas (no LLM)
5. Trust ring enforcement: basada en actor_type + resource sensitivity

Dependencias: Solo stdlib Python 3.11+ y core/action_envelope.py
"""

from __future__ import annotations

from dataclasses import replace

from core.action_envelope import (
    ActionEnvelope,
    ActionStatus,
    ActionType,
    PolicyDecision,
    ResourceKind,
    RiskLevel,
    TrustRing,
    transition,
)

# ── Validation errors ─────────────────────────────────────────────


class ValidationError(Exception):
    """Error de validación del envelope."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"[{field}] {message}")


class ValidationResult:
    """Resultado acumulativo de validación."""

    __slots__ = ("errors", "warnings", "reclassified")

    def __init__(self):
        self.errors: list[ValidationError] = []
        self.warnings: list[str] = []
        self.reclassified: bool = False

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, field: str, message: str) -> None:
        self.errors.append(ValidationError(field, message))

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


# ── Schema validation ─────────────────────────────────────────────

MAX_INTENT_SUMMARY_LEN = 500
MAX_OPERATION_LEN = 200
MAX_PAYLOAD_SIZE_BYTES = 65_536  # 64KB
MAX_LOCATOR_LEN = 2048


def validate_schema(envelope: ActionEnvelope, result: ValidationResult) -> None:
    """Valida campos requeridos, tipos, y longitudes."""

    # action_id
    if not envelope.action_id or not envelope.action_id.startswith("act_"):
        result.add_error("action_id", "Must start with 'act_' prefix")

    # trace_id
    if not envelope.trace_id:
        result.add_error("trace_id", "Cannot be empty")

    # session_id
    if not envelope.session_id:
        result.add_error("session_id", "Cannot be empty")

    # actor
    if not envelope.actor.actor_id:
        result.add_error("actor.actor_id", "Cannot be empty")
    if envelope.actor.actor_type not in ("user", "agent", "service", "kernel"):
        result.add_error("actor.actor_type", f"Invalid: {envelope.actor.actor_type}")

    # target
    if not envelope.target.resource_id:
        result.add_error("target.resource_id", "Cannot be empty")
    if not envelope.target.locator:
        result.add_error("target.locator", "Cannot be empty")
    if len(envelope.target.locator) > MAX_LOCATOR_LEN:
        result.add_error("target.locator", f"Exceeds max length {MAX_LOCATOR_LEN}")

    # operation
    if not envelope.operation:
        result.add_error("operation", "Cannot be empty")
    if len(envelope.operation) > MAX_OPERATION_LEN:
        result.add_error("operation", f"Exceeds max length {MAX_OPERATION_LEN}")

    # intent_summary
    if not envelope.intent_summary:
        result.add_error("intent_summary", "Cannot be empty")
    if len(envelope.intent_summary) > MAX_INTENT_SUMMARY_LEN:
        result.add_error("intent_summary", f"Exceeds max length {MAX_INTENT_SUMMARY_LEN}")

    # payload size
    import json

    payload_bytes = len(json.dumps(dict(envelope.payload), default=str).encode("utf-8"))
    if payload_bytes > MAX_PAYLOAD_SIZE_BYTES:
        result.add_error("payload", f"Size {payload_bytes}B exceeds max {MAX_PAYLOAD_SIZE_BYTES}B")

    # status must be PROPOSED for new envelopes entering validation
    if envelope.status != ActionStatus.PROPOSED:
        result.add_error("status", f"Expected PROPOSED, got {envelope.status}")

    # timestamps
    if envelope.timestamps.created_at is None:
        result.add_error("timestamps.created_at", "Cannot be None")


# ── Semantic validation + reclassification ────────────────────────

# Operations that imply EXECUTE even when declared as READ
EXECUTE_IMPLYING_OPERATIONS = frozenset(
    {
        "invoke",
        "call",
        "trigger",
        "run",
        "execute",
        "send",
        "post",
        "submit",
        "dispatch",
        "deploy",
        "create",
        "update",
        "delete",
        "mutate",
        "patch",
    }
)

# Resource kinds that trigger READ→EXECUTE reclassification
EXECUTE_RESOURCE_KINDS = frozenset(
    {
        ResourceKind.API,
        ResourceKind.TOOL,
        ResourceKind.AGENT,
    }
)


def validate_semantic(envelope: ActionEnvelope, result: ValidationResult) -> ActionEnvelope:
    """
    Validación semántica + reclasificación determinista.
    Retorna el envelope (posiblemente reclasificado).
    """
    action_type = envelope.action_type
    target = envelope.target
    operation_lower = envelope.operation.lower()

    # ── Reclasificación READ → EXECUTE ────────────────────────────
    if action_type == ActionType.READ:
        # Si el target es API/TOOL/AGENT y la operación implica mutación
        if target.resource_kind in EXECUTE_RESOURCE_KINDS:
            for keyword in EXECUTE_IMPLYING_OPERATIONS:
                if keyword in operation_lower:
                    result.add_warning(
                        f"Reclassified READ→EXECUTE: operation '{envelope.operation}' "
                        f"on {target.resource_kind.value} implies execution"
                    )
                    envelope = replace(envelope, action_type=ActionType.EXECUTE)
                    result.reclassified = True
                    break

    # ── Coherencia action_type vs operation ───────────────────────
    # DELETE debe tener operación que implique eliminación
    if envelope.action_type == ActionType.DELETE:
        delete_keywords = {
            "delete",
            "remove",
            "drop",
            "purge",
            "destroy",
            "clear",
            "erase",
        }
        if not any(kw in operation_lower for kw in delete_keywords):
            result.add_warning(
                f"DELETE action but operation '{envelope.operation}' doesn't contain delete-related keywords"
            )

    # WRITE a SECRET siempre es sensible
    if envelope.action_type in (ActionType.WRITE, ActionType.DELETE) and target.resource_kind == ResourceKind.SECRET:
        if not target.contains_sensitive_data:
            result.add_warning(
                "WRITE/DELETE on SECRET resource but contains_sensitive_data=False. Auto-correcting to True."
            )
            corrected_target = replace(target, contains_sensitive_data=True)
            envelope = replace(envelope, target=corrected_target)

    return envelope


# ── Risk classification (determinista) ────────────────────────────


def classify_risk(envelope: ActionEnvelope) -> RiskLevel:
    """
    Clasificación de riesgo determinista basada en reglas.
    NO usa LLM — solo lógica de negocio.
    """
    target = envelope.target
    action_type = envelope.action_type

    # L3: Siempre sensible
    if target.resource_kind == ResourceKind.SECRET:
        return RiskLevel.L3_SENSITIVE
    if target.contains_sensitive_data and action_type in (
        ActionType.WRITE,
        ActionType.DELETE,
    ):
        return RiskLevel.L3_SENSITIVE
    if action_type == ActionType.DELETE and target.resource_kind in (
        ResourceKind.DB,
        ResourceKind.FILE,
    ):
        return RiskLevel.L3_SENSITIVE
    if target.external_network and action_type == ActionType.EXECUTE:
        return RiskLevel.L3_SENSITIVE

    # L2: Precaución
    if action_type in (ActionType.WRITE, ActionType.EXECUTE):
        return RiskLevel.L2_CAUTION
    if target.external_network:
        return RiskLevel.L2_CAUTION
    if target.contains_sensitive_data and action_type == ActionType.READ:
        return RiskLevel.L2_CAUTION

    # L1: Seguro
    return RiskLevel.L1_SAFE


# ── Trust ring enforcement ────────────────────────────────────────


def enforce_trust_ring(envelope: ActionEnvelope) -> TrustRing:
    """
    Determina el trust ring enforced basado en actor_type + context.
    El actor puede DECLARAR un ring, pero el kernel ENFORCE el real.
    """
    actor = envelope.actor

    # Kernel siempre es R0
    if actor.actor_type == "kernel":
        return TrustRing.R0_KERNEL

    # User delegated (Alfredo via Telegram, API, etc.)
    if actor.actor_type == "user":
        return TrustRing.R2_USER_DELEGATED

    # Agents y services — depende de si el input es untrusted
    if actor.actor_type in ("agent", "service"):
        # Si el payload contiene datos de fuentes externas no verificadas
        if envelope.target.external_network:
            return TrustRing.R3_UNTRUSTED_INPUT
        return TrustRing.R2_USER_DELEGATED

    # Default: untrusted
    return TrustRing.R3_UNTRUSTED_INPUT


# ── HITL determination ────────────────────────────────────────────


def requires_hitl(risk: RiskLevel, trust_ring: TrustRing, action_type: ActionType) -> bool:
    """
    Determina si la acción requiere aprobación humana.
    Reglas deterministas — sin LLM.
    """
    # L3 + cualquier ring no-kernel = HITL
    if risk == RiskLevel.L3_SENSITIVE and trust_ring != TrustRing.R0_KERNEL:
        return True

    # DELETE en DB/FILE siempre requiere HITL (excepto kernel)
    if action_type == ActionType.DELETE and trust_ring != TrustRing.R0_KERNEL:
        return True

    # R3 (untrusted) + L2+ = HITL
    if trust_ring == TrustRing.R3_UNTRUSTED_INPUT and risk != RiskLevel.L1_SAFE:
        return True

    return False


# ── Orchestrator: validate_and_classify ───────────────────────────

POLICY_VERSION = "v2.0.0-sprint1"


def validate_and_classify(
    envelope: ActionEnvelope,
) -> tuple[ActionEnvelope, ValidationResult]:
    """
    Pipeline completo de validación:
    1. Schema validation
    2. Semantic validation + reclasificación
    3. Risk classification
    4. Trust ring enforcement
    5. HITL determination
    6. Transition PROPOSED → VALIDATED → POLICY_CHECKED

    Retorna: (envelope_procesado, validation_result)
    """
    result = ValidationResult()

    # 1. Schema
    validate_schema(envelope, result)
    if not result.is_valid:
        return envelope, result

    # 2. Semantic + reclasificación
    envelope = validate_semantic(envelope, result)

    # 3. Risk
    risk = classify_risk(envelope)

    # 4. Trust ring
    trust_ring = enforce_trust_ring(envelope)

    # 5. HITL
    needs_hitl = requires_hitl(risk, trust_ring, envelope.action_type)

    # 6. Build policy decision
    if needs_hitl:
        decision = "HITL"
        decision_reason = f"Risk={risk.value}, TrustRing={trust_ring.value}, ActionType={envelope.action_type.value}"
    else:
        decision = "ALLOW"
        decision_reason = f"Risk={risk.value}, TrustRing={trust_ring.value} — within safe bounds"

    policy = PolicyDecision(
        enforced_trust_ring=trust_ring,
        risk_level=risk,
        requires_hitl=needs_hitl,
        decision=decision,
        decision_reason=decision_reason,
        policy_version=POLICY_VERSION,
    )

    # 7. Transition: PROPOSED → VALIDATED → POLICY_CHECKED
    envelope = transition(envelope, ActionStatus.VALIDATED)
    envelope = transition(envelope, ActionStatus.POLICY_CHECKED, policy_decision=policy)

    return envelope, result
