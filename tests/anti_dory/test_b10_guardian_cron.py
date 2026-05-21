"""
Unit Tests — B10 Guardian Autónomo Cron
Anti-Dory FORGE v3.0 — Batch 005 Célula E

Tests feature flag, check registration, run cycle, activation.
No scheduler enabled. No production side effects.
"""

import pytest
from datetime import datetime, timedelta

from kernel.anti_dory.b10_guardian_cron import (
    CheckResult,
    FeatureFlag,
    GuardianAutonomoCron,
    GuardianCheck,
    GuardianRunResult,
    GuardianStatus,
)


@pytest.fixture
def guardian():
    return GuardianAutonomoCron()


@pytest.fixture
def sample_check():
    return GuardianCheck(
        name="anchor_integrity",
        description="Check Anchor Store integrity",
        interval_minutes=60,
    )


class TestFeatureFlag:
    def test_disabled_by_default(self, guardian):
        assert guardian.feature_flag.enabled is False
        assert guardian.get_status() == GuardianStatus.DISABLED

    def test_flag_has_reason(self, guardian):
        assert "T1" in guardian.feature_flag.reason


class TestActivation:
    def test_activate_changes_status(self, guardian):
        guardian.activate("T1")
        assert guardian.get_status() == GuardianStatus.ENABLED
        assert guardian.feature_flag.enabled is True
        assert guardian.feature_flag.activated_by == "T1"

    def test_activate_requires_identity(self, guardian):
        with pytest.raises(ValueError):
            guardian.activate("")

    def test_activate_whitespace_raises(self, guardian):
        with pytest.raises(ValueError):
            guardian.activate("   ")

    def test_deactivate(self, guardian):
        guardian.activate("T1")
        guardian.deactivate("Maintenance")
        assert guardian.get_status() == GuardianStatus.DISABLED
        assert guardian.feature_flag.enabled is False


class TestRegisterCheck:
    def test_register_check(self, guardian, sample_check):
        guardian.register_check(sample_check)
        checks = guardian.get_registered_checks()
        assert len(checks) == 1
        assert checks[0].name == "anchor_integrity"

    def test_register_with_handler(self, guardian, sample_check):
        handler = lambda: True
        guardian.register_check(sample_check, handler=handler)
        assert len(guardian.get_registered_checks()) == 1


class TestIsCheckDue:
    def test_never_run_is_due(self, guardian, sample_check):
        assert guardian.is_check_due(sample_check) is True

    def test_recently_run_not_due(self, guardian, sample_check):
        sample_check.last_run = datetime.utcnow()
        assert guardian.is_check_due(sample_check) is False

    def test_old_run_is_due(self, guardian, sample_check):
        sample_check.last_run = datetime.utcnow() - timedelta(hours=2)
        assert guardian.is_check_due(sample_check) is True

    def test_disabled_check_not_due(self, guardian, sample_check):
        sample_check.enabled = False
        assert guardian.is_check_due(sample_check) is False


class TestRunCycle:
    def test_disabled_raises(self, guardian, sample_check):
        guardian.register_check(sample_check)
        with pytest.raises(RuntimeError, match="DISABLED"):
            guardian.run_cycle()

    def test_run_with_passing_handler(self, guardian, sample_check):
        guardian.activate("T1")
        guardian.register_check(sample_check, handler=lambda: True)
        result = guardian.run_cycle()
        assert isinstance(result, GuardianRunResult)
        assert result.checks_passed == 1
        assert result.overall_healthy is True

    def test_run_with_failing_handler(self, guardian, sample_check):
        guardian.activate("T1")
        guardian.register_check(sample_check, handler=lambda: False)
        result = guardian.run_cycle()
        assert result.checks_failed == 1
        assert result.overall_healthy is False

    def test_run_with_exception_handler(self, guardian, sample_check):
        guardian.activate("T1")

        def bad_handler():
            raise Exception("DB connection failed")

        guardian.register_check(sample_check, handler=bad_handler)
        result = guardian.run_cycle()
        assert result.checks_failed == 1
        assert "Exception" in result.details[0]["message"]

    def test_run_with_no_handler_skips(self, guardian, sample_check):
        guardian.activate("T1")
        guardian.register_check(sample_check)  # No handler
        result = guardian.run_cycle()
        assert result.checks_skipped == 1

    def test_run_history_tracked(self, guardian, sample_check):
        guardian.activate("T1")
        guardian.register_check(sample_check, handler=lambda: True)
        guardian.run_cycle()
        guardian.run_cycle()
        assert len(guardian.get_run_history()) == 2

    def test_warn_result(self, guardian):
        guardian.activate("T1")
        check = GuardianCheck(name="warn_check", description="Warns")
        guardian.register_check(check, handler=lambda: CheckResult.WARN)
        result = guardian.run_cycle()
        assert result.checks_warned == 1


class TestGuardianRunResult:
    def test_overall_healthy_no_failures(self):
        result = GuardianRunResult(
            timestamp=datetime.utcnow(),
            checks_run=3, checks_passed=2, checks_warned=1,
            checks_failed=0, checks_skipped=0,
        )
        assert result.overall_healthy is True

    def test_overall_unhealthy_with_failure(self):
        result = GuardianRunResult(
            timestamp=datetime.utcnow(),
            checks_run=3, checks_passed=1, checks_warned=0,
            checks_failed=1, checks_skipped=1,
        )
        assert result.overall_healthy is False
