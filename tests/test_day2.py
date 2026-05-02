"""
El Monstruo — Day 2 Tests
============================
Tests for:
- ConversationMemory (episodes, context, search, replay)
- SovereignCheckpointStore (save/load/cleanup/system state)
- KnowledgeGraph (entities, relations, traversal, path finding)
- SupabaseClient (connection handling)
- Integration: Memory + Checkpoint + Graph working together
"""

import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def supabase_client():
    """In-memory only (no Supabase connection)."""
    from memory.supabase_client import SupabaseClient

    client = SupabaseClient(url="", key="")
    return client


@pytest.fixture
def conversation_memory():
    """ConversationMemory without persistence."""
    from memory.conversation import ConversationMemory

    return ConversationMemory(db=None)


@pytest.fixture
def checkpoint_store():
    """CheckpointStore without persistence."""
    from memory.checkpoint_store import SovereignCheckpointStore

    return SovereignCheckpointStore(db=None)


@pytest.fixture
def knowledge_graph():
    """KnowledgeGraph without persistence."""
    from memory.knowledge_graph import KnowledgeGraph

    return KnowledgeGraph(db=None)


def make_memory_event(**kwargs):
    """Helper to create MemoryEvent."""
    from contracts.memory_interface import MemoryEvent, MemoryType

    defaults = {
        "event_id": uuid4(),
        "memory_type": MemoryType.EPISODIC,
        "run_id": uuid4(),
        "user_id": "alfredo",
        "channel": "telegram",
        "content": "Test message",
        "metadata": {"role": "user"},
    }
    defaults.update(kwargs)
    return MemoryEvent(**defaults)


def make_entity(**kwargs):
    """Helper to create Entity."""
    from contracts.memory_interface import Entity, EntityType

    defaults = {
        "entity_id": uuid4(),
        "entity_type": EntityType.PERSON,
        "name": "Alfredo",
        "attributes": {"role": "CEO"},
    }
    defaults.update(kwargs)
    return Entity(**defaults)


def make_relation(source_id, target_id, **kwargs):
    """Helper to create Relation."""
    from contracts.memory_interface import Relation

    defaults = {
        "relation_id": uuid4(),
        "source_id": source_id,
        "target_id": target_id,
        "relation_type": "works_at",
        "weight": 1.0,
    }
    defaults.update(kwargs)
    return Relation(**defaults)


# ══════════════════════════════════════════════════════════════════
# CONVERSATION MEMORY TESTS
# ══════════════════════════════════════════════════════════════════


class TestConversationMemory:
    """Tests for ConversationMemory."""

    def test_append_event(self, conversation_memory):
        """Should append a memory event."""
        event = make_memory_event(content="Hola Monstruo")
        eid = asyncio.new_event_loop().run_until_complete(conversation_memory.append(event))
        assert eid == event.event_id

    def test_append_indexes_by_user(self, conversation_memory):
        """Should index events by user."""
        loop = asyncio.new_event_loop()
        e1 = make_memory_event(user_id="alfredo", content="msg1")
        e2 = make_memory_event(user_id="alfredo", content="msg2")
        e3 = make_memory_event(user_id="otro", content="msg3")

        loop.run_until_complete(conversation_memory.append(e1))
        loop.run_until_complete(conversation_memory.append(e2))
        loop.run_until_complete(conversation_memory.append(e3))

        count_alfredo = loop.run_until_complete(conversation_memory.get_event_count(user_id="alfredo"))
        count_otro = loop.run_until_complete(conversation_memory.get_event_count(user_id="otro"))
        assert count_alfredo == 2
        assert count_otro == 1

    def test_append_indexes_by_type(self, conversation_memory):
        """Should index events by memory type."""
        from contracts.memory_interface import MemoryType

        loop = asyncio.new_event_loop()

        e1 = make_memory_event(memory_type=MemoryType.EPISODIC)
        e2 = make_memory_event(memory_type=MemoryType.SEMANTIC)
        e3 = make_memory_event(memory_type=MemoryType.EPISODIC)

        loop.run_until_complete(conversation_memory.append(e1))
        loop.run_until_complete(conversation_memory.append(e2))
        loop.run_until_complete(conversation_memory.append(e3))

        count_ep = loop.run_until_complete(conversation_memory.get_event_count(memory_type=MemoryType.EPISODIC))
        count_sem = loop.run_until_complete(conversation_memory.get_event_count(memory_type=MemoryType.SEMANTIC))
        assert count_ep == 2
        assert count_sem == 1

    def test_append_batch(self, conversation_memory):
        """Should append multiple events."""
        loop = asyncio.new_event_loop()
        events = [make_memory_event(content=f"msg{i}") for i in range(5)]
        ids = loop.run_until_complete(conversation_memory.append_batch(events))
        assert len(ids) == 5

    def test_keyword_search(self, conversation_memory):
        """Should find events by keyword."""
        loop = asyncio.new_event_loop()

        loop.run_until_complete(conversation_memory.append(make_memory_event(content="El Monstruo es soberano")))
        loop.run_until_complete(conversation_memory.append(make_memory_event(content="La memoria es persistente")))
        loop.run_until_complete(conversation_memory.append(make_memory_event(content="El kernel es soberano también")))

        results = loop.run_until_complete(conversation_memory.search_keyword("soberano"))
        assert len(results) == 2
        assert all(r.source == "keyword" for r in results)

    def test_keyword_search_with_user_filter(self, conversation_memory):
        """Should filter search by user."""
        loop = asyncio.new_event_loop()

        loop.run_until_complete(
            conversation_memory.append(make_memory_event(user_id="alfredo", content="soberano alfredo"))
        )
        loop.run_until_complete(conversation_memory.append(make_memory_event(user_id="otro", content="soberano otro")))

        results = loop.run_until_complete(conversation_memory.search_keyword("soberano", user_id="alfredo"))
        assert len(results) == 1

    def test_episode_lifecycle(self, conversation_memory):
        """Should start and end episodes."""
        loop = asyncio.new_event_loop()

        # Start episode
        episode = loop.run_until_complete(conversation_memory.start_episode("alfredo", "telegram"))
        assert episode.user_id == "alfredo"
        assert episode.channel == "telegram"
        assert episode.ended_at is None

        # Add events to episode
        event = make_memory_event(user_id="alfredo", content="Hola")
        loop.run_until_complete(conversation_memory.add_to_episode(episode.episode_id, event))

        # End episode
        ended = loop.run_until_complete(
            conversation_memory.end_episode(episode.episode_id, summary="Test conversation")
        )
        assert ended.ended_at is not None
        assert ended.summary == "Test conversation"
        assert len(ended.events) == 1

    def test_recent_episodes(self, conversation_memory):
        """Should return recent episodes for a user."""
        loop = asyncio.new_event_loop()

        for i in range(3):
            loop.run_until_complete(conversation_memory.start_episode("alfredo", f"channel_{i}"))

        episodes = loop.run_until_complete(conversation_memory.get_recent_episodes("alfredo", limit=2))
        assert len(episodes) == 2

    def test_replay_by_run(self, conversation_memory):
        """Should replay events for a specific run."""
        loop = asyncio.new_event_loop()
        run_id = uuid4()

        events = [make_memory_event(run_id=run_id, content=f"step {i}") for i in range(3)]
        loop.run_until_complete(conversation_memory.append_batch(events))

        replayed = loop.run_until_complete(conversation_memory.replay(run_id))
        assert len(replayed) == 3

    def test_conversation_context(self, conversation_memory):
        """Should build conversation context for LLM calls."""
        from contracts.memory_interface import MemoryType

        loop = asyncio.new_event_loop()

        # Add user message
        loop.run_until_complete(
            conversation_memory.append(
                make_memory_event(
                    user_id="alfredo",
                    channel="telegram",
                    content="Hola Monstruo",
                    memory_type=MemoryType.EPISODIC,
                    metadata={"role": "user"},
                )
            )
        )
        # Add assistant response
        loop.run_until_complete(
            conversation_memory.append(
                make_memory_event(
                    user_id="alfredo",
                    channel="telegram",
                    content="Hola Alfredo, soy El Monstruo",
                    memory_type=MemoryType.EPISODIC,
                    metadata={"role": "assistant"},
                )
            )
        )

        context = loop.run_until_complete(conversation_memory.get_conversation_context("alfredo", "telegram"))
        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[1]["role"] == "assistant"

    def test_user_summary(self, conversation_memory):
        """Should return user summary."""
        loop = asyncio.new_event_loop()

        loop.run_until_complete(conversation_memory.append(make_memory_event(user_id="alfredo", content="msg1")))
        loop.run_until_complete(conversation_memory.append(make_memory_event(user_id="alfredo", content="msg2")))

        summary = loop.run_until_complete(conversation_memory.get_user_summary("alfredo"))
        assert summary["user_id"] == "alfredo"
        assert summary["total_events"] == 2

    def test_stats(self, conversation_memory):
        """Should return memory statistics."""
        loop = asyncio.new_event_loop()

        loop.run_until_complete(conversation_memory.append(make_memory_event(content="test")))

        stats = loop.run_until_complete(conversation_memory.get_stats())
        assert stats["total_events"] == 1
        assert stats["persistence"] == "in-memory"


# ══════════════════════════════════════════════════════════════════
# CHECKPOINT STORE TESTS
# ══════════════════════════════════════════════════════════════════


class TestCheckpointStore:
    """Tests for SovereignCheckpointStore."""

    def test_save_and_load(self, checkpoint_store):
        """Should save and load a checkpoint."""
        from contracts.checkpoint_model import CheckpointData, CheckpointType

        loop = asyncio.new_event_loop()

        cp = CheckpointData(
            checkpoint_type=CheckpointType.AUTO,
            run_id=uuid4(),
            step=3,
            kernel_state={"status": "executing"},
            reason="test checkpoint",
        )

        saved_id = loop.run_until_complete(checkpoint_store.save(cp))
        loaded = loop.run_until_complete(checkpoint_store.load(saved_id))

        assert loaded is not None
        assert loaded.checkpoint_id == cp.checkpoint_id
        assert loaded.step == 3
        assert loaded.kernel_state == {"status": "executing"}

    def test_load_latest(self, checkpoint_store):
        """Should load the most recent checkpoint."""
        from contracts.checkpoint_model import CheckpointData

        loop = asyncio.new_event_loop()

        run_id = uuid4()
        for i in range(3):
            cp = CheckpointData(run_id=run_id, step=i, reason=f"step {i}")
            loop.run_until_complete(checkpoint_store.save(cp))

        latest = loop.run_until_complete(checkpoint_store.load_latest(run_id))
        assert latest is not None
        assert latest.step == 2

    def test_load_latest_global(self, checkpoint_store):
        """Should load the most recent checkpoint globally."""
        from contracts.checkpoint_model import CheckpointData

        loop = asyncio.new_event_loop()

        cp1 = CheckpointData(run_id=uuid4(), step=1, reason="first")
        cp2 = CheckpointData(run_id=uuid4(), step=2, reason="second")
        loop.run_until_complete(checkpoint_store.save(cp1))
        loop.run_until_complete(checkpoint_store.save(cp2))

        latest = loop.run_until_complete(checkpoint_store.load_latest())
        assert latest is not None
        assert latest.step == 2

    def test_list_checkpoints(self, checkpoint_store):
        """Should list checkpoints with filters."""
        from contracts.checkpoint_model import CheckpointData, CheckpointType

        loop = asyncio.new_event_loop()

        run_id = uuid4()
        loop.run_until_complete(
            checkpoint_store.save(CheckpointData(run_id=run_id, checkpoint_type=CheckpointType.AUTO))
        )
        loop.run_until_complete(
            checkpoint_store.save(CheckpointData(run_id=run_id, checkpoint_type=CheckpointType.MANUAL))
        )
        loop.run_until_complete(
            checkpoint_store.save(CheckpointData(run_id=uuid4(), checkpoint_type=CheckpointType.AUTO))
        )

        # Filter by run
        by_run = loop.run_until_complete(checkpoint_store.list_checkpoints(run_id=run_id))
        assert len(by_run) == 2

        # Filter by type
        by_type = loop.run_until_complete(checkpoint_store.list_checkpoints(checkpoint_type=CheckpointType.AUTO))
        assert len(by_type) == 2

    def test_delete_checkpoint(self, checkpoint_store):
        """Should delete a checkpoint."""
        from contracts.checkpoint_model import CheckpointData

        loop = asyncio.new_event_loop()

        cp = CheckpointData(reason="to delete")
        loop.run_until_complete(checkpoint_store.save(cp))

        deleted = loop.run_until_complete(checkpoint_store.delete(cp.checkpoint_id))
        assert deleted is True

        loaded = loop.run_until_complete(checkpoint_store.load(cp.checkpoint_id))
        assert loaded is None

    def test_cleanup_expired(self, checkpoint_store):
        """Should clean up expired checkpoints."""
        from contracts.checkpoint_model import CheckpointData

        loop = asyncio.new_event_loop()

        # Create an expired checkpoint (TTL = 0 hours)
        expired_cp = CheckpointData(
            ttl_hours=0,
            reason="expired",
            created_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        # Create a valid checkpoint
        valid_cp = CheckpointData(ttl_hours=168, reason="valid")

        loop.run_until_complete(checkpoint_store.save(expired_cp))
        loop.run_until_complete(checkpoint_store.save(valid_cp))

        cleaned = loop.run_until_complete(checkpoint_store.cleanup_expired())
        assert cleaned == 1

        # Valid one should still exist
        loaded = loop.run_until_complete(checkpoint_store.load(valid_cp.checkpoint_id))
        assert loaded is not None

    def test_system_state(self, checkpoint_store):
        """Should save and retrieve system state."""
        from contracts.checkpoint_model import SystemHealth, SystemState

        loop = asyncio.new_event_loop()

        state = SystemState(
            health=SystemHealth.HEALTHY,
            active_runs=3,
            total_runs_today=42,
            total_cost_today_usd=1.23,
            models_available=["gpt-5.5", "claude-sonnet"],
        )

        loop.run_until_complete(checkpoint_store.save_system_state(state))
        retrieved = loop.run_until_complete(checkpoint_store.get_system_state())

        assert retrieved.health == SystemHealth.HEALTHY
        assert retrieved.active_runs == 3
        assert retrieved.total_runs_today == 42

    def test_system_health_shortcut(self, checkpoint_store):
        """Should return just the health status."""
        from contracts.checkpoint_model import SystemHealth, SystemState

        loop = asyncio.new_event_loop()

        state = SystemState(health=SystemHealth.DEGRADED)
        loop.run_until_complete(checkpoint_store.save_system_state(state))

        health = loop.run_until_complete(checkpoint_store.get_system_health())
        assert health == SystemHealth.DEGRADED

    def test_stats(self, checkpoint_store):
        """Should return checkpoint store stats."""
        from contracts.checkpoint_model import CheckpointData

        loop = asyncio.new_event_loop()

        loop.run_until_complete(checkpoint_store.save(CheckpointData(reason="test")))
        stats = loop.run_until_complete(checkpoint_store.get_stats())

        assert stats["total_checkpoints"] == 1
        assert stats["persistence"] == "in-memory"


# ══════════════════════════════════════════════════════════════════
# KNOWLEDGE GRAPH TESTS
# ══════════════════════════════════════════════════════════════════


class TestKnowledgeGraph:
    """Tests for KnowledgeGraph."""

    def test_create_entity(self, knowledge_graph):
        """Should create an entity."""
        loop = asyncio.new_event_loop()
        entity = make_entity(name="Alfredo", attributes={"role": "CEO"})

        eid = loop.run_until_complete(knowledge_graph.upsert_entity(entity))
        assert eid == entity.entity_id

    def test_upsert_merges_attributes(self, knowledge_graph):
        """Should merge attributes on upsert."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="Alfredo", attributes={"role": "CEO"})
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))

        e2 = make_entity(name="Alfredo", attributes={"company": "Hive"})
        eid = loop.run_until_complete(knowledge_graph.upsert_entity(e2))

        # Should return the original ID (merged)
        assert eid == e1.entity_id

        # Check merged attributes
        entity = loop.run_until_complete(knowledge_graph.get_entity(eid))
        assert entity.attributes["role"] == "CEO"
        assert entity.attributes["company"] == "Hive"

    def test_find_entities_by_name(self, knowledge_graph):
        """Should find entities by name."""
        loop = asyncio.new_event_loop()

        loop.run_until_complete(knowledge_graph.upsert_entity(make_entity(name="Alfredo Gongora")))
        loop.run_until_complete(knowledge_graph.upsert_entity(make_entity(name="Hive Business Center")))

        results = loop.run_until_complete(knowledge_graph.find_entities("Alfredo"))
        assert len(results) >= 1
        assert results[0].name == "Alfredo Gongora"

    def test_find_entities_by_type(self, knowledge_graph):
        """Should filter entities by type."""
        from contracts.memory_interface import EntityType

        loop = asyncio.new_event_loop()

        loop.run_until_complete(
            knowledge_graph.upsert_entity(make_entity(name="Alfredo", entity_type=EntityType.PERSON))
        )
        loop.run_until_complete(
            knowledge_graph.upsert_entity(make_entity(name="Hive", entity_type=EntityType.ORGANIZATION))
        )

        results = loop.run_until_complete(knowledge_graph.find_entities("", entity_type=EntityType.PERSON))
        # Should find Alfredo but not Hive
        person_names = [r.name for r in results]
        assert "Alfredo" in person_names

    def test_add_relation(self, knowledge_graph):
        """Should add a relation between entities."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="Alfredo")
        e2 = make_entity(name="Hive")
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))
        loop.run_until_complete(knowledge_graph.upsert_entity(e2))

        relation = make_relation(e1.entity_id, e2.entity_id, relation_type="owns")
        rid = loop.run_until_complete(knowledge_graph.add_relation(relation))
        assert rid == relation.relation_id

    def test_get_relations(self, knowledge_graph):
        """Should get relations for an entity."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="Alfredo")
        e2 = make_entity(name="Hive")
        e3 = make_entity(name="CIP")
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))
        loop.run_until_complete(knowledge_graph.upsert_entity(e2))
        loop.run_until_complete(knowledge_graph.upsert_entity(e3))

        loop.run_until_complete(
            knowledge_graph.add_relation(make_relation(e1.entity_id, e2.entity_id, relation_type="owns"))
        )
        loop.run_until_complete(
            knowledge_graph.add_relation(make_relation(e1.entity_id, e3.entity_id, relation_type="founded"))
        )

        relations = loop.run_until_complete(knowledge_graph.get_relations(e1.entity_id))
        assert len(relations) == 2

    def test_invalidate_relation(self, knowledge_graph):
        """Should mark a relation as no longer valid."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="Alfredo")
        e2 = make_entity(name="OldCompany")
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))
        loop.run_until_complete(knowledge_graph.upsert_entity(e2))

        relation = make_relation(e1.entity_id, e2.entity_id, relation_type="works_at")
        loop.run_until_complete(knowledge_graph.add_relation(relation))

        # Invalidate
        result = loop.run_until_complete(knowledge_graph.invalidate_relation(relation.relation_id))
        assert result is True

        # Should no longer appear in valid relations
        relations = loop.run_until_complete(knowledge_graph.get_relations(e1.entity_id))
        assert len(relations) == 0

    def test_graph_traversal_depth_1(self, knowledge_graph):
        """Should traverse graph at depth 1."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="Alfredo")
        e2 = make_entity(name="Hive")
        e3 = make_entity(name="CIP")
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))
        loop.run_until_complete(knowledge_graph.upsert_entity(e2))
        loop.run_until_complete(knowledge_graph.upsert_entity(e3))

        loop.run_until_complete(knowledge_graph.add_relation(make_relation(e1.entity_id, e2.entity_id)))
        loop.run_until_complete(knowledge_graph.add_relation(make_relation(e2.entity_id, e3.entity_id)))

        entities, relations = loop.run_until_complete(knowledge_graph.get_entity_graph(e1.entity_id, depth=1))
        # Depth 1: Alfredo + Hive (direct), NOT CIP
        entity_names = {e.name for e in entities}
        assert "Alfredo" in entity_names
        assert "Hive" in entity_names
        assert "CIP" not in entity_names

    def test_graph_traversal_depth_2(self, knowledge_graph):
        """Should traverse graph at depth 2."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="Alfredo")
        e2 = make_entity(name="Hive")
        e3 = make_entity(name="CIP")
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))
        loop.run_until_complete(knowledge_graph.upsert_entity(e2))
        loop.run_until_complete(knowledge_graph.upsert_entity(e3))

        loop.run_until_complete(knowledge_graph.add_relation(make_relation(e1.entity_id, e2.entity_id)))
        loop.run_until_complete(knowledge_graph.add_relation(make_relation(e2.entity_id, e3.entity_id)))

        entities, relations = loop.run_until_complete(knowledge_graph.get_entity_graph(e1.entity_id, depth=2))
        # Depth 2: Alfredo + Hive + CIP
        entity_names = {e.name for e in entities}
        assert "Alfredo" in entity_names
        assert "Hive" in entity_names
        assert "CIP" in entity_names

    def test_shortest_path(self, knowledge_graph):
        """Should find shortest path between entities."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="A")
        e2 = make_entity(name="B")
        e3 = make_entity(name="C")
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))
        loop.run_until_complete(knowledge_graph.upsert_entity(e2))
        loop.run_until_complete(knowledge_graph.upsert_entity(e3))

        loop.run_until_complete(knowledge_graph.add_relation(make_relation(e1.entity_id, e2.entity_id)))
        loop.run_until_complete(knowledge_graph.add_relation(make_relation(e2.entity_id, e3.entity_id)))

        path = loop.run_until_complete(knowledge_graph.get_shortest_path(e1.entity_id, e3.entity_id))
        assert path is not None
        assert len(path) == 3
        assert path[0] == e1.entity_id
        assert path[-1] == e3.entity_id

    def test_no_path_returns_none(self, knowledge_graph):
        """Should return None when no path exists."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="Isolated1")
        e2 = make_entity(name="Isolated2")
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))
        loop.run_until_complete(knowledge_graph.upsert_entity(e2))

        path = loop.run_until_complete(knowledge_graph.get_shortest_path(e1.entity_id, e2.entity_id))
        assert path is None

    def test_relation_validation(self, knowledge_graph):
        """Should reject relations with non-existent entities."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="Exists")
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))

        relation = make_relation(e1.entity_id, uuid4(), relation_type="invalid")
        with pytest.raises(ValueError):
            loop.run_until_complete(knowledge_graph.add_relation(relation))

    def test_stats(self, knowledge_graph):
        """Should return graph statistics."""
        loop = asyncio.new_event_loop()

        e1 = make_entity(name="A")
        e2 = make_entity(name="B")
        loop.run_until_complete(knowledge_graph.upsert_entity(e1))
        loop.run_until_complete(knowledge_graph.upsert_entity(e2))
        loop.run_until_complete(knowledge_graph.add_relation(make_relation(e1.entity_id, e2.entity_id)))

        stats = loop.run_until_complete(knowledge_graph.get_stats())
        assert stats["total_entities"] == 2
        assert stats["total_relations"] == 1


# ══════════════════════════════════════════════════════════════════
# SUPABASE CLIENT TESTS
# ══════════════════════════════════════════════════════════════════


class TestSupabaseClient:
    """Tests for SupabaseClient."""

    def test_not_connected_by_default(self, supabase_client):
        """Should not be connected without credentials."""
        assert supabase_client.connected is False

    def test_insert_returns_none_when_not_connected(self, supabase_client):
        """Should return None for insert when not connected."""
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(supabase_client.insert("test", {"key": "value"}))
        assert result is None

    def test_select_returns_empty_when_not_connected(self, supabase_client):
        """Should return empty list for select when not connected."""
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(supabase_client.select("test"))
        assert result == []

    def test_count_returns_zero_when_not_connected(self, supabase_client):
        """Should return 0 for count when not connected."""
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(supabase_client.count("test"))
        assert result == 0


# ══════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════════


class TestIntegration:
    """Integration tests: Memory + Checkpoint + Graph working together."""

    def test_full_conversation_flow(self, conversation_memory, checkpoint_store, knowledge_graph):
        """Should handle a complete conversation flow."""
        from contracts.checkpoint_model import CheckpointData, CheckpointType
        from contracts.memory_interface import EntityType, MemoryType

        loop = asyncio.new_event_loop()

        # 1. Start episode
        episode = loop.run_until_complete(conversation_memory.start_episode("alfredo", "telegram"))

        # 2. User sends message
        run_id = uuid4()
        user_msg = make_memory_event(
            run_id=run_id,
            user_id="alfredo",
            channel="telegram",
            content="Analiza el mercado inmobiliario de Mérida",
            memory_type=MemoryType.EPISODIC,
            metadata={"role": "user"},
        )
        loop.run_until_complete(conversation_memory.append(user_msg))
        loop.run_until_complete(conversation_memory.add_to_episode(episode.episode_id, user_msg))

        # 3. Create checkpoint before execution
        cp = CheckpointData(
            checkpoint_type=CheckpointType.PRE_TOOL,
            run_id=run_id,
            step=1,
            kernel_state={"status": "executing", "intent": "deep_think"},
            reason="Before market analysis",
        )
        loop.run_until_complete(checkpoint_store.save(cp))

        # 4. Assistant responds
        assistant_msg = make_memory_event(
            run_id=run_id,
            user_id="alfredo",
            channel="telegram",
            content="El mercado inmobiliario de Mérida muestra crecimiento del 15%...",
            memory_type=MemoryType.EPISODIC,
            metadata={"role": "assistant"},
        )
        loop.run_until_complete(conversation_memory.append(assistant_msg))

        # 5. Extract entities
        merida = make_entity(name="Mérida", entity_type=EntityType.LOCATION, attributes={"growth": "15%"})
        alfredo = make_entity(
            name="Alfredo",
            entity_type=EntityType.PERSON,
            attributes={"role": "investor"},
        )
        loop.run_until_complete(knowledge_graph.upsert_entity(merida))
        loop.run_until_complete(knowledge_graph.upsert_entity(alfredo))
        loop.run_until_complete(
            knowledge_graph.add_relation(
                make_relation(alfredo.entity_id, merida.entity_id, relation_type="interested_in")
            )
        )

        # 6. End episode
        loop.run_until_complete(conversation_memory.end_episode(episode.episode_id, summary="Market analysis request"))

        # Verify everything
        context = loop.run_until_complete(conversation_memory.get_conversation_context("alfredo", "telegram"))
        assert len(context) == 2

        latest_cp = loop.run_until_complete(checkpoint_store.load_latest(run_id))
        assert latest_cp is not None
        assert latest_cp.kernel_state["intent"] == "deep_think"

        entities, relations = loop.run_until_complete(knowledge_graph.get_entity_graph(alfredo.entity_id, depth=1))
        assert len(entities) == 2
        assert len(relations) == 1

    def test_memory_survives_checkpoint_restore(self, conversation_memory, checkpoint_store):
        """Should maintain memory consistency across checkpoint save/restore."""
        from contracts.checkpoint_model import CheckpointData

        loop = asyncio.new_event_loop()

        # Add some memory
        run_id = uuid4()
        for i in range(5):
            loop.run_until_complete(
                conversation_memory.append(make_memory_event(run_id=run_id, content=f"message {i}"))
            )

        # Save checkpoint with memory state
        stats = loop.run_until_complete(conversation_memory.get_stats())
        cp = CheckpointData(
            run_id=run_id,
            step=5,
            memory_state=stats,
            reason="mid-conversation checkpoint",
        )
        loop.run_until_complete(checkpoint_store.save(cp))

        # Load checkpoint
        loaded = loop.run_until_complete(checkpoint_store.load_latest(run_id))
        assert loaded.memory_state["total_events"] == 5

        # Memory should still have all events
        replayed = loop.run_until_complete(conversation_memory.replay(run_id))
        assert len(replayed) == 5
