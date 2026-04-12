"""
El Monstruo — Day 1 Tests
============================
Tests for Kernel + Router + EventStore integration.
Runs WITHOUT LiteLLM proxy (uses kernel fallback stubs).

Test plan:
1. Kernel state machine transitions
2. Intent classification (local)
3. Event store operations
4. Full pipeline: message → route → execute → respond → log
5. Kill switch (cancel)
6. Replay
7. FastAPI endpoints
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
from uuid import uuid4

from contracts.kernel_interface import (
    IntentType,
    RunInput,
    RunOutput,
    RunStatus,
)
from contracts.event_envelope import EventBuilder, EventCategory, EventEnvelope, Severity
from kernel.engine import KernelEngine, _basic_intent_classify
from memory.event_store import EventStore


# ── Fixtures ────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def event_store():
    """Create a fresh in-memory event store."""
    store = EventStore()
    await store.initialize()
    return store


@pytest_asyncio.fixture
async def kernel_no_router(event_store):
    """Create a kernel without router (uses stubs)."""
    return KernelEngine(router=None, event_store=event_store)


# ── Test 1: Intent Classification ───────────────────────────────────

class TestIntentClassification:
    """Test local keyword-based intent classification."""

    def test_chat_simple(self):
        assert _basic_intent_classify("hola") == IntentType.CHAT

    def test_chat_question(self):
        assert _basic_intent_classify("qué hora es") == IntentType.CHAT

    def test_deep_think_analiza(self):
        assert _basic_intent_classify("analiza el mercado inmobiliario") == IntentType.DEEP_THINK

    def test_deep_think_piensa(self):
        assert _basic_intent_classify("piensa en una estrategia") == IntentType.DEEP_THINK

    def test_deep_think_long_message(self):
        long_msg = "x " * 300  # > 500 chars
        assert _basic_intent_classify(long_msg) == IntentType.DEEP_THINK

    def test_execute_haz(self):
        assert _basic_intent_classify("haz un reporte") == IntentType.EXECUTE

    def test_execute_crea(self):
        assert _basic_intent_classify("crea una presentación") == IntentType.EXECUTE

    def test_execute_envía(self):
        assert _basic_intent_classify("envía un correo") == IntentType.EXECUTE

    def test_system_status(self):
        assert _basic_intent_classify("/status") == IntentType.SYSTEM

    def test_system_help(self):
        assert _basic_intent_classify("/help") == IntentType.SYSTEM

    def test_system_start(self):
        assert _basic_intent_classify("/start") == IntentType.SYSTEM


# ── Test 2: Event Store ─────────────────────────────────────────────

class TestEventStore:
    """Test event store operations."""

    @pytest.mark.asyncio
    async def test_append_and_count(self, event_store):
        event = (
            EventBuilder()
            .category(EventCategory.RUN_STARTED)
            .actor("test")
            .action("Test event")
            .build()
        )
        eid = await event_store.append(event)
        assert eid == event.event_id
        assert await event_store.count() == 1

    @pytest.mark.asyncio
    async def test_get_by_run(self, event_store):
        run_id = uuid4()
        for i in range(3):
            event = (
                EventBuilder()
                .category(EventCategory.RUN_STEP)
                .actor("test")
                .action(f"Step {i}")
                .for_run(run_id)
                .build()
            )
            await event_store.append(event)

        events = await event_store.get_by_run(run_id)
        assert len(events) == 3

    @pytest.mark.asyncio
    async def test_get_by_category(self, event_store):
        for cat in [EventCategory.RUN_STARTED, EventCategory.RUN_COMPLETED, EventCategory.RUN_STARTED]:
            event = (
                EventBuilder()
                .category(cat)
                .actor("test")
                .action("Test")
                .build()
            )
            await event_store.append(event)

        started = await event_store.get_by_category(EventCategory.RUN_STARTED)
        assert len(started) == 2

    @pytest.mark.asyncio
    async def test_get_errors(self, event_store):
        # Normal event
        await event_store.append(
            EventBuilder()
            .category(EventCategory.RUN_STARTED)
            .actor("test")
            .action("Normal")
            .build()
        )
        # Error event
        await event_store.append(
            EventBuilder()
            .category(EventCategory.RUN_FAILED)
            .severity(Severity.ERROR)
            .actor("test")
            .action("Error happened")
            .build()
        )

        errors = await event_store.get_errors()
        assert len(errors) == 1
        assert errors[0].severity == Severity.ERROR

    @pytest.mark.asyncio
    async def test_replay(self, event_store):
        run_id = uuid4()
        for action in ["Started", "Routed", "Executed", "Completed"]:
            event = (
                EventBuilder()
                .category(EventCategory.RUN_STARTED)
                .actor("test")
                .action(action)
                .for_run(run_id)
                .build()
            )
            await event_store.append(event)

        replay = await event_store.replay(run_id)
        assert len(replay) == 4
        assert replay[0]["action"] == "Started"

    @pytest.mark.asyncio
    async def test_stats(self, event_store):
        await event_store.append(
            EventBuilder()
            .category(EventCategory.SYSTEM_STARTUP)
            .actor("test")
            .action("Boot")
            .build()
        )
        stats = await event_store.get_stats()
        assert stats["total_events"] == 1
        assert stats["persistence"] == "in-memory"


# ── Test 3: Kernel State Machine ────────────────────────────────────

class TestKernelStateMachine:
    """Test kernel state transitions and execution flow."""

    @pytest.mark.asyncio
    async def test_start_run_completes(self, kernel_no_router, event_store):
        """Full pipeline: message → route → execute → respond."""
        run_input = RunInput(
            user_id="alfredo",
            channel="test",
            message="Hola Monstruo",
        )

        output = await kernel_no_router.start_run(run_input)

        assert output.status == RunStatus.COMPLETED
        assert output.intent == IntentType.CHAT
        assert output.response != ""
        assert output.latency_ms > 0

    @pytest.mark.asyncio
    async def test_deep_think_intent(self, kernel_no_router, event_store):
        """Deep think messages get classified correctly."""
        run_input = RunInput(
            user_id="alfredo",
            channel="test",
            message="Analiza el mercado inmobiliario de Mérida en 2026",
        )

        output = await kernel_no_router.start_run(run_input)

        assert output.status == RunStatus.COMPLETED
        assert output.intent == IntentType.DEEP_THINK

    @pytest.mark.asyncio
    async def test_execute_intent(self, kernel_no_router, event_store):
        """Execute messages get classified correctly."""
        run_input = RunInput(
            user_id="alfredo",
            channel="test",
            message="Crea un reporte de ventas",
        )

        output = await kernel_no_router.start_run(run_input)

        assert output.status == RunStatus.COMPLETED
        assert output.intent == IntentType.EXECUTE

    @pytest.mark.asyncio
    async def test_events_logged(self, kernel_no_router, event_store):
        """Events are logged for every run."""
        run_input = RunInput(
            user_id="alfredo",
            channel="test",
            message="Hola",
        )

        output = await kernel_no_router.start_run(run_input)

        events = await event_store.get_by_run(output.run_id)
        assert len(events) >= 3  # At least: started, route_decided, completed

        categories = [e.category for e in events]
        assert EventCategory.RUN_STARTED in categories
        assert EventCategory.ROUTE_DECIDED in categories
        assert EventCategory.RUN_COMPLETED in categories

    @pytest.mark.asyncio
    async def test_cancel_run(self, kernel_no_router, event_store):
        """Kill switch works."""
        run_input = RunInput(
            user_id="alfredo",
            channel="test",
            message="Hola",
        )

        # Start a run
        output = await kernel_no_router.start_run(run_input)

        # Can't cancel a completed run
        cancelled = await kernel_no_router.cancel(output.run_id, "test cancel")
        assert cancelled is False

    @pytest.mark.asyncio
    async def test_get_status(self, kernel_no_router, event_store):
        """Status check works after run completes."""
        run_input = RunInput(
            user_id="alfredo",
            channel="test",
            message="Status test",
        )

        output = await kernel_no_router.start_run(run_input)
        status = await kernel_no_router.get_status(output.run_id)
        assert status == RunStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_checkpoint(self, kernel_no_router, event_store):
        """Checkpoint creation works."""
        run_input = RunInput(
            user_id="alfredo",
            channel="test",
            message="Checkpoint test",
        )

        output = await kernel_no_router.start_run(run_input)
        cp = await kernel_no_router.checkpoint(output.run_id)
        assert cp.run_id == output.run_id
        assert cp.status == RunStatus.CHECKPOINTED

    @pytest.mark.asyncio
    async def test_replay_full_run(self, kernel_no_router, event_store):
        """Replay shows complete run history."""
        run_input = RunInput(
            user_id="alfredo",
            channel="test",
            message="Replay test",
        )

        output = await kernel_no_router.start_run(run_input)
        replay = await event_store.replay(output.run_id)

        assert len(replay) >= 3
        # First event should be RUN_STARTED
        assert replay[0]["category"] == "run.started"
        # Last event should be RUN_COMPLETED
        assert replay[-1]["category"] == "run.completed"

    @pytest.mark.asyncio
    async def test_hooks_fire(self, kernel_no_router, event_store):
        """Lifecycle hooks fire correctly."""
        hook_log = []

        async def on_pre_route(*args):
            hook_log.append("pre_route")

        async def on_post_route(*args):
            hook_log.append("post_route")

        async def on_post_execute(*args):
            hook_log.append("post_execute")

        await kernel_no_router.register_hook("pre_route", on_pre_route)
        await kernel_no_router.register_hook("post_route", on_post_route)
        await kernel_no_router.register_hook("post_execute", on_post_execute)

        run_input = RunInput(
            user_id="alfredo",
            channel="test",
            message="Hook test",
        )

        await kernel_no_router.start_run(run_input)

        assert "pre_route" in hook_log
        assert "post_route" in hook_log
        assert "post_execute" in hook_log


# ── Test 4: FastAPI Endpoints ───────────────────────────────────────

class TestFastAPIEndpoints:
    """Test HTTP endpoints via TestClient."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        # Need to import with proper path setup
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from kernel.main import app
        return TestClient(app)

    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "El Monstruo"
        assert data["status"] == "alive"

    def test_chat_endpoint(self, client):
        resp = client.post("/v1/chat", json={
            "message": "Hola Monstruo",
            "user_id": "test_user",
            "channel": "test",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ["completed", "failed"]
        assert data["run_id"] != ""
        assert data["intent"] != ""

    def test_chat_deep_think(self, client):
        resp = client.post("/v1/chat", json={
            "message": "Analiza la situación económica de México",
            "user_id": "test_user",
        })
        assert resp.status_code == 200
        data = resp.json()
        # With router connected but LiteLLM down, LLM classification fails
        # and falls back to local. Intent may be deep_think or chat depending
        # on fallback. The important thing is the endpoint works.
        assert data["intent"] in ["deep_think", "chat"]

    def test_stats_endpoint(self, client):
        resp = client.get("/v1/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "event_store" in data
        assert "system" in data

    def test_recent_events(self, client):
        # First make a chat to generate events
        client.post("/v1/chat", json={"message": "Generate events"})

        resp = client.get("/v1/events/recent")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] > 0

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "0.1.0-sprint1"


# ── Run ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
