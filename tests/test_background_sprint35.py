"""
El Monstruo — Tests: Background Mode Sprint 35
================================================
Cubre los 4 gaps que llevaban el modo background al 10%:

    Gap 1: Persistencia en Supabase (BackgroundStore)
    Gap 2: Progreso en tiempo real (progress_log + SSE endpoint)
    Gap 3: Cancelación de jobs activos
    Gap 4: Tests (este archivo)

Ejecutar:
    pytest tests/test_background_sprint35.py -v
"""

from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from kernel.background_store import BackgroundStore

# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def store_inmemory():
    """BackgroundStore sin Supabase (modo in-memory)."""
    return BackgroundStore(db=None)


@pytest.fixture
def mock_db():
    """Mock de SupabaseClient con _connected=True."""
    db = MagicMock()
    db._connected = True
    # Mock del client de Supabase
    table_mock = MagicMock()
    db._client.table.return_value = table_mock
    table_mock.insert.return_value = table_mock
    table_mock.update.return_value = table_mock
    table_mock.select.return_value = table_mock
    table_mock.eq.return_value = table_mock
    table_mock.order.return_value = table_mock
    table_mock.limit.return_value = table_mock
    table_mock.execute.return_value = MagicMock(data=[])
    db._client.rpc.return_value = MagicMock()
    db._client.rpc.return_value.execute.return_value = MagicMock()
    return db


@pytest.fixture
def store_with_db(mock_db):
    """BackgroundStore con Supabase mockeado."""
    return BackgroundStore(db=mock_db)


# ── Gap 1: Persistencia ───────────────────────────────────────────────


class TestPersistencia:
    """Gap 1: Jobs deben sobrevivir a reinicios (Supabase como backend)."""

    @pytest.mark.asyncio
    async def test_create_job_inmemory(self, store_inmemory):
        """Job se crea correctamente en modo in-memory."""
        job_id = str(uuid4())
        result = await store_inmemory.create(
            job_id=job_id,
            message="Test message",
            user_id="test_user",
        )
        assert result == job_id
        job = await store_inmemory.get(job_id)
        assert job is not None
        assert job["status"] == "queued"
        assert job["message"] == "Test message"
        assert job["user_id"] == "test_user"

    @pytest.mark.asyncio
    async def test_create_job_with_all_fields(self, store_inmemory):
        """Job se crea con todos los campos opcionales."""
        job_id = str(uuid4())
        await store_inmemory.create(
            job_id=job_id,
            message="Full test",
            user_id="alfredo",
            channel="telegram",
            brain="monstruo",
            session_id="sess_123",
            metadata={"key": "value"},
            webhook_url="https://example.com/webhook",
        )
        job = await store_inmemory.get(job_id)
        assert job["brain"] == "monstruo"
        assert job["session_id"] == "sess_123"
        assert job["webhook_url"] == "https://example.com/webhook"

    @pytest.mark.asyncio
    async def test_get_nonexistent_job(self, store_inmemory):
        """Get de job inexistente retorna None."""
        result = await store_inmemory.get("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_jobs_empty(self, store_inmemory):
        """List de jobs vacío retorna lista vacía."""
        result = await store_inmemory.list_jobs()
        assert result == []

    @pytest.mark.asyncio
    async def test_list_jobs_with_filter(self, store_inmemory):
        """List filtra correctamente por user_id."""
        job_id_1 = str(uuid4())
        job_id_2 = str(uuid4())
        await store_inmemory.create(job_id=job_id_1, message="msg1", user_id="user_a")
        await store_inmemory.create(job_id=job_id_2, message="msg2", user_id="user_b")

        result_a = await store_inmemory.list_jobs(user_id="user_a")
        result_b = await store_inmemory.list_jobs(user_id="user_b")

        assert len(result_a) == 1
        assert result_a[0]["user_id"] == "user_a"
        assert len(result_b) == 1
        assert result_b[0]["user_id"] == "user_b"

    @pytest.mark.asyncio
    async def test_use_db_false_without_db(self, store_inmemory):
        """_use_db() retorna False cuando no hay Supabase."""
        assert store_inmemory._use_db() is False

    @pytest.mark.asyncio
    async def test_use_db_true_with_connected_db(self, store_with_db):
        """_use_db() retorna True cuando Supabase está conectado."""
        assert store_with_db._use_db() is True


# ── Gap 2: Progreso en tiempo real ────────────────────────────────────


class TestProgreso:
    """Gap 2: El progreso debe actualizarse durante la ejecución."""

    @pytest.mark.asyncio
    async def test_initial_progress_is_zero(self, store_inmemory):
        """Job recién creado tiene progreso 0."""
        job_id = str(uuid4())
        await store_inmemory.create(job_id=job_id, message="test")
        job = await store_inmemory.get(job_id)
        assert job["progress"] == 0
        assert job["progress_log"] == []

    @pytest.mark.asyncio
    async def test_append_progress_updates_pct(self, store_inmemory):
        """append_progress actualiza el porcentaje y el log."""
        job_id = str(uuid4())
        await store_inmemory.create(job_id=job_id, message="test")

        await store_inmemory.append_progress(job_id, 25, "Iniciando")
        await store_inmemory.append_progress(job_id, 50, "Procesando")
        await store_inmemory.append_progress(job_id, 75, "Finalizando")

        job = await store_inmemory.get(job_id)
        assert job["progress"] == 75
        assert len(job["progress_log"]) == 3
        assert job["progress_log"][0]["pct"] == 25
        assert job["progress_log"][1]["msg"] == "Procesando"
        assert job["progress_log"][2]["pct"] == 75

    @pytest.mark.asyncio
    async def test_completed_job_has_100_progress(self, store_inmemory):
        """Job completado tiene progreso 100."""
        job_id = str(uuid4())
        await store_inmemory.create(job_id=job_id, message="test")
        await store_inmemory.set_running(job_id)
        await store_inmemory.set_completed(
            job_id,
            {
                "run_id": "test",
                "status": "completed",
                "response": "ok",
                "tokens_in": 10,
                "tokens_out": 20,
                "cost_usd": 0.001,
                "latency_ms": 500,
            },
        )
        job = await store_inmemory.get(job_id)
        assert job["progress"] == 100
        assert job["status"] == "completed"


# ── Gap 3: Cancelación ────────────────────────────────────────────────


class TestCancelacion:
    """Gap 3: Jobs deben poder cancelarse mientras están en cola o corriendo."""

    @pytest.mark.asyncio
    async def test_cancel_queued_job(self, store_inmemory):
        """Job en estado queued puede cancelarse."""
        job_id = str(uuid4())
        await store_inmemory.create(job_id=job_id, message="test")

        result = await store_inmemory.request_cancel(job_id)
        assert result is True

        is_cancel = await store_inmemory.is_cancel_requested(job_id)
        assert is_cancel is True

    @pytest.mark.asyncio
    async def test_cancel_running_job(self, store_inmemory):
        """Job en estado running puede cancelarse."""
        job_id = str(uuid4())
        await store_inmemory.create(job_id=job_id, message="test")
        await store_inmemory.set_running(job_id)

        result = await store_inmemory.request_cancel(job_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_cancel_completed_job_fails(self, store_inmemory):
        """Job completado no puede cancelarse."""
        job_id = str(uuid4())
        await store_inmemory.create(job_id=job_id, message="test")
        await store_inmemory.set_running(job_id)
        await store_inmemory.set_completed(
            job_id,
            {"status": "completed", "response": "ok", "tokens_in": 0, "tokens_out": 0, "cost_usd": 0, "latency_ms": 0},
        )

        result = await store_inmemory.request_cancel(job_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_job_fails(self, store_inmemory):
        """Job inexistente no puede cancelarse."""
        result = await store_inmemory.request_cancel("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_set_cancelled_status(self, store_inmemory):
        """set_cancelled marca el job como cancelled."""
        job_id = str(uuid4())
        await store_inmemory.create(job_id=job_id, message="test")
        await store_inmemory.set_cancelled(job_id)

        job = await store_inmemory.get(job_id)
        assert job["status"] == "cancelled"
        assert job["cancelled_at"] is not None


# ── Transiciones de estado ────────────────────────────────────────────


class TestTransicionesEstado:
    """Ciclo de vida completo de un job."""

    @pytest.mark.asyncio
    async def test_full_lifecycle_success(self, store_inmemory):
        """queued → running → completed."""
        job_id = str(uuid4())
        await store_inmemory.create(job_id=job_id, message="lifecycle test")

        job = await store_inmemory.get(job_id)
        assert job["status"] == "queued"

        await store_inmemory.set_running(job_id)
        job = await store_inmemory.get(job_id)
        assert job["status"] == "running"
        assert job["started_at"] is not None

        await store_inmemory.set_completed(
            job_id,
            {
                "status": "completed",
                "response": "done",
                "tokens_in": 100,
                "tokens_out": 200,
                "cost_usd": 0.005,
                "latency_ms": 1200,
            },
        )
        job = await store_inmemory.get(job_id)
        assert job["status"] == "completed"
        assert job["completed_at"] is not None
        assert job["result"]["response"] == "done"
        assert job["tokens_in"] == 100
        assert job["cost_usd"] == 0.005

    @pytest.mark.asyncio
    async def test_full_lifecycle_failure(self, store_inmemory):
        """queued → running → failed."""
        job_id = str(uuid4())
        await store_inmemory.create(job_id=job_id, message="failure test")
        await store_inmemory.set_running(job_id)
        await store_inmemory.set_failed(job_id, "Kernel timeout after 300s")

        job = await store_inmemory.get(job_id)
        assert job["status"] == "failed"
        assert "Kernel timeout" in job["error"]
        assert job["completed_at"] is not None
