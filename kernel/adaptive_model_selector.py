"""
El Monstruo — SP9: Adaptive Model Selection
============================================
Selecciona el modelo óptimo según complejidad de tarea y budget restante.

Lee historial de costos desde task_plans (total_cost_usd, tokens) para
informar decisiones de routing. Complementa sovereign_llm.py con una capa
adaptiva que respeta presupuesto.

Spec (Hilo B):
  - select_optimal_model(task_complexity, budget_remaining)
  - complexity < 0.3 → modelo barato
  - 0.3 <= complexity <= 0.7 → modelo estándar
  - complexity > 0.7 → modelo premium
  - Respetar budget restante del plan
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.adaptive_model_selector")


# ─── Model Definitions ────────────────────────────────────────────────────────


class ModelTier(str, Enum):
    """Tier de modelo por costo/capacidad."""

    CHEAP = "cheap"
    STANDARD = "standard"
    PREMIUM = "premium"


@dataclass
class ModelOption:
    """Un modelo disponible con sus características."""

    name: str
    provider: str
    tier: ModelTier
    cost_per_1k_tokens: float  # USD por 1k tokens (input+output promedio)
    max_context: int = 128000
    strengths: list[str] = field(default_factory=list)

    def estimated_cost(self, tokens: int) -> float:
        """Costo estimado para N tokens."""
        return (tokens / 1000) * self.cost_per_1k_tokens


# Catálogo de modelos disponibles — orden por tier
MODEL_CATALOG: list[ModelOption] = [
    # ── Tier CHEAP ──
    ModelOption(
        name="gpt-4o-mini",
        provider="openai",
        tier=ModelTier.CHEAP,
        cost_per_1k_tokens=0.00015,
        strengths=["fast", "classification", "formatting"],
    ),
    ModelOption(
        name="gemma3:8b",
        provider="ollama_local",
        tier=ModelTier.CHEAP,
        cost_per_1k_tokens=0.0,
        max_context=32000,
        strengths=["free", "local", "simple_tasks"],
    ),
    # ── Tier STANDARD ──
    ModelOption(
        name="gemini-2.5-flash",
        provider="google",
        tier=ModelTier.STANDARD,
        cost_per_1k_tokens=0.00075,
        strengths=["balanced", "reasoning", "multimodal"],
    ),
    ModelOption(
        name="gpt-4o",
        provider="openai",
        tier=ModelTier.STANDARD,
        cost_per_1k_tokens=0.005,
        strengths=["general", "code", "analysis"],
    ),
    # ── Tier PREMIUM ──
    ModelOption(
        name="claude-opus-4-7",
        provider="anthropic",
        tier=ModelTier.PREMIUM,
        cost_per_1k_tokens=0.015,
        strengths=["deep_reasoning", "code", "complex_analysis"],
    ),
    ModelOption(
        name="gpt-5.5",
        provider="openai",
        tier=ModelTier.PREMIUM,
        cost_per_1k_tokens=0.01,
        strengths=["reasoning", "planning", "creative"],
    ),
]

# Lookup rápido
_MODELS_BY_NAME: dict[str, ModelOption] = {m.name: m for m in MODEL_CATALOG}
_MODELS_BY_TIER: dict[ModelTier, list[ModelOption]] = {}
for _m in MODEL_CATALOG:
    _MODELS_BY_TIER.setdefault(_m.tier, []).append(_m)


# ─── Selection Result ─────────────────────────────────────────────────────────


@dataclass
class ModelSelection:
    """Resultado de la selección de modelo."""

    model: ModelOption
    reason: str
    tier_selected: ModelTier
    budget_constrained: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_name": self.model.name,
            "provider": self.model.provider,
            "tier": self.tier_selected.value,
            "cost_per_1k": self.model.cost_per_1k_tokens,
            "reason": self.reason,
            "budget_constrained": self.budget_constrained,
        }


# ─── Cost History Reader ──────────────────────────────────────────────────────


async def read_cost_history(db: Any) -> dict[str, Any]:
    """
    Lee historial de costos desde task_plans para informar selección.

    Returns dict con:
      - total_spent_usd: gasto total histórico
      - avg_cost_per_plan: costo promedio por plan
      - plans_count: número de planes ejecutados
      - tokens_total: tokens totales usados
    """
    if db is None:
        return {
            "total_spent_usd": 0.0,
            "avg_cost_per_plan": 0.0,
            "plans_count": 0,
            "tokens_total": 0,
        }

    try:
        result = await db.fetch_one(
            """
            SELECT
                COALESCE(SUM(total_cost_usd), 0) as total_spent,
                COALESCE(AVG(total_cost_usd), 0) as avg_cost,
                COUNT(*) as plans_count,
                COALESCE(SUM(total_tokens), 0) as tokens_total
            FROM task_plans
            WHERE status IN ('done', 'failed')
            """
        )
        if result:
            return {
                "total_spent_usd": float(result["total_spent"]),
                "avg_cost_per_plan": float(result["avg_cost"]),
                "plans_count": int(result["plans_count"]),
                "tokens_total": int(result["tokens_total"]),
            }
    except Exception as e:
        logger.warning("cost_history_read_failed", error=str(e)[:100])

    return {
        "total_spent_usd": 0.0,
        "avg_cost_per_plan": 0.0,
        "plans_count": 0,
        "tokens_total": 0,
    }


# ─── Core Selection Logic ─────────────────────────────────────────────────────


def select_optimal_model(
    task_complexity: float,
    budget_remaining: float,
    estimated_tokens: int = 2000,
    prefer_provider: Optional[str] = None,
) -> ModelSelection:
    """
    Selecciona el modelo óptimo según complejidad y budget.

    Args:
        task_complexity: Float 0.0-1.0 indicando complejidad de la tarea.
            - < 0.3: tarea simple (clasificación, formatting)
            - 0.3-0.7: tarea media (resumen, análisis, Q&A)
            - > 0.7: tarea compleja (razonamiento profundo, código)
        budget_remaining: USD restantes en el budget del plan.
        estimated_tokens: Tokens estimados para la tarea (default 2000).
        prefer_provider: Proveedor preferido (opcional).

    Returns:
        ModelSelection con el modelo elegido y la razón.
    """
    # Determinar tier deseado por complejidad
    if task_complexity < 0.3:
        desired_tier = ModelTier.CHEAP
        reason_base = "simple task (complexity < 0.3)"
    elif task_complexity <= 0.7:
        desired_tier = ModelTier.STANDARD
        reason_base = "medium task (0.3 <= complexity <= 0.7)"
    else:
        desired_tier = ModelTier.PREMIUM
        reason_base = "complex task (complexity > 0.7)"

    # Obtener candidatos del tier deseado
    candidates = list(_MODELS_BY_TIER.get(desired_tier, []))

    # Si hay preferencia de proveedor, priorizar
    if prefer_provider:
        preferred = [c for c in candidates if c.provider == prefer_provider]
        others = [c for c in candidates if c.provider != prefer_provider]
        candidates = preferred + others

    # Verificar budget — si no alcanza para el tier deseado, bajar
    budget_constrained = False
    selected = None

    for candidate in candidates:
        estimated_cost = candidate.estimated_cost(estimated_tokens)
        if estimated_cost <= budget_remaining:
            selected = candidate
            break

    # Si ningún candidato del tier deseado cabe en budget, bajar tier
    if selected is None:
        budget_constrained = True
        # Intentar tiers más baratos en orden
        fallback_tiers: list[ModelTier] = []
        if desired_tier == ModelTier.PREMIUM:
            fallback_tiers = [ModelTier.STANDARD, ModelTier.CHEAP]
        elif desired_tier == ModelTier.STANDARD:
            fallback_tiers = [ModelTier.CHEAP]

        for fallback_tier in fallback_tiers:
            for candidate in _MODELS_BY_TIER.get(fallback_tier, []):
                estimated_cost = candidate.estimated_cost(estimated_tokens)
                if estimated_cost <= budget_remaining:
                    selected = candidate
                    reason_base = (
                        f"downgraded from {desired_tier.value} to "
                        f"{fallback_tier.value} (budget: "
                        f"${budget_remaining:.4f} remaining)"
                    )
                    desired_tier = fallback_tier
                    break
            if selected:
                break

    # Último recurso: modelo más barato disponible (gemma3 = $0)
    if selected is None:
        selected = _MODELS_BY_TIER[ModelTier.CHEAP][-1]  # gemma3 (free)
        reason_base = "emergency fallback — budget exhausted, using free model"
        budget_constrained = True
        desired_tier = ModelTier.CHEAP

    logger.info(
        "model_selected",
        model=selected.name,
        tier=desired_tier.value,
        complexity=round(task_complexity, 2),
        budget_remaining=round(budget_remaining, 4),
        budget_constrained=budget_constrained,
    )

    return ModelSelection(
        model=selected,
        reason=reason_base,
        tier_selected=desired_tier,
        budget_constrained=budget_constrained,
    )


# ─── Integration Helper ──────────────────────────────────────────────────────


def get_model_for_step(
    step_description: str,
    plan_total_cost: float,
    plan_budget: float = 1.0,
) -> ModelSelection:
    """
    Helper para el TaskPlanner — selecciona modelo para un step.

    Estima complejidad a partir de la descripción del paso usando
    heurísticas simples (longitud, keywords).
    """
    budget_remaining = max(0.0, plan_budget - plan_total_cost)
    complexity = _estimate_complexity(step_description)

    return select_optimal_model(
        task_complexity=complexity,
        budget_remaining=budget_remaining,
    )


def _estimate_complexity(description: str) -> float:
    """
    Estima complejidad de una tarea a partir de su descripción.

    Heurísticas:
      - Longitud del texto
      - Presencia de keywords de complejidad
      - Número de sub-tareas implícitas
    """
    desc_lower = description.lower()

    # Keywords de alta complejidad
    complex_keywords = [
        "analiza",
        "investiga",
        "diseña",
        "arquitectura",
        "optimiza",
        "refactoriza",
        "multi-paso",
        "integra",
        "compara",
        "evalúa",
        "razonamiento",
        "profundo",
        "complejo",
        "estrategia",
        "código",
        "implementa",
        "debug",
        "pipeline",
    ]

    # Keywords de baja complejidad
    simple_keywords = [
        "lista",
        "formatea",
        "extrae",
        "clasifica",
        "resume",
        "traduce",
        "convierte",
        "busca",
        "filtra",
        "ordena",
    ]

    # Scoring
    score = 0.4  # Base: medio

    # Longitud
    if len(description) > 200:
        score += 0.1
    elif len(description) < 50:
        score -= 0.1

    # Keywords
    complex_hits = sum(1 for kw in complex_keywords if kw in desc_lower)
    simple_hits = sum(1 for kw in simple_keywords if kw in desc_lower)

    score += complex_hits * 0.08
    score -= simple_hits * 0.08

    # Clamp to [0, 1]
    return max(0.0, min(1.0, score))


# ─── Module-level convenience ─────────────────────────────────────────────────

PLAN_BUDGET_USD = float(os.environ.get("PLANNER_BUDGET_USD", "1.0"))
