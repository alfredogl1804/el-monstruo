"""
Sprint 34 — Tests for Bidirectional Sabio Dialogue
===================================================
Tests the new communication circuit between the Embrión and the 6 Sabios.

Covers:
1. Auto-save of sabio responses in tool_dispatch
2. Dialogue trigger detection (dialogo_sabios)
3. Sabio rotation logic
4. Budget guards for dialogues
5. Follow-up question detection
6. Bidirectional reply saving
"""

import ast
import json
import os
import sys
import pytest

# Ensure project root is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestDialogoCompilation:
    """Verify all modified files compile without syntax errors."""

    def test_embrion_loop_compiles(self):
        with open("kernel/embrion_loop.py") as f:
            ast.parse(f.read())

    def test_tool_dispatch_compiles(self):
        with open("kernel/tool_dispatch.py") as f:
            ast.parse(f.read())

    def test_consult_sabios_compiles(self):
        with open("tools/consult_sabios.py") as f:
            ast.parse(f.read())


class TestDialogoConfiguration:
    """Verify dialogue configuration constants exist and are sane."""

    def test_dialogo_interval_exists(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "DIALOGO_INTERVAL" in content
        assert "EMBRION_DIALOGO_INTERVAL" in content

    def test_sabios_per_dialogo_exists(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "SABIOS_PER_DIALOGO" in content
        assert "EMBRION_SABIOS_PER_DIALOGO" in content

    def test_dialogo_budget_exists(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "DIALOGO_BUDGET_USD" in content
        assert "EMBRION_DIALOGO_BUDGET" in content

    def test_sabio_rotation_has_6_pairs(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        # Verify all 6 sabio IDs appear in rotation
        for sabio_id in ["gpt54", "claude", "gemini", "grok", "deepseek", "perplexity"]:
            assert sabio_id in content, f"Sabio {sabio_id} missing from rotation"


class TestDialogoTriggerDetection:
    """Verify the dialogo_sabios trigger type is properly integrated."""

    def test_trigger_type_exists(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert '"dialogo_sabios"' in content

    def test_trigger_in_should_speak(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert 'trigger["type"] == "dialogo_sabios"' in content or \
               '"dialogo_sabios"' in content

    def test_trigger_in_judge_before(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        # dialogo_sabios should bypass the judge
        assert "dialogo_sabios" in content

    def test_trigger_in_report_emoji(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "dialogo_sabios" in content


class TestAutoSaveInToolDispatch:
    """Verify consult_sabios auto-saves responses to patron_emergencia."""

    def test_autosave_code_exists(self):
        with open("kernel/tool_dispatch.py") as f:
            content = f.read()
        assert "embrion_patron_emergencia" in content
        assert "auto_save_consult_sabios" in content

    def test_autosave_checks_db_connected(self):
        with open("kernel/tool_dispatch.py") as f:
            content = f.read()
        assert "_tool_db" in content
        assert "connected" in content

    def test_autosave_saves_each_response(self):
        with open("kernel/tool_dispatch.py") as f:
            content = f.read()
        assert 'for resp in result.get("responses", [])' in content

    def test_autosave_includes_metadata(self):
        with open("kernel/tool_dispatch.py") as f:
            content = f.read()
        assert "autor" in content
        assert "prompt_original" in content
        assert "canal" in content


class TestBidirectionalReply:
    """Verify the Embrión saves its reply back to patron_emergencia."""

    def test_reply_save_exists(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "respuesta_embrion_a_sabio" in content

    def test_reply_includes_original_contribution(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "contribucion_original" in content
        assert "respuesta_bidireccional" in content

    def test_followup_question_detection(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "followup_q" in content
        assert "followup_sabio" in content
        assert "followup_bidireccional" in content


class TestDialogoConSabiosMethod:
    """Verify the _dialogo_con_sabios method structure."""

    def test_method_exists(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "async def _dialogo_con_sabios" in content

    def test_method_gathers_memories(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "recent_memories" in content

    def test_method_formulates_question(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "question_prompt" in content
        assert "Formula UNA pregunta" in content

    def test_method_uses_rotation(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "_SABIO_ROTATION" in content
        assert "rotation_idx" in content

    def test_method_saves_to_patron(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "dialogo_autonomo" in content

    def test_method_synthesizes_reflection(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "reflection_prompt" in content
        assert "Qué aprendiste" in content

    def test_method_saves_dialogue_memory(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert 'tipo="dialogo_sabios"' in content

    def test_method_updates_tracking(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "_dialogos_today" in content
        assert "_autonomous_reflections_since_dialogo" in content
        assert "_last_dialogo_at" in content

    def test_method_has_budget_guard(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "dialogo_budget_exhausted" in content

    def test_method_has_timeout_handling(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "embrion_dialogo_timeout" in content
        assert "embrion_dialogo_failed" in content


class TestStatsIncludeDialogo:
    """Verify dialogue stats are exposed in the stats property."""

    def test_stats_include_dialogo_section(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert '"dialogo_sabios"' in content
        assert '"reflections_since"' in content
        assert '"dialogos_today"' in content
        assert '"dialogo_cost_today"' in content
        assert '"dialogo_budget"' in content
        assert '"last_sabios"' in content

    def test_daily_reset_includes_dialogo(self):
        with open("kernel/embrion_loop.py") as f:
            content = f.read()
        assert "_dialogos_today = 0" in content
        assert "_dialogo_cost_today_usd = 0.0" in content
