"""
El Monstruo — Prediction Validator (Sprint 56.2)
================================================
Feedback loop del Simulador Causal.

Ciclo:
  1. Registrar predicción con fecha de vencimiento
  2. Cuando la fecha llega, investigar qué pasó realmente (Perplexity Sonar)
  3. Comparar predicción vs realidad (LLM assessment)
  4. Ajustar pesos de factores causales
  5. Registrar lección aprendida

Tabla Supabase: `predictions`
  - id, scenario, predicted_probability, predicted_at
  - validation_date, actual_outcome, accuracy_score
  - factors_used, factors_adjusted, lesson_learned

Este es el mecanismo que hace que el Simulador MEJORE con el tiempo.
Sin esto, el simulador es estático y eventualmente obsoleto.

Obj #10: "precisión que sube perpetuamente" — este módulo es el motor de ese crecimiento.

Validated: APScheduler 3.11.2 (MIT), Perplexity Sonar (ya en stack),
           OpenAI GPT-4o-mini (bajo costo para assessment semántico)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from uuid import uuid4

import httpx
import structlog

logger = structlog.get_logger("kernel.prediction_validator")


# ── Prediction dataclass ──────────────────────────────────────────────────────

@dataclass
class Prediction:
    """Una predicción registrada para validación futura."""
    prediction_id: str = field(default_factory=lambda: str(uuid4()))
    scenario: str = ""
    predicted_probability: float = 0.5
    confidence_interval: tuple[float, float] = (0.0, 1.0)
    dominant_factors: list[str] = field(default_factory=list)
    factors_used: list[dict[str, Any]] = field(default_factory=list)
    predicted_at: Optional[str] = None
    validation_date: Optional[str] = None  # YYYY-MM-DD — cuándo validar
    status: str = "pending"  # pending | validated | expired | cancelled

    # Post-validación
    actual_outcome: Optional[str] = None
    outcome_probability: Optional[float] = None  # 0=no ocurrió, 1=ocurrió exactamente
    accuracy_score: Optional[float] = None       # 1 - |predicted - actual|
    factors_adjusted: list[dict[str, Any]] = field(default_factory=list)
    lesson_learned: Optional[str] = None
    validated_at: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "scenario": self.scenario,
            "predicted_probability": self.predicted_probability,
            "confidence_interval": list(self.confidence_interval),
            "dominant_factors": self.dominant_factors,
            "factors_used": self.factors_used,
            "predicted_at": self.predicted_at,
            "validation_date": self.validation_date,
            "status": self.status,
            "actual_outcome": self.actual_outcome,
            "outcome_probability": self.outcome_probability,
            "accuracy_score": self.accuracy_score,
            "factors_adjusted": self.factors_adjusted,
            "lesson_learned": self.lesson_learned,
            "validated_at": self.validated_at,
        }

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> "Prediction":
        """Reconstruir Prediction desde fila de Supabase."""
        ci_raw = row.get("confidence_interval", "[0.0, 1.0]")
        if isinstance(ci_raw, str):
            ci_list = json.loads(ci_raw)
        elif isinstance(ci_raw, list):
            ci_list = ci_raw
        else:
            ci_list = [0.0, 1.0]

        fu_raw = row.get("factors_used", "[]")
        if isinstance(fu_raw, str):
            factors_used = json.loads(fu_raw)
        elif isinstance(fu_raw, list):
            factors_used = fu_raw
        else:
            factors_used = []

        fa_raw = row.get("factors_adjusted", "[]")
        if isinstance(fa_raw, str):
            factors_adjusted = json.loads(fa_raw)
        elif isinstance(fa_raw, list):
            factors_adjusted = fa_raw
        else:
            factors_adjusted = []

        return cls(
            prediction_id=row.get("id", str(uuid4())),
            scenario=row.get("scenario", ""),
            predicted_probability=float(row.get("predicted_probability", 0.5)),
            confidence_interval=(float(ci_list[0]), float(ci_list[1])) if len(ci_list) >= 2 else (0.0, 1.0),
            dominant_factors=row.get("dominant_factors") or [],
            factors_used=factors_used,
            predicted_at=row.get("predicted_at"),
            validation_date=row.get("validation_date"),
            status=row.get("status", "pending"),
            actual_outcome=row.get("actual_outcome"),
            outcome_probability=row.get("outcome_probability"),
            accuracy_score=row.get("accuracy_score"),
            factors_adjusted=factors_adjusted,
            lesson_learned=row.get("lesson_learned"),
            validated_at=row.get("validated_at"),
        )


# ── PredictionValidator ───────────────────────────────────────────────────────

class PredictionValidator:
    """
    Motor de validación de predicciones.
    Cierra el feedback loop del Simulador Causal.

    Flujo de uso:
      1. SimuladorCausal llama register_prediction() después de generar una predicción
      2. EmbrionScheduler ejecuta validate_due_predictions() diariamente a las 3am UTC
      3. validate_due_predictions() investiga outcomes reales y ajusta pesos causales
      4. Los ajustes se persisten en Supabase para mejorar predicciones futuras
    """

    TABLE = "predictions"

    def __init__(
        self,
        db=None,
        search_fn=None,
        causal_kb=None,
    ):
        """
        Args:
            db: Supabase client para persistencia
            search_fn: Función async de búsqueda (Perplexity) — fn(query) -> str
            causal_kb: CausalKnowledgeBase para ajustar pesos de factores
        """
        self._db = db
        self._search = search_fn
        self._causal_kb = causal_kb
        self._openai_key = os.environ.get("OPENAI_API_KEY")
        self._openai_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self._sonar_key = os.environ.get("SONAR_API_KEY")
        self._pending_count: int = 0
        self._total_validated: int = 0
        self._total_accuracy_sum: float = 0.0

    async def initialize(self) -> None:
        """Cargar conteo de predicciones pendientes desde Supabase."""
        if not self._db:
            logger.info("prediction_validator_initialized_no_db", pending=0)
            return
        try:
            # Contar predicciones pendientes
            rows = await self._db.select(self.TABLE, filters={"status": "pending"})
            self._pending_count = len(rows) if rows else 0
            logger.info("prediction_validator_initialized", pending=self._pending_count)
        except Exception as e:
            logger.warning("prediction_validator_init_partial", error=str(e))

    # ── Registro de predicciones ──────────────────────────────────────────────

    async def register_prediction(
        self,
        scenario: str,
        probability: float,
        confidence_interval: tuple[float, float] = (0.0, 1.0),
        dominant_factors: Optional[list[str]] = None,
        factors_used: Optional[list[dict[str, Any]]] = None,
        validation_date: Optional[str] = None,
        time_horizon_days: int = 30,
    ) -> str:
        """
        Registrar una predicción para validación futura.

        Args:
            scenario: Descripción del escenario predicho
            probability: Probabilidad predicha (0.0-1.0)
            confidence_interval: Intervalo de confianza (low, high)
            dominant_factors: Factores causales dominantes (descripciones)
            factors_used: Lista completa de factores con pesos
            validation_date: Fecha YYYY-MM-DD para validar (default: hoy + time_horizon_days)
            time_horizon_days: Días hasta validación si no se especifica validation_date

        Returns:
            prediction_id (UUID string)
        """
        if not validation_date:
            val_date = datetime.now(timezone.utc) + timedelta(days=time_horizon_days)
            validation_date = val_date.strftime("%Y-%m-%d")

        prediction = Prediction(
            scenario=scenario,
            predicted_probability=max(0.0, min(1.0, probability)),
            confidence_interval=confidence_interval,
            dominant_factors=dominant_factors or [],
            factors_used=factors_used or [],
            predicted_at=datetime.now(timezone.utc).isoformat(),
            validation_date=validation_date,
        )

        if self._db:
            try:
                await self._db.upsert(self.TABLE, {
                    "id": prediction.prediction_id,
                    "scenario": prediction.scenario,
                    "predicted_probability": prediction.predicted_probability,
                    "confidence_interval": json.dumps(list(prediction.confidence_interval)),
                    "dominant_factors": prediction.dominant_factors,
                    "factors_used": json.dumps(prediction.factors_used),
                    "predicted_at": prediction.predicted_at,
                    "validation_date": prediction.validation_date,
                    "status": "pending",
                })
            except Exception as e:
                logger.warning("prediction_persist_failed", error=str(e))

        self._pending_count += 1
        logger.info(
            "prediction_registered",
            prediction_id=prediction.prediction_id,
            scenario=scenario[:80],
            probability=probability,
            validation_date=validation_date,
            horizon_days=time_horizon_days,
        )

        return prediction.prediction_id

    # ── Validación de predicciones vencidas ───────────────────────────────────

    async def validate_due_predictions(self) -> list[dict[str, Any]]:
        """
        Validar todas las predicciones cuya fecha de validación ha llegado.
        Este método se ejecuta diariamente via EmbrionScheduler (3am UTC).

        Returns:
            Lista de resultados de validación con accuracy scores
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if not self._db:
            logger.warning("prediction_validator_no_db")
            return []

        # Obtener predicciones pendientes
        try:
            all_pending = await self._db.select(self.TABLE, filters={"status": "pending"})
        except Exception as e:
            logger.error("prediction_fetch_failed", error=str(e))
            return []

        if not all_pending:
            logger.info("no_pending_predictions")
            return []

        # Filtrar por fecha de validación
        due = [
            p for p in all_pending
            if p.get("validation_date", "9999-99-99") <= today
        ]

        if not due:
            logger.info("no_due_predictions", today=today, total_pending=len(all_pending))
            return []

        logger.info("validation_cycle_start", due=len(due), today=today)

        results = []
        for pred_row in due:
            try:
                result = await self._validate_single(pred_row)
                results.append(result)
            except Exception as e:
                logger.error(
                    "prediction_validation_failed",
                    prediction_id=pred_row.get("id"),
                    error=str(e),
                )

        avg_accuracy = (
            sum(r.get("accuracy", 0) for r in results) / len(results)
            if results else 0.0
        )

        logger.info(
            "validation_cycle_complete",
            validated=len(results),
            avg_accuracy=round(avg_accuracy, 3),
            remaining_pending=self._pending_count,
        )

        return results

    async def _validate_single(self, pred_row: dict) -> dict[str, Any]:
        """Validar una predicción individual — el corazón del feedback loop."""
        scenario = pred_row.get("scenario", "")
        predicted_prob = float(pred_row.get("predicted_probability", 0.5))
        prediction_id = pred_row.get("id", "")

        # Paso 1: Investigar qué pasó realmente (Perplexity)
        actual_outcome = await self._research_outcome(scenario)

        # Paso 2: Evaluar si el evento ocurrió (LLM assessment semántico)
        outcome_prob = await self._assess_outcome(scenario, actual_outcome, predicted_prob)

        # Paso 3: Calcular accuracy score
        accuracy = round(1.0 - abs(predicted_prob - outcome_prob), 4)

        # Paso 4: Calcular ajustes a factores causales
        fu_raw = pred_row.get("factors_used", "[]")
        if isinstance(fu_raw, str):
            factors_used = json.loads(fu_raw)
        elif isinstance(fu_raw, list):
            factors_used = fu_raw
        else:
            factors_used = []

        adjustments = self._calculate_factor_adjustments(
            factors_used, predicted_prob, outcome_prob
        )

        # Paso 5: Extraer lección aprendida
        lesson = self._extract_lesson(scenario, predicted_prob, outcome_prob, adjustments)

        # Paso 6: Actualizar predicción en Supabase
        if self._db:
            try:
                await self._db.update(
                    self.TABLE,
                    {
                        "status": "validated",
                        "actual_outcome": actual_outcome[:2000] if actual_outcome else None,
                        "outcome_probability": outcome_prob,
                        "accuracy_score": accuracy,
                        "factors_adjusted": json.dumps(adjustments),
                        "lesson_learned": lesson,
                        "validated_at": datetime.now(timezone.utc).isoformat(),
                    },
                    filters={"id": prediction_id},
                )
            except Exception as e:
                logger.warning("prediction_update_failed", prediction_id=prediction_id, error=str(e))

        # Paso 7: Aplicar ajustes a la Causal KB (v1: solo log; v2: actualiza pesos)
        if self._causal_kb and adjustments:
            await self._apply_adjustments_to_kb(adjustments)

        self._pending_count = max(0, self._pending_count - 1)
        self._total_validated += 1
        self._total_accuracy_sum += accuracy

        logger.info(
            "prediction_validated",
            prediction_id=prediction_id,
            scenario=scenario[:80],
            predicted=predicted_prob,
            actual=outcome_prob,
            accuracy=accuracy,
            adjustments=len(adjustments),
            lesson=lesson[:100] if lesson else None,
        )

        return {
            "prediction_id": prediction_id,
            "scenario": scenario,
            "predicted": predicted_prob,
            "actual": outcome_prob,
            "accuracy": accuracy,
            "adjustments": len(adjustments),
            "lesson": lesson,
        }

    # ── Investigación de outcomes ─────────────────────────────────────────────

    async def _research_outcome(self, scenario: str) -> str:
        """Investigar qué pasó realmente con el escenario predicho via Perplexity."""
        query = (
            f"What actually happened with the following scenario? "
            f"Provide current status, outcome, and key facts: {scenario}"
        )

        # Intentar con search_fn inyectada
        if self._search:
            try:
                result = await self._search(query)
                return result if isinstance(result, str) else json.dumps(result)
            except Exception as e:
                logger.warning("outcome_search_fn_failed", error=str(e))

        # Fallback: Perplexity directo
        if self._sonar_key:
            try:
                return await self._call_perplexity_for_outcome(query)
            except Exception as e:
                logger.warning("outcome_perplexity_failed", error=str(e))

        return "Unable to research outcome: no search function available"

    async def _call_perplexity_for_outcome(self, query: str) -> str:
        """Llamar a Perplexity Sonar para investigar el outcome real."""
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._sonar_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a fact-checker. Given a scenario that was predicted "
                                "to occur, research what actually happened. Be concise and factual. "
                                "Focus on: did it happen? what was the actual outcome? key facts."
                            ),
                        },
                        {"role": "user", "content": query},
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.1,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    # ── Assessment semántico ──────────────────────────────────────────────────

    async def _assess_outcome(
        self, scenario: str, actual_outcome: str, predicted_prob: float
    ) -> float:
        """
        Evaluar si el evento predicho ocurrió (0.0 = no ocurrió, 1.0 = ocurrió exactamente).
        Usa LLM para evaluación semántica cuando está disponible.
        """
        # Intentar assessment via LLM (más preciso)
        if self._openai_key:
            try:
                llm_score = await self._llm_assess_outcome(scenario, actual_outcome)
                if llm_score is not None:
                    return llm_score
            except Exception as e:
                logger.warning("llm_assessment_failed", error=str(e))

        # Fallback: heurística basada en keywords
        return self._heuristic_assess_outcome(actual_outcome)

    async def _llm_assess_outcome(self, scenario: str, actual_outcome: str) -> Optional[float]:
        """Usar GPT-4o-mini para evaluar semánticamente si el outcome ocurrió."""
        prompt = f"""Given this prediction scenario and the actual outcome, rate how much the predicted event occurred on a scale from 0.0 to 1.0.

Prediction scenario: {scenario[:500]}

Actual outcome research: {actual_outcome[:1000]}

Return ONLY a JSON object: {{"score": 0.75, "reasoning": "brief explanation"}}
Where score 0.0 = did not occur at all, 1.0 = occurred exactly as predicted."""

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{self._openai_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._openai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 200,
                    "response_format": {"type": "json_object"},
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                content = json.loads(data["choices"][0]["message"]["content"])
                score = float(content.get("score", 0.5))
                return max(0.0, min(1.0, score))
        return None

    def _heuristic_assess_outcome(self, actual_outcome: str) -> float:
        """Heurística basada en keywords para evaluar el outcome."""
        outcome_lower = actual_outcome.lower()

        positive_indicators = [
            "succeeded", "achieved", "happened", "confirmed", "reached",
            "surpassed", "completed", "launched", "approved", "passed",
            "grew", "increased", "expanded", "won", "acquired",
        ]
        negative_indicators = [
            "failed", "did not", "hasn't", "unlikely", "cancelled",
            "abandoned", "rejected", "declined", "fell", "dropped",
            "missed", "lost", "shutdown", "bankrupt",
        ]

        pos_count = sum(1 for w in positive_indicators if w in outcome_lower)
        neg_count = sum(1 for w in negative_indicators if w in outcome_lower)

        if pos_count > neg_count:
            return min(0.9, 0.5 + pos_count * 0.12)
        elif neg_count > pos_count:
            return max(0.1, 0.5 - neg_count * 0.12)
        return 0.5

    # ── Ajuste de factores causales ───────────────────────────────────────────

    def _calculate_factor_adjustments(
        self,
        factors_used: list[dict],
        predicted: float,
        actual: float,
    ) -> list[dict[str, Any]]:
        """
        Calcular ajustes a los factores basado en el error de predicción.

        Lógica:
          - Si predijimos alto y fue bajo (error < 0) → factores positivos sobre-estimados
          - Si predijimos bajo y fue alto (error > 0) → factores positivos sub-estimados
          - Ajuste conservador: 10% del error por factor
        """
        error = actual - predicted  # Positivo = sub-estimamos, negativo = sobre-estimamos
        adjustments = []

        for factor in factors_used:
            direction = factor.get("direction", "positive")
            weight = float(factor.get("weight", 0.5))

            # Ajuste proporcional al error (conservador)
            if direction == "positive":
                new_weight = weight + (error * 0.1)
            elif direction == "negative":
                new_weight = weight - (error * 0.1)
            else:
                continue  # Factores neutros no se ajustan

            # Clamp entre 0.05 y 0.95
            new_weight = max(0.05, min(0.95, new_weight))

            # Solo registrar cambios significativos (>1%)
            if abs(new_weight - weight) > 0.01:
                adjustments.append({
                    "description": factor.get("description", "")[:100],
                    "category": factor.get("category", "general"),
                    "old_weight": round(weight, 4),
                    "new_weight": round(new_weight, 4),
                    "adjustment": round(new_weight - weight, 4),
                    "reason": "over-estimated" if error < 0 else "under-estimated",
                })

        return adjustments

    def _extract_lesson(
        self,
        scenario: str,
        predicted: float,
        actual: float,
        adjustments: list,
    ) -> str:
        """Extraer una lección concisa y accionable de la validación."""
        error = abs(predicted - actual)
        direction = "under" if actual > predicted else "over"

        if error < 0.1:
            return (
                f"Prediction accurate (error={error:.2f}). "
                f"Model well-calibrated for this type of scenario."
            )
        elif error < 0.3:
            top_adj = adjustments[0]["description"] if adjustments else "unknown factor"
            return (
                f"Moderate {direction}-estimation (error={error:.2f}). "
                f"Key factor '{top_adj}' needs weight adjustment. "
                f"{len(adjustments)} factors adjusted."
            )
        else:
            return (
                f"Significant {direction}-estimation (error={error:.2f}). "
                f"Model needs recalibration for this scenario type. "
                f"Consider adding missing causal factors. "
                f"{len(adjustments)} factors adjusted."
            )

    async def _apply_adjustments_to_kb(self, adjustments: list[dict]) -> None:
        """
        Aplicar ajustes de peso a eventos similares en la Causal KB.
        v1: Solo loguea los ajustes (no modifica la KB directamente).
        v2 (Sprint 57+): Actualiza embeddings y pesos en Supabase.
        """
        for adj in adjustments:
            logger.info(
                "factor_weight_adjusted",
                factor=adj["description"][:60],
                category=adj.get("category", "?"),
                old=adj["old_weight"],
                new=adj["new_weight"],
                delta=adj["adjustment"],
                reason=adj["reason"],
            )

    # ── Stats y utilidades ────────────────────────────────────────────────────

    def get_stats(self) -> dict[str, Any]:
        """Estadísticas del validador para el EmbrionScheduler."""
        avg_accuracy = (
            round(self._total_accuracy_sum / self._total_validated, 4)
            if self._total_validated > 0 else None
        )
        return {
            "pending_predictions": self._pending_count,
            "total_validated": self._total_validated,
            "average_accuracy": avg_accuracy,
            "status": "active",
        }

    async def get_recent_validations(self, limit: int = 10) -> list[dict[str, Any]]:
        """Obtener las últimas validaciones para reporting."""
        if not self._db:
            return []
        try:
            rows = await self._db.select(
                self.TABLE,
                filters={"status": "validated"},
                limit=limit,
                order_by="validated_at",
                desc=True,
            )
            return rows or []
        except Exception as e:
            logger.warning("get_recent_validations_failed", error=str(e))
            return []


# ── Singleton factory ─────────────────────────────────────────────────────────

_prediction_validator_instance: Optional[PredictionValidator] = None


def get_prediction_validator() -> Optional[PredictionValidator]:
    """Obtener la instancia singleton del PredictionValidator."""
    return _prediction_validator_instance


def init_prediction_validator(
    db=None,
    search_fn=None,
    causal_kb=None,
) -> PredictionValidator:
    """Inicializar el singleton del PredictionValidator."""
    global _prediction_validator_instance
    _prediction_validator_instance = PredictionValidator(
        db=db,
        search_fn=search_fn,
        causal_kb=causal_kb,
    )
    return _prediction_validator_instance
