"""
Sprint 87.2 Bloque 2 — Tests para kernel/e2e/screenshot/capture.py

Coverage:
1. Heuristic preview URL → skip directo sin invocar Playwright
2. ScreenshotResult Pydantic strict
3. Brand DNA en error codes
4. Storage dir se crea
5. Fallback cuando Playwright tira excepción → resultado con playwright_available=False
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from kernel.e2e.screenshot.capture import (
    ScreenshotCaptureFailed,
    ScreenshotPlaywrightUnavailable,
    ScreenshotResult,
    ScreenshotTimeout,
    ScreenshotTooLarge,
    _get_storage_dir,
    capture_screenshot,
)


# ── 1. Preview URL skip ─────────────────────────────────────────────────────


def test_heuristic_preview_url_skipped():
    result = asyncio.run(
        capture_screenshot(
            deploy_url="https://preview.el-monstruo.dev/e2e_999",
            run_id="e2e_test_skip",
        )
    )
    assert isinstance(result, ScreenshotResult)
    assert result.playwright_available is False
    assert result.fallback_reason == "heuristic_preview_url_skipped"
    assert result.screenshot_path is None
    assert result.bytes_captured == 0


# ── 2. Pydantic strict ───────────────────────────────────────────────────────


def test_screenshot_result_strict():
    r = ScreenshotResult(
        deploy_url="https://x.io",
        screenshot_path="/tmp/x.png",
        bytes_captured=1024,
        captured_at="2026-05-05T18:00:00+00:00",
        duration_ms=500,
    )
    assert r.playwright_available is True
    with pytest.raises(Exception):
        ScreenshotResult(
            deploy_url="x",
            captured_at="2026",
            duration_ms=0,
            extra_field="nope",
        )


# ── 3. Brand DNA error codes ─────────────────────────────────────────────────


def test_brand_dna_error_codes():
    assert ScreenshotCaptureFailed.code == "e2e_screenshot_capture_failed"
    assert ScreenshotPlaywrightUnavailable.code == "e2e_screenshot_playwright_unavailable"
    assert ScreenshotTimeout.code == "e2e_screenshot_timeout"
    assert ScreenshotTooLarge.code == "e2e_screenshot_too_large"


# ── 4. Storage dir ──────────────────────────────────────────────────────────


def test_storage_dir_created(tmp_path, monkeypatch):
    monkeypatch.setenv("MONSTRUO_SCREENSHOT_DIR", str(tmp_path / "shots"))
    d = _get_storage_dir()
    assert d.exists()
    assert d.is_dir()


# ── 5. Fallback cuando Playwright tira ──────────────────────────────────────


def test_fallback_when_playwright_fails():
    """Mock _capture_with_playwright para que tire ScreenshotCaptureFailed."""
    fake = AsyncMock(
        side_effect=ScreenshotCaptureFailed("e2e_screenshot_capture_failed: test")
    )
    with patch(
        "kernel.e2e.screenshot.capture._capture_with_playwright",
        new=fake,
    ):
        result = asyncio.run(
            capture_screenshot(
                deploy_url="https://example.com/e2e_test",
                run_id="e2e_fallback_test",
            )
        )
    assert result.playwright_available is False
    assert result.fallback_reason == "e2e_screenshot_capture_failed"
    assert result.bytes_captured == 0


# ── 6. Fallback cuando Playwright no está instalado ──────────────────────────


def test_fallback_when_playwright_unavailable():
    fake = AsyncMock(
        side_effect=ScreenshotPlaywrightUnavailable(
            "e2e_screenshot_playwright_unavailable: not installed"
        )
    )
    with patch(
        "kernel.e2e.screenshot.capture._capture_with_playwright",
        new=fake,
    ):
        result = asyncio.run(
            capture_screenshot(
                deploy_url="https://example.com/x",
                run_id="e2e_unavail",
            )
        )
    assert result.playwright_available is False
    assert result.fallback_reason == "e2e_screenshot_playwright_unavailable"
