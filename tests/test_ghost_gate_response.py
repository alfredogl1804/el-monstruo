"""
DAN T2 — Tests for detect_ghost_in_response (server-side ghost-gate)
====================================================================

Unit tests for the post-LLM-response ghost detector that runs in
`kernel/nodes.py::execute()` BEFORE the response is served to the
frontend. The detector decides whether to re-prompt with
tool_choice="required" or pass the response through.

Coverage:
- V1 repro S5 prose ("Voy a consultar las Pull Requests...")
- V2 repro S5 prose ("**Herramienta:** github + **Acción:** list_prs")
- Legacy alias "github" maps to canonical "github_ops" (anti-drift)
- Clean responses (no tool narration) → None
- has_tool_calls=True suppresses ghost detection (tool_call wins)
- Empty/None response → None
- Tools not in available list don't trigger
"""

from __future__ import annotations

import pytest

from kernel.anti_ghost import (
    ResponseGhostHit,
    TOOL_NAME_ALIASES,
    detect_ghost_in_response,
)


# ── Test fixtures: real prose observed in iPhone repro S5 ──────────────────

V1_PROSE_REPRO_S5 = """Voy a consultar las Pull Requests abiertas en el repositorio
`alfredogl1804/el-monstruo`. Dame un momento mientras llamo a la herramienta
github y luego te muestro los resultados."""

V2_PROSE_REPRO_S5 = """Voy a consultar las Pull Requests abiertas en el repositorio
`alfredogl1804/el-monstruo`. Dame un momento.

**Acción:** `list_prs` en `alfredogl1804/el-monstruo` con filtro `open`.
**Riesgo:** medium (lectura de repositorio público)
**Herramienta:** github

**Petición directa:** list_prs con owner="alfredogl1804", repo="el-monstruo",
state="open" (sin parámetros adicionales de paginación).

Voy a ejecutarla ahora. (No describo más — procedo con la llamada)."""

CLEAN_RESPONSE_TEXT_ONLY = """Te explico de qué se trata el repositorio: es un
proyecto de IA con kernel propio escrito en Python. No requiere consulta
externa para responder esta pregunta general."""

CLEAN_RESPONSE_AFTER_TOOL = """Aquí están los Pull Requests abiertos:
1. PR #225 — feat(dan/s5/t1): anti-drift prompt
2. PR #224 — feat(dan/p0.6): harden anti-ghost detector
"""

EN_GHOST_PROSE = """I will call the github tool to list the open pull requests
for you. Give me a moment while I fetch the data."""


# ── Available tools mock ────────────────────────────────────────────────────

DEFAULT_TOOLS = [
    "web_search",
    "github_ops",
    "skill_read",
    "consult_sabios",
    "notion",
    "delegate_task",
]


# ── Tests: ghost detection ──────────────────────────────────────────────────


class TestDetectGhostInResponseV1:
    """V1 repro: prosa narrativa con 'llamo a la herramienta github'."""

    def test_v1_repro_detects_github_legacy_alias(self):
        hit = detect_ghost_in_response(
            response_text=V1_PROSE_REPRO_S5,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is not None
        assert isinstance(hit, ResponseGhostHit)
        assert hit.suspected_tool == "github_ops"
        # Should match via legacy alias "github"
        assert hit.matched_alias == "github"
        assert "github" in hit.offending_excerpt.lower()

    def test_v1_repro_reason_is_actionable(self):
        hit = detect_ghost_in_response(
            response_text=V1_PROSE_REPRO_S5,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is not None
        reason = hit.reason()
        assert "github_ops" in reason
        assert "github" in reason  # alias mentioned
        assert "tool_call" in reason  # action explained


class TestDetectGhostInResponseV2:
    """V2 repro: markdown bold estructurado con **Herramienta:** github."""

    def test_v2_repro_detects_markdown_bold_herramienta(self):
        hit = detect_ghost_in_response(
            response_text=V2_PROSE_REPRO_S5,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is not None
        assert hit.suspected_tool == "github_ops"
        assert hit.matched_alias == "github"

    def test_v2_repro_excerpt_contains_evidence(self):
        hit = detect_ghost_in_response(
            response_text=V2_PROSE_REPRO_S5,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is not None
        # Either "Herramienta" or "github" should be in the excerpt
        excerpt_lower = hit.offending_excerpt.lower()
        assert "herramienta" in excerpt_lower or "github" in excerpt_lower


class TestDetectGhostInResponseHappyPath:
    """Casos limpios: ningún ghost debe ser reportado."""

    def test_clean_text_only_response(self):
        """Respuesta de texto puro sin mención de tools."""
        hit = detect_ghost_in_response(
            response_text=CLEAN_RESPONSE_TEXT_ONLY,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is None

    def test_clean_response_after_tool_executed(self):
        """Respuesta del LLM después de un tool_call exitoso (resultados)."""
        hit = detect_ghost_in_response(
            response_text=CLEAN_RESPONSE_AFTER_TOOL,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is None

    def test_has_tool_calls_suppresses_detection(self):
        """Si el LLM emitió tool_calls, no es ghost aunque la prosa lo mencione."""
        hit = detect_ghost_in_response(
            response_text=V1_PROSE_REPRO_S5,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=True,  # ← LLM SÍ function-calleó
        )
        assert hit is None

    def test_empty_response_returns_none(self):
        hit = detect_ghost_in_response(
            response_text="",
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is None

    def test_none_response_returns_none(self):
        hit = detect_ghost_in_response(
            response_text=None,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is None

    def test_empty_tool_list_returns_none(self):
        hit = detect_ghost_in_response(
            response_text=V1_PROSE_REPRO_S5,
            available_tool_names=[],
            has_tool_calls=False,
        )
        assert hit is None


class TestDetectGhostInResponseEnglish:
    """Patrones EN: 'I'll call the github tool'."""

    def test_en_ghost_detected(self):
        hit = detect_ghost_in_response(
            response_text=EN_GHOST_PROSE,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is not None
        assert hit.suspected_tool == "github_ops"


class TestToolNameAliases:
    """Validar el mapping legacy → canonical."""

    def test_github_ops_has_legacy_alias(self):
        assert "github_ops" in TOOL_NAME_ALIASES
        assert "github" in TOOL_NAME_ALIASES["github_ops"]
        assert "github_ops" in TOOL_NAME_ALIASES["github_ops"]

    def test_tool_without_alias_uses_canonical_only(self):
        """Tools sin entrada en TOOL_NAME_ALIASES usan solo su nombre canónico."""
        # web_search no tiene alias legacy
        prose_with_web_search = "Voy a llamar a la herramienta web_search ahora"
        hit = detect_ghost_in_response(
            response_text=prose_with_web_search,
            available_tool_names=["web_search"],
            has_tool_calls=False,
        )
        assert hit is not None
        assert hit.suspected_tool == "web_search"
        assert hit.matched_alias == "web_search"


class TestDetectGhostInResponseEdgeCases:
    """Edge cases para robustez del detector."""

    def test_tool_mentioned_but_not_in_available_list(self):
        """Si la prosa narra una tool que no está disponible, no es ghost."""
        prose = "Voy a llamar a la herramienta unknown_tool"
        hit = detect_ghost_in_response(
            response_text=prose,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is None

    def test_invocar_pattern(self):
        prose = "Voy a invocar github_ops para esto."
        hit = detect_ghost_in_response(
            response_text=prose,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is not None
        assert hit.suspected_tool == "github_ops"

    def test_usar_pattern(self):
        prose = "Voy a usar la herramienta web_search para buscarlo."
        hit = detect_ghost_in_response(
            response_text=prose,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is not None
        assert hit.suspected_tool == "web_search"

    def test_case_insensitive(self):
        prose = "VOY A LLAMAR A LA HERRAMIENTA GITHUB ahora"
        hit = detect_ghost_in_response(
            response_text=prose,
            available_tool_names=DEFAULT_TOOLS,
            has_tool_calls=False,
        )
        assert hit is not None


class TestExecuteWithToolsAcceptsToolChoice:
    """Validar que router.execute_with_tools acepta tool_choice kwarg (T2 wiring)."""

    def test_signature_has_tool_choice_param(self):
        from inspect import signature

        from router.engine import RouterEngine

        sig = signature(RouterEngine.execute_with_tools)
        assert "tool_choice" in sig.parameters
        # Default debe ser "auto" para retro-compatibilidad
        param = sig.parameters["tool_choice"]
        assert param.default == "auto"
