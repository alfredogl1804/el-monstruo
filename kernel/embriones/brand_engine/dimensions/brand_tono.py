"""Dimensión 1 — Brand DNA tono.

Evalúa si la voz de la respuesta candidata es reconocible como Monstruo
(directo, magnánimo, implacable, metáforas industriales cuando aportan) o si
suena a chatbot corporativo genérico (disclaimers innecesarios, frases plantilla).

Implementación PR-B: subclase delgada de ``BaseSabioDimension``. Toda la lógica
(prompt, router, fallback, parsing, scoring) vive en la base. Aquí solo se
declara el nombre canónico de la dimensión.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T2 D1).
DSC: DSC-MO-006 (par bicéfalo).
"""

from __future__ import annotations

from kernel.embriones.brand_engine.dimensions import BaseSabioDimension


class BrandTonoEvaluator(BaseSabioDimension):
    """Evaluador real de D1 — tono de marca Monstruo."""

    name = "D1_brand_tono"
