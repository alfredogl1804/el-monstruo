"""
Tests for SP11: Browser Automation
====================================
Validates the BrowserAutomation class structure and behavior.
Tests are designed to work WITHOUT Playwright installed (testing stubs/structure).
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.browser_automation import (
    BLOCKED_DOMAINS,
    DEFAULT_TIMEOUT_MS,
    DEFAULT_VIEWPORT,
    BrowserAutomation,
    BrowserResult,
    PageInfo,
)

# ─── BrowserResult Tests ──────────────────────────────────────────────────────


class TestBrowserResult:
    """Tests for BrowserResult dataclass."""

    def test_success_result(self):
        r = BrowserResult(success=True, data="hello")
        assert r.success is True
        assert r.data == "hello"
        assert r.error is None
        assert r.screenshot_path is None

    def test_error_result(self):
        r = BrowserResult(success=False, error="failed")
        assert r.success is False
        assert r.error == "failed"

    def test_screenshot_result(self):
        r = BrowserResult(success=True, screenshot_path="/tmp/shot.png")
        assert r.screenshot_path == "/tmp/shot.png"

    def test_to_dict(self):
        r = BrowserResult(success=True, data="test", screenshot_path="/tmp/x.png")
        d = r.to_dict()
        assert d["success"] is True
        assert d["data"] == "test"
        assert d["screenshot_path"] == "/tmp/x.png"
        assert d["error"] is None


# ─── PageInfo Tests ───────────────────────────────────────────────────────────


class TestPageInfo:
    """Tests for PageInfo dataclass."""

    def test_default_values(self):
        p = PageInfo()
        assert p.url == ""
        assert p.title == ""
        assert p.status_code == 0

    def test_custom_values(self):
        p = PageInfo(url="https://example.com", title="Example", status_code=200)
        assert p.url == "https://example.com"
        assert p.title == "Example"
        assert p.status_code == 200


# ─── BrowserAutomation Class Structure Tests ──────────────────────────────────


class TestBrowserAutomationStructure:
    """Tests that validate the class has the required interface."""

    def test_class_exists(self):
        """BrowserAutomation class exists."""
        assert BrowserAutomation is not None

    def test_has_navigate_method(self):
        """Has navigate(url) method."""
        browser = BrowserAutomation()
        assert hasattr(browser, "navigate")
        assert callable(browser.navigate)

    def test_has_extract_text_method(self):
        """Has extract_text(selector) method."""
        browser = BrowserAutomation()
        assert hasattr(browser, "extract_text")
        assert callable(browser.extract_text)

    def test_has_click_method(self):
        """Has click(selector) method."""
        browser = BrowserAutomation()
        assert hasattr(browser, "click")
        assert callable(browser.click)

    def test_has_fill_form_method(self):
        """Has fill_form(selector, value) method."""
        browser = BrowserAutomation()
        assert hasattr(browser, "fill_form")
        assert callable(browser.fill_form)

    def test_has_screenshot_method(self):
        """Has screenshot() method."""
        browser = BrowserAutomation()
        assert hasattr(browser, "screenshot")
        assert callable(browser.screenshot)

    def test_has_initialize_method(self):
        """Has initialize() method."""
        browser = BrowserAutomation()
        assert hasattr(browser, "initialize")
        assert callable(browser.initialize)

    def test_has_close_method(self):
        """Has close() method."""
        browser = BrowserAutomation()
        assert hasattr(browser, "close")
        assert callable(browser.close)


# ─── Configuration Tests ──────────────────────────────────────────────────────


class TestBrowserConfiguration:
    """Tests for browser configuration."""

    def test_default_headless(self):
        """Default is headless mode."""
        browser = BrowserAutomation()
        assert browser.headless is True

    def test_custom_headless(self):
        """Can override headless."""
        browser = BrowserAutomation(headless=False)
        assert browser.headless is False

    def test_default_timeout(self):
        """Default timeout is 30000ms."""
        browser = BrowserAutomation()
        assert browser.timeout_ms == 30000

    def test_custom_timeout(self):
        """Can override timeout."""
        browser = BrowserAutomation(timeout_ms=5000)
        assert browser.timeout_ms == 5000

    def test_default_viewport(self):
        """Default viewport is 1280x720."""
        browser = BrowserAutomation()
        assert browser.viewport == {"width": 1280, "height": 720}

    def test_custom_viewport(self):
        """Can override viewport."""
        browser = BrowserAutomation(viewport={"width": 1920, "height": 1080})
        assert browser.viewport == {"width": 1920, "height": 1080}

    def test_not_initialized_by_default(self):
        """Browser starts uninitialized."""
        browser = BrowserAutomation()
        assert browser.is_initialized is False

    def test_current_url_empty_by_default(self):
        """Current URL starts empty."""
        browser = BrowserAutomation()
        assert browser.current_url == ""


# ─── Security Tests ───────────────────────────────────────────────────────────


class TestBrowserSecurity:
    """Tests for URL blocking security."""

    def test_blocks_localhost(self):
        """Blocks localhost URLs."""
        browser = BrowserAutomation()
        assert browser._is_blocked_url("http://localhost:3000") is True

    def test_blocks_127_0_0_1(self):
        """Blocks 127.0.0.1."""
        browser = BrowserAutomation()
        assert browser._is_blocked_url("http://127.0.0.1:8080") is True

    def test_blocks_private_ip_10(self):
        """Blocks 10.x.x.x IPs."""
        browser = BrowserAutomation()
        assert browser._is_blocked_url("http://10.0.0.1/admin") is True

    def test_blocks_private_ip_192(self):
        """Blocks 192.168.x.x IPs."""
        browser = BrowserAutomation()
        assert browser._is_blocked_url("http://192.168.1.1") is True

    def test_blocks_private_ip_172(self):
        """Blocks 172.16.x.x IPs."""
        browser = BrowserAutomation()
        assert browser._is_blocked_url("http://172.16.0.1") is True

    def test_allows_public_urls(self):
        """Allows public URLs."""
        browser = BrowserAutomation()
        assert browser._is_blocked_url("https://example.com") is False
        assert browser._is_blocked_url("https://google.com") is False

    def test_blocks_0_0_0_0(self):
        """Blocks 0.0.0.0."""
        browser = BrowserAutomation()
        assert browser._is_blocked_url("http://0.0.0.0:5000") is True


# ─── Uninitialized State Tests ────────────────────────────────────────────────


class TestUninitializedBehavior:
    """Tests that methods return proper errors when browser not initialized."""

    @pytest.mark.asyncio
    async def test_navigate_without_init(self):
        """navigate() returns error when not initialized."""
        browser = BrowserAutomation()
        result = await browser.navigate("https://example.com")
        assert result.success is False
        assert "not initialized" in result.error.lower()

    @pytest.mark.asyncio
    async def test_extract_text_without_init(self):
        """extract_text() returns error when not initialized."""
        browser = BrowserAutomation()
        result = await browser.extract_text("h1")
        assert result.success is False
        assert "not initialized" in result.error.lower()

    @pytest.mark.asyncio
    async def test_click_without_init(self):
        """click() returns error when not initialized."""
        browser = BrowserAutomation()
        result = await browser.click("button")
        assert result.success is False
        assert "not initialized" in result.error.lower()

    @pytest.mark.asyncio
    async def test_fill_form_without_init(self):
        """fill_form() returns error when not initialized."""
        browser = BrowserAutomation()
        result = await browser.fill_form("input", "test")
        assert result.success is False
        assert "not initialized" in result.error.lower()

    @pytest.mark.asyncio
    async def test_screenshot_without_init(self):
        """screenshot() returns error when not initialized."""
        browser = BrowserAutomation()
        result = await browser.screenshot()
        assert result.success is False
        assert "not initialized" in result.error.lower()

    @pytest.mark.asyncio
    async def test_navigate_blocked_url_without_init(self):
        """navigate() blocks URLs even without initialization."""
        browser = BrowserAutomation()
        result = await browser.navigate("http://localhost:3000")
        assert result.success is False
        assert "blocked" in result.error.lower()


# ─── Initialize Tests (without Playwright) ────────────────────────────────────


class TestInitializeWithoutPlaywright:
    """Tests for initialize() when Playwright is not installed."""

    @pytest.mark.asyncio
    async def test_initialize_without_playwright(self):
        """initialize() returns helpful error when Playwright not available."""
        # This test works because Playwright is likely not installed in test env
        browser = BrowserAutomation()
        result = await browser.initialize()
        # Either succeeds (Playwright installed) or fails gracefully
        if not result.success:
            assert "playwright" in result.error.lower() or "install" in result.error.lower()


# ─── Constants Tests ──────────────────────────────────────────────────────────


class TestConstants:
    """Tests for module-level constants."""

    def test_blocked_domains_list(self):
        """BLOCKED_DOMAINS contains expected entries."""
        assert "localhost" in BLOCKED_DOMAINS
        assert "127.0.0.1" in BLOCKED_DOMAINS

    def test_default_timeout(self):
        """DEFAULT_TIMEOUT_MS is reasonable."""
        assert DEFAULT_TIMEOUT_MS >= 5000
        assert DEFAULT_TIMEOUT_MS <= 60000

    def test_default_viewport_dimensions(self):
        """DEFAULT_VIEWPORT has width and height."""
        assert "width" in DEFAULT_VIEWPORT
        assert "height" in DEFAULT_VIEWPORT
        assert DEFAULT_VIEWPORT["width"] > 0
        assert DEFAULT_VIEWPORT["height"] > 0
