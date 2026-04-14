"""
El Monstruo — Tests: Action Envelope v2.0
===========================================
Tests unitarios para core/action_envelope.py y core/action_validator.py
Sprint 1 Día 1 — 14 abril 2026
"""
import sys
import os
import json
import pytest
from datetime import datetime, timezone, timedelta

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.action_envelope import (
    ActionEnvelope,
    ActionType,
    ActionStatus,
    RiskLevel,
    TrustRing,
    ResourceKind,
    ActorRef,
    ResourceRef,
    EnvelopeTimestamps,
    PolicyDecision,
    create_envelope,
    transition,
    is_terminal,
    is_expired,
    envelope_to_dict,
    build_action_fingerprint,
    build_idempotency,
    InvalidTransitionError,
    VALID_TRANSITIONS,
    TERMINAL_STATUSES,
)
from core.action_validator import (
    validate_and_classify,
    validate_schema,
    validate_semantic,
    classify_risk,
    enforce_trust_ring,
    requires_hitl,
    ValidationResult,
    POLICY_VERSION,
)


# ── Fixtures ──────────────────────────────────────────────────────

def make_actor(actor_type: str = "user", actor_id: str = "alfredo_telegram") -> ActorRef:
    return ActorRef(actor_id=actor_id, actor_type=actor_type)


def make_target(
    kind: ResourceKind = ResourceKind.MEMORY,
    sensitive: bool = False,
    external: bool = False,
) -> ResourceRef:
    return ResourceRef(
        resource_kind=kind,
        resource_id="mem_001",
        locator="memory://conversation/latest",
        contains_sensitive_data=sensitive,
        external_network=external,
    )


def make_envelope(**overrides) -> ActionEnvelope:
    """Helper para crear envelopes de test."""
    defaults = dict(
        session_id="sess_test_001",
        trace_id="trace_test_001",
        actor=make_actor(),
        action_type=ActionType.READ,
        target=make_target(),
        operation="read_conversation_history",
        payload={"limit": 10},
        intent_summary="Read last 10 conversation messages",
    )
    defaults.update(overrides)
    return create_envelope(**defaults)


# ══════════════════════════════════════════════════════════════════
# TESTS: Action Envelope creation
# ══════════════════════════════════════════════════════════════════

class TestCreateEnvelope:
    def test_creates_with_proposed_status(self):
        env = make_envelope()
        assert env.status == ActionStatus.PROPOSED

    def test_generates_unique_action_id(self):
        e1 = make_envelope()
        e2 = make_envelope()
        assert e1.action_id != e2.action_id

    def test_action_id_has_prefix(self):
        env = make_envelope()
        assert env.action_id.startswith("act_")

    def test_timestamps_are_set(self):
        env = make_envelope()
        assert env.timestamps.created_at is not None
        assert env.timestamps.updated_at is not None
        assert env.timestamps.created_at.tzinfo == timezone.utc

    def test_expires_at_default_15min(self):
        env = make_envelope()
        assert env.timestamps.expires_at is not None
        delta = env.timestamps.expires_at - env.timestamps.created_at
        assert 899 <= delta.total_seconds() <= 901

    def test_expires_at_custom(self):
        env = make_envelope(expires_in_seconds=60)
        delta = env.timestamps.expires_at - env.timestamps.created_at
        assert 59 <= delta.total_seconds() <= 61

    def test_expires_at_none(self):
        env = make_envelope(expires_in_seconds=None)
        assert env.timestamps.expires_at is None

    def test_fingerprint_deterministic(self):
        e1 = make_envelope()
        e2 = make_envelope()
        assert e1.action_fingerprint == e2.action_fingerprint

    def test_fingerprint_changes_with_payload(self):
        e1 = make_envelope(payload={"limit": 10})
        e2 = make_envelope(payload={"limit": 20})
        assert e1.action_fingerprint != e2.action_fingerprint

    def test_idempotency_key_deterministic(self):
        e1 = make_envelope()
        e2 = make_envelope()
        assert e1.idempotency_key == e2.idempotency_key

    def test_idempotency_scope_format(self):
        env = make_envelope()
        assert "alfredo_telegram:trace_test_001" == env.idempotency_scope

    def test_policy_decision_is_none_at_creation(self):
        env = make_envelope()
        assert env.policy_decision is None

    def test_payload_is_normalized(self):
        env = make_envelope(payload={"b": 2, "a": 1})
        assert list(env.payload.keys()) == ["a", "b"]

    def test_frozen_immutability(self):
        env = make_envelope()
        with pytest.raises(AttributeError):
            env.status = ActionStatus.VALIDATED


# ══════════════════════════════════════════════════════════════════
# TESTS: Lifecycle transitions
# ══════════════════════════════════════════════════════════════════

class TestTransitions:
    def test_proposed_to_validated(self):
        env = make_envelope()
        env2 = transition(env, ActionStatus.VALIDATED)
        assert env2.status == ActionStatus.VALIDATED
        assert env.status == ActionStatus.PROPOSED  # original unchanged

    def test_invalid_transition_raises(self):
        env = make_envelope()
        with pytest.raises(InvalidTransitionError):
            transition(env, ActionStatus.EXECUTING)

    def test_terminal_states_have_no_transitions(self):
        for status in TERMINAL_STATUSES:
            assert VALID_TRANSITIONS[status] == set()

    def test_full_happy_path(self):
        env = make_envelope()
        env = transition(env, ActionStatus.VALIDATED)
        env = transition(env, ActionStatus.POLICY_CHECKED)
        env = transition(env, ActionStatus.EXECUTING)
        env = transition(env, ActionStatus.SUCCEEDED)
        assert env.status == ActionStatus.SUCCEEDED
        assert is_terminal(env)

    def test_hitl_path(self):
        env = make_envelope()
        env = transition(env, ActionStatus.VALIDATED)
        env = transition(env, ActionStatus.POLICY_CHECKED)
        env = transition(env, ActionStatus.AWAITING_APPROVAL)
        env = transition(env, ActionStatus.APPROVED)
        env = transition(env, ActionStatus.EXECUTING)
        env = transition(env, ActionStatus.SUCCEEDED)
        assert env.status == ActionStatus.SUCCEEDED

    def test_rejection_path(self):
        env = make_envelope()
        env = transition(env, ActionStatus.VALIDATED)
        env = transition(env, ActionStatus.POLICY_CHECKED)
        env = transition(env, ActionStatus.AWAITING_APPROVAL)
        env = transition(env, ActionStatus.REJECTED)
        assert is_terminal(env)

    def test_block_path(self):
        env = make_envelope()
        env = transition(env, ActionStatus.VALIDATED)
        env = transition(env, ActionStatus.POLICY_CHECKED)
        env = transition(env, ActionStatus.BLOCKED)
        assert is_terminal(env)

    def test_updated_at_changes_on_transition(self):
        env = make_envelope()
        import time
        time.sleep(0.01)
        env2 = transition(env, ActionStatus.VALIDATED)
        assert env2.timestamps.updated_at >= env.timestamps.updated_at


# ══════════════════════════════════════════════════════════════════
# TESTS: Expiration
# ══════════════════════════════════════════════════════════════════

class TestExpiration:
    def test_not_expired_when_not_awaiting(self):
        env = make_envelope()
        assert not is_expired(env)

    def test_not_expired_when_no_expiry(self):
        env = make_envelope(expires_in_seconds=None)
        env = transition(env, ActionStatus.VALIDATED)
        env = transition(env, ActionStatus.POLICY_CHECKED)
        env = transition(env, ActionStatus.AWAITING_APPROVAL)
        assert not is_expired(env)


# ══════════════════════════════════════════════════════════════════
# TESTS: Serialization
# ══════════════════════════════════════════════════════════════════

class TestSerialization:
    def test_envelope_to_dict_roundtrip(self):
        env = make_envelope()
        d = envelope_to_dict(env)
        assert d["action_id"] == env.action_id
        assert d["status"] == "PROPOSED"
        assert d["action_type"] == "READ"
        assert d["policy_decision"] is None

    def test_envelope_to_dict_with_policy(self):
        env = make_envelope()
        env, _ = validate_and_classify(env)
        d = envelope_to_dict(env)
        assert d["policy_decision"] is not None
        assert d["policy_decision"]["policy_version"] == POLICY_VERSION

    def test_serialization_is_json_safe(self):
        env = make_envelope()
        d = envelope_to_dict(env)
        json_str = json.dumps(d)
        assert json_str  # no exception


# ══════════════════════════════════════════════════════════════════
# TESTS: Validator — Schema
# ══════════════════════════════════════════════════════════════════

class TestSchemaValidation:
    def test_valid_envelope_passes(self):
        env = make_envelope()
        result = ValidationResult()
        validate_schema(env, result)
        assert result.is_valid

    def test_empty_operation_fails(self):
        env = make_envelope(operation="")
        result = ValidationResult()
        validate_schema(env, result)
        assert not result.is_valid
        assert any("operation" in e.field for e in result.errors)


# ══════════════════════════════════════════════════════════════════
# TESTS: Validator — Semantic + Reclassification
# ══════════════════════════════════════════════════════════════════

class TestSemanticValidation:
    def test_read_on_memory_stays_read(self):
        env = make_envelope(
            action_type=ActionType.READ,
            target=make_target(kind=ResourceKind.MEMORY),
            operation="read_history",
        )
        result = ValidationResult()
        env2 = validate_semantic(env, result)
        assert env2.action_type == ActionType.READ
        assert not result.reclassified

    def test_read_on_api_with_invoke_becomes_execute(self):
        env = make_envelope(
            action_type=ActionType.READ,
            target=make_target(kind=ResourceKind.API),
            operation="invoke_weather_api",
        )
        result = ValidationResult()
        env2 = validate_semantic(env, result)
        assert env2.action_type == ActionType.EXECUTE
        assert result.reclassified

    def test_read_on_tool_with_call_becomes_execute(self):
        env = make_envelope(
            action_type=ActionType.READ,
            target=make_target(kind=ResourceKind.TOOL),
            operation="call_calculator",
        )
        result = ValidationResult()
        env2 = validate_semantic(env, result)
        assert env2.action_type == ActionType.EXECUTE
        assert result.reclassified

    def test_read_on_file_stays_read(self):
        env = make_envelope(
            action_type=ActionType.READ,
            target=make_target(kind=ResourceKind.FILE),
            operation="invoke_something",
        )
        result = ValidationResult()
        env2 = validate_semantic(env, result)
        assert env2.action_type == ActionType.READ  # FILE not in EXECUTE_RESOURCE_KINDS

    def test_write_to_secret_autocorrects_sensitive(self):
        target = ResourceRef(
            resource_kind=ResourceKind.SECRET,
            resource_id="sec_001",
            locator="secrets://api_key",
            contains_sensitive_data=False,
        )
        env = make_envelope(
            action_type=ActionType.WRITE,
            target=target,
            operation="write_api_key",
        )
        result = ValidationResult()
        env2 = validate_semantic(env, result)
        assert env2.target.contains_sensitive_data is True


# ══════════════════════════════════════════════════════════════════
# TESTS: Validator — Risk Classification
# ══════════════════════════════════════════════════════════════════

class TestRiskClassification:
    def test_read_memory_is_l1(self):
        env = make_envelope()
        assert classify_risk(env) == RiskLevel.L1_SAFE

    def test_write_memory_is_l2(self):
        env = make_envelope(action_type=ActionType.WRITE)
        assert classify_risk(env) == RiskLevel.L2_CAUTION

    def test_delete_db_is_l3(self):
        env = make_envelope(
            action_type=ActionType.DELETE,
            target=make_target(kind=ResourceKind.DB),
        )
        assert classify_risk(env) == RiskLevel.L3_SENSITIVE

    def test_secret_always_l3(self):
        env = make_envelope(
            action_type=ActionType.READ,
            target=make_target(kind=ResourceKind.SECRET),
        )
        assert classify_risk(env) == RiskLevel.L3_SENSITIVE

    def test_external_execute_is_l3(self):
        env = make_envelope(
            action_type=ActionType.EXECUTE,
            target=make_target(external=True),
        )
        assert classify_risk(env) == RiskLevel.L3_SENSITIVE

    def test_external_read_is_l2(self):
        env = make_envelope(
            action_type=ActionType.READ,
            target=make_target(external=True),
        )
        assert classify_risk(env) == RiskLevel.L2_CAUTION


# ══════════════════════════════════════════════════════════════════
# TESTS: Validator — Trust Ring
# ══════════════════════════════════════════════════════════════════

class TestTrustRing:
    def test_kernel_is_r0(self):
        env = make_envelope(actor=make_actor(actor_type="kernel"))
        assert enforce_trust_ring(env) == TrustRing.R0_KERNEL

    def test_user_is_r2(self):
        env = make_envelope(actor=make_actor(actor_type="user"))
        assert enforce_trust_ring(env) == TrustRing.R2_USER_DELEGATED

    def test_agent_external_is_r3(self):
        env = make_envelope(
            actor=make_actor(actor_type="agent"),
            target=make_target(external=True),
        )
        assert enforce_trust_ring(env) == TrustRing.R3_UNTRUSTED_INPUT


# ══════════════════════════════════════════════════════════════════
# TESTS: Validator — HITL
# ══════════════════════════════════════════════════════════════════

class TestHITL:
    def test_l3_user_requires_hitl(self):
        assert requires_hitl(RiskLevel.L3_SENSITIVE, TrustRing.R2_USER_DELEGATED, ActionType.DELETE)

    def test_l3_kernel_no_hitl(self):
        assert not requires_hitl(RiskLevel.L3_SENSITIVE, TrustRing.R0_KERNEL, ActionType.DELETE)

    def test_delete_user_requires_hitl(self):
        assert requires_hitl(RiskLevel.L1_SAFE, TrustRing.R2_USER_DELEGATED, ActionType.DELETE)

    def test_l1_user_read_no_hitl(self):
        assert not requires_hitl(RiskLevel.L1_SAFE, TrustRing.R2_USER_DELEGATED, ActionType.READ)

    def test_r3_l2_requires_hitl(self):
        assert requires_hitl(RiskLevel.L2_CAUTION, TrustRing.R3_UNTRUSTED_INPUT, ActionType.WRITE)


# ══════════════════════════════════════════════════════════════════
# TESTS: Validator — Full Pipeline
# ══════════════════════════════════════════════════════════════════

class TestFullPipeline:
    def test_safe_read_passes_and_allows(self):
        env = make_envelope()
        env, result = validate_and_classify(env)
        assert result.is_valid
        assert env.status == ActionStatus.POLICY_CHECKED
        assert env.policy_decision.decision == "ALLOW"
        assert env.policy_decision.risk_level == RiskLevel.L1_SAFE

    def test_delete_db_triggers_hitl(self):
        env = make_envelope(
            action_type=ActionType.DELETE,
            target=make_target(kind=ResourceKind.DB),
            operation="delete_all_records",
            intent_summary="Delete all records from users table",
        )
        env, result = validate_and_classify(env)
        assert result.is_valid
        assert env.policy_decision.decision == "HITL"
        assert env.policy_decision.requires_hitl is True
        assert env.policy_decision.risk_level == RiskLevel.L3_SENSITIVE

    def test_reclassification_in_pipeline(self):
        env = make_envelope(
            action_type=ActionType.READ,
            target=make_target(kind=ResourceKind.API),
            operation="invoke_payment_api",
            intent_summary="Invoke payment processing API",
        )
        env, result = validate_and_classify(env)
        assert result.is_valid
        assert result.reclassified
        assert env.action_type == ActionType.EXECUTE

    def test_policy_version_is_set(self):
        env = make_envelope()
        env, _ = validate_and_classify(env)
        assert env.policy_decision.policy_version == POLICY_VERSION


# ══════════════════════════════════════════════════════════════════
# TESTS: Fingerprint & Idempotency
# ══════════════════════════════════════════════════════════════════

class TestFingerprint:
    def test_same_inputs_same_fingerprint(self):
        target = make_target()
        fp1 = build_action_fingerprint(ActionType.READ, target, "read", {"a": 1})
        fp2 = build_action_fingerprint(ActionType.READ, target, "read", {"a": 1})
        assert fp1 == fp2

    def test_different_payload_different_fingerprint(self):
        target = make_target()
        fp1 = build_action_fingerprint(ActionType.READ, target, "read", {"a": 1})
        fp2 = build_action_fingerprint(ActionType.READ, target, "read", {"a": 2})
        assert fp1 != fp2

    def test_different_action_type_different_fingerprint(self):
        target = make_target()
        fp1 = build_action_fingerprint(ActionType.READ, target, "op", {})
        fp2 = build_action_fingerprint(ActionType.WRITE, target, "op", {})
        assert fp1 != fp2

    def test_idempotency_key_deterministic(self):
        _, key1 = build_idempotency("user1", "trace1", "fp1")
        _, key2 = build_idempotency("user1", "trace1", "fp1")
        assert key1 == key2

    def test_idempotency_key_changes_with_actor(self):
        _, key1 = build_idempotency("user1", "trace1", "fp1")
        _, key2 = build_idempotency("user2", "trace1", "fp1")
        assert key1 != key2


# ══════════════════════════════════════════════════════════════════
# Run
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
