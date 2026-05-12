"""Brand Engine — segundo embrión del par bicéfalo del Monstruo.

Validador VETO sobre output del Embrión 1 antes de salir al transport.
Evalúa 4 dimensiones (tono, honestidad, doctrina, calidad Apple/Tesla)
mediante un Sabio canónico interno (Claude Opus 4.7 default).

Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md
DSC aplicables: DSC-MO-006 (par bicéfalo), DSC-MO-011 (Embryo Patch Lane).
Naming canónico: DSC-G-004 (no service/handler/utils/helper/misc).
"""

from kernel.embriones.brand_engine.brand_engine import (
    BrandEngine,
    ValidationResult,
    ValidationVerdict,
)

__all__ = ["BrandEngine", "ValidationResult", "ValidationVerdict"]
