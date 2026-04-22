"""
LightRAG Bridge — Knowledge Graph RAG for El Monstruo
Sprint 24 | v0.17.0-sprint24
IVD: lightrag-hku==1.4.15 (MIT, PyPI latest 2026-04-22)
CVE-2026-39413: JWT in API server only — we don't use the server.

Architecture:
  - LightRAG builds a knowledge graph from ingested documents
  - Supports dual-level retrieval: local (entity-centric) + global (theme-centric)
  - Storage: nano-vectordb (default, file-based in working_dir)
  - Embeddings: Uses OpenAI API via OPENAI_API_KEY env var (auto-detected)

API validated locally 2026-04-22:
  - LightRAG(working_dir, llm_model_func=openai_complete, llm_model_name, embedding_func=openai_embed)
  - openai_embed is an EmbeddingFunc instance (not a plain function)
  - openai_complete is a callable
  - OPENAI_API_KEY is read automatically from env by the openai SDK

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
_rag_init_error: str | None = None


async def _get_rag(force_retry: bool = False):
    """Lazy-initialize LightRAG instance. Returns None if unavailable."""
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

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            _rag_init_error = "OPENAI_API_KEY not set"
            logger.warning("lightrag_disabled", extra={"reason": _rag_init_error})
            return None

        working_dir = os.getenv("LIGHTRAG_WORKING_DIR", "/tmp/monstruo_lightrag")
        model = os.getenv("LIGHTRAG_MODEL", "gpt-4o-mini")

        os.makedirs(working_dir, exist_ok=True)

        # LightRAG 1.4.15 correct API (validated locally):
        # - llm_model_func: callable (openai_complete)
        # - llm_model_name: str (model name for the LLM)
        # - embedding_func: EmbeddingFunc instance (openai_embed)
        # - OPENAI_API_KEY is auto-read from env by the openai SDK
        rag = LightRAG(
            working_dir=working_dir,
            llm_model_func=openai_complete,
            llm_model_name=model,
            embedding_func=openai_embed,
        )

        _rag = rag
        logger.info(
            "lightrag_initialized",
            extra={
                "working_dir": working_dir,
                "model": model,
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
        working_dir = os.getenv("LIGHTRAG_WORKING_DIR", "/tmp/monstruo_lightrag")
        kg_exists = os.path.exists(
            os.path.join(working_dir, "graph_chunk_entity_relation.graphml")
        )

        return {
            "status": "active",
            "working_dir": working_dir,
            "knowledge_graph_exists": kg_exists,
            "model": os.getenv("LIGHTRAG_MODEL", "gpt-4o-mini"),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
