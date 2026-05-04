"""kernel.browser.sovereign_browser — Wrapper HTTP-friendly.

Sprint 84.6 — Browser Automation Soberano.

Encapsula `BrowserAutomation` para los endpoints `/v1/browser/*`. Cada operacion:
1. Crea un browser efimero
2. Navega a la URL
3. Ejecuta la accion (screenshot, metrics, mobile check)
4. Cierra el browser y libera recursos

Nada de estado compartido entre llamadas (HTTP es stateless). Si en el futuro
queremos un pool warm de browsers, se agrega aqui sin cambiar la API publica.

Storage de screenshots:
- Si SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY estan configurados, sube el PNG
  a Supabase Storage bucket `screenshots` y devuelve URL publica.
- Fallback: devuelve path local (/tmp/...). Graceful degradation.

Patron de credenciales: lectura via os.environ.get() en cada uso (NO cache al
boot). Cumple disciplina del Hilo Catastro / Sprint 85 Bloque 4.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

from kernel.browser_automation import BrowserAutomation, BrowserResult

logger = structlog.get_logger("kernel.browser.sovereign")


# --- Viewport presets ----------------------------------------------------

DEFAULT_DESKTOP_VIEWPORT = {"width": 1280, "height": 720}
MOBILE_VIEWPORT = {"width": 375, "height": 812}  # iPhone 13 Pro


# --- Result dataclasses --------------------------------------------------


@dataclass
class RenderResult:
    """Resultado de render(): screenshot + HTML + metrics."""
    success: bool
    url: str
    screenshot_url: Optional[str] = None  # public URL si subio a Supabase
    screenshot_local_path: Optional[str] = None  # path local en sandbox
    html: Optional[str] = None
    title: Optional[str] = None
    status_code: int = 0
    metrics: dict[str, int] = field(default_factory=dict)
    viewport: dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "url": self.url,
            "screenshot_url": self.screenshot_url,
            "screenshot_local_path": self.screenshot_local_path,
            "html_length": len(self.html or ""),
            "html": self.html,
            "title": self.title,
            "status_code": self.status_code,
            "metrics": self.metrics,
            "viewport": self.viewport,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


@dataclass
class MetricsResult:
    """Resultado de metrics(): solo Web Vitals."""
    success: bool
    url: str
    ttfb_ms: int = 0
    lcp_ms: int = 0
    load_time_ms: int = 0
    status_code: int = 0
    error: Optional[str] = None
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "url": self.url,
            "ttfb_ms": self.ttfb_ms,
            "lcp_ms": self.lcp_ms,
            "load_time_ms": self.load_time_ms,
            "status_code": self.status_code,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


@dataclass
class CheckMobileResult:
    """Resultado de check_mobile(): screenshot mobile + chequeo overflow."""
    success: bool
    url: str
    screenshot_url: Optional[str] = None
    screenshot_local_path: Optional[str] = None
    has_horizontal_scroll: bool = False
    document_width: int = 0
    viewport_width: int = MOBILE_VIEWPORT["width"]
    error: Optional[str] = None
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "url": self.url,
            "screenshot_url": self.screenshot_url,
            "screenshot_local_path": self.screenshot_local_path,
            "has_horizontal_scroll": self.has_horizontal_scroll,
            "document_width": self.document_width,
            "viewport_width": self.viewport_width,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


# --- SovereignBrowser ----------------------------------------------------


class SovereignBrowser:
    """Wrapper HTTP-friendly sobre BrowserAutomation.

    Cada metodo abre y cierra un browser efimero. Sin estado compartido.

    Uso desde un endpoint:
        sb = SovereignBrowser()
        res = await sb.render("https://example.com")
        return res.to_dict()
    """

    def __init__(self, headless: bool = True, timeout_ms: Optional[int] = None):
        self.headless = headless
        self.timeout_ms = timeout_ms

    async def _open(self, viewport: Optional[dict[str, int]] = None) -> BrowserAutomation:
        kwargs: dict[str, Any] = {"headless": self.headless}
        if self.timeout_ms is not None:
            kwargs["timeout_ms"] = self.timeout_ms
        if viewport is not None:
            kwargs["viewport"] = viewport
        browser = BrowserAutomation(**kwargs)
        init = await browser.initialize()
        if not init.success:
            raise RuntimeError(f"browser_init_failed: {init.error}")
        return browser

    async def render(
        self,
        url: str,
        viewport: Optional[dict[str, int]] = None,
        full_page: bool = True,
        capture_html: bool = True,
    ) -> RenderResult:
        """Renderiza URL, captura screenshot + HTML + metrics."""
        t0 = time.time()
        viewport = viewport or DEFAULT_DESKTOP_VIEWPORT
        browser: Optional[BrowserAutomation] = None
        try:
            browser = await self._open(viewport=viewport)

            nav = await browser.navigate(url)
            if not nav.success:
                return RenderResult(
                    success=False,
                    url=url,
                    viewport=viewport,
                    error=nav.error or "navigate_failed",
                    duration_ms=int((time.time() - t0) * 1000),
                )

            data = nav.data if isinstance(nav.data, dict) else {}
            title = data.get("title", "")
            status_code = data.get("status_code", 0)
            metrics = {
                "ttfb_ms": data.get("ttfb_ms", 0),
                "lcp_ms": data.get("lcp_ms", 0),
                "load_time_ms": data.get("load_time_ms", 0),
            }

            # Screenshot
            shot_path = f"/tmp/sovereign_{int(time.time() * 1000)}.png"
            shot = await browser.screenshot(path=shot_path, full_page=full_page)

            screenshot_url: Optional[str] = None
            if shot.success and shot.screenshot_path:
                # Intentar subir a Supabase Storage
                screenshot_url = await _upload_to_supabase_storage(
                    local_path=shot.screenshot_path,
                    storage_subpath=f"renders/{int(time.time() * 1000)}.png",
                )

            # HTML opcional (puede ser pesado)
            html: Optional[str] = None
            if capture_html and browser._page is not None:
                try:
                    html = await browser._page.content()
                except Exception as e:
                    logger.warning("html_capture_failed", error=str(e)[:100])

            return RenderResult(
                success=True,
                url=url,
                screenshot_url=screenshot_url,
                screenshot_local_path=shot.screenshot_path if shot.success else None,
                html=html,
                title=title,
                status_code=status_code,
                metrics=metrics,
                viewport=viewport,
                duration_ms=int((time.time() - t0) * 1000),
            )

        except Exception as e:
            logger.error("sovereign_render_failed", url=url, error=str(e)[:200])
            return RenderResult(
                success=False,
                url=url,
                viewport=viewport or DEFAULT_DESKTOP_VIEWPORT,
                error=str(e)[:300],
                duration_ms=int((time.time() - t0) * 1000),
            )
        finally:
            if browser is not None:
                try:
                    await browser.close()
                except Exception:
                    pass

    async def metrics(self, url: str) -> MetricsResult:
        """Solo navegacion + Web Vitals (sin screenshot ni HTML)."""
        t0 = time.time()
        browser: Optional[BrowserAutomation] = None
        try:
            browser = await self._open()
            nav = await browser.navigate(url)
            if not nav.success:
                return MetricsResult(
                    success=False,
                    url=url,
                    error=nav.error or "navigate_failed",
                    duration_ms=int((time.time() - t0) * 1000),
                )
            data = nav.data if isinstance(nav.data, dict) else {}
            return MetricsResult(
                success=True,
                url=url,
                ttfb_ms=data.get("ttfb_ms", 0),
                lcp_ms=data.get("lcp_ms", 0),
                load_time_ms=data.get("load_time_ms", 0),
                status_code=data.get("status_code", 0),
                duration_ms=int((time.time() - t0) * 1000),
            )
        except Exception as e:
            logger.error("sovereign_metrics_failed", url=url, error=str(e)[:200])
            return MetricsResult(
                success=False,
                url=url,
                error=str(e)[:300],
                duration_ms=int((time.time() - t0) * 1000),
            )
        finally:
            if browser is not None:
                try:
                    await browser.close()
                except Exception:
                    pass

    async def check_mobile(self, url: str) -> CheckMobileResult:
        """Render mobile (375x812) + chequeo de scroll horizontal."""
        t0 = time.time()
        browser: Optional[BrowserAutomation] = None
        try:
            browser = await self._open(viewport=MOBILE_VIEWPORT)
            nav = await browser.navigate(url)
            if not nav.success:
                return CheckMobileResult(
                    success=False,
                    url=url,
                    error=nav.error or "navigate_failed",
                    duration_ms=int((time.time() - t0) * 1000),
                )

            # Chequeo de overflow horizontal
            doc_width = MOBILE_VIEWPORT["width"]
            has_overflow = False
            if browser._page is not None:
                try:
                    doc_width = await browser._page.evaluate(
                        "() => Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0)"
                    )
                    has_overflow = doc_width > MOBILE_VIEWPORT["width"]
                except Exception as e:
                    logger.warning("mobile_overflow_check_failed", error=str(e)[:100])

            shot_path = f"/tmp/sovereign_mobile_{int(time.time() * 1000)}.png"
            shot = await browser.screenshot(path=shot_path, full_page=True)
            screenshot_url: Optional[str] = None
            if shot.success and shot.screenshot_path:
                screenshot_url = await _upload_to_supabase_storage(
                    local_path=shot.screenshot_path,
                    storage_subpath=f"mobile/{int(time.time() * 1000)}.png",
                )

            return CheckMobileResult(
                success=True,
                url=url,
                screenshot_url=screenshot_url,
                screenshot_local_path=shot.screenshot_path if shot.success else None,
                has_horizontal_scroll=has_overflow,
                document_width=int(doc_width),
                viewport_width=MOBILE_VIEWPORT["width"],
                duration_ms=int((time.time() - t0) * 1000),
            )
        except Exception as e:
            logger.error("sovereign_check_mobile_failed", url=url, error=str(e)[:200])
            return CheckMobileResult(
                success=False,
                url=url,
                error=str(e)[:300],
                duration_ms=int((time.time() - t0) * 1000),
            )
        finally:
            if browser is not None:
                try:
                    await browser.close()
                except Exception:
                    pass


# --- Supabase Storage helper ----------------------------------------------

# Bucket name configurable via env
SCREENSHOTS_BUCKET = os.environ.get("BROWSER_SCREENSHOTS_BUCKET", "screenshots")


async def _upload_to_supabase_storage(
    local_path: str,
    storage_subpath: str,
) -> Optional[str]:
    """Sube un archivo local a Supabase Storage y devuelve URL publica.

    Lee credenciales en cada llamada (no cache al boot) — disciplina del
    Hilo Catastro / Sprint 85 Bloque 4. Si SUPABASE_URL o
    SUPABASE_SERVICE_ROLE_KEY no estan, retorna None (graceful degradation).

    Args:
        local_path: Path absoluto del archivo en la sandbox del kernel.
        storage_subpath: Path destino dentro del bucket (e.g., "renders/123.png").

    Returns:
        URL publica del objeto, o None si no se pudo subir.
    """
    supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    service_key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_KEY")
        or ""
    )

    if not supabase_url or not service_key:
        logger.debug("supabase_storage_skipped", reason="no_credentials")
        return None

    if not os.path.isfile(local_path):
        logger.warning("supabase_storage_skipped", reason="file_not_found", path=local_path)
        return None

    try:
        import httpx
    except ImportError:
        logger.warning("supabase_storage_skipped", reason="httpx_not_installed")
        return None

    bucket = SCREENSHOTS_BUCKET
    upload_url = f"{supabase_url}/storage/v1/object/{bucket}/{storage_subpath}"
    public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{storage_subpath}"

    try:
        with open(local_path, "rb") as f:
            payload = f.read()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                upload_url,
                content=payload,
                headers={
                    "Authorization": f"Bearer {service_key}",
                    "Content-Type": "image/png",
                    "x-upsert": "true",
                },
            )
        if resp.status_code in (200, 201):
            logger.info(
                "supabase_storage_upload_ok",
                bucket=bucket,
                path=storage_subpath,
                bytes=len(payload),
            )
            return public_url
        logger.warning(
            "supabase_storage_upload_failed",
            status=resp.status_code,
            body=resp.text[:200],
        )
        return None
    except Exception as e:
        logger.warning("supabase_storage_upload_exception", error=str(e)[:200])
        return None
