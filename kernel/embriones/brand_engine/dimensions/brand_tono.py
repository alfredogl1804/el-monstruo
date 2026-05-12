"""Dimensión 1 — Brand DNA tono.

Evalúa si la voz de la respuesta candidata es reconocible como Monstruo
(directo, magnánimo, implacable, metáforas industriales: forja+graphite+acero)
o si suena a chatbot corporativo genérico ("estoy aquí para ayudarte",
disclaimers innecesarios de IA, frases plantilla).

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T2 D1).
DSC: DSC-MO-006 (par bicéfalo), Regla Dura #4 (Brand Engine — toda producción tiene identidad).
"""

from __future__ import annotations

from kernel.embriones.brand_engine.dimensions import DimensionEvaluator, DimensionResult


class BrandTonoEvaluator(DimensionEvaluator):
    """Evaluador de D1 — tono de marca Monstruo.

    PR-A: stub que retorna passed=True con score=1.0 sin llamar LLM real.
    PR-B: implementación real con Anthropic SDK + prompt en prompts/d1_brand_tono.txt.
    """

    name = "D1_brand_tono"

    def evaluate(
        self,
        respuesta_candidata: str,
        criterios: list[str],
        umbral_pass: float,
    ) -> DimensionResult:
        # PR-A scaffolding: passed=True por default. PR-B reemplaza.
        return DimensionResult(
            score=1.0,
            passed=True,
            reason=None,
            cost_usd=0.0,
            latency_ms=0,
        )
