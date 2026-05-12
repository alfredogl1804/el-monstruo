"""Dimensión 3 — Consistencia doctrinal.

Evalúa si la respuesta contradice algún DSC firme (Decisión Soberana
Canonizada) del Monstruo, alguna regla dura de AGENTS.md, o algún objetivo
maestro. El Sabio recibe la lista de DSCs y reglas duras como criterios y
verifica consistencia.

Implementación PR-B: subclase delgada de ``BaseSabioDimension``.

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T2 D3).
DSC: DSC-MO-006 (par bicéfalo), DSC-G-008 (consistencia doctrinal).
"""

from __future__ import annotations

from kernel.embriones.brand_engine.dimensions import BaseSabioDimension


class DoctrinaEvaluator(BaseSabioDimension):
    """Evaluador real de D3 — consistencia con doctrina canonizada."""

    name = "D3_consistencia_doctrina"
