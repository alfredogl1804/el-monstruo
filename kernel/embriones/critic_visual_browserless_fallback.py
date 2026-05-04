"""
El Monstruo — Browserless Fallback Client (Sprint 85)
======================================================
Cliente HTTP minimalista para Browserless.io / Browserless self-hosted.

Implementa la misma firma pública que `BrowserAutomation` (initialize, navigate,
screenshot, extract_text, close, set_viewport) pero por encima de la API REST
de Browserless. Se usa como FALLBACK temporal mientras el Sprint 84.6 termina
el browser soberano.

Cuando el browser soberano esté listo, este fallback queda como respaldo si
Playwright local falla (CI sin Chromium, sandbox sin display, etc.).

Switch via env var: CRITIC_BROWSER_BACKEND=browserless | soberano (default)
URL via env var:    BROWSERLESS_URL (ej: https://chrome.browserless.io)
Token via env var:  BROWSERLESS_TOKEN

Soberanía: este fallback es temporal por diseño. Su existencia se justifica
solo mientras la Capa 1 (Manos) no esté completa. Una vez completa, el
backend "soberano" se convierte en el único camino productivo.

Sprint 85 — 2026-05-04
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Any, Optional

import structlog

logger = structlog.get_logger("monstruo.critic_visual.browserless")


# ── Resultado compatible con BrowserAutomation ────────────────────────────────
@dataclass
class BrowserResult:
    """Mismo contrato que kernel.browser_automation.BrowserResult."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    screenshot_path: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "screenshot_path": self.screenshot_path,
        }


# ── Errores con identidad ────────────────────────────────────────────────────
class BrowserlessClientError(Exception):
    """Error base del cliente Browserless."""


BROWSERLESS_SIN_TOKEN = (
    "BROWSERLESS_SIN_TOKEN: "
    "BROWSERLESS_TOKEN no está en environment. "
    "Sugerencia: setear BROWSERLESS_TOKEN o cambiar a CRITIC_BROWSER_BACKEND=soberano."
)

BROWSERLESS_SIN_URL = (
    "BROWSERLESS_SIN_URL: "
    "BROWSERLESS_URL no está en environment. "
    "Sugerencia: usar 'https://chrome.browserless.io' o tu propia URL self-hosted."
)


# ── Cliente Browserless ──────────────────────────────────────────────────────
class BrowserlessClient:
    """
    Cliente HTTP para Browserless. Implementa la firma pública de
    `BrowserAutomation` para ser drop-in compatible.

    Uso:
        client = BrowserlessClient()
        await client.initialize()
        await client.navigate("https://example.com")
        await client.screenshot(path="/tmp/shot.png", full_page=True)
        await client.close()
    """

    def __init__(
        self,
        timeout_ms: int = 30000,
        viewport: Optional[dict[str, int]] = None,
    ):
        # Lectura de credenciales en cada uso (regla del Cowork)
        self.timeout_ms = timeout_ms
        self.viewport = viewport or {"width": 1280, "height": 720}
        self._current_url: Optional[str] = None
        self._initialized = False

    def _get_url(self) -> str:
        url = os.environ.get("BROWSERLESS_URL", "").rstrip("/")
        if not url:
            raise BrowserlessClientError(BROWSERLESS_SIN_URL)
        return url

    def _get_token(self) -> str:
        token = os.environ.get("BROWSERLESS_TOKEN", "")
        if not token:
            raise BrowserlessClientError(BROWSERLESS_SIN_TOKEN)
        return token

    async def initialize(self) -> BrowserResult:
        """No-op para REST; solo valida credenciales."""
        try:
            self._get_url()
            self._get_token()
            self._initialized = True
            logger.info("browserless_initialized")
            return BrowserResult(success=True, data={"backend": "browserless"})
        except BrowserlessClientError as exc:
            return BrowserResult(success=False, error=str(exc))

    async def navigate(self, url: str) -> BrowserResult:
        """
        Browserless no expone navigate() puro vía REST; lo emulamos guardando
        la URL para usarla en screenshot/content. Las métricas de performance
        las llenamos en una segunda llamada a /performance si está disponible.
        """
        self._current_url = url
        # Intentar obtener métricas de performance
        try:
            metrics = await self._fetch_performance(url)
            return BrowserResult(success=True, data=metrics)
        except Exception as exc:
            # No bloquear si performance falla; la navegación lógica está hecha
            logger.warning("browserless_navigate_metrics_failed", error=str(exc))
            return BrowserResult(
                success=True,
                data={"ttfb_ms": 0, "lcp_ms": 0, "load_time_ms": 0},
            )

    async def _fetch_performance(self, url: str) -> dict[str, int]:
        """Llama al endpoint /performance de Browserless. Falla silenciosamente."""
        try:
            import httpx
        except ImportError:
            return {"ttfb_ms": 0, "lcp_ms": 0, "load_time_ms": 0}

        bl_url = self._get_url()
        bl_token = self._get_token()
        endpoint = f"{bl_url}/performance?token={bl_token}"
        async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as cli:
            resp = await cli.post(
                endpoint,
                json={"url": url, "config": {"category": "performance"}},
            )
            if resp.status_code != 200:
                return {"ttfb_ms": 0, "lcp_ms": 0, "load_time_ms": 0}
            data = resp.json()
            audits = data.get("data", {}).get("lhr", {}).get("audits", {})
            return {
                "ttfb_ms": int(audits.get("server-response-time", {}).get("numericValue", 0)),
                "lcp_ms": int(audits.get("largest-contentful-paint", {}).get("numericValue", 0)),
                "load_time_ms": int(audits.get("speed-index", {}).get("numericValue", 0)),
            }

    async def screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False,
    ) -> BrowserResult:
        """Captura screenshot vía endpoint /screenshot."""
        if not self._current_url:
            return BrowserResult(success=False, error="No URL navigated yet")

        try:
            import httpx
        except ImportError:
            return BrowserResult(
                success=False, error="httpx no instalado en el environment"
            )

        try:
            bl_url = self._get_url()
            bl_token = self._get_token()
        except BrowserlessClientError as exc:
            return BrowserResult(success=False, error=str(exc))

        endpoint = f"{bl_url}/screenshot?token={bl_token}"
        payload = {
            "url": self._current_url,
            "options": {"fullPage": full_page, "type": "png"},
            "viewport": self.viewport,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as cli:
                resp = await cli.post(endpoint, json=payload)
                if resp.status_code != 200:
                    return BrowserResult(
                        success=False,
                        error=f"Browserless returned {resp.status_code}: {resp.text[:200]}",
                    )

                # Browserless devuelve binary PNG
                png_bytes = resp.content
                if path:
                    with open(path, "wb") as f:
                        f.write(png_bytes)
                    return BrowserResult(success=True, screenshot_path=path)

                # Si no hay path, devolver base64
                return BrowserResult(
                    success=True,
                    data={"base64": base64.b64encode(png_bytes).decode("ascii")},
                )
        except Exception as exc:
            return BrowserResult(success=False, error=f"screenshot_failed: {exc}")

    async def extract_text(self, selector: str) -> BrowserResult:
        """Extrae texto vía endpoint /content + parsing local con BeautifulSoup."""
        if not self._current_url:
            return BrowserResult(success=False, error="No URL navigated yet")

        try:
            import httpx
        except ImportError:
            return BrowserResult(success=False, error="httpx no instalado")

        try:
            bl_url = self._get_url()
            bl_token = self._get_token()
        except BrowserlessClientError as exc:
            return BrowserResult(success=False, error=str(exc))

        endpoint = f"{bl_url}/content?token={bl_token}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_ms / 1000) as cli:
                resp = await cli.post(endpoint, json={"url": self._current_url})
                if resp.status_code != 200:
                    return BrowserResult(
                        success=False,
                        error=f"Browserless content failed: {resp.status_code}",
                    )
                html = resp.text

                # Parsing local
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    elements = soup.select(selector)
                    text = "\n".join(el.get_text(strip=True) for el in elements)
                    return BrowserResult(success=True, data=text[:5000])
                except ImportError:
                    return BrowserResult(
                        success=False, error="beautifulsoup4 no instalado"
                    )
        except Exception as exc:
            return BrowserResult(success=False, error=f"extract_text_failed: {exc}")

    async def set_viewport(self, width: int, height: int) -> BrowserResult:
        """Cambia viewport. En Browserless es por-request, así que solo guardamos."""
        self.viewport = {"width": width, "height": height}
        return BrowserResult(success=True, data=self.viewport)

    async def close(self) -> BrowserResult:
        """No-op para REST."""
        self._initialized = False
        return BrowserResult(success=True)
