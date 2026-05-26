"""
El Monstruo — API Authentication Middleware
=============================================
Simple API key authentication for kernel endpoints.

Strategy:
    - MONSTRUO_API_KEY env var holds the shared secret
    - Clients send it via X-API-Key header or Authorization: Bearer <key>
    - /health, /health/auth, and / are always public (for Railway health checks)
    - All /v1/* endpoints require authentication
    - If MONSTRUO_API_KEY is not set, auth is FAIL-CLOSED (503)

Sprint 2 — 2026-04-15
Fix: 2026-04-16 — Use JSONResponse instead of raise HTTPException inside
     BaseHTTPMiddleware.dispatch(). HTTPException raised inside middleware
     is NOT caught by FastAPI's exception handlers and always returns 500.
     See: https://github.com/fastapi/fastapi/issues/1125

SECURITY FIX: 2026-04-21 (Sprint 22) — Convert from fail-open to fail-closed.
     Previous behavior: if MONSTRUO_API_KEY was not set, all requests were
     allowed ("dev mode"). This caused a critical security regression when
     Railway env vars were corrupted (IVD v3.8 FAIL #30-32).
     New behavior: if MONSTRUO_API_KEY is not set, protected endpoints
     return 503 Service Unavailable. Better to be down than compromised.
"""

from __future__ import annotations

import os
from typing import Optional

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = structlog.get_logger("kernel.auth")

# Public paths that never require auth (always exact-match)
#
# Sprint 91 hotfix (2026-05-26) — Mapa Vivo del Monstruo:
#   /v1/genome/now y /v1/genome/now/health son read-only y publicos por contrato
#   declarado en PR #201 ("La lectura simple es publica para que cualquier hilo
#   pueda consumirlo sin credenciales"). El JSON expuesto pasa secret-scan
#   (Gitleaks/Trufflehog/Secret Scan verdes en sha 88c35e9). El refresh con
#   side-effects (?refresh=1) sigue exigiendo X-API-Key dentro del router.
PUBLIC_PATHS = frozenset(
    {
        "/",
        "/health",
        "/health/auth",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/v1/genome/now",
        "/v1/genome/now/health",
    }
)

# Public ingest paths under /v1/* that bypass auth (Sprint 88 — 2026-05-06).
# Used by anonymous tracking from public landings (monstruo-tracking.js) that must
# POST without API key. Exact-match only — readers like /v1/traffic/summary/{run_id}
# remain protected. Brand DNA: e2e_traffic_ingest_public_path.
#
# Sprint EMBRION-NEEDS-001 / Tarea 4 (2026-05-10) — added /v1/embrion/telegram/webhook:
# Telegram cannot send X-API-Key header — it sends X-Telegram-Bot-Api-Secret-Token.
# The endpoint enforces its own stronger auth: a 32-byte URL-safe secret known
# only by Telegram (via setWebhook) and our service (via TELEGRAM_WEBHOOK_SECRET
# env var). API key would be weaker because it's shared across many clients,
# while the webhook secret is per-integration and rotates independently.
PUBLIC_INGEST_PATHS = frozenset(
    {
        "/v1/traffic/ingest",
        "/v1/embrion/telegram/webhook",
    }
)


def _get_api_key() -> Optional[str]:
    """Get the API key from environment. None means auth key is NOT configured."""
    return os.environ.get("MONSTRUO_API_KEY")


def _extract_token(request: Request) -> Optional[str]:
    """Extract API key from request headers."""
    # Try X-API-Key header first (preferred)
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return api_key

    # Try Authorization: Bearer <key>
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    return None


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces API key authentication on /v1/* endpoints.

    FAIL-CLOSED: If MONSTRUO_API_KEY is not set, protected endpoints
    return 503 Service Unavailable. This prevents security regressions
    caused by misconfigured environment variables.

    IMPORTANT: Uses JSONResponse instead of HTTPException because
    BaseHTTPMiddleware does not propagate HTTPException to FastAPI's
    exception handlers — it always converts them to 500.
    """

    async def dispatch(self, request: Request, call_next):
        # Always allow public paths
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # Always allow OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Sprint 88 (Tarea 3.A.1) — public ingest paths bypass auth (anonymous tracking).
        # Only POSTs allowed; GET/DELETE on these paths still require API key.
        if request.url.path in PUBLIC_INGEST_PATHS and request.method == "POST":
            logger.debug(
                "auth_public_ingest_bypass",
                path=request.url.path,
                client=request.client.host if request.client else "unknown",
            )
            return await call_next(request)

        # Enforce auth on /v1/* and /openai/v1/* paths only
        if not (request.url.path.startswith("/v1") or request.url.path.startswith("/openai/v1")):
            return await call_next(request)

        # Check if auth is configured — FAIL-CLOSED
        expected_key = _get_api_key()
        if not expected_key:
            logger.critical(
                "auth_key_not_configured",
                path=request.url.path,
                client=request.client.host if request.client else "unknown",
                msg="MONSTRUO_API_KEY not found in environment — DENYING ACCESS (fail-closed)",
            )
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Service temporarily unavailable — authentication not configured",
                    "error": "AUTH_NOT_CONFIGURED",
                },
            )

        # Extract and validate token
        provided_key = _extract_token(request)
        if not provided_key:
            logger.warning(
                "auth_missing_key",
                path=request.url.path,
                client=request.client.host if request.client else "unknown",
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing API key. Use X-API-Key header or Authorization: Bearer <key>"},
            )

        if provided_key != expected_key:
            logger.warning(
                "auth_invalid_key",
                path=request.url.path,
                client=request.client.host if request.client else "unknown",
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid API key"},
            )

        return await call_next(request)
