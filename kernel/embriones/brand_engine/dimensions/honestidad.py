"""Dimensión 2 — Honestidad pura.

Evalúa si la respuesta candidata admite explícitamente lo que no sabe en vez
de inventar datos, fingir certeza, o emitir hedging vago. Castiga alucinaciones
(fechas inventadas, links muertos, citas inexistentes).

Implementación PR-B: subclase delgada de ``BaseSabioDimension``.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T2 D2).
DSC: DSC-MO-006 (par bicéfalo).
"""

from __future__ import annotations

from kernel.embriones.brand_engine.dimensions import BaseSabioDimension


class HonestidadEvaluator(BaseSabioDimension):
    """Evaluador real de D2 — honestidad sobre lo que se ignora."""

    name = "D2_honestidad_pura"
