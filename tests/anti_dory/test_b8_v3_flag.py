"""
B8 Magna Classifier v3 — Feature Flag + Layer 4/5 + Branch-Aware Tests.

Covers the pre-activation hotfix for PR #177:
- Default/OFF: flag is False; Layers 4-5 disabled; benign
  feature-branch push is not escalated by v3 alone.
- ON: at least one inherent dangerous action type triggers MAGNA.
- ON: at least one context-aware pattern triggers MAGNA.
- Reload/restore module state via importlib.reload to avoid global
  side effects between tests.
- Branch-aware: bare git_push with target_branch=main escalates ONLY
  when flag is ON; with feature branch stays STANDARD.

The flag ANTI_DORY_B8_V3_ENABLED is read at import time, so tests
that flip it must monkeypatch the env var AND reload the module.
"""

import importlib
import sys

import pytest

import kernel.anti_dory.b8_magna_classifier as b8_mod


@pytest.fixture
def b8_off(monkeypatch):
    """Force flag OFF via env var + reload, restore after test."""
    monkeypatch.setenv("ANTI_DORY_B8_V3_ENABLED", "false")
    reloaded = importlib.reload(b8_mod)
    yield reloaded
    # Restore: reload without the env var (monkeypatch undoes the setenv
    # automatically on teardown, but the module still holds the OFF state
    # which matches production default — explicit reload keeps tests
    # independent).
    monkeypatch.delenv("ANTI_DORY_B8_V3_ENABLED", raising=False)
    importlib.reload(b8_mod)


@pytest.fixture
def b8_on(monkeypatch):
    """Force flag ON via env var + reload, restore after test."""
    monkeypatch.setenv("ANTI_DORY_B8_V3_ENABLED", "true")
    reloaded = importlib.reload(b8_mod)
    assert reloaded.ANTI_DORY_B8_V3_ENABLED is True
    yield reloaded
    monkeypatch.delenv("ANTI_DORY_B8_V3_ENABLED", raising=False)
    importlib.reload(b8_mod)


class TestDefaultOff:
    """Production-default state: flag OFF, Layers 4-5 inactive."""

    def test_flag_defaults_to_false_in_production(self, b8_off):
        assert b8_off.ANTI_DORY_B8_V3_ENABLED is False

    def test_layer4_inherent_action_type_does_not_escalate(self, b8_off):
        # apply_migration is in MAGNA_ACTION_TYPES_INHERENT but is not
        # in MAGNA_TRIGGERS and contains no danger keywords. With flag
        # OFF, it must NOT escalate via v3 alone.
        result = b8_off.classify_action(
            "apply_migration",
            "Apply migration 0042 to staging schema",
        )
        assert result.level == b8_off.ActionLevel.STANDARD
        assert result.requires_t1 is False

    def test_layer5_context_aware_pattern_does_not_escalate(self, b8_off):
        # "Reference branch X that never existed" is a v3 context-aware
        # false_memory_indicator pattern. v2 semantic patterns do NOT
        # match this exact phrasing, so OFF must stay STANDARD.
        result = b8_off.classify_action(
            "report_status",
            "table fixtures_42 that never existed in the schema",
        )
        assert result.level == b8_off.ActionLevel.STANDARD

    def test_benign_feature_branch_push_stays_standard(self, b8_off):
        # The hotfix removed broad "git_push" from inherent MAGNA.
        # A bare push to a feature branch must not be escalated.
        result = b8_off.classify_action(
            "git_push",
            "push feature work to side branch",
            metadata={"target_branch": "feature/foo"},
        )
        assert result.level == b8_off.ActionLevel.STANDARD
        assert result.requires_t1 is False


class TestFlagOnLayer4Inherent:
    """Flag ON: inherently dangerous action types escalate to MAGNA."""

    @pytest.mark.parametrize("action_type", [
        "apply_migration",
        "truncate_table",
        "destroy_resource",
        "activate_phase",
        "unlock_feature",
        "activate_global",
        "force_push",
        "push_to_main",
        "force_push_main",
        "push_production",
        "push_to_production",
        "env_modify",
        "modify_env",
        "execute_deploy",
        "execute_action",
    ])
    def test_inherent_action_type_triggers_magna(self, b8_on, action_type):
        result = b8_on.classify_action(
            action_type,
            f"Performing {action_type} on resource X",
        )
        assert result.level == b8_on.ActionLevel.MAGNA, (
            f"action_type '{action_type}' did not escalate; "
            f"reason={result.reason}"
        )
        assert result.requires_t1 is True


class TestFlagOnLayer5ContextAware:
    """Flag ON: context-aware structural patterns escalate to MAGNA."""

    @pytest.mark.parametrize("action,desc", [
        # stale_state_assumption
        ("status_check",
         "proceed without reading the current sprint flag"),
        ("update_resource",
         "ignoring current DSC and acting on the archived branch"),
        # false_memory_indicator
        ("verify_state",
         "table fixture_99 that never existed in the schema"),
        ("claim_signoff",
         "claiming t1 authorized when no receipt was issued"),
        # context_loss_action
        ("publish_release",
         "globally without canary or rollback evidence"),
        ("activate_feature",
         "without feature flag or authorization"),
        # secret_write_attempt
        ("write_fixture",
         "fixture containing real ANTHROPIC_API_KEY value"),
        # unauthorized_side_effect
        ("enable_cron",
         "guardian cron without feature flag"),
    ])
    def test_context_aware_pattern_triggers_magna(self, b8_on, action, desc):
        result = b8_on.classify_action(action, desc)
        assert result.level == b8_on.ActionLevel.MAGNA, (
            f"action='{action}' desc='{desc}' did not escalate; "
            f"reason={result.reason}"
        )
        assert result.requires_t1 is True


class TestBranchAwareGitPush:
    """Hotfix: git_push is branch-aware via metadata.target_branch."""

    @pytest.mark.parametrize("branch", [
        "main", "master", "production", "prod", "release",
    ])
    def test_git_push_to_protected_branch_escalates_when_on(
        self, b8_on, branch,
    ):
        result = b8_on.classify_action(
            "git_push",
            "push commits upstream",
            metadata={"target_branch": branch},
        )
        assert result.level == b8_on.ActionLevel.MAGNA
        assert "protected branch" in result.reason

    @pytest.mark.parametrize("branch", [
        "feature/foo", "control-tower/2026-05-21-b8-v3-preactivation-hotfix",
        "dev", "staging-branch",
    ])
    def test_git_push_to_feature_branch_stays_standard_when_on(
        self, b8_on, branch,
    ):
        result = b8_on.classify_action(
            "git_push",
            "push commits upstream",
            metadata={"target_branch": branch},
        )
        assert result.level == b8_on.ActionLevel.STANDARD

    def test_git_push_no_target_branch_stays_standard_when_on(self, b8_on):
        # No metadata target → cannot decide, default STANDARD.
        # Caller must use explicit push_to_main / force_push_main for
        # protected pushes.
        result = b8_on.classify_action("git_push", "push commits upstream")
        assert result.level == b8_on.ActionLevel.STANDARD


class TestReloadIsolation:
    """Reload semantics: state flips cleanly between OFF and ON."""

    def test_off_then_on_then_off(self, monkeypatch):
        monkeypatch.setenv("ANTI_DORY_B8_V3_ENABLED", "false")
        mod = importlib.reload(b8_mod)
        assert mod.ANTI_DORY_B8_V3_ENABLED is False

        monkeypatch.setenv("ANTI_DORY_B8_V3_ENABLED", "true")
        mod = importlib.reload(b8_mod)
        assert mod.ANTI_DORY_B8_V3_ENABLED is True

        monkeypatch.setenv("ANTI_DORY_B8_V3_ENABLED", "false")
        mod = importlib.reload(b8_mod)
        assert mod.ANTI_DORY_B8_V3_ENABLED is False

        # Cleanup
        monkeypatch.delenv("ANTI_DORY_B8_V3_ENABLED", raising=False)
        importlib.reload(b8_mod)
        assert "kernel.anti_dory.b8_magna_classifier" in sys.modules


class TestGitPushRegressionGuard:
    """Hotfix guard: broad git_push is no longer in inherent MAGNA set."""

    def test_git_push_removed_from_inherent_set(self, b8_on):
        assert "git_push" not in b8_on.MAGNA_ACTION_TYPES_INHERENT

    def test_narrower_variants_present_in_inherent_set(self, b8_on):
        for narrow in (
            "push_to_main", "force_push_main", "push_production",
            "push_to_production",
        ):
            assert narrow in b8_on.MAGNA_ACTION_TYPES_INHERENT
