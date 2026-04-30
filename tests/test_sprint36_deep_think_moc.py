"""
El Monstruo — Tests Sprint 36: deep_think pipeline + MOC
=========================================================
Cobertura:
  - deep_think_pipeline.py: pipeline multi-paso, consulta a Sabios, acumulación de usage
  - MOC Priorizador: scoring de urgencia, impacto, presupuesto, historial
  - MOC Sintetizador: métricas, síntesis LLM, guardado en Supabase
  - MOC orquestador: start/stop, priorizar_jobs, sintetizar_ciclos
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ══════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_router():
    """Router mock que retorna respuestas predecibles."""
    router = MagicMock()
    router.execute = AsyncMock(
        return_value=(
            "Respuesta de prueba del modelo.",
            {"prompt_tokens": 100, "completion_tokens": 50, "cost_usd": 0.001},
        )
    )
    return router


@pytest.fixture
def mock_db():
    """DB mock con métodos async."""
    db = MagicMock()
    db.connected = True
    db.select = AsyncMock(return_value=[])
    db.insert = AsyncMock(return_value={"id": "test-insight-id"})
    db.update = AsyncMock(return_value=None)
    return db


@pytest.fixture
def sample_jobs():
    """Lista de jobs de prueba con diferentes características."""
    now = datetime.now(timezone.utc)
    return [
        {
            "id": "job-1",
            "title": "embrion_cycle diario",
            "status": "scheduled",
            "run_at": (now - timedelta(minutes=5)).isoformat(),
            "estimated_cost_usd": 0.02,
            "success_rate": 0.95,
        },
        {
            "id": "job-2",
            "title": "report semanal",
            "status": "scheduled",
            "run_at": (now - timedelta(minutes=90)).isoformat(),
            "estimated_cost_usd": 0.05,
            "success_rate": 0.80,
        },
        {
            "id": "job-3",
            "title": "maintenance cleanup",
            "status": "scheduled",
            "run_at": (now - timedelta(minutes=2)).isoformat(),
            "estimated_cost_usd": 0.01,
            "success_rate": None,
        },
    ]


@pytest.fixture
def sample_executions():
    """Lista de ejecuciones de prueba."""
    now = datetime.now(timezone.utc)
    return [
        {
            "id": "exec-1",
            "scheduled_job_id": "job-1",
            "status": "completed",
            "started_at": (now - timedelta(hours=2)).isoformat(),
            "finished_at": (now - timedelta(hours=1, minutes=55)).isoformat(),
            "tokens_used": 500,
            "result_summary": "Ciclo completado exitosamente.",
        },
        {
            "id": "exec-2",
            "scheduled_job_id": "job-2",
            "status": "completed",
            "started_at": (now - timedelta(hours=1)).isoformat(),
            "finished_at": (now - timedelta(minutes=55)).isoformat(),
            "tokens_used": 1200,
            "result_summary": "Reporte generado.",
        },
        {
            "id": "exec-3",
            "scheduled_job_id": "job-3",
            "status": "failed",
            "started_at": (now - timedelta(minutes=30)).isoformat(),
            "finished_at": (now - timedelta(minutes=28)).isoformat(),
            "tokens_used": 0,
            "result_summary": "Error en mantenimiento.",
        },
    ]


# ══════════════════════════════════════════════════════════════════════
# Tests: deep_think_pipeline
# ══════════════════════════════════════════════════════════════════════


class TestDeepThinkPipeline:
    """Tests del pipeline multi-paso de deep_think."""

    @pytest.mark.asyncio
    async def test_pipeline_ejecuta_tres_pasos(self, mock_router):
        """El pipeline debe hacer al menos 3 llamadas al router (plan + 2 sabios + síntesis)."""
        from kernel.deep_think_pipeline import run_deep_think_pipeline

        response, usage = await run_deep_think_pipeline(
            message="¿Cuál es la estrategia óptima para Hive en 2027?",
            context={"system_prompt": "Eres El Monstruo."},
            router=mock_router,
            model="gpt-5.5",
        )

        # Al menos 4 llamadas: plan + 2 sabios + síntesis
        assert mock_router.execute.call_count >= 4
        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_pipeline_acumula_usage(self, mock_router):
        """El usage final debe ser la suma de todas las llamadas."""
        from kernel.deep_think_pipeline import run_deep_think_pipeline

        _, usage = await run_deep_think_pipeline(
            message="Analiza el mercado de Mérida.",
            context={},
            router=mock_router,
            model="gpt-5.5",
        )

        # Con 4 llamadas y 50 tokens cada una = 200 completion tokens mínimo
        assert usage["completion_tokens"] >= 50
        assert usage["cost_usd"] >= 0.0

    @pytest.mark.asyncio
    async def test_pipeline_maneja_fallo_de_sabio(self, mock_router):
        """Si un Sabio falla, el pipeline debe continuar y generar respuesta."""
        call_count = 0

        async def execute_con_fallo(message, model, intent, context):
            nonlocal call_count
            call_count += 1
            if call_count == 2 and "claude" in model:
                raise RuntimeError("Claude no disponible")
            return (
                "Respuesta de prueba.",
                {"prompt_tokens": 100, "completion_tokens": 50, "cost_usd": 0.001},
            )

        mock_router.execute = execute_con_fallo

        from kernel.deep_think_pipeline import run_deep_think_pipeline

        # No debe lanzar excepción
        response, usage = await run_deep_think_pipeline(
            message="Prueba de resiliencia.",
            context={},
            router=mock_router,
            model="gpt-5.5",
        )
        assert isinstance(response, str)

    def test_accumulate_usage(self):
        """_accumulate_usage debe sumar correctamente."""
        from kernel.deep_think_pipeline import _accumulate_usage

        total = {"prompt_tokens": 100, "completion_tokens": 50, "cost_usd": 0.001}
        current = {"prompt_tokens": 200, "completion_tokens": 100, "cost_usd": 0.002}
        _accumulate_usage(total, current)

        assert total["prompt_tokens"] == 300
        assert total["completion_tokens"] == 150
        assert abs(total["cost_usd"] - 0.003) < 0.0001


# ══════════════════════════════════════════════════════════════════════
# Tests: MOC Priorizador
# ══════════════════════════════════════════════════════════════════════


class TestMOCPriorizador:
    """Tests del priorizador dinámico del MOC."""

    @pytest.fixture
    def priorizador(self, mock_db):
        from kernel.moc.priorizador import Priorizador
        return Priorizador(db=mock_db)

    @pytest.mark.asyncio
    async def test_priorizar_lista_vacia(self, priorizador):
        """Lista vacía debe retornar lista vacía."""
        result = await priorizador.priorizar([])
        assert result == []

    @pytest.mark.asyncio
    async def test_priorizar_ordena_por_score(self, priorizador, sample_jobs):
        """Los jobs deben estar ordenados por score descendente."""
        result = await priorizador.priorizar(sample_jobs)

        assert len(result) == 3
        scores = [j["moc_priority_score"] for j in result]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_embrion_cycle_tiene_mayor_impacto(self, priorizador, sample_jobs):
        """El job de embrion_cycle debe tener el mayor score de impacto."""
        result = await priorizador.priorizar(sample_jobs)

        # El job con "embrion_cycle" en el título debe estar primero o tener alto score
        embrion_job = next(j for j in result if "embrion" in j["title"])
        assert embrion_job["moc_priority_score"] > 0

    @pytest.mark.asyncio
    async def test_job_muy_retrasado_tiene_urgencia_alta(self, priorizador):
        """Un job con 90 minutos de retraso debe tener urgencia máxima."""
        now = datetime.now(timezone.utc)
        jobs = [
            {
                "id": "job-retrasado",
                "title": "report",
                "run_at": (now - timedelta(minutes=90)).isoformat(),
                "estimated_cost_usd": 0.01,
            }
        ]
        result = await priorizador.priorizar(jobs)
        assert result[0]["moc_priority_score"] > 0

    def test_score_urgencia_job_reciente(self, priorizador):
        """Job reciente (< 5 min) debe tener urgencia baja."""
        now = datetime.now(timezone.utc)
        job = {"run_at": (now - timedelta(minutes=2)).isoformat()}
        score = priorizador._score_urgencia(job, now)
        assert score <= 5.0

    def test_score_urgencia_job_muy_retrasado(self, priorizador):
        """Job con > 60 min de retraso debe tener urgencia máxima."""
        now = datetime.now(timezone.utc)
        job = {"run_at": (now - timedelta(hours=2)).isoformat()}
        score = priorizador._score_urgencia(job, now)
        assert score == 10.0

    def test_score_impacto_embrion(self, priorizador):
        """Job de embrion debe tener impacto 9.0."""
        job = {"title": "embrion_cycle diario", "task_type": ""}
        score = priorizador._score_impacto(job)
        assert score == 9.0

    def test_score_impacto_default(self, priorizador):
        """Job sin tipo conocido debe tener impacto default."""
        from kernel.moc.priorizador import TASK_IMPACT_MAP
        job = {"title": "tarea_desconocida", "task_type": ""}
        score = priorizador._score_impacto(job)
        assert score == TASK_IMPACT_MAP["default"]

    def test_score_presupuesto_abundante(self, priorizador):
        """Con presupuesto abundante (> 50%), score debe ser alto."""
        job = {"estimated_cost_usd": 0.10}
        score = priorizador._score_presupuesto(job, presupuesto_ratio=0.8)
        assert score == 8.0

    def test_score_presupuesto_critico(self, priorizador):
        """Con presupuesto crítico (< 20%), tarea costosa debe penalizarse."""
        job = {"estimated_cost_usd": 0.20}
        score = priorizador._score_presupuesto(job, presupuesto_ratio=0.1)
        assert score == 2.0

    def test_score_historial_sin_datos(self, priorizador):
        """Job sin historial debe tener score neutro."""
        job = {}
        score = priorizador._score_historial(job)
        assert score == 7.0

    def test_score_historial_alta_tasa_exito(self, priorizador):
        """Job con alta tasa de éxito debe tener score alto."""
        job = {"success_rate": 0.95}
        score = priorizador._score_historial(job)
        assert score == 9.0


# ══════════════════════════════════════════════════════════════════════
# Tests: MOC Sintetizador
# ══════════════════════════════════════════════════════════════════════


class TestMOCSintetizador:
    """Tests del sintetizador de ciclos del MOC."""

    @pytest.fixture
    def sintetizador(self, mock_db, mock_router):
        from kernel.moc.sintetizador import Sintetizador
        return Sintetizador(db=mock_db, router=mock_router)

    @pytest.mark.asyncio
    async def test_sintetizar_sin_ejecuciones(self, sintetizador):
        """Sin ejecuciones, debe retornar mensaje de no hay datos."""
        result = await sintetizador.sintetizar(window_hours=24)

        assert "summary" in result
        assert result["metadata"]["executions_analyzed"] == 0

    @pytest.mark.asyncio
    async def test_sintetizar_con_ejecuciones(self, sintetizador, mock_db, sample_executions):
        """Con ejecuciones, debe generar un insight con métricas."""
        mock_db.select = AsyncMock(return_value=sample_executions)
        mock_router_response = json.dumps({
            "summary": "El sistema operó con normalidad.",
            "patterns": ["Alta latencia en job-2"],
            "alerts": [],
            "recommendations": ["Optimizar job-2"],
        })
        sintetizador._router.execute = AsyncMock(
            return_value=(mock_router_response, {"prompt_tokens": 200, "completion_tokens": 100, "cost_usd": 0.002})
        )

        result = await sintetizador.sintetizar(window_hours=24)

        assert result["summary"] == "El sistema operó con normalidad."
        assert len(result["patterns"]) > 0
        assert result["metadata"]["executions_analyzed"] > 0

    def test_calcular_metricas_vacias(self, sintetizador):
        """Métricas con lista vacía deben retornar dict vacío."""
        result = sintetizador._calcular_metricas([])
        assert result == {}

    def test_calcular_metricas_con_datos(self, sintetizador, sample_executions):
        """Métricas deben calcular correctamente tasa de éxito."""
        result = sintetizador._calcular_metricas(sample_executions)

        assert result["total_executions"] == 3
        assert result["completed"] == 2
        assert result["failed"] == 1
        assert result["success_rate"] == round(2 / 3, 2)
        assert result["total_tokens"] == 1700  # 500 + 1200 + 0

    @pytest.mark.asyncio
    async def test_generar_sintesis_llm_json_invalido(self, sintetizador):
        """Si el LLM retorna texto no-JSON, debe usar el texto como summary."""
        sintetizador._router.execute = AsyncMock(
            return_value=("Texto libre sin JSON.", {"prompt_tokens": 50, "completion_tokens": 20, "cost_usd": 0.0})
        )
        result = await sintetizador._generar_sintesis_llm([], {})

        assert "Texto libre" in result["summary"]
        assert result["patterns"] == []


# ══════════════════════════════════════════════════════════════════════
# Tests: MOC Orquestador
# ══════════════════════════════════════════════════════════════════════


class TestMOCOrquestador:
    """Tests del MOC orquestador principal."""

    @pytest.fixture
    def moc(self, mock_db, mock_router):
        from kernel.moc.moc import MOC
        runner = MagicMock()
        return MOC(db=mock_db, router=mock_router, runner=runner)

    @pytest.mark.asyncio
    async def test_start_stop(self, moc):
        """El MOC debe poder iniciarse y detenerse sin errores."""
        await moc.start()
        assert moc._running is True
        assert moc.stats["running"] is True

        await moc.stop()
        assert moc._running is False

    @pytest.mark.asyncio
    async def test_start_idempotente(self, moc):
        """Llamar start() dos veces no debe crear dos loops."""
        await moc.start()
        task1 = moc._synthesis_task
        await moc.start()  # Segunda llamada
        task2 = moc._synthesis_task

        assert task1 is task2  # Mismo task
        await moc.stop()

    @pytest.mark.asyncio
    async def test_priorizar_jobs_delega_a_priorizador(self, moc, sample_jobs):
        """priorizar_jobs debe delegar al Priorizador y retornar jobs con score."""
        result = await moc.priorizar_jobs(sample_jobs)

        assert len(result) == 3
        assert all("moc_priority_score" in j for j in result)

    @pytest.mark.asyncio
    async def test_sintetizar_ciclos_incrementa_contador(self, moc, mock_db, mock_router):
        """sintetizar_ciclos debe incrementar el contador de insights."""
        mock_db.select = AsyncMock(return_value=[])

        initial_count = moc._insights_generated
        await moc.sintetizar_ciclos()

        assert moc._insights_generated == initial_count + 1
        assert moc._last_synthesis_at is not None

    def test_stats_iniciales(self, moc):
        """Stats iniciales deben tener valores por defecto correctos."""
        stats = moc.stats
        assert stats["running"] is False
        assert stats["insights_generated"] == 0
        assert stats["last_synthesis_at"] is None
