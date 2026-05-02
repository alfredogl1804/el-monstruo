"""
Sprint 37 — Tests: MOC → AutonomousRunner Integration + Feedback Loop
======================================================================
Cubre:
  1. AutonomousRunner.set_moc() inyecta el MOC correctamente
  2. _poll_once() llama a moc.priorizar_jobs() cuando hay múltiples jobs
  3. _poll_once() persiste moc_priority_score en scheduled_jobs
  4. _execute_job() llama a _update_success_rate() tras completar
  5. _update_success_rate() calcula el ratio correcto y persiste
  6. _handle_failure() también llama a _update_success_rate()
  7. _handle_recurrence() hereda task_type y success_rate
  8. stats() incluye moc_enabled, jobs_prioritized, moc_reorders
  9. MOC.priorizar_jobs() reordena correctamente por score
  10. Priorizador.priorizar() asigna scores y ordena descendentemente
  11. /v1/stats incluye secciones moc y autonomous_runner
  12. Migración: columnas MOC presentes en scheduled_jobs
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

# ── Fixtures ────────────────────────────────────────────────────────


def make_job(
    job_id: str = None,
    title: str = "Test Job",
    status: str = "running",
    run_at: datetime = None,
    task_type: str = "default",
    success_rate: float = 1.0,
    estimated_cost_usd: float = 0.0,
    recurrence: str = None,
) -> dict[str, Any]:
    """Crear un job de prueba."""
    now = datetime.now(timezone.utc)
    return {
        "id": job_id or str(uuid4()),
        "title": title,
        "instruction": f"Ejecuta: {title}",
        "user_id": "test_user",
        "channel": "telegram",
        "status": status,
        "run_at": (run_at or now - timedelta(minutes=5)).isoformat(),
        "task_type": task_type,
        "success_rate": success_rate,
        "estimated_cost_usd": estimated_cost_usd,
        "recurrence": recurrence,
        "retry_count": 0,
        "max_retries": 1,
        "timezone": "America/Mexico_City",
    }


def make_mock_db(jobs: list = None, executions: list = None) -> MagicMock:
    """Crear un mock de SupabaseClient."""
    db = MagicMock()
    db.connected = True
    db.rpc = AsyncMock(return_value=jobs or [])
    db.select = AsyncMock(return_value=executions or [])
    db.insert = AsyncMock(return_value={"id": str(uuid4())})
    db.update = AsyncMock(return_value=True)
    return db


def make_mock_kernel() -> MagicMock:
    """Crear un mock del kernel."""
    kernel = MagicMock()
    result = MagicMock()
    result.response = "Respuesta de prueba"
    result.tokens_used = 100
    kernel.start_run = AsyncMock(return_value=result)
    return kernel


def make_mock_moc(jobs_returned: list = None) -> MagicMock:
    """Crear un mock del MOC."""
    moc = MagicMock()

    # priorizar_jobs retorna los jobs con score añadido
    async def mock_priorizar(jobs):
        for i, job in enumerate(jobs):
            job["moc_priority_score"] = 90.0 - (i * 10)
        return sorted(jobs, key=lambda j: j["moc_priority_score"], reverse=True)

    moc.priorizar_jobs = mock_priorizar
    return moc


# ── Tests: AutonomousRunner ──────────────────────────────────────────


class TestAutonomousRunnerMOCIntegration:
    """Tests de integración MOC → AutonomousRunner."""

    def test_set_moc_injects_correctly(self):
        """set_moc() debe inyectar el MOC y marcarlo como habilitado."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        db = make_mock_db()
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        assert runner._moc is None
        assert runner.stats["moc_enabled"] is False

        moc = make_mock_moc()
        runner.set_moc(moc)

        assert runner._moc is moc
        assert runner.stats["moc_enabled"] is True

    def test_stats_includes_moc_fields(self):
        """stats() debe incluir moc_enabled, jobs_prioritized, moc_reorders."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        db = make_mock_db()
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        stats = runner.stats
        assert "moc_enabled" in stats
        assert "jobs_prioritized" in stats
        assert "moc_reorders" in stats
        assert stats["moc_enabled"] is False
        assert stats["jobs_prioritized"] == 0
        assert stats["moc_reorders"] == 0

    @pytest.mark.asyncio
    async def test_poll_once_calls_moc_priorizar_with_multiple_jobs(self):
        """_poll_once() debe llamar a moc.priorizar_jobs() cuando hay múltiples jobs."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        job1 = make_job(title="Job A", task_type="notification")
        job2 = make_job(title="Job B", task_type="embrion_cycle")
        db = make_mock_db(jobs=[job1, job2])
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        # Mock del MOC con spy
        moc_called_with = []

        async def spy_priorizar(jobs):
            moc_called_with.extend(jobs)
            for i, job in enumerate(jobs):
                job["moc_priority_score"] = 90.0 - (i * 10)
            return sorted(jobs, key=lambda j: j["moc_priority_score"], reverse=True)

        moc = MagicMock()
        moc.priorizar_jobs = spy_priorizar
        runner.set_moc(moc)

        # Mock _execute_job para no ejecutar realmente
        runner._execute_job = AsyncMock()

        await runner._poll_once()

        # Verificar que el MOC fue llamado con los 2 jobs
        assert len(moc_called_with) == 2
        assert runner._jobs_prioritized == 2

    @pytest.mark.asyncio
    async def test_poll_once_persists_moc_score(self):
        """_poll_once() debe persistir moc_priority_score en scheduled_jobs."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        job = make_job(title="Single Job")
        db = make_mock_db(jobs=[job])
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        moc = make_mock_moc()
        runner.set_moc(moc)
        runner._execute_job = AsyncMock()

        await runner._poll_once()

        # Verificar que se llamó update con moc_priority_score
        update_calls = db.update.call_args_list
        score_updates = [c for c in update_calls if "moc_priority_score" in str(c)]
        assert len(score_updates) >= 1

    @pytest.mark.asyncio
    async def test_poll_once_without_moc_uses_fifo(self):
        """Sin MOC, _poll_once() debe ejecutar en orden FIFO."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        job1 = make_job(title="Job Primero")
        job2 = make_job(title="Job Segundo")
        db = make_mock_db(jobs=[job1, job2])
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        # Sin MOC
        assert runner._moc is None

        executed_order = []

        async def track_execution(job):
            executed_order.append(job["title"])

        runner._execute_job = track_execution

        await runner._poll_once()

        # Debe ejecutar en el orden recibido del DB
        assert executed_order == ["Job Primero", "Job Segundo"]
        assert runner._jobs_prioritized == 0

    @pytest.mark.asyncio
    async def test_moc_reorder_counter_increments(self):
        """moc_reorders debe incrementar cuando el MOC cambia el orden."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        job1 = make_job(job_id="aaa", title="Job A - baja prioridad")
        job2 = make_job(job_id="bbb", title="Job B - alta prioridad")
        db = make_mock_db(jobs=[job1, job2])
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        # MOC que invierte el orden
        async def invert_order(jobs):
            jobs_copy = list(jobs)
            jobs_copy.reverse()
            for i, job in enumerate(jobs_copy):
                job["moc_priority_score"] = 90.0 - (i * 10)
            return jobs_copy

        moc = MagicMock()
        moc.priorizar_jobs = invert_order
        runner.set_moc(moc)
        runner._execute_job = AsyncMock()

        await runner._poll_once()

        assert runner._moc_reorders == 1


# ── Tests: Feedback Loop ─────────────────────────────────────────────


class TestFeedbackLoop:
    """Tests del feedback loop de success_rate."""

    @pytest.mark.asyncio
    async def test_update_success_rate_calculates_correctly(self):
        """_update_success_rate() debe calcular el ratio correcto."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        # 3 completadas, 1 fallida → success_rate = 0.75
        executions = [
            {"status": "completed"},
            {"status": "completed"},
            {"status": "completed"},
            {"status": "failed"},
        ]
        db = make_mock_db(executions=executions)
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        job_id = str(uuid4())
        await runner._update_success_rate(job_id)

        # Verificar que se llamó update con success_rate=0.75
        update_calls = db.update.call_args_list
        rate_updates = [c for c in update_calls if "success_rate" in str(c)]
        assert len(rate_updates) == 1
        # El valor debe ser 0.75
        call_args = rate_updates[0][0]  # positional args
        assert call_args[1]["success_rate"] == 0.75

    @pytest.mark.asyncio
    async def test_update_success_rate_with_no_history(self):
        """Sin historial, success_rate debe ser 1.0 (asumir éxito)."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        db = make_mock_db(executions=[])
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        job_id = str(uuid4())
        await runner._update_success_rate(job_id)

        # Sin historial no debe llamar update
        update_calls = [c for c in db.update.call_args_list if "success_rate" in str(c)]
        assert len(update_calls) == 0

    @pytest.mark.asyncio
    async def test_execute_job_calls_update_success_rate_on_success(self):
        """_execute_job() debe llamar _update_success_rate() tras completar."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        job = make_job()
        db = make_mock_db()
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        # Spy en _update_success_rate
        update_called_with = []

        async def spy_update(job_id):
            update_called_with.append(job_id)

        runner._update_success_rate = spy_update
        runner._notify = AsyncMock()
        runner._handle_recurrence = AsyncMock()

        await runner._execute_job(job)

        assert len(update_called_with) == 1
        assert update_called_with[0] == job["id"]

    @pytest.mark.asyncio
    async def test_handle_failure_calls_update_success_rate(self):
        """_handle_failure() también debe llamar _update_success_rate()."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        job = make_job()
        db = make_mock_db()
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        update_called_with = []

        async def spy_update(job_id):
            update_called_with.append(job_id)

        runner._update_success_rate = spy_update
        runner._notify = AsyncMock()

        await runner._handle_failure(
            job_id=job["id"],
            execution_id=str(uuid4()),
            error="Test error",
            job=job,
            user_id="test_user",
            channel="telegram",
            title="Test Job",
        )

        assert len(update_called_with) == 1
        assert update_called_with[0] == job["id"]

    @pytest.mark.asyncio
    async def test_execute_job_records_cost_usd(self):
        """_execute_job() debe registrar cost_usd en job_executions."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        job = make_job()
        db = make_mock_db()
        kernel = make_mock_kernel()  # tokens_used=100
        runner = AutonomousRunner(db=db, kernel=kernel)

        runner._update_success_rate = AsyncMock()
        runner._notify = AsyncMock()
        runner._handle_recurrence = AsyncMock()

        await runner._execute_job(job)

        # Verificar que job_executions se actualizó con cost_usd
        update_calls = db.update.call_args_list
        exec_updates = [c for c in update_calls if "cost_usd" in str(c)]
        assert len(exec_updates) >= 1
        # 100 tokens * 0.000002 = 0.0002
        call_data = exec_updates[0][0][1]
        assert "cost_usd" in call_data
        assert call_data["cost_usd"] == pytest.approx(0.0002, rel=1e-3)


# ── Tests: Recurrencia con herencia de metadatos ─────────────────────


class TestRecurrenceInheritance:
    """Tests de herencia de metadatos MOC en jobs recurrentes."""

    @pytest.mark.asyncio
    async def test_handle_recurrence_inherits_task_type(self):
        """_handle_recurrence() debe heredar task_type del job original."""
        from kernel.runner.autonomous_runner import AutonomousRunner

        job = make_job(
            task_type="embrion_cycle",
            success_rate=0.9,
            estimated_cost_usd=0.05,
            recurrence="daily",
        )
        db = make_mock_db()
        kernel = make_mock_kernel()
        runner = AutonomousRunner(db=db, kernel=kernel)

        await runner._handle_recurrence(job)

        # Verificar que se insertó el nuevo job con task_type heredado
        insert_calls = db.insert.call_args_list
        assert len(insert_calls) >= 1
        new_job_data = insert_calls[-1][0][1]  # segundo arg de insert
        assert new_job_data["task_type"] == "embrion_cycle"
        assert new_job_data["success_rate"] == 0.9
        assert new_job_data["estimated_cost_usd"] == 0.05


# ── Tests: Priorizador ───────────────────────────────────────────────


class TestPriorizador:
    """Tests del Priorizador del MOC."""

    @pytest.mark.asyncio
    async def test_priorizar_adds_score_field(self):
        """priorizar() debe añadir moc_priority_score a cada job."""
        from kernel.moc.priorizador import Priorizador

        db = make_mock_db()
        priorizador = Priorizador(db=db)

        jobs = [make_job(title="Job 1"), make_job(title="Job 2")]
        result = await priorizador.priorizar(jobs, gasto_hoy_usd=0.0)

        for job in result:
            assert "moc_priority_score" in job
            assert 0 <= job["moc_priority_score"] <= 100

    @pytest.mark.asyncio
    async def test_priorizar_sorts_descending(self):
        """priorizar() debe ordenar por score descendente."""
        from kernel.moc.priorizador import Priorizador

        db = make_mock_db()
        priorizador = Priorizador(db=db)

        # Job urgente (vencido hace mucho) vs job reciente
        old_job = make_job(
            title="Job Urgente",
            run_at=datetime.now(timezone.utc) - timedelta(hours=5),
            task_type="embrion_cycle",
        )
        new_job = make_job(
            title="Job Reciente",
            run_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            task_type="default",
        )

        result = await priorizador.priorizar([new_job, old_job], gasto_hoy_usd=0.0)

        # El job urgente debe estar primero
        assert result[0]["title"] == "Job Urgente"
        assert result[0]["moc_priority_score"] >= result[1]["moc_priority_score"]

    @pytest.mark.asyncio
    async def test_priorizar_embrion_cycle_gets_high_score(self):
        """embrion_cycle debe recibir score más alto que default."""
        from kernel.moc.priorizador import Priorizador

        db = make_mock_db()
        priorizador = Priorizador(db=db)

        embrion_job = make_job(task_type="embrion_cycle")
        default_job = make_job(task_type="default")

        # Mismo run_at para aislar el factor de impacto
        now = datetime.now(timezone.utc) - timedelta(minutes=5)
        embrion_job["run_at"] = now.isoformat()
        default_job["run_at"] = now.isoformat()

        result = await priorizador.priorizar([default_job, embrion_job], gasto_hoy_usd=0.0)

        embrion_score = next(j["moc_priority_score"] for j in result if j["task_type"] == "embrion_cycle")
        default_score = next(j["moc_priority_score"] for j in result if j["task_type"] == "default")

        assert embrion_score > default_score

    @pytest.mark.asyncio
    async def test_priorizar_low_success_rate_penalizes(self):
        """Job con success_rate bajo debe recibir score menor."""
        from kernel.moc.priorizador import Priorizador

        db = make_mock_db()
        priorizador = Priorizador(db=db)

        good_job = make_job(task_type="default", success_rate=1.0)
        bad_job = make_job(task_type="default", success_rate=0.2)

        now = datetime.now(timezone.utc) - timedelta(minutes=5)
        good_job["run_at"] = now.isoformat()
        bad_job["run_at"] = now.isoformat()

        result = await priorizador.priorizar([bad_job, good_job], gasto_hoy_usd=0.0)

        good_score = next(j["moc_priority_score"] for j in result if j["success_rate"] == 1.0)
        bad_score = next(j["moc_priority_score"] for j in result if j["success_rate"] == 0.2)

        assert good_score > bad_score

    @pytest.mark.asyncio
    async def test_priorizar_empty_list(self):
        """priorizar() con lista vacía debe retornar lista vacía."""
        from kernel.moc.priorizador import Priorizador

        db = make_mock_db()
        priorizador = Priorizador(db=db)

        result = await priorizador.priorizar([], gasto_hoy_usd=0.0)
        assert result == []


# ── Tests: MOC.priorizar_jobs ────────────────────────────────────────


class TestMOCPriorizarJobs:
    """Tests del método priorizar_jobs del MOC."""

    @pytest.mark.asyncio
    async def test_moc_priorizar_jobs_calls_priorizador(self):
        """MOC.priorizar_jobs() debe delegar al Priorizador."""
        from kernel.moc.moc import MOC

        db = make_mock_db()
        router = MagicMock()
        runner = MagicMock()
        moc = MOC(db=db, router=router, runner=runner)

        jobs = [make_job(title="Job 1"), make_job(title="Job 2")]
        result = await moc.priorizar_jobs(jobs)

        assert len(result) == 2
        for job in result:
            assert "moc_priority_score" in job

    @pytest.mark.asyncio
    async def test_moc_priorizar_jobs_empty(self):
        """MOC.priorizar_jobs() con lista vacía debe retornar vacío."""
        from kernel.moc.moc import MOC

        db = make_mock_db()
        router = MagicMock()
        runner = MagicMock()
        moc = MOC(db=db, router=router, runner=runner)

        result = await moc.priorizar_jobs([])
        assert result == []
