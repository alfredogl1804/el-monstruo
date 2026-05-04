"""
El Monstruo — SP11: Browser Automation
========================================
Navegación web autónoma con Playwright para el embrión.

Permite al embrión:
  - Navegar a URLs
  - Extraer texto de elementos
  - Hacer click en elementos
  - Rellenar formularios
  - Tomar screenshots

Spec (Hilo B):
  Clase BrowserAutomation con métodos stub:
    - navigate(url)
    - extract_text(selector)
    - click(selector)
    - fill_form(selector, value)
    - screenshot()

Cada método tiene docstring explicando qué hará cuando se implemente.
La implementación real requiere Playwright instalado.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.browser_automation")


# ─── Configuration ────────────────────────────────────────────────────────────

HEADLESS = os.environ.get("BROWSER_HEADLESS", "true").lower() == "true"
DEFAULT_TIMEOUT_MS = int(os.environ.get("BROWSER_TIMEOUT_MS", "30000"))
DEFAULT_VIEWPORT = {"width": 1280, "height": 720}
BLOCKED_DOMAINS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "169.254.",
    "10.",
    "192.168.",
    "172.16.",
]


# ─── Result Types ─────────────────────────────────────────────────────────────


@dataclass
class BrowserResult:
    """Resultado de una operación del browser."""

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


@dataclass
class PageInfo:
    """Información de la página actual."""

    url: str = ""
    title: str = ""
    status_code: int = 0


# ─── Browser Automation Class ─────────────────────────────────────────────────


class BrowserAutomation:
    """
    Clase principal de browser automation para El Monstruo.

    Encapsula Playwright para proveer navegación web autónoma al embrión.
    Todos los métodos son stubs documentados hasta que Playwright se instale
    y configure en el entorno de producción.

    Uso:
        browser = BrowserAutomation()
        await browser.initialize()
        result = await browser.navigate("https://example.com")
        text = await browser.extract_text("h1")
        await browser.close()
    """

    def __init__(
        self,
        headless: bool = HEADLESS,
        timeout_ms: int = DEFAULT_TIMEOUT_MS,
        viewport: dict[str, int] | None = None,
    ):
        """
        Inicializa la configuración del browser.

        Args:
            headless: Ejecutar sin interfaz gráfica (default: True).
            timeout_ms: Timeout global en milisegundos (default: 30000).
            viewport: Dimensiones del viewport (default: 1280x720).
        """
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.viewport = viewport or DEFAULT_VIEWPORT
        self._browser = None
        self._context = None
        self._page = None
        self._initialized = False
        self._current_url: str = ""

    async def initialize(self) -> BrowserResult:
        """
        Inicializa Playwright y crea una instancia de browser.

        Cuando se implemente completamente:
        1. Lanza Playwright con chromium en modo headless
        2. Crea un browser context con viewport configurado
        3. Crea una página nueva lista para navegar
        4. Configura timeouts y user-agent

        Returns:
            BrowserResult indicando si la inicialización fue exitosa.
        """
        try:
            # Intentar importar playwright
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
            )
            self._context = await self._browser.new_context(
                viewport=self.viewport,
            )
            self._page = await self._context.new_page()
            self._page.set_default_timeout(self.timeout_ms)
            self._initialized = True

            logger.info(
                "browser_initialized",
                headless=self.headless,
                viewport=self.viewport,
            )
            return BrowserResult(success=True, data="Browser initialized")

        except ImportError:
            logger.warning(
                "playwright_not_installed",
                msg="Install with: pip install playwright && playwright install chromium",
            )
            return BrowserResult(
                success=False,
                error=("Playwright not installed. Install with: pip install playwright && playwright install chromium"),
            )
        except Exception as e:
            logger.error("browser_init_failed", error=str(e)[:200])
            return BrowserResult(
                success=False,
                error=f"Browser initialization failed: {str(e)[:200]}",
            )

    async def navigate(self, url: str) -> BrowserResult:
        """
        Navega a una URL específica.

        Cuando se implemente completamente:
        1. Valida que la URL no sea un dominio bloqueado (localhost, IPs internas)
        2. Navega a la URL con wait_until="domcontentloaded"
        3. Espera a que la página cargue completamente
        4. Retorna el título y status code de la página

        Args:
            url: URL a la que navegar (debe ser https:// o http://).

        Returns:
            BrowserResult con PageInfo en .data si exitoso.

        Security:
            Bloquea navegación a localhost, IPs internas, y dominios privados.
        """
        # Security check
        if self._is_blocked_url(url):
            return BrowserResult(
                success=False,
                error=f"URL blocked for security: {url}",
            )

        if not self._initialized:
            return BrowserResult(
                success=False,
                error="Browser not initialized. Call initialize() first.",
            )

        try:
            response = await self._page.goto(url, wait_until="domcontentloaded")
            self._current_url = url
            title = await self._page.title()

            page_info = PageInfo(
                url=url,
                title=title,
                status_code=response.status if response else 0,
            )

            logger.info("browser_navigated", url=url, title=title)
            return BrowserResult(success=True, data=page_info)

        except Exception as e:
            logger.error("browser_navigate_failed", url=url, error=str(e)[:200])
            return BrowserResult(
                success=False,
                error=f"Navigation failed: {str(e)[:200]}",
            )

    async def extract_text(self, selector: str) -> BrowserResult:
        """
        Extrae texto de un elemento de la página usando un selector CSS.

        Cuando se implemente completamente:
        1. Busca el elemento con el selector CSS dado
        2. Extrae el textContent del elemento
        3. Limpia whitespace innecesario
        4. Retorna el texto extraído

        Args:
            selector: Selector CSS del elemento (e.g., "h1", ".title", "#content").

        Returns:
            BrowserResult con el texto extraído en .data.

        Nota:
            Si el selector no encuentra elementos, retorna error.
            Para múltiples elementos, usa extract_all_text().
        """
        if not self._initialized:
            return BrowserResult(
                success=False,
                error="Browser not initialized. Call initialize() first.",
            )

        try:
            element = await self._page.query_selector(selector)
            if element is None:
                return BrowserResult(
                    success=False,
                    error=f"Element not found: {selector}",
                )

            text = await element.text_content()
            text = (text or "").strip()

            logger.info(
                "browser_text_extracted",
                selector=selector,
                text_length=len(text),
            )
            return BrowserResult(success=True, data=text)

        except Exception as e:
            logger.error(
                "browser_extract_failed",
                selector=selector,
                error=str(e)[:200],
            )
            return BrowserResult(
                success=False,
                error=f"Text extraction failed: {str(e)[:200]}",
            )

    async def click(self, selector: str) -> BrowserResult:
        """
        Hace click en un elemento de la página.

        Cuando se implemente completamente:
        1. Espera a que el elemento sea visible y clickeable
        2. Hace scroll al elemento si es necesario
        3. Ejecuta el click
        4. Espera a que la navegación/acción se complete

        Args:
            selector: Selector CSS del elemento a clickear.

        Returns:
            BrowserResult indicando si el click fue exitoso.

        Nota:
            Espera automáticamente a que el elemento sea interactivo.
            Timeout configurable via self.timeout_ms.
        """
        if not self._initialized:
            return BrowserResult(
                success=False,
                error="Browser not initialized. Call initialize() first.",
            )

        try:
            await self._page.click(selector)
            logger.info("browser_clicked", selector=selector)
            return BrowserResult(success=True, data=f"Clicked: {selector}")

        except Exception as e:
            logger.error(
                "browser_click_failed",
                selector=selector,
                error=str(e)[:200],
            )
            return BrowserResult(
                success=False,
                error=f"Click failed: {str(e)[:200]}",
            )

    async def fill_form(self, selector: str, value: str) -> BrowserResult:
        """
        Rellena un campo de formulario con un valor.

        Cuando se implemente completamente:
        1. Busca el campo de input/textarea con el selector
        2. Limpia el contenido existente
        3. Escribe el nuevo valor carácter por carácter (simula typing)
        4. Dispara eventos de input/change

        Args:
            selector: Selector CSS del campo (e.g., "input[name='email']").
            value: Valor a escribir en el campo.

        Returns:
            BrowserResult indicando si el fill fue exitoso.

        Nota:
            Usa fill() de Playwright que dispara todos los eventos necesarios.
            Para selects/dropdowns, usa select_option() en su lugar.
        """
        if not self._initialized:
            return BrowserResult(
                success=False,
                error="Browser not initialized. Call initialize() first.",
            )

        try:
            await self._page.fill(selector, value)
            logger.info(
                "browser_form_filled",
                selector=selector,
                value_length=len(value),
            )
            return BrowserResult(
                success=True,
                data=f"Filled {selector} with {len(value)} chars",
            )

        except Exception as e:
            logger.error(
                "browser_fill_failed",
                selector=selector,
                error=str(e)[:200],
            )
            return BrowserResult(
                success=False,
                error=f"Fill failed: {str(e)[:200]}",
            )

    async def screenshot(
        self,
        path: Optional[str] = None,
        full_page: bool = False,
    ) -> BrowserResult:
        """
        Toma un screenshot de la página actual.

        Cuando se implemente completamente:
        1. Captura el viewport actual (o página completa si full_page=True)
        2. Guarda como PNG en la ruta especificada
        3. Retorna la ruta del archivo guardado

        Args:
            path: Ruta donde guardar el screenshot (default: /tmp/screenshot_<ts>.png).
            full_page: Si True, captura la página completa (no solo viewport).

        Returns:
            BrowserResult con la ruta del screenshot en .screenshot_path.

        Nota:
            Screenshots se guardan en formato PNG.
            Útil para verificación visual de navegación.
        """
        if not self._initialized:
            return BrowserResult(
                success=False,
                error="Browser not initialized. Call initialize() first.",
            )

        try:
            import time

            if path is None:
                path = f"/tmp/screenshot_{int(time.time())}.png"

            await self._page.screenshot(path=path, full_page=full_page)

            logger.info(
                "browser_screenshot_taken",
                path=path,
                full_page=full_page,
            )
            return BrowserResult(
                success=True,
                data=f"Screenshot saved to {path}",
                screenshot_path=path,
            )

        except Exception as e:
            logger.error("browser_screenshot_failed", error=str(e)[:200])
            return BrowserResult(
                success=False,
                error=f"Screenshot failed: {str(e)[:200]}",
            )

    async def close(self) -> BrowserResult:
        """
        Cierra el browser y libera recursos.

        Cuando se implemente completamente:
        1. Cierra todas las páginas abiertas
        2. Cierra el browser context
        3. Cierra la instancia de Playwright
        4. Libera memoria

        Returns:
            BrowserResult indicando si el cierre fue exitoso.
        """
        try:
            if self._browser:
                await self._browser.close()
            if hasattr(self, "_playwright") and self._playwright:
                await self._playwright.stop()
            self._initialized = False
            self._page = None
            self._context = None
            self._browser = None

            logger.info("browser_closed")
            return BrowserResult(success=True, data="Browser closed")

        except Exception as e:
            logger.error("browser_close_failed", error=str(e)[:200])
            return BrowserResult(
                success=False,
                error=f"Close failed: {str(e)[:200]}",
            )

    # ─── Internal Helpers ─────────────────────────────────────────────────────

    def _is_blocked_url(self, url: str) -> bool:
        """Check if URL targets a blocked domain (security)."""
        url_lower = url.lower()
        for blocked in BLOCKED_DOMAINS:
            if blocked in url_lower:
                return True
        return False

    @property
    def is_initialized(self) -> bool:
        """Whether the browser is initialized and ready."""
        return self._initialized

    @property
    def current_url(self) -> str:
        """The current page URL."""
        return self._current_url
