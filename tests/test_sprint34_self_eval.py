"""
Tests for Sprint 34: Self-Evaluation Loop + Memory Consolidation.

Tests the new methods added to EmbrionLoop:
- _parse_evaluation: robust parsing of judge responses
- _get_relevant_lessons: filtering of discarded/superseded lessons
- _apply_consolidation_decisions: parsing of consolidator responses

These are unit tests that don't require Supabase or LLM connections.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

# ── Test _parse_evaluation ──────────────────────────────────────────────


class TestParseEvaluation:
    """Test the robust parser for judge evaluation responses."""

    def _make_embrion(self):
        """Create a minimal EmbrionLoop instance for testing."""
        from kernel.embrion_loop import EmbrionLoop

        db = MagicMock()
        db.connected = False
        kernel = MagicMock()
        return EmbrionLoop(db=db, kernel=kernel)

    def test_standard_format(self):
        embrion = self._make_embrion()
        result = embrion._parse_evaluation("UTIL:SI | CALIDAD:8 | NOTA:Buen resultado")
        assert result["util"] is True
        assert result["calidad"] == 8
        assert "Buen resultado" in result["nota"]

    def test_negative_evaluation(self):
        embrion = self._make_embrion()
        result = embrion._parse_evaluation("UTIL:NO | CALIDAD:3 | NOTA:No contribuyó")
        assert result["util"] is False
        assert result["calidad"] == 3

    def test_malformed_response(self):
        embrion = self._make_embrion()
        result = embrion._parse_evaluation("This is not the expected format at all")
        # Should return defaults without crashing
        assert result["util"] is False
        assert result["calidad"] == 5  # default
        assert len(result["nota"]) > 0

    def test_partial_response(self):
        embrion = self._make_embrion()
        result = embrion._parse_evaluation("UTIL:SI | CALIDAD:9")
        assert result["util"] is True
        assert result["calidad"] == 9

    def test_calidad_clamped(self):
        embrion = self._make_embrion()
        result = embrion._parse_evaluation("UTIL:SI | CALIDAD:15 | NOTA:test")
        assert result["calidad"] == 10  # clamped to max

        result2 = embrion._parse_evaluation("UTIL:NO | CALIDAD:0 | NOTA:test")
        assert result2["calidad"] == 1  # clamped to min

    def test_yes_english(self):
        embrion = self._make_embrion()
        result = embrion._parse_evaluation("UTIL:YES | CALIDAD:7 | NOTA:Good")
        assert result["util"] is True

    def test_empty_response(self):
        embrion = self._make_embrion()
        result = embrion._parse_evaluation("")
        assert result["util"] is False
        assert result["calidad"] == 5


# ── Test lesson filtering ───────────────────────────────────────────────


class TestGetRelevantLessons:
    """Test that _get_relevant_lessons correctly filters lessons."""

    def _make_embrion(self):
        from kernel.embrion_loop import EmbrionLoop

        db = AsyncMock()
        db.connected = True
        kernel = MagicMock()
        return EmbrionLoop(db=db, kernel=kernel)

    @pytest.mark.asyncio
    async def test_filters_discarded(self):
        embrion = self._make_embrion()
        embrion._db.select = AsyncMock(
            return_value=[
                {
                    "contenido": "[ESTRATEGIA] Always create branch first",
                    "contexto": json.dumps({"estado": "consolidada"}),
                    "importancia": 8,
                },
                {
                    "contenido": "[GUARDRAIL] Never use sync httpx",
                    "contexto": json.dumps({"estado": "descartada"}),
                    "importancia": 1,
                },
                {
                    "contenido": "[ESTRATEGIA] Old merged rule",
                    "contexto": json.dumps({"estado": "superseded"}),
                    "importancia": 2,
                },
            ]
        )

        result = await embrion._get_relevant_lessons({"type": "reflexion_autonoma"})

        # Should include consolidated but NOT discarded or superseded
        assert "Always create branch first" in result
        assert "[CONSOLIDADA]" in result
        assert "Never use sync httpx" not in result
        assert "Old merged rule" not in result

    @pytest.mark.asyncio
    async def test_empty_when_no_lessons(self):
        embrion = self._make_embrion()
        embrion._db.select = AsyncMock(return_value=[])

        result = await embrion._get_relevant_lessons({"type": "reflexion_autonoma"})
        assert result == ""

    @pytest.mark.asyncio
    async def test_handles_db_error(self):
        embrion = self._make_embrion()
        embrion._db.select = AsyncMock(side_effect=Exception("DB connection lost"))

        result = await embrion._get_relevant_lessons({"type": "reflexion_autonoma"})
        assert result == ""


# ── Test consolidation decision parsing ─────────────────────────────────


class TestApplyConsolidationDecisions:
    """Test parsing of consolidator responses."""

    def _make_embrion(self):
        from kernel.embrion_loop import EmbrionLoop

        db = AsyncMock()
        db.connected = True
        db.update = AsyncMock()
        db.insert = AsyncMock()
        kernel = MagicMock()
        return EmbrionLoop(db=db, kernel=kernel)

    @pytest.mark.asyncio
    async def test_consolidate_decision(self):
        embrion = self._make_embrion()
        lessons = [
            {"id": "abc123", "contenido": "test lesson", "_ctx": {"estado": "provisional"}},
        ]

        response = "ID:abc123|ACCION:CONSOLIDAR|RAZON:Válida y útil"
        await embrion._apply_consolidation_decisions(response, lessons)

        # Should have called db.update to promote the lesson
        embrion._db.update.assert_called_once()
        call_args = embrion._db.update.call_args
        assert call_args.kwargs["filters"] == {"id": "abc123"}
        updated_ctx = json.loads(call_args.kwargs["data"]["contexto"])
        assert updated_ctx["estado"] == "consolidada"

    @pytest.mark.asyncio
    async def test_discard_decision(self):
        embrion = self._make_embrion()
        lessons = [
            {"id": "def456", "contenido": "bad lesson", "_ctx": {"estado": "provisional"}},
        ]

        response = "ID:def456|ACCION:DESCARTAR|RAZON:Redundante"
        await embrion._apply_consolidation_decisions(response, lessons)

        embrion._db.update.assert_called_once()
        call_args = embrion._db.update.call_args
        updated_ctx = json.loads(call_args.kwargs["data"]["contexto"])
        assert updated_ctx["estado"] == "descartada"
        assert call_args.kwargs["data"]["importancia"] == 1

    @pytest.mark.asyncio
    async def test_handles_unknown_ids(self):
        embrion = self._make_embrion()
        lessons = [
            {"id": "abc123", "contenido": "test", "_ctx": {"estado": "provisional"}},
        ]

        response = "ID:unknown_id|ACCION:CONSOLIDAR|RAZON:test"
        await embrion._apply_consolidation_decisions(response, lessons)

        # Should not crash, and should not call update (ID not found)
        embrion._db.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_malformed_response(self):
        embrion = self._make_embrion()
        lessons = [
            {"id": "abc123", "contenido": "test", "_ctx": {"estado": "provisional"}},
        ]

        response = "This is not the expected format"
        await embrion._apply_consolidation_decisions(response, lessons)

        # Should not crash
        embrion._db.update.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
