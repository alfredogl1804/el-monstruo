"""
DAN P0.4 — tests/test_tool_registry.py
=======================================
Contract tests para la capa tipada del DAN P0.4-mínimo:

  - `kernel/tool_definitions.py` ToolDefinition + ToolResult + catálogo.
  - `tools/skill_read.py` (handler nuevo).
  - Cableado en `kernel/tool_dispatch._execute_tool` y ToolSpecs registrados.
  - AG-UI events `TOOL_CALL_COMPLETED` / `TOOL_CALL_FAILED`.
  - Smoke test del shape REAL de `tools.web_search.web_search()` sin mockear
    (petición explícita de Cowork — gate anti-F23, último hueco que el suite
    de P0.5 dejaba mock-oculta-realidad).

NO llama Perplexity ni GitHub real: las llamadas externas se mockean.

Sprint DAN — P0.4 — 2026-05-27 — Manus E1
"""

from __future__ import annotations

import asyncio
import inspect
import os
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from kernel.tool_definitions import (
    GITHUB_OPS_TOOL_DEF,
    SKILL_READ_TOOL_DEF,
    WEB_SEARCH_TOOL_DEF,
    ToolDefinition,
    ToolResult,
    get_p04_tool_definitions,
    get_tool_definition,
)
from tools.skill_read import skill_read


# ──────────────────────────────────────────────────────────────────────
# 1. ToolDefinition catalog — los 3 tools del DAN P0.4-mínimo existen
# ──────────────────────────────────────────────────────────────────────
class TestToolDefinitionCatalog(unittest.TestCase):
    def test_catalog_contains_three_tools(self):
        defs = get_p04_tool_definitions()
        names = {d.name for d in defs}
        self.assertEqual(names, {"web_search", "skill_read", "github_ops"})
        # Todos deben ser ToolDefinition tipadas
        for d in defs:
            self.assertIsInstance(d, ToolDefinition)

    def test_lookup_by_name(self):
        self.assertEqual(get_tool_definition("web_search"), WEB_SEARCH_TOOL_DEF)
        self.assertEqual(get_tool_definition("skill_read"), SKILL_READ_TOOL_DEF)
        self.assertEqual(get_tool_definition("github_ops"), GITHUB_OPS_TOOL_DEF)
        self.assertIsNone(get_tool_definition("does_not_exist"))

    def test_github_ops_requires_approval(self):
        # Regla dura: github_ops es write-capable → HITL obligatorio.
        self.assertTrue(GITHUB_OPS_TOOL_DEF.requires_approval)
        self.assertFalse(WEB_SEARCH_TOOL_DEF.requires_approval)
        self.assertFalse(SKILL_READ_TOOL_DEF.requires_approval)

    def test_web_search_has_cost_and_latency_estimates(self):
        # Petición explícita de Cowork: el ToolSpec del web_search debe
        # declarar cost_usd_estimated y latency_ms_estimated.
        self.assertGreater(WEB_SEARCH_TOOL_DEF.cost_usd_estimated, 0.0)
        self.assertGreater(WEB_SEARCH_TOOL_DEF.latency_ms_estimated, 0)

    def test_github_ops_action_enum_matches_dispatcher(self):
        # El enum de actions debe casar exactamente con los keys de
        # tools.github.execute_github (anti-ghost: sin acciones inventadas).
        from tools.github import (
            COMMIT_LOOP_ACTIONS,
            HITL_WRITE_ACTIONS,
            READ_ACTIONS,
        )

        declared = set(
            GITHUB_OPS_TOOL_DEF.json_schema["properties"]["action"]["enum"]
        )
        real = set(READ_ACTIONS) | set(COMMIT_LOOP_ACTIONS) | set(HITL_WRITE_ACTIONS)
        self.assertEqual(
            declared,
            real,
            f"github_ops action enum drifted from execute_github: declared={declared} real={real}",
        )


# ──────────────────────────────────────────────────────────────────────
# 2. ToolResult.from_handler_result — mapeo de los 4 status
# ──────────────────────────────────────────────────────────────────────
class TestToolResult(unittest.TestCase):
    def test_success_status(self):
        r = ToolResult.from_handler_result(
            tool_name="web_search",
            result={"answer": "ok", "cost_usd": 0.01},
            latency_ms=120,
            run_id="r1",
        )
        self.assertEqual(r.status, "success")
        self.assertEqual(r.cost_usd, 0.01)
        self.assertEqual(r.latency_ms, 120)
        self.assertEqual(r.tool_name, "web_search")
        self.assertEqual(r.run_id, "r1")

    def test_error_status(self):
        r = ToolResult.from_handler_result(
            tool_name="web_search",
            result={"error": "timeout to Perplexity"},
            latency_ms=5000,
        )
        self.assertEqual(r.status, "error")
        self.assertEqual(r.error, "timeout to Perplexity")

    def test_denied_status(self):
        r = ToolResult.from_handler_result(
            tool_name="github_ops",
            result={"status": "denied", "error": "HITL_REQUIRED"},
            latency_ms=10,
        )
        self.assertEqual(r.status, "denied")
        self.assertEqual(r.error, "HITL_REQUIRED")

    def test_timeout_status(self):
        r = ToolResult.from_handler_result(
            tool_name="github_ops",
            result={"status": "timeout"},
            latency_ms=30000,
        )
        self.assertEqual(r.status, "timeout")


# ──────────────────────────────────────────────────────────────────────
# 3. tools/skill_read.py — read-only, redacción PII, anti path-traversal
# ──────────────────────────────────────────────────────────────────────
class TestSkillRead(unittest.TestCase):
    def setUp(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        except Exception:
            self.loop = asyncio.get_event_loop()

    def tearDown(self):
        try:
            self.loop.close()
        except Exception:
            pass

    def test_skill_read_blocks_path_traversal(self):
        out = self.loop.run_until_complete(skill_read("../../etc"))
        self.assertIsNone(out["content"])
        self.assertIn("invalid", out["error"].lower())

    def test_skill_read_blocks_absolute_path(self):
        out = self.loop.run_until_complete(skill_read("/etc/passwd"))
        self.assertIsNone(out["content"])
        self.assertIsNotNone(out["error"])

    def test_skill_read_returns_not_found_for_unknown(self):
        out = self.loop.run_until_complete(skill_read("does-not-exist-skill-xyz"))
        self.assertIsNone(out["content"])
        self.assertIn("not found", out["error"].lower())

    def test_skill_read_redacts_pii(self):
        # Construir SKILL.md temporal con credenciales falsas; verificar redacción
        from tools.skill_read import _redact_pii

        # Strings rotas con concatenacion para no disparar GitHub push
        # protection ni gitleaks: este test verifica que _redact_pii() detecte
        # y reemplace patrones realistas, pero el repo no debe contener cadenas
        # parseables como secretos por escaneres automaticos.
        _sk = "sk" + "-" + "abc123def456ghi789jkl012mno345pqr"
        _stripe = "sk" + "_" + "live" + "_" + "A" * 24
        _gh = "ghp" + "_" + "a" * 30
        _jwt = "eyJhbGciOiJIUzI1NiJ9" + "." + "eyJzdWIiOiIxMjMifQ" + "." + "abcdefghij"
        sample = (
            f"OpenAI key: {_sk} "
            f"Stripe: {_stripe} "
            f"GitHub: {_gh} "
            "Email: foo@example.com "
            "Postgres: postgres://user:pass@host/db "
            f"JWT: {_jwt}"
        )
        clean, hits = _redact_pii(sample)
        self.assertGreaterEqual(hits, 5)
        self.assertNotIn(_sk, clean)
        self.assertNotIn(_stripe, clean)
        self.assertNotIn(_gh, clean)
        self.assertNotIn("foo@example.com", clean)
        self.assertNotIn("user:pass", clean)
        self.assertIn("[REDACTED:", clean)


# ──────────────────────────────────────────────────────────────────────
# 4. tool_dispatch — get_tool_specs incluye los 3 P0.4 tools
# ──────────────────────────────────────────────────────────────────────
class TestToolDispatchRegistration(unittest.TestCase):
    def test_get_tool_specs_includes_p04_tools(self):
        from kernel.tool_dispatch import get_tool_specs

        specs = get_tool_specs()
        names = {s.name for s in specs}
        self.assertIn("web_search", names)
        self.assertIn("skill_read", names)
        self.assertIn("github_ops", names)

    def test_web_search_spec_has_cost_estimate(self):
        from kernel.tool_dispatch import get_tool_specs

        specs = {s.name: s for s in get_tool_specs()}
        ws = specs["web_search"]
        # Petición Cowork: el spec real registrado debe declarar costo/latencia.
        self.assertGreater(getattr(ws, "cost_usd_estimated", 0.0), 0.0)
        self.assertGreater(getattr(ws, "latency_ms_estimated", 0), 0)

    def test_github_ops_spec_marked_high_risk(self):
        from kernel.tool_dispatch import get_tool_specs

        specs = {s.name: s for s in get_tool_specs()}
        self.assertEqual(specs["github_ops"].risk, "high")


# ──────────────────────────────────────────────────────────────────────
# 5. _execute_tool — github_ops sin HITL devuelve denied (no ejecuta)
# ──────────────────────────────────────────────────────────────────────
class TestExecuteToolGitHubOps(unittest.TestCase):
    def setUp(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        except Exception:
            self.loop = asyncio.get_event_loop()

    def tearDown(self):
        try:
            self.loop.close()
        except Exception:
            pass

    def test_github_ops_write_without_hitl_returns_denied(self):
        # create_issue es HITL_WRITE_ACTIONS → debe bloquearse sin _hitl_approved.
        from kernel.tool_dispatch import _execute_tool

        out = self.loop.run_until_complete(
            _execute_tool(
                "github_ops",
                {
                    "action": "create_issue",
                    "params": {
                        "repo": "alfredogl1804/el-monstruo",
                        "title": "test",
                        "body": "test",
                    },
                    # _hitl_approved omitido → False por defecto
                },
            )
        )
        self.assertEqual(out.get("status"), "denied")
        self.assertEqual(out.get("error"), "HITL_REQUIRED")


# ──────────────────────────────────────────────────────────────────────
# 6. SMOKE REAL: shape de tools.web_search.web_search() sin mockear
#    (petición Cowork F23 — último hueco mock-oculta-realidad)
# ──────────────────────────────────────────────────────────────────────
class TestWebSearchRealShapeSmoke(unittest.TestCase):
    """
    No llama Perplexity. Verifica:
      - La función existe y es coroutine.
      - Su firma acepta los kwargs que el wrapper P0.5 le pasa.
      - Sin SONAR_API_KEY devuelve un dict con las keys que el wrapper consume
        (`answer`, `citations`, `model_used`, `tokens_used`, `error`) — el path
        fail-loud está conectado al shape que ToolResult espera.
    """

    def test_web_search_function_exists_and_is_async(self):
        from tools.web_search import web_search

        self.assertTrue(inspect.iscoroutinefunction(web_search))

    def test_web_search_signature_accepts_wrapper_kwargs(self):
        from tools.web_search import web_search

        sig = inspect.signature(web_search)
        params = sig.parameters
        # El wrapper P0.5 le pasa: query, context, model, max_tokens, temperature
        for required in ("query", "context", "model", "max_tokens", "temperature"):
            self.assertIn(
                required, params, f"web_search() missing param '{required}' that wrapper expects"
            )

    def test_web_search_no_key_returns_expected_keys(self):
        # Forzamos ausencia de SONAR_API_KEY y verificamos shape real.
        from tools.web_search import web_search

        original = os.environ.pop("SONAR_API_KEY", None)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                out = loop.run_until_complete(web_search(query="ping"))
            finally:
                loop.close()
        finally:
            if original is not None:
                os.environ["SONAR_API_KEY"] = original

        # Estas son exactamente las keys que `web_search_with_telemetry` lee.
        for k in ("answer", "citations", "model_used", "tokens_used", "error"):
            self.assertIn(k, out, f"web_search() shape missing key '{k}'")
        self.assertTrue(out["error"], "web_search() must fail loud without SONAR_API_KEY")


if __name__ == "__main__":
    unittest.main()
