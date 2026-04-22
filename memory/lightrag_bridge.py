"""
LightRAG Bridge — Knowledge Graph RAG for El Monstruo
Sprint 23 | v0.16.0-sprint23
IVD: lightrag-hku==1.4.15 (MIT, PyPI latest 2026-04-22)
CVE-2026-39413: JWT in API server only — we don't use the server.

Architecture:
  - LightRAG builds a knowledge graph from ingested documents
  - Supports dual-level retrieval: local (entity-centric) + global (theme-centric)
  - Storage: nano-vectordb (default) or pgvector (via Supabase)
  - Embeddings: Uses OpenAI-compatible API (routed through our existing config)

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

logger = logging.getLogger("monstruo.memory.lightrag")

# ── Lazy singleton ────────────────────────────────────────────────────
_rag = None
_rag_init_attempted = False


async def _get_rag(force_retry: bool = False):
    """Lazy-initialize LightRAG instance. Returns None if unavailable."""
    global _rag, _rag_init_attempted

    if _rag is not None:
        return _rag

    if _rag_init_attempted and not force_retry:
        return None  # Don't retry if init already failed (unless forced)

    _rag_init_attempted = True

    try:
        from lightrag import LightRAG, QueryParam
        from lightrag.llm.openai import openai_complete, openai_embed

        working_dir = os.getenv("LIGHTRAG_WORKING_DIR", "/tmp/monstruo_lightrag")
        os.makedirs(working_dir, exist_ok=True)

        # Use the same OpenAI-compatible endpoint as the kernel router
        # This routes through our existing model configuration
        api_key = os.getenv("OPENAI_API_KEY", "")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("LIGHTRAG_MODEL", "gpt-4o-mini")
        embed_model = os.getenv("LIGHTRAG_EMBED_MODEL", "text-embedding-3-small")

        if not api_key:
            logger.warning("lightrag_disabled", reason="OPENAI_API_KEY not set")
            return None

        rag = LightRAG(
            working_dir=working_dir,
            llm_model_func=openai_complete,
            llm_model_name=model,
            llm_model_kwargs={
                "api_key": api_key,
                "base_url": api_base,
            },
            embedding_func=openai_embed,
            embedding_model_name=embed_model,
            embedding_model_kwargs={
                "api_key": api_key,
                "base_url": api_base,
            },
        )

        _rag = rag
        logger.info(
            "lightrag_initialized",
            extra={
                "working_dir": working_dir,
                "model": model,
                "embed_model": embed_model,
            },
        )
        return _rag

    except ImportError as ie:
        logger.warning("lightrag_import_failed", extra={"error": str(ie), "detail": "lightrag-hku package not installed or missing dependency"})
        return None
    except Exception as exc:
        import traceback
        logger.error("lightrag_init_failed", extra={"error": str(exc), "traceback": traceback.format_exc()[:500]})
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
    rag = await _get_rag(force_retry=True)  # Retry on explicit calls
    if rag is None:
        return {"ingested": False, "reason": "lightrag_unavailable"}

    try:
        # LightRAG's insert method processes the document and builds the KG
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
        mode: Retrieval mode \u2014 "local", "global", "hybrid", or "naive"
        top_k: Max results to return

    Returns dict with results and metadata.
    """
    rag = await _get_rag(force_retry=True)  # Retry on explicit calls
    if rag is None:
        return {"results": [], "reason": "lightrag_unavailable"}

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
        return {"status": "unavailable", "reason": "not_initialized"}

    try:
        working_dir = os.getenv("LIGHTRAG_WORKING_DIR", "/tmp/monstruo_lightrag")
        # Check if knowledge graph files exist
        kg_exists = os.path.exists(os.path.join(working_dir, "graph_chunk_entity_relation.graphml"))

        return {
            "status": "active",
            "working_dir": working_dir,
            "knowledge_graph_exists": kg_exists,
            "model": os.getenv("LIGHTRAG_MODEL", "gpt-4o-mini"),
            "embed_model": os.getenv("LIGHTRAG_EMBED_MODEL", "text-embedding-3-small"),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
