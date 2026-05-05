"""
Sprint 87.2 Bloque 2 — Screenshot capture para Critic Visual.

Playwright headless. Privacy-first: cero servicios externos pagados.
"""
from kernel.e2e.screenshot.capture import (
    ScreenshotCaptureFailed,
    ScreenshotResult,
    capture_screenshot,
)

__all__ = ["ScreenshotCaptureFailed", "ScreenshotResult", "capture_screenshot"]
