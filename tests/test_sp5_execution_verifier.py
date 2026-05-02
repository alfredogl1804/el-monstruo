"""
Tests SP5 — Execution Verifier (ACI Repair)
=============================================
Validates the ExecutionVerifier: verdict logic, evidence extraction,
persistence, and integration with TaskPlanner.

The core ACI bug: plans completing with tool_calls = 0.
These tests ensure the verifier catches this and blocks false DONE.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from kernel.execution_verifier import (
    EvidenceType,
    ExecutionVerifier,
    Verdict,
    VerificationResult,
)

# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def mock_db():
    """Mock del SupabaseClient para tests."""
    db = MagicMock()
    db.insert = AsyncMock(return_value={"verification_id": "test-id"})
    db.update = AsyncMock(return_value=True)
    db.select = AsyncMock(return_value=[])
    return db


@pytest.fixture
def verifier(mock_db):
    """ExecutionVerifier con DB mockeada."""
    return ExecutionVerifier(db=mock_db)


@pytest.fixture
def verifier_no_db():
    """ExecutionVerifier sin DB (modo degradado)."""
    return ExecutionVerifier(db=None)


# ── Tests: Verdict Logic ─────────────────────────────────────────────


class TestVerdictLogic:
    """Tests para la lógica de veredictos del verificador."""

    @pytest.mark.asyncio
    async def test_success_when_tools_called_with_evidence(self, verifier):
        """SUCCESS: tool_calls > 0 + evidencia concreta = paso realmente ejecutado."""
        result = await verifier.verify_step(
            plan_id="plan-001",
            step_id="step-001",
            step_index=0,
            step_description="Buscar información sobre LangGraph",
            tool_call_history=[
                ("web_search", "abc123"),
                ("browse_web", "def456"),
            ],
            step_tool_calls=2,
            final_response="Encontré la documentación de LangGraph en https://...",
            plan_total_tool_calls=2,
        )

        assert result.verdict == Verdict.SUCCESS
        assert result.tool_calls_count == 2
        assert len(result.evidence) > 0
        assert result.task_id == "plan-001"
        assert result.step_id == "step-001"

    @pytest.mark.asyncio
    async def test_continue_when_no_tools_called(self, verifier):
        """CONTINUE: tool_calls = 0 + sin evidencia = paso NO ejecutado (el bug ACI)."""
        result = await verifier.verify_step(
            plan_id="plan-002",
            step_id="step-002",
            step_index=0,
            step_description="Crear un archivo con el código del módulo",
            tool_call_history=[],
            step_tool_calls=0,
            final_response="He creado el archivo con el código necesario.",
            plan_total_tool_calls=0,
        )

        assert result.verdict == Verdict.CONTINUE
        assert result.tool_calls_count == 0
        # Must have NONE evidence
        none_evidence = [e for e in result.evidence if e.get("type") == EvidenceType.NONE.value]
        assert len(none_evidence) > 0

    @pytest.mark.asyncio
    async def test_pivot_on_stuck_signal(self, verifier):
        """PIVOT: respuesta contiene señal de atasco = cambiar enfoque."""
        result = await verifier.verify_step(
            plan_id="plan-003",
            step_id="step-003",
            step_index=1,
            step_description="Ejecutar el script de migración",
            tool_call_history=[("code_exec", "aaa111")],
            step_tool_calls=1,
            final_response="[STUCK] El agente repitió code_exec 3 veces con los mismos argumentos. Paso abortado.",
            plan_total_tool_calls=1,
        )

        assert result.verdict == Verdict.PIVOT
        pivot_evidence = [e for e in result.evidence if e.get("type") == "pivot_signal"]
        assert len(pivot_evidence) > 0

    @pytest.mark.asyncio
    async def test_pivot_on_cap_signal(self, verifier):
        """PIVOT: señal [CAP] = límite de herramientas alcanzado."""
        result = await verifier.verify_step(
            plan_id="plan-004",
            step_id="step-004",
            step_index=0,
            step_description="Analizar el repositorio",
            tool_call_history=[("browse_web", "bbb222")] * 12,
            step_tool_calls=12,
            final_response="[CAP] Se alcanzó el límite de 12 llamadas a herramientas en este paso.",
            plan_total_tool_calls=12,
        )

        assert result.verdict == Verdict.PIVOT


# ── Tests: Evidence Extraction ───────────────────────────────────────


class TestEvidenceExtraction:
    """Tests para la extracción de evidencia concreta."""

    @pytest.mark.asyncio
    async def test_evidence_maps_tool_names_correctly(self, verifier):
        """La evidencia debe mapear nombres de herramientas a tipos correctos."""
        result = await verifier.verify_step(
            plan_id="plan-010",
            step_id="step-010",
            step_index=0,
            step_description="Buscar y crear archivo",
            tool_call_history=[
                ("web_search", "aaa"),
                ("code_exec", "bbb"),
                ("github", "ccc"),
            ],
            step_tool_calls=3,
            final_response="Busqué, ejecuté código y creé el archivo en GitHub.",
            plan_total_tool_calls=3,
        )

        evidence_types = [e.get("type") for e in result.evidence]
        assert EvidenceType.SEARCH_RESULTS.value in evidence_types
        assert EvidenceType.CODE_EXECUTED.value in evidence_types
        assert EvidenceType.FILE_CREATED.value in evidence_types

    @pytest.mark.asyncio
    async def test_evidence_includes_summary(self, verifier):
        """La evidencia debe incluir un resumen con conteos."""
        result = await verifier.verify_step(
            plan_id="plan-011",
            step_id="step-011",
            step_index=0,
            step_description="Paso de prueba",
            tool_call_history=[("web_search", "xxx")],
            step_tool_calls=1,
            final_response="Resultado de la búsqueda...",
            plan_total_tool_calls=1,
        )

        summaries = [e for e in result.evidence if e.get("type") == "summary"]
        assert len(summaries) == 1
        assert summaries[0]["total_tool_calls"] == 1
        assert "web_search" in summaries[0]["unique_tools"]

    @pytest.mark.asyncio
    async def test_no_tools_produces_none_evidence(self, verifier):
        """Sin herramientas = evidencia tipo NONE."""
        result = await verifier.verify_step(
            plan_id="plan-012",
            step_id="step-012",
            step_index=0,
            step_description="Paso sin herramientas",
            tool_call_history=[],
            step_tool_calls=0,
            final_response="Lo hice mentalmente.",
            plan_total_tool_calls=0,
        )

        none_evidence = [e for e in result.evidence if e.get("type") == EvidenceType.NONE.value]
        assert len(none_evidence) > 0


# ── Tests: Persistence ───────────────────────────────────────────────


class TestVerificationPersistence:
    """Tests para la persistencia en Supabase."""

    @pytest.mark.asyncio
    async def test_result_persisted_to_db(self, verifier, mock_db):
        """El resultado debe persistirse en la tabla verification_results."""
        await verifier.verify_step(
            plan_id="plan-020",
            step_id="step-020",
            step_index=0,
            step_description="Paso de persistencia",
            tool_call_history=[("web_search", "aaa")],
            step_tool_calls=1,
            final_response="Resultado...",
            plan_total_tool_calls=1,
        )

        # Verify insert was called
        mock_db.insert.assert_called_once()
        call_args = mock_db.insert.call_args
        assert call_args[0][0] == "verification_results"
        row = call_args[0][1]
        assert row["task_id"] == "plan-020"
        assert row["step_id"] == "step-020"
        assert row["verdict"] == "success"
        assert row["tool_calls_count"] == 1

    @pytest.mark.asyncio
    async def test_no_db_skips_persistence(self, verifier_no_db):
        """Sin DB, la verificación funciona pero no persiste."""
        result = await verifier_no_db.verify_step(
            plan_id="plan-021",
            step_id="step-021",
            step_index=0,
            step_description="Paso sin DB",
            tool_call_history=[("code_exec", "bbb")],
            step_tool_calls=1,
            final_response="Ejecuté el código.",
            plan_total_tool_calls=1,
        )

        # Should still produce a verdict
        assert result.verdict == Verdict.SUCCESS

    @pytest.mark.asyncio
    async def test_db_error_doesnt_crash(self, mock_db):
        """Error en DB no debe crashear la verificación."""
        mock_db.insert = AsyncMock(side_effect=Exception("DB connection failed"))
        verifier = ExecutionVerifier(db=mock_db)

        result = await verifier.verify_step(
            plan_id="plan-022",
            step_id="step-022",
            step_index=0,
            step_description="Paso con DB rota",
            tool_call_history=[("web_search", "ccc")],
            step_tool_calls=1,
            final_response="Resultado...",
            plan_total_tool_calls=1,
        )

        # Should still produce a verdict despite DB failure
        assert result.verdict == Verdict.SUCCESS


# ── Tests: VerificationResult Serialization ──────────────────────────


class TestVerificationResultSerialization:
    """Tests para la serialización de VerificationResult."""

    def test_to_dict_has_required_fields(self):
        """to_dict debe incluir todos los campos requeridos."""
        result = VerificationResult(
            task_id="plan-030",
            step_id="step-030",
            step_index=0,
            verdict=Verdict.SUCCESS,
            evidence=[{"type": "tool_output", "tool": "web_search"}],
            reasoning="Structural: PASS | Evidence: 1 items",
            tool_calls_count=1,
            cost_usd=0.001,
        )

        d = result.to_dict()
        required = [
            "verification_id",
            "task_id",
            "step_id",
            "step_index",
            "verdict",
            "evidence",
            "reasoning",
            "tool_calls_count",
            "cost_usd",
            "verified_at",
        ]
        for field in required:
            assert field in d, f"Campo '{field}' faltante en to_dict()"

    def test_verdict_serializes_as_string(self):
        """El veredicto debe serializarse como string."""
        result = VerificationResult(
            task_id="plan-031",
            step_id="step-031",
            step_index=0,
            verdict=Verdict.CONTINUE,
            evidence=[],
            reasoning="Test",
            tool_calls_count=0,
        )

        d = result.to_dict()
        assert d["verdict"] == "continue"
        assert isinstance(d["verdict"], str)


# ── Tests: Stats ─────────────────────────────────────────────────────


class TestVerifierStats:
    """Tests para las estadísticas del verificador."""

    @pytest.mark.asyncio
    async def test_stats_track_verdicts(self, verifier):
        """Las estadísticas deben rastrear los veredictos correctamente."""
        # SUCCESS
        await verifier.verify_step(
            plan_id="p1",
            step_id="s1",
            step_index=0,
            step_description="Paso 1",
            tool_call_history=[("web_search", "a")],
            step_tool_calls=1,
            final_response="OK",
            plan_total_tool_calls=1,
        )

        # CONTINUE (no tools)
        await verifier.verify_step(
            plan_id="p2",
            step_id="s2",
            step_index=0,
            step_description="Paso 2",
            tool_call_history=[],
            step_tool_calls=0,
            final_response="Hecho",
            plan_total_tool_calls=0,
        )

        stats = verifier.get_stats()
        assert stats["total_verifications"] == 2
        assert stats["verdicts"]["success"] == 1
        assert stats["verdicts"]["continue"] == 1
        assert stats["success_rate"] == 0.5


# ── Tests: Verdict Enum ──────────────────────────────────────────────


class TestVerdictEnum:
    """Tests para el enum Verdict."""

    def test_verdict_values(self):
        """Verdict debe tener los 3 valores esperados."""
        assert Verdict.SUCCESS == "success"
        assert Verdict.CONTINUE == "continue"
        assert Verdict.PIVOT == "pivot"

    def test_evidence_type_values(self):
        """EvidenceType debe tener los tipos esperados."""
        assert EvidenceType.TOOL_OUTPUT == "tool_output"
        assert EvidenceType.FILE_CREATED == "file_created"
        assert EvidenceType.CODE_EXECUTED == "code_executed"
        assert EvidenceType.NONE == "none"


# ── Tests: Integration with TaskPlanner ──────────────────────────────


class TestPlannerIntegration:
    """Tests para la integración del verificador con el TaskPlanner."""

    def test_planner_initializes_verifier(self):
        """TaskPlanner debe inicializar el ExecutionVerifier."""
        from kernel.task_planner import TaskPlanner

        kernel = MagicMock()
        db = MagicMock()
        db.insert = AsyncMock()
        db.update = AsyncMock()
        db.select = AsyncMock(return_value=[])
        db.upsert = AsyncMock()

        planner = TaskPlanner(kernel=kernel, db=db)
        assert planner._verifier is not None

    def test_planner_without_db_still_has_verifier(self):
        """TaskPlanner sin DB aún debe tener verificador."""
        from kernel.task_planner import TaskPlanner

        kernel = MagicMock()

        planner = TaskPlanner(kernel=kernel, db=None)
        assert planner._verifier is not None

    def test_execution_verifier_importable(self):
        """ExecutionVerifier debe ser importable."""
        from kernel.execution_verifier import EvidenceType, ExecutionVerifier, Verdict

        assert ExecutionVerifier is not None
        assert Verdict is not None
        assert EvidenceType is not None
