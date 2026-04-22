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

# Public paths that never require auth
PUBLIC_PATHS = frozenset({"/", "/health", "/health/auth", "/docs", "/openapi.json", "/redoc"})


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
