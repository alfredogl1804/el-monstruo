"""
El Monstruo — Web Search Tool (Perplexity Sonar API)
=====================================================
Gives El Monstruo the ability to research the internet in real-time.

Uses Perplexity's sonar-reasoning-pro model for grounded, cited answers.
Falls back to sonar-pro then sonar (smaller, faster) if primary fails.

Env vars required:
    SONAR_API_KEY — Perplexity API key

Sprint 2 — 2026-04-15
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import structlog

logger = structlog.get_logger("tools.web_search")

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

# Models validated on PyPI/docs 2026-04-15
SONAR_MODELS = ["sonar-reasoning-pro", "sonar-pro", "sonar"]


async def web_search(
    query: str,
    context: str = "",
    model: str = "sonar-reasoning-pro",
    max_tokens: int = 2048,
    temperature: float = 0.2,
) -> dict[str, Any]:
    """
    Search the web using Perplexity Sonar API.

    Args:
        query: The search query or research question
        context: Optional context to help Perplexity understand the query better
        model: Perplexity model to use (sonar-reasoning-pro, sonar-pro, or sonar)
        max_tokens: Maximum tokens in response
        temperature: Response temperature (lower = more factual)

    Returns:
        dict with keys: answer, citations, model_used, tokens_used, error
    """
    api_key = os.environ.get("SONAR_API_KEY")
    if not api_key:
        return {
            "answer": "",
            "citations": [],
            "model_used": "",
            "tokens_used": 0,
            "error": "SONAR_API_KEY not set. Cannot search the web.",
        }

    # Build the message
    system_msg = (
        "You are a research assistant for El Monstruo, a sovereign AI system. "
        "Provide accurate, well-sourced answers. Always cite your sources. "
        "Be concise but thorough. Respond in the same language as the query."
    )
    if context:
        system_msg += f"\n\nAdditional context: {context}"

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": query},
    ]

    # Try primary model, fallback to secondary
    models_to_try = [model] if model in SONAR_MODELS else SONAR_MODELS
    if model == "sonar-reasoning-pro":
        models_to_try = ["sonar-reasoning-pro", "sonar-pro", "sonar"]
    elif model == "sonar-pro":
        models_to_try = ["sonar-pro", "sonar"]
    elif model == "sonar":
        models_to_try = ["sonar"]

    last_error = None
    for m in models_to_try:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    PERPLEXITY_API_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": m,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    },
                )
                response.raise_for_status()
                data = response.json()

            answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = data.get("citations", [])
            usage = data.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)

            logger.info(
                "web_search_success",
                model=m,
                query_preview=query[:80],
                citations_count=len(citations),
                tokens=total_tokens,
            )

            return {
                "answer": answer,
                "citations": citations,
                "model_used": m,
                "tokens_used": total_tokens,
                "error": None,
            }

        except Exception as e:
            last_error = str(e)
            logger.warning("web_search_failed", model=m, error=last_error)
            continue

    return {
        "answer": "",
        "citations": [],
        "model_used": "",
        "tokens_used": 0,
        "error": f"All models failed. Last error: {last_error}",
    }


async def multi_search(
    queries: list[str],
    context: str = "",
) -> list[dict[str, Any]]:
    """
    Execute multiple searches in sequence (not parallel to respect rate limits).

    Args:
        queries: List of search queries
        context: Shared context for all queries

    Returns:
        List of search results
    """
    results = []
    for q in queries:
        result = await web_search(q, context=context)
        results.append(result)
    return results
