"""
El Monstruo — Rate Limiter & Cost Caps Middleware
===================================================
In-memory sliding window rate limiter + daily cost caps.

Strategy:
    - Sliding window counter per API key (or IP if no key)
    - Configurable via env vars:
        RATE_LIMIT_RPM=60          # Requests per minute
        RATE_LIMIT_RPH=500         # Requests per hour
        DAILY_COST_CAP_USD=10.0    # Daily spend cap in USD
    - Returns 429 Too Many Requests when exceeded
    - Returns 402 Payment Required when cost cap exceeded
    - Public paths (/health, /) are exempt
    - Tracks cost accumulation from kernel responses

Sprint 3 — 2026-04-16
Validated by 6 Sabios consensus: "Rate limiting is P1 — a leaked key
without limits burns your entire LLM budget in hours."
"""
from __future__ import annotations

import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = structlog.get_logger("kernel.rate_limiter")

# ── Configuration ──────────────────────────────────────────────────

RATE_LIMIT_RPM = int(os.environ.get("RATE_LIMIT_RPM", "60"))
RATE_LIMIT_RPH = int(os.environ.get("RATE_LIMIT_RPH", "500"))
DAILY_COST_CAP_USD = float(os.environ.get("DAILY_COST_CAP_USD", "10.0"))

# Paths exempt from rate limiting
EXEMPT_PATHS = frozenset({"/", "/health", "/docs", "/openapi.json", "/redoc"})


# ── Sliding Window Counter ─────────────────────────────────────────

@dataclass
class SlidingWindow:
    """Sliding window rate counter with automatic cleanup."""
    timestamps: list[float] = field(default_factory=list)

    def add(self, now: float) -> None:
        self.timestamps.append(now)

    def count_in_window(self, now: float, window_seconds: float) -> int:
        """Count requests within the last `window_seconds`."""
        cutoff = now - window_seconds
        # Prune old entries (keep list manageable)
        self.timestamps = [t for t in self.timestamps if t > cutoff]
        return len(self.timestamps)


@dataclass
class DailyCost:
    """Track daily cost accumulation."""
    date: str = ""
    total_usd: float = 0.0

    def add_cost(self, cost_usd: float, today: str) -> None:
        if self.date != today:
            # New day — reset
            self.date = today
            self.total_usd = 0.0
        self.total_usd += cost_usd

    def get_cost(self, today: str) -> float:
        if self.date != today:
            return 0.0
        return self.total_usd


# ── Global State (in-memory, resets on restart) ────────────────────

_windows: dict[str, SlidingWindow] = defaultdict(SlidingWindow)
_daily_costs: dict[str, DailyCost] = defaultdict(DailyCost)


def _get_client_id(request: Request) -> str:
    """Get a unique client identifier from API key or IP."""
    api_key = request.headers.get("X-API-Key", "")
    if api_key:
        # Use last 8 chars of key as identifier (privacy)
        return f"key:{api_key[-8:]}"
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
        return f"key:{token[-8:]}"
    # Fallback to IP
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


def record_cost(client_id: str, cost_usd: float) -> None:
    """
    Record cost for a client. Called by the kernel after each LLM call.
    This is the public API for other modules to report costs.
    """
    today = time.strftime("%Y-%m-%d", time.gmtime())
    _daily_costs[client_id].add_cost(cost_usd, today)
    logger.debug(
        "cost_recorded",
        client=client_id,
        cost_usd=cost_usd,
        daily_total=_daily_costs[client_id].get_cost(today),
    )


def get_daily_cost(client_id: str) -> float:
    """Get the current daily cost for a client."""
    today = time.strftime("%Y-%m-%d", time.gmtime())
    return _daily_costs[client_id].get_cost(today)


def get_rate_stats(client_id: str) -> dict:
    """Get rate limiting stats for a client."""
    now = time.time()
    window = _windows.get(client_id, SlidingWindow())
    today = time.strftime("%Y-%m-%d", time.gmtime())
    return {
        "client_id": client_id,
        "requests_last_minute": window.count_in_window(now, 60),
        "requests_last_hour": window.count_in_window(now, 3600),
        "limits": {
            "rpm": RATE_LIMIT_RPM,
            "rph": RATE_LIMIT_RPH,
        },
        "daily_cost_usd": _daily_costs.get(client_id, DailyCost()).get_cost(today),
        "daily_cost_cap_usd": DAILY_COST_CAP_USD,
    }


# ── Middleware ─────────────────────────────────────────────────────

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces rate limits and cost caps.

    Uses JSONResponse (not HTTPException) because BaseHTTPMiddleware
    does not propagate HTTPException to FastAPI's exception handlers.
    """

    async def dispatch(self, request: Request, call_next):
        # Exempt paths
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        # Only rate-limit API endpoints
        if not (request.url.path.startswith("/v1") or request.url.path.startswith("/openai/v1")):
            return await call_next(request)

        # OPTIONS always pass (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        client_id = _get_client_id(request)
        now = time.time()
        window = _windows[client_id]

        # Check per-minute rate
        rpm_count = window.count_in_window(now, 60)
        if rpm_count >= RATE_LIMIT_RPM:
            logger.warning(
                "rate_limit_exceeded",
                client=client_id,
                limit="rpm",
                count=rpm_count,
                max=RATE_LIMIT_RPM,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": f"Rate limit exceeded: {rpm_count}/{RATE_LIMIT_RPM} requests per minute",
                        "type": "rate_limit_error",
                        "code": "rate_limit_exceeded",
                    }
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(RATE_LIMIT_RPM),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(now + 60)),
                },
            )

        # Check per-hour rate
        rph_count = window.count_in_window(now, 3600)
        if rph_count >= RATE_LIMIT_RPH:
            logger.warning(
                "rate_limit_exceeded",
                client=client_id,
                limit="rph",
                count=rph_count,
                max=RATE_LIMIT_RPH,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": f"Rate limit exceeded: {rph_count}/{RATE_LIMIT_RPH} requests per hour",
                        "type": "rate_limit_error",
                        "code": "rate_limit_exceeded",
                    }
                },
                headers={
                    "Retry-After": "3600",
                    "X-RateLimit-Limit": str(RATE_LIMIT_RPH),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(now + 3600)),
                },
            )

        # Check daily cost cap (only for chat/completions endpoints)
        if "chat" in request.url.path or "completions" in request.url.path:
            today = time.strftime("%Y-%m-%d", time.gmtime())
            daily_cost = _daily_costs[client_id].get_cost(today)
            if daily_cost >= DAILY_COST_CAP_USD:
                logger.warning(
                    "cost_cap_exceeded",
                    client=client_id,
                    daily_cost_usd=daily_cost,
                    cap_usd=DAILY_COST_CAP_USD,
                    path=request.url.path,
                )
                return JSONResponse(
                    status_code=402,
                    content={
                        "error": {
                            "message": f"Daily cost cap exceeded: ${daily_cost:.2f}/${DAILY_COST_CAP_USD:.2f} USD",
                            "type": "cost_cap_error",
                            "code": "daily_cost_cap_exceeded",
                        }
                    },
                )

        # Record request and proceed
        window.add(now)

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_RPM)
        response.headers["X-RateLimit-Remaining"] = str(max(0, RATE_LIMIT_RPM - rpm_count - 1))
        response.headers["X-RateLimit-Reset"] = str(int(now + 60))

        return response
