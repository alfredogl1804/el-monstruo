"""
MemPalace Bridge — Episodic + Semantic Memory for El Monstruo
Sprint 23-fix | v0.16.1-sprint23

CORRECTED: Previous bridge used a hallucinated `MemPalace` class that does not exist.
MemPalace is a CLI/MCP tool. The Python API is:
  - mempalace.palace.get_collection(path, name) → ChromaDB Collection
  - collection.add(documents, metadatas, ids) → store
  - collection.query(query_texts, n_results) → search

Tested locally: chromadb 1.5.8 works correctly. No regression.

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

# ── Lazy-loaded collections ──────────────────────────────────────────
_episodes_col = None
_semantic_col = None
_initialized = False
_init_error: Optional[str] = None


def _ensure_initialized():
    """Lazy-init both collections. Returns True if ready."""
    global _episodes_col, _semantic_col, _initialized, _init_error

    if _initialized:
        return _episodes_col is not None

    _initialized = True  # prevent retry loops

    try:
        from mempalace.palace import get_collection
    except ImportError:
        _init_error = "mempalace package not installed"
        logger.warning("mempalace_not_installed")
        return False

    storage_path = os.getenv("MEMPALACE_STORAGE_PATH", "/tmp/monstruo_mempalace")
    os.makedirs(storage_path, exist_ok=True)

    try:
        _episodes_col = get_collection(
            storage_path, collection_name="monstruo_episodes", create=True
        )
        _semantic_col = get_collection(
            storage_path, collection_name="monstruo_semantic", create=True
        )

        # Health probe: verify write + read roundtrip
        _episodes_col.add(
            documents=["__healthcheck__"],
            metadatas=[{"type": "healthcheck"}],
            ids=["__hc__"],
        )
        probe = _episodes_col.query(query_texts=["__healthcheck__"], n_results=1)
        docs = probe.documents[0] if hasattr(probe, "documents") else probe.get("documents", [[]])[0]

        if not docs or docs[0] != "__healthcheck__":
            _init_error = "health probe write/read mismatch"
            logger.error("mempalace_health_probe_failed", extra={"detail": _init_error})
            _episodes_col = None
            _semantic_col = None
            return False

        # Cleanup probe
        try:
            _episodes_col.delete(ids=["__hc__"])
        except Exception:
            pass

        logger.info(
            "mempalace_initialized",
            extra={
                "storage_path": storage_path,
                "episodes_count": _episodes_col.count(),
                "semantic_count": _semantic_col.count(),
            },
        )
        return True

    except Exception as exc:
        _init_error = str(exc)
        logger.error("mempalace_init_failed", extra={"error": _init_error})
        _episodes_col = None
        _semantic_col = None
        return False


# ── Public API ─────────────────────────────────────────────────────


async def store_episode(
    user_id: str,
    session_id: str,
    content: str,
    metadata: Optional[dict[str, Any]] = None,
) -> bool:
    """Store an episodic memory. Called from memory_write node. Fail-silent."""
    if not _ensure_initialized():
        return False

    try:
        doc_metadata = {
            "user_id": user_id,
            "session_id": session_id,
            "type": "episode",
            **(metadata or {}),
        }
        doc_id = f"{session_id}_{hash(content) & 0xFFFFFFFF:08x}"
        _episodes_col.add(
            documents=[content],
            metadatas=[doc_metadata],
            ids=[doc_id],
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
    """Store a semantic memory (fact, pattern, insight). Fail-silent."""
    if not _ensure_initialized():
        return False

    try:
        doc_metadata = {
            "topic": topic,
            "type": "semantic",
            **(metadata or {}),
        }
        doc_id = f"sem_{topic}_{hash(content) & 0xFFFFFFFF:08x}"
        _semantic_col.add(
            documents=[content],
            metadatas=[doc_metadata],
            ids=[doc_id],
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
    """Recall relevant memories by semantic search. Fail-silent."""
    if not _ensure_initialized():
        return []

    try:
        # Choose collection based on memory_type
        col = _semantic_col if memory_type == "semantic" else _episodes_col

        where_filter = {}
        if user_id:
            where_filter["user_id"] = user_id
        if memory_type and memory_type != "semantic":
            where_filter["type"] = memory_type

        results = col.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None,
        )

        memories = []
        docs = results.documents[0] if hasattr(results, "documents") else results.get("documents", [[]])[0]
        metas = results.metadatas[0] if hasattr(results, "metadatas") else results.get("metadatas", [[]])[0]
        dists = results.distances[0] if hasattr(results, "distances") else results.get("distances", [[]])[0]

        for i, doc in enumerate(docs):
            if doc is not None:
                memories.append({
                    "content": doc,
                    "metadata": metas[i] if i < len(metas) else {},
                    "distance": dists[i] if i < len(dists) else None,
                })

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
    if not _ensure_initialized():
        return {
            "status": "unavailable",
            "reason": _init_error or "not_initialized",
        }

    try:
        return {
            "status": "active",
            "backend": "chromadb",
            "episodes_count": _episodes_col.count(),
            "semantic_count": _semantic_col.count(),
            "storage_path": os.getenv("MEMPALACE_STORAGE_PATH", "/tmp/monstruo_mempalace"),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
