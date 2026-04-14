"""
El Monstruo — Policy Engine v1.0
==================================
Motor de políticas Python puro con interfaz compatible OPA/Cedar.
Diseñado por el Consejo de 6 Sabios (Ciclo 3, 14 abril 2026).

Arquitectura:
  1. Reglas declarativas (dict-based, no DSL externo)
  2. Evaluación determinista en < 1ms
  3. Integra CompositeRiskCalculator para cadenas de acciones
  4. Interfaz Cedar-like: permit/forbid/when conditions
  5. Backward compatible con PolicyHook ABC existente

Dependencias: Solo stdlib + core/action_envelope.py + core/composite_risk.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable

import structlog

from core.action_envelope import (
    ActionEnvelope,
    ActionType,
    RiskLevel,
    TrustRing,
    ResourceKind,
    PolicyDecision as EnvelopePolicyDecision,
)
from core.composite_risk import get_composite_calculator

logger = structlog.get_logger("policy.engine")


# ── Policy Effect (Cedar-compatible) ────────────────────────────────

class PolicyEffect(StrEnum):
    """Cedar-compatible policy effects."""
    PERMIT = "PERMIT"
    FORBID = "FORBID"


# ── Policy Rule ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class PolicyRule:
    """A single policy rule (Cedar-like: effect + conditions).

    Attributes:
        rule_id: Unique identifier for the rule
        effect: PERMIT or FORBID
        description: Human-readable description
        priority: Lower = evaluated first (0-999)
        conditions: Dict of field_name -> expected_value or callable
    """
    rule_id: str
    effect: PolicyEffect
    description: str
    priority: int = 100
    conditions: dict[str, Any] = field(default_factory=dict)


# ── Evaluation Result ────────────────────────────────────────────────

@dataclass
class PolicyEvalResult:
    """Result of evaluating the policy engine against an envelope."""
    decision: str           # "ALLOW" | "DENY" | "HITL"
    decision_reason: str
    matched_rule: str | None = None
    composite_risk: str | None = None
    composite_value: float = 0.0
    density_count: int = 0
    requires_hitl: bool = False


# ── Default Rules (Sprint 1) ────────────────────────────────────────

DEFAULT_RULES: list[PolicyRule] = [
    # R1: Kernel bypass — kernel actions always permitted
    PolicyRule(
        rule_id="kernel_bypass",
        effect=PolicyEffect.PERMIT,
        description="Kernel (R0) actions always permitted",
        priority=0,
        conditions={"trust_ring": TrustRing.R0_KERNEL.value},
    ),
    # R2: DELETE on SECRET always forbidden without HITL
    PolicyRule(
        rule_id="forbid_delete_secret",
        effect=PolicyEffect.FORBID,
        description="DELETE on SECRET resource always requires HITL",
        priority=10,
        conditions={
            "action_type": ActionType.DELETE.value,
            "resource_kind": ResourceKind.SECRET.value,
        },
    ),
    # R3: L3_SENSITIVE + untrusted input = HITL
    PolicyRule(
        rule_id="sensitive_untrusted_hitl",
        effect=PolicyEffect.FORBID,
        description="L3_SENSITIVE from untrusted source requires HITL",
        priority=20,
        conditions={
            "risk_level": RiskLevel.L3_SENSITIVE.value,
            "trust_ring": TrustRing.R3_UNTRUSTED_INPUT.value,
        },
    ),
    # R4: DELETE on DB always requires HITL
    PolicyRule(
        rule_id="forbid_delete_db",
        effect=PolicyEffect.FORBID,
        description="DELETE on DB resource requires HITL",
        priority=30,
        conditions={
            "action_type": ActionType.DELETE.value,
            "resource_kind": ResourceKind.DB.value,
        },
    ),
    # R5: EXECUTE on external network requires HITL if untrusted
    PolicyRule(
        rule_id="external_execute_untrusted",
        effect=PolicyEffect.FORBID,
        description="EXECUTE on external network from untrusted source requires HITL",
        priority=40,
        conditions={
            "action_type": ActionType.EXECUTE.value,
            "external_network": True,
            "trust_ring": TrustRing.R3_UNTRUSTED_INPUT.value,
        },
    ),
    # R6: Composite risk escalation — if density pushes risk above L3
    PolicyRule(
        rule_id="composite_escalation",
        effect=PolicyEffect.FORBID,
        description="Composite risk escalated to L3 due to action density",
        priority=50,
        conditions={"composite_risk": RiskLevel.L3_SENSITIVE.value},
    ),
]


# ── Policy Engine ────────────────────────────────────────────────────

class PolicyEngine:
    """Python-pure policy engine with Cedar-like semantics.

    Evaluation order:
      1. Extract facts from envelope
      2. Calculate composite risk
      3. Evaluate rules in priority order
      4. First FORBID match → HITL/DENY
      5. No FORBID match → ALLOW

    Cedar semantics: FORBID wins over PERMIT at same priority.
    """

    def __init__(self, rules: list[PolicyRule] | None = None) -> None:
        self._rules = sorted(rules or DEFAULT_RULES, key=lambda r: r.priority)
        self._version = "v1.0.0-sprint1-day2"

    @property
    def version(self) -> str:
        return self._version

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a rule and re-sort by priority."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID. Returns True if found."""
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        return len(self._rules) < before

    def evaluate(self, envelope: ActionEnvelope) -> PolicyEvalResult:
        """Evaluate all rules against an envelope. Returns PolicyEvalResult.

        This is the main entry point. Deterministic, < 1ms.
        """
        # Step 1: Extract facts from envelope
        facts = self._extract_facts(envelope)

        # Step 2: Calculate composite risk
        calculator = get_composite_calculator()
        composite = calculator.calculate(
            session_id=envelope.session_id,
            action_type=envelope.action_type.value,
            resource_kind=envelope.target.resource_kind.value,
            risk_level=facts["risk_level"],
        )
        facts["composite_risk"] = composite["composite_risk"]
        facts["composite_value"] = composite["composite_value"]

        # Step 3: Evaluate rules in priority order
        for rule in self._rules:
            if self._matches(rule, facts):
                if rule.effect == PolicyEffect.PERMIT:
                    logger.info(
                        "policy_permit",
                        rule=rule.rule_id,
                        action_id=envelope.action_id,
                    )
                    return PolicyEvalResult(
                        decision="ALLOW",
                        decision_reason=rule.description,
                        matched_rule=rule.rule_id,
                        composite_risk=composite["composite_risk"],
                        composite_value=composite["composite_value"],
                        density_count=composite["density_count"],
                        requires_hitl=False,
                    )
                elif rule.effect == PolicyEffect.FORBID:
                    logger.info(
                        "policy_forbid",
                        rule=rule.rule_id,
                        action_id=envelope.action_id,
                    )
                    return PolicyEvalResult(
                        decision="HITL",
                        decision_reason=rule.description,
                        matched_rule=rule.rule_id,
                        composite_risk=composite["composite_risk"],
                        composite_value=composite["composite_value"],
                        density_count=composite["density_count"],
                        requires_hitl=True,
                    )

        # Step 4: No rule matched → default ALLOW
        return PolicyEvalResult(
            decision="ALLOW",
            decision_reason="No policy rule matched — default allow",
            composite_risk=composite["composite_risk"],
            composite_value=composite["composite_value"],
            density_count=composite["density_count"],
            requires_hitl=False,
        )

    def to_envelope_policy_decision(
        self,
        result: PolicyEvalResult,
        trust_ring: TrustRing,
        risk_level: RiskLevel,
    ) -> EnvelopePolicyDecision:
        """Convert PolicyEvalResult to ActionEnvelope's PolicyDecision.

        This bridges the new PolicyEngine with the existing ActionEnvelope contract.
        """
        return EnvelopePolicyDecision(
            enforced_trust_ring=trust_ring,
            risk_level=risk_level,
            requires_hitl=result.requires_hitl,
            decision=result.decision,
            decision_reason=result.decision_reason,
            policy_version=self._version,
        )

    # ── Private helpers ──────────────────────────────────────────────

    @staticmethod
    def _extract_facts(envelope: ActionEnvelope) -> dict[str, Any]:
        """Extract evaluable facts from an envelope."""
        # Get risk_level from policy_decision if available, else default
        risk_level = RiskLevel.L1_SAFE.value
        trust_ring = TrustRing.R2_USER_DELEGATED.value
        if envelope.policy_decision:
            risk_level = envelope.policy_decision.risk_level.value
            trust_ring = envelope.policy_decision.enforced_trust_ring.value

        return {
            "action_type": envelope.action_type.value,
            "resource_kind": envelope.target.resource_kind.value,
            "risk_level": risk_level,
            "trust_ring": trust_ring,
            "external_network": envelope.target.external_network,
            "contains_sensitive_data": envelope.target.contains_sensitive_data,
            "actor_type": envelope.actor.actor_type,
            "session_id": envelope.session_id,
        }

    @staticmethod
    def _matches(rule: PolicyRule, facts: dict[str, Any]) -> bool:
        """Check if all rule conditions match the facts."""
        for key, expected in rule.conditions.items():
            actual = facts.get(key)
            if callable(expected):
                if not expected(actual):
                    return False
            elif actual != expected:
                return False
        return True


# ── Module-level singleton ───────────────────────────────────────────

_engine: PolicyEngine | None = None


def get_policy_engine() -> PolicyEngine:
    """Get or create the module-level PolicyEngine singleton."""
    global _engine
    if _engine is None:
        _engine = PolicyEngine()
    return _engine
