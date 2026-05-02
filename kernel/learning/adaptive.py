"""
El Monstruo — Adaptive Learning Engine (Sprint 61)
====================================================
Motor de aprendizaje adaptativo que mejora el sistema con cada interacción.

3 mecanismos de aprendizaje:
1. Pattern Recognition — detecta patrones en outcomes de proyectos
2. Feedback Loop — ajusta pesos de decisiones basado en resultados reales
3. Knowledge Distillation — comprime aprendizajes en reglas accionables

Objetivo #4: Nunca se equivoca dos veces
Sprint 61 — 2026-05-01

Soberanía:
- Supabase → in-memory fallback si no hay SUPABASE_URL
- Sabios LLM → reglas heurísticas si no hay API key
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import structlog

logger = structlog.get_logger("monstruo.learning")


# ── Excepciones con identidad ──────────────────────────────────────────────


class AprendizajePatronInvalido(ValueError):
    """El patrón de aprendizaje tiene formato inválido.

    Causa: context, outcome o lesson vacíos.
    Sugerencia: Incluir siempre el contexto del proyecto y el outcome medible.
    """


class AprendizajeFeedbackInvalido(ValueError):
    """El feedback recibido tiene campos inválidos.

    Causa: score fuera del rango [0, 1] o decision_id vacío.
    Sugerencia: score debe ser float entre 0.0 y 1.0.
    """


# ── Enums ──────────────────────────────────────────────────────────────────


class OutcomeType(str, Enum):
    """Tipos de outcomes aprendibles."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNEXPECTED = "unexpected"


class PatternCategory(str, Enum):
    """Categorías de patrones detectados."""

    DESIGN = "design"
    TECHNICAL = "technical"
    BUSINESS = "business"
    USER_BEHAVIOR = "user_behavior"
    PERFORMANCE = "performance"


# ── Dataclasses ────────────────────────────────────────────────────────────


@dataclass
class LearningPattern:
    """Patrón de aprendizaje extraído de un outcome.

    Args:
        id: Identificador único.
        category: Categoría del patrón (PatternCategory).
        context: Descripción del contexto donde ocurrió.
        outcome: Resultado observado.
        outcome_type: Tipo de outcome (OutcomeType).
        lesson: Lección accionable extraída.
        confidence: Confianza en el patrón (0.0-1.0).
        occurrences: Número de veces que se ha observado.
        last_seen: ISO 8601 UTC de la última observación.
    """

    id: str
    category: PatternCategory
    context: str
    outcome: str
    outcome_type: OutcomeType
    lesson: str
    confidence: float = 0.5
    occurrences: int = 1
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category.value,
            "context": self.context,
            "outcome": self.outcome,
            "outcome_type": self.outcome_type.value,
            "lesson": self.lesson,
            "confidence": self.confidence,
            "occurrences": self.occurrences,
            "last_seen": self.last_seen,
        }


@dataclass
class FeedbackSignal:
    """Señal de feedback para ajustar pesos de decisiones.

    Args:
        id: Identificador único.
        decision_id: ID de la decisión que se está evaluando.
        decision_type: Tipo de decisión (ej: "design_choice", "tech_stack").
        score: Score del outcome (0.0 = fracaso total, 1.0 = éxito total).
        context: Contexto adicional del feedback.
        source: Fuente del feedback ("user", "metrics", "embrion").
    """

    id: str
    decision_id: str
    decision_type: str
    score: float
    context: str
    source: str = "metrics"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "score": self.score,
            "context": self.context,
            "source": self.source,
            "timestamp": self.timestamp,
        }


@dataclass
class DistilledRule:
    """Regla destilada del aprendizaje acumulado.

    Args:
        id: Identificador único.
        rule: Enunciado de la regla en lenguaje natural.
        category: Categoría de la regla.
        confidence: Confianza en la regla (0.0-1.0).
        supporting_patterns: IDs de patrones que soportan la regla.
        times_applied: Número de veces que se aplicó la regla.
        times_successful: Número de veces que fue exitosa.
    """

    id: str
    rule: str
    category: PatternCategory
    confidence: float
    supporting_patterns: list[str]
    times_applied: int = 0
    times_successful: int = 0

    @property
    def success_rate(self) -> float:
        """Tasa de éxito de la regla."""
        return self.times_successful / max(self.times_applied, 1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "rule": self.rule,
            "category": self.category.value,
            "confidence": self.confidence,
            "supporting_patterns": len(self.supporting_patterns),
            "times_applied": self.times_applied,
            "success_rate": round(self.success_rate, 2),
        }


# ── Motor principal ────────────────────────────────────────────────────────


@dataclass
class AdaptiveLearningEngine:
    """Motor de aprendizaje adaptativo.

    Aprende de cada proyecto y ajusta el comportamiento del sistema.
    Garantiza que el Monstruo nunca cometa el mismo error dos veces.

    Args:
        _supabase: Cliente Supabase (opcional — fallback in-memory).
        _sabios: Motor LLM para destilación de reglas (opcional).

    Soberanía:
        Sin Supabase: patrones en memoria (se pierden al reiniciar).
        Sin Sabios: reglas heurísticas basadas en frecuencia.
    """

    _supabase: Optional[object] = field(default=None, repr=False)
    _sabios: Optional[object] = field(default=None, repr=False)
    _patterns: dict[str, LearningPattern] = field(default_factory=dict)
    _feedback_signals: list[FeedbackSignal] = field(default_factory=list)
    _distilled_rules: dict[str, DistilledRule] = field(default_factory=dict)
    _decision_weights: dict[str, float] = field(default_factory=dict)

    # ── Registro de Patrones ───────────────────────────────────────────────

    async def record_pattern(
        self,
        category: PatternCategory,
        context: str,
        outcome: str,
        outcome_type: OutcomeType,
        lesson: str,
        confidence: float = 0.5,
    ) -> LearningPattern:
        """Registrar un patrón de aprendizaje.

        Args:
            category: Categoría del patrón.
            context: Contexto donde ocurrió el outcome.
            outcome: Resultado observado.
            outcome_type: Tipo de outcome.
            lesson: Lección accionable extraída.
            confidence: Confianza inicial (0.0-1.0).

        Returns:
            LearningPattern registrado.

        Raises:
            AprendizajePatronInvalido: Si context, outcome o lesson están vacíos.
        """
        if not context or not outcome or not lesson:
            raise AprendizajePatronInvalido(
                "Patrón inválido: context, outcome y lesson son requeridos. "
                "Incluir siempre el contexto del proyecto y el outcome medible."
            )

        # Buscar patrón similar existente
        similar = self._find_similar_pattern(context, outcome)
        if similar:
            similar.occurrences += 1
            similar.confidence = min(1.0, similar.confidence + 0.05)
            similar.last_seen = datetime.now(timezone.utc).isoformat()
            logger.info("patron_reforzado", id=similar.id, occurrences=similar.occurrences)
            return similar

        pattern = LearningPattern(
            id=str(uuid.uuid4())[:8],
            category=category,
            context=context,
            outcome=outcome,
            outcome_type=outcome_type,
            lesson=lesson,
            confidence=confidence,
        )
        self._patterns[pattern.id] = pattern

        # Persistir en Supabase
        if self._supabase:
            try:
                self._supabase.table("learning_patterns").insert(pattern.to_dict()).execute()
            except Exception as e:
                logger.warning("pattern_persist_failed", error=str(e))

        logger.info(
            "patron_registrado",
            id=pattern.id,
            category=category.value,
            outcome_type=outcome_type.value,
            confidence=confidence,
        )

        # Trigger destilación si hay suficientes patrones
        if len(self._patterns) % 10 == 0:
            await self.distill_rules()

        return pattern

    def _find_similar_pattern(self, context: str, outcome: str) -> Optional[LearningPattern]:
        """Buscar patrón similar por keywords.

        Args:
            context: Contexto a comparar.
            outcome: Outcome a comparar.

        Returns:
            LearningPattern similar si existe, None si no.
        """
        context_words = set(context.lower().split())
        outcome_words = set(outcome.lower().split())

        for pattern in self._patterns.values():
            p_context_words = set(pattern.context.lower().split())
            p_outcome_words = set(pattern.outcome.lower().split())

            context_overlap = len(context_words & p_context_words) / max(len(context_words), 1)
            outcome_overlap = len(outcome_words & p_outcome_words) / max(len(outcome_words), 1)

            if context_overlap > 0.7 and outcome_overlap > 0.7:
                return pattern

        return None

    # ── Feedback Loop ──────────────────────────────────────────────────────

    async def receive_feedback(
        self, decision_id: str, decision_type: str, score: float, context: str, source: str = "metrics"
    ) -> FeedbackSignal:
        """Recibir señal de feedback para ajustar pesos.

        Args:
            decision_id: ID de la decisión evaluada.
            decision_type: Tipo de decisión.
            score: Score del outcome (0.0-1.0).
            context: Contexto del feedback.
            source: Fuente del feedback.

        Returns:
            FeedbackSignal registrado.

        Raises:
            AprendizajeFeedbackInvalido: Si score está fuera de [0, 1] o decision_id vacío.
        """
        if not (0.0 <= score <= 1.0):
            raise AprendizajeFeedbackInvalido(f"Score inválido: {score}. Debe ser float entre 0.0 y 1.0.")
        if not decision_id:
            raise AprendizajeFeedbackInvalido("decision_id vacío. Incluir el ID de la decisión que se evalúa.")

        signal = FeedbackSignal(
            id=str(uuid.uuid4())[:8],
            decision_id=decision_id,
            decision_type=decision_type,
            score=score,
            context=context,
            source=source,
        )
        self._feedback_signals.append(signal)

        # Ajustar peso de la decisión
        current_weight = self._decision_weights.get(decision_type, 0.5)
        # Actualización incremental: mueve el peso hacia el score
        new_weight = current_weight + 0.1 * (score - current_weight)
        self._decision_weights[decision_type] = round(new_weight, 3)

        # Persistir en Supabase
        if self._supabase:
            try:
                self._supabase.table("feedback_signals").insert(signal.to_dict()).execute()
            except Exception as e:
                logger.warning("feedback_persist_failed", error=str(e))

        logger.info("feedback_recibido", decision_type=decision_type, score=score, new_weight=new_weight, source=source)
        return signal

    def get_decision_weight(self, decision_type: str) -> float:
        """Obtener peso aprendido para un tipo de decisión.

        Args:
            decision_type: Tipo de decisión.

        Returns:
            Peso aprendido (0.0-1.0). Default: 0.5.
        """
        return self._decision_weights.get(decision_type, 0.5)

    # ── Knowledge Distillation ─────────────────────────────────────────────

    async def distill_rules(self) -> list[DistilledRule]:
        """Destilar patrones acumulados en reglas accionables.

        Returns:
            Lista de reglas destiladas con alta confianza.
        """
        if len(self._patterns) < 5:
            return []

        # Agrupar patrones por categoría y outcome_type
        by_category: dict[str, list[LearningPattern]] = {}
        for pattern in self._patterns.values():
            key = f"{pattern.category.value}_{pattern.outcome_type.value}"
            by_category.setdefault(key, []).append(pattern)

        new_rules = []

        for key, patterns in by_category.items():
            if len(patterns) < 3:
                continue

            # Patrones con alta confianza
            high_conf = [p for p in patterns if p.confidence >= 0.7]
            if not high_conf:
                continue

            if self._sabios:
                rule_text = await self._distill_with_llm(high_conf)
            else:
                rule_text = self._distill_heuristic(high_conf)

            if rule_text:
                category_str, _ = key.split("_", 1)
                rule = DistilledRule(
                    id=str(uuid.uuid4())[:8],
                    rule=rule_text,
                    category=PatternCategory(category_str),
                    confidence=sum(p.confidence for p in high_conf) / len(high_conf),
                    supporting_patterns=[p.id for p in high_conf],
                )
                self._distilled_rules[rule.id] = rule
                new_rules.append(rule)

        if new_rules:
            logger.info("reglas_destiladas", count=len(new_rules), total_rules=len(self._distilled_rules))

        return new_rules

    async def _distill_with_llm(self, patterns: list[LearningPattern]) -> str:
        """Destilar regla con LLM.

        Args:
            patterns: Lista de patrones a destilar.

        Returns:
            Regla en lenguaje natural.
        """
        lessons = "\n".join([f"- {p.lesson} (confianza: {p.confidence:.2f})" for p in patterns])
        prompt = f"""Dado estos patrones de aprendizaje observados:
{lessons}

Destila UNA regla general accionable que capture el patrón común.
La regla debe ser específica, accionable y en español.
Responde SOLO con la regla, sin explicación adicional."""

        try:
            return await self._sabios.ask(prompt)
        except Exception as e:
            logger.warning("distill_llm_failed", error=str(e))
            return self._distill_heuristic(patterns)

    @staticmethod
    def _distill_heuristic(patterns: list[LearningPattern]) -> str:
        """Destilar regla heurística sin LLM.

        Args:
            patterns: Lista de patrones a destilar.

        Returns:
            Regla heurística basada en la lección más frecuente.
        """
        if not patterns:
            return ""
        # Usar la lección del patrón con mayor confianza
        best = max(patterns, key=lambda p: p.confidence)
        return f"[Heurística] {best.lesson} (basado en {len(patterns)} observaciones)"

    # ── Consultas ──────────────────────────────────────────────────────────

    def get_relevant_rules(self, category: PatternCategory, min_confidence: float = 0.6) -> list[DistilledRule]:
        """Obtener reglas relevantes para una categoría.

        Args:
            category: Categoría de reglas a buscar.
            min_confidence: Confianza mínima (default: 0.6).

        Returns:
            Lista de reglas ordenadas por confianza descendente.
        """
        rules = [r for r in self._distilled_rules.values() if r.category == category and r.confidence >= min_confidence]
        return sorted(rules, key=lambda r: r.confidence, reverse=True)

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return {
            "patrones_registrados": len(self._patterns),
            "feedback_signals": len(self._feedback_signals),
            "reglas_destiladas": len(self._distilled_rules),
            "decision_weights": self._decision_weights,
            "patrones_por_categoria": {
                cat.value: len([p for p in self._patterns.values() if p.category == cat]) for cat in PatternCategory
            },
        }


# ── Singleton ──────────────────────────────────────────────────────────────

_learning_engine_instance: Optional[AdaptiveLearningEngine] = None


def get_adaptive_learning_engine() -> Optional[AdaptiveLearningEngine]:
    """Obtener instancia singleton del Adaptive Learning Engine."""
    return _learning_engine_instance


def init_adaptive_learning_engine(supabase=None, sabios=None) -> AdaptiveLearningEngine:
    """Inicializar el Adaptive Learning Engine.

    Args:
        supabase: Cliente Supabase (opcional).
        sabios: Motor LLM para destilación (opcional).

    Returns:
        Instancia singleton de AdaptiveLearningEngine.
    """
    global _learning_engine_instance
    _learning_engine_instance = AdaptiveLearningEngine(
        _supabase=supabase,
        _sabios=sabios,
    )
    logger.info(
        "adaptive_learning_engine_inicializado", con_supabase=supabase is not None, con_sabios=sabios is not None
    )
    return _learning_engine_instance
