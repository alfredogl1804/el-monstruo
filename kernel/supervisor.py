"""
El Monstruo — Supervisor Node (Sprint 29 — Épica 1)
=====================================================
Multi-Agent Hierarchical Supervisor that analyzes message complexity
and routes to the optimal model tier:

  SIMPLE  → gemini-3.1-flash-lite or gpt-4.1-mini  (workers económicos)
  COMPLEX → gpt-5.5 or claude-opus-4-7              (flagships)
  DEEP    → gpt-5.5 + tool calling + enrichment     (full pipeline)

Gate Épica 1: 70% of requests resolved by workers económicos.

Architecture:
  intake → supervisor → [enrich] → execute → respond
                ↓
    Analyzes: message length, keywords, conversation depth,
    tool requirements, and language complexity to determine tier.

The supervisor does NOT make an LLM call — it uses heuristic analysis
for zero-latency routing. This is intentional: the supervisor must be
faster than the models it routes to.

Sprint 29 | 0.22.0-sprint29 | 25 abril 2026
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger("kernel.supervisor")


# ── Complexity Tiers ──────────────────────────────────────────────────


class ComplexityTier(str, Enum):
    """Message complexity classification."""

    SIMPLE = "simple"  # Greetings, short questions, lookups
    MODERATE = "moderate"  # Multi-step questions, summaries
    COMPLEX = "complex"  # Analysis, reasoning, multi-domain
    DEEP = "deep"  # Research, tool-heavy, multi-agent


@dataclass
class SupervisorDecision:
    """Result of supervisor analysis."""

    tier: ComplexityTier
    model: str
    fallbacks: list[str]
    reason: str
    skip_enrich: bool  # Simple queries don't need memory enrichment
    estimated_tokens: int
    confidence: float  # 0.0 - 1.0
    latency_ms: float


# ── Tier → Model Mapping ─────────────────────────────────────────────

# Sprint 42: Model selection optimized for TTFT based on BenchLM April 2026 data.
# Consensus from Los 3 Sabios (Gemini 3 Pro + Perplexity Sonar Pro):
#   - SIMPLE: grok-4.1-fast (0.54s TTFT, score 70) — blazing fast for greetings/short Q
#   - MODERATE: gpt-4.1-nano (0.63s TTFT, score 27) — fast with good quality for multi-step
#   - COMPLEX/DEEP: unchanged (gpt-5.5, claude-opus-4-7 for max quality)
TIER_MODEL_MAP: dict[ComplexityTier, dict[str, Any]] = {
    ComplexityTier.SIMPLE: {
        "primary": "grok-4.1-fast",
        "fallbacks": ["gpt-4.1-nano", "gemini-3.1-flash-lite", "groq-llama-scout"],
        "skip_enrich": True,
    },
    ComplexityTier.MODERATE: {
        "primary": "gpt-4.1-nano",
        "fallbacks": ["grok-4.1-fast", "gpt-4.1-mini", "gemini-3.1-flash-lite"],
        "skip_enrich": False,
    },
    ComplexityTier.COMPLEX: {
        "primary": "gpt-5.5",
        "fallbacks": ["claude-opus-4-7", "gemini-3.1-pro", "groq-llama-scout"],
        "skip_enrich": False,
    },
    ComplexityTier.DEEP: {
        "primary": "gpt-5.5",
        "fallbacks": ["claude-opus-4-7", "grok-4.20", "together-llama-scout"],
        "skip_enrich": False,
    },
}


# ── Heuristic Signals ────────────────────────────────────────────────

# Keywords that signal complexity
_COMPLEX_KEYWORDS = {
    "analiza",
    "analyze",
    "compara",
    "compare",
    "evalúa",
    "evaluate",
    "investiga",
    "research",
    "profundiza",
    "deep dive",
    "arquitectura",
    "architecture",
    "estrategia",
    "strategy",
    "diseña",
    "design",
    "optimiza",
    "optimize",
    "refactoriza",
    "refactor",
    "audita",
    "audit",
    "simula",
    "simulate",
    "modela",
    "model",
    "predice",
    "predict",
}

_DEEP_KEYWORDS = {
    "sabios",
    "council",
    "enjambre",
    "swarm",
    "cidp",
    "multi-model",
    "consensus",
    "deep research",
    "investigación profunda",
    "plan completo",
    "full plan",
    "sprint",
    "deploy",
    "despliegue",
}

_SIMPLE_PATTERNS = [
    r"^(hola|hi|hey|buenos?\s+d[ií]as?|buenas?\s+tardes?|buenas?\s+noches?)\b",
    r"^(gracias|thanks|ok|sí|si|no|claro|perfecto|listo|entendido)\b",
    r"^(qué|que|cuál|cual|cómo|como|cuánto|cuanto|dónde|donde)\s+\w{1,10}\s*\??$",
    r"^.{1,30}\?$",  # Very short questions
]

_TOOL_KEYWORDS = {
    "busca en",
    "search",
    "web search",
    "github",
    "database",
    "supabase",
    "email",
    "webhook",
    "api",
    "endpoint",
    "deploy",
    "browse",
}


def _estimate_tokens(message: str) -> int:
    """Rough token estimate (1 token ≈ 4 chars for English, 2 chars for Spanish)."""
    return max(len(message) // 3, 1)


def analyze_complexity(
    message: str,
    conversation_depth: int = 0,
    has_tool_history: bool = False,
    intent: str = "chat",
) -> SupervisorDecision:
    """
    Analyze message complexity using heuristic signals.
    Zero LLM calls — pure pattern matching for speed.

    Signals analyzed:
      1. Message length
      2. Keyword complexity
      3. Conversation depth (multi-turn = more complex)
      4. Tool requirements
      5. Syntactic complexity (sentence count, question marks)
      6. Intent override (deep_think always → COMPLEX+)

    Returns SupervisorDecision with model selection and routing metadata.
    """
    start = time.monotonic()
    msg_lower = message.strip().lower()
    msg_len = len(message)
    estimated_tokens = _estimate_tokens(message)

    # ── Signal 1: Simple pattern matching ──
    for pattern in _SIMPLE_PATTERNS:
        if re.match(pattern, msg_lower):
            tier_config = TIER_MODEL_MAP[ComplexityTier.SIMPLE]
            return SupervisorDecision(
                tier=ComplexityTier.SIMPLE,
                model=tier_config["primary"],
                fallbacks=tier_config["fallbacks"],
                reason="simple_pattern_match",
                skip_enrich=tier_config["skip_enrich"],
                estimated_tokens=estimated_tokens,
                confidence=0.95,
                latency_ms=(time.monotonic() - start) * 1000,
            )

    # ── Signal 2: Deep keywords ──
    deep_score = sum(1 for kw in _DEEP_KEYWORDS if kw in msg_lower)
    if deep_score >= 1 or intent == "deep_think":
        tier_config = TIER_MODEL_MAP[ComplexityTier.DEEP]
        return SupervisorDecision(
            tier=ComplexityTier.DEEP,
            model=tier_config["primary"],
            fallbacks=tier_config["fallbacks"],
            reason=f"deep_keywords={deep_score}, intent={intent}",
            skip_enrich=tier_config["skip_enrich"],
            estimated_tokens=estimated_tokens,
            confidence=0.85,
            latency_ms=(time.monotonic() - start) * 1000,
        )

    # ── Signal 3: Complex keywords ──
    complex_score = sum(1 for kw in _COMPLEX_KEYWORDS if kw in msg_lower)

    # ── Signal 4: Tool requirements ──
    tool_score = sum(1 for kw in _TOOL_KEYWORDS if kw in msg_lower)

    # ── Signal 5: Syntactic complexity ──
    sentence_count = len(re.split(r"[.!?]+", message.strip())) - 1
    question_count = message.count("?")
    has_code_block = "```" in message
    has_list = bool(re.search(r"^\s*[-*\d]+[.)]\s", message, re.MULTILINE))

    # ── Composite score ──
    score = 0.0
    score += min(msg_len / 500, 2.0)  # Length: 0-2 points
    score += complex_score * 1.5  # Complex keywords: 1.5 each
    score += tool_score * 1.0  # Tool keywords: 1.0 each
    score += sentence_count * 0.3  # Sentences: 0.3 each
    score += question_count * 0.5  # Questions: 0.5 each
    score += conversation_depth * 0.2  # Depth: 0.2 per turn
    score += 2.0 if has_code_block else 0.0  # Code blocks: +2
    score += 1.0 if has_list else 0.0  # Lists: +1
    score += 1.0 if has_tool_history else 0.0  # Previous tool use: +1

    # ── Tier selection ──
    if score < 1.5:
        tier = ComplexityTier.SIMPLE
        confidence = min(0.9, 1.0 - score / 3.0)
    elif score < 4.0:
        tier = ComplexityTier.MODERATE
        confidence = 0.75
    elif score < 7.0:
        tier = ComplexityTier.COMPLEX
        confidence = 0.8
    else:
        tier = ComplexityTier.DEEP
        confidence = 0.85

    tier_config = TIER_MODEL_MAP[tier]
    elapsed_ms = (time.monotonic() - start) * 1000

    decision = SupervisorDecision(
        tier=tier,
        model=tier_config["primary"],
        fallbacks=tier_config["fallbacks"],
        reason=f"score={score:.1f}, complex_kw={complex_score}, tool_kw={tool_score}, sents={sentence_count}, depth={conversation_depth}",
        skip_enrich=tier_config["skip_enrich"],
        estimated_tokens=estimated_tokens,
        confidence=confidence,
        latency_ms=elapsed_ms,
    )

    logger.info(
        "supervisor_decision",
        tier=tier.value,
        model=decision.model,
        score=f"{score:.1f}",
        confidence=f"{confidence:.2f}",
        skip_enrich=decision.skip_enrich,
        latency_ms=f"{elapsed_ms:.2f}",
        msg_len=msg_len,
    )

    return decision


# ── Supervisor Node (for LangGraph integration) ──────────────────────


async def supervisor_node(state: dict, config: dict) -> dict:
    """
    LangGraph node that runs the supervisor analysis.
    Injects model selection and routing metadata into state.

    This replaces the simple classify_and_route for Sprint 29.
    """
    message = state.get("message", "")
    conversation_context = state.get("conversation_context", [])
    intent = state.get("intent", "chat")
    tool_results = state.get("tool_results", [])

    decision = analyze_complexity(
        message=message,
        conversation_depth=len(conversation_context),
        has_tool_history=bool(tool_results),
        intent=intent,
    )

    return {
        "model": decision.model,
        "fallbacks": decision.fallbacks,
        "complexity_tier": decision.tier.value,
        "skip_enrich": decision.skip_enrich,
        "supervisor_reason": decision.reason,
        "supervisor_confidence": decision.confidence,
        "supervisor_latency_ms": decision.latency_ms,
    }


# ── Metrics ───────────────────────────────────────────────────────────

_tier_counts: dict[str, int] = {
    "simple": 0,
    "moderate": 0,
    "complex": 0,
    "deep": 0,
}


def record_tier(tier: ComplexityTier) -> None:
    """Record a tier selection for metrics."""
    _tier_counts[tier.value] = _tier_counts.get(tier.value, 0) + 1


def get_tier_metrics() -> dict[str, Any]:
    """Get supervisor routing metrics."""
    total = sum(_tier_counts.values()) or 1
    economico = _tier_counts.get("simple", 0) + _tier_counts.get("moderate", 0)
    return {
        "tier_counts": dict(_tier_counts),
        "total_requests": total,
        "economico_pct": round(economico / total * 100, 1),
        "gate_met": economico / total >= 0.70,  # Épica 1 Gate: 70%
    }


def get_status() -> dict[str, Any]:
    """Return supervisor status for /health endpoint."""
    metrics = get_tier_metrics()
    return {
        "active": True,
        "version": "1.0.0-sprint29",
        "tiers": list(ComplexityTier),
        "metrics": metrics,
    }
