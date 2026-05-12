"""
Catastros canónicos DSC-G-007.1 — capa semántica sobre tablas/vistas en Supabase.

Sprint 89 v2 (Opción B firmada por Cowork T2-A, commit f240cdc).

Los 4 catastros canónicos exponen contratos limpios DSC-G-007.1 sobre la
realidad de producción:
  - CatastroModelosLLM    → VIEW catastro_modelos_llm (sobre catastro_modelos)
  - CatastroAgentes2026   → VIEW catastro_agentes_2026 (sobre catastro_agentes)
  - CatastroHerramientasAI → VIEW catastro_herramientas_ai (UNION ALL de
                            catastro_vision_generativa + tool_registry)
  - CatastroSuppliers     → TABLE catastro_suppliers_humanos (única tabla NUEVA)

Mapping verbatim: bridge/manus_to_cowork_S89_V2_MAPPING_2026_05_12.md
"""

from kernel.catastros.base import CatastroBase
from kernel.catastros.modelos_llm import CatastroModelosLLM
from kernel.catastros.agentes_2026 import CatastroAgentes2026
from kernel.catastros.herramientas_ai import CatastroHerramientasAI
from kernel.catastros.suppliers_humanos import CatastroSuppliers

__all__ = [
    "CatastroBase",
    "CatastroModelosLLM",
    "CatastroAgentes2026",
    "CatastroHerramientasAI",
    "CatastroSuppliers",
]
