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
