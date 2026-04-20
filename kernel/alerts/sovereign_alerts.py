"""
El Monstruo — Sovereign Alert System (Sprint 14 Task 1.6)
==========================================================
Monitors Langfuse traces and kernel health metrics, then routes
critical alerts to Telegram via the existing TelegramNotifier.

Architecture:
    AutonomousRunner (poll loop) → SovereignAlertMonitor.check_all()
    → Langfuse API (traces, scores, costs)
    → Alert rules evaluation
    → TelegramNotifier.send_message()

Alert Categories:
    1. COST_SPIKE    — Daily cost exceeds budget threshold
    2. ERROR_RATE    — Error rate exceeds threshold in last N traces
    3. LATENCY_SPIKE — P95 latency exceeds threshold
    4. EVAL_FAILURE  — Boolean evaluator scores drop below threshold
    5. HEALTH_DOWN   — Kernel health check fails

Design Principles:
    - No Celery/Redis dependency (uses existing asyncio poll loop)
    - Langfuse API for metrics (same BFF pattern as Command Center)
    - Cooldown per alert type to prevent spam
    - All thresholds configurable via env vars
    - Graceful degradation if Langfuse is unreachable

Sprint 14 — 2026-04-19
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import httpx
import structlog

logger = structlog.get_logger("alerts.sovereign")


# ── Alert Types ──────────────────────────────────────────────────────


class AlertType(str, Enum):
    COST_SPIKE = "cost_spike"
    ERROR_RATE = "error_rate"
    LATENCY_SPIKE = "latency_spike"
    EVAL_FAILURE = "eval_failure"
    HEALTH_DOWN = "health_down"


@dataclass
class Alert:
    """Represents a triggered alert."""

    alert_type: AlertType
    severity: str  # "critical", "warning", "info"
    title: str
    message: str
    value: float  # The metric value that triggered the alert
    threshold: float  # The threshold that was exceeded
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ── Configuration ────────────────────────────────────────────────────


@dataclass
class AlertConfig:
    """Alert thresholds and configuration, all from env vars."""

    # Cost alerts
    daily_cost_budget_usd: float = float(os.environ.get("ALERT_DAILY_COST_USD", "5.0"))

    # Error rate (percentage of traces with errors in last window)
    error_rate_threshold: float = float(os.environ.get("ALERT_ERROR_RATE_PCT", "15.0"))

    # Latency P95 in seconds
    latency_p95_threshold_s: float = float(os.environ.get("ALERT_LATENCY_P95_S", "30.0"))

    # Eval score threshold (minimum acceptable pass rate)
    eval_pass_rate_threshold: float = float(os.environ.get("ALERT_EVAL_PASS_RATE", "0.7"))

    # Cooldown in seconds per alert type (prevent spam)
    cooldown_seconds: int = int(os.environ.get("ALERT_COOLDOWN_S", "3600"))  # 1 hour

    # Langfuse API
    langfuse_host: str = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
    langfuse_public_key: str = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    langfuse_secret_key: str = os.environ.get("LANGFUSE_SECRET_KEY", "")

    # Kernel health endpoint
    kernel_health_url: str = os.environ.get("KERNEL_HEALTH_URL", "http://localhost:8000/health")

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)


# ── Sovereign Alert Monitor ─────────────────────────────────────────


class SovereignAlertMonitor:
    """
    Monitors system health and routes alerts to Telegram.

    Usage:
        from kernel.alerts.sovereign_alerts import SovereignAlertMonitor
        from kernel.runner.telegram_notifier import TelegramNotifier

        notifier = TelegramNotifier()
        monitor = SovereignAlertMonitor(notifier)

        # In the poll loop or a periodic task:
        alerts = await monitor.check_all()
    """

    def __init__(self, notifier, config: Optional[AlertConfig] = None):
        """
        Args:
            notifier: TelegramNotifier instance (or any object with send_message())
            config: AlertConfig (defaults to env-var-based config)
        """
        self._notifier = notifier
        self._config = config or AlertConfig()
        self._cooldowns: dict[str, float] = {}  # alert_type -> last_fired_timestamp
        self._http = httpx.AsyncClient(timeout=15)

    async def close(self):
        """Cleanup HTTP client."""
        await self._http.aclose()

    # ── Main entry point ─────────────────────────────────────────────

    async def check_all(self) -> list[Alert]:
        """
        Run all alert checks and send notifications for triggered alerts.
        Returns list of triggered alerts.
        """
        triggered: list[Alert] = []

        # Health check (always runs, no Langfuse needed)
        alert = await self._check_health()
        if alert:
            triggered.append(alert)

        # Langfuse-dependent checks
        if self._config.langfuse_enabled:
            for check_fn in [
                self._check_cost_spike,
                self._check_error_rate,
                self._check_latency_spike,
                self._check_eval_failure,
            ]:
                try:
                    alert = await check_fn()
                    if alert:
                        triggered.append(alert)
                except Exception as e:
                    logger.warning("alert_check_failed", check=check_fn.__name__, error=str(e))
        else:
            logger.debug("langfuse_alerts_skipped", reason="no_credentials")

        # Send notifications for non-cooldown alerts
        for alert in triggered:
            if self._should_fire(alert.alert_type):
                await self._send_alert(alert)
                self._cooldowns[alert.alert_type.value] = time.time()

        if triggered:
            logger.info(
                "alerts_triggered",
                count=len(triggered),
                types=[a.alert_type.value for a in triggered],
            )

        return triggered

    # ── Individual checks ────────────────────────────────────────────

    async def _check_health(self) -> Optional[Alert]:
        """Check kernel health endpoint."""
        try:
            resp = await self._http.get(self._config.kernel_health_url)
            if resp.status_code != 200:
                return Alert(
                    alert_type=AlertType.HEALTH_DOWN,
                    severity="critical",
                    title="Kernel Health Check Failed",
                    message=f"Health endpoint returned HTTP {resp.status_code}",
                    value=resp.status_code,
                    threshold=200,
                )
            data = resp.json()
            if data.get("status") != "healthy":
                return Alert(
                    alert_type=AlertType.HEALTH_DOWN,
                    severity="critical",
                    title="Kernel Unhealthy",
                    message=f"Status: {data.get('status')}. Components: {data.get('components', {})}",
                    value=0,
                    threshold=1,
                )
        except Exception as e:
            return Alert(
                alert_type=AlertType.HEALTH_DOWN,
                severity="critical",
                title="Kernel Unreachable",
                message=f"Cannot reach health endpoint: {e}",
                value=0,
                threshold=1,
            )
        return None

    async def _check_cost_spike(self) -> Optional[Alert]:
        """Check if daily cost exceeds budget."""
        data = await self._langfuse_get(
            "/api/public/metrics/daily",
            params={
                "traceName": None,
                "fromTimestamp": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat(),
            },
        )
        if not data:
            return None

        # Sum today's costs
        daily_cost = 0.0
        for entry in data.get("data", []):
            daily_cost += entry.get("totalCost", 0.0)

        if daily_cost > self._config.daily_cost_budget_usd:
            return Alert(
                alert_type=AlertType.COST_SPIKE,
                severity="warning",
                title="Daily Cost Budget Exceeded",
                message=f"Today's cost: ${daily_cost:.2f} exceeds budget of ${self._config.daily_cost_budget_usd:.2f}",
                value=daily_cost,
                threshold=self._config.daily_cost_budget_usd,
            )
        return None

    async def _check_error_rate(self) -> Optional[Alert]:
        """Check error rate in recent traces."""
        data = await self._langfuse_get(
            "/api/public/traces",
            params={
                "limit": 50,
                "orderBy": "timestamp.desc",
            },
        )
        if not data:
            return None

        traces = data.get("data", [])
        if len(traces) < 5:
            return None  # Not enough data

        error_count = sum(1 for t in traces if t.get("level") == "ERROR" or t.get("status") == "ERROR")
        error_rate = (error_count / len(traces)) * 100

        if error_rate > self._config.error_rate_threshold:
            return Alert(
                alert_type=AlertType.ERROR_RATE,
                severity="critical" if error_rate > 30 else "warning",
                title="High Error Rate Detected",
                message=f"Error rate: {error_rate:.1f}% ({error_count}/{len(traces)} traces). Threshold: {self._config.error_rate_threshold}%",  # noqa: E501
                value=error_rate,
                threshold=self._config.error_rate_threshold,
            )
        return None

    async def _check_latency_spike(self) -> Optional[Alert]:
        """Check P95 latency of recent traces."""
        data = await self._langfuse_get(
            "/api/public/traces",
            params={
                "limit": 50,
                "orderBy": "timestamp.desc",
            },
        )
        if not data:
            return None

        traces = data.get("data", [])
        latencies = []
        for t in traces:
            if t.get("latency") is not None:
                latencies.append(t["latency"])

        if len(latencies) < 5:
            return None

        latencies.sort()
        p95_idx = int(len(latencies) * 0.95)
        p95_latency = latencies[min(p95_idx, len(latencies) - 1)]

        if p95_latency > self._config.latency_p95_threshold_s:
            return Alert(
                alert_type=AlertType.LATENCY_SPIKE,
                severity="warning",
                title="High Latency Detected",
                message=f"P95 latency: {p95_latency:.1f}s exceeds threshold of {self._config.latency_p95_threshold_s}s",
                value=p95_latency,
                threshold=self._config.latency_p95_threshold_s,
            )
        return None

    async def _check_eval_failure(self) -> Optional[Alert]:
        """Check if Boolean evaluator pass rates drop below threshold."""
        data = await self._langfuse_get(
            "/api/public/scores",
            params={
                "limit": 100,
                "dataType": "BOOLEAN",
            },
        )
        if not data:
            return None

        scores = data.get("data", [])
        if len(scores) < 5:
            return None

        true_count = sum(1 for s in scores if s.get("value") is True or s.get("stringValue") == "True")
        pass_rate = true_count / len(scores)

        if pass_rate < self._config.eval_pass_rate_threshold:
            return Alert(
                alert_type=AlertType.EVAL_FAILURE,
                severity="warning",
                title="Evaluation Pass Rate Drop",
                message=f"Boolean eval pass rate: {pass_rate:.1%} below threshold of {self._config.eval_pass_rate_threshold:.1%} ({true_count}/{len(scores)} passed)",  # noqa: E501
                value=pass_rate,
                threshold=self._config.eval_pass_rate_threshold,
            )
        return None

    # ── Helpers ───────────────────────────────────────────────────────

    async def _langfuse_get(self, path: str, params: Optional[dict] = None) -> Optional[dict]:
        """Make authenticated GET request to Langfuse API."""
        url = f"{self._config.langfuse_host}{path}"
        auth = (self._config.langfuse_public_key, self._config.langfuse_secret_key)

        # Filter out None params
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}

        try:
            resp = await self._http.get(url, params=clean_params, auth=auth)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.warning("langfuse_api_error", path=path, status=resp.status_code)
                return None
        except Exception as e:
            logger.warning("langfuse_api_unreachable", path=path, error=str(e))
            return None

    def _should_fire(self, alert_type: AlertType) -> bool:
        """Check if alert is not in cooldown period."""
        last_fired = self._cooldowns.get(alert_type.value, 0)
        return (time.time() - last_fired) > self._config.cooldown_seconds

    async def _send_alert(self, alert: Alert) -> bool:
        """Format and send alert to Telegram."""
        severity_emoji = {
            "critical": "\U0001f6a8",  # 🚨
            "warning": "\u26a0\ufe0f",  # ⚠️
            "info": "\u2139\ufe0f",  # ℹ️
        }
        emoji = severity_emoji.get(alert.severity, "\U0001f514")  # 🔔

        message = (
            f"{emoji} *Alerta Soberana — {alert.severity.upper()}*\n\n"
            f"*{alert.title}*\n"
            f"{alert.message}\n\n"
            f"Valor: `{alert.value}` | Umbral: `{alert.threshold}`\n"
            f"Timestamp: `{alert.timestamp}`"
        )

        try:
            result = await self._notifier.send_message(
                user_id="sovereign-alerts",
                text=message,
            )
            if result:
                logger.info("alert_sent", type=alert.alert_type.value, severity=alert.severity)
            return result
        except Exception as e:
            logger.error("alert_send_failed", type=alert.alert_type.value, error=str(e))
            return False
