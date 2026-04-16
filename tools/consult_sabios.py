"""
El Monstruo — Consult Sabios Tool (Multi-Model AI Consultation)
================================================================
Gives El Monstruo the ability to consult the 6 Sabios (wise AIs)
and synthesize their answers into a unified response.

The 6 Sabios (validated 2026-04-15):
    1. GPT-5.4 (OpenAI) — Architect, strategic reasoning
    2. Claude claude-sonnet-4-20250514 (Anthropic) — Auditor, careful analysis
    3. Gemini 2.5 Flash (Google) — Cartographer, technical mapping
    4. Grok (xAI) — Red team, adversarial thinking
    5. DeepSeek R1 (via OpenRouter) — Normalizer, structured data
    6. Perplexity sonar-pro — Verifier, real-time web grounding

Each sabio is called via its native SDK. Falls back gracefully
if any sabio is unavailable.

Env vars required:
    OPENAI_API_KEY — GPT-5.4
    ANTHROPIC_API_KEY — Claude
    GEMINI_API_KEY — Gemini
    XAI_API_KEY — Grok
    OPENROUTER_API_KEY — DeepSeek R1 via OpenRouter
    SONAR_API_KEY — Perplexity

Sprint 2 — 2026-04-15
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Optional

import httpx
import structlog

logger = structlog.get_logger("tools.consult_sabios")


# ── Sabio Definitions ─────────────────────────────────────────────────

SABIOS = {
    "gpt54": {
        "name": "GPT-5.4",
        "role": "Arquitecto estratégico",
        "provider": "openai",
        "model": "gpt-5.4",
        "env_key": "OPENAI_API_KEY",
    },
    "claude": {
        "name": "Claude Sonnet 4.6",  # validated 2026-04-15
        "role": "Auditor analítico",
        "provider": "anthropic",
        "model": "claude-sonnet-4-6",  # validated 2026-04-15 — was claude-sonnet-4-20250514 (deprecated)
        "env_key": "ANTHROPIC_API_KEY",
    },
    "gemini": {
        "name": "Gemini 2.5 Flash",
        "role": "Cartógrafo técnico",
        "provider": "google",
        "model": "gemini-2.5-flash",
        "env_key": "GEMINI_API_KEY",
    },
    "grok": {
        "name": "Grok 4.20",  # validated 2026-04-15
        "role": "Red team adversarial",
        "provider": "xai",
        "model": "grok-4.20",  # validated 2026-04-15 — was grok-3 (over 1 year old)
        "env_key": "XAI_API_KEY",
    },
    "deepseek": {
        "name": "DeepSeek R1",
        "role": "Normalizador estructurado",
        "provider": "openrouter",
        "model": "deepseek/deepseek-r1",
        "env_key": "OPENROUTER_API_KEY",
    },
    "perplexity": {
        "name": "Perplexity Sonar Pro",
        "role": "Verificador en tiempo real",
        "provider": "perplexity",
        "model": "sonar-pro",
        "env_key": "SONAR_API_KEY",
    },
}


# ── Individual Sabio Callers ──────────────────────────────────────────

async def _call_openai(model: str, system: str, user: str, api_key: str) -> str:
    """Call OpenAI-compatible API (GPT-5.4)."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "max_tokens": 2048, "temperature": 0.3},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _call_anthropic(model: str, system: str, user: str, api_key: str) -> str:
    """Call Anthropic API (Claude)."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": model, "system": system, "messages": [{"role": "user", "content": user}], "max_tokens": 2048, "temperature": 0.3},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]


async def _call_google(model: str, system: str, user: str, api_key: str) -> str:
    """Call Google Gemini API."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "system_instruction": {"parts": [{"text": system}]},
                "contents": [{"parts": [{"text": user}]}],
                "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.3},
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def _call_xai(model: str, system: str, user: str, api_key: str) -> str:
    """Call xAI Grok API (OpenAI-compatible)."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "max_tokens": 2048, "temperature": 0.3},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _call_openrouter(model: str, system: str, user: str, api_key: str) -> str:
    """Call OpenRouter API (DeepSeek R1)."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "max_tokens": 2048, "temperature": 0.3},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _call_perplexity(model: str, system: str, user: str, api_key: str) -> str:
    """Call Perplexity API (sonar-pro)."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "max_tokens": 2048, "temperature": 0.2},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# Provider → caller mapping
_CALLERS = {
    "openai": _call_openai,
    "anthropic": _call_anthropic,
    "google": _call_google,
    "xai": _call_xai,
    "openrouter": _call_openrouter,
    "perplexity": _call_perplexity,
}


# ── Main Consultation Function ────────────────────────────────────────

async def _consult_single_sabio(
    sabio_id: str,
    sabio: dict[str, str],
    prompt: str,
    context: str,
) -> dict[str, Any]:
    """Consult a single sabio and return its response."""
    api_key = os.environ.get(sabio["env_key"])
    if not api_key:
        return {
            "sabio": sabio["name"],
            "role": sabio["role"],
            "response": "",
            "error": f"{sabio['env_key']} not set",
            "latency_ms": 0,
        }

    system_prompt = (
        f"Eres {sabio['name']}, uno de los 6 Sabios de El Monstruo. "
        f"Tu rol es: {sabio['role']}. "
        f"Responde de manera concisa, precisa y fundamentada. "
        f"Responde en el mismo idioma que la pregunta."
    )
    if context:
        system_prompt += f"\n\nContexto adicional: {context}"

    caller = _CALLERS.get(sabio["provider"])
    if not caller:
        return {
            "sabio": sabio["name"],
            "role": sabio["role"],
            "response": "",
            "error": f"Unknown provider: {sabio['provider']}",
            "latency_ms": 0,
        }

    start = time.monotonic()
    try:
        response = await caller(sabio["model"], system_prompt, prompt, api_key)
        latency = (time.monotonic() - start) * 1000

        logger.info(
            "sabio_consulted",
            sabio=sabio["name"],
            model=sabio["model"],
            latency_ms=round(latency),
            response_len=len(response),
        )

        return {
            "sabio": sabio["name"],
            "role": sabio["role"],
            "response": response,
            "error": None,
            "latency_ms": round(latency),
        }

    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        logger.warning("sabio_failed", sabio=sabio["name"], error=str(e))
        return {
            "sabio": sabio["name"],
            "role": sabio["role"],
            "response": "",
            "error": str(e),
            "latency_ms": round(latency),
        }


async def consult_sabios(
    prompt: str,
    context: str = "",
    sabios: Optional[list[str]] = None,
    parallel: bool = True,
) -> dict[str, Any]:
    """
    Consult the 6 Sabios (or a subset) and return their responses.
    
    Args:
        prompt: The question or task for the sabios
        context: Additional context to help them respond
        sabios: List of sabio IDs to consult (default: all 6)
        parallel: Whether to consult in parallel (True) or sequential (False)
    
    Returns:
        dict with keys: responses (list), synthesis, total_latency_ms, errors
    """
    # Select which sabios to consult
    sabio_ids = sabios or list(SABIOS.keys())
    selected = {sid: SABIOS[sid] for sid in sabio_ids if sid in SABIOS}

    if not selected:
        return {
            "responses": [],
            "synthesis": "",
            "total_latency_ms": 0,
            "errors": ["No valid sabios selected"],
        }

    start = time.monotonic()

    # Consult sabios
    if parallel:
        tasks = [
            _consult_single_sabio(sid, sabio, prompt, context)
            for sid, sabio in selected.items()
        ]
        responses = await asyncio.gather(*tasks)
    else:
        responses = []
        for sid, sabio in selected.items():
            resp = await _consult_single_sabio(sid, sabio, prompt, context)
            responses.append(resp)

    total_latency = (time.monotonic() - start) * 1000

    # Collect successful responses and errors
    successful = [r for r in responses if r["response"] and not r["error"]]
    errors = [f"{r['sabio']}: {r['error']}" for r in responses if r["error"]]

    # Build synthesis (simple aggregation — the kernel's execute node can do deeper synthesis)
    synthesis = ""
    if successful:
        synthesis_parts = []
        for r in successful:
            synthesis_parts.append(f"**{r['sabio']}** ({r['role']}):\n{r['response']}")
        synthesis = "\n\n---\n\n".join(synthesis_parts)

    logger.info(
        "sabios_consultation_complete",
        total_consulted=len(selected),
        successful=len(successful),
        failed=len(errors),
        total_latency_ms=round(total_latency),
    )

    return {
        "responses": list(responses),
        "synthesis": synthesis,
        "total_latency_ms": round(total_latency),
        "successful_count": len(successful),
        "failed_count": len(errors),
        "errors": errors,
    }
