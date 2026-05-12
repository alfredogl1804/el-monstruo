"""Dimensiones canónicas del Brand Engine.

Cada dimensión es un evaluador especializado que recibe la respuesta candidata
y emite un ``DimensionResult`` con score numérico y veredicto binario contra
un umbral configurable.

Las 4 dimensiones canónicas (DSC-MO-006):
    D1 — Brand DNA tono (¿suena a Monstruo o a chatbot genérico?)
    D2 — Honestidad pura (¿admite lo que no sabe?)
    D3 — Consistencia doctrinal (¿contradice algún DSC firme?)
    D4 — Calidad Apple/Tesla (¿pasaría test "keynote-ready"?)

Naming canónico DSC-G-004: archivo por dimensión con nombre de dominio,
NO `dimension_a.py`/`dimension_b.py`/`helper.py`.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T1-T2).
"""

from __future__ import annotations

import abc
import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class DimensionResult:
    """Resultado de evaluar una dimensión individual sobre una respuesta candidata.

    Atributos
    ---------
    score : float entre 0.0 (peor) y 1.0 (mejor).
    passed : bool — True si score >= umbral configurado en YAML.
    reason : razón estructurada cuando passed=False (None cuando passed=True).
    cost_usd : costo de la llamada al Sabio para esta dimensión.
    latency_ms : latencia de esta dimensión específica.
    """

    score: float
    passed: bool
    reason: Optional[str]
    cost_usd: float
    latency_ms: int


class DimensionEvaluator(abc.ABC):
    """Interfaz canónica para todas las dimensiones del Brand Engine.

    Cada dimensión concreta implementa ``evaluate(respuesta_candidata, criterios, umbral_pass)``
    y retorna un ``DimensionResult``. PR-A solo expone esta interfaz abstracta;
    PR-B implementa los 4 evaluadores reales con llamadas a Anthropic SDK.
    """

    name: str = "DimensionEvaluator"

    @abc.abstractmethod
    def evaluate(
        self,
        respuesta_candidata: str,
        criterios: list[str],
        umbral_pass: float,
    ) -> DimensionResult:
        """Evalúa la respuesta contra los criterios y emite DimensionResult."""
        raise NotImplementedError
