"""
El Monstruo — Adaptive Model Selector (SP9)
============================================
Automatiza la selección de modelo según tipo de tarea, registrando
qué modelo funcionó mejor para cada clase de tarea.

Routing rules (initial):
  - Creativas (copy, narrativa, diseño) → Gemini 3.1 Pro
  - Razonamiento complejo (código, lógica, causal) → Claude Opus
  - Búsqueda factual (investigación, datos) → Perplexity Sonar
  - Análisis/resumen → GPT-5.5
  - Clasificación simple → Local (Ollama/gemma3)

Learning loop:
  1. Classify incoming task → TaskClass
  2. Select best model for that class (from performance history)
  3. Execute task with selected model
  4. Record outcome (success/failure, latency, cost, quality_score)
  5. Update model rankings per TaskClass

Persistence:
  - model_performance table in Supabase (task_class, model, metrics)
  - In-memory cache for fast lookups

Integration:
  - sovereign_llm.py uses this to override tier defaults
  - task_planner.py can query optimal model for each step type

Sprint: SP9 (Embrión Superpowers)
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.adaptive_model_selector")


# ── Task Classification ──────────────────────────────────────────────

class TaskClass(str, Enum):
    """Classification of task types for model routing."""
    CREATIVE = "creative"           # Copy, narrativa, diseño, brainstorming
    REASONING = "reasoning"         # Código, lógica, causal, debugging
    FACTUAL_SEARCH = "factual_search"  # Investigación, datos actuales, verificación
    ANALYSIS = "analysis"           # Resumen, síntesis, comparación
    CLASSIFICATION = "classification"  # Clasificación simple, routing, triage
    CONVERSATION = "conversation"   # Chat, Q&A simple, soporte
    CODE_GENERATION = "code_generation"  # Escribir código nuevo
    CODE_REVIEW = "code_review"     # Revisar, debuggear código existente
    PLANNING = "planning"           # Planificación, descomposición de tareas
    TRANSLATION = "translation"     # Traducción, i18n


# ── Model Registry ───────────────────────────────────────────────────

@dataclass
class ModelConfig:
    """Configuration for a model."""
    model_id: str
    provider: str  # openai, anthropic, google, perplexity, ollama
    cost_per_1k_tokens: float
    max_tokens: int = 4096
    supports_tools: bool = True
    supports_vision: bool = False
    latency_tier: str = "medium"  # fast, medium, slow


# Default model assignments per task class
DEFAULT_ROUTING: dict[TaskClass, list[str]] = {
    TaskClass.CREATIVE: ["gemini-3.1-pro", "claude-opus-4-7", "gpt-5.5"],
    TaskClass.REASONING: ["claude-opus-4-7", "gpt-5.5", "deepseek-r1"],
    TaskClass.FACTUAL_SEARCH: ["sonar-reasoning-pro", "sonar-pro", "gemini-3.1-pro"],
    TaskClass.ANALYSIS: ["gpt-5.5", "claude-opus-4-7", "gemini-3.1-pro"],
    TaskClass.CLASSIFICATION: ["gpt-4o-mini", "gemma3:8b", "gpt-5.5"],
    TaskClass.CONVERSATION: ["gpt-4o-mini", "gpt-5.5", "claude-opus-4-7"],
    TaskClass.CODE_GENERATION: ["claude-opus-4-7", "gpt-5.5", "deepseek-r1"],
    TaskClass.CODE_REVIEW: ["claude-opus-4-7", "gpt-5.5", "gemini-3.1-pro"],
    TaskClass.PLANNING: ["gpt-5.5", "claude-opus-4-7", "gemini-3.1-pro"],
    TaskClass.TRANSLATION: ["gpt-5.5", "gemini-3.1-pro", "gpt-4o-mini"],
}

# Model metadata
MODEL_REGISTRY: dict[str, ModelConfig] = {
    "gpt-5.5": ModelConfig(
        model_id="gpt-5.5", provider="openai",
        cost_per_1k_tokens=0.010, max_tokens=32768,
        supports_tools=True, supports_vision=True, latency_tier="medium",
    ),
    "gpt-4o-mini": ModelConfig(
        model_id="gpt-4o-mini", provider="openai",
        cost_per_1k_tokens=0.00015, max_tokens=16384,
        supports_tools=True, supports_vision=True, latency_tier="fast",
    ),
    "claude-opus-4-7": ModelConfig(
        model_id="claude-opus-4-7", provider="anthropic",
        cost_per_1k_tokens=0.015, max_tokens=32768,
        supports_tools=True, supports_vision=True, latency_tier="slow",
    ),
    "gemini-3.1-pro": ModelConfig(
        model_id="gemini-3.1-pro", provider="google",
        cost_per_1k_tokens=0.00125, max_tokens=65536,
        supports_tools=True, supports_vision=True, latency_tier="medium",
    ),
    "sonar-reasoning-pro": ModelConfig(
        model_id="sonar-reasoning-pro", provider="perplexity",
        cost_per_1k_tokens=0.005, max_tokens=8192,
        supports_tools=False, supports_vision=False, latency_tier="medium",
    ),
    "sonar-pro": ModelConfig(
        model_id="sonar-pro", provider="perplexity",
        cost_per_1k_tokens=0.003, max_tokens=8192,
        supports_tools=False, supports_vision=False, latency_tier="fast",
    ),
    "deepseek-r1": ModelConfig(
        model_id="deepseek-r1", provider="openrouter",
        cost_per_1k_tokens=0.003, max_tokens=32768,
        supports_tools=True, supports_vision=False, latency_tier="slow",
    ),
    "gemma3:8b": ModelConfig(
        model_id="gemma3:8b", provider="ollama",
        cost_per_1k_tokens=0.0, max_tokens=8192,
        supports_tools=False, supports_vision=False, latency_tier="fast",
    ),
}


# ── Performance Record ───────────────────────────────────────────────

@dataclass
class PerformanceRecord:
    """Record of a model's performance on a task class."""
    task_class: str
    model_id: str
    total_calls: int = 0
    successes: int = 0
    failures: int = 0
    avg_latency_ms: float = 0.0
    avg_cost_usd: float = 0.0
    avg_quality_score: float = 0.5  # 0.0-1.0
    last_used: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.5  # neutral prior
        return self.successes / self.total_calls

    @property
    def composite_score(self) -> float:
        """
        Composite score combining success rate, quality, cost efficiency, and speed.
        Higher = better model for this task class.
        """
        # Weighted composite:
        # 40% success rate, 30% quality, 20% cost efficiency, 10% speed
        cost_efficiency = max(0, 1.0 - (self.avg_cost_usd * 100))  # Penalize expensive
        speed_score = {
            "fast": 1.0, "medium": 0.7, "slow": 0.4
        }.get(MODEL_REGISTRY.get(self.model_id, ModelConfig("", "", 0)).latency_tier, 0.5)

        return (
            0.40 * self.success_rate
            + 0.30 * self.avg_quality_score
            + 0.20 * cost_efficiency
            + 0.10 * speed_score
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_class": self.task_class,
            "model_id": self.model_id,
            "total_calls": self.total_calls,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": round(self.success_rate, 3),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "avg_cost_usd": round(self.avg_cost_usd, 6),
            "avg_quality_score": round(self.avg_quality_score, 3),
            "composite_score": round(self.composite_score, 3),
            "last_used": self.last_used,
        }


# ── Task Classifier ─────────────────────────────────────────────────

# Keywords for fast classification (no LLM needed)
_CLASSIFICATION_KEYWORDS: dict[TaskClass, list[str]] = {
    TaskClass.CREATIVE: [
        "escribe", "redacta", "crea un copy", "narrativa", "storytelling",
        "brainstorm", "imagina", "diseña", "genera ideas", "slogan",
    ],
    TaskClass.REASONING: [
        "analiza por qué", "razona", "explica la lógica", "demuestra",
        "causal", "causa-efecto", "deduce", "infiere",
    ],
    TaskClass.FACTUAL_SEARCH: [
        "busca", "investiga", "encuentra", "qué es", "cuándo",
        "datos sobre", "estadísticas", "fuentes", "verifica",
    ],
    TaskClass.CODE_GENERATION: [
        "escribe código", "implementa", "programa", "crea un script",
        "función que", "endpoint", "api para", "módulo de",
    ],
    TaskClass.CODE_REVIEW: [
        "revisa el código", "debug", "encuentra el bug", "optimiza",
        "refactoriza", "code review", "qué está mal",
    ],
    TaskClass.PLANNING: [
        "planifica", "descompón", "crea un plan", "roadmap",
        "paso a paso", "estrategia para", "hoja de ruta",
    ],
    TaskClass.ANALYSIS: [
        "resume", "sintetiza", "compara", "analiza", "evalúa",
        "pros y contras", "benchmark", "diferencias entre",
    ],
    TaskClass.TRANSLATION: [
        "traduce", "translate", "en inglés", "en español",
        "localiza", "i18n",
    ],
    TaskClass.CONVERSATION: [
        "hola", "gracias", "cómo estás", "ayuda con",
    ],
}


def classify_task(objective: str, tool_hint: Optional[str] = None) -> TaskClass:
    """
    Classify a task objective into a TaskClass using keyword matching.
    Fast, deterministic, no LLM needed.
    """
    objective_lower = objective.lower()

    # Tool hint provides strong signal
    if tool_hint:
        tool_class_map = {
            "web_search": TaskClass.FACTUAL_SEARCH,
            "browse_web": TaskClass.FACTUAL_SEARCH,
            "code_exec": TaskClass.CODE_GENERATION,
            "github": TaskClass.CODE_GENERATION,
            "query_knowledge": TaskClass.ANALYSIS,
        }
        if tool_hint in tool_class_map:
            return tool_class_map[tool_hint]

    # Keyword matching
    scores: dict[TaskClass, int] = {}
    for task_class, keywords in _CLASSIFICATION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in objective_lower)
        if score > 0:
            scores[task_class] = score

    if scores:
        return max(scores, key=scores.get)  # type: ignore[arg-type]

    # Default: analysis (safe middle ground)
    return TaskClass.ANALYSIS


# ── Adaptive Model Selector ──────────────────────────────────────────

class AdaptiveModelSelector:
    """
    Selects the best model for a given task class based on historical performance.
    Learns over time which models work best for which types of tasks.
    """

    def __init__(self, db: Optional[Any] = None):
        self._db = db
        self._performance_cache: dict[str, PerformanceRecord] = {}
        self._initialized = False
        self._stats = {
            "selections": 0,
            "overrides": 0,  # Times learned routing beat default
            "records": 0,
        }

    async def initialize(self) -> None:
        """Load performance history from DB."""
        if self._db:
            try:
                rows = await self._db.select(
                    "model_performance",
                    filters={"active": True},
                )
                for row in (rows or []):
                    key = f"{row['task_class']}:{row['model_id']}"
                    self._performance_cache[key] = PerformanceRecord(
                        task_class=row["task_class"],
                        model_id=row["model_id"],
                        total_calls=row.get("total_calls", 0),
                        successes=row.get("successes", 0),
                        failures=row.get("failures", 0),
                        avg_latency_ms=row.get("avg_latency_ms", 0),
                        avg_cost_usd=row.get("avg_cost_usd", 0),
                        avg_quality_score=row.get("avg_quality_score", 0.5),
                        last_used=row.get("last_used", 0),
                    )
                self._stats["records"] = len(self._performance_cache)
                logger.info(
                    "adaptive_model_selector_loaded",
                    records=len(self._performance_cache),
                )
            except Exception as e:
                logger.warning("adaptive_model_selector_load_failed", error=str(e)[:100])

        self._initialized = True

    def select_model(
        self,
        task_class: TaskClass,
        require_tools: bool = False,
        require_vision: bool = False,
        budget_usd: Optional[float] = None,
    ) -> str:
        """
        Select the best model for a given task class.

        Priority:
        1. Historical performance (if enough data: >= 5 calls)
        2. Default routing table
        3. Fallback to gpt-5.5

        Returns model_id string.
        """
        self._stats["selections"] += 1

        # Check if we have enough performance data to override defaults
        candidates: list[tuple[str, float]] = []
        for key, record in self._performance_cache.items():
            if record.task_class != task_class.value:
                continue
            if record.total_calls < 5:
                continue  # Not enough data to trust

            model_config = MODEL_REGISTRY.get(record.model_id)
            if not model_config:
                continue

            # Filter by requirements
            if require_tools and not model_config.supports_tools:
                continue
            if require_vision and not model_config.supports_vision:
                continue
            if budget_usd and model_config.cost_per_1k_tokens > budget_usd:
                continue

            candidates.append((record.model_id, record.composite_score))

        # If we have learned candidates, use the best one
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_model = candidates[0][0]

            # Check if this overrides the default
            default_models = DEFAULT_ROUTING.get(task_class, [])
            if default_models and best_model != default_models[0]:
                self._stats["overrides"] += 1
                logger.info(
                    "adaptive_model_override",
                    task_class=task_class.value,
                    default=default_models[0] if default_models else "none",
                    selected=best_model,
                    score=candidates[0][1],
                )

            return best_model

        # Fall back to default routing
        default_models = DEFAULT_ROUTING.get(task_class, ["gpt-5.5"])
        for model_id in default_models:
            config = MODEL_REGISTRY.get(model_id)
            if not config:
                continue
            if require_tools and not config.supports_tools:
                continue
            if require_vision and not config.supports_vision:
                continue
            if budget_usd and config.cost_per_1k_tokens > budget_usd:
                continue
            return model_id

        return "gpt-5.5"  # Ultimate fallback

    async def record_outcome(
        self,
        task_class: TaskClass,
        model_id: str,
        success: bool,
        latency_ms: float = 0.0,
        cost_usd: float = 0.0,
        quality_score: float = 0.5,
    ) -> None:
        """
        Record the outcome of a model call for learning.
        Updates in-memory cache and persists to DB.
        """
        key = f"{task_class.value}:{model_id}"

        if key not in self._performance_cache:
            self._performance_cache[key] = PerformanceRecord(
                task_class=task_class.value,
                model_id=model_id,
            )

        record = self._performance_cache[key]
        record.total_calls += 1
        if success:
            record.successes += 1
        else:
            record.failures += 1

        # Running average for latency and cost
        n = record.total_calls
        record.avg_latency_ms = (
            (record.avg_latency_ms * (n - 1) + latency_ms) / n
        )
        record.avg_cost_usd = (
            (record.avg_cost_usd * (n - 1) + cost_usd) / n
        )
        # Exponential moving average for quality (more weight to recent)
        alpha = 0.3
        record.avg_quality_score = (
            alpha * quality_score + (1 - alpha) * record.avg_quality_score
        )
        record.last_used = time.time()

        # Persist to DB
        if self._db:
            try:
                await self._db.upsert(
                    "model_performance",
                    {
                        "task_class": task_class.value,
                        "model_id": model_id,
                        "total_calls": record.total_calls,
                        "successes": record.successes,
                        "failures": record.failures,
                        "avg_latency_ms": round(record.avg_latency_ms, 1),
                        "avg_cost_usd": round(record.avg_cost_usd, 6),
                        "avg_quality_score": round(record.avg_quality_score, 3),
                        "composite_score": round(record.composite_score, 3),
                        "last_used": record.last_used,
                        "active": True,
                    },
                    on_conflict="task_class,model_id",
                )
            except Exception as e:
                logger.warning(
                    "adaptive_model_record_failed",
                    error=str(e)[:100],
                    task_class=task_class.value,
                    model_id=model_id,
                )

        logger.debug(
            "adaptive_model_outcome_recorded",
            task_class=task_class.value,
            model_id=model_id,
            success=success,
            composite_score=round(record.composite_score, 3),
        )

    def get_rankings(self, task_class: Optional[TaskClass] = None) -> list[dict]:
        """Get model rankings, optionally filtered by task class."""
        records = []
        for record in self._performance_cache.values():
            if task_class and record.task_class != task_class.value:
                continue
            records.append(record.to_dict())

        records.sort(key=lambda r: r["composite_score"], reverse=True)
        return records

    def get_stats(self) -> dict[str, Any]:
        """Get selector statistics."""
        return {
            **self._stats,
            "cache_size": len(self._performance_cache),
            "initialized": self._initialized,
            "task_classes": len(TaskClass),
            "models_registered": len(MODEL_REGISTRY),
        }


# ── Singleton ────────────────────────────────────────────────────────

_selector_instance: Optional[AdaptiveModelSelector] = None


def get_adaptive_model_selector() -> Optional[AdaptiveModelSelector]:
    """Get the singleton AdaptiveModelSelector."""
    return _selector_instance


async def init_adaptive_model_selector(db: Optional[Any] = None) -> AdaptiveModelSelector:
    """Initialize and return the singleton AdaptiveModelSelector."""
    global _selector_instance
    _selector_instance = AdaptiveModelSelector(db=db)
    await _selector_instance.initialize()
    return _selector_instance
