"""
El Monstruo — Sprint 1 Day 2 Tests (Governance Pipeline)
==========================================================
Tests for:
  1. CompositeRiskCalculator (core/composite_risk.py)
  2. PolicyEngine (core/policy_engine.py)
  3. HITL Gate (kernel/hitl.py)
  4. End-to-end governance pipeline

Run: pytest tests/test_sprint1_day2.py -v
"""

from __future__ import annotations

from core.action_envelope import (
    ActionType,
    ActorRef,
    ResourceKind,
    ResourceRef,
    RiskLevel,
    TrustRing,
    create_envelope,
)
from core.action_validator import validate_and_classify
from core.composite_risk import CompositeRiskCalculator
from core.policy_engine import (
    PolicyEffect,
    PolicyEngine,
    PolicyRule,
    get_policy_engine,
)

# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════


def _make_envelope(
    action_type: ActionType = ActionType.READ,
    resource_kind: ResourceKind = ResourceKind.MEMORY,
    actor_type: str = "user",
    intent: str = "chat",
):
    """Create a test envelope and run it through validate_and_classify."""
    envelope = create_envelope(
        session_id="test-session-001",
        trace_id="test-trace-001",
        actor=ActorRef(actor_id="user-alfredo", actor_type=actor_type),
        action_type=action_type,
        target=ResourceRef(
            resource_kind=resource_kind,
            resource_id=f"test_{intent}",
            locator=f"kernel://{intent}/test",
        ),
        operation=f"{intent}_response",
        payload={"test": True},
        intent_summary=f"Test {intent} action",
    )
    envelope, _ = validate_and_classify(envelope)
    return envelope


# ══════════════════════════════════════════════════════════════════════
# 1. CompositeRiskCalculator Tests
# ══════════════════════════════════════════════════════════════════════


class TestCompositeRiskCalculator:
    """Tests for core/composite_risk.py"""

    def setup_method(self):
        self.calc = CompositeRiskCalculator()

    def test_single_safe_action(self):
        """Single L1_SAFE action should remain L1_SAFE."""
        result = self.calc.calculate(
            session_id="s1",
            action_type="READ",
            resource_kind="MEMORY",
            risk_level="L1_SAFE",
        )
        assert result["composite_risk"] == "L1_SAFE"
        assert result["composite_value"] <= 0.3
        assert result["density_count"] == 0

    def test_single_caution_action(self):
        """Single L2_CAUTION action should remain L2_CAUTION."""
        result = self.calc.calculate(
            session_id="s2",
            action_type="WRITE",
            resource_kind="DB",
            risk_level="L2_CAUTION",
        )
        assert result["composite_risk"] == "L2_CAUTION"
        assert 0.3 <= result["composite_value"] < 0.7

    def test_single_sensitive_action(self):
        """Single L3_SENSITIVE action should remain L3_SENSITIVE."""
        result = self.calc.calculate(
            session_id="s3",
            action_type="DELETE",
            resource_kind="SECRET",
            risk_level="L3_SENSITIVE",
        )
        assert result["composite_risk"] == "L3_SENSITIVE"
        assert result["composite_value"] >= 0.7

    def test_density_escalation(self):
        """Multiple L2_CAUTION actions in window should increase composite risk."""
        for _ in range(6):
            result = self.calc.calculate(
                session_id="s4",
                action_type="WRITE",
                resource_kind="DB",
                risk_level="L2_CAUTION",
            )
        # After 6 actions: density_count >= 4, factor >= 0.4
        # composite = 0.5 * (1 + 0.4+) = 0.7+ → L3_SENSITIVE
        assert result["composite_risk"] == "L3_SENSITIVE"
        assert result["density_count"] >= 4

    def test_no_false_positive_from_safe_actions(self):
        """10 L1_SAFE actions should NOT escalate to L3 (Claude's key finding)."""
        for _ in range(10):
            result = self.calc.calculate(
                session_id="s5",
                action_type="READ",
                resource_kind="MEMORY",
                risk_level="L1_SAFE",
            )
        assert result["composite_risk"] == "L1_SAFE"
        assert result["density_count"] == 0

    def test_session_isolation(self):
        """Different sessions should have independent risk calculations."""
        self.calc.calculate("session_a", "WRITE", "DB", "L2_CAUTION")
        self.calc.calculate("session_a", "WRITE", "DB", "L2_CAUTION")
        result_b = self.calc.calculate("session_b", "WRITE", "DB", "L2_CAUTION")
        assert result_b["density_count"] == 0

    def test_cleanup_session(self):
        """cleanup_session should remove all history for that session."""
        self.calc.calculate("s7", "WRITE", "DB", "L2_CAUTION")
        assert self.calc.get_window_size("s7") == 1
        self.calc.cleanup_session("s7")
        assert self.calc.get_window_size("s7") == 0

    def test_mixed_action_types_no_density(self):
        """Different action types should not count as similar."""
        self.calc.calculate("s9", "READ", "DB", "L2_CAUTION")
        self.calc.calculate("s9", "WRITE", "DB", "L2_CAUTION")
        result = self.calc.calculate("s9", "DELETE", "DB", "L2_CAUTION")
        assert result["density_count"] == 0


# ══════════════════════════════════════════════════════════════════════
# 2. PolicyEngine Tests
# ══════════════════════════════════════════════════════════════════════


class TestPolicyEngine:
    """Tests for core/policy_engine.py"""

    def setup_method(self):
        self.engine = PolicyEngine()

    def test_kernel_bypass(self):
        """Kernel (R0) actions should always be permitted."""
        envelope = _make_envelope(
            action_type=ActionType.DELETE,
            resource_kind=ResourceKind.SECRET,
            actor_type="kernel",
        )
        result = self.engine.evaluate(envelope)
        assert result.decision == "ALLOW"
        assert result.matched_rule == "kernel_bypass"
        assert not result.requires_hitl

    def test_delete_secret_requires_hitl(self):
        """DELETE on SECRET should require HITL for non-kernel actors."""
        envelope = _make_envelope(
            action_type=ActionType.DELETE,
            resource_kind=ResourceKind.SECRET,
            actor_type="user",
        )
        result = self.engine.evaluate(envelope)
        assert result.decision == "HITL"
        assert result.requires_hitl
        assert result.matched_rule == "forbid_delete_secret"

    def test_safe_read_allowed(self):
        """Simple READ on MEMORY should be allowed."""
        envelope = _make_envelope(
            action_type=ActionType.READ,
            resource_kind=ResourceKind.MEMORY,
        )
        result = self.engine.evaluate(envelope)
        assert result.decision == "ALLOW"
        assert not result.requires_hitl

    def test_delete_db_requires_hitl(self):
        """DELETE on DB should require HITL."""
        envelope = _make_envelope(
            action_type=ActionType.DELETE,
            resource_kind=ResourceKind.DB,
        )
        result = self.engine.evaluate(envelope)
        assert result.decision == "HITL"
        assert result.requires_hitl

    def test_add_custom_rule(self):
        """Custom rules should be evaluable."""
        custom_rule = PolicyRule(
            rule_id="test_custom",
            effect=PolicyEffect.FORBID,
            description="Test custom rule",
            priority=5,
            conditions={"action_type": "WRITE", "resource_kind": "FILE"},
        )
        self.engine.add_rule(custom_rule)
        envelope = _make_envelope(
            action_type=ActionType.WRITE,
            resource_kind=ResourceKind.FILE,
        )
        result = self.engine.evaluate(envelope)
        assert result.decision == "HITL"
        assert result.matched_rule == "test_custom"

    def test_remove_rule(self):
        """Removing a rule should work."""
        assert self.engine.remove_rule("kernel_bypass")

    def test_composite_risk_in_result(self):
        """PolicyEvalResult should include composite risk data."""
        envelope = _make_envelope()
        result = self.engine.evaluate(envelope)
        assert result.composite_risk is not None
        assert isinstance(result.composite_value, float)
        assert isinstance(result.density_count, int)

    def test_to_envelope_policy_decision(self):
        """Bridge method should produce valid PolicyDecision."""
        envelope = _make_envelope()
        result = self.engine.evaluate(envelope)
        pd = self.engine.to_envelope_policy_decision(result, TrustRing.R2_USER_DELEGATED, RiskLevel.L1_SAFE)
        assert pd.decision in ("ALLOW", "DENY", "HITL")
        assert pd.policy_version == self.engine.version

    def test_version(self):
        """Engine should report its version."""
        assert "v1.1.0" in self.engine.version

    def test_singleton(self):
        """get_policy_engine should return same instance."""
        e1 = get_policy_engine()
        e2 = get_policy_engine()
        assert e1 is e2


# ══════════════════════════════════════════════════════════════════════
# 3. HITL Gate Tests
# ══════════════════════════════════════════════════════════════════════


class TestHITLGate:
    """Tests for kernel/hitl.py hitl_gate function."""

    def test_normal_flow_goes_to_respond(self):
        """Non-HITL actions should go to respond."""
        from kernel.hitl import hitl_gate

        state = {
            "status": "executing",
            "policy_decision": "ALLOW",
            "needs_human_approval": False,
        }
        assert hitl_gate(state) == "respond"

    def test_hitl_policy_goes_to_review(self):
        """HITL policy decision should route to hitl_review."""
        from kernel.hitl import hitl_gate

        state = {
            "status": "executing",
            "policy_decision": "HITL",
            "needs_human_approval": True,
            "human_approval_reason": "Test reason",
        }
        assert hitl_gate(state) == "hitl_review"

    def test_failed_status_goes_to_respond(self):
        """Failed execution should skip HITL and go to respond."""
        from kernel.hitl import hitl_gate

        state = {
            "status": "failed",
            "policy_decision": "HITL",
            "needs_human_approval": True,
        }
        assert hitl_gate(state) == "respond"

    def test_needs_approval_flag_alone(self):
        """needs_human_approval flag alone should trigger HITL."""
        from kernel.hitl import hitl_gate

        state = {
            "status": "executing",
            "policy_decision": "ALLOW",
            "needs_human_approval": True,
        }
        assert hitl_gate(state) == "hitl_review"


# ══════════════════════════════════════════════════════════════════════
# 4. End-to-End Governance Pipeline
# ══════════════════════════════════════════════════════════════════════


class TestEndToEndGovernance:
    """Integration tests for the full governance pipeline."""

    def test_safe_chat_flows_through(self):
        """A simple chat should pass all governance checks."""
        envelope = _make_envelope(intent="chat")
        engine = PolicyEngine()
        result = engine.evaluate(envelope)
        assert result.decision == "ALLOW"
        assert not result.requires_hitl

    def test_execute_tool_gets_caution(self):
        """An execute intent on TOOL should get L2_CAUTION."""
        envelope = _make_envelope(
            action_type=ActionType.EXECUTE,
            resource_kind=ResourceKind.TOOL,
            intent="execute",
        )
        assert envelope.policy_decision is not None
        assert envelope.policy_decision.risk_level in (
            RiskLevel.L2_CAUTION,
            RiskLevel.L3_SENSITIVE,
        )

    def test_delete_secret_full_pipeline(self):
        """DELETE SECRET should trigger HITL through full pipeline."""
        envelope = _make_envelope(
            action_type=ActionType.DELETE,
            resource_kind=ResourceKind.SECRET,
        )
        engine = PolicyEngine()
        result = engine.evaluate(envelope)
        assert result.requires_hitl
        # Verify hitl_gate would route correctly
        from kernel.hitl import hitl_gate

        state = {
            "status": "executing",
            "policy_decision": result.decision,
            "needs_human_approval": result.requires_hitl,
            "human_approval_reason": result.decision_reason,
        }
        assert hitl_gate(state) == "hitl_review"

    def test_rapid_writes_escalate(self):
        """Rapid DB writes should escalate via composite risk."""
        engine = PolicyEngine()
        for i in range(7):
            envelope = create_envelope(
                session_id="rapid-test-session",
                trace_id=f"trace-{i}",
                actor=ActorRef(actor_id="user-test", actor_type="user"),
                action_type=ActionType.WRITE,
                target=ResourceRef(
                    resource_kind=ResourceKind.DB,
                    resource_id=f"table_{i}",
                    locator="db://test/table",
                ),
                operation="write_record",
                payload={"record": i},
                intent_summary=f"Write record {i}",
            )
            envelope, _ = validate_and_classify(envelope)
            result = engine.evaluate(envelope)

        # After 7 rapid writes, composite should escalate
        assert result.composite_value > 0.5
        assert result.density_count >= 4
