"""
LightRAG Bridge — Knowledge Graph RAG for El Monstruo
Sprint 25 | v0.18.0-sprint25
IVD: lightrag-hku==1.4.15 (MIT, PyPI latest 2026-04-22)
CVE-2026-39413: JWT in API server only — we don't use the server.

Architecture:
  - LightRAG builds a knowledge graph from ingested documents
  - Supports dual-level retrieval: local (entity-centric) + global (theme-centric)
  - Storage: pgvector via Supabase (Sprint 25 — migrated from /tmp file-based)
  - Embeddings: Uses OpenAI API via OPENAI_API_KEY env var (auto-detected)

Sprint 25 Migration (CRITICAL):
  - BEFORE: working_dir=/tmp/monstruo_lightrag (NanoVectorDB + NetworkX + JSON)
    → Data LOST on every Railway deploy (ephemeral filesystem)
  - AFTER: PGKVStorage + PGVectorStorage + PGGraphStorage + PGDocStatusStorage
    → Persistent in Supabase PostgreSQL with pgvector extension
  - Connection: LightRAG's ClientManager reads POSTGRES_* env vars automatically
    Required env vars: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER,
    POSTGRES_PASSWORD, POSTGRES_DATABASE, POSTGRES_WORKSPACE
  - LightRAG auto-creates tables on first init via its own migration system

API validated locally 2026-04-22:
  - PGKVStorage, PGVectorStorage, PGGraphStorage, PGDocStatusStorage
    from lightrag.kg.postgres_impl
  - ClientManager.get_config() reads POSTGRES_* env vars
  - LightRAG constructor: kv_storage, vector_storage, graph_storage, doc_status_storage

Integration:
  - /v1/knowledge/ingest → ingest documents into the knowledge graph
  - /v1/knowledge/query  → query the knowledge graph (hybrid retrieval)
  - enrich node          → retrieve relevant knowledge during conversation

Principio: LightRAG is an optional enhancement. Fails silently, never blocks.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger("monstruo.memory.lightrag")

# ── Lazy singleton ────────────────────────────────────────────────────
_rag = None
_rag_init_attempted = False
_rag_init_error: str | None = None


def _inject_postgres_env_from_db_url() -> bool:
    """
    Parse SUPABASE_DB_URL and set POSTGRES_* env vars that LightRAG's
    ClientManager.get_config() expects. Returns True if successful.

    This bridges the gap between our single SUPABASE_DB_URL and LightRAG's
    expectation of individual POSTGRES_* env vars.
    Only sets vars if they are not already set (respects explicit overrides).
    """
    db_url = os.getenv("SUPABASE_DB_URL", "")
    if not db_url:
        return False

    parsed = urlparse(db_url)
    qs = parse_qs(parsed.query)

    env_map = {
        "POSTGRES_HOST": parsed.hostname or "localhost",
        "POSTGRES_PORT": str(parsed.port or 5432),
        "POSTGRES_USER": parsed.username or "postgres",
        "POSTGRES_PASSWORD": parsed.password or "",
        "POSTGRES_DATABASE": (parsed.path or "/postgres").lstrip("/"),
        "POSTGRES_WORKSPACE": os.getenv("LIGHTRAG_WORKSPACE", "monstruo"),
    }

    # SSL mode: Supabase uses self-signed certs, so we need "require" (not "verify-full")
    # LightRAG's PostgreSQLDB.initdb() handles ssl_mode="require" by setting ssl=True
    # which tells asyncpg to use SSL without verifying the certificate chain
    ssl_mode = qs.get("sslmode", [None])[0]
    # Default to "require" for Supabase — avoids CERTIFICATE_VERIFY_FAILED
    env_map["POSTGRES_SSL_MODE"] = ssl_mode or "require"

    # Only set if not already defined (allow explicit overrides)
    for key, value in env_map.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.debug("lightrag_env_set", extra={"key": key, "value": "***" if "PASSWORD" in key else value})

    return True


async def _get_rag(force_retry: bool = False):
    """Lazy-initialize LightRAG instance with pgvector storage. Returns None if unavailable."""
    global _rag, _rag_init_attempted, _rag_init_error

    if _rag is not None:
        return _rag

    if _rag_init_attempted and not force_retry:
        return None  # Don't retry if init already failed (unless forced)

    _rag_init_attempted = True
    _rag_init_error = None

    try:
        from lightrag import LightRAG
        from lightrag.llm.openai import openai_complete, openai_embed
        # LightRAG 1.4.15: storage params expect STRING class names, not class references
        # Validated 2026-04-22: type hint is `str`, default is "JsonKVStorage"

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            _rag_init_error = "OPENAI_API_KEY not set"
            logger.warning("lightrag_disabled", extra={"reason": _rag_init_error})
            return None

        # Inject POSTGRES_* env vars from SUPABASE_DB_URL
        # LightRAG's ClientManager.get_config() reads these automatically
        if not _inject_postgres_env_from_db_url():
            # Check if POSTGRES_* vars are already set directly
            if not os.getenv("POSTGRES_HOST"):
                _rag_init_error = "No SUPABASE_DB_URL or POSTGRES_HOST — cannot use pgvector storage"
                logger.warning("lightrag_disabled", extra={"reason": _rag_init_error})
                return None

        model = os.getenv("LIGHTRAG_MODEL", "gpt-4o-mini")

        # Still need a working_dir for LightRAG internals (temp files, logs)
        # But actual data goes to PostgreSQL now
        working_dir = os.getenv("LIGHTRAG_WORKING_DIR", "/tmp/monstruo_lightrag")
        os.makedirs(working_dir, exist_ok=True)

        # LightRAG 1.4.15 with pgvector storage (validated locally 2026-04-22):
        # - kv_storage: PGKVStorage (replaces JsonKVStorage)
        # - vector_storage: PGVectorStorage (replaces NanoVectorDBStorage)
        # - graph_storage: PGGraphStorage (replaces NetworkXStorage)
        # - doc_status_storage: PGDocStatusStorage (replaces JsonDocStatusStorage)
        # - ClientManager.get_config() reads POSTGRES_* env vars automatically
        # - Tables are auto-created by LightRAG on initialize_storages()
        rag = LightRAG(
            working_dir=working_dir,
            llm_model_func=openai_complete,
            llm_model_name=model,
            embedding_func=openai_embed,
            kv_storage="PGKVStorage",
            vector_storage="PGVectorStorage",
            graph_storage="PGGraphStorage",
            doc_status_storage="PGDocStatusStorage",
        )

        # LightRAG 1.4.15 requires explicit storage initialization
        # This creates the PostgreSQL tables if they don't exist
        await rag.initialize_storages()

        _rag = rag
        logger.info(
            "lightrag_initialized",
            extra={
                "working_dir": working_dir,
                "model": model,
                "storage": "pgvector",
                "host": os.getenv("POSTGRES_HOST", "unknown"),
                "database": os.getenv("POSTGRES_DATABASE", "unknown"),
                "workspace": os.getenv("POSTGRES_WORKSPACE", "monstruo"),
            },
        )
        return _rag

    except ImportError as ie:
        _rag_init_error = f"ImportError: {ie}"
        logger.warning("lightrag_import_failed", extra={"error": str(ie)})
        return None
    except Exception as exc:
        import traceback
        _rag_init_error = f"{type(exc).__name__}: {exc}"
        logger.error(
            "lightrag_init_failed",
            extra={"error": str(exc), "traceback": traceback.format_exc()[:500]},
        )
        return None


# ── Public API ─────────────────────────────────────────────────────


async def ingest_document(
    content: str,
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Ingest a document into the LightRAG knowledge graph.

    Args:
        content: Document text to ingest
        metadata: Optional metadata (source, type, etc.)

    Returns dict with status and details.
    """
    rag = await _get_rag(force_retry=True)
    if rag is None:
        return {
            "ingested": False,
            "reason": "lightrag_unavailable",
            "error": _rag_init_error,
        }

    try:
        await rag.ainsert(content)

        logger.info(
            "lightrag_document_ingested",
            extra={
                "content_length": len(content),
                "metadata": metadata,
            },
        )
        return {
            "ingested": True,
            "content_length": len(content),
            "metadata": metadata,
        }
    except Exception as exc:
        logger.error("lightrag_ingest_failed", extra={"error": str(exc)})
        return {"ingested": False, "error": str(exc)}


async def query_knowledge(
    query: str,
    mode: str = "hybrid",
    top_k: int = 5,
) -> dict[str, Any]:
    """
    Query the LightRAG knowledge graph.

    Args:
        query: Natural language query
        mode: Retrieval mode — "local", "global", "hybrid", or "naive"
        top_k: Max results to return

    Returns dict with results and metadata.
    """
    rag = await _get_rag(force_retry=True)
    if rag is None:
        return {
            "results": [],
            "reason": "lightrag_unavailable",
            "error": _rag_init_error,
        }

    try:
        from lightrag import QueryParam

        param = QueryParam(mode=mode, top_k=top_k)
        result = await rag.aquery(query, param=param)

        logger.info(
            "lightrag_query_complete",
            extra={
                "query_length": len(query),
                "mode": mode,
                "result_length": len(result) if result else 0,
            },
        )
        return {
            "results": result if result else "",
            "mode": mode,
            "query": query,
        }
    except Exception as exc:
        logger.error("lightrag_query_failed", extra={"error": str(exc)})
        return {"results": [], "error": str(exc)}


async def get_stats() -> dict[str, Any]:
    """Return LightRAG status for health checks."""
    rag = await _get_rag()
    if rag is None:
        return {
            "status": "unavailable",
            "reason": _rag_init_error or "not_initialized",
        }

    try:
        return {
            "status": "active",
            "storage": "pgvector",
            "host": os.getenv("POSTGRES_HOST", "unknown"),
            "workspace": os.getenv("POSTGRES_WORKSPACE", "monstruo"),
            "model": os.getenv("LIGHTRAG_MODEL", "gpt-4o-mini"),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
