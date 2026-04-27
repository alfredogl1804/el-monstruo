"""
LightRAG Bridge — Knowledge Graph RAG for El Monstruo
Sprint 31 | v0.24.0-sprint31

IVD: lightrag-hku==1.4.15 (MIT, PyPI latest 2026-04-22)
CVE-2026-39413: JWT in API server only — we don't use the server.

Architecture:
  - LightRAG builds a knowledge graph from ingested documents
  - Supports dual-level retrieval: local (entity-centric) + global (theme-centric)
  - Storage: pgvector via Supabase (Sprint 25 — migrated from /tmp file-based)
  - LLM: gpt-4.1-mini via OPENAI_API_KEY (fast, cheap, good quality)
  - Embeddings: OpenAI text-embedding-3-small via OPENAI_API_KEY (stable, MTEB 62.26)

Sprint 31 Migration History:
  - v1: gpt-4o-mini for both LLM and embeddings → low quality extraction
  - v2: Gemini 2.5 Flash (LLM) + gemini-embedding-001 → embed bug (vector mismatch)
  - v3: Gemini 2.5 Flash (LLM) + OpenAI embeddings → embed works, LLM too slow
  - v4: Gemini ingest + gpt-4.1-mini queries → ingest still too slow (2min+)
  - v5 (CURRENT): gpt-4.1-mini for everything + OpenAI embeddings
    → Fast ingest (<10s), fast queries (<5s), good entity extraction
    → $0.10/$0.40 per MTok — cheaper than gpt-4o-mini
    → Compatible with existing pgvector data (text-embedding-3-small tables)

Sprint 25 Migration (Storage):
  - BEFORE: working_dir=/tmp/monstruo_lightrag (NanoVectorDB + NetworkX + JSON)
    → Data LOST on every Railway deploy (ephemeral filesystem)
  - AFTER: PGKVStorage + PGVectorStorage + PGDocStatusStorage (persistent in Supabase)
    → NetworkXStorage for graph (no Apache AGE on Supabase)
    → Graph persisted to PostgreSQL via pg_graph_storage.py (Sprint 31)
  - Connection: LightRAG's ClientManager reads POSTGRES_* env vars automatically

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
from urllib.parse import parse_qs, urlparse

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
    ssl_mode = qs.get("sslmode", [None])[0]
    env_map["POSTGRES_SSL_MODE"] = ssl_mode or "require"

    # Only set if not already defined (allow explicit overrides)
    for key, value in env_map.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.debug("lightrag_env_set", extra={"key": key, "value": "***" if "PASSWORD" in key else value})

    return True


async def _get_rag(force_retry: bool = False):
    """Lazy-initialize LightRAG instance with pgvector storage and OpenAI models."""
    global _rag, _rag_init_attempted, _rag_init_error

    if _rag is not None:
        return _rag

    if _rag_init_attempted and not force_retry:
        return None  # Don't retry if init already failed (unless forced)

    _rag_init_attempted = True
    _rag_init_error = None

    try:
        # ── SSL fix for Supabase (self-signed cert chain) ──────────────
        import ssl as _ssl

        from lightrag import LightRAG
        from lightrag.kg.postgres_impl import PostgreSQLDB

        # ── Import OpenAI model functions ──────────────────────────────
        # LLM: gpt-4.1-mini — fast, cheap, good quality for entity extraction
        # Embeddings: text-embedding-3-small — stable, proven, compatible
        from lightrag.llm.openai import openai_complete, openai_embed

        _original_create_ssl = PostgreSQLDB._create_ssl_context

        def _patched_create_ssl(self_db):
            if self_db.ssl_mode and self_db.ssl_mode.lower() in ("require", "prefer", "allow"):
                ctx = _ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = _ssl.CERT_NONE
                return ctx
            return _original_create_ssl(self_db)

        PostgreSQLDB._create_ssl_context = _patched_create_ssl
        logger.info("lightrag_ssl_patched", extra={"mode": "no-verify for require/prefer/allow"})

        # ── Validate OPENAI_API_KEY ────────────────────────────────────
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if not openai_key:
            _rag_init_error = "OPENAI_API_KEY not set — required for LightRAG"
            logger.warning("lightrag_disabled", extra={"reason": _rag_init_error})
            return None

        # ── Inject POSTGRES_* env vars from SUPABASE_DB_URL ──────────
        if not _inject_postgres_env_from_db_url():
            if not os.getenv("POSTGRES_HOST"):
                _rag_init_error = "No SUPABASE_DB_URL or POSTGRES_HOST — cannot use pgvector storage"
                logger.warning("lightrag_disabled", extra={"reason": _rag_init_error})
                return None

        # ── Model configuration ──────────────────────────────────────
        # gpt-4.1-mini: $0.10/$0.40 per MTok, fast (<5s), good extraction
        # text-embedding-3-small: $0.02/MTok, 1536d, stable
        llm_model = os.getenv("LIGHTRAG_MODEL", "gpt-4.1-mini")
        embedding_model = os.getenv("LIGHTRAG_EMBEDDING_MODEL", "text-embedding-3-small")

        # Still need a working_dir for LightRAG internals (temp files, logs)
        working_dir = os.getenv("LIGHTRAG_WORKING_DIR", "/tmp/monstruo_lightrag")
        os.makedirs(working_dir, exist_ok=True)

        # ── Initialize LightRAG ──────────────────────────────────────
        rag = LightRAG(
            working_dir=working_dir,
            llm_model_func=openai_complete,
            llm_model_name=llm_model,
            embedding_func=openai_embed,
            kv_storage="PGKVStorage",
            vector_storage="PGVectorStorage",
            graph_storage="NetworkXStorage",  # No AGE extension on Supabase
            doc_status_storage="PGDocStatusStorage",
        )

        # LightRAG 1.4.15 requires explicit storage initialization
        await rag.initialize_storages()

        # ── Sprint 31: Restore graph from PostgreSQL ─────────────────
        # NetworkXStorage saves to filesystem which is ephemeral on Railway.
        # We restore the graph from PG on startup so it survives deploys.
        try:
            from memory.pg_graph_storage import load_graph_from_pg

            pg_graph = await load_graph_from_pg(graph_id="main")
            if pg_graph is not None:
                # Inject the restored graph into NetworkXStorage
                graph_storage = rag.chunk_entity_relation_graph
                graph_storage._graph = pg_graph
                # Also write to filesystem so NetworkXStorage's file-based sync works
                from lightrag.kg.networkx_impl import NetworkXStorage
                NetworkXStorage.write_nx_graph(
                    pg_graph, graph_storage._graphml_xml_file, graph_storage.workspace
                )
                logger.info(
                    "pg_graph_restored_to_networkx",
                    extra={
                        "nodes": pg_graph.number_of_nodes(),
                        "edges": pg_graph.number_of_edges(),
                    },
                )
            else:
                logger.info("pg_graph_empty_starting_fresh")
        except Exception as exc:
            logger.warning("pg_graph_restore_failed", extra={"error": str(exc)})
            # Non-fatal: LightRAG will work with empty graph

        _rag = rag
        logger.info(
            "lightrag_initialized",
            extra={
                "working_dir": working_dir,
                "llm_model": llm_model,
                "embedding_model": embedding_model,
                "storage": "pgvector",
                "graph_storage": "NetworkX + PG persistence",
                "host": os.getenv("POSTGRES_HOST", "unknown"),
                "database": os.getenv("POSTGRES_DATABASE", "unknown"),
                "workspace": os.getenv("POSTGRES_WORKSPACE", "monstruo"),
                "provider": "openai",
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

        # ── Sprint 31: Persist graph to PostgreSQL after ingest ──────
        try:
            from memory.pg_graph_storage import save_graph_to_pg

            graph_storage = rag.chunk_entity_relation_graph
            await save_graph_to_pg(graph_storage._graph, graph_id="main")
        except Exception as pg_exc:
            logger.warning("pg_graph_save_after_ingest_failed", extra={"error": str(pg_exc)})
            # Non-fatal: graph is still in memory and filesystem

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
            "llm_model": os.getenv("LIGHTRAG_MODEL", "gpt-4.1-mini"),
            "embedding_model": os.getenv("LIGHTRAG_EMBEDDING_MODEL", "text-embedding-3-small"),
            "provider": "openai",
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
