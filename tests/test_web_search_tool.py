"""
DAN P0.5 — tests/test_web_search_tool.py
=========================================
Tests del wrapper `tools.web_search_tool.web_search_with_telemetry`:

- `test_web_search_returns_cost_and_latency`: el wrapper devuelve `cost_usd`
  y `latency_ms` numéricos derivados de `tokens_used` × pricing del catálogo.
- `test_web_search_no_key_fails_loud`: sin `SONAR_API_KEY` → error explícito,
  NO respuesta vacía silenciosa (la base ya lo hace, validamos el wrapper).
- `test_cost_ledger_records_query`: cuando se pasa un `finops` fake, cada
  query deja un registro vía `record_run_cost`.
- `test_results_shape_dan_compliant`: `results` es lista de dicts con keys
  {url, citation_id, title, snippet}; title/snippet pueden ser None.
- `test_unknown_model_cost_zero`: si el modelo no está en `model_catalog`,
  `cost_usd == 0.0` y `cost_source == "unknown"` (no inventar).

NO llama Perplexity real — mocks de `tools.web_search.web_search`.

Sprint DAN — P0.5 — 2026-05-27 — Manus E1
"""

from __future__ import annotations

import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch

from tools.web_search_tool import web_search_with_telemetry


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class _FakeFinOps:
    """FinOps fake que captura la última llamada a `record_run_cost`."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def record_run_cost(self, **kwargs):
        self.calls.append(kwargs)
        return {"id": "fake", **kwargs}


class TestWebSearchTool(unittest.TestCase):
    def setUp(self) -> None:
        # Asegurar event loop limpio por test
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        except Exception:
            self.loop = asyncio.get_event_loop()

    def tearDown(self) -> None:
        try:
            self.loop.close()
        except Exception:
            pass

    @patch("tools.web_search_tool._base_web_search", new_callable=AsyncMock)
    def test_web_search_returns_cost_and_latency(self, mock_base):
        mock_base.return_value = {
            "answer": "respuesta",
            "citations": ["https://example.com/a", "https://example.com/b"],
            "model_used": "sonar-reasoning-pro",
            "tokens_used": 1_000_000,  # 1M tokens — cost = blended (2+8)/2 = 5 USD
            "error": None,
        }

        out = self.loop.run_until_complete(
            web_search_with_telemetry(query="¿qué hora es?")
        )

        self.assertIsInstance(out["latency_ms"], int)
        self.assertGreaterEqual(out["latency_ms"], 0)
        # 1M tokens × blended (2.00+8.00)/2 = $5.00
        self.assertAlmostEqual(out["cost_usd"], 5.0, places=4)
        self.assertEqual(out["cost_source"], "model_catalog")
        self.assertEqual(out["model_used"], "sonar-reasoning-pro")
        self.assertEqual(out["tokens_used"], 1_000_000)
        self.assertIsNone(out["error"])

    @patch("tools.web_search_tool._base_web_search", new_callable=AsyncMock)
    def test_web_search_no_key_fails_loud(self, mock_base):
        # La base ya devuelve error explícito si no hay key — el wrapper
        # debe propagarlo, NO sobrescribirlo a "" silenciosamente.
        mock_base.return_value = {
            "answer": "",
            "citations": [],
            "model_used": "",
            "tokens_used": 0,
            "error": "SONAR_API_KEY not set. Cannot search the web.",
        }

        out = self.loop.run_until_complete(
            web_search_with_telemetry(query="test")
        )

        self.assertIsNotNone(out["error"])
        self.assertIn("SONAR_API_KEY", out["error"])
        self.assertEqual(out["cost_usd"], 0.0)
        self.assertEqual(out["cost_source"], "unknown")
        self.assertEqual(out["results"], [])

    @patch("tools.web_search_tool._base_web_search", new_callable=AsyncMock)
    def test_cost_ledger_records_query(self, mock_base):
        mock_base.return_value = {
            "answer": "ok",
            "citations": ["https://x.com"],
            "model_used": "sonar-reasoning-pro",
            "tokens_used": 500,
            "error": None,
        }
        finops = _FakeFinOps()

        out = self.loop.run_until_complete(
            web_search_with_telemetry(
                query="precio del bitcoin",
                finops=finops,
                run_id="run-test-123",
            )
        )

        self.assertEqual(len(finops.calls), 1)
        call = finops.calls[0]
        self.assertEqual(call["run_id"], "run-test-123")
        self.assertEqual(call["model_used"], "sonar-reasoning-pro")
        self.assertEqual(call["tokens_out"], 500)
        self.assertEqual(call["tool_count"], 1)
        self.assertEqual(call["status"], "completed")
        self.assertGreater(call["cost_usd"], 0)
        self.assertEqual(out["run_id"], "run-test-123")

    @patch("tools.web_search_tool._base_web_search", new_callable=AsyncMock)
    def test_cost_ledger_skipped_on_error(self, mock_base):
        mock_base.return_value = {
            "answer": "",
            "citations": [],
            "model_used": "",
            "tokens_used": 0,
            "error": "All models failed.",
        }
        finops = _FakeFinOps()

        self.loop.run_until_complete(
            web_search_with_telemetry(query="x", finops=finops)
        )

        # No registramos en ledger si hubo error
        self.assertEqual(finops.calls, [])

    @patch("tools.web_search_tool._base_web_search", new_callable=AsyncMock)
    def test_results_shape_dan_compliant(self, mock_base):
        mock_base.return_value = {
            "answer": "respuesta",
            "citations": ["https://a.com", "https://b.com", "https://c.com"],
            "model_used": "sonar-pro",
            "tokens_used": 1000,
            "error": None,
        }

        out = self.loop.run_until_complete(
            web_search_with_telemetry(query="test")
        )

        self.assertEqual(len(out["results"]), 3)
        for idx, r in enumerate(out["results"], start=1):
            self.assertIn("url", r)
            self.assertIn("citation_id", r)
            self.assertIn("title", r)
            self.assertIn("snippet", r)
            self.assertEqual(r["citation_id"], f"[{idx}]")
            # Sonar no devuelve title/snippet hoy — deben ser None, no inventar
            self.assertIsNone(r["title"])
            self.assertIsNone(r["snippet"])

    @patch("tools.web_search_tool._base_web_search", new_callable=AsyncMock)
    def test_unknown_model_cost_zero(self, mock_base):
        mock_base.return_value = {
            "answer": "x",
            "citations": [],
            "model_used": "modelo-fantasma-no-existe",
            "tokens_used": 1_000_000,
            "error": None,
        }

        out = self.loop.run_until_complete(
            web_search_with_telemetry(query="test")
        )

        # Modelo no en catálogo → cost=0, source=unknown (NO inventar pricing)
        self.assertEqual(out["cost_usd"], 0.0)
        self.assertEqual(out["cost_source"], "unknown")


if __name__ == "__main__":
    unittest.main()
