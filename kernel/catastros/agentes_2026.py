"""
CatastroAgentes2026 — catastro canónico #2 (Agentes 2026 de las 21 biblias).

Apunta a la VISTA catastro_agentes_2026 (sobre catastro_agentes).
Mapping verbatim: bridge/manus_to_cowork_S89_V2_MAPPING_2026_05_12.md §4
Migración: migrations/sql/0022_catastro_vistas_dsc_g_007_1.sql

Sprint 89 v2 (Opción B firmada por Cowork T2-A, commit f240cdc).
"""

from kernel.catastros.base import CatastroBase


class CatastroAgentes2026(CatastroBase):
    """Catastro canónico de agentes 2026 (DSC-G-007.1 #2)."""

    TABLE: str = "catastro_agentes_2026"
    KEY_COLUMN: str = "key"
