"""Tests Sprint 84.6 - Browser Automation Soberano.

Cubre:
- Refactor _is_blocked_url (urlparse + ipaddress, no substring crudo)
- set_viewport runtime
- _collect_web_vitals shape
- SovereignBrowser API (sin Playwright real - se mockea)
- RenderResult / MetricsResult / CheckMobileResult dataclasses
- Tool sovereign_browser_render dispatch
- Backward compat: BLOCKED_DOMAINS sigue exportandose

NO requiere Playwright instalado (todos los tests son unitarios + mocks).
"""
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.browser_automation import (
    BLOCKED_DOMAINS,
    BLOCKED_HOSTNAMES,
    BLOCKED_HOSTNAME_SUFFIXES,
    DEFAULT_VIEWPORT,
    BrowserAutomation,
    BrowserResult,
)
from kernel.browser import (
    DEFAULT_DESKTOP_VIEWPORT,
    MOBILE_VIEWPORT,
    CheckMobileResult,
    MetricsResult,
    RenderResult,
    SovereignBrowser,
)


# ============================================================================
# 1. _is_blocked_url - regression contra el bug de substring crudo
# ============================================================================


class TestIsBlockedUrl:
    """Sprint 84.6 - validacion estructurada (urlparse + ipaddress)."""

    def setup_method(self):
        self.b = BrowserAutomation()

    # Casos que DEBEN bloquearse
    def test_blocks_localhost(self):
        assert self.b._is_blocked_url("http://localhost:3000") is True

    def test_blocks_localhost_uppercase(self):
        assert self.b._is_blocked_url("http://LOCALHOST/admin") is True

    def test_blocks_loopback_ipv4(self):
        assert self.b._is_blocked_url("http://127.0.0.1:8080") is True

    def test_blocks_loopback_ipv4_alt(self):
        assert self.b._is_blocked_url("http://127.1.2.3") is True

    def test_blocks_unspecified_ipv4(self):
        assert self.b._is_blocked_url("http://0.0.0.0:5000") is True

    def test_blocks_private_10_x(self):
        assert self.b._is_blocked_url("http://10.0.0.1/admin") is True

    def test_blocks_private_192_168(self):
        assert self.b._is_blocked_url("http://192.168.1.1") is True

    def test_blocks_private_172_16(self):
        assert self.b._is_blocked_url("http://172.16.0.1") is True

    def test_blocks_link_local_169_254(self):
        assert self.b._is_blocked_url("http://169.254.169.254/metadata") is True

    def test_blocks_local_suffix(self):
        assert self.b._is_blocked_url("http://router.local") is True

    def test_blocks_internal_suffix(self):
        assert self.b._is_blocked_url("http://api.internal/v1") is True

    def test_blocks_lan_suffix(self):
        assert self.b._is_blocked_url("http://printer.lan") is True

    def test_blocks_non_http_scheme(self):
        assert self.b._is_blocked_url("file:///etc/passwd") is True
        assert self.b._is_blocked_url("ftp://example.com") is True
        assert self.b._is_blocked_url("javascript:alert(1)") is True

    def test_blocks_loopback_ipv6(self):
        assert self.b._is_blocked_url("http://[::1]/admin") is True

    def test_blocks_empty_url(self):
        assert self.b._is_blocked_url("") is True

    def test_blocks_garbage_url(self):
        assert self.b._is_blocked_url("not a url at all") is True

    # Casos que NO deben bloquearse - regression del bug del substring
    def test_allows_public_url(self):
        assert self.b._is_blocked_url("https://example.com") is False
        assert self.b._is_blocked_url("https://google.com") is False

    def test_allows_path_with_dotted_numbers(self):
        """Bug original: '10.' in 'blog.com/210.html' matcheaba.

        Con urlparse, el path no se considera para bloqueo.
        """
        assert self.b._is_blocked_url("https://blog.com/post/210.html") is False

    def test_allows_url_with_192_in_path(self):
        assert self.b._is_blocked_url("https://example.com/api/v1/192") is False

    def test_allows_url_with_127_in_path(self):
        assert self.b._is_blocked_url("https://gist.github.com/127001") is False

    def test_allows_subdomain_localhost(self):
        """'localhost.evil.com' NO debe bloquearse - hostname check es exacto."""
        # Aunque empiece con 'localhost', el hostname completo es publico
        assert self.b._is_blocked_url("https://localhost.evil.com") is False

    def test_allows_public_ip(self):
        assert self.b._is_blocked_url("http://8.8.8.8") is False
        assert self.b._is_blocked_url("http://1.1.1.1") is False


# ============================================================================
# 2. set_viewport runtime (requerimiento Critic Visual)
# ============================================================================


class TestSetViewport:
    """Sprint 84.6 - set_viewport sin reinicializar."""

    @pytest.mark.asyncio
    async def test_set_viewport_without_init(self):
        """Sin init, set_viewport retorna error."""
        b = BrowserAutomation()
        result = await b.set_viewport(375, 812)
        assert result.success is False
        assert "not initialized" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_set_viewport_invalid_dimensions(self):
        """Dimensiones invalidas (<=0) retornan error."""
        b = BrowserAutomation()
        b._initialized = True
        b._page = MagicMock()
        result = await b.set_viewport(0, 100)
        assert result.success is False
        result = await b.set_viewport(100, -1)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_set_viewport_success(self):
        """set_viewport exitoso actualiza self.viewport."""
        b = BrowserAutomation()
        b._initialized = True
        page = MagicMock()
        page.set_viewport_size = AsyncMock(return_value=None)
        b._page = page
        result = await b.set_viewport(375, 812)
        assert result.success is True
        assert b.viewport == {"width": 375, "height": 812}
        assert result.data == {"width": 375, "height": 812}
        page.set_viewport_size.assert_called_once_with({"width": 375, "height": 812})


# ============================================================================
# 3. _collect_web_vitals
# ============================================================================


class TestCollectWebVitals:
    """Sprint 84.6 - captura JS shim de performance.timing."""

    @pytest.mark.asyncio
    async def test_returns_zeros_without_init(self):
        b = BrowserAutomation()
        m = await b._collect_web_vitals()
        assert m == {"ttfb_ms": 0, "lcp_ms": 0, "load_time_ms": 0}

    @pytest.mark.asyncio
    async def test_returns_metrics_dict_shape(self):
        """Aun cuando JS evaluacion falle, retorna shape correcto."""
        b = BrowserAutomation()
        b._initialized = True
        page = MagicMock()
        page.evaluate = AsyncMock(
            return_value={"ttfb_ms": 123, "lcp_ms": 456, "load_time_ms": 789}
        )
        b._page = page
        m = await b._collect_web_vitals()
        assert m["ttfb_ms"] == 123
        assert m["lcp_ms"] == 456
        assert m["load_time_ms"] == 789

    @pytest.mark.asyncio
    async def test_returns_zeros_on_evaluate_error(self):
        b = BrowserAutomation()
        b._initialized = True
        page = MagicMock()
        page.evaluate = AsyncMock(side_effect=RuntimeError("boom"))
        b._page = page
        m = await b._collect_web_vitals()
        assert m == {"ttfb_ms": 0, "lcp_ms": 0, "load_time_ms": 0}


# ============================================================================
# 4. Backward compat: BLOCKED_DOMAINS sigue importable
# ============================================================================


class TestBackwardCompat:
    """Tests SP11 originales no deben romperse."""

    def test_blocked_domains_alias_exists(self):
        assert BLOCKED_DOMAINS is not None
        assert "localhost" in BLOCKED_DOMAINS
        assert "127.0.0.1" in BLOCKED_DOMAINS

    def test_blocked_hostnames_constant(self):
        assert "localhost" in BLOCKED_HOSTNAMES

    def test_blocked_suffixes_tuple(self):
        assert ".local" in BLOCKED_HOSTNAME_SUFFIXES
        assert ".internal" in BLOCKED_HOSTNAME_SUFFIXES

    def test_default_viewport_unchanged(self):
        assert DEFAULT_VIEWPORT["width"] == 1280
        assert DEFAULT_VIEWPORT["height"] == 720


# ============================================================================
# 5. SovereignBrowser dataclasses
# ============================================================================


class TestRenderResult:
    def test_default_values(self):
        r = RenderResult(success=True, url="https://x")
        assert r.success is True
        assert r.url == "https://x"
        assert r.metrics == {}
        assert r.viewport == {}

    def test_to_dict_includes_html_length(self):
        r = RenderResult(success=True, url="https://x", html="<html>test</html>")
        d = r.to_dict()
        assert d["html_length"] == 17
        assert d["url"] == "https://x"


class TestMetricsResult:
    def test_to_dict(self):
        r = MetricsResult(
            success=True, url="https://x", ttfb_ms=100, lcp_ms=500, load_time_ms=1000
        )
        d = r.to_dict()
        assert d["ttfb_ms"] == 100
        assert d["lcp_ms"] == 500


class TestCheckMobileResult:
    def test_default_viewport_width(self):
        r = CheckMobileResult(success=True, url="https://x")
        assert r.viewport_width == 375

    def test_to_dict_overflow_flag(self):
        r = CheckMobileResult(
            success=True,
            url="https://x",
            has_horizontal_scroll=True,
            document_width=500,
        )
        d = r.to_dict()
        assert d["has_horizontal_scroll"] is True
        assert d["document_width"] == 500


# ============================================================================
# 6. Viewport presets
# ============================================================================


class TestViewportPresets:
    def test_desktop_preset(self):
        assert DEFAULT_DESKTOP_VIEWPORT["width"] == 1280
        assert DEFAULT_DESKTOP_VIEWPORT["height"] == 720

    def test_mobile_preset_iphone_13_pro(self):
        assert MOBILE_VIEWPORT["width"] == 375
        assert MOBILE_VIEWPORT["height"] == 812


# ============================================================================
# 7. SovereignBrowser flow con browser mockeado
# ============================================================================


class TestSovereignBrowserFlow:
    """SovereignBrowser delega a BrowserAutomation - testeamos flow con mocks."""

    @pytest.mark.asyncio
    async def test_render_navigate_failure_returns_error(self):
        """Si navigate falla, render retorna RenderResult con error."""
        sb = SovereignBrowser()
        with patch("kernel.browser.sovereign_browser.BrowserAutomation") as MockBA:
            instance = MagicMock()
            instance.initialize = AsyncMock(
                return_value=BrowserResult(success=True, data="ok")
            )
            instance.navigate = AsyncMock(
                return_value=BrowserResult(success=False, error="dns_failed")
            )
            instance.close = AsyncMock(return_value=BrowserResult(success=True))
            MockBA.return_value = instance

            res = await sb.render(url="https://broken.example")
            assert res.success is False
            assert "dns_failed" in (res.error or "")

    @pytest.mark.asyncio
    async def test_metrics_returns_web_vitals_from_navigate_data(self):
        sb = SovereignBrowser()
        with patch("kernel.browser.sovereign_browser.BrowserAutomation") as MockBA:
            instance = MagicMock()
            instance.initialize = AsyncMock(
                return_value=BrowserResult(success=True)
            )
            instance.navigate = AsyncMock(
                return_value=BrowserResult(
                    success=True,
                    data={
                        "ttfb_ms": 100,
                        "lcp_ms": 500,
                        "load_time_ms": 1500,
                        "status_code": 200,
                    },
                )
            )
            instance.close = AsyncMock(return_value=BrowserResult(success=True))
            MockBA.return_value = instance

            res = await sb.metrics(url="https://example.com")
            assert res.success is True
            assert res.ttfb_ms == 100
            assert res.lcp_ms == 500
            assert res.load_time_ms == 1500
            assert res.status_code == 200

    @pytest.mark.asyncio
    async def test_check_mobile_uses_mobile_viewport(self):
        sb = SovereignBrowser()
        captured_viewports = []
        with patch("kernel.browser.sovereign_browser.BrowserAutomation") as MockBA:
            def factory(*args, **kwargs):
                captured_viewports.append(kwargs.get("viewport"))
                instance = MagicMock()
                instance.initialize = AsyncMock(
                    return_value=BrowserResult(success=True)
                )
                instance.navigate = AsyncMock(
                    return_value=BrowserResult(
                        success=True, data={"status_code": 200}
                    )
                )
                page = MagicMock()
                page.evaluate = AsyncMock(return_value=400)  # > 375 -> overflow
                instance._page = page
                instance.screenshot = AsyncMock(
                    return_value=BrowserResult(
                        success=True, screenshot_path="/tmp/m.png"
                    )
                )
                instance.close = AsyncMock(return_value=BrowserResult(success=True))
                return instance
            MockBA.side_effect = factory

            res = await sb.check_mobile(url="https://example.com")
            assert res.success is True
            assert captured_viewports[0] == MOBILE_VIEWPORT
            assert res.has_horizontal_scroll is True
            assert res.document_width == 400


# ============================================================================
# 8. Tool dispatch
# ============================================================================


class TestSovereignBrowserTool:
    """Validacion del tool tools/sovereign_browser.py."""

    def test_tool_module_imports(self):
        from tools.sovereign_browser import (
            SOVEREIGN_BROWSER_TOOL_SPEC,
            sovereign_browser_check_mobile,
            sovereign_browser_metrics,
            sovereign_browser_render,
        )
        assert callable(sovereign_browser_render)
        assert callable(sovereign_browser_metrics)
        assert callable(sovereign_browser_check_mobile)
        assert SOVEREIGN_BROWSER_TOOL_SPEC["name"] == "sovereign_browser_render"

    def test_tool_spec_has_required_fields(self):
        from tools.sovereign_browser import SOVEREIGN_BROWSER_TOOL_SPEC
        assert "description" in SOVEREIGN_BROWSER_TOOL_SPEC
        params = SOVEREIGN_BROWSER_TOOL_SPEC["parameters"]
        assert "url" in params["properties"]
        assert "url" in params["required"]
