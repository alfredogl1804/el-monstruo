"""
El Monstruo — Action Envelope v2.0
====================================
Contrato canónico de gobernanza para TODAS las acciones del kernel.
Diseñado por el Consejo de 6 Sabios (Ciclo 2, 13 abril 2026).

Principios rectores:
1. El envelope transporta intención + metadatos verificables
2. Campos sensibles (risk, trust_ring, requires_hitl) los calcula el kernel — NUNCA el actor
3. No hay blobs opacos — todo es tipado y determinista
4. Lifecycle cerrado con transiciones explícitas
5. Idempotencia scoped por (actor_id, trace_id, action_fingerprint)

Dependencias: Solo stdlib Python 3.11+ (dataclasses, enum, uuid, hashlib, json, datetime)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any, Mapping
from uuid import uuid4

# ── Utilidades ────────────────────────────────────────────────────


def utcnow() -> datetime:
    """Timestamp UTC timezone-aware."""
    return datetime.now(timezone.utc)


def canonical_json(data: Any) -> str:
    """JSON canónico determinista para hashing."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def sha256_str(value: str) -> str:
    """SHA-256 hex digest de un string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normaliza payload a dict determinista."""
    return json.loads(canonical_json(payload))


# ── Enums ─────────────────────────────────────────────────────────


class ActionType(StrEnum):
    """4 tipos de acción canónicos. MEMORY es ResourceKind, no ActionType."""

    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    EXECUTE = "EXECUTE"


class RiskLevel(StrEnum):
    """3 niveles de riesgo. L4 diferido para Sprint 2+."""

    L1_SAFE = "L1_SAFE"
    L2_CAUTION = "L2_CAUTION"
    L3_SENSITIVE = "L3_SENSITIVE"


class TrustRing(StrEnum):
    """3 anillos de confianza. R1 diferido para Sprint 2+."""

    R0_KERNEL = "R0_KERNEL"
    R2_USER_DELEGATED = "R2_USER_DELEGATED"
    R3_UNTRUSTED_INPUT = "R3_UNTRUSTED_INPUT"


class ActionStatus(StrEnum):
    """Lifecycle cerrado — sin strings libres."""

    PROPOSED = "PROPOSED"
    VALIDATED = "VALIDATED"
    POLICY_CHECKED = "POLICY_CHECKED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class ResourceKind(StrEnum):
    """Tipos de recurso target. MEMORY es recurso, no acción."""

    FILE = "FILE"
    DB = "DB"
    API = "API"
    TOOL = "TOOL"
    AGENT = "AGENT"
    MEMORY = "MEMORY"
    SECRET = "SECRET"
    OTHER = "OTHER"


# ── Tipos estructurados ──────────────────────────────────────────


@dataclass(slots=True, frozen=True)
class ActorRef:
    """Referencia al actor que propone la acción."""

    actor_id: str
    actor_type: str  # "user" | "agent" | "service" | "kernel"
    declared_trust_ring: TrustRing | None = None


@dataclass(slots=True, frozen=True)
class ResourceRef:
    """Referencia al recurso target de la acción."""

    resource_kind: ResourceKind
    resource_id: str
    locator: str
    owner: str | None = None
    contains_sensitive_data: bool = False
    external_network: bool = False


@dataclass(slots=True, frozen=True)
class EnvelopeTimestamps:
    """Timestamps del lifecycle del envelope."""

    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None


@dataclass(slots=True, frozen=True)
class PolicyDecision:
    """Decisión sellada por el policy engine — NUNCA editable por el actor."""

    enforced_trust_ring: TrustRing
    risk_level: RiskLevel
    requires_hitl: bool
    decision: str  # "ALLOW" | "DENY" | "HITL"
    decision_reason: str
    policy_version: str


# ── Action Envelope v2.0 ─────────────────────────────────────────


@dataclass(slots=True, frozen=True)
class ActionEnvelope:
    """
    Contrato universal de gobernanza del Monstruo.
    Frozen (inmutable) — las transiciones crean nuevas instancias via replace().
    """

    # Identidad
    action_id: str
    trace_id: str
    session_id: str
    parent_action_id: str | None

    # Intención declarada
    actor: ActorRef
    action_type: ActionType
    target: ResourceRef
    operation: str
    payload: Mapping[str, Any]
    intent_summary: str

    # Integridad / deduplicación
    idempotency_scope: str
    idempotency_key: str
    action_fingerprint: str
    semantic_continuity_hash: str | None

    # Estado
    status: ActionStatus

    # Derivados sellados por kernel/policy
    policy_decision: PolicyDecision | None

    # Metadata temporal
    timestamps: EnvelopeTimestamps


# ── Lifecycle transitions ─────────────────────────────────────────

# Mapa de transiciones válidas: status_actual -> set de status_destino
VALID_TRANSITIONS: dict[ActionStatus, set[ActionStatus]] = {
    ActionStatus.PROPOSED: {ActionStatus.VALIDATED},
    ActionStatus.VALIDATED: {ActionStatus.POLICY_CHECKED},
    ActionStatus.POLICY_CHECKED: {
        ActionStatus.AWAITING_APPROVAL,
        ActionStatus.BLOCKED,
        ActionStatus.EXECUTING,
    },
    ActionStatus.AWAITING_APPROVAL: {
        ActionStatus.APPROVED,
        ActionStatus.REJECTED,
        ActionStatus.EXPIRED,
    },
    ActionStatus.APPROVED: {ActionStatus.EXECUTING},
    ActionStatus.EXECUTING: {
        ActionStatus.SUCCEEDED,
        ActionStatus.FAILED,
    },
    # Terminal states — no transitions
    ActionStatus.REJECTED: set(),
    ActionStatus.BLOCKED: set(),
    ActionStatus.SUCCEEDED: set(),
    ActionStatus.FAILED: set(),
    ActionStatus.EXPIRED: set(),
}

TERMINAL_STATUSES = {
    ActionStatus.REJECTED,
    ActionStatus.BLOCKED,
    ActionStatus.SUCCEEDED,
    ActionStatus.FAILED,
    ActionStatus.EXPIRED,
}


class InvalidTransitionError(Exception):
    """Transición de estado inválida."""

    pass


def transition(envelope: ActionEnvelope, new_status: ActionStatus, **overrides: Any) -> ActionEnvelope:
    """
    Transiciona un envelope a un nuevo estado.
    Valida que la transición sea legal. Actualiza updated_at.
    Retorna un NUEVO envelope (frozen dataclass).
    """
    valid = VALID_TRANSITIONS.get(envelope.status, set())
    if new_status not in valid:
        raise InvalidTransitionError(f"Transición inválida: {envelope.status} -> {new_status}. Válidas: {valid}")

    now = utcnow()
    new_timestamps = replace(envelope.timestamps, updated_at=now)

    return replace(
        envelope,
        status=new_status,
        timestamps=new_timestamps,
        **overrides,
    )


# ── Builder functions ─────────────────────────────────────────────


def build_action_fingerprint(
    action_type: ActionType,
    target: ResourceRef,
    operation: str,
    payload: Mapping[str, Any],
) -> str:
    """Fingerprint semántico de la acción para idempotencia."""
    material = canonical_json(
        {
            "action_type": action_type.value,
            "target": {
                "resource_kind": target.resource_kind.value,
                "resource_id": target.resource_id,
                "locator": target.locator,
            },
            "operation": operation,
            "payload": normalize_payload(payload),
        }
    )
    return sha256_str(material)


def build_idempotency(
    actor_id: str,
    trace_id: str,
    action_fingerprint: str,
) -> tuple[str, str]:
    """
    Construye scope e idempotency key.
    Scope: {actor_id}:{trace_id}
    Key: sha256(scope:fingerprint)
    """
    scope = f"{actor_id}:{trace_id}"
    key = sha256_str(f"{scope}:{action_fingerprint}")
    return scope, key


def create_envelope(
    *,
    session_id: str,
    trace_id: str,
    actor: ActorRef,
    action_type: ActionType,
    target: ResourceRef,
    operation: str,
    payload: Mapping[str, Any],
    intent_summary: str,
    parent_action_id: str | None = None,
    expires_in_seconds: int | None = 900,
) -> ActionEnvelope:
    """
    Factory canónica para crear un ActionEnvelope en estado PROPOSED.
    Este es el ÚNICO punto de entrada para crear envelopes.
    """
    now = utcnow()
    fp = build_action_fingerprint(action_type, target, operation, payload)
    scope, idem_key = build_idempotency(actor.actor_id, trace_id, fp)

    return ActionEnvelope(
        action_id=f"act_{uuid4().hex[:16]}",
        trace_id=trace_id,
        session_id=session_id,
        parent_action_id=parent_action_id,
        actor=actor,
        action_type=action_type,
        target=target,
        operation=operation,
        payload=normalize_payload(payload),
        intent_summary=intent_summary,
        idempotency_scope=scope,
        idempotency_key=idem_key,
        action_fingerprint=fp,
        semantic_continuity_hash=None,
        status=ActionStatus.PROPOSED,
        policy_decision=None,
        timestamps=EnvelopeTimestamps(
            created_at=now,
            updated_at=now,
            expires_at=(now + timedelta(seconds=expires_in_seconds)) if expires_in_seconds else None,
        ),
    )


def is_terminal(envelope: ActionEnvelope) -> bool:
    """Verifica si el envelope está en un estado terminal."""
    return envelope.status in TERMINAL_STATUSES


def is_expired(envelope: ActionEnvelope) -> bool:
    """Verifica si el envelope expiró (AWAITING_APPROVAL timeout)."""
    if envelope.status != ActionStatus.AWAITING_APPROVAL:
        return False
    if envelope.timestamps.expires_at is None:
        return False
    return utcnow() > envelope.timestamps.expires_at


def envelope_to_dict(envelope: ActionEnvelope) -> dict[str, Any]:
    """Serializa un envelope a dict para persistencia/logging."""
    return {
        "action_id": envelope.action_id,
        "trace_id": envelope.trace_id,
        "session_id": envelope.session_id,
        "parent_action_id": envelope.parent_action_id,
        "actor": {
            "actor_id": envelope.actor.actor_id,
            "actor_type": envelope.actor.actor_type,
            "declared_trust_ring": envelope.actor.declared_trust_ring.value
            if envelope.actor.declared_trust_ring
            else None,
        },
        "action_type": envelope.action_type.value,
        "target": {
            "resource_kind": envelope.target.resource_kind.value,
            "resource_id": envelope.target.resource_id,
            "locator": envelope.target.locator,
            "owner": envelope.target.owner,
            "contains_sensitive_data": envelope.target.contains_sensitive_data,
            "external_network": envelope.target.external_network,
        },
        "operation": envelope.operation,
        "payload": dict(envelope.payload),
        "intent_summary": envelope.intent_summary,
        "idempotency_scope": envelope.idempotency_scope,
        "idempotency_key": envelope.idempotency_key,
        "action_fingerprint": envelope.action_fingerprint,
        "semantic_continuity_hash": envelope.semantic_continuity_hash,
        "status": envelope.status.value,
        "policy_decision": {
            "enforced_trust_ring": envelope.policy_decision.enforced_trust_ring.value,
            "risk_level": envelope.policy_decision.risk_level.value,
            "requires_hitl": envelope.policy_decision.requires_hitl,
            "decision": envelope.policy_decision.decision,
            "decision_reason": envelope.policy_decision.decision_reason,
            "policy_version": envelope.policy_decision.policy_version,
        }
        if envelope.policy_decision
        else None,
        "timestamps": {
            "created_at": envelope.timestamps.created_at.isoformat(),
            "updated_at": envelope.timestamps.updated_at.isoformat(),
            "expires_at": envelope.timestamps.expires_at.isoformat() if envelope.timestamps.expires_at else None,
        },
    }
