"""
CatastroModelosLLM — catastro canónico #1 (LLMs).

Apunta a la VISTA catastro_modelos_llm (sobre catastro_modelos).
Mapping verbatim: bridge/manus_to_cowork_S89_V2_MAPPING_2026_05_12.md §3
Migración: migrations/sql/0022_catastro_vistas_dsc_g_007_1.sql

Sprint 89 v2 (Opción B firmada por Cowork T2-A, commit f240cdc).
"""

from kernel.catastros.base import CatastroBase


class CatastroModelosLLM(CatastroBase):
    """Catastro canónico de modelos LLM (DSC-G-007.1 #1)."""

    TABLE: str = "catastro_modelos_llm"
    KEY_COLUMN: str = "key"
