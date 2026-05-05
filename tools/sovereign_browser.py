"""tools.sovereign_browser - Tool del Embrion para Browser Automation Soberano.

Sprint 84.6 - Browser Automation Soberano.

Esta tool permite al Embrion del Monstruo renderizar URLs, extraer HTML,
capturar screenshots y obtener Web Vitals usando el modulo soberano
kernel.browser.sovereign_browser (Playwright + Chromium en Docker).

A diferencia de tools/browser.py (Cloudflare Browser Run, externa),
este tool usa el browser que corre dentro del propio kernel (soberania,
Objetivo #12), evitando dependencia y costo de Cloudflare.

Uso desde el Embrion:
    from tools.sovereign_browser import sovereign_browser_render
    result = await sovereign_browser_render(
        url="https://example.com",
        viewport_preset="desktop",
        capture_html=True,
    )
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from kernel.browser.sovereign_browser import (
    DEFAULT_DESKTOP_VIEWPORT,
    MOBILE_VIEWPORT,
    SovereignBrowser,
)

logger = logging.getLogger("monstruo.tools.sovereign_browser")

# Sprint Memento Bloque 5 Fase 1 — pre-flight via library Memento (async)
_MEMENTO_AVAILABLE = True
try:
    from tools.memento_preflight import (  # type: ignore
        preflight_check_async,
        MementoPreflightError,
    )
except Exception as _import_exc:
    _MEMENTO_AVAILABLE = False
    logger.warning(
        "tools.memento_preflight no disponible (%r); sovereign_browser_* operará sin preflight",
        _import_exc,
    )


async def _maybe_run_preflight(
    operation_func: str,
    url: str,
    extra_context: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    """Ejecuta pre-flight async via Memento. Retorna error string si bloquea, None si OK.

    NO levanta excepciones — fallback degradado: si Memento no responde,
    el render continúa y queda registrado en logs (warn-mode) para que la
    operación no quede bloqueada por una falla del propio sistema de validación.
    """
    if not _MEMENTO_AVAILABLE:
        return None
    try:
        ctx: dict[str, Any] = {"url": url, "function": operation_func}
        if extra_context:
            ctx.update(extra_context)
        preflight = await preflight_check_async(
            operation="external_api_call",
            context_used=ctx,
            hilo_id="manus_ejecutor_sovereign_browser",
            intent_summary=f"sovereign_browser.{operation_func}({url})",
        )
        if not preflight.proceed:
            err = (
                f"preflight bloqueó ejecución: status={preflight.validation_status} "
                f"remediation={preflight.remediation}"
            )
            logger.warning("sovereign_browser %s: %s", operation_func, err)
            return err
        logger.info(
            "sovereign_browser %s: preflight OK validation_id=%s",
            operation_func,
            preflight.validation_id,
        )
        return None
    except MementoPreflightError as exc:
        logger.warning(
            "sovereign_browser %s: preflight falló (degraded): %s",
            operation_func,
            exc,
        )
        return None
    except Exception as exc:
        logger.warning(
            "sovereign_browser %s: preflight inesperado (degraded): %r",
            operation_func,
            exc,
        )
        return None


async def sovereign_browser_render(
    url: str,
    viewport_preset: str = "desktop",
    full_page: bool = True,
    capture_html: bool = True,
    headless: bool = True,
) -> dict[str, Any]:
    """Renderiza una URL y devuelve screenshot + HTML + metrics.

    Args:
        url: URL a renderizar (debe ser http:// o https://, no privada).
        viewport_preset: "desktop" (1280x720) o "mobile" (375x812).
        full_page: Si True, captura screenshot full-page (no solo viewport).
        capture_html: Si True, incluye el HTML rendered en la respuesta.
        headless: Si True (default), corre sin UI (obligatorio en Docker).

    Returns:
        dict con keys:
          - success: bool
          - url: str
          - screenshot_url: Optional[str] (URL publica si Supabase Storage configurado)
          - screenshot_local_path: Optional[str]
          - html: Optional[str]
          - title: str
          - status_code: int
          - metrics: {ttfb_ms, lcp_ms, load_time_ms}
          - viewport: {width, height}
          - duration_ms: int
          - error: Optional[str]
    """
    block_reason = await _maybe_run_preflight(
        "render",
        url,
        extra_context={
            "viewport_preset": viewport_preset,
            "full_page": full_page,
            "capture_html": capture_html,
        },
    )
    if block_reason is not None:
        return {"success": False, "url": url, "error": f"preflight: {block_reason}"}

    viewport = MOBILE_VIEWPORT if viewport_preset == "mobile" else DEFAULT_DESKTOP_VIEWPORT
    sb = SovereignBrowser(headless=headless)
    res = await sb.render(
        url=url,
        viewport=viewport,
        full_page=full_page,
        capture_html=capture_html,
    )
    return res.to_dict()


async def sovereign_browser_metrics(url: str, headless: bool = True) -> dict[str, Any]:
    """Devuelve solo Web Vitals (ttfb, lcp, load_time) de una URL.

    Mas rapido que render() porque no toma screenshot ni captura HTML.
    """
    block_reason = await _maybe_run_preflight("metrics", url)
    if block_reason is not None:
        return {"success": False, "url": url, "error": f"preflight: {block_reason}"}
    sb = SovereignBrowser(headless=headless)
    res = await sb.metrics(url=url)
    return res.to_dict()


async def sovereign_browser_check_mobile(
    url: str,
    headless: bool = True,
) -> dict[str, Any]:
    """Renderiza URL en viewport mobile (375x812) y chequea overflow horizontal.

    Returns:
        dict con keys:
          - success, url
          - screenshot_url, screenshot_local_path
          - has_horizontal_scroll: bool (True si hay overflow horizontal)
          - document_width: int
          - viewport_width: int (375)
          - duration_ms: int
          - error: Optional[str]
    """
    block_reason = await _maybe_run_preflight("check_mobile", url)
    if block_reason is not None:
        return {"success": False, "url": url, "error": f"preflight: {block_reason}"}
    sb = SovereignBrowser(headless=headless)
    res = await sb.check_mobile(url=url)
    return res.to_dict()


# --- Tool spec descriptor (para registry) -----------------------------------

SOVEREIGN_BROWSER_TOOL_SPEC = {
    "name": "sovereign_browser_render",
    "description": (
        "Renderiza una URL en un browser soberano (Playwright + Chromium "
        "dentro del kernel) y devuelve screenshot, HTML y Core Web Vitals "
        "(TTFB, LCP, load_time). Soporta viewport desktop o mobile."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL http:// o https:// a renderizar"},
            "viewport_preset": {
                "type": "string",
                "enum": ["desktop", "mobile"],
                "default": "desktop",
            },
            "full_page": {"type": "boolean", "default": True},
            "capture_html": {"type": "boolean", "default": True},
        },
        "required": ["url"],
    },
}


__all__ = [
    "sovereign_browser_render",
    "sovereign_browser_metrics",
    "sovereign_browser_check_mobile",
    "SOVEREIGN_BROWSER_TOOL_SPEC",
]
