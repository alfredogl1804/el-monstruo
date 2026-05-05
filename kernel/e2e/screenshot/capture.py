"""
Sprint 87.2 Bloque 2 — Screenshot capture con Playwright headless.

Diseño:
- Playwright Chromium headless (ya en requirements.txt)
- Full-page screenshot (no solo viewport)
- Storage: /tmp/monstruo_screenshots/{run_id}.png (default) o $MONSTRUO_SCREENSHOT_DIR
- Timeout duro 30s por screenshot
- Fallback determinístico: si Playwright falla, devuelve placeholder con flag
  `playwright_unavailable=True` para que Critic Visual sepa que no debe procesar.

Capa Memento aplicada: el screenshot puede contener datos generados por el
pipeline. Validación post-captura limita el tamaño máximo (5 MB).

Brand DNA en errores: e2e_screenshot_*_failed.
"""
from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel, ConfigDict, Field

logger = structlog.get_logger("kernel.e2e.screenshot.capture")

DEFAULT_DIR = "/tmp/monstruo_screenshots"
DEFAULT_TIMEOUT_S = 30
MAX_SCREENSHOT_BYTES = 5 * 1024 * 1024  # 5 MB cap


# ── Errores con identidad ────────────────────────────────────────────────────


class ScreenshotCaptureFailed(Exception):
    """Brand DNA: e2e_screenshot_capture_failed."""

    code = "e2e_screenshot_capture_failed"


class ScreenshotPlaywrightUnavailable(ScreenshotCaptureFailed):
    code = "e2e_screenshot_playwright_unavailable"


class ScreenshotTimeout(ScreenshotCaptureFailed):
    code = "e2e_screenshot_timeout"


class ScreenshotTooLarge(ScreenshotCaptureFailed):
    code = "e2e_screenshot_too_large"


# ── Schema ───────────────────────────────────────────────────────────────────


class ScreenshotResult(BaseModel):
    """Resultado del screenshot capture."""

    model_config = ConfigDict(extra="forbid")

    deploy_url: str
    screenshot_path: Optional[str] = Field(None, description="Ruta local PNG")
    bytes_captured: int = Field(0, description="Tamaño del PNG")
    captured_at: str
    duration_ms: int
    playwright_available: bool = True
    fallback_reason: Optional[str] = None


# ── Capture core ─────────────────────────────────────────────────────────────


def _get_storage_dir() -> Path:
    target = Path(os.environ.get("MONSTRUO_SCREENSHOT_DIR", DEFAULT_DIR))
    target.mkdir(parents=True, exist_ok=True)
    return target


async def _capture_with_playwright(
    *, url: str, output_path: Path, timeout_s: int
) -> int:
    """Invoca Playwright; retorna bytes escritos."""
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise ScreenshotPlaywrightUnavailable(
            f"e2e_screenshot_playwright_unavailable: paquete no instalado — {e!s}"
        ) from e

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    user_agent="MonstruoScreenshot/1.0 (privacy-first)",
                )
                page = await context.new_page()
                await page.goto(url, timeout=timeout_s * 1000, wait_until="domcontentloaded")
                # Pequeño settle para CSS/fonts
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass  # tolerar si nunca llega a idle
                await page.screenshot(path=str(output_path), full_page=True, type="png")
            finally:
                await browser.close()
    except ScreenshotPlaywrightUnavailable:
        raise
    except asyncio.TimeoutError as e:
        raise ScreenshotTimeout(
            f"e2e_screenshot_timeout: {url} — más de {timeout_s}s"
        ) from e
    except Exception as e:
        raise ScreenshotCaptureFailed(
            f"e2e_screenshot_capture_failed: {url} — {e!s}"
        ) from e

    if not output_path.exists():
        raise ScreenshotCaptureFailed(
            f"e2e_screenshot_capture_failed: PNG no se escribió en {output_path}"
        )

    size = output_path.stat().st_size
    if size > MAX_SCREENSHOT_BYTES:
        # Capa Memento: rechazar screenshots desproporcionados
        output_path.unlink(missing_ok=True)
        raise ScreenshotTooLarge(
            f"e2e_screenshot_too_large: {size} bytes > {MAX_SCREENSHOT_BYTES} cap"
        )
    return size


# ── API pública ──────────────────────────────────────────────────────────────


async def capture_screenshot(
    *,
    deploy_url: str,
    run_id: str,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> ScreenshotResult:
    """
    Captura full-page screenshot de la URL deployada.

    Si la URL es heuristic preview o Playwright no está disponible →
    devuelve resultado con `playwright_available=False` y razón explícita.
    """
    started = time.perf_counter()
    storage = _get_storage_dir()
    output_path = storage / f"{run_id}.png"

    # Si la URL es preview interna del Monstruo, no intentamos screenshot
    if "preview.el-monstruo.dev" in deploy_url:
        return ScreenshotResult(
            deploy_url=deploy_url,
            screenshot_path=None,
            bytes_captured=0,
            captured_at=datetime.now(timezone.utc).isoformat(),
            duration_ms=int((time.perf_counter() - started) * 1000),
            playwright_available=False,
            fallback_reason="heuristic_preview_url_skipped",
        )

    try:
        bytes_written = await _capture_with_playwright(
            url=deploy_url, output_path=output_path, timeout_s=timeout_s
        )
        result = ScreenshotResult(
            deploy_url=deploy_url,
            screenshot_path=str(output_path),
            bytes_captured=bytes_written,
            captured_at=datetime.now(timezone.utc).isoformat(),
            duration_ms=int((time.perf_counter() - started) * 1000),
            playwright_available=True,
            fallback_reason=None,
        )
        logger.info(
            "e2e_screenshot_captured",
            run_id=run_id,
            url=deploy_url,
            bytes=bytes_written,
            duration_ms=result.duration_ms,
        )
        return result
    except ScreenshotCaptureFailed as e:
        logger.warning(
            "e2e_screenshot_fallback",
            run_id=run_id,
            url=deploy_url,
            error=str(e),
            code=e.code,
        )
        return ScreenshotResult(
            deploy_url=deploy_url,
            screenshot_path=None,
            bytes_captured=0,
            captured_at=datetime.now(timezone.utc).isoformat(),
            duration_ms=int((time.perf_counter() - started) * 1000),
            playwright_available=False,
            fallback_reason=e.code,
        )
