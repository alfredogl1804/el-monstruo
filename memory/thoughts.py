"""
El Monstruo — Thoughts Store (Sprint 12)
==========================================
Persistent memory layer backed by Supabase `thoughts` table.
Supports:
  - CRUD operations (create, read, update, delete)
  - Hybrid search (semantic + lexical via RRF fusion)
  - Boot sequence (load high-priority memories at session start)
  - Supersede (mark old thought as replaced by new one)
  - Embedding generation via OpenAI text-embedding-3-small

ADR-012 Section 5: "thoughts table is the single source of truth for
all persistent memory. Every memory operation goes through this store."
"""

from __future__ import annotations

import os
from typing import Any, Optional

import structlog

logger = structlog.get_logger("thoughts_store")


class ThoughtsStore:
    """Persistent memory store backed by Supabase thoughts table."""

    def __init__(self, db=None):
        self._db = db
        self._embedding_model = "text-embedding-3-small"
        self._openai_client = None

    async def initialize(self) -> bool:
        """Initialize the store and OpenAI client for embeddings."""
        try:
            from openai import AsyncOpenAI

            api_key = os.environ.get("OPENAI_API_KEY", "")
            if api_key:
                self._openai_client = AsyncOpenAI(api_key=api_key)
                logger.info("thoughts_store_initialized", embedding_model=self._embedding_model)
                return True
            else:
                logger.warning("thoughts_store_no_openai_key", msg="Embeddings disabled")
                return True  # Store works without embeddings, just no vector search
        except Exception as e:
            logger.error("thoughts_store_init_failed", error=str(e))
            return False

    # ── Embedding Generation ──────────────────────────────────────────

    async def _generate_embedding(self, text: str) -> Optional[list[float]]:
        """Generate embedding for text using OpenAI text-embedding-3-small."""
        if not self._openai_client:
            return None
        try:
            response = await self._openai_client.embeddings.create(
                model=self._embedding_model,
                input=text[:8000],  # Truncate to model limit
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("embedding_generation_failed", error=str(e))
            return None

    # ── CRUD Operations ───────────────────────────────────────────────

    async def create(
        self,
        user_id: str,
        layer: str,
        content: str,
        summary: Optional[str] = None,
        tags: Optional[list[str]] = None,
        importance: int = 5,
        project: Optional[str] = None,
        source: Optional[str] = None,
        source_ref: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        procedure_steps: Optional[list[dict]] = None,
        metadata: Optional[dict] = None,
        generate_embedding: bool = True,
    ) -> Optional[dict]:
        """Create a new thought with optional embedding."""
        if not self._db or not self._db.connected:
            logger.warning("thoughts_create_no_db")
            return None

        # Generate embedding from content + summary
        embedding = None
        if generate_embedding:
            embed_text = content
            if summary:
                embed_text = f"{summary}\n\n{content}"
            embedding = await self._generate_embedding(embed_text)

        data = {
            "user_id": user_id,
            "layer": layer,
            "content": content,
            "summary": summary,
            "tags": tags or [],
            "importance": max(1, min(10, importance)),
            "project": project,
            "source": source,
            "source_ref": source_ref,
            "session_id": session_id,
            "agent_id": agent_id,
            "parent_id": parent_id,
            "procedure_steps": procedure_steps,
            "metadata": metadata or {},
            "embedding_model": self._embedding_model,
        }

        if embedding:
            data["embedding"] = embedding

        result = await self._db.insert("thoughts", data)
        if result:
            logger.info(
                "thought_created",
                id=result.get("id"),
                layer=layer,
                importance=importance,
                has_embedding=embedding is not None,
            )
        return result

    async def get(self, thought_id: str) -> Optional[dict]:
        """Get a single thought by ID."""
        if not self._db or not self._db.connected:
            return None
        rows = await self._db.select(
            "thoughts",
            filters={"id": thought_id},
            limit=1,
        )
        return rows[0] if rows else None

    async def list_thoughts(
        self,
        user_id: str,
        layer: Optional[str] = None,
        project: Optional[str] = None,
        include_superseded: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """List thoughts with filters."""
        if not self._db or not self._db.connected:
            return []

        filters = {"user_id": user_id}
        if layer:
            filters["layer"] = layer
        if project:
            filters["project"] = project
        if not include_superseded:
            filters["superseded"] = False

        return await self._db.select(
            "thoughts",
            columns="id,created_at,updated_at,layer,content,summary,tags,importance,project,superseded,superseded_by,source,source_ref,success_count,failure_count",
            filters=filters,
            order_by="created_at",
            order_desc=True,
            limit=limit,
        )

    async def update(
        self,
        thought_id: str,
        user_id: str,
        updates: dict[str, Any],
    ) -> Optional[dict]:
        """Update a thought. Regenerates embedding if content/summary changed."""
        if not self._db or not self._db.connected:
            return None

        # If content or summary changed, regenerate embedding
        if "content" in updates or "summary" in updates:
            current = await self.get(thought_id)
            if current:
                content = updates.get("content", current.get("content", ""))
                summary = updates.get("summary", current.get("summary", ""))
                embed_text = f"{summary}\n\n{content}" if summary else content
                embedding = await self._generate_embedding(embed_text)
                if embedding:
                    updates["embedding"] = embedding

        result = await self._db.update(
            "thoughts",
            data=updates,
            filters={"id": thought_id, "user_id": user_id},
        )
        if result:
            logger.info("thought_updated", id=thought_id)
        return result

    async def delete(self, thought_id: str, user_id: str) -> bool:
        """Delete a thought."""
        if not self._db or not self._db.connected:
            return False
        success = await self._db.delete(
            "thoughts",
            filters={"id": thought_id, "user_id": user_id},
        )
        if success:
            logger.info("thought_deleted", id=thought_id)
        return success

    # ── Supersede ─────────────────────────────────────────────────────

    async def supersede(
        self,
        old_thought_id: str,
        user_id: str,
        new_content: str,
        new_summary: Optional[str] = None,
        new_tags: Optional[list[str]] = None,
        new_importance: Optional[int] = None,
    ) -> Optional[dict]:
        """Replace an old thought with a new one (supersede pattern).
        The old thought is marked as superseded and linked to the new one."""
        old = await self.get(old_thought_id)
        if not old or old.get("user_id") != user_id:
            return None

        # Create new thought inheriting properties from old
        new_thought = await self.create(
            user_id=user_id,
            layer=old["layer"],
            content=new_content,
            summary=new_summary or old.get("summary"),
            tags=new_tags or old.get("tags", []),
            importance=new_importance or old.get("importance", 5),
            project=old.get("project"),
            source=old.get("source"),
            parent_id=old_thought_id,
        )

        if new_thought:
            # Mark old as superseded
            await self._db.update(
                "thoughts",
                data={"superseded": True, "superseded_by": new_thought["id"]},
                filters={"id": old_thought_id},
            )
            logger.info(
                "thought_superseded",
                old_id=old_thought_id,
                new_id=new_thought["id"],
            )

        return new_thought

    # ── Search ────────────────────────────────────────────────────────

    async def hybrid_search(
        self,
        user_id: str,
        query: str,
        layer: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 10,
        min_importance: int = 1,
    ) -> list[dict]:
        """Hybrid search using RRF fusion (semantic + lexical)."""
        if not self._db or not self._db.connected:
            return []

        # Generate query embedding
        embedding = await self._generate_embedding(query)
        if not embedding:
            logger.warning("hybrid_search_no_embedding", fallback="lexical_only")
            # Fall back to lexical-only search
            return await self._lexical_search(user_id, query, layer, project, limit)

        params = {
            "p_user_id": user_id,
            "p_query": query,
            "p_embedding": embedding,
            "p_limit": limit,
            "p_min_importance": min_importance,
        }
        if layer:
            params["p_layer"] = layer
        if project:
            params["p_project"] = project

        result = await self._db.rpc("hybrid_search_thoughts", params)
        return result or []

    async def semantic_search(
        self,
        user_id: str,
        query: str,
        layer: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 10,
        min_importance: int = 1,
    ) -> list[dict]:
        """Pure semantic (vector) search."""
        if not self._db or not self._db.connected:
            return []

        embedding = await self._generate_embedding(query)
        if not embedding:
            return []

        params = {
            "p_user_id": user_id,
            "p_embedding": embedding,
            "p_limit": limit,
            "p_min_importance": min_importance,
        }
        if layer:
            params["p_layer"] = layer
        if project:
            params["p_project"] = project

        result = await self._db.rpc("search_thoughts_semantic", params)
        return result or []

    async def _lexical_search(
        self,
        user_id: str,
        query: str,
        layer: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Fallback lexical-only search using Supabase text search."""
        if not self._db or not self._db.connected:
            return []
        # Use Supabase textSearch
        try:
            q = (
                self._db._client.table("thoughts")
                .select("id,content,summary,layer,importance,tags,project,created_at")
                .eq("user_id", user_id)
                .eq("superseded", False)
                .text_search("content_tsv", query, config="spanish")
                .limit(limit)
            )

            if layer:
                q = q.eq("layer", layer)
            if project:
                q = q.eq("project", project)

            result = q.execute()
            return result.data or []
        except Exception as e:
            logger.error("lexical_search_failed", error=str(e))
            return []

    # ── Boot Sequence ─────────────────────────────────────────────────

    async def boot_sequence(
        self,
        user_id: str,
        project: Optional[str] = None,
        procedural_limit: int = 5,
        semantic_limit: int = 5,
        episodic_limit: int = 10,
    ) -> list[dict]:
        """Load high-priority memories for session start.
        Returns procedural + semantic + episodic thoughts sorted by priority."""
        if not self._db or not self._db.connected:
            return []

        params = {
            "p_user_id": user_id,
            "p_procedural_limit": procedural_limit,
            "p_semantic_limit": semantic_limit,
            "p_episodic_limit": episodic_limit,
        }
        if project:
            params["p_project"] = project

        result = await self._db.rpc("boot_sequence_thoughts", params)
        return result or []

    # ── Stats ─────────────────────────────────────────────────────────

    async def get_stats(self, user_id: str) -> dict:
        """Get memory statistics for a user."""
        if not self._db or not self._db.connected:
            return {"total": 0, "by_layer": {}, "by_project": {}}

        total = await self._db.count("thoughts", filters={"user_id": user_id, "superseded": False})

        stats = {
            "total": total,
            "by_layer": {},
            "by_project": {},
        }

        for layer in ["episodic", "semantic", "procedural"]:
            count = await self._db.count(
                "thoughts",
                filters={"user_id": user_id, "layer": layer, "superseded": False},
            )
            stats["by_layer"][layer] = count

        return stats
