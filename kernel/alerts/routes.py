"""
El Monstruo — Alert System API Routes (Sprint 14)
===================================================
Exposes alert configuration and manual trigger endpoints.

Routes:
    GET  /v1/alerts/status  — Current alert config and cooldown state
    POST /v1/alerts/check   — Manually trigger all alert checks
    POST /v1/alerts/test    — Send a test alert to Telegram

All routes require API key authentication (same as /v1/chat).
"""

from __future__ import annotations

from typing import Optional

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

logger = structlog.get_logger("alerts.routes")

router = APIRouter(prefix="/v1/alerts", tags=["alerts"])

# Lazy singleton — initialized on first use
_monitor: Optional["SovereignAlertMonitor"] = None  # noqa: F821


def _get_monitor():
    """Lazy-init the SovereignAlertMonitor singleton."""
    global _monitor
    if _monitor is None:
        from kernel.alerts.sovereign_alerts import AlertConfig, SovereignAlertMonitor
        from kernel.runner.telegram_notifier import TelegramNotifier

        notifier = TelegramNotifier()
        config = AlertConfig()
        _monitor = SovereignAlertMonitor(notifier=notifier, config=config)
        logger.info(
            "alert_monitor_initialized",
            langfuse_enabled=config.langfuse_enabled,
            telegram_enabled=notifier.enabled,
        )
    return _monitor


class AlertCheckResponse(BaseModel):
    triggered: int
    alerts: list[dict]


class AlertStatusResponse(BaseModel):
    langfuse_enabled: bool
    telegram_enabled: bool
    cooldown_seconds: int
    daily_cost_budget_usd: float
    error_rate_threshold: float
    latency_p95_threshold_s: float
    eval_pass_rate_threshold: float
    active_cooldowns: dict[str, float]


@router.get("/status", response_model=AlertStatusResponse)
async def alert_status():
    """Return current alert configuration and cooldown state."""
    monitor = _get_monitor()
    config = monitor._config
    return AlertStatusResponse(
        langfuse_enabled=config.langfuse_enabled,
        telegram_enabled=monitor._notifier.enabled,
        cooldown_seconds=config.cooldown_seconds,
        daily_cost_budget_usd=config.daily_cost_budget_usd,
        error_rate_threshold=config.error_rate_threshold,
        latency_p95_threshold_s=config.latency_p95_threshold_s,
        eval_pass_rate_threshold=config.eval_pass_rate_threshold,
        active_cooldowns={k: round(v, 1) for k, v in monitor._cooldowns.items()},
    )


@router.post("/check", response_model=AlertCheckResponse)
async def check_alerts():
    """Manually trigger all alert checks."""
    monitor = _get_monitor()
    alerts = await monitor.check_all()
    return AlertCheckResponse(
        triggered=len(alerts),
        alerts=[
            {
                "type": a.alert_type.value,
                "severity": a.severity,
                "title": a.title,
                "message": a.message,
                "value": a.value,
                "threshold": a.threshold,
            }
            for a in alerts
        ],
    )


@router.post("/test")
async def test_alert():
    """Send a test alert to Telegram to verify the pipeline."""
    monitor = _get_monitor()
    from kernel.alerts.sovereign_alerts import Alert, AlertType

    test_alert = Alert(
        alert_type=AlertType.HEALTH_DOWN,
        severity="info",
        title="Test Alert — Sistema de Alertas Soberanas",
        message="Este es un mensaje de prueba. Si recibes esto, el sistema de alertas funciona correctamente.",
        value=1.0,
        threshold=0.0,
    )

    # Bypass cooldown for test
    success = await monitor._send_alert(test_alert)
    return {
        "success": success,
        "message": "Test alert sent to Telegram"
        if success
        else "Failed to send test alert (check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)",
    }
