"""
kernel/cost_optimizer.py
Sprint 62.5 — Cost Optimization Engine (Objetivo #5: Gasolina Magna vs Premium)

Motor de optimización de costos de LLM que selecciona automáticamente
el modelo correcto para cada tarea según complejidad y presupuesto.

Filosofía: No siempre necesitas GPT-4o. Un análisis de sentiment puede hacerse
con Gemini Flash a 1/20 del costo. El Monstruo lo sabe y lo aplica.

Soberanía: Si no hay modelos disponibles, usa heurísticas de costo fijo.
Alternativa: Tabla de costos estática sin llamadas a APIs de precios.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import structlog

logger = structlog.get_logger("cost_optimizer")


# --- Excepciones con identidad ---

class ModeloNoDisponible(Exception):
    """Ningún modelo disponible cumple los requisitos de la tarea."""
    def __init__(self, tarea: str, budget_restante: float):
        super().__init__(
            f"No hay modelos disponibles para '{tarea}' con budget restante ${budget_restante:.4f}. "
            f"Incrementa el budget diario en DAILY_LLM_BUDGET o reduce la complejidad de la tarea."
        )
        self.tarea = tarea
        self.budget_restante = budget_restante


class BudgetAgotado(Exception):
    """El budget diario de LLM ha sido agotado."""
    def __init__(self, gasto_hoy: float, limite: float):
        super().__init__(
            f"Budget diario de LLM agotado: ${gasto_hoy:.4f} / ${limite:.2f}. "
            f"El sistema continúa con modelos gratuitos o modo offline hasta mañana."
        )
        self.gasto_hoy = gasto_hoy
        self.limite = limite


# --- Enums ---

class NivelComplejidad(str, Enum):
    """Nivel de complejidad de una tarea de LLM."""
    TRIVIAL = "trivial"       # Clasificación, sentiment, extracción simple
    SIMPLE = "simple"         # Resumen, traducción, Q&A básico
    MODERADO = "moderado"     # Análisis, generación de contenido
    COMPLEJO = "complejo"     # Razonamiento multi-paso, código complejo
    CRITICO = "critico"       # Decisiones estratégicas, arquitectura


class TipoTarea(str, Enum):
    """Tipo de tarea para optimización de modelo."""
    CLASIFICACION = "clasificacion"
    RESUMEN = "resumen"
    GENERACION = "generacion"
    RAZONAMIENTO = "razonamiento"
    CODIGO = "codigo"
    VISION = "vision"
    EMBEDDING = "embedding"
    MODERACION = "moderacion"


# --- Modelos disponibles con costos ---

@dataclass
class ModelConfig:
    """Configuración y costos de un modelo LLM."""
    id: str
    provider: str
    name: str
    input_cost_per_1k: float    # USD por 1K tokens de input
    output_cost_per_1k: float   # USD por 1K tokens de output
    context_window: int
    max_output_tokens: int
    strengths: list[str]
    complejidad_minima: NivelComplejidad
    complejidad_maxima: NivelComplejidad
    disponible: bool = True
    latency_ms_avg: int = 1000

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estima el costo de una llamada."""
        return (input_tokens / 1000 * self.input_cost_per_1k +
                output_tokens / 1000 * self.output_cost_per_1k)


AVAILABLE_MODELS: list[ModelConfig] = [
    # Gratuitos / muy baratos
    ModelConfig(
        id="gemini-2.0-flash-lite", provider="google", name="Gemini 2.0 Flash Lite",
        input_cost_per_1k=0.000075, output_cost_per_1k=0.0003,
        context_window=1_000_000, max_output_tokens=8192,
        strengths=["clasificacion", "resumen", "moderacion"],
        complejidad_minima=NivelComplejidad.TRIVIAL,
        complejidad_maxima=NivelComplejidad.SIMPLE,
        latency_ms_avg=500,
    ),
    ModelConfig(
        id="gemini-2.0-flash", provider="google", name="Gemini 2.0 Flash",
        input_cost_per_1k=0.0001, output_cost_per_1k=0.0004,
        context_window=1_000_000, max_output_tokens=8192,
        strengths=["generacion", "resumen", "razonamiento"],
        complejidad_minima=NivelComplejidad.SIMPLE,
        complejidad_maxima=NivelComplejidad.MODERADO,
        latency_ms_avg=800,
    ),
    ModelConfig(
        id="gpt-4o-mini", provider="openai", name="GPT-4o Mini",
        input_cost_per_1k=0.00015, output_cost_per_1k=0.0006,
        context_window=128_000, max_output_tokens=16384,
        strengths=["codigo", "razonamiento", "generacion"],
        complejidad_minima=NivelComplejidad.SIMPLE,
        complejidad_maxima=NivelComplejidad.MODERADO,
        latency_ms_avg=1200,
    ),
    # Medios
    ModelConfig(
        id="gemini-2.5-flash", provider="google", name="Gemini 2.5 Flash",
        input_cost_per_1k=0.00025, output_cost_per_1k=0.001,
        context_window=1_000_000, max_output_tokens=65536,
        strengths=["razonamiento", "codigo", "vision"],
        complejidad_minima=NivelComplejidad.MODERADO,
        complejidad_maxima=NivelComplejidad.COMPLEJO,
        latency_ms_avg=2000,
    ),
    ModelConfig(
        id="claude-3-5-haiku", provider="anthropic", name="Claude 3.5 Haiku",
        input_cost_per_1k=0.0008, output_cost_per_1k=0.004,
        context_window=200_000, max_output_tokens=8192,
        strengths=["razonamiento", "codigo", "generacion"],
        complejidad_minima=NivelComplejidad.MODERADO,
        complejidad_maxima=NivelComplejidad.COMPLEJO,
        latency_ms_avg=1500,
    ),
    # Premium
    ModelConfig(
        id="gpt-4o", provider="openai", name="GPT-4o",
        input_cost_per_1k=0.0025, output_cost_per_1k=0.01,
        context_window=128_000, max_output_tokens=16384,
        strengths=["razonamiento", "codigo", "vision", "critico"],
        complejidad_minima=NivelComplejidad.COMPLEJO,
        complejidad_maxima=NivelComplejidad.CRITICO,
        latency_ms_avg=3000,
    ),
    ModelConfig(
        id="claude-3-5-sonnet", provider="anthropic", name="Claude 3.5 Sonnet",
        input_cost_per_1k=0.003, output_cost_per_1k=0.015,
        context_window=200_000, max_output_tokens=8192,
        strengths=["razonamiento", "codigo", "critico"],
        complejidad_minima=NivelComplejidad.COMPLEJO,
        complejidad_maxima=NivelComplejidad.CRITICO,
        latency_ms_avg=2500,
    ),
    ModelConfig(
        id="gemini-2.5-pro", provider="google", name="Gemini 2.5 Pro",
        input_cost_per_1k=0.00125, output_cost_per_1k=0.01,
        context_window=2_000_000, max_output_tokens=65536,
        strengths=["razonamiento", "codigo", "critico", "vision"],
        complejidad_minima=NivelComplejidad.COMPLEJO,
        complejidad_maxima=NivelComplejidad.CRITICO,
        latency_ms_avg=4000,
    ),
]

# Mapa de tipo de tarea → complejidad sugerida
TASK_COMPLEXITY_MAP: dict[TipoTarea, NivelComplejidad] = {
    TipoTarea.CLASIFICACION: NivelComplejidad.TRIVIAL,
    TipoTarea.MODERACION: NivelComplejidad.TRIVIAL,
    TipoTarea.RESUMEN: NivelComplejidad.SIMPLE,
    TipoTarea.EMBEDDING: NivelComplejidad.TRIVIAL,
    TipoTarea.GENERACION: NivelComplejidad.MODERADO,
    TipoTarea.VISION: NivelComplejidad.MODERADO,
    TipoTarea.CODIGO: NivelComplejidad.COMPLEJO,
    TipoTarea.RAZONAMIENTO: NivelComplejidad.COMPLEJO,
}


@dataclass
class OptimizationDecision:
    """Decisión de optimización de modelo."""
    modelo_seleccionado: str
    provider: str
    costo_estimado: float
    costo_alternativa_premium: float
    ahorro_estimado: float
    razon: str
    input_tokens_estimados: int
    output_tokens_estimados: int
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "modelo": self.modelo_seleccionado,
            "provider": self.provider,
            "costo_estimado_usd": round(self.costo_estimado, 6),
            "ahorro_estimado_usd": round(self.ahorro_estimado, 6),
            "razon": self.razon,
            "timestamp": self.timestamp,
        }


class CostOptimizer:
    """
    Motor de optimización de costos de LLM.

    Selecciona automáticamente el modelo más económico que puede
    manejar la complejidad de cada tarea, respetando el budget diario.
    """

    def __init__(self, daily_budget_usd: float = 5.0):
        """
        Args:
            daily_budget_usd: Budget diario máximo para LLM en USD.
        """
        self.daily_budget_usd = daily_budget_usd
        self._gasto_hoy: float = 0.0
        self._decisiones: list[OptimizationDecision] = []
        self._ultimo_reset: str = datetime.now(timezone.utc).date().isoformat()
        self._modelos = {m.id: m for m in AVAILABLE_MODELS}

    def select_model(
        self,
        task_type: TipoTarea,
        complejidad: Optional[NivelComplejidad] = None,
        input_tokens: int = 1000,
        output_tokens: int = 500,
        force_premium: bool = False,
    ) -> OptimizationDecision:
        """
        Selecciona el modelo óptimo para una tarea.

        Args:
            task_type: Tipo de tarea a realizar.
            complejidad: Nivel de complejidad explícito (opcional).
            input_tokens: Tokens de input estimados.
            output_tokens: Tokens de output estimados.
            force_premium: Forzar modelo premium independientemente del costo.

        Returns:
            OptimizationDecision con el modelo seleccionado y métricas.

        Raises:
            ModeloNoDisponible: Si no hay modelos dentro del budget.
            BudgetAgotado: Si el budget diario está agotado.
        """
        self._reset_if_new_day()

        budget_restante = self.daily_budget_usd - self._gasto_hoy
        if budget_restante <= 0 and not force_premium:
            raise BudgetAgotado(self._gasto_hoy, self.daily_budget_usd)

        nivel = complejidad or TASK_COMPLEXITY_MAP.get(task_type, NivelComplejidad.MODERADO)

        # Filtrar modelos compatibles con la complejidad
        candidatos = [
            m for m in AVAILABLE_MODELS
            if m.disponible
            and self._nivel_compatible(nivel, m.complejidad_minima, m.complejidad_maxima)
            and (task_type.value in m.strengths or True)  # Preferir por strengths
        ]

        if not candidatos:
            raise ModeloNoDisponible(task_type.value, budget_restante)

        if force_premium:
            # Seleccionar el más capaz
            candidatos.sort(key=lambda m: m.input_cost_per_1k, reverse=True)
        else:
            # Seleccionar el más económico que cumple los requisitos
            candidatos.sort(key=lambda m: m.estimate_cost(input_tokens, output_tokens))

        modelo = candidatos[0]
        costo_estimado = modelo.estimate_cost(input_tokens, output_tokens)

        # Costo de alternativa premium (para mostrar el ahorro)
        premium = max(AVAILABLE_MODELS, key=lambda m: m.input_cost_per_1k)
        costo_premium = premium.estimate_cost(input_tokens, output_tokens)
        ahorro = max(0.0, costo_premium - costo_estimado)

        decision = OptimizationDecision(
            modelo_seleccionado=modelo.id,
            provider=modelo.provider,
            costo_estimado=costo_estimado,
            costo_alternativa_premium=costo_premium,
            ahorro_estimado=ahorro,
            razon=f"Modelo más económico para {task_type.value} de complejidad {nivel.value}",
            input_tokens_estimados=input_tokens,
            output_tokens_estimados=output_tokens,
        )

        self._decisiones.append(decision)

        logger.info(
            "modelo_seleccionado",
            modelo=modelo.id,
            tarea=task_type.value,
            costo_estimado=round(costo_estimado, 6),
            ahorro=round(ahorro, 6),
        )

        return decision

    def register_actual_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """
        Registra el costo real de una llamada y actualiza el gasto del día.

        Args:
            model_id: ID del modelo usado.
            input_tokens: Tokens de input reales.
            output_tokens: Tokens de output reales.

        Returns:
            Costo real de la llamada en USD.
        """
        modelo = self._modelos.get(model_id)
        if not modelo:
            logger.warning("modelo_desconocido_en_registro", model_id=model_id)
            return 0.0

        costo = modelo.estimate_cost(input_tokens, output_tokens)
        self._gasto_hoy += costo

        logger.info(
            "costo_registrado",
            modelo=model_id,
            costo=round(costo, 6),
            gasto_hoy=round(self._gasto_hoy, 4),
            budget_restante=round(self.daily_budget_usd - self._gasto_hoy, 4),
        )

        return costo

    def get_daily_stats(self) -> dict:
        """Retorna estadísticas del día actual."""
        return {
            "gasto_hoy_usd": round(self._gasto_hoy, 4),
            "budget_diario_usd": self.daily_budget_usd,
            "budget_restante_usd": round(self.daily_budget_usd - self._gasto_hoy, 4),
            "porcentaje_usado": round(self._gasto_hoy / self.daily_budget_usd * 100, 1),
            "decisiones_hoy": len(self._decisiones),
            "fecha": self._ultimo_reset,
        }

    def to_dict(self) -> dict:
        """Serialización para el Command Center."""
        return {
            **self.get_daily_stats(),
            "modelos_disponibles": len([m for m in AVAILABLE_MODELS if m.disponible]),
            "ultima_decision": self._decisiones[-1].to_dict() if self._decisiones else None,
        }

    def _nivel_compatible(
        self,
        nivel: NivelComplejidad,
        minimo: NivelComplejidad,
        maximo: NivelComplejidad,
    ) -> bool:
        """Verifica si un nivel de complejidad está dentro del rango del modelo."""
        niveles = list(NivelComplejidad)
        idx = niveles.index(nivel)
        idx_min = niveles.index(minimo)
        idx_max = niveles.index(maximo)
        return idx_min <= idx <= idx_max

    def _reset_if_new_day(self) -> None:
        """Resetea el gasto si es un nuevo día."""
        hoy = datetime.now(timezone.utc).date().isoformat()
        if hoy != self._ultimo_reset:
            logger.info("budget_reset_nuevo_dia", dia_anterior=self._ultimo_reset, gasto_anterior=self._gasto_hoy)
            self._gasto_hoy = 0.0
            self._decisiones = []
            self._ultimo_reset = hoy


# --- Singleton ---

_cost_optimizer: CostOptimizer | None = None


def get_cost_optimizer() -> CostOptimizer:
    """Retorna el singleton del CostOptimizer."""
    global _cost_optimizer
    if _cost_optimizer is None:
        import os
        budget = float(os.getenv("DAILY_LLM_BUDGET", "5.0"))
        _cost_optimizer = CostOptimizer(daily_budget_usd=budget)
    return _cost_optimizer


def init_cost_optimizer(daily_budget_usd: float = 5.0) -> CostOptimizer:
    """Inicializa el singleton del CostOptimizer."""
    global _cost_optimizer
    _cost_optimizer = CostOptimizer(daily_budget_usd=daily_budget_usd)
    return _cost_optimizer
