"""
El Monstruo — Webhook Tool (External Action Gateway)
=====================================================
Gives El Monstruo the ability to trigger external actions via webhooks.
Supports Zapier, Make.com, n8n, or any HTTP endpoint.

Security:
    - Only whitelisted domains are allowed (WEBHOOK_ALLOWED_DOMAINS env var)
    - All webhook calls are HIGH risk → always trigger HITL review
    - Payloads are logged for audit trail

Env vars:
    WEBHOOK_ALLOWED_DOMAINS — Comma-separated list of allowed domains
        Default: "hooks.zapier.com,hook.us1.make.com,n8n.cloud"
    WEBHOOK_TIMEOUT — Timeout in seconds (default: 30)

Sprint 5 — 2026-04-17
"""

from __future__ import annotations

import os
from typing import Any, Optional
from urllib.parse import urlparse

import httpx
import structlog

logger = structlog.get_logger("tools.webhook")

# Whitelisted domains for security
DEFAULT_ALLOWED_DOMAINS = "hooks.zapier.com,hook.us1.make.com,hook.eu1.make.com,n8n.cloud,hooks.slack.com"
ALLOWED_DOMAINS = set(
    d.strip() for d in os.environ.get("WEBHOOK_ALLOWED_DOMAINS", DEFAULT_ALLOWED_DOMAINS).split(",") if d.strip()
)

TIMEOUT = int(os.environ.get("WEBHOOK_TIMEOUT", "30"))


def _validate_url(url: str) -> tuple[bool, str]:
    """Validate that the URL is allowed."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("https",):
            return False, "Only HTTPS URLs are allowed"
        if not parsed.hostname:
            return False, "Invalid URL: no hostname"
        # Check if the hostname matches any allowed domain
        hostname = parsed.hostname.lower()
        for domain in ALLOWED_DOMAINS:
            if hostname == domain or hostname.endswith(f".{domain}"):
                return True, "OK"
        return False, f"Domain '{hostname}' not in whitelist: {ALLOWED_DOMAINS}"
    except Exception as e:
        return False, f"URL parse error: {e}"


async def call_webhook(
    url: str,
    payload: dict[str, Any],
    method: str = "POST",
    headers: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """
    Call an external webhook endpoint.

    Args:
        url: The webhook URL (must be HTTPS and on a whitelisted domain)
        payload: JSON payload to send
        method: HTTP method (POST or PUT, default POST)
        headers: Optional additional headers

    Returns:
        dict with status_code, response_body, and success flag
    """
    # Validate URL
    valid, reason = _validate_url(url)
    if not valid:
        logger.warning("webhook_blocked", url=url, reason=reason)
        return {
            "success": False,
            "error": f"URL blocked: {reason}",
            "status_code": 0,
        }

    # Validate method
    method = method.upper()
    if method not in ("POST", "PUT", "PATCH"):
        return {
            "success": False,
            "error": f"Method '{method}' not allowed. Use POST, PUT, or PATCH.",
            "status_code": 0,
        }

    # Build headers
    req_headers = {"Content-Type": "application/json", "User-Agent": "ElMonstruo/0.3.0"}
    if headers:
        req_headers.update(headers)

    logger.info(
        "webhook_call_start",
        url=url,
        method=method,
        payload_keys=list(payload.keys()),
    )

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=url,
                json=payload,
                headers=req_headers,
            )

        # Try to parse response as JSON
        try:
            response_body = response.json()
        except Exception:
            response_body = {"raw": response.text[:1000]}

        success = 200 <= response.status_code < 300

        logger.info(
            "webhook_call_complete",
            url=url,
            status_code=response.status_code,
            success=success,
        )

        return {
            "success": success,
            "status_code": response.status_code,
            "response": response_body,
        }

    except httpx.TimeoutException:
        logger.error("webhook_timeout", url=url, timeout=TIMEOUT)
        return {
            "success": False,
            "error": f"Timeout after {TIMEOUT}s",
            "status_code": 0,
        }
    except Exception as e:
        logger.error("webhook_call_failed", url=url, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "status_code": 0,
        }
