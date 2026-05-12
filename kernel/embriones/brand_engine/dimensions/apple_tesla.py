"""Dimensión 4 — Calidad Apple/Tesla.

Evalúa si la respuesta pasaría el test "esto daría orgullo en keynote de Apple":
craft visible (no rellenado), estructura mínima necesaria, evita listas largas
innecesarias y formato sobre-cargado.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T2 D4).
DSC: DSC-MO-006, Objetivo Maestro #2 (Apple/Tesla quality).
"""

from __future__ import annotations

from kernel.embriones.brand_engine.dimensions import DimensionEvaluator, DimensionResult


class AppleTeslaEvaluator(DimensionEvaluator):
    """Evaluador de D4 — calidad Apple/Tesla.

    PR-A: stub que retorna passed=True con score=1.0. PR-B reemplaza.
    """

    name = "D4_calidad_apple_tesla"

    def evaluate(
        self,
        respuesta_candidata: str,
        criterios: list[str],
        umbral_pass: float,
    ) -> DimensionResult:
        return DimensionResult(
            score=1.0,
            passed=True,
            reason=None,
            cost_usd=0.0,
            latency_ms=0,
        )
