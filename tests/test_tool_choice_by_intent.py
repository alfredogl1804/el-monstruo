"""Tests for DAN T4 — tool_choice per intent in router/engine.py.

S5 KERNEL FIX 2026-05-27 — closes 2nd path of ghost bug:
even if model wants to narrate action in prose, provider REJECTS responses
without tool_calls when intent=EXECUTE and tools available.

Refs:
  - bridge/cowork_to_e1_S5_KERNEL_FIX_SPEC_2026_05_27.md (T4)
  - router/engine.py::_tool_choice_for_intent
"""
from __future__ import annotations

import pytest

from contracts.kernel_interface import IntentType
from router.engine import _tool_choice_for_intent


class TestNoTools:
    """Sin tools, siempre 'auto' (no hay nada que forzar)."""

    @pytest.mark.parametrize("intent", list(IntentType))
    def test_no_tools_always_auto(self, intent):
        assert _tool_choice_for_intent(intent, has_tools=False, is_followup=False) == "auto"

    @pytest.mark.parametrize("intent", list(IntentType))
    def test_no_tools_followup_still_auto(self, intent):
        assert _tool_choice_for_intent(intent, has_tools=False, is_followup=True) == "auto"


class TestFollowup:
    """En follow-up (tool_results presentes), siempre 'auto' — LLM narra resultado."""

    @pytest.mark.parametrize("intent", list(IntentType))
    def test_followup_always_auto(self, intent):
        # Aun con has_tools=True, follow-up debe NO forzar otro tool call
        assert (
            _tool_choice_for_intent(intent, has_tools=True, is_followup=True) == "auto"
        )


class TestExecuteIntent:
    """Intent EXECUTE + tools available + NO follow-up => 'required'."""

    def test_execute_with_tools_forces_required(self):
        assert (
            _tool_choice_for_intent(
                IntentType.EXECUTE, has_tools=True, is_followup=False
            )
            == "required"
        )

    def test_execute_no_tools_falls_back_to_auto(self):
        assert (
            _tool_choice_for_intent(
                IntentType.EXECUTE, has_tools=False, is_followup=False
            )
            == "auto"
        )

    def test_execute_in_followup_falls_back_to_auto(self):
        assert (
            _tool_choice_for_intent(
                IntentType.EXECUTE, has_tools=True, is_followup=True
            )
            == "auto"
        )


class TestNonExecuteIntents:
    """CHAT, DEEP_THINK, BACKGROUND, SYSTEM con tools => 'auto' (modelo decide)."""

    @pytest.mark.parametrize(
        "intent",
        [
            IntentType.CHAT,
            IntentType.DEEP_THINK,
            IntentType.BACKGROUND,
            IntentType.SYSTEM,
        ],
    )
    def test_non_execute_with_tools_stays_auto(self, intent):
        assert (
            _tool_choice_for_intent(intent, has_tools=True, is_followup=False)
            == "auto"
        )


class TestSemanticContract:
    """Contrato semantico: el helper debe retornar EXACTAMENTE 'auto'/'required'/'none'."""

    @pytest.mark.parametrize(
        "intent,has_tools,is_followup",
        [
            (IntentType.EXECUTE, True, False),
            (IntentType.EXECUTE, True, True),
            (IntentType.EXECUTE, False, False),
            (IntentType.CHAT, True, False),
            (IntentType.DEEP_THINK, True, False),
            (IntentType.BACKGROUND, False, True),
            (IntentType.SYSTEM, True, False),
        ],
    )
    def test_returns_canonical_string(self, intent, has_tools, is_followup):
        result = _tool_choice_for_intent(intent, has_tools, is_followup)
        assert result in {"auto", "required", "none"}, (
            f"Helper returned non-canonical value: {result!r}"
        )


class TestRegressionGhostBug:
    """
    Regresión del bug ghost S5 iPhone 2026-05-27:
    Mision real EXECUTE 'lista PRs abiertas' con tools=[github_ops, ...] debe
    forzar tool_choice='required' para que el provider rechace prosa sin FC.
    """

    def test_repro_ghost_mission_forces_required(self):
        # Reproducimos el escenario exacto del bug:
        # - intent=EXECUTE (el usuario pidio una accion)
        # - has_tools=True (github_ops, web_search, skill_read estan bound)
        # - is_followup=False (es la primera vuelta del LLM)
        intent = IntentType.EXECUTE
        has_tools = True
        is_followup = False

        result = _tool_choice_for_intent(intent, has_tools, is_followup)

        assert result == "required", (
            "REGRESION: ghost bug volveria a aparecer. "
            "Para mision EXECUTE con tools disponibles, el helper DEBE forzar "
            "'required' para que el provider rechace prosa sin tool_calls."
        )
