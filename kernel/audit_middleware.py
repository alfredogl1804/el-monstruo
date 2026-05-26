"""
El Monstruo — Audit Middleware
==================================
Sprint S-003.B — Tarea 1
Audit trail end-to-end de TODA request HTTP que pasa por el kernel.

Diseño:
    - INSERT-only en kernel_audit_log via Supabase service_role REST API.
    - Asíncrono: el insert se hace en background task para NO bloquear response.
    - Headers redactados antes de persistir (DSC-S-004 + DSC-S-006 v1.1 regla 3).
    - Captura: timestamp, request_id, method, path, status, duración_ms, caller, IP.
    - Si Supabase falla, log estructurado pero NO derriba la request (fail-open audit).

Performance gate:
    - Overhead esperado: <5% p50 latency (DSC-S-010 regla operacional).
    - INSERT fire-and-forget via asyncio.create_task() para no bloquear.
    - Si el background insert falla, queda en logs estructurados.

Orden en main.py:
    1. CORSMiddleware (CORS preflight)
    2. APIKeyAuthMiddleware (kernel/auth.py — NO TOCAR)
    3. AuditMiddleware ← este (después de auth, registra caller_identity ya validado)
    4. RateLimiterMiddleware

Autor: Hilo B (Manus)
Fecha: 2026-05-10
DSCs: DSC-S-004, DSC-S-006 v1.1, DSC-S-010
"""

from __future__ import annotations

import asyncio
import os
import re
import time
from typing import Any, Optional
from uuid import uuid4

import httpx
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = structlog.get_logger("kernel.audit")

# ============================================================================
# Configuración
# ============================================================================

# Paths excluidos del audit (alta frecuencia, bajo valor forense)
EXCLUDED_PATHS = frozenset(
    {
        "/",
        "/health",
        "/health/auth",
        "/openapi.json",
        "/docs",
        "/redoc",
        "/favicon.ico",
    }
)

# Headers que SIEMPRE se redactan (case-insensitive)
SENSITIVE_HEADERS = frozenset(
    {
        "authorization",
        "x-api-key",
        "x-telegram-bot-api-secret-token",
        "cookie",
        "set-cookie",
        "x-supabase-auth",
        "proxy-authorization",
    }
)

# Patrones regex para detectar secrets en valores de headers
SECRET_PATTERNS = [
    # Bearer tokens
    (re.compile(r"Bearer\s+[\w\-\.\=]{16,}", re.IGNORECASE), "Bearer <REDACTED>"),
    # JWT (3 partes base64)
    (re.compile(r"eyJ[\w\-]{10,}\.eyJ[\w\-]{10,}\.[\w\-]{10,}"), "<REDACTED:JWT>"),
    # Supabase legacy keys
    (re.compile(r"sb_(?:secret|publ)_[\w]{16,}", re.IGNORECASE), "<REDACTED:SUPABASE>"),
    # Supabase Personal Access Tokens
    (re.compile(r"sbp_[\w]{20,}"), "<REDACTED:SBP>"),
    # Anthropic sk-ant keys (chequeado ANTES de OpenAI porque sk-ant es prefijo más específico)
    (re.compile(r"sk-ant-[\w\-]{20,}"), "<REDACTED:ANTHROPIC>"),
    # OpenAI sk- keys (acepta guiones, ej. sk-proj-xxxx)
    (re.compile(r"sk-[\w\-]{20,}"), "<REDACTED:OPENAI>"),
    # Generic tokens >40 chars (base64-like). Excluye los marcadores REDACTED ya aplicados.
    (re.compile(r"(?<![\w<])[A-Za-z0-9_\-]{40,}(?![\w>])"), "<REDACTED:TOKEN>"),
]


# ============================================================================
# Funciones helper
# ============================================================================


def redact_secrets(value: str) -> str:
    """Redacta secrets conocidos en un string usando regex patterns."""
    if not value:
        return value
    for pattern, replacement in SECRET_PATTERNS:
        value = pattern.sub(replacement, value)
    return value


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Redacta headers sensibles. Returns new dict."""
    redacted: dict[str, str] = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if key_lower in SENSITIVE_HEADERS:
            redacted[key] = f"<REDACTED:{len(value)}>"
        else:
            # Heurística: redactar valores que parezcan secrets
            redacted[key] = redact_secrets(value)
    return redacted


def extract_caller_identity(request: Request) -> tuple[str, Optional[str]]:
    """Extrae caller_identity y api_key_prefix de la request.

    Returns:
        (caller_identity, api_key_prefix) — caller="anon" si no hay auth.
    """
    # API key
    api_key = request.headers.get("X-API-Key", "")
    if not api_key:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:].strip()

    if api_key:
        prefix = api_key[:8] if len(api_key) >= 8 else api_key[:4]
        # Si el API key coincide con MONSTRUO_API_KEY, identificamos como service_role
        expected_key = os.environ.get("MONSTRUO_API_KEY", "")
        if expected_key and api_key == expected_key:
            return "service_role", prefix
        return "authenticated", prefix

    # Telegram webhook (auth secreta separada)
    telegram_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if telegram_secret:
        return "telegram_webhook", telegram_secret[:8]

    return "anon", None


def get_supabase_credentials() -> Optional[tuple[str, str]]:
    """Obtiene credenciales de Supabase. Returns None si fail-closed.

    DSC-S-004: NO default values con secrets.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        return None
    return (url, key)


# ============================================================================
# Background insert task
# ============================================================================


async def _insert_audit_log(record: dict[str, Any]) -> None:
    """Inserta un audit log en Supabase de forma asíncrona.

    Si falla, log estructurado pero NO levanta excepción.
    """
    creds = get_supabase_credentials()
    if not creds:
        logger.warning("audit_supabase_creds_missing", request_id=record.get("request_id"))
        return

    url, key = creds
    endpoint = f"{url}/rest/v1/kernel_audit_log"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(endpoint, headers=headers, json=record)
            if resp.status_code not in (201, 204):
                logger.warning(
                    "audit_insert_non_2xx",
                    status=resp.status_code,
                    body=resp.text[:200],
                    request_id=record.get("request_id"),
                )
    except Exception as e:
        logger.warning(
            "audit_insert_failed",
            error=str(e)[:200],
            request_id=record.get("request_id"),
        )


# ============================================================================
# Middleware
# ============================================================================


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware que registra TODA request HTTP en kernel_audit_log.

    Registra después de auth (caller_identity validado) y antes de rate limit
    (auditamos requests aunque sean rate-limited al endpoint final).

    Fail-open: si Supabase falla, loggea pero NO derriba la request.
    """

    async def dispatch(self, request: Request, call_next):
        # Bypass paths públicos de alta frecuencia
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        # Bypass OPTIONS (CORS preflight, no aporta valor forense)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Generar/extraer request_id
        request_id = request.headers.get("X-Request-ID") or str(uuid4())

        # Capturar metadata pre-request
        start_time = time.perf_counter()
        caller_identity, api_key_prefix = extract_caller_identity(request)
        method = request.method
        path = request.url.path
        query_string = str(request.url.query) if request.url.query else None
        source_ip = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent", "")[:512]

        headers_dict = {k: v for k, v in request.headers.items()}
        headers_redacted = redact_headers(headers_dict)

        # Ejecutar request
        response: Optional[Response] = None
        error_class: Optional[str] = None
        try:
            response = await call_next(request)
        except Exception as e:
            error_class = type(e).__name__
            logger.error(
                "audit_request_exception",
                request_id=request_id,
                error_class=error_class,
                path=path,
            )
            raise
        finally:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            response_status = response.status_code if response else 500

            # Construir record
            record = {
                "request_id": request_id,
                "duration_ms": duration_ms,
                "caller_identity": caller_identity,
                "api_key_prefix": api_key_prefix,
                "source_ip": source_ip,
                "user_agent": user_agent or None,
                "method": method,
                "path": path[:2048],
                "query_string": query_string[:4096] if query_string else None,
                "response_status": response_status,
                "headers_redacted": headers_redacted,
                "error_class": error_class,
                "completed_at": "now()",
            }

            # Fire-and-forget para no bloquear la response
            asyncio.create_task(_insert_audit_log(record))

            # Agregar X-Request-ID a la response para correlación
            if response is not None and "X-Request-ID" not in response.headers:
                response.headers["X-Request-ID"] = request_id

        return response
