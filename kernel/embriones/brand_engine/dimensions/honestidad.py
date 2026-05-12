"""Dimensión 2 — Honestidad pura.

Evalúa si la respuesta admite explícitamente lo que no sabe, cita evidencia
para claims factuales, y evita el patrón PR-friendly ("claro que sí" sin sustancia,
aproximaciones presentadas como certezas).

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T2 D2).
DSC: DSC-MO-006 (par bicéfalo).
"""

from __future__ import annotations

from kernel.embriones.brand_engine.dimensions import DimensionEvaluator, DimensionResult


class HonestidadEvaluator(DimensionEvaluator):
    """Evaluador de D2 — honestidad pura.

    PR-A: stub que retorna passed=True con score=1.0. PR-B reemplaza.
    """

    name = "D2_honestidad_pura"

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
