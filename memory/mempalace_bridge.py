"""
MemPalace Bridge — Episodic + Semantic Memory for El Monstruo
Sprint 23 | v0.16.0-sprint23
IVD: mempalace==3.3.2 (MIT, PyPI latest 2026-04-22)
Fix: chromadb>=1.5.4 has regression (issue #1006) — added defensive init + health probe
GitHub: MemPalace/mempalace (48K+ stars)

Architecture:
  - MemPalace stores long-term episodic memories (conversations, decisions, outcomes)
  - Complemented by Honcho (user modeling) and PostgresSaver (checkpoints)
  - Memory hierarchy:
      1. PostgresSaver → short-term (graph state checkpoints)
      2. Honcho → user modeling (preferences, dialectic profiles)
      3. MemPalace → long-term episodic + semantic (searchable palace)

Integration:
  - Called from memory_write node (after respond)
  - Called from intake node (retrieval before processing)
  - Fail-silent: if MemPalace is unavailable, kernel continues without it
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

logger = logging.getLogger("monstruo.memory.mempalace")

# ── Lazy import to avoid import-time failures ──────────────────────
_palace = None


def _get_palace():
    """Lazy-load MemPalace instance. Returns None if unavailable.

    Sprint 23: Added health probe after init to catch chromadb 1.5.x
    regression (issue #1006) where writes silently fail.
    """
    global _palace
    if _palace is not None:
        return _palace

    try:
        from mempalace import MemPalace

        # MemPalace uses ChromaDB as backend — no API key required
        # Storage path configurable via env
        storage_path = os.getenv(
            "MEMPALACE_STORAGE_PATH", "/tmp/monstruo_mempalace"
        )
        palace = MemPalace(
            storage_path=storage_path,
            collection_name=os.getenv("MEMPALACE_COLLECTION", "monstruo_v1"),
        )

        # Sprint 23: Health probe — verify chromadb actually works
        _test_id = "__healthcheck__"
        palace.add(
            documents=["mempalace health probe"],
            metadatas=[{"type": "healthcheck"}],
            ids=[_test_id],
        )
        probe = palace.query(
            query_texts=["mempalace health probe"],
            n_results=1,
        )
        probe_docs = probe.get("documents", [[]])[0] if probe else []
        probe_metas = probe.get("metadatas", [[]])[0] if probe else []

        if not probe_docs or probe_docs[0] is None:
            logger.error(
                "mempalace_chromadb_regression_detected",
                extra={
                    "issue": "chromadb 1.5.x regression — writes silently broken",
                    "ref": "https://github.com/MemPalace/mempalace/issues/1006",
                },
            )
            return None

        if not probe_metas or probe_metas[0] is None:
            logger.warning(
                "mempalace_metadata_degraded",
                extra={"detail": "query returns None metadata — partial regression"},
            )

        # Clean up health probe
        try:
            palace._collection.delete(ids=[_test_id])
        except Exception:
            pass  # Non-critical

        _palace = palace
        logger.info(
            "mempalace_initialized",
            extra={"storage_path": storage_path, "health_probe": "passed"},
        )
        return _palace
    except ImportError:
        logger.warning("mempalace package not installed — memory disabled")
        return None
    except Exception as exc:
        logger.error("mempalace_init_failed", extra={"error": str(exc)})
        return None


# ── Public API ─────────────────────────────────────────────────────


async def store_episode(
    user_id: str,
    session_id: str,
    content: str,
    metadata: Optional[dict[str, Any]] = None,
) -> bool:
    """
    Store an episodic memory (conversation turn, decision, outcome).
    Called from memory_write node.

    Returns True if stored successfully, False otherwise (fail-silent).
    """
    palace = _get_palace()
    if palace is None:
        return False

    try:
        doc_metadata = {
            "user_id": user_id,
            "session_id": session_id,
            "type": "episode",
            **(metadata or {}),
        }
        palace.add(
            documents=[content],
            metadatas=[doc_metadata],
            ids=[f"{session_id}_{hash(content) & 0xFFFFFFFF:08x}"],
        )
        logger.debug(
            "episode_stored",
            extra={"user_id": user_id, "session_id": session_id, "len": len(content)},
        )
        return True
    except Exception as exc:
        logger.error("episode_store_failed", extra={"error": str(exc)})
        return False


async def store_semantic(
    topic: str,
    content: str,
    metadata: Optional[dict[str, Any]] = None,
) -> bool:
    """
    Store a semantic memory (fact, learned pattern, skill outcome).
    Called after skill_evaluator produces insights.

    Returns True if stored successfully, False otherwise.
    """
    palace = _get_palace()
    if palace is None:
        return False

    try:
        doc_metadata = {
            "topic": topic,
            "type": "semantic",
            **(metadata or {}),
        }
        palace.add(
            documents=[content],
            metadatas=[doc_metadata],
            ids=[f"sem_{topic}_{hash(content) & 0xFFFFFFFF:08x}"],
        )
        logger.debug("semantic_stored", extra={"topic": topic, "len": len(content)})
        return True
    except Exception as exc:
        logger.error("semantic_store_failed", extra={"error": str(exc)})
        return False


async def recall(
    query: str,
    user_id: Optional[str] = None,
    n_results: int = 5,
    memory_type: Optional[str] = None,
) -> list[dict[str, Any]]:
    """
    Recall relevant memories by semantic search.
    Called from intake node to enrich context.

    Args:
        query: Natural language query
        user_id: Optional filter by user
        n_results: Max results to return
        memory_type: Optional filter ("episode" or "semantic")

    Returns list of dicts with 'content', 'metadata', 'distance'.
    Returns empty list on failure (fail-silent).
    """
    palace = _get_palace()
    if palace is None:
        return []

    try:
        where_filter = {}
        if user_id:
            where_filter["user_id"] = user_id
        if memory_type:
            where_filter["type"] = memory_type

        results = palace.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None,
        )

        memories = []
        if results and results.get("documents"):
            docs = results["documents"][0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]

            for i, doc in enumerate(docs):
                memories.append(
                    {
                        "content": doc,
                        "metadata": metas[i] if i < len(metas) else {},
                        "distance": dists[i] if i < len(dists) else None,
                    }
                )

        logger.debug(
            "recall_complete",
            extra={"query_len": len(query), "results": len(memories)},
        )
        return memories
    except Exception as exc:
        logger.error("recall_failed", extra={"error": str(exc)})
        return []


async def get_stats() -> dict[str, Any]:
    """Return MemPalace stats for /v1/memory/status endpoint."""
    palace = _get_palace()
    if palace is None:
        return {"status": "unavailable", "reason": "not_initialized"}

    try:
        # ChromaDB collection count
        count = palace._collection.count() if hasattr(palace, "_collection") else -1
        return {
            "status": "active",
            "backend": "chromadb",
            "collection": os.getenv("MEMPALACE_COLLECTION", "monstruo_v1"),
            "document_count": count,
            "storage_path": os.getenv("MEMPALACE_STORAGE_PATH", "/tmp/monstruo_mempalace"),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
