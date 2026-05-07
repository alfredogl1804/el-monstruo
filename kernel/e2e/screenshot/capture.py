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


async def _wait_for_github_pages_ready(
    *, url: str, max_wait_s: int = 90, marker: str = "<h1"
) -> bool:
    """Sprint 88.1: GitHub Pages tarda 30-90s en propagar nuevos paths.

    Polea la URL hasta que devuelva HTTP 200 + contenga `marker` (default `<h1`)
    indicando que la landing renderizada está sirviéndose, no un 404 cacheado.
    Retorna True si listo, False si timeout. NO bloquea screenshot — si False, se
    captura igual y Gemini reporta el estado real (mejor que un sleep ciego).
    """
    if "github.io" not in url:
        return True  # solo aplica a GitHub Pages
    import urllib.request
    deadline = time.perf_counter() + max_wait_s
    poll_interval_s = 5
    while time.perf_counter() < deadline:
        try:
            def _fetch() -> tuple[int, str]:
                req = urllib.request.Request(url, headers={"User-Agent": "MonstruoScreenshot/1.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    return resp.status, resp.read(8192).decode("utf-8", errors="ignore")
            status, body = await asyncio.to_thread(_fetch)
            if status == 200 and marker in body:
                logger.info("e2e_github_pages_ready", url=url, waited_s=int(max_wait_s - (deadline - time.perf_counter())))
                return True
        except Exception:
            pass
        await asyncio.sleep(poll_interval_s)
    logger.warning("e2e_github_pages_timeout", url=url, max_wait_s=max_wait_s)
    return False


async def _capture_with_playwright(
    *, url: str, output_path: Path, timeout_s: int
) -> int:
    """Invoca Playwright; retorna bytes escritos."""
    # Sprint 88.1: esperar propagación GitHub Pages antes de capturar
    await _wait_for_github_pages_ready(url=url, max_wait_s=90)

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
                # Sprint 88.1 v4: wait_until="load" (no "domcontentloaded") para
                # que CSS externo (style.css linkeado) se descargue y aplique
                # ANTES del screenshot. Si solo esperáramos DOM, capturaríamos
                # texto sin estilos = Gemini ve "wireframe vacío".
                await page.goto(url, timeout=timeout_s * 1000, wait_until="load")
                # Wait explícito por h1 visible con texto real (>10 chars)
                try:
                    await page.wait_for_function(
                        """() => {
                            const h1 = document.querySelector('h1');
                            return h1 && h1.textContent && h1.textContent.trim().length > 10;
                        }""",
                        timeout=8000,
                    )
                except Exception:
                    pass  # capturamos igual; Gemini reportará lo real
                # Settle adicional para fonts/imágenes
                try:
                    await page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                # Sprint 88.2 c: esperar a que document.fonts estén LOADED.
                # Sin esto, Chromium puede pintar el texto con un fallback
                # invisible/bitmap-vacío si la web font (Inter) aún no terminó
                # de descargarse. Esto era la causa raz de "página vacía".
                try:
                    await page.evaluate("""async () => {
                        if (document.fonts && document.fonts.ready) {
                            await document.fonts.ready;
                        }
                    }""")
                except Exception:
                    pass
                # Sleep final para que browser termine compositing
                await asyncio.sleep(1.5)
                # Sprint 88.2 debug: log de qué ve Playwright realmente
                # (h1 text + content length + has_inline_style) — clave para
                # detectar bug de captura vs render.
                try:
                    diag = await page.evaluate("""() => ({
                        h1_text: (document.querySelector('h1')?.textContent || '').slice(0, 80),
                        body_text_length: (document.body?.innerText || '').length,
                        has_inline_style: !!document.querySelector('style'),
                        has_external_css: !!document.querySelector('link[rel=\"stylesheet\"]'),
                        cta_count: document.querySelectorAll('a.btn, button').length,
                        title: document.title.slice(0, 80),
                    })""")
                    logger.info(
                        "e2e_screenshot_pre_capture_diag",
                        url=url,
                        h1_text=diag.get("h1_text"),
                        body_len=diag.get("body_text_length"),
                        inline_style=diag.get("has_inline_style"),
                        external_css=diag.get("has_external_css"),
                        cta_count=diag.get("cta_count"),
                        title=diag.get("title"),
                    )
                except Exception as _diag_err:
                    logger.warning("e2e_screenshot_diag_failed", error=str(_diag_err))
                await page.screenshot(path=str(output_path), full_page=True, type="png")
                # Sprint 88.2 b: también capturar SOLO viewport (lo que Gemini
                # "ve" si el screenshot full_page incluye contenido vacío abajo)
                viewport_path = str(output_path).replace(".png", "_viewport.png")
                try:
                    await page.screenshot(path=viewport_path, full_page=False, type="png")
                except Exception:
                    viewport_path = None
            finally:
                await browser.close()

        # Sprint 88.2 b: subir el screenshot a un servicio público para inspección
        # humana del bug de captura. Probamos en orden: catbox.moe → tmpfiles.org
        # (0x0.st devolvió 503). URL queda en logs estructurados.
        try:
            import urllib.request
            def _upload_catbox(path: str) -> str | None:
                with open(path, "rb") as f:
                    body = f.read()
                boundary = "----monstruoboundary7777"
                payload = (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="reqtype"\r\n\r\nfileupload\r\n'
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="fileToUpload"; filename="shot.png"\r\n'
                    f"Content-Type: image/png\r\n\r\n"
                ).encode() + body + f"\r\n--{boundary}--\r\n".encode()
                req = urllib.request.Request(
                    "https://catbox.moe/user/api.php",
                    data=payload,
                    headers={
                        "Content-Type": f"multipart/form-data; boundary={boundary}",
                        "User-Agent": "MonstruoScreenshotDebug/1.0 (sprint88.2)",
                    },
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    out = resp.read().decode().strip()
                    return out if out.startswith("http") else None
            def _upload_tmpfiles(path: str) -> str | None:
                with open(path, "rb") as f:
                    body = f.read()
                boundary = "----monstruoboundary7777"
                payload = (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="file"; filename="shot.png"\r\n'
                    f"Content-Type: image/png\r\n\r\n"
                ).encode() + body + f"\r\n--{boundary}--\r\n".encode()
                req = urllib.request.Request(
                    "https://tmpfiles.org/api/v1/upload",
                    data=payload,
                    headers={
                        "Content-Type": f"multipart/form-data; boundary={boundary}",
                        "User-Agent": "MonstruoScreenshotDebug/1.0 (sprint88.2)",
                    },
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    import json as _json
                    out = _json.loads(resp.read().decode())
                    return (out.get("data") or {}).get("url")
            def _upload(path: str) -> str | None:
                for fn in (_upload_catbox, _upload_tmpfiles):
                    try:
                        u = fn(path)
                        if u:
                            return u
                    except Exception:
                        continue
                return None
            full_url = await asyncio.to_thread(_upload, str(output_path))
            viewport_url = None
            if viewport_path:
                viewport_url = await asyncio.to_thread(_upload, viewport_path)
            logger.info(
                "e2e_screenshot_uploaded_for_inspection",
                full_page_url=full_url,
                viewport_url=viewport_url,
            )
        except Exception as _up_err:
            logger.warning("e2e_screenshot_upload_failed", error=str(_up_err))
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
