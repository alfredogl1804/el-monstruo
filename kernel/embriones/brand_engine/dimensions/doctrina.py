"""Dimensión 3 — Consistencia doctrinal.

Evalúa que la respuesta NO contradiga ningún DSC con ``estado=firme``, NO invente
canonizaciones nuevas, y NO use naming prohibido por DSC-G-004
(service/handler/utils/helper/misc).

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T2 D3).
DSC: DSC-MO-006, DSC-G-004 (naming canónico).
"""

from __future__ import annotations

from kernel.embriones.brand_engine.dimensions import DimensionEvaluator, DimensionResult


class DoctrinaEvaluator(DimensionEvaluator):
    """Evaluador de D3 — consistencia doctrinal.

    PR-A: stub que retorna passed=True con score=1.0. PR-B reemplaza.
    """

    name = "D3_consistencia_doctrina"

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
