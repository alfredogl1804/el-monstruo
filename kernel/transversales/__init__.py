# kernel/transversales/__init__.py
"""
El Monstruo — Capas Transversales (Obj #9).

7 Capas que se inyectan en TODO output del Monstruo per vertical:

    1. Ventas               (kernel.transversales.ventas)
    2. SEO y Descubrimiento (kernel.transversales.seo)         — pendiente
    3. Publicidad           (kernel.transversales.publicidad)  — pendiente
    4. Tendencias           (kernel.transversales.tendencias)  — pendiente
    5. Operaciones          (kernel.transversales.operaciones) — pendiente
    6. Finanzas             (kernel.transversales.finanzas)    — pendiente
    7. Resiliencia Agentica (aplica al propio Monstruo)        — separado

Plus Capa 8 Memento (anti-Sindrome-Dory) — separado, ver kernel.memento.

Patron canonico: cada Capa es un paquete con (a) interfaz que extiende
TransversalLayer (kernel.transversales.base), (b) constants per vertical
en `_canonical_constraints.py`, (c) archetypes YAML en `archetypes/` (uno
por tipo de modelo de negocio), (d) tests que parsean DSCs y asertean que
constants coinciden con texto canonico, (e) implementacion principal en
__init__.py o modulo dedicado.

Origen: Obj #9, AGENTS.md Regla Dura #2, DSC-G-002.
Patron: mirror de kernel.brand (Sprint 82) con dimension de
business-model-archetype + per-vertical hard constraints.
"""
from kernel.transversales.base import (
    BusinessModelArchetype,
    GeoRegion,
    RestrictedVerticalError,
    TransversalContext,
    TransversalLayer,
    TransversalRecommendations,
    VerticalId,
)

__all__ = [
    "BusinessModelArchetype",
    "GeoRegion",
    "RestrictedVerticalError",
    "TransversalContext",
    "TransversalLayer",
    "TransversalRecommendations",
    "VerticalId",
]
