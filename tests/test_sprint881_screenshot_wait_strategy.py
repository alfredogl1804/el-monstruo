"""
Sprint 88.1 v4 — fix BUG VISUAL: screenshot capturado antes que CSS aplicara.

Bug raíz Critic Score 0-5 (cuarta iteración):
- Playwright usaba `wait_until="domcontentloaded"` que se dispara ANTES de que
  el `<link rel="stylesheet" href="style.css">` termine de descargarse y aplicar.
- Resultado: el screenshot capturaba HTML estructural pero SIN estilos:
  texto en serif default, sin layout, botones como `<a>` sin formato.
- Gemini Vision veía "wireframe vacío, página sin contenido textual" porque
  literalmente la imagen mostraba una página NO estilizada.

Fix v4:
- `wait_until="load"` para esperar al evento `load` del window (CSS externo + imágenes).
- `wait_for_function` explícito que confirma `<h1>` visible con texto real (>10 chars).
- Doble settle: networkidle 8s + asyncio.sleep(1s) para compositing final.

Tests verifican que la lógica esté presente; integración E2E real corre en eval suite.
"""
from __future__ import annotations

import inspect

from kernel.e2e.screenshot import capture as capture_module


class TestScreenshotWaitStrategy:
    """Verifica que la estrategia de espera correcta esté implementada."""

    def test_capture_usa_wait_until_load_no_domcontentloaded(self):
        """`wait_until="load"` garantiza que CSS externo se descargue y aplique."""
        source = inspect.getsource(capture_module._capture_with_playwright)
        assert 'wait_until="load"' in source, (
            "_capture_with_playwright DEBE usar wait_until='load' (no 'domcontentloaded') "
            "para esperar CSS externo"
        )
        assert 'wait_until="domcontentloaded"' not in source, (
            "domcontentloaded se dispara antes que CSS aplique"
        )

    def test_capture_espera_h1_con_texto_real(self):
        """Debe haber wait_for_function que confirme h1 con >10 chars."""
        source = inspect.getsource(capture_module._capture_with_playwright)
        assert "wait_for_function" in source, (
            "Debe haber wait_for_function explícito"
        )
        assert "h1" in source.lower(), (
            "Debe verificar la presencia del h1"
        )
        assert "trim().length > 10" in source, (
            "Debe verificar texto real (>10 chars), no solo h1 vacío"
        )

    def test_capture_tiene_settle_adicional(self):
        """Debe haber settle final (sleep) para compositing del browser."""
        source = inspect.getsource(capture_module._capture_with_playwright)
        assert "asyncio.sleep" in source, (
            "Debe haber asyncio.sleep final para compositing"
        )

    def test_capture_doble_networkidle(self):
        """Networkidle se mantiene como settle adicional para fuentes/imágenes."""
        source = inspect.getsource(capture_module._capture_with_playwright)
        assert "networkidle" in source, (
            "networkidle se mantiene como settle adicional"
        )

    def test_capture_screenshot_full_page(self):
        """Screenshot debe ser full_page (toda la altura), no solo viewport."""
        source = inspect.getsource(capture_module._capture_with_playwright)
        assert "full_page=True" in source, (
            "Screenshot debe ser full_page=True para capturar toda la landing"
        )
