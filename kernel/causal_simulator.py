"""
El Monstruo — Causal Monte Carlo Simulator (Sprint 55.5)
======================================================
Primer prototipo del Simulador Predictivo Causal (Objetivo #10).

Toma un escenario hipotético y simula N variaciones Monte Carlo
para estimar la distribución de probabilidad de diferentes outcomes.

Pipeline:
  1. Recibe escenario (pregunta + factores conocidos)
  2. Busca eventos similares en CausalKnowledgeBase
  3. Construye modelo probabilístico con factores + pesos
  4. Ejecuta N simulaciones Monte Carlo
  5. Agrega resultados en distribución de probabilidad
  6. Retorna predicción con intervalos de confianza

Ejemplo:
  Input: "¿Qué probabilidad tiene una startup de AI en 2026 de llegar a $10M ARR en 2 años?"
  Factores: [market_size=0.9, team_quality=0.8, timing=0.85, competition=0.6, funding=0.7]
  Output: {
    "probability": 0.23,
    "confidence_interval": [0.15, 0.31],
    "dominant_factors": ["market_size", "timing"],
    "risk_factors": ["competition"],
    "simulations_run": 10000
  }

Validated: numpy (ya en stack), scipy (ya en stack)
Future: PyMC para modelos Bayesianos más sofisticados
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np
import structlog

from memory.causal_kb import CausalKnowledgeBase

logger = structlog.get_logger("kernel.causal_simulator")


@dataclass
class SimulationScenario:
    """Escenario a simular."""
    question: str  # La pregunta predictiva
    known_factors: dict[str, float] = field(default_factory=dict)  # factor → valor actual (0-1)
    time_horizon: str = "1_year"  # Horizonte temporal
    category: str = "general"
    context: str = ""


@dataclass
class SimulationResult:
    """Resultado de una simulación Monte Carlo."""
    scenario: str
    probability: float  # Probabilidad estimada del outcome
    confidence_interval: tuple[float, float] = (0.0, 1.0)  # 95% CI
    dominant_factors: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    simulations_run: int = 0
    mean_outcome: float = 0.0
    std_outcome: float = 0.0
    percentiles: dict[str, float] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario,
            "probability": round(self.probability, 4),
            "confidence_interval": [round(x, 4) for x in self.confidence_interval],
            "dominant_factors": self.dominant_factors,
            "risk_factors": self.risk_factors,
            "simulations_run": self.simulations_run,
            "mean_outcome": round(self.mean_outcome, 4),
            "std_outcome": round(self.std_outcome, 4),
            "percentiles": {k: round(v, 4) for k, v in self.percentiles.items()},
            "timestamp": self.timestamp,
        }


class CausalSimulator:
    """
    Simulador Monte Carlo Causal.
    Primer prototipo — usa distribuciones Beta para modelar factores
    y sampling Monte Carlo para estimar outcomes.

    T1: simulate(scenario) ejecuta 10,000 simulaciones en <5 segundos
    T4: Distribución Beta modela correctamente la incertidumbre de cada factor
    T5: Con más eventos en CausalKB, las predicciones se vuelven más precisas
    """

    DEFAULT_SIMULATIONS = 10_000
    CONFIDENCE_LEVEL = 0.95

    def __init__(self, causal_kb: CausalKnowledgeBase):
        self._kb = causal_kb

    async def simulate(
        self,
        scenario: SimulationScenario,
        n_simulations: int = DEFAULT_SIMULATIONS,
    ) -> SimulationResult:
        """
        Ejecutar simulación Monte Carlo para un escenario.

        Método:
          1. Obtener factores base de eventos similares
          2. Combinar con factores conocidos del escenario
          3. Modelar cada factor como distribución Beta(α, β)
          4. Samplear N veces y calcular outcome agregado
          5. Retornar distribución de probabilidad

        T1: Ejecuta 10,000 simulaciones en <5 segundos (CPU puro, sin API)
        T2: Resultado incluye probability, confidence_interval, dominant_factors
        """
        logger.info(
            "simulation_start",
            question=scenario.question,
            n_simulations=n_simulations,
            known_factors=len(scenario.known_factors),
        )

        # ── Paso 1: Obtener factores históricos ────────────────────
        historical_factors = await self._get_historical_factors(scenario)

        # ── Paso 2: Combinar factores ──────────────────────────────
        combined_factors = self._combine_factors(
            historical_factors, scenario.known_factors
        )

        if not combined_factors:
            # Sin factores, retornar prior uniforme (máxima incertidumbre)
            logger.warning("simulation_no_factors", question=scenario.question)
            return SimulationResult(
                scenario=scenario.question,
                probability=0.5,
                confidence_interval=(0.2, 0.8),
                simulations_run=0,
                mean_outcome=0.5,
                std_outcome=0.25,
                percentiles={"p10": 0.2, "p25": 0.35, "p50": 0.5, "p75": 0.65, "p90": 0.8},
            )

        # ── Paso 3: Ejecutar Monte Carlo ───────────────────────────
        outcomes = self._run_monte_carlo(combined_factors, n_simulations)

        # ── Paso 4: Analizar resultados ────────────────────────────
        result = self._analyze_outcomes(outcomes, combined_factors, scenario)

        logger.info(
            "simulation_complete",
            question=scenario.question,
            probability=result.probability,
            ci=result.confidence_interval,
            simulations=result.simulations_run,
        )

        return result

    async def _get_historical_factors(
        self, scenario: SimulationScenario
    ) -> list[dict[str, Any]]:
        """Obtener factores de eventos históricos similares."""
        try:
            similar_events = await self._kb.search_similar(scenario.question, limit=5)
        except Exception as e:
            logger.warning("historical_factors_fetch_failed", error=str(e))
            return []

        all_factors = []
        for event in similar_events:
            raw = event.get("factors", "[]")
            try:
                factors = raw if isinstance(raw, list) else json.loads(raw)
                for f in factors:
                    if isinstance(f, dict):
                        f["source_event"] = event.get("title", "unknown")
                        f["source_similarity"] = event.get("similarity", 0.0)
                        all_factors.append(f)
            except (json.JSONDecodeError, TypeError):
                pass

        return all_factors

    def _combine_factors(
        self,
        historical: list[dict[str, Any]],
        known: dict[str, float],
    ) -> dict[str, dict[str, Any]]:
        """
        Combinar factores históricos con factores conocidos.
        Retorna: {factor_name: {weight, confidence, value, direction, count}}
        """
        combined: dict[str, dict[str, Any]] = {}

        # Agregar factores históricos (promediando pesos de eventos similares)
        for f in historical:
            desc = f.get("description", "unknown")
            if not desc:
                continue
            if desc not in combined:
                combined[desc] = {
                    "weight": float(f.get("weight", 0.5)),
                    "confidence": float(f.get("confidence", 0.5)),
                    "value": float(f.get("weight", 0.5)),  # Usar peso como valor base
                    "direction": f.get("direction", "positive"),
                    "count": 1,
                }
            else:
                existing = combined[desc]
                n = existing["count"]
                existing["weight"] = (existing["weight"] * n + float(f.get("weight", 0.5))) / (n + 1)
                existing["confidence"] = max(existing["confidence"], float(f.get("confidence", 0.5)))
                existing["count"] = n + 1

        # Override con factores conocidos del escenario (alta confianza)
        for factor_name, value in known.items():
            if factor_name in combined:
                combined[factor_name]["value"] = float(value)
                combined[factor_name]["confidence"] = 0.9
            else:
                combined[factor_name] = {
                    "weight": float(value),
                    "confidence": 0.9,
                    "value": float(value),
                    "direction": "positive",
                    "count": 1,
                }

        return combined

    def _run_monte_carlo(
        self,
        factors: dict[str, dict[str, Any]],
        n_simulations: int,
    ) -> np.ndarray:
        """
        Ejecutar N simulaciones Monte Carlo.

        Cada factor se modela como Beta(α, β) donde:
          α = value * confidence * 10
          β = (1 - value) * confidence * 10

        El outcome de cada simulación es el producto ponderado
        de los factores sampleados.

        T4: Distribución Beta modela correctamente la incertidumbre de cada factor.
        """
        n_factors = len(factors)
        samples = np.zeros((n_simulations, n_factors))
        weights = np.zeros(n_factors)
        directions = np.ones(n_factors)

        for i, (name, f) in enumerate(factors.items()):
            value = np.clip(float(f["value"]), 0.01, 0.99)
            confidence = np.clip(float(f["confidence"]), 0.1, 0.99)

            # Parámetros Beta — mayor concentración con mayor confianza
            alpha = value * confidence * 10
            beta_param = (1 - value) * confidence * 10

            # Samplear distribución Beta
            samples[:, i] = np.random.beta(alpha, beta_param, size=n_simulations)
            weights[i] = float(f["weight"])

            if f.get("direction") == "negative":
                directions[i] = -1.0

        # Outcome = weighted average de factores (con dirección)
        weighted_samples = samples * weights[np.newaxis, :] * directions[np.newaxis, :]
        outcomes = np.mean(weighted_samples, axis=1)

        # Normalizar a [0, 1]
        min_o = outcomes.min()
        max_o = outcomes.max()
        if max_o - min_o > 1e-10:
            outcomes = (outcomes - min_o) / (max_o - min_o)
        else:
            outcomes = np.full(n_simulations, 0.5)

        return outcomes

    def _analyze_outcomes(
        self,
        outcomes: np.ndarray,
        factors: dict[str, dict[str, Any]],
        scenario: SimulationScenario,
    ) -> SimulationResult:
        """
        Analizar distribución de outcomes.
        T2: Resultado incluye probability, confidence_interval, dominant_factors.
        """
        mean = float(np.mean(outcomes))
        std = float(np.std(outcomes))

        # Intervalo de confianza 95%
        alpha = (1 - self.CONFIDENCE_LEVEL) / 2
        ci_low = float(np.percentile(outcomes, alpha * 100))
        ci_high = float(np.percentile(outcomes, (1 - alpha) * 100))

        # Probabilidad = proporción de outcomes > 0.5 (umbral de "éxito")
        probability = float(np.mean(outcomes > 0.5))

        # Factores dominantes (top 3 por peso * valor)
        factor_impact = [
            (name, float(f["weight"]) * float(f["value"]))
            for name, f in factors.items()
        ]
        factor_impact.sort(key=lambda x: x[1], reverse=True)
        dominant = [name for name, _ in factor_impact[:3]]

        # Factores de riesgo (dirección negativa o valor bajo)
        risk = [
            name for name, f in factors.items()
            if f.get("direction") == "negative" or float(f["value"]) < 0.4
        ]

        # Percentiles
        percentiles = {
            "p10": float(np.percentile(outcomes, 10)),
            "p25": float(np.percentile(outcomes, 25)),
            "p50": float(np.percentile(outcomes, 50)),
            "p75": float(np.percentile(outcomes, 75)),
            "p90": float(np.percentile(outcomes, 90)),
        }

        return SimulationResult(
            scenario=scenario.question,
            probability=probability,
            confidence_interval=(ci_low, ci_high),
            dominant_factors=dominant,
            risk_factors=risk[:3],
            simulations_run=len(outcomes),
            mean_outcome=mean,
            std_outcome=std,
            percentiles=percentiles,
        )

    async def simulate_counterfactual(
        self,
        scenario: SimulationScenario,
        removed_factor: str,
        n_simulations: int = DEFAULT_SIMULATIONS,
    ) -> dict[str, Any]:
        """
        Simulación contrafactual: ¿Qué habría pasado SIN un factor específico?
        Compara outcome con y sin el factor para medir su impacto causal.

        T3: simulate_counterfactual() muestra impacto de remover un factor.
        """
        # Simulación con todos los factores
        result_with = await self.simulate(scenario, n_simulations)

        # Simulación sin el factor
        modified_known = {
            k: v for k, v in scenario.known_factors.items()
            if k != removed_factor
        }
        modified_scenario = SimulationScenario(
            question=scenario.question,
            known_factors=modified_known,
            time_horizon=scenario.time_horizon,
            category=scenario.category,
            context=scenario.context,
        )
        result_without = await self.simulate(modified_scenario, n_simulations)

        # Impacto causal = diferencia en probabilidad
        causal_impact = result_with.probability - result_without.probability

        return {
            "factor_removed": removed_factor,
            "probability_with": round(result_with.probability, 4),
            "probability_without": round(result_without.probability, 4),
            "causal_impact": round(causal_impact, 4),
            "interpretation": (
                f"Removing '{removed_factor}' changes probability from "
                f"{result_with.probability:.2%} to {result_without.probability:.2%} "
                f"(impact: {causal_impact:+.2%})"
            ),
        }


# ── Singleton ──────────────────────────────────────────────────────

_simulator_instance: Optional[CausalSimulator] = None


def get_causal_simulator() -> Optional[CausalSimulator]:
    """Obtener el singleton del CausalSimulator."""
    return _simulator_instance


def init_causal_simulator(causal_kb: CausalKnowledgeBase) -> CausalSimulator:
    """
    Inicializar el CausalSimulator singleton.
    Llamar desde el lifespan de main.py.
    """
    global _simulator_instance
    _simulator_instance = CausalSimulator(causal_kb=causal_kb)
    logger.info("causal_simulator_initialized", engine="monte_carlo_beta", simulations=10_000)
    return _simulator_instance
