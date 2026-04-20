"""
Test R7: EXECUTE from user always requires HITL.
Validates the fix for the HITL pipeline not triggering.
"""

import pytest

from core.action_envelope import (
    ActionEnvelope,
    ActionType,
    ActorRef,
    PolicyDecision,
    ResourceKind,
    ResourceRef,
    RiskLevel,
    TrustRing,
    create_envelope,
)
from core.policy_engine import PolicyEngine


@pytest.fixture
def engine():
    """Fresh PolicyEngine with default rules (including R7)."""
    return PolicyEngine()


def _make_envelope(
    action_type: ActionType = ActionType.EXECUTE,
    actor_type: str = "user",
    resource_kind: ResourceKind = ResourceKind.TOOL,
    risk_level: RiskLevel = RiskLevel.L2_CAUTION,
    trust_ring: TrustRing = TrustRing.R2_USER_DELEGATED,
    external_network: bool = False,
) -> ActionEnvelope:
    """Helper to create test envelopes with policy_decision pre-set."""
    env = create_envelope(
        session_id="test-session",
        trace_id="test-trace",
        actor=ActorRef(actor_id="alfredo", actor_type=actor_type),
        action_type=action_type,
        target=ResourceRef(
            resource_kind=resource_kind,
            resource_id="test-resource",
            locator="kernel://test/execute",
            external_network=external_network,
        ),
        operation="test_operation",
        payload={"test": True},
        intent_summary="test intent",
    )
    # Pre-set policy_decision so _extract_facts gets the right values
    from dataclasses import replace

    env = replace(
        env,
        policy_decision=PolicyDecision(
            enforced_trust_ring=trust_ring,
            risk_level=risk_level,
            requires_hitl=False,
            decision="PENDING",
            decision_reason="pre-evaluation",
            policy_version="test",
        ),
    )
    return env


class TestR7ExecuteUserHITL:
    """Tests for rule R7: EXECUTE from user always requires HITL."""

    def test_execute_user_triggers_hitl(self, engine):
        """EXECUTE + user → HITL (the core fix)."""
        env = _make_envelope(
            action_type=ActionType.EXECUTE,
            actor_type="user",
        )
        result = engine.evaluate(env)
        assert result.requires_hitl is True
        assert result.decision == "HITL"
        assert result.matched_rule == "execute_user_hitl"

    def test_execute_user_l2_caution_triggers_hitl(self, engine):
        """EXECUTE + user + L2_CAUTION → HITL (the exact production scenario)."""
        env = _make_envelope(
            action_type=ActionType.EXECUTE,
            actor_type="user",
            risk_level=RiskLevel.L2_CAUTION,
            trust_ring=TrustRing.R2_USER_DELEGATED,
        )
        result = engine.evaluate(env)
        assert result.requires_hitl is True
        assert result.decision == "HITL"

    def test_execute_user_l1_safe_still_triggers_hitl(self, engine):
        """Even L1_SAFE EXECUTE from user → HITL (conservative governance)."""
        env = _make_envelope(
            action_type=ActionType.EXECUTE,
            actor_type="user",
            risk_level=RiskLevel.L1_SAFE,
        )
        result = engine.evaluate(env)
        assert result.requires_hitl is True

    def test_read_user_does_not_trigger_hitl(self, engine):
        """READ + user → ALLOW (no HITL for read operations)."""
        env = _make_envelope(
            action_type=ActionType.READ,
            actor_type="user",
            resource_kind=ResourceKind.MEMORY,
            risk_level=RiskLevel.L1_SAFE,
        )
        result = engine.evaluate(env)
        assert result.requires_hitl is False
        assert result.decision == "ALLOW"

    def test_execute_kernel_bypasses_hitl(self, engine):
        """EXECUTE + kernel → ALLOW (R0 kernel bypass has priority 0)."""
        env = _make_envelope(
            action_type=ActionType.EXECUTE,
            actor_type="kernel",
            trust_ring=TrustRing.R0_KERNEL,
        )
        result = engine.evaluate(env)
        assert result.requires_hitl is False
        assert result.decision == "ALLOW"
        assert result.matched_rule == "kernel_bypass"

    def test_execute_agent_does_not_trigger_r7(self, engine):
        """EXECUTE + agent → depends on other rules (R7 is user-only)."""
        env = _make_envelope(
            action_type=ActionType.EXECUTE,
            actor_type="agent",
            risk_level=RiskLevel.L2_CAUTION,
        )
        result = engine.evaluate(env)
        # Agent EXECUTE with L2 doesn't match R7 (user-only)
        # It may or may not trigger HITL based on other rules
        assert result.matched_rule != "execute_user_hitl"

    def test_r7_has_correct_priority(self, engine):
        """R7 should have priority 60 (after all other rules)."""
        r7 = [r for r in engine._rules if r.rule_id == "execute_user_hitl"]
        assert len(r7) == 1
        assert r7[0].priority == 60

    def test_delete_secret_still_higher_priority(self, engine):
        """DELETE + SECRET should match R2 (priority 10) before R7 (priority 60)."""
        env = _make_envelope(
            action_type=ActionType.DELETE,
            actor_type="user",
            resource_kind=ResourceKind.SECRET,
            risk_level=RiskLevel.L3_SENSITIVE,
        )
        result = engine.evaluate(env)
        assert result.requires_hitl is True
        assert result.matched_rule == "forbid_delete_secret"  # R2, not R7


class TestR7RegressionExistingRules:
    """Verify R7 doesn't break existing rules."""

    def test_kernel_bypass_still_works(self, engine):
        """R1: Kernel actions always permitted."""
        env = _make_envelope(
            action_type=ActionType.READ,
            actor_type="kernel",
            trust_ring=TrustRing.R0_KERNEL,
        )
        result = engine.evaluate(env)
        assert result.decision == "ALLOW"
        assert result.matched_rule == "kernel_bypass"

    def test_sensitive_untrusted_still_works(self, engine):
        """R3: L3_SENSITIVE + untrusted → HITL."""
        env = _make_envelope(
            action_type=ActionType.READ,
            actor_type="agent",
            risk_level=RiskLevel.L3_SENSITIVE,
            trust_ring=TrustRing.R3_UNTRUSTED_INPUT,
        )
        result = engine.evaluate(env)
        assert result.requires_hitl is True
        assert result.matched_rule == "sensitive_untrusted_hitl"

    def test_default_allow_for_safe_read(self, engine):
        """No rule matches → default ALLOW."""
        env = _make_envelope(
            action_type=ActionType.READ,
            actor_type="user",
            resource_kind=ResourceKind.MEMORY,
            risk_level=RiskLevel.L1_SAFE,
            trust_ring=TrustRing.R2_USER_DELEGATED,
        )
        result = engine.evaluate(env)
        assert result.decision == "ALLOW"
        assert result.requires_hitl is False
