"""
Tests Sprint 89 v2 — 4 catastros canónicos DSC-G-007.1.

Tests deterministas que NO requieren conexión a Supabase:
  - test_base_requires_table_attribute
  - test_base_lookup_works_over_views
  - test_subclass_isolation_4_catastros
  - test_load_from_db_handles_missing_keys
  - test_count_and_list_after_load
  - test_refresh_reloads
  - test_get_returns_none_for_unknown_key
  - test_table_names_match_migration_artifacts

Smoke test sobre prod (test_views_exist_and_return_rows) marcado como
@pytest.mark.smoke — solo corre si SUPABASE_DB_URL está configurado.

Sprint 89 v2 (Opción B firmada por Cowork T2-A, commit f240cdc).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock

import pytest

from kernel.catastros import (
    CatastroAgentes2026,
    CatastroBase,
    CatastroHerramientasAI,
    CatastroModelosLLM,
    CatastroSuppliers,
)


# ───────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────


def make_mock_db(rows_by_table: Dict[str, List[Dict[str, Any]]]) -> Any:
    """Crea un mock db client con .select() asíncrono."""
    mock = AsyncMock()

    async def _select(table: str, filters: Optional[Dict] = None):
        return rows_by_table.get(table, [])

    mock.select = AsyncMock(side_effect=_select)
    return mock


# ───────────────────────────────────────────────────────────────────────────
# Tests
# ───────────────────────────────────────────────────────────────────────────


def test_base_requires_table_attribute():
    """CatastroBase debe rechazar instanciación sin TABLE."""
    with pytest.raises(ValueError, match="TABLE"):
        CatastroBase(db_client=AsyncMock())


def test_subclass_isolation_4_catastros():
    """Cada subclase apunta a su tabla/vista canónica y son independientes."""
    assert CatastroModelosLLM.TABLE == "catastro_modelos_llm"
    assert CatastroAgentes2026.TABLE == "catastro_agentes_2026"
    assert CatastroHerramientasAI.TABLE == "catastro_herramientas_ai"
    assert CatastroSuppliers.TABLE == "catastro_suppliers_humanos"

    # KEY_COLUMN canónica
    for cls in (
        CatastroModelosLLM,
        CatastroAgentes2026,
        CatastroHerramientasAI,
        CatastroSuppliers,
    ):
        assert cls.KEY_COLUMN == "key"


@pytest.mark.asyncio
async def test_base_lookup_works_over_views():
    """load_from_db carga rows y get() las recupera por KEY_COLUMN."""
    fake_rows = {
        "catastro_modelos_llm": [
            {"key": "gpt-5", "name": "GPT-5", "provider": "openai"},
            {"key": "claude-opus", "name": "Claude Opus", "provider": "anthropic"},
        ]
    }
    db = make_mock_db(fake_rows)
    catastro = CatastroModelosLLM(db_client=db)
    count = await catastro.load_from_db()

    assert count == 2
    assert catastro.is_loaded is True
    assert catastro.count() == 2
    assert catastro.get("gpt-5")["provider"] == "openai"
    assert catastro.get("claude-opus")["name"] == "Claude Opus"


@pytest.mark.asyncio
async def test_load_from_db_handles_missing_keys():
    """Rows sin KEY_COLUMN se ignoran sin romper carga."""
    fake_rows = {
        "catastro_agentes_2026": [
            {"key": "agente-x", "name": "X"},
            {"name": "broken-no-key"},  # row sin key — debe ignorarse
            {"key": "agente-y", "name": "Y"},
        ]
    }
    db = make_mock_db(fake_rows)
    catastro = CatastroAgentes2026(db_client=db)
    count = await catastro.load_from_db()

    assert count == 2  # solo las 2 con key
    assert catastro.get("agente-x")["name"] == "X"
    assert catastro.get("agente-y")["name"] == "Y"


@pytest.mark.asyncio
async def test_count_and_list_after_load():
    """count() y list() reflejan el cache cargado."""
    fake_rows = {
        "catastro_suppliers_humanos": [
            {"key": "alfredo", "name": "Alfredo González", "role": "T1"},
            {"key": "manus", "name": "Manus", "role": "T3"},
            {"key": "embrion", "name": "Embrión", "role": "autonomo"},
        ]
    }
    db = make_mock_db(fake_rows)
    catastro = CatastroSuppliers(db_client=db)
    await catastro.load_from_db()

    assert catastro.count() == 3
    all_rows = catastro.list()
    assert len(all_rows) == 3
    names = {r["name"] for r in all_rows}
    assert "Alfredo González" in names
    assert "Manus" in names
    assert "Embrión" in names


@pytest.mark.asyncio
async def test_refresh_reloads():
    """refresh() re-invoca load_from_db (alias semántico)."""
    fake_rows = {
        "catastro_herramientas_ai": [
            {"key": "veo-3", "name": "Veo 3", "category": "vision_generativa"},
        ]
    }
    db = make_mock_db(fake_rows)
    catastro = CatastroHerramientasAI(db_client=db)
    await catastro.load_from_db()
    assert catastro.count() == 1

    # Mutamos los rows underlying y refresh debería detectar
    fake_rows["catastro_herramientas_ai"].append(
        {"key": "sora-2", "name": "Sora 2", "category": "vision_generativa"}
    )
    count_after = await catastro.refresh()
    assert count_after == 2
    assert catastro.get("sora-2") is not None


@pytest.mark.asyncio
async def test_get_returns_none_for_unknown_key():
    """get() devuelve None si la key no existe en cache."""
    db = make_mock_db({"catastro_modelos_llm": [{"key": "gpt-5", "name": "x"}]})
    catastro = CatastroModelosLLM(db_client=db)
    await catastro.load_from_db()

    assert catastro.get("gpt-5") is not None
    assert catastro.get("nonexistent") is None


def test_table_names_match_migration_artifacts():
    """
    Verifica que los nombres TABLE en las clases coincidan con los nombres
    declarados en las migraciones SQL (regression guard sin DB).
    """
    repo_root = Path(__file__).parent.parent
    mig_0021 = (repo_root / "migrations/sql/0021_catastro_suppliers_humanos.sql").read_text()
    mig_0022 = (repo_root / "migrations/sql/0022_catastro_vistas_dsc_g_007_1.sql").read_text()

    # 0021 crea catastro_suppliers_humanos
    assert "CREATE TABLE IF NOT EXISTS public.catastro_suppliers_humanos" in mig_0021
    assert CatastroSuppliers.TABLE == "catastro_suppliers_humanos"

    # 0022 crea las 3 vistas
    assert "CREATE OR REPLACE VIEW public.catastro_modelos_llm" in mig_0022
    assert "CREATE OR REPLACE VIEW public.catastro_agentes_2026" in mig_0022
    assert "CREATE OR REPLACE VIEW public.catastro_herramientas_ai" in mig_0022

    assert CatastroModelosLLM.TABLE == "catastro_modelos_llm"
    assert CatastroAgentes2026.TABLE == "catastro_agentes_2026"
    assert CatastroHerramientasAI.TABLE == "catastro_herramientas_ai"


def test_migration_0021_has_rls_enabled():
    """Migración 0021 debe habilitar RLS desde nacimiento (DSC-S-006 v1.1)."""
    repo_root = Path(__file__).parent.parent
    mig_0021 = (repo_root / "migrations/sql/0021_catastro_suppliers_humanos.sql").read_text()

    assert "ENABLE ROW LEVEL SECURITY" in mig_0021
    assert "CREATE POLICY" in mig_0021
    assert "service_role_only" in mig_0021


def test_migration_0022_views_protected_with_revoke_grant():
    """Migración 0022 vistas deben tener REVOKE PUBLIC + GRANT service_role (doctrina §7)."""
    repo_root = Path(__file__).parent.parent
    mig_0022 = (repo_root / "migrations/sql/0022_catastro_vistas_dsc_g_007_1.sql").read_text()

    # Las 3 vistas deben tener REVOKE + GRANT
    for view in [
        "catastro_modelos_llm",
        "catastro_agentes_2026",
        "catastro_herramientas_ai",
    ]:
        assert f"REVOKE ALL ON public.{view} FROM PUBLIC" in mig_0022
        assert f"GRANT SELECT ON public.{view} TO service_role" in mig_0022


# ───────────────────────────────────────────────────────────────────────────
# Smoke test contra producción (opcional, requiere SUPABASE_DB_URL)
# ───────────────────────────────────────────────────────────────────────────


@pytest.mark.smoke
@pytest.mark.skipif(
    not os.environ.get("SUPABASE_DB_URL"),
    reason="Requires SUPABASE_DB_URL env var for smoke test",
)
def test_views_exist_and_return_rows_in_prod():
    """Smoke test: las 3 vistas existen en prod y retornan rows."""
    import psycopg2

    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    cur = conn.cursor()
    try:
        for view in [
            "catastro_modelos_llm",
            "catastro_agentes_2026",
            "catastro_herramientas_ai",
        ]:
            cur.execute(f"SELECT COUNT(*) FROM public.{view}")
            count = cur.fetchone()[0]
            assert count > 0, f"View {view} returned 0 rows"
        # catastro_suppliers_humanos también debe existir (puede estar vacía)
        cur.execute("SELECT COUNT(*) FROM public.catastro_suppliers_humanos")
        assert cur.fetchone()[0] >= 0
    finally:
        cur.close()
        conn.close()
