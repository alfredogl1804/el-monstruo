#!/usr/bin/env python3.11
"""
fallback_policy.py — Política de fallbacks para el pipeline de creación.

Define y ejecuta estrategias de fallback cuando fallan APIs,
generación de código, o validación. Garantiza que el pipeline
siempre produzca un resultado, aunque sea degradado.

Uso:
    from fallback_policy import FallbackPolicy
    policy = FallbackPolicy()
    result = await policy.execute_with_fallback("generate_script", primary_fn, fallback_fn)
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

FACTORY_ROOT = Path(__file__).parent.parent
FALLBACK_LOG = FACTORY_ROOT / "data" / "fallback_log.jsonl"


# Cadenas de fallback por operación
FALLBACK_CHAINS = {
    "generate_script": {
        "primary": "gpt54",
        "fallbacks": ["claude", "gemini", "grok"],
        "max_retries": 2,
        "timeout": 120,
    },
    "generate_reference": {"primary": "gpt54", "fallbacks": ["claude", "gemini"], "max_retries": 2, "timeout": 90},
    "generate_skillmd": {"primary": "gpt54", "fallbacks": ["claude"], "max_retries": 2, "timeout": 90},
    "validate_quality": {"primary": "claude", "fallbacks": ["gpt54", "gemini"], "max_retries": 1, "timeout": 90},
    "research_topic": {"primary": "perplexity", "fallbacks": ["gemini", "gpt54"], "max_retries": 2, "timeout": 60},
    "design_architecture": {"primary": "gpt54", "fallbacks": ["claude", "gemini"], "max_retries": 2, "timeout": 120},
}


class FallbackPolicy:
    """Gestiona fallbacks para operaciones del pipeline."""

    def __init__(self):
        self.fallback_history = []

    async def execute_with_fallback(self, operation: str, fn, *args, **kwargs) -> dict:
        """Ejecuta una función con cadena de fallback."""

        chain = FALLBACK_CHAINS.get(
            operation, {"primary": "gpt54", "fallbacks": ["claude"], "max_retries": 1, "timeout": 60}
        )

        models = [chain["primary"]] + chain["fallbacks"]
        last_error = None

        for i, model in enumerate(models):
            for retry in range(chain["max_retries"]):
                try:
                    start = time.time()
                    result = await asyncio.wait_for(fn(model=model, *args, **kwargs), timeout=chain["timeout"])
                    elapsed = time.time() - start

                    # Registrar si hubo fallback
                    if i > 0 or retry > 0:
                        self._log_fallback(operation, chain["primary"], model, i, retry, elapsed, "success")

                    return {
                        "status": "ok",
                        "model_used": model,
                        "was_fallback": i > 0,
                        "retry_count": retry,
                        "elapsed": round(elapsed, 1),
                        "result": result,
                    }

                except asyncio.TimeoutError:
                    last_error = f"Timeout ({chain['timeout']}s) con {model}"
                    self._log_fallback(operation, chain["primary"], model, i, retry, chain["timeout"], "timeout")

                except Exception as e:
                    last_error = f"{model}: {str(e)[:200]}"
                    self._log_fallback(operation, chain["primary"], model, i, retry, 0, f"error: {e}")

        # Todos fallaron
        return {
            "status": "failed",
            "model_used": None,
            "was_fallback": True,
            "last_error": last_error,
            "models_tried": models,
        }

    def get_fallback_chain(self, operation: str) -> list:
        """Retorna la cadena de fallback para una operación."""
        chain = FALLBACK_CHAINS.get(operation, {})
        return [chain.get("primary", "gpt54")] + chain.get("fallbacks", [])

    def _log_fallback(
        self, operation: str, primary: str, used: str, chain_index: int, retry: int, elapsed: float, status: str
    ):
        """Registra un evento de fallback."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "primary_model": primary,
            "model_used": used,
            "chain_index": chain_index,
            "retry": retry,
            "elapsed": elapsed,
            "status": status,
        }
        self.fallback_history.append(entry)

        FALLBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(FALLBACK_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_stats(self) -> dict:
        """Estadísticas de fallbacks."""
        if not FALLBACK_LOG.exists():
            return {"total_fallbacks": 0}

        entries = []
        with open(FALLBACK_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass

        return {
            "total_fallbacks": len(entries),
            "by_operation": {
                op: sum(1 for e in entries if e.get("operation") == op)
                for op in set(e.get("operation", "") for e in entries)
            },
            "by_status": {
                s: sum(1 for e in entries if e.get("status") == s) for s in set(e.get("status", "") for e in entries)
            },
            "most_reliable": _most_reliable_model(entries),
            "least_reliable": _least_reliable_model(entries),
        }


def _most_reliable_model(entries: list) -> str:
    """Encuentra el modelo más confiable."""
    success = {}
    total = {}
    for e in entries:
        model = e.get("model_used", "unknown")
        total[model] = total.get(model, 0) + 1
        if e.get("status") == "success":
            success[model] = success.get(model, 0) + 1

    rates = {m: success.get(m, 0) / total[m] for m in total}
    return max(rates, key=rates.get) if rates else "unknown"


def _least_reliable_model(entries: list) -> str:
    """Encuentra el modelo menos confiable."""
    failures = {}
    for e in entries:
        if e.get("status") != "success":
            model = e.get("model_used", "unknown")
            failures[model] = failures.get(model, 0) + 1

    return max(failures, key=failures.get) if failures else "none"


if __name__ == "__main__":
    policy = FallbackPolicy()
    stats = policy.get_stats()
    print("📊 Estadísticas de fallbacks:")
    print(f"  Total: {stats['total_fallbacks']}")
    if stats["total_fallbacks"] > 0:
        print(f"  Por operación: {stats.get('by_operation', {})}")
        print(f"  Más confiable: {stats.get('most_reliable', 'N/A')}")
        print(f"  Menos confiable: {stats.get('least_reliable', 'N/A')}")
