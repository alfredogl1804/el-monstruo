"""
Mem0 Bridge — Episodic Memory Layer (Sprint 27)

Replaces Honcho as the user-modeling / episodic memory system.
Uses Mem0 2.0.0 OSS with pgvector (Supabase) for persistent storage.

Architecture:
  - Vector store: pgvector on Supabase (same DB as MemPalace/LightRAG)
  - LLM: OpenAI gpt-5-mini (Mem0 default for fact extraction)
  - Embeddings: OpenAI text-embedding-3-small (1536 dims)

API:
  - add_memory(messages, user_id, metadata) → dict
  - search_memory(query, user_id, limit) → list[dict]
  - get_user_profile(user_id) → dict
  - get_stats() → dict
"""

import os
import logging
from urllib.parse import urlparse

logger = logging.getLogger("monstruo.mem0")

# ── Singleton ──────────────────────────────────────────────────────────
_mem0_instance = None
_init_error = None


def _parse_supabase_url():
    """Parse SUPABASE_DB_URL into individual pgvector config params."""
    db_url = os.environ.get("SUPABASE_DB_URL", "")
    if not db_url:
        raise ValueError("SUPABASE_DB_URL not set — cannot configure Mem0 pgvector")

    parsed = urlparse(db_url)
    return {
        "user": parsed.username or "postgres",
        "password": parsed.password or "",
        "host": parsed.hostname or "localhost",
        "port": str(parsed.port or 5432),
        "dbname": parsed.path.lstrip("/") or "postgres",
    }


def _get_mem0():
    """Lazy-init Mem0 Memory instance with pgvector config."""
    global _mem0_instance, _init_error

    if _mem0_instance is not None:
        return _mem0_instance
    if _init_error is not None:
        raise _init_error

    try:
        from mem0 import Memory

        pg_config = _parse_supabase_url()

        config = {
            "vector_store": {
                "provider": "pgvector",
                "config": {
                    "user": pg_config["user"],
                    "password": pg_config["password"],
                    "host": pg_config["host"],
                    "port": pg_config["port"],
                    "dbname": pg_config["dbname"],
                },
            },
        }

        _mem0_instance = Memory.from_config(config)
        logger.info(
            "mem0_initialized",
            host=pg_config["host"],
            dbname=pg_config["dbname"],
        )
        return _mem0_instance

    except Exception as e:
        _init_error = e
        logger.error("mem0_init_failed", error=str(e))
        raise


# ── Public API ─────────────────────────────────────────────────────────


async def add_memory(
    messages: list[dict],
    user_id: str,
    metadata: dict | None = None,
) -> dict:
    """
    Add a conversation to Mem0 for fact extraction and storage.

    Args:
        messages: List of {"role": "user"|"assistant", "content": "..."}
        user_id: Unique user identifier
        metadata: Optional metadata dict

    Returns:
        dict with "added" count and "memories" list
    """
    try:
        m = _get_mem0()
        kwargs = {"user_id": user_id}
        if metadata:
            kwargs["metadata"] = metadata

        # Mem0's add() is synchronous — run in thread to not block event loop
        import asyncio
        result = await asyncio.to_thread(m.add, messages, **kwargs)

        added_count = len(result.get("results", [])) if isinstance(result, dict) else 0
        logger.info("mem0_add_success", user_id=user_id, added=added_count)
        return {"added": added_count, "raw": result}

    except Exception as e:
        logger.warning("mem0_add_failed", user_id=user_id, error=str(e))
        return {"added": 0, "error": str(e)}


async def search_memory(
    query: str,
    user_id: str,
    limit: int = 5,
) -> list[dict]:
    """
    Search Mem0 for relevant memories.

    Returns:
        List of {"id", "memory", "score", "created_at"} dicts
    """
    try:
        m = _get_mem0()
        import asyncio
        result = await asyncio.to_thread(
            m.search, query, user_id=user_id, limit=limit
        )

        memories = []
        raw_results = result.get("results", []) if isinstance(result, dict) else result
        for r in raw_results:
            memories.append({
                "id": r.get("id", ""),
                "memory": r.get("memory", ""),
                "score": r.get("score", 0.0),
                "created_at": r.get("created_at", ""),
            })

        logger.info("mem0_search_success", user_id=user_id, results=len(memories))
        return memories

    except Exception as e:
        logger.warning("mem0_search_failed", user_id=user_id, error=str(e))
        return []


async def get_user_profile(user_id: str) -> dict:
    """
    Get all memories for a user — used for user profile/context injection.

    Returns:
        dict with "memories" list and "mem0_active" bool
    """
    try:
        m = _get_mem0()
        import asyncio
        result = await asyncio.to_thread(m.get_all, user_id=user_id)

        raw_results = result.get("results", []) if isinstance(result, dict) else result
        memories = []
        for r in raw_results:
            memories.append({
                "id": r.get("id", ""),
                "memory": r.get("memory", ""),
                "categories": r.get("categories", []),
                "created_at": r.get("created_at", ""),
            })

        return {
            "mem0_active": True,
            "memory_count": len(memories),
            "memories": memories,
        }

    except Exception as e:
        logger.warning("mem0_get_all_failed", user_id=user_id, error=str(e))
        return {"mem0_active": False, "memory_count": 0, "memories": [], "error": str(e)}


async def get_stats() -> dict:
    """Return stats for the /memory/stats endpoint."""
    try:
        _get_mem0()
        return {"status": "active", "provider": "pgvector", "version": "2.0.0"}
    except Exception as e:
        return {"status": "inactive", "error": str(e)}
