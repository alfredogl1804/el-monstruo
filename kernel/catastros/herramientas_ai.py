"""
CatastroHerramientasAI — catastro canónico #3 (Herramientas AI verticales).

Apunta a la VISTA catastro_herramientas_ai, que es UNION ALL de
catastro_vision_generativa + tool_registry.

Mapping verbatim: bridge/manus_to_cowork_S89_V2_MAPPING_2026_05_12.md §5
Migración: migrations/sql/0022_catastro_vistas_dsc_g_007_1.sql

Sprint 89 v2 (Opción B firmada por Cowork T2-A, commit f240cdc).
"""

from kernel.catastros.base import CatastroBase


class CatastroHerramientasAI(CatastroBase):
    """Catastro canónico de herramientas AI verticales (DSC-G-007.1 #3)."""

    TABLE: str = "catastro_herramientas_ai"
    KEY_COLUMN: str = "key"
