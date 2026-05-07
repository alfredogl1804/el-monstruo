"""
Sprint 88.1 — GitHub Pages propagation wait antes de screenshot.

Bug raíz: el screenshot del Critic se capturaba inmediatamente después del
deploy a gh-pages, pero GitHub Pages tarda 30-90s en propagar nuevos paths.
Resultado: Gemini Vision veía página vacía / 404 y reportaba scores 0-5.

Fix: poll URL hasta que sirva el `<h1>` (landing renderizada real).
"""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import patch, MagicMock

from kernel.e2e.screenshot.capture import _wait_for_github_pages_ready


class TestWaitForGithubPagesReady:
    """Wait function debe retornar True/False segun status del fetch."""

    def test_no_aplica_a_url_no_github_pages(self):
        """URLs que no son github.io retornan True inmediatamente."""
        result = asyncio.run(_wait_for_github_pages_ready(url="https://vercel.app/foo"))
        assert result is True

    def test_no_aplica_a_localhost(self):
        result = asyncio.run(_wait_for_github_pages_ready(url="http://localhost:8000/landing"))
        assert result is True

    def test_retorna_true_cuando_fetch_devuelve_h1(self):
        """Si el primer fetch devuelve HTML con <h1>, retorna True rapido."""
        url = "https://test.github.io/landing/"

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"<html><body><h1>Hero real</h1></body></html>"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda *a: None

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = asyncio.run(
                _wait_for_github_pages_ready(url=url, max_wait_s=10)
            )
        assert result is True

    def test_retorna_false_cuando_404_persiste(self):
        """Si la URL siempre devuelve 404/contenido vacio, retorna False tras max_wait."""
        url = "https://test.github.io/landing-404/"

        mock_resp = MagicMock()
        mock_resp.status = 404
        mock_resp.read.return_value = b"Not Found"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda *a: None

        with patch("urllib.request.urlopen", return_value=mock_resp):
            with patch("kernel.e2e.screenshot.capture.asyncio.sleep") as mock_sleep:
                # mock sleep para que no espere de verdad
                mock_sleep.side_effect = lambda s: asyncio.sleep(0)
                result = asyncio.run(
                    _wait_for_github_pages_ready(url=url, max_wait_s=2)
                )
        assert result is False

    def test_retorna_false_si_html_no_tiene_h1(self):
        """Si HTML llega pero no tiene <h1> marker, sigue esperando."""
        url = "https://test.github.io/landing-empty/"

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"<html><body>Empty</body></html>"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = lambda *a: None

        with patch("urllib.request.urlopen", return_value=mock_resp):
            with patch("kernel.e2e.screenshot.capture.asyncio.sleep") as mock_sleep:
                mock_sleep.side_effect = lambda s: asyncio.sleep(0)
                result = asyncio.run(
                    _wait_for_github_pages_ready(url=url, max_wait_s=2)
                )
        assert result is False
