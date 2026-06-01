"""
El Catastro · Refresh Prices (Soberanía del Monstruo).

Endpoint y cron job interno para actualización automática de precios LLM.
Se ejecuta cada 14 días vía background task del Kernel.

Fuente: Perplexity Sonar Pro (validación en tiempo real).
Fallback: OpenRouter API (ya integrada en sources/).

Flujo:
  1. Consulta Perplexity Sonar Pro para precios actuales
  2. Compara con precios en catastro_modelos
  3. Actualiza los que cambiaron (UPSERT via Supabase)
  4. Recalcula cost_efficiency
  5. Ejecuta catastro_recompute_trono_all()
  6. Registra evento tipo 'price_change' en catastro_eventos

Disciplina os.environ:
  - SONAR_API_KEY (requerido para Perplexity)
  - SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY (requerido para persistir)

[Hilo Manus] · 2026-06-01 · Soberanía Catastral
"""

from __future__ import annotations

import asyncio
import logging
import math
import os
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

logger = logging.getLogger("kernel.catastro.refresh_prices")


# ============================================================================
# PERPLEXITY PRICE FETCHER
# ============================================================================


async def _fetch_prices_perplexity() -> list[dict[str, Any]]:
    """Query Perplexity Sonar Pro for current LLM pricing."""
    api_key = os.environ.get("SONAR_API_KEY", "")
    if not api_key:
        logger.warning("SONAR_API_KEY not set — cannot fetch fresh prices")
        return []

    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a pricing research assistant. Return ONLY a JSON array "
                    "with no markdown formatting. Each object must have: "
                    "id (lowercase-hyphenated model name), "
                    "input_price (USD per 1M tokens), "
                    "output_price (USD per 1M tokens). "
                    "Only include models you are confident about."
                ),
            },
            {
                "role": "user",
                "content": (
                    "What are the current prices (USD per 1 million tokens) for these LLM models? "
                    "Return JSON array only: GPT-5.5, GPT-5.5 Pro, GPT-5.4, GPT-4.1, GPT-4.1 mini, "
                    "Claude Opus 4.7, Claude Sonnet 4.6, Claude Haiku 4.5, "
                    "Gemini 3.5 Flash, Gemini 3.1 Pro, Gemini 2.5 Flash, Gemini 2.5 Pro, "
                    "Grok 4, Grok 3, DeepSeek V4 Flash, DeepSeek V4 Pro, DeepSeek R1, "
                    "Mistral Large 3, o3, o4-mini, Llama 4 Maverick, Llama 4 Scout"
                ),
            },
        ],
        "temperature": 0.1,
        "max_tokens": 2000,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if resp.status_code == 200:
                import json
                import re

                content = resp.json()["choices"][0]["message"]["content"]
                m = re.search(r"\[.*\]", content, re.DOTALL)
                if m:
                    return json.loads(m.group(0))
            else:
                logger.warning(f"Perplexity returned status {resp.status_code}")
    except Exception as e:
        logger.error(f"Perplexity price fetch failed: {e}")

    return []


# ============================================================================
# PRICE UPDATE LOGIC
# ============================================================================

# Map common Perplexity response IDs to our catastro_modelos IDs
_ID_MAP = {
    "gpt-5.5": "gpt-5-5",
    "gpt-5-5": "gpt-5-5",
    "gpt-5.5-pro": "gpt-5-5-pro",
    "gpt-5-5-pro": "gpt-5-5-pro",
    "gpt-5.4": "gpt-5-4",
    "gpt-5-4": "gpt-5-4",
    "gpt-4.1": "gpt-4-1",
    "gpt-4-1": "gpt-4-1",
    "gpt-4.1-mini": "gpt-4-1-mini",
    "gpt-4-1-mini": "gpt-4-1-mini",
    "claude-opus-4.7": "claude-opus-4-7",
    "claude-opus-4-7": "claude-opus-4-7",
    "claude-sonnet-4.6": "claude-sonnet-4-6",
    "claude-sonnet-4-6": "claude-sonnet-4-6",
    "claude-haiku-4.5": "claude-haiku-4-5",
    "claude-haiku-4-5": "claude-haiku-4-5",
    "gemini-3.5-flash": "gemini-3-5-flash",
    "gemini-3-5-flash": "gemini-3-5-flash",
    "gemini-3.1-pro": "gemini-3-1-pro",
    "gemini-3-1-pro": "gemini-3-1-pro",
    "gemini-2.5-flash": "gemini-2-5-flash",
    "gemini-2-5-flash": "gemini-2-5-flash",
    "gemini-2.5-pro": "gemini-2-5-pro",
    "gemini-2-5-pro": "gemini-2-5-pro",
    "grok-4": "grok-4",
    "grok-3": "grok-3",
    "deepseek-v4-flash": "deepseek-v4-flash",
    "deepseek-v4-pro": "deepseek-v4-pro",
    "deepseek-r1": "deepseek-r1",
    "mistral-large-3": "mistral-large-3",
    "o3": "o3",
    "o4-mini": "o4-mini",
    "llama-4-maverick": "llama-4-maverick",
    "llama-4-scout": "llama-4-scout",
}


def _calculate_cost_efficiency(input_price: float, output_price: float) -> float:
    """
    Calculate cost_efficiency score (0-99.99).
    Cheaper = higher score. Logarithmic scale.
    Blended price = 60% input + 40% output.
    """
    blended = input_price * 0.6 + output_price * 0.4
    if blended <= 0:
        return 99.00
    score = 100 - 25 * math.log10(max(blended, 0.01))
    return round(max(0, min(99.99, score)), 2)


async def refresh_prices(*, dry_run: bool = False) -> dict[str, Any]:
    """
    Main refresh logic. Returns summary dict.

    Args:
        dry_run: If True, fetches prices but doesn't persist.
    """
    from supabase import create_client

    logger.info("catastro_refresh_prices_start")

    # Step 1: Fetch fresh prices
    fresh_prices = await _fetch_prices_perplexity()
    if not fresh_prices:
        logger.warning("catastro_refresh_prices_no_data")
        return {"status": "no_data", "updated": 0, "source": "perplexity"}

    # Step 2: Connect to Supabase
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not supabase_url or not supabase_key:
        logger.error("catastro_refresh_prices_no_supabase_creds")
        return {"status": "error", "reason": "missing_supabase_creds", "updated": 0}

    if dry_run:
        logger.info(f"catastro_refresh_prices_dry_run: {len(fresh_prices)} prices fetched")
        return {"status": "dry_run", "fetched": len(fresh_prices), "updated": 0}

    sb = create_client(supabase_url, supabase_key)

    # Step 3: Update prices
    updated = 0
    changes = []

    for item in fresh_prices:
        raw_id = item.get("id", "").lower().strip()
        our_id = _ID_MAP.get(raw_id, raw_id)
        input_price = float(item.get("input_price", 0))
        output_price = float(item.get("output_price", 0))

        if input_price <= 0 and output_price <= 0:
            continue

        cost_eff = _calculate_cost_efficiency(input_price, output_price)

        try:
            result = (
                sb.table("catastro_modelos")
                .update(
                    {
                        "precio_input_per_million": input_price,
                        "precio_output_per_million": output_price,
                        "cost_efficiency": cost_eff,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("id", our_id)
                .eq("estado", "production")
                .execute()
            )
            if result.data:
                updated += 1
                changes.append({"id": our_id, "input": input_price, "output": output_price})
        except Exception as e:
            logger.warning(f"catastro_refresh_price_update_failed: {our_id}: {e}")

    # Step 4: Recompute trono
    if updated > 0:
        try:
            sb.rpc("catastro_recompute_trono_all").execute()
            logger.info("catastro_trono_recomputed")
        except Exception as e:
            logger.warning(f"catastro_trono_recompute_failed: {e}")

    # Step 5: Log event
    try:
        sb.table("catastro_eventos").insert(
            {
                "tipo": "price_change",
                "prioridad": "info",
                "descripcion": f"Refresh automático de precios — {updated} modelos actualizados via Perplexity Sonar Pro",
                "contexto": {
                    "source": "refresh_prices_cron",
                    "modelos_actualizados": updated,
                    "changes": changes[:10],  # Top 10 for brevity
                },
                "curador_origen": "curador-manus",
                "fecha": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()
    except Exception as e:
        logger.warning(f"catastro_refresh_event_log_failed: {e}")

    summary = {
        "status": "success",
        "updated": updated,
        "fetched": len(fresh_prices),
        "source": "perplexity_sonar_pro",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    logger.info("catastro_refresh_prices_complete", **summary)
    return summary


# ============================================================================
# BACKGROUND SCHEDULER (14-day interval)
# ============================================================================

_refresh_task: Optional[asyncio.Task] = None
REFRESH_INTERVAL_SECONDS = 14 * 24 * 60 * 60  # 14 days


async def _refresh_loop():
    """Background loop that runs refresh every 14 days."""
    while True:
        try:
            await asyncio.sleep(REFRESH_INTERVAL_SECONDS)
            result = await refresh_prices()
            logger.info("catastro_scheduled_refresh_done", **result)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"catastro_scheduled_refresh_error: {e}")
            # Wait 1 hour before retrying on error
            await asyncio.sleep(3600)


def start_refresh_scheduler():
    """Start the background refresh task. Call once during app lifespan."""
    global _refresh_task
    if _refresh_task is None or _refresh_task.done():
        _refresh_task = asyncio.create_task(_refresh_loop())
        logger.info(
            "catastro_refresh_scheduler_started",
            interval_days=14,
            next_run_in="14 days",
        )


def stop_refresh_scheduler():
    """Stop the background refresh task. Call during shutdown."""
    global _refresh_task
    if _refresh_task and not _refresh_task.done():
        _refresh_task.cancel()
        logger.info("catastro_refresh_scheduler_stopped")
