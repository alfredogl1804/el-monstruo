"""
B10 Guardian Autónomo Cron — Anti-Dory FORGE v3.0

Autonomous guardian that runs periodic checks on the Anti-Dory system.
DISABLED BY DEFAULT via feature flag.

Responsibilities:
1. Periodic Anchor Store integrity audit.
2. Memento drift detection.
3. Plan Ledger stale plan cleanup alerts.
4. Authority Matrix health check.
5. Signature chain validation.

This module provides the skeleton and scheduling logic.
Actual execution requires explicit T1 activation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional


class GuardianStatus(Enum):
    DISABLED = "DISABLED"
    ENABLED = "ENABLED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"


class CheckResult(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class GuardianCheck:
    """A single check performed by the Guardian."""

    name: str
    description: str
    interval_minutes: int = 60
    last_run: Optional[datetime] = None
    last_result: CheckResult = CheckResult.SKIP
    last_message: str = ""
    enabled: bool = True


@dataclass
class GuardianRunResult:
    """Result of a full Guardian run cycle."""

    timestamp: datetime
    checks_run: int
    checks_passed: int
    checks_warned: int
    checks_failed: int
    checks_skipped: int
    details: list[dict] = field(default_factory=list)

    @property
    def overall_healthy(self) -> bool:
        return self.checks_failed == 0


@dataclass
class FeatureFlag:
    """Feature flag controlling Guardian activation."""

    name: str = "GUARDIAN_AUTONOMO_ENABLED"
    enabled: bool = False
    reason: str = "Disabled by default — requires T1 activation"
    activated_at: Optional[datetime] = None
    activated_by: Optional[str] = None


class GuardianAutonomoCron:
    """
    B10 Guardian Autónomo Cron.

    DISABLED BY DEFAULT. Requires explicit activation via feature flag.

    Provides:
    - register_check(check) → None
    - run_cycle() → GuardianRunResult
    - activate(activated_by) → None
    - deactivate(reason) → None
    - get_status() → GuardianStatus
    - is_check_due(check) → bool
    """

    def __init__(self):
        self._flag = FeatureFlag()
        self._checks: list[GuardianCheck] = []
        self._check_handlers: dict[str, Callable] = {}
        self._status = GuardianStatus.DISABLED
        self._last_run: Optional[datetime] = None
        self._run_history: list[GuardianRunResult] = []

    @property
    def feature_flag(self) -> FeatureFlag:
        return self._flag

    def get_status(self) -> GuardianStatus:
        """Get current Guardian status."""
        return self._status

    def activate(self, activated_by: str) -> None:
        """
        Activate the Guardian (requires T1 authorization).

        Args:
            activated_by: Identity of who activated (must be T1).
        """
        if not activated_by or not activated_by.strip():
            raise ValueError("activated_by is required")

        self._flag.enabled = True
        self._flag.activated_at = datetime.utcnow()
        self._flag.activated_by = activated_by
        self._flag.reason = f"Activated by {activated_by}"
        self._status = GuardianStatus.ENABLED

    def deactivate(self, reason: str = "Manual deactivation") -> None:
        """Deactivate the Guardian."""
        self._flag.enabled = False
        self._flag.reason = reason
        self._status = GuardianStatus.DISABLED

    def register_check(self, check: GuardianCheck, handler: Optional[Callable] = None) -> None:
        """
        Register a check to be performed during run cycles.

        Args:
            check: GuardianCheck configuration.
            handler: Optional callable that performs the check.
        """
        self._checks.append(check)
        if handler:
            self._check_handlers[check.name] = handler

    def is_check_due(self, check: GuardianCheck) -> bool:
        """Determine if a check is due to run based on its interval."""
        if not check.enabled:
            return False
        if check.last_run is None:
            return True
        elapsed = datetime.utcnow() - check.last_run
        return elapsed >= timedelta(minutes=check.interval_minutes)

    def run_cycle(self) -> GuardianRunResult:
        """
        Execute a full Guardian run cycle.

        Returns:
            GuardianRunResult with all check outcomes.

        Raises:
            RuntimeError: If Guardian is not activated.
        """
        if not self._flag.enabled:
            raise RuntimeError("Guardian Autónomo is DISABLED. Requires T1 activation via activate() method.")

        self._status = GuardianStatus.RUNNING
        timestamp = datetime.utcnow()

        results = []
        passed = warned = failed = skipped = 0

        for check in self._checks:
            if not self.is_check_due(check):
                skipped += 1
                results.append(
                    {
                        "name": check.name,
                        "result": CheckResult.SKIP.value,
                        "message": "Not due yet",
                    }
                )
                continue

            handler = self._check_handlers.get(check.name)
            if handler is None:
                skipped += 1
                check.last_result = CheckResult.SKIP
                check.last_message = "No handler registered"
                results.append(
                    {
                        "name": check.name,
                        "result": CheckResult.SKIP.value,
                        "message": "No handler registered",
                    }
                )
                continue

            try:
                result = handler()
                check.last_run = datetime.utcnow()

                if result is True or result == CheckResult.PASS:
                    check.last_result = CheckResult.PASS
                    check.last_message = "OK"
                    passed += 1
                elif result == CheckResult.WARN:
                    check.last_result = CheckResult.WARN
                    check.last_message = "Warning"
                    warned += 1
                else:
                    check.last_result = CheckResult.FAIL
                    check.last_message = str(result) if result else "Failed"
                    failed += 1

                results.append(
                    {
                        "name": check.name,
                        "result": check.last_result.value,
                        "message": check.last_message,
                    }
                )

            except Exception as e:
                check.last_run = datetime.utcnow()
                check.last_result = CheckResult.FAIL
                check.last_message = f"Exception: {e}"
                failed += 1
                results.append(
                    {
                        "name": check.name,
                        "result": CheckResult.FAIL.value,
                        "message": f"Exception: {e}",
                    }
                )

        run_result = GuardianRunResult(
            timestamp=timestamp,
            checks_run=len(self._checks),
            checks_passed=passed,
            checks_warned=warned,
            checks_failed=failed,
            checks_skipped=skipped,
            details=results,
        )

        self._last_run = timestamp
        self._run_history.append(run_result)
        self._status = GuardianStatus.ENABLED

        return run_result

    def get_registered_checks(self) -> list[GuardianCheck]:
        """Return all registered checks."""
        return list(self._checks)

    def get_run_history(self) -> list[GuardianRunResult]:
        """Return run history."""
        return list(self._run_history)
