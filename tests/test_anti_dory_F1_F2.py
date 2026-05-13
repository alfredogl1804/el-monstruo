"""
Tests Anti-Dory F1 + F2 (Sprint 2026-05-12)
============================================
Verifica que:

F1: ConversationMemory._search_semantic_supabase() YA NO es stub.
    - Cuando hay db conectada, llama a RPC `match_memory_events`.
    - Hace fallback DEFENSIVO al local cosine si la RPC falla.
    - Devuelve SearchResult con source="vector".

F2: SovereignCheckpointStore se instancia en kernel/main.py lifespan.
    - Verificación estática del wiring (import + instancia + app.state).

Estos tests usan mocks para no depender de Supabase real en CI; la
verificación binaria contra la RPC real ya se hizo vía
`python3 ~/.monstruo/sb_sql.py sql -q "SELECT * FROM match_memory_events(...)"`.
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from contracts.memory_interface import MemoryEvent, MemoryType, SearchResult
from memory.conversation import ConversationMemory

# ── F1: RPC pgvector real ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_f1_search_semantic_supabase_uses_rpc_when_db_connected():
    """Cuando la db está conectada, debe llamar a la RPC match_memory_events."""
    fake_db = MagicMock()
    fake_db.connected = True
    fake_db.rpc = AsyncMock(
        return_value=[
            {
                "event_id": str(uuid4()),
                "memory_type": "episodic",
                "run_id": None,
                "user_id": "alfredo",
                "channel": "telegram",
                "content": "hola monstruo",
                "metadata": {"src": "test"},
                "created_at": "2026-05-12T00:00:00Z",
                "score": 0.91,
            }
        ]
    )

    mem = ConversationMemory(db=fake_db)

    results = await mem._search_semantic_supabase(
        query_embedding=[0.1] * 1536,
        user_id="alfredo",
        memory_types=[MemoryType.EPISODIC],
        limit=5,
        threshold=0.7,
    )

    fake_db.rpc.assert_awaited_once()
    args, kwargs = fake_db.rpc.call_args
    assert args[0] == "match_memory_events"
    params = args[1]
    assert params["match_threshold"] == 0.7
    assert params["match_count"] == 5
    assert params["p_user_id"] == "alfredo"
    assert params["p_memory_types"] == ["episodic"]
    assert len(params["query_embedding"]) == 1536

    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert results[0].source == "vector"
    assert results[0].score == pytest.approx(0.91)
    assert results[0].event.user_id == "alfredo"


@pytest.mark.asyncio
async def test_f1_search_semantic_supabase_falls_back_on_rpc_failure():
    """Si la RPC lanza excepción, debe caer al búsqueda local in-memory (cero crash)."""
    fake_db = MagicMock()
    fake_db.connected = True
    fake_db.rpc = AsyncMock(side_effect=RuntimeError("rls denied / rpc missing"))

    mem = ConversationMemory(db=fake_db)
    # Sembrar un evento local con embedding para que el fallback tenga algo
    ev = MemoryEvent(
        event_id=uuid4(),
        memory_type=MemoryType.EPISODIC,
        user_id="alfredo",
        content="texto seed",
        embedding=[0.1] * 1536,
    )
    mem._events.append(ev)
    mem._by_user["alfredo"].append(ev)

    results = await mem._search_semantic_supabase(
        query_embedding=[0.1] * 1536,
        user_id="alfredo",
        memory_types=None,
        limit=5,
        threshold=0.0,
    )

    fake_db.rpc.assert_awaited_once()
    # Fallback debió correr y devolver el evento local
    assert len(results) == 1
    assert results[0].event.event_id == ev.event_id


@pytest.mark.asyncio
async def test_f1_search_semantic_supabase_handles_none_response():
    """Si la RPC devuelve None, también debe caer al fallback local sin crash."""
    fake_db = MagicMock()
    fake_db.connected = True
    fake_db.rpc = AsyncMock(return_value=None)

    mem = ConversationMemory(db=fake_db)
    results = await mem._search_semantic_supabase(
        query_embedding=[0.1] * 1536,
        user_id=None,
        memory_types=None,
        limit=10,
        threshold=0.7,
    )
    fake_db.rpc.assert_awaited_once()
    assert results == []  # no hay eventos locales sembrados → lista vacía


# ── F2: Wiring estático de SovereignCheckpointStore ─────────────────


def test_f2_checkpoint_store_imported_in_kernel_main():
    """Verifica que el import existe en kernel/main.py."""
    src = Path(__file__).resolve().parents[1] / "kernel" / "main.py"
    code = src.read_text(encoding="utf-8")
    assert "from memory.checkpoint_store import SovereignCheckpointStore" in code


def test_f2_checkpoint_store_instantiated_in_lifespan():
    """Verifica que se instancia con db y se llama initialize() en lifespan."""
    src = Path(__file__).resolve().parents[1] / "kernel" / "main.py"
    code = src.read_text(encoding="utf-8")
    assert "checkpoint_store = SovereignCheckpointStore(db=db if db_connected else None)" in code
    assert "await checkpoint_store.initialize()" in code


def test_f2_checkpoint_store_exposed_in_app_state():
    """Verifica que se expone en app.state.checkpoint_store para que rutas puedan usarlo."""
    src = Path(__file__).resolve().parents[1] / "kernel" / "main.py"
    code = src.read_text(encoding="utf-8")
    assert "app.state.checkpoint_store = checkpoint_store" in code


def test_f2_checkpoint_store_in_health_endpoint():
    """Verifica que /health reporta el estado del checkpoint_store."""
    src = Path(__file__).resolve().parents[1] / "kernel" / "main.py"
    code = src.read_text(encoding="utf-8")
    # Patrón directo: clave checkpoint_store presente en components
    assert re.search(r'"checkpoint_store"\s*:\s*\(?\s*await\s+checkpoint_store\.get_stats\(\)', code)


def test_f2_global_declaration_includes_checkpoint_store():
    """El global de lifespan debe incluir checkpoint_store para evitar shadowing."""
    src = Path(__file__).resolve().parents[1] / "kernel" / "main.py"
    code = src.read_text(encoding="utf-8")
    pattern = (
        r"global\s+kernel,\s+event_store,\s+conversation_memory,\s+"
        r"knowledge_graph,\s+checkpoint_store,\s+observability"
    )
    assert re.search(pattern, code)


# ── F1+F2: Verificación de migración SQL ──────────────────────────


def test_f1_migration_0028_exists_and_creates_rpc():
    """La migración 0028 debe existir y crear la RPC con SECURITY INVOKER + grant a service_role."""
    src = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "sql"
        / "0028_rpc_match_memory_events.sql"
    )
    assert src.exists(), "Migración 0028 no existe"
    sql = src.read_text(encoding="utf-8")
    assert "CREATE OR REPLACE FUNCTION public.match_memory_events" in sql
    assert "vector(1536)" in sql
    assert "SECURITY INVOKER" in sql
    grant_a = "GRANT  EXECUTE ON FUNCTION public.match_memory_events"
    grant_b = "GRANT EXECUTE ON FUNCTION public.match_memory_events"
    assert grant_a in sql or grant_b in sql
    assert "USING hnsw (embedding vector_cosine_ops)" in sql
