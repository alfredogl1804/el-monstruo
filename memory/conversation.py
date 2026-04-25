"""
El Monstruo — Conversation Memory (Día 2)
============================================
Full implementation of MemoryInterface.
Manages episodic memory, conversation context, and search.

Dual mode: in-memory (always) + Supabase (when configured).
Embedding generation via LiteLLM or OpenAI for semantic search.

Principio: Las conversaciones persisten. El Monstruo recuerda todo.
"""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

import structlog

from contracts.memory_interface import (
    Entity,
    Episode,
    MemoryEvent,
    MemoryInterface,
    MemoryType,
    Relation,
    SearchResult,
)
from memory.supabase_client import SupabaseClient

logger = structlog.get_logger("conversation_memory")


class ConversationMemory(MemoryInterface):
    """
    Sovereign conversation memory.

    Implements the full MemoryInterface contract:
    - Append-only event log (event sourcing)
    - Semantic search (via embeddings)
    - Keyword search (full-text)
    - Hybrid search (vector + keyword)
    - Episodes (conversation grouping)
    - Replay (reconstruct any conversation)

    Always keeps data in-memory for fast access.
    Optionally persists to Supabase for durability.
    """

    def __init__(
        self,
        db: Optional[SupabaseClient] = None,
        embedding_model: str = "text-embedding-3-small",
    ) -> None:
        # In-memory stores
        self._events: list[MemoryEvent] = []
        self._by_run: dict[UUID, list[MemoryEvent]] = defaultdict(list)
        self._by_user: dict[str, list[MemoryEvent]] = defaultdict(list)
        self._by_type: dict[MemoryType, list[MemoryEvent]] = defaultdict(list)
        self._episodes: dict[UUID, Episode] = {}
        self._episodes_by_user: dict[str, list[UUID]] = defaultdict(list)

        # Persistence
        self._db = db
        self._embedding_model = embedding_model
        self._embedding_client = None

    async def count(self) -> int:
        """Return total number of memory events stored."""
        return len(self._events)

    async def initialize(self) -> None:
        """Initialize embedding client and DB connection."""
        # Embedding generation uses OpenAI or Gemini directly (no LiteLLM proxy)
        openai_key = os.environ.get("OPENAI_API_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if openai_key:
            logger.info(
                "embedding_client_initialized",
                provider="openai",
                model=self._embedding_model,
            )
        elif gemini_key:
            logger.info(
                "embedding_client_initialized",
                provider="gemini",
                model="text-embedding-004",
            )
        else:
            logger.warning("embedding_no_provider", msg="No OPENAI_API_KEY or GEMINI_API_KEY found")

        if self._db and self._db.connected:
            logger.info("conversation_memory_initialized", persistence="supabase")
        else:
            logger.info("conversation_memory_initialized", persistence="in-memory")

    # ── Event Log ──────────────────────────────────────────────────

    async def append(self, event: MemoryEvent) -> UUID:
        """Append a memory event. Never modifies, never deletes."""
        # In-memory
        self._events.append(event)
        if event.run_id:
            self._by_run[event.run_id].append(event)
        if event.user_id:
            self._by_user[event.user_id].append(event)
        self._by_type[event.memory_type].append(event)

        # Generate embedding if not provided
        embedding = event.embedding
        if embedding is None and event.content:
            embedding = await self._generate_embedding(event.content)

        # Persist to Supabase
        if self._db and self._db.connected:
            await self._db.insert(
                "memory_events",
                {
                    "event_id": str(event.event_id),
                    "memory_type": event.memory_type.value,
                    "run_id": str(event.run_id) if event.run_id else None,
                    "user_id": event.user_id or None,
                    "channel": event.channel or None,
                    "content": event.content,
                    "embedding": embedding,
                    "metadata": event.metadata,
                    "created_at": event.created_at.isoformat()
                    if hasattr(event.created_at, "isoformat")
                    else str(event.created_at),
                },
            )

        logger.debug(
            "memory_event_appended",
            event_id=str(event.event_id),
            memory_type=event.memory_type.value,
            has_embedding=embedding is not None,
        )
        return event.event_id

    async def append_batch(self, events: list[MemoryEvent]) -> list[UUID]:
        """Append multiple events."""
        ids = []
        for event in events:
            eid = await self.append(event)
            ids.append(eid)
        return ids

    # ── Search ─────────────────────────────────────────────────────

    async def search_semantic(
        self,
        query: str,
        user_id: Optional[str] = None,
        memory_types: Optional[list[MemoryType]] = None,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[SearchResult]:
        """Search by vector similarity."""
        query_embedding = await self._generate_embedding(query)
        if not query_embedding:
            # Fallback to keyword search
            return await self.search_keyword(query, user_id, memory_types, limit)

        # If Supabase is connected, use pgvector
        if self._db and self._db.connected:
            return await self._search_semantic_supabase(query_embedding, user_id, memory_types, limit, threshold)

        # In-memory cosine similarity
        return self._search_semantic_local(query_embedding, user_id, memory_types, limit, threshold)

    async def search_keyword(
        self,
        query: str,
        user_id: Optional[str] = None,
        memory_types: Optional[list[MemoryType]] = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Search by keywords. In-memory first, Supabase fallback."""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        results = []

        candidates = self._events
        if user_id:
            candidates = self._by_user.get(user_id, [])

        # If in-memory is empty, try Supabase
        if not candidates and self._db and self._db.connected:
            try:
                filters = {}
                if user_id:
                    filters["user_id"] = user_id
                rows = await self._db.select(
                    "memory_events",
                    columns="event_id,content,metadata,memory_type,user_id,channel,created_at",
                    filters=filters,
                    order_by="created_at",
                    order_desc=True,
                    limit=50,  # Get recent events for keyword search
                )
                for row in rows:
                    content_lower = (row.get("content", "") or "").lower()
                    content_words = set(content_lower.split())
                    overlap = len(query_words & content_words)
                    if overlap > 0:
                        score = overlap / max(len(query_words), 1)
                        # Create a lightweight MemoryEvent from DB row
                        event = MemoryEvent(
                            event_id=UUID(row["event_id"]) if row.get("event_id") else uuid4(),
                            memory_type=MemoryType(row.get("memory_type", "episodic")),
                            user_id=row.get("user_id"),
                            channel=row.get("channel"),
                            content=row.get("content", ""),
                            metadata=row.get("metadata", {}),
                        )
                        results.append(
                            SearchResult(
                                event=event,
                                score=score,
                                source="keyword_supabase",
                            )
                        )
                logger.info(
                    "keyword_search_from_supabase",
                    results=len(results),
                    query=query[:50],
                )
            except Exception as e:
                logger.warning("keyword_search_supabase_failed", error=str(e))
        else:
            for event in candidates:
                if memory_types and event.memory_type not in memory_types:
                    continue

                content_lower = event.content.lower()
                content_words = set(content_lower.split())
                overlap = len(query_words & content_words)
                if overlap > 0:
                    score = overlap / max(len(query_words), 1)
                    results.append(
                        SearchResult(
                            event=event,
                            score=score,
                            source="keyword",
                        )
                    )

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    async def search_hybrid(
        self,
        query: str,
        user_id: Optional[str] = None,
        memory_types: Optional[list[MemoryType]] = None,
        limit: int = 10,
        vector_weight: float = 0.7,
    ) -> list[SearchResult]:
        """Hybrid search: vector + keyword with configurable weights."""
        # Get both result sets
        semantic_results = await self.search_semantic(query, user_id, memory_types, limit * 2)
        keyword_results = await self.search_keyword(query, user_id, memory_types, limit * 2)

        # Merge and re-score
        scored: dict[UUID, tuple[MemoryEvent, float]] = {}

        for r in semantic_results:
            scored[r.event.event_id] = (r.event, r.score * vector_weight)

        keyword_weight = 1.0 - vector_weight
        for r in keyword_results:
            if r.event.event_id in scored:
                event, existing_score = scored[r.event.event_id]
                scored[r.event.event_id] = (
                    event,
                    existing_score + r.score * keyword_weight,
                )
            else:
                scored[r.event.event_id] = (r.event, r.score * keyword_weight)

        # Sort and return
        merged = [
            SearchResult(event=event, score=score, source="hybrid")
            for event, score in sorted(scored.values(), key=lambda x: x[1], reverse=True)
        ]
        return merged[:limit]

    # ── Episodes ───────────────────────────────────────────────────

    async def start_episode(self, user_id: str, channel: str) -> Episode:
        """Start a new conversation episode."""
        episode = Episode(
            episode_id=uuid4(),
            user_id=user_id,
            channel=channel,
            started_at=datetime.now(timezone.utc),
        )

        self._episodes[episode.episode_id] = episode
        self._episodes_by_user[user_id].append(episode.episode_id)

        # Persist
        if self._db and self._db.connected:
            await self._db.insert(
                "episodes",
                {
                    "episode_id": str(episode.episode_id),
                    "user_id": user_id,
                    "channel": channel,
                    "started_at": episode.started_at.isoformat(),
                },
            )

        logger.info("episode_started", episode_id=str(episode.episode_id), user_id=user_id)
        return episode

    async def end_episode(
        self,
        episode_id: UUID,
        summary: Optional[str] = None,
    ) -> Episode:
        """End an episode and optionally set summary."""
        episode = self._episodes.get(episode_id)
        if not episode:
            raise ValueError(f"Episode {episode_id} not found")

        episode.ended_at = datetime.now(timezone.utc)
        if summary:
            episode.summary = summary

        # Persist
        if self._db and self._db.connected:
            await self._db.update(
                "episodes",
                {
                    "ended_at": episode.ended_at.isoformat(),
                    "summary": episode.summary,
                },
                {"episode_id": str(episode_id)},
            )

        logger.info("episode_ended", episode_id=str(episode_id), event_count=len(episode.events))
        return episode

    async def get_recent_episodes(
        self,
        user_id: str,
        limit: int = 5,
    ) -> list[Episode]:
        """Get the most recent episodes for a user."""
        episode_ids = self._episodes_by_user.get(user_id, [])
        episodes = [self._episodes[eid] for eid in episode_ids if eid in self._episodes]
        # Sort by start time descending
        episodes.sort(key=lambda e: e.started_at, reverse=True)
        return episodes[:limit]

    async def add_to_episode(
        self,
        episode_id: UUID,
        event: MemoryEvent,
    ) -> None:
        """Add a memory event to an episode."""
        episode = self._episodes.get(episode_id)
        if episode:
            episode.events.append(event)

    # ── Replay ─────────────────────────────────────────────────────

    async def replay(self, run_id: UUID) -> list[MemoryEvent]:
        """Reconstruct the complete event sequence for a run."""
        events = self._by_run.get(run_id, [])
        return sorted(events, key=lambda e: e.created_at)

    async def get_event_count(
        self,
        user_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
    ) -> int:
        """Count events with optional filters."""
        if user_id and memory_type:
            return len([e for e in self._by_user.get(user_id, []) if e.memory_type == memory_type])
        if user_id:
            return len(self._by_user.get(user_id, []))
        if memory_type:
            return len(self._by_type.get(memory_type, []))
        return len(self._events)

    # ── Context Building ───────────────────────────────────────────

    async def get_conversation_context(
        self,
        user_id: str,
        channel: str = "",
        max_messages: int = 20,
        max_tokens: int = 4000,
    ) -> list[dict[str, str]]:
        """
        Build conversation context for LLM calls.
        Returns recent messages in OpenAI-compatible format.
        Reads from in-memory first, falls back to Supabase for persistence.
        """
        user_events = self._by_user.get(user_id, [])

        # Filter to episodic events in the right channel
        relevant = [
            e for e in user_events if e.memory_type == MemoryType.EPISODIC and (not channel or e.channel == channel)
        ]

        # If in-memory is empty but Supabase is connected, read from DB
        if not relevant and self._db and self._db.connected:
            try:
                filters = {"user_id": user_id, "memory_type": "episodic"}
                if channel:
                    filters["channel"] = channel
                rows = await self._db.select(
                    "memory_events",
                    columns="content,metadata,created_at",
                    filters=filters,
                    order_by="created_at",
                    order_desc=False,
                    limit=max_messages,
                )
                if rows:
                    messages = []
                    total_chars = 0
                    char_limit = max_tokens * 4
                    for row in rows[-max_messages:]:
                        meta = row.get("metadata", {}) or {}
                        role = meta.get("role", "user")
                        content = row.get("content", "")
                        if total_chars + len(content) > char_limit:
                            break
                        messages.append({"role": role, "content": content})
                        total_chars += len(content)
                    logger.info(
                        "conversation_context_from_supabase",
                        messages=len(messages),
                        user_id=user_id,
                    )
                    return messages
            except Exception as e:
                logger.warning("conversation_context_supabase_failed", error=str(e))

        # Take the most recent from in-memory
        recent = relevant[-max_messages:]

        # Build messages
        messages = []
        total_chars = 0
        char_limit = max_tokens * 4  # Rough chars-to-tokens ratio

        for event in recent:
            role = event.metadata.get("role", "user")
            content = event.content

            if total_chars + len(content) > char_limit:
                break

            messages.append({"role": role, "content": content})
            total_chars += len(content)

        return messages

    async def get_user_summary(self, user_id: str) -> dict[str, Any]:
        """Get a summary of what we know about a user."""
        user_events = self._by_user.get(user_id, [])
        episodes = await self.get_recent_episodes(user_id, limit=10)

        type_counts = defaultdict(int)
        for e in user_events:
            type_counts[e.memory_type.value] += 1

        return {
            "user_id": user_id,
            "total_events": len(user_events),
            "total_episodes": len(episodes),
            "events_by_type": dict(type_counts),
            "first_seen": user_events[0].created_at.isoformat() if user_events else None,
            "last_seen": user_events[-1].created_at.isoformat() if user_events else None,
        }

    # ── Stats ──────────────────────────────────────────────────────

    async def get_stats(self) -> dict[str, Any]:
        """Get conversation memory statistics."""
        return {
            "total_events": len(self._events),
            "unique_users": len(self._by_user),
            "unique_runs": len(self._by_run),
            "total_episodes": len(self._episodes),
            "events_by_type": {t.value: len(events) for t, events in self._by_type.items()},
            "persistence": "supabase" if (self._db and self._db.connected) else "in-memory",
        }

    # ── Knowledge Graph stubs (delegated to graph module) ──────────

    async def upsert_entity(self, entity: Entity) -> UUID:
        raise DeprecationWarning("Delegated to KnowledgeGraph module. Import from memory.knowledge_graph directly.")

    async def add_relation(self, relation: Relation) -> UUID:
        raise DeprecationWarning("Delegated to KnowledgeGraph module. Import from memory.knowledge_graph directly.")

    async def get_entity_graph(self, entity_id: UUID, depth: int = 2):
        raise DeprecationWarning("Delegated to KnowledgeGraph module. Import from memory.knowledge_graph directly.")

    async def find_entities(self, query: str, entity_type=None, limit: int = 10):
        raise DeprecationWarning("Delegated to KnowledgeGraph module. Import from memory.knowledge_graph directly.")

    # ── Private Methods ────────────────────────────────────────────

    async def _generate_embedding(self, text: str) -> Optional[list[float]]:
        """Generate embedding via OpenAI directly (sovereign, no LiteLLM proxy)."""
        if not text.strip():
            return None

        # Try OpenAI directly (primary path — sovereign, no proxy)
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.openai.com/v1/embeddings",
                        json={
                            "model": self._embedding_model,
                            "input": text[:8000],
                        },
                        headers={"Authorization": f"Bearer {openai_key}"},
                        timeout=30.0,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return data["data"][0]["embedding"]
                    else:
                        logger.warning(
                            "embedding_openai_error",
                            status=response.status_code,
                            body=response.text[:200],
                        )
            except Exception as e:
                logger.warning("embedding_openai_exception", error=str(e))

        # Fallback: try Gemini embedding if available
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            try:
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={gemini_key}",
                        json={
                            "model": "models/text-embedding-004",
                            "content": {"parts": [{"text": text[:8000]}]},
                        },
                        timeout=30.0,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        embedding = data.get("embedding", {}).get("values", [])
                        if embedding:
                            return embedding
            except Exception as e:
                logger.warning("embedding_gemini_exception", error=str(e))

        logger.warning("embedding_generation_failed", text_len=len(text))
        return None

    def _search_semantic_local(
        self,
        query_embedding: list[float],
        user_id: Optional[str],
        memory_types: Optional[list[MemoryType]],
        limit: int,
        threshold: float,
    ) -> list[SearchResult]:
        """In-memory cosine similarity search."""

        results = []
        candidates = self._events
        if user_id:
            candidates = self._by_user.get(user_id, [])

        for event in candidates:
            if memory_types and event.memory_type not in memory_types:
                continue
            if not event.embedding:
                continue

            # Cosine similarity
            score = self._cosine_similarity(query_embedding, event.embedding)
            if score >= threshold:
                results.append(
                    SearchResult(
                        event=event,
                        score=score,
                        source="vector",
                    )
                )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    async def _search_semantic_supabase(
        self,
        query_embedding: list[float],
        user_id: Optional[str],
        memory_types: Optional[list[MemoryType]],
        limit: int,
        threshold: float,
    ) -> list[SearchResult]:
        """Search using pgvector in Supabase via RPC."""
        # This would call a Postgres function for vector similarity
        # For now, fall back to local search
        return self._search_semantic_local(query_embedding, user_id, memory_types, limit, threshold)

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import math

        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
