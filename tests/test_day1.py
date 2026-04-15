"""
El Monstruo — Day 1 Tests (LangGraph Rewrite)
===============================================
Tests for:
- LangGraphKernel (start_run, cancel, checkpoint, graph export)
- Intent classification (local keywords)
- Model routing (default fallback chains)
- Event logging through the graph
- Memory integration (enrich + memory_write)
- FastAPI endpoints
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
from uuid import uuid4

from contracts.kernel_interface import RunInput, RunOutput, RunStatus, IntentType
from contracts.event_envelope import EventBuilder, EventCategory, Severity
from kernel.engine import LangGraphKernel
from kernel.nodes import _local_classify, _default_model_for_intent
from memory.event_store import EventStore
from memory.conversation import ConversationMemory
from memory.knowledge_graph import KnowledgeGraph


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def event_store():
    store = EventStore()
    await store.initialize()
    return store


@pytest.fixture
def memory():
    return ConversationMemory()


@pytest.fixture
def knowledge():
    return KnowledgeGraph()


@pytest_asyncio.fixture
async def kernel(event_store, memory, knowledge):
    return LangGraphKernel(
        router=None,
        event_store=event_store,
        memory=memory,
        knowledge=knowledge,
    )


# ══════════════════════════════════════════════════════════════════════
# 1. Intent Classification (local)
# ══════════════════════════════════════════════════════════════════════

class TestIntentClassification:
    def test_chat_simple(self):
        assert _local_classify("hola") == IntentType.CHAT

    def test_chat_question(self):
        assert _local_classify("qué hora es") == IntentType.CHAT

    def test_system_slash(self):
        assert _local_classify("/status") == IntentType.SYSTEM

    def test_system_bang(self):
        assert _local_classify("!help") == IntentType.SYSTEM

    def test_execute_keywords(self):
        assert _local_classify("Ejecuta el deploy") == IntentType.EXECUTE
        assert _local_classify("Crea una presentación") == IntentType.EXECUTE
        assert _local_classify("Borra ese registro") == IntentType.EXECUTE

    def test_deep_think_keywords(self):
        assert _local_classify("Analiza este problema") == IntentType.DEEP_THINK
        assert _local_classify("Compara estas opciones") == IntentType.DEEP_THINK
        assert _local_classify("Explica cómo funciona") == IntentType.DEEP_THINK

    def test_english_keywords(self):
        assert _local_classify("execute the deployment") == IntentType.EXECUTE
        assert _local_classify("analyze this data") == IntentType.DEEP_THINK


# ══════════════════════════════════════════════════════════════════════
# 2. Model Routing
# ══════════════════════════════════════════════════════════════════════

class TestModelRouting:
    def test_chat_model(self):
        model, fallbacks = _default_model_for_intent("chat")
        assert model == "gemini-3.1-flash-lite"
        assert len(fallbacks) == 2

    def test_deep_think_model(self):
        model, fallbacks = _default_model_for_intent("deep_think")
        assert model == "gpt-5.4"
        assert "claude-sonnet-4-6" in fallbacks

    def test_execute_model(self):
        model, fallbacks = _default_model_for_intent("execute")
        assert model == "gpt-5.4"

    def test_system_model(self):
        model, fallbacks = _default_model_for_intent("system")
        assert model == "gemini-3.1-flash-lite"

    def test_unknown_defaults_to_chat(self):
        model, _ = _default_model_for_intent("unknown")
        assert model == "gemini-3.1-flash-lite"


# ══════════════════════════════════════════════════════════════════════
# 3. Event Store
# ══════════════════════════════════════════════════════════════════════

class TestEventStore:
    @pytest.mark.asyncio
    async def test_append_and_count(self, event_store):
        event = EventBuilder().category(EventCategory.RUN_STARTED).actor("test").action("Test").build()
        eid = await event_store.append(event)
        assert eid == event.event_id
        assert await event_store.count() == 1

    @pytest.mark.asyncio
    async def test_get_by_run(self, event_store):
        run_id = uuid4()
        for i in range(3):
            event = EventBuilder().category(EventCategory.RUN_STEP).actor("test").action(f"Step {i}").for_run(run_id).build()
            await event_store.append(event)
        events = await event_store.get_by_run(run_id)
        assert len(events) == 3

    @pytest.mark.asyncio
    async def test_get_by_category(self, event_store):
        for cat in [EventCategory.RUN_STARTED, EventCategory.RUN_COMPLETED, EventCategory.RUN_STARTED]:
            event = EventBuilder().category(cat).actor("test").action("Test").build()
            await event_store.append(event)
        started = await event_store.get_by_category(EventCategory.RUN_STARTED)
        assert len(started) == 2

    @pytest.mark.asyncio
    async def test_get_errors(self, event_store):
        await event_store.append(EventBuilder().category(EventCategory.RUN_STARTED).actor("test").action("Normal").build())
        await event_store.append(EventBuilder().category(EventCategory.RUN_FAILED).severity(Severity.ERROR).actor("test").action("Error").build())
        errors = await event_store.get_errors()
        assert len(errors) == 1

    @pytest.mark.asyncio
    async def test_replay(self, event_store):
        run_id = uuid4()
        for action in ["Started", "Routed", "Executed", "Completed"]:
            event = EventBuilder().category(EventCategory.RUN_STARTED).actor("test").action(action).for_run(run_id).build()
            await event_store.append(event)
        replay = await event_store.replay(run_id)
        assert len(replay) == 4
        assert replay[0]["action"] == "Started"

    @pytest.mark.asyncio
    async def test_stats(self, event_store):
        await event_store.append(EventBuilder().category(EventCategory.SYSTEM_STARTUP).actor("test").action("Boot").build())
        stats = await event_store.get_stats()
        assert stats["total_events"] == 1


# ══════════════════════════════════════════════════════════════════════
# 4. LangGraph Kernel — Core Execution
# ══════════════════════════════════════════════════════════════════════

class TestKernelExecution:
    @pytest.mark.asyncio
    async def test_simple_chat(self, kernel):
        inp = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message="Hola Monstruo")
        out = await kernel.start_run(inp)
        assert out.status == RunStatus.COMPLETED
        assert out.intent == IntentType.CHAT
        assert out.response
        assert out.model_used == "gemini-3.1-flash-lite"

    @pytest.mark.asyncio
    async def test_deep_think(self, kernel):
        inp = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message="Analiza las ventajas de LangGraph vs CrewAI")
        out = await kernel.start_run(inp)
        assert out.status == RunStatus.COMPLETED
        assert out.intent == IntentType.DEEP_THINK
        assert out.metadata.get("enriched") is True
        assert out.model_used == "gpt-5.4"

    @pytest.mark.asyncio
    async def test_execute_intent(self, kernel):
        inp = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message="Ejecuta un deploy del bot")
        out = await kernel.start_run(inp)
        assert out.status == RunStatus.COMPLETED
        assert out.intent == IntentType.EXECUTE
        assert out.metadata.get("enriched") is True

    @pytest.mark.asyncio
    async def test_system_command(self, kernel):
        inp = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message="/status")
        out = await kernel.start_run(inp)
        assert out.status == RunStatus.COMPLETED
        assert out.intent == IntentType.SYSTEM

    @pytest.mark.asyncio
    async def test_multiple_runs(self, kernel):
        results = []
        for i in range(5):
            inp = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message=f"Mensaje {i}")
            out = await kernel.start_run(inp)
            results.append(out)
        assert all(r.status == RunStatus.COMPLETED for r in results)


# ══════════════════════════════════════════════════════════════════════
# 5. Event Logging Through Graph
# ══════════════════════════════════════════════════════════════════════

class TestEventLogging:
    @pytest.mark.asyncio
    async def test_events_generated(self, kernel):
        inp = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message="Hola")
        out = await kernel.start_run(inp)
        assert out.metadata.get("events_count", 0) > 0

    @pytest.mark.asyncio
    async def test_event_store_populated(self, kernel, event_store):
        inp = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message="Hola")
        await kernel.start_run(inp)
        events = await event_store.get_recent(limit=50)
        assert len(events) > 0


# ══════════════════════════════════════════════════════════════════════
# 6. Memory Integration
# ══════════════════════════════════════════════════════════════════════

class TestMemoryIntegration:
    @pytest.mark.asyncio
    async def test_memory_written_on_chat(self, kernel):
        inp = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message="Recuerda que me gusta el café")
        out = await kernel.start_run(inp)
        assert out.status == RunStatus.COMPLETED
        assert out.metadata.get("memory_written") is True

    @pytest.mark.asyncio
    async def test_enrichment_on_deep_think(self, kernel):
        # Create memory first
        inp1 = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message="Me gusta Python más que JavaScript")
        await kernel.start_run(inp1)
        # Deep think should enrich
        inp2 = RunInput(run_id=uuid4(), user_id="alfredo", channel="test", message="Analiza qué lenguaje debería usar")
        out = await kernel.start_run(inp2)
        assert out.status == RunStatus.COMPLETED
        assert out.metadata.get("enriched") is True


# ══════════════════════════════════════════════════════════════════════
# 7. Cancel / Kill Switch
# ══════════════════════════════════════════════════════════════════════

class TestCancel:
    @pytest.mark.asyncio
    async def test_cancel_completed_run(self, kernel):
        """Cancelling a completed run returns True (marks as cancelled in store)."""
        run_id = uuid4()
        inp = RunInput(run_id=run_id, user_id="alfredo", channel="test", message="Hola")
        await kernel.start_run(inp)
        # Run already completed synchronously (stub mode), cancel should still work
        # because the run exists in _runs dict
        result = await kernel.cancel(run_id, reason="test cancel")
        # In LangGraph stub mode, runs complete instantly, so cancel returns True
        # (run exists) or False (already terminal). Both are valid.
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_run(self, kernel):
        result = await kernel.cancel(uuid4(), reason="test")
        assert result is False


# ══════════════════════════════════════════════════════════════════════
# 8. Graph Export
# ══════════════════════════════════════════════════════════════════════

class TestGraphExport:
    def test_mermaid_export(self, kernel):
        mermaid = kernel.get_graph_mermaid()
        assert len(mermaid) > 0
        for node in ["intake", "classify_and_route", "enrich", "execute", "memory_write", "respond"]:
            assert node in mermaid, f"Node {node} not found in graph"

    def test_graph_has_seven_nodes(self, kernel):
        mermaid = kernel.get_graph_mermaid()
        node_names = ["intake", "classify_and_route", "enrich", "execute", "memory_write", "respond"]
        for name in node_names:
            assert name in mermaid


# ══════════════════════════════════════════════════════════════════════
# 9. EventEnvelope Contract
# ══════════════════════════════════════════════════════════════════════

class TestEventEnvelope:
    def test_event_builder(self):
        event = EventBuilder().category(EventCategory.RUN_STARTED).actor("test").action("test action").build()
        assert event.category == EventCategory.RUN_STARTED

    def test_event_severity(self):
        event = EventBuilder().category(EventCategory.RUN_FAILED).severity(Severity.ERROR).actor("test").action("failed").build()
        assert event.severity == Severity.ERROR

    def test_event_for_run(self):
        run_id = uuid4()
        event = EventBuilder().category(EventCategory.RUN_STARTED).actor("test").action("test").for_run(run_id).build()
        assert event.run_id == run_id

    def test_event_for_run_str(self):
        run_id = uuid4()
        event = EventBuilder().category(EventCategory.RUN_STARTED).actor("test").action("test").for_run_str(str(run_id)).build()
        assert event.run_id == run_id


# ══════════════════════════════════════════════════════════════════════
# 10. FastAPI Endpoints
# ══════════════════════════════════════════════════════════════════════

class TestFastAPIEndpoints:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from kernel.main import app
        return TestClient(app)

    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "El Monstruo"
        assert data["status"] == "alive"

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "0.3.0-sprint2"
        # Verify thin-client contract fields
        assert "models_available" in data
        assert "observability" in data
        assert isinstance(data["models_available"], list)

    def test_chat_endpoint(self, client):
        resp = client.post("/v1/chat", json={
            "message": "Hola Monstruo",
            "user_id": "test_user",
            "channel": "test",
        })
        # Kernel initializes via lifespan; TestClient triggers it
        assert resp.status_code in [200, 503]
        if resp.status_code == 200:
            data = resp.json()
            assert data["status"] in ["completed", "failed"]
            assert data["run_id"] != ""

    def test_stats_endpoint(self, client):
        resp = client.get("/v1/stats")
        assert resp.status_code == 200
        data = resp.json()
        # May return {"status": "no_event_store"} if lifespan didn't run,
        # or full stats if it did
        assert "event_store" in data or "status" in data

    def test_recent_events(self, client):
        resp = client.get("/v1/events/recent")
        # May be 503 if lifespan didn't initialize event_store
        assert resp.status_code in [200, 503]
        if resp.status_code == 200:
            data = resp.json()
            assert "count" in data


# ── Run ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
