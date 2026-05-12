"""Dimensión 4 — Calidad Apple/Tesla.

Evalúa si la respuesta tiene el nivel de pulido, claridad y densidad que pasaría
un test "keynote-ready": una respuesta que podría mostrarse en una presentación
de producto Apple o Tesla sin avergonzar al autor. Castiga respuestas largas
sin densidad, prosa florida sin sustancia, o estructura sin remate.

Implementación PR-B: subclase delgada de ``BaseSabioDimension``.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T2 D4).
DSC: DSC-MO-006 (par bicéfalo), Obj #2 (calidad Apple/Tesla).
"""

from __future__ import annotations

from kernel.embriones.brand_engine.dimensions import BaseSabioDimension


class AppleTeslaEvaluator(BaseSabioDimension):
    """Evaluador real de D4 — calidad keynote-ready."""

    name = "D4_calidad_apple_tesla"
