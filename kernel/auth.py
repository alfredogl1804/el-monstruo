"""
El Monstruo — API Authentication Middleware
=============================================
Simple API key authentication for kernel endpoints.

Strategy:
    - MONSTRUO_API_KEY env var holds the shared secret
    - Clients send it via X-API-Key header or Authorization: Bearer <key>
    - /health and / are always public (for Railway health checks)
    - All /v1/* endpoints require authentication
    - If MONSTRUO_API_KEY is not set, auth is DISABLED (dev mode)

Sprint 2 — 2026-04-15
Fix: 2026-04-16 — Use JSONResponse instead of raise HTTPException inside
     BaseHTTPMiddleware.dispatch(). HTTPException raised inside middleware
     is NOT caught by FastAPI's exception handlers and always returns 500.
     See: https://github.com/fastapi/fastapi/issues/1125
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
PUBLIC_PATHS = frozenset({"/", "/health", "/docs", "/openapi.json", "/redoc"})


def _get_api_key() -> Optional[str]:
    """Get the API key from environment. None means auth is disabled."""
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

    If MONSTRUO_API_KEY is not set, all requests are allowed (dev mode).
    This is intentional — Railway sets the env var in production.

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

        # Check if auth is enabled
        expected_key = _get_api_key()
        if not expected_key:
            # Auth disabled — dev mode
            return await call_next(request)

        # Enforce auth on /v1/* and /openai/v1/* paths
        if not (request.url.path.startswith("/v1") or request.url.path.startswith("/openai/v1")):
            return await call_next(request)

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
