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


# ──────────────────────────────────────────────────────────────────────
# DAN S5 SENTINEL PATTERN tests (added 2026-05-27 post-rebase)
# ──────────────────────────────────────────────────────────────────────
#
# Verifies execute_with_tools() honors the sentinel:
#   - tool_choice=None  -> derive via _tool_choice_for_intent (T4 path)
#   - tool_choice='required'/'auto'/'none' (explicit) -> caller wins (T2 path)
#
# Critical: T2 ghost-gate passes 'required' explicitly on re-prompt and MUST
# NOT be clobbered by T4 derivation.

from unittest.mock import AsyncMock, MagicMock, patch

import pytest as _pytest_sentinel

from router.engine import RouterEngine


class _StubLLMResponse:
    def __init__(self):
        self.content = "stub"
        self.tool_calls = []
        self.usage = {}


@_pytest_sentinel.fixture
def router_with_mocked_llm():
    """RouterEngine with chat_with_tools mocked to capture the tool_choice arg."""
    engine = RouterEngine(use_llm_classification=False)
    engine._llm.chat_with_tools = AsyncMock(return_value=_StubLLMResponse())
    return engine


class TestSentinelPatternCallerExplicitWins:
    """
    DAN S5 SENTINEL: when caller passes explicit tool_choice (not None),
    the value MUST be forwarded as-is to chat_with_tools, even when
    intent=EXECUTE+has_tools+!is_followup would otherwise derive 'required'.
    """

    @_pytest_sentinel.mark.asyncio
    async def test_caller_required_wins_over_derived_required(
        self, router_with_mocked_llm
    ):
        """T2 re-prompt: caller passes 'required' explicit -> forwarded as 'required'."""
        engine = router_with_mocked_llm
        await engine.execute_with_tools(
            message="ejecuta",
            model="gpt-5.5",
            intent=IntentType.EXECUTE,
            tools=[{"name": "github_ops"}],
            tool_choice="required",  # caller-explicit
        )
        forwarded = engine._llm.chat_with_tools.call_args.kwargs["tool_choice"]
        assert forwarded == "required", "caller 'required' must be honored"

    @_pytest_sentinel.mark.asyncio
    async def test_caller_auto_wins_over_derived_required(
        self, router_with_mocked_llm
    ):
        """Caller forces 'auto' even when intent=EXECUTE would derive 'required'."""
        engine = router_with_mocked_llm
        await engine.execute_with_tools(
            message="ejecuta",
            model="gpt-5.5",
            intent=IntentType.EXECUTE,
            tools=[{"name": "github_ops"}],
            tool_choice="auto",  # caller forces auto
        )
        forwarded = engine._llm.chat_with_tools.call_args.kwargs["tool_choice"]
        assert forwarded == "auto", "caller 'auto' must NOT be clobbered by T4"

    @_pytest_sentinel.mark.asyncio
    async def test_caller_none_value_wins_over_derived(
        self, router_with_mocked_llm
    ):
        """Caller explicitly passes 'none' (string) to forbid tools — must be honored."""
        engine = router_with_mocked_llm
        await engine.execute_with_tools(
            message="ejecuta",
            model="gpt-5.5",
            intent=IntentType.EXECUTE,
            tools=[{"name": "github_ops"}],
            tool_choice="none",  # caller forbids
        )
        forwarded = engine._llm.chat_with_tools.call_args.kwargs["tool_choice"]
        assert forwarded == "none", "caller 'none' must be honored"


class TestSentinelPatternNoneDerives:
    """
    When caller passes tool_choice=None (default), the helper
    _tool_choice_for_intent decides based on (intent, has_tools, is_followup).
    """

    @_pytest_sentinel.mark.asyncio
    async def test_none_with_execute_and_tools_derives_required(
        self, router_with_mocked_llm
    ):
        """Default sentinel: EXECUTE+tools+!followup -> 'required' (T4)."""
        engine = router_with_mocked_llm
        await engine.execute_with_tools(
            message="ejecuta",
            model="gpt-5.5",
            intent=IntentType.EXECUTE,
            tools=[{"name": "github_ops"}],
            # tool_choice not passed -> defaults to None
        )
        forwarded = engine._llm.chat_with_tools.call_args.kwargs["tool_choice"]
        assert forwarded == "required", "T4 must derive 'required' on EXECUTE+tools"

    @_pytest_sentinel.mark.asyncio
    async def test_none_with_chat_intent_derives_auto(self, router_with_mocked_llm):
        """Default sentinel: CHAT+tools+!followup -> 'auto'."""
        engine = router_with_mocked_llm
        await engine.execute_with_tools(
            message="hola",
            model="gpt-5.5",
            intent=IntentType.CHAT,
            tools=[{"name": "github_ops"}],
        )
        forwarded = engine._llm.chat_with_tools.call_args.kwargs["tool_choice"]
        assert forwarded == "auto"

    @_pytest_sentinel.mark.asyncio
    async def test_none_with_no_tools_derives_auto(self, router_with_mocked_llm):
        """Default sentinel: no tools -> 'auto' regardless of intent."""
        engine = router_with_mocked_llm
        await engine.execute_with_tools(
            message="ejecuta",
            model="gpt-5.5",
            intent=IntentType.EXECUTE,
            tools=[],
        )
        forwarded = engine._llm.chat_with_tools.call_args.kwargs["tool_choice"]
        assert forwarded == "auto"

    @_pytest_sentinel.mark.asyncio
    async def test_none_with_followup_derives_auto(self, router_with_mocked_llm):
        """Default sentinel: follow-up -> 'auto' (LLM narra resultado, no re-llama)."""
        engine = router_with_mocked_llm
        await engine.execute_with_tools(
            message="ejecuta",
            model="gpt-5.5",
            intent=IntentType.EXECUTE,
            tools=[{"name": "github_ops"}],
            tool_results=[
                {
                    "tool_call_id": "call_xyz",
                    "name": "github_ops",
                    "args": {},
                    "result": "ok",
                }
            ],
        )
        forwarded = engine._llm.chat_with_tools.call_args.kwargs["tool_choice"]
        assert forwarded == "auto"


class TestSentinelGhostGateScenario:
    """
    Reproducción del escenario T2 ghost-gate: en el re-prompt forzado tras
    detectar narración fantasma, el caller pasa tool_choice='required' para
    que el provider RECHACE prosa. T4 NO debe sobrescribir esto.
    """

    @_pytest_sentinel.mark.asyncio
    async def test_t2_reprompt_required_not_clobbered_by_t4(
        self, router_with_mocked_llm
    ):
        engine = router_with_mocked_llm

        # Simulamos exactamente lo que hace kernel/nodes.py::execute en el
        # re-prompt cuando detect_ghost_in_response devuelve un ghost match.
        await engine.execute_with_tools(
            message="dame la lista de PRs abiertas",
            model="gpt-5.5",
            intent=IntentType.EXECUTE,
            tools=[
                {"name": "github_ops"},
                {"name": "web_search"},
            ],
            tool_results=None,  # NOT a follow-up: fresh re-prompt
            tool_choice="required",  # T2 explicit
        )

        forwarded = engine._llm.chat_with_tools.call_args.kwargs["tool_choice"]
        assert forwarded == "required", (
            "REGRESION CRITICA: T4 sobrescribio el 'required' explicito de "
            "T2 ghost-gate. Esto reabre el bug ghost porque permite que el "
            "provider acepte prosa en el re-prompt forzado."
        )
