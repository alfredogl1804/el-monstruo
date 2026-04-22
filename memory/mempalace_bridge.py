"""
MemPalace Bridge — Episodic + Semantic Memory for El Monstruo
Sprint 24 | v0.17.0-sprint24

MIGRATED: ChromaDB → pgvector (Supabase).
  - ChromaDB used /tmp/ in Railway (ephemeral, lost on every deploy)
  - pgvector uses Supabase PostgreSQL (persistent, already hosts checkpointer)
  - Embeddings via OpenAI text-embedding-3-small (1536 dims)

Tables:
  - mempalace_episodes: user conversations, decisions, outcomes
  - mempalace_semantic: facts, patterns, insights

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

import httpx

logger = logging.getLogger("monstruo.memory.mempalace")

# ── State ───────────────────────────────────────────────────────────
_initialized = False
_init_error: Optional[str] = None
_db_url: Optional[str] = None
_openai_api_key: Optional[str] = None
_conn = None


def _get_connection():
    """Get or create a psycopg v3 connection to Supabase."""
    global _conn
    if _conn is not None:
        try:
            _conn.execute("SELECT 1")
            return _conn
        except Exception:
            try:
                _conn.close()
            except Exception:
                pass
            _conn = None

    import psycopg
    _conn = psycopg.connect(_db_url, autocommit=True)
    return _conn


def _get_embedding(text: str) -> Optional[list[float]]:
    """Get embedding from OpenAI text-embedding-3-small. Synchronous for simplicity."""
    if not _openai_api_key:
        return None
    try:
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        resp = httpx.post(
            f"{api_base}/embeddings",
            headers={"Authorization": f"Bearer {_openai_api_key}"},
            json={"model": "text-embedding-3-small", "input": text},
            timeout=15.0,
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except Exception as exc:
        logger.warning("embedding_failed", extra={"error": str(exc)})
        return None


def _ensure_initialized() -> bool:
    """Lazy-init pgvector connection. Returns True if ready."""
    global _initialized, _init_error, _db_url, _openai_api_key

    if _initialized:
        return _db_url is not None

    _initialized = True

    _db_url = os.getenv("SUPABASE_DB_URL")
    if not _db_url:
        _init_error = "SUPABASE_DB_URL not set"
        logger.warning("mempalace_no_db_url")
        return False

    _openai_api_key = os.getenv("OPENAI_API_KEY")
    if not _openai_api_key:
        _init_error = "OPENAI_API_KEY not set (needed for embeddings)"
        logger.warning("mempalace_no_openai_key")
        return False

    try:
        conn = _get_connection()

        # Health probe: verify tables exist
        result = conn.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'mempalace_episodes')"
        ).fetchone()
        if not result[0]:
            _init_error = "mempalace_episodes table not found"
            logger.error("mempalace_table_missing")
            _db_url = None
            return False

        # Test embedding generation
        test_emb = _get_embedding("health check")
        if not test_emb or len(test_emb) != 1536:
            _init_error = "embedding generation failed or wrong dimensions"
            logger.error("mempalace_embedding_test_failed")
            _db_url = None
            return False

        # Count existing records
        ep_count = conn.execute("SELECT count(*) FROM mempalace_episodes").fetchone()[0]
        sem_count = conn.execute("SELECT count(*) FROM mempalace_semantic").fetchone()[0]

        logger.info(
            "mempalace_initialized",
            extra={
                "backend": "pgvector",
                "episodes_count": ep_count,
                "semantic_count": sem_count,
            },
        )
        return True

    except Exception as exc:
        _init_error = str(exc)
        logger.error("mempalace_init_failed", extra={"error": _init_error})
        _db_url = None
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
        import json as _json
        embedding = _get_embedding(content)
        doc_id = f"{session_id}_{hash(content) & 0xFFFFFFFF:08x}"
        meta_json = _json.dumps(metadata or {})

        conn = _get_connection()

        if embedding:
            conn.execute(
                """INSERT INTO mempalace_episodes (id, user_id, session_id, content, embedding, metadata)
                   VALUES (%s, %s, %s, %s, %s::vector, %s::jsonb)
                   ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content,
                   embedding = EXCLUDED.embedding, metadata = EXCLUDED.metadata""",
                (doc_id, user_id, session_id, content, str(embedding), meta_json),
            )
        else:
            conn.execute(
                """INSERT INTO mempalace_episodes (id, user_id, session_id, content, metadata)
                   VALUES (%s, %s, %s, %s, %s::jsonb)
                   ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, metadata = EXCLUDED.metadata""",
                (doc_id, user_id, session_id, content, meta_json),
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
        import json as _json
        embedding = _get_embedding(content)
        doc_id = f"sem_{topic}_{hash(content) & 0xFFFFFFFF:08x}"
        meta_json = _json.dumps(metadata or {})

        conn = _get_connection()

        if embedding:
            conn.execute(
                """INSERT INTO mempalace_semantic (id, topic, content, embedding, metadata)
                   VALUES (%s, %s, %s, %s::vector, %s::jsonb)
                   ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content,
                   embedding = EXCLUDED.embedding, metadata = EXCLUDED.metadata""",
                (doc_id, topic, content, str(embedding), meta_json),
            )
        else:
            conn.execute(
                """INSERT INTO mempalace_semantic (id, topic, content, metadata)
                   VALUES (%s, %s, %s, %s::jsonb)
                   ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, metadata = EXCLUDED.metadata""",
                (doc_id, topic, content, meta_json),
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
    """Recall relevant memories by semantic search using pgvector. Fail-silent."""
    if not _ensure_initialized():
        return []

    try:
        embedding = _get_embedding(query)
        if not embedding:
            return []

        table = "mempalace_semantic" if memory_type == "semantic" else "mempalace_episodes"
        emb_str = str(embedding)

        # Build query with optional filters
        if user_id and table == "mempalace_episodes":
            sql = f"""SELECT id, content, metadata, 1 - (embedding <=> %s::vector) AS similarity
                      FROM {table} WHERE user_id = %s
                      ORDER BY embedding <=> %s::vector LIMIT %s"""
            params = (emb_str, user_id, emb_str, n_results)
        else:
            sql = f"""SELECT id, content, metadata, 1 - (embedding <=> %s::vector) AS similarity
                      FROM {table}
                      ORDER BY embedding <=> %s::vector LIMIT %s"""
            params = (emb_str, emb_str, n_results)

        conn = _get_connection()
        rows = conn.execute(sql, params).fetchall()

        memories = []
        for row in rows:
            doc_id, content, meta, similarity = row
            memories.append({
                "content": content,
                "metadata": meta or {},
                "similarity": round(float(similarity), 4) if similarity else None,
                "id": doc_id,
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
        conn = _get_connection()
        ep_count = conn.execute("SELECT count(*) FROM mempalace_episodes").fetchone()[0]
        sem_count = conn.execute("SELECT count(*) FROM mempalace_semantic").fetchone()[0]

        return {
            "status": "active",
            "backend": "pgvector",
            "episodes_count": ep_count,
            "semantic_count": sem_count,
            "db": "supabase",
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
