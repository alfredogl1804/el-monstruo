"""
CatastroSuppliers — catastro canónico #4 (Suppliers humanos).

Apunta a la TABLA catastro_suppliers_humanos (creada por migración 0021).
Es la única de los 4 catastros DSC-G-007.1 que es tabla física nueva.

Migración: migrations/sql/0021_catastro_suppliers_humanos.sql
Spec: bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_89_v2_OPCION_B_KICKOFF_2026_05_12.md §T1

Sprint 89 v2 (Opción B firmada por Cowork T2-A, commit f240cdc).
"""

from kernel.catastros.base import CatastroBase


class CatastroSuppliers(CatastroBase):
    """Catastro canónico de suppliers humanos del Monstruo (DSC-G-007.1 #4)."""

    TABLE: str = "catastro_suppliers_humanos"
    KEY_COLUMN: str = "key"
