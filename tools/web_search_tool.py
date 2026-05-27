"""
El Monstruo — Web Search Tool (DAN P0.5 wrapper)
================================================
Thin wrapper sobre `tools.web_search.web_search()` que añade lo que el DAN
exige y la versión base no entrega:

    - `latency_ms` medido alrededor de la llamada.
    - `cost_usd` calculado desde `tokens_used` + pricing del catálogo
      (`config/model_catalog.py`). Pricing es **input/output USD por 1M tokens**.
      Usamos un blended cost asumiendo split 50/50 in/out porque la respuesta
      Sonar no descompone tokens_in vs tokens_out (usage.total_tokens).
      Marcado NO VERIFICADO: el split exacto debe ajustarse cuando Perplexity
      exponga `prompt_tokens`/`completion_tokens` por separado.
    - `results: list[{url, citation_id, title, snippet}]` mapeado desde
      `citations` (URLs). title/snippet quedan en None cuando Sonar no los trae
      (no inventar).
    - Cost ledger: persiste cada query en la tabla `run_costs` vía
      `kernel.finops.FinOpsController.record_run_cost(...)` (ya existente).
      No inventa tabla nueva (DSC-G-004 anti-duplicación).

Anti-duplicación (DSC-G-004): NO reescribe `web_search()`, solo lo envuelve.

Sprint DAN — P0.5 — 2026-05-27 — Manus E1
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Optional

import structlog

from tools.web_search import web_search as _base_web_search

logger = structlog.get_logger("tools.web_search_tool")


def _compute_cost_usd(
    *, model_used: str, tokens_used: int
) -> tuple[float, str]:
    """
    Calcula cost_usd a partir de tokens_used y el pricing del model_catalog.

    Pricing en `config/model_catalog.py` está en **USD por 1M tokens**
    (verificado: sonar-reasoning-pro = {input: 2.00, output: 8.00}).

    Como Sonar devuelve `usage.total_tokens` sin descomponer in/out, usamos
    un blended cost = total_tokens × ((input + output) / 2) / 1_000_000.
    Cuando Perplexity exponga prompt_tokens/completion_tokens separados,
    refactorizar para usar el split real.

    Returns:
        (cost_usd, source) — `source` indica de dónde salió el pricing
        (model_catalog | unknown). Si el modelo no está en el catálogo
        devolvemos cost=0.0 y source="unknown" para no inventar costos.
    """
    if not model_used or tokens_used <= 0:
        return 0.0, "unknown"
    try:
        from config.model_catalog import get_model

        spec = get_model(model_used)
    except Exception as e:  # pragma: no cover — defensive
        logger.warning("web_search_tool_pricing_lookup_failed", model=model_used, error=str(e))
        return 0.0, "unknown"

    pricing = (spec or {}).get("pricing")
    if not pricing or "input" not in pricing or "output" not in pricing:
        return 0.0, "unknown"

    blended_per_million = (float(pricing["input"]) + float(pricing["output"])) / 2.0
    cost_usd = (tokens_used / 1_000_000.0) * blended_per_million
    return round(cost_usd, 6), "model_catalog"


def _map_citations_to_results(citations: list[Any]) -> list[dict[str, Any]]:
    """
    Mapea `citations` (lista de URLs string que devuelve Sonar) al shape DAN
    `results: [{url, citation_id, title, snippet}]`.

    title/snippet quedan en None — Sonar las URLs sin descomponer. NO inventar.
    """
    results: list[dict[str, Any]] = []
    for idx, c in enumerate(citations or [], start=1):
        if isinstance(c, str):
            results.append(
                {
                    "url": c,
                    "citation_id": f"[{idx}]",
                    "title": None,
                    "snippet": None,
                }
            )
        elif isinstance(c, dict):
            # Forward-compat: si Sonar empieza a devolver dicts con title/snippet
            results.append(
                {
                    "url": c.get("url"),
                    "citation_id": c.get("citation_id") or f"[{idx}]",
                    "title": c.get("title"),
                    "snippet": c.get("snippet") or c.get("text"),
                }
            )
    return results


async def web_search_with_telemetry(
    query: str,
    *,
    context: str = "",
    model: str = "sonar-reasoning-pro",
    max_tokens: int = 2048,
    temperature: float = 0.2,
    finops: Optional[Any] = None,
    run_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Web search con cost_usd, latency_ms y results estructurados.
    Persiste el run en `run_costs` si `finops` está disponible.

    Args:
        query: pregunta a buscar.
        context: contexto opcional para el system prompt.
        model: modelo Sonar a usar (sonar-reasoning-pro|sonar-pro|sonar).
        max_tokens: max tokens en respuesta.
        temperature: temperatura del modelo.
        finops: instancia opcional de `FinOpsController`. Si se pasa, registra
            la query en `run_costs`. Si es None, NO registra (caller decide).
        run_id: identificador opcional de run para correlación. Si es None,
            generamos un uuid para esta llamada.

    Returns:
        dict con keys:
            - answer: str
            - citations: list[str]  (forward-compat con caller existente)
            - results: list[{url, citation_id, title, snippet}]  (DAN shape)
            - model_used: str
            - tokens_used: int
            - cost_usd: float
            - cost_source: "model_catalog" | "unknown"
            - latency_ms: int
            - run_id: str
            - error: str | None
    """
    if run_id is None:
        run_id = f"web_search:{uuid.uuid4().hex[:12]}"

    t_start = time.monotonic()
    base = await _base_web_search(
        query=query,
        context=context,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    latency_ms = int((time.monotonic() - t_start) * 1000)

    model_used: str = base.get("model_used", "") or ""
    tokens_used: int = int(base.get("tokens_used", 0) or 0)
    error: Optional[str] = base.get("error")
    citations: list[Any] = base.get("citations", []) or []

    cost_usd, cost_source = _compute_cost_usd(
        model_used=model_used, tokens_used=tokens_used
    )
    results = _map_citations_to_results(citations)

    out = {
        "answer": base.get("answer", "") or "",
        "citations": citations,
        "results": results,
        "model_used": model_used,
        "tokens_used": tokens_used,
        "cost_usd": cost_usd,
        "cost_source": cost_source,
        "latency_ms": latency_ms,
        "run_id": run_id,
        "error": error,
    }

    # Cost ledger — usar lo existente, no inventar tabla
    if finops is not None and not error:
        try:
            await finops.record_run_cost(
                run_id=run_id,
                model_used=model_used or "unknown",
                tokens_in=0,  # Sonar no descompone — registramos total en tokens_out
                tokens_out=tokens_used,
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                tool_count=1,
                status="completed",
            )
        except Exception as e:  # pragma: no cover — defensive
            logger.warning(
                "web_search_tool_ledger_failed",
                run_id=run_id,
                error=str(e),
            )

    logger.info(
        "web_search_tool_completed",
        run_id=run_id,
        model_used=model_used,
        tokens_used=tokens_used,
        cost_usd=cost_usd,
        cost_source=cost_source,
        latency_ms=latency_ms,
        results_count=len(results),
        error=bool(error),
    )

    return out
