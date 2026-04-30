"""
El Monstruo — Context Reranker (ZeroEntropy Zerank-2)
=====================================================
Sprint 45: Context Distillation via the #1 reranker in the world.

Purpose: After all retrievers complete (memories, MemPalace, Mem0, LightRAG,
knowledge graph), this module reranks ALL candidate text chunks against the
user's query and returns only the top-N most relevant ones.

Result: System prompt shrinks from ~80K tokens to ~8-10K tokens, reducing
LLM prefill time from 30-45s to 2-4s.

Architecture:
    retrievers → [reranker.distill_context()] → system_prompt injection

Uses ZeroEntropy Zerank-2 API:
    - #1 ELO on agentset.ai benchmark (1638 ELO, March 2026)
    - 60ms latency (subsecond guaranteed)
    - Instruction-following (can prioritize personal memories)
    - $0.025/1M tokens

Fallback: If API is unavailable, falls back to score-based sorting (no rerank).
"""

from __future__ import annotations

import os
import time
from typing import Any

import httpx
import structlog

logger = structlog.get_logger("kernel.reranker")

# ── Configuration ────────────────────────────────────────────────────
ZEROENTROPY_API_KEY = os.environ.get("ZEROENTROPY_API_KEY", "")
ZEROENTROPY_API_URL = "https://api.zeroentropy.dev/v1/models/rerank"
MODEL = "zerank-2"
DEFAULT_TOP_N = 5  # Return top 5 most relevant chunks
TIMEOUT_SECONDS = 2.0  # Hard timeout — never block more than 2s
LATENCY_MODE = "fast"  # Guaranteed subsecond inference


# ── Singleton HTTP client (connection pooling) ───────────────────────
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    """Lazy-init a persistent async HTTP client with connection pooling."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(TIMEOUT_SECONDS, connect=1.0),
            http2=True,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
    return _client


# ── Public API ───────────────────────────────────────────────────────


async def distill_context(
    query: str,
    candidates: list[dict[str, Any]],
    top_n: int = DEFAULT_TOP_N,
    instruction: str | None = None,
) -> list[dict[str, Any]]:
    """
    Rerank candidate context chunks and return only the top-N most relevant.

    Args:
        query: The user's message/question.
        candidates: List of dicts, each with at least a "content" key.
                    May also have "score", "type", "source", etc.
        top_n: How many top results to return.
        instruction: Optional instruction for the reranker (e.g.,
                     "Prioritize personal memories over general knowledge").

    Returns:
        The top-N candidates, reordered by relevance. Each dict gets an
        additional "rerank_score" field (0.0-1.0).

    Fallback:
        If the API is unavailable or errors, returns candidates sorted by
        their original "score" field (no reranking applied).
    """
    if not candidates:
        return []

    if len(candidates) <= top_n:
        # No need to rerank if we already have fewer than top_n
        return candidates

    if not ZEROENTROPY_API_KEY:
        logger.warning("reranker_no_api_key", msg="ZEROENTROPY_API_KEY not set, using score fallback")
        return _fallback_sort(candidates, top_n)

    # Build the documents list for the API
    documents = []
    for c in candidates:
        text = c.get("content", "")
        if not text:
            text = str(c)
        documents.append(text)

    # Build the query with optional instruction prefix
    rerank_query = query
    if instruction:
        rerank_query = f"{instruction}\n\nQuery: {query}"

    start = time.monotonic()

    try:
        client = _get_client()
        response = await client.post(
            ZEROENTROPY_API_URL,
            headers={
                "Authorization": f"Bearer {ZEROENTROPY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "query": rerank_query,
                "documents": documents,
                "top_n": top_n,
                "latency": LATENCY_MODE,
            },
        )

        elapsed_ms = (time.monotonic() - start) * 1000

        if response.status_code != 200:
            logger.warning(
                "reranker_api_error",
                status=response.status_code,
                body=response.text[:200],
                elapsed_ms=elapsed_ms,
            )
            return _fallback_sort(candidates, top_n)

        data = response.json()
        results = data.get("results", [])

        # Map back to original candidates with rerank scores
        reranked = []
        for r in results:
            idx = r["index"]
            score = r["relevance_score"]
            candidate = candidates[idx].copy()
            candidate["rerank_score"] = score
            reranked.append(candidate)

        logger.info(
            "reranker_success",
            query_len=len(query),
            candidates_in=len(candidates),
            candidates_out=len(reranked),
            top_score=reranked[0]["rerank_score"] if reranked else 0,
            elapsed_ms=round(elapsed_ms, 1),
            e2e_latency=data.get("e2e_latency"),
            inference_latency=data.get("inference_latency"),
            total_tokens=data.get("total_tokens"),
        )

        return reranked

    except httpx.TimeoutException:
        elapsed_ms = (time.monotonic() - start) * 1000
        logger.warning("reranker_timeout", elapsed_ms=elapsed_ms, timeout=TIMEOUT_SECONDS)
        return _fallback_sort(candidates, top_n)

    except Exception as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        logger.warning("reranker_exception", error=str(e), elapsed_ms=elapsed_ms)
        return _fallback_sort(candidates, top_n)


# ── Fallback: sort by existing score ─────────────────────────────────


def _fallback_sort(candidates: list[dict[str, Any]], top_n: int) -> list[dict[str, Any]]:
    """Sort candidates by their pre-existing score (from vector search)."""
    sorted_candidates = sorted(
        candidates,
        key=lambda c: c.get("score", c.get("rerank_score", 0)),
        reverse=True,
    )
    return sorted_candidates[:top_n]
