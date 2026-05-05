"""Sprint Memento B5 F1 — tests integración preflight en tools/sovereign_browser.py.

Verifica que las 3 funciones async (render, metrics, check_mobile) llamen a
preflight_check_async con operation="external_api_call" y manejen el resultado
correctamente:
  - proceed=True → continúa con la operación real
  - proceed=False → retorna {"success": False, "error": "preflight: ..."}
  - excepción de Memento → fallback degradado (continúa con warning)
  - import fallido → no llama preflight, opera normal
"""
from __future__ import annotations

import asyncio
import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _fake_preflight_result(proceed: bool = True, status: str = "ok", remediation: str = "") -> MagicMock:
    res = MagicMock()
    res.proceed = proceed
    res.validation_status = status
    res.remediation = remediation
    res.validation_id = "mv_test_xxx"
    return res


@pytest.fixture
def patched_browser_module():
    """Stub the kernel.browser.sovereign_browser SovereignBrowser to avoid
    requiring playwright/docker in test env."""
    fake_kbs = types.ModuleType("kernel.browser.sovereign_browser")
    fake_kbs.DEFAULT_DESKTOP_VIEWPORT = {"width": 1280, "height": 720}
    fake_kbs.MOBILE_VIEWPORT = {"width": 375, "height": 812}

    class _FakeSB:
        def __init__(self, headless=True):
            self.headless = headless

        async def render(self, **kw):
            r = MagicMock()
            r.to_dict.return_value = {"success": True, "url": kw["url"], "actually_rendered": True}
            return r

        async def metrics(self, **kw):
            r = MagicMock()
            r.to_dict.return_value = {"success": True, "url": kw["url"], "ttfb_ms": 100}
            return r

        async def check_mobile(self, **kw):
            r = MagicMock()
            r.to_dict.return_value = {"success": True, "url": kw["url"], "has_horizontal_scroll": False}
            return r

    fake_kbs.SovereignBrowser = _FakeSB
    fake_kb = types.ModuleType("kernel.browser")
    fake_kb.sovereign_browser = fake_kbs
    fake_kernel = sys.modules.get("kernel") or types.ModuleType("kernel")

    with patch.dict(sys.modules, {
        "kernel": fake_kernel,
        "kernel.browser": fake_kb,
        "kernel.browser.sovereign_browser": fake_kbs,
    }):
        # Force re-import
        sys.modules.pop("tools.sovereign_browser", None)
        import tools.sovereign_browser as sb_tool
        yield sb_tool
        sys.modules.pop("tools.sovereign_browser", None)


def test_render_calls_preflight_with_external_api_call(patched_browser_module):
    sb_tool = patched_browser_module
    fake_pf = AsyncMock(return_value=_fake_preflight_result(proceed=True))
    with patch.object(sb_tool, "preflight_check_async", fake_pf):
        result = asyncio.run(sb_tool.sovereign_browser_render(url="https://example.com"))
    assert result.get("actually_rendered") is True, "render real debe ejecutarse cuando proceed=True"
    fake_pf.assert_awaited_once()
    call_kwargs = fake_pf.call_args.kwargs
    assert call_kwargs["operation"] == "external_api_call"
    assert call_kwargs["context_used"]["url"] == "https://example.com"
    assert call_kwargs["context_used"]["function"] == "render"
    assert call_kwargs["hilo_id"] == "manus_ejecutor_sovereign_browser"


def test_render_blocks_when_preflight_proceed_false(patched_browser_module):
    sb_tool = patched_browser_module
    fake_pf = AsyncMock(return_value=_fake_preflight_result(
        proceed=False,
        status="block_critical",
        remediation="dominio bloqueado por catálogo",
    ))
    with patch.object(sb_tool, "preflight_check_async", fake_pf):
        result = asyncio.run(sb_tool.sovereign_browser_render(url="https://example.com"))
    assert result["success"] is False
    assert "preflight" in result["error"].lower()
    assert "block_critical" in result["error"]
    assert "actually_rendered" not in result, "render real NO debe ejecutarse cuando bloqueado"


def test_metrics_calls_preflight(patched_browser_module):
    sb_tool = patched_browser_module
    fake_pf = AsyncMock(return_value=_fake_preflight_result(proceed=True))
    with patch.object(sb_tool, "preflight_check_async", fake_pf):
        result = asyncio.run(sb_tool.sovereign_browser_metrics(url="https://example.com"))
    assert result.get("ttfb_ms") == 100
    fake_pf.assert_awaited_once()
    assert fake_pf.call_args.kwargs["context_used"]["function"] == "metrics"


def test_check_mobile_calls_preflight(patched_browser_module):
    sb_tool = patched_browser_module
    fake_pf = AsyncMock(return_value=_fake_preflight_result(proceed=True))
    with patch.object(sb_tool, "preflight_check_async", fake_pf):
        result = asyncio.run(sb_tool.sovereign_browser_check_mobile(url="https://example.com"))
    assert result.get("has_horizontal_scroll") is False
    fake_pf.assert_awaited_once()
    assert fake_pf.call_args.kwargs["context_used"]["function"] == "check_mobile"


def test_render_degrades_gracefully_on_memento_error(patched_browser_module):
    """Si preflight lanza MementoPreflightError, render continúa sin bloquear."""
    sb_tool = patched_browser_module
    fake_pf = AsyncMock(side_effect=sb_tool.MementoPreflightError("HTTP 503 simulated"))
    with patch.object(sb_tool, "preflight_check_async", fake_pf):
        result = asyncio.run(sb_tool.sovereign_browser_render(url="https://example.com"))
    # Debe continuar con render real (degraded mode)
    assert result.get("actually_rendered") is True


def test_render_degrades_gracefully_on_unexpected_exception(patched_browser_module):
    """Si preflight lanza una excepción inesperada, render continúa."""
    sb_tool = patched_browser_module
    fake_pf = AsyncMock(side_effect=RuntimeError("network unreachable"))
    with patch.object(sb_tool, "preflight_check_async", fake_pf):
        result = asyncio.run(sb_tool.sovereign_browser_render(url="https://example.com"))
    assert result.get("actually_rendered") is True


def test_render_no_preflight_when_memento_unavailable(patched_browser_module):
    """Si _MEMENTO_AVAILABLE=False, no llama preflight y opera normal."""
    sb_tool = patched_browser_module
    fake_pf = AsyncMock(return_value=_fake_preflight_result(proceed=False))
    with patch.object(sb_tool, "_MEMENTO_AVAILABLE", False), \
         patch.object(sb_tool, "preflight_check_async", fake_pf):
        result = asyncio.run(sb_tool.sovereign_browser_render(url="https://example.com"))
    fake_pf.assert_not_awaited()
    assert result.get("actually_rendered") is True


def test_render_passes_extra_context(patched_browser_module):
    sb_tool = patched_browser_module
    fake_pf = AsyncMock(return_value=_fake_preflight_result(proceed=True))
    with patch.object(sb_tool, "preflight_check_async", fake_pf):
        asyncio.run(sb_tool.sovereign_browser_render(
            url="https://example.com",
            viewport_preset="mobile",
            full_page=False,
            capture_html=False,
        ))
    ctx = fake_pf.call_args.kwargs["context_used"]
    assert ctx["viewport_preset"] == "mobile"
    assert ctx["full_page"] is False
    assert ctx["capture_html"] is False
