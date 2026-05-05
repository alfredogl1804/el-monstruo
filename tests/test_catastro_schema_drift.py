"""
tests/test_catastro_schema_drift.py

Tests del Mini-Sprint 86.4.5 pre-B2 (Schema Canónico Auto-validado).

Garantizan que:
  1. El generador Pydantic-from-SQL siempre puede correr sobre las migrations
     actuales sin errores.
  2. El archivo `kernel/catastro/schema_generated.py` está sincronizado con
     las migrations (modo --check del generator).
  3. El audit de drift entre `schema_generated.py` (SQL) y `schema.py`
     (manual) no detecta drifts NUEVOS fuera del baseline conocido.

Si CUALQUIERA de estos tests falla en CI:
  - Una migration cambió y nadie regeneró schema_generated.py, O
  - schema.py manual divergió del baseline esperado, O
  - El generador necesita actualización (tipo nuevo, sintaxis nueva).

En cualquier caso, el bug se detecta ANTES de llegar a producción.

Autor: Hilo Manus · 2026-05-05
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GEN_SCRIPT = REPO_ROOT / "scripts" / "_gen_catastro_pydantic_from_sql.py"
AUDIT_SCRIPT = REPO_ROOT / "scripts" / "_audit_catastro_schema_drift.py"
GENERATED_FILE = REPO_ROOT / "kernel" / "catastro" / "schema_generated.py"


@pytest.fixture(scope="module")
def python_executable() -> str:
    return sys.executable


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=60)


# ============================================================================
# Tests
# ============================================================================


def test_generator_script_exists():
    """El script generator debe existir."""
    assert GEN_SCRIPT.exists(), f"falta {GEN_SCRIPT}"
    assert GEN_SCRIPT.is_file()


def test_audit_script_exists():
    """El script de audit debe existir."""
    assert AUDIT_SCRIPT.exists(), f"falta {AUDIT_SCRIPT}"
    assert AUDIT_SCRIPT.is_file()


def test_generated_file_exists():
    """schema_generated.py debe existir (correr generator si falla)."""
    assert GENERATED_FILE.exists(), (
        f"falta {GENERATED_FILE} — correr `python3 scripts/_gen_catastro_pydantic_from_sql.py`"
    )


def test_generated_file_importable():
    """schema_generated.py debe ser importable (Python válido)."""
    from kernel.catastro import schema_generated  # noqa: F401
    assert hasattr(schema_generated, "TABLE_COLUMNS")
    assert hasattr(schema_generated, "__SOURCE_HASH__")
    assert hasattr(schema_generated, "__GENERATED_AT__")


def test_generated_has_all_5_tables():
    """Las 5 tablas del Catastro deben estar generadas."""
    from kernel.catastro.schema_generated import TABLE_COLUMNS

    expected = {
        "catastro_modelos",
        "catastro_historial",
        "catastro_eventos",
        "catastro_notas",
        "catastro_curadores",
    }
    assert set(TABLE_COLUMNS.keys()) == expected, (
        f"diferencia: faltan={expected - set(TABLE_COLUMNS.keys())}, "
        f"sobran={set(TABLE_COLUMNS.keys()) - expected}"
    )


def test_generated_has_validated_by_in_modelos():
    """Migration 019.1 hotfix debe estar reflejada (validated_by)."""
    from kernel.catastro.schema_generated import TABLE_COLUMNS
    assert "validated_by" in TABLE_COLUMNS["catastro_modelos"], (
        "validated_by debe estar en catastro_modelos (de migration 019.1)"
    )


def test_generated_uses_correct_column_names():
    """Verifica que los nombres canónicos del schema (que generaron 3 bugs en"""
    """Bloque 1) están correctamente capturados."""
    from kernel.catastro.schema_generated import TABLE_COLUMNS
    cols = TABLE_COLUMNS["catastro_modelos"]
    # Estos nombres son los CORRECTOS según el SQL productivo
    assert "ultima_validacion" in cols, "debe ser ultima_validacion (no last_validated_at)"
    assert "dominios" in cols, "debe ser dominios plural text[] (no dominio singular)"
    # Confirmar que los nombres BUGGY no aparecen en SQL
    assert "last_validated_at" not in cols, "last_validated_at NO existe en SQL"
    assert "dominio" not in cols, "dominio singular NO existe en SQL"


def test_pydantic_models_instantiable():
    """Los Row models generados deben ser instanciables con datos válidos."""
    from kernel.catastro.schema_generated import (
        CatastroModeloRow,
        CatastroHistorialRow,
        CatastroEventoRow,
        CatastroNotaRow,
        CatastroCuradorRow,
    )

    # NOT NULL fields requeridos por SQL DDL
    m = CatastroModeloRow(
        id="test", nombre="Test", proveedor="Test", macroarea="llm"
    )
    assert m.id == "test"

    # Campos array text[] → list[str]
    m2 = CatastroModeloRow(
        id="test2", nombre="T2", proveedor="P2", macroarea="llm",
        dominios=["llm_frontier", "vision"],
    )
    assert m2.dominios == ["llm_frontier", "vision"]


def test_generator_check_mode_passes(python_executable):
    """`--check` del generator debe pasar (file actual sincronizado con migrations)."""
    result = _run([python_executable, str(GEN_SCRIPT), "--check"])
    assert result.returncode == 0, (
        f"generator --check falló (drift). stdout=\n{result.stdout}\nstderr=\n{result.stderr}"
    )


def test_audit_drift_no_new_drifts(python_executable):
    """Audit drift debe pasar (no hay drifts NUEVOS fuera del baseline)."""
    result = _run([python_executable, str(AUDIT_SCRIPT)])
    assert result.returncode == 0, (
        f"drift NUEVO detectado. stdout=\n{result.stdout}\nstderr=\n{result.stderr}\n"
        f"HINT: si es drift aceptable, agregar a BASELINE_DRIFT en _audit_catastro_schema_drift.py"
    )


def test_audit_json_output_well_formed(python_executable):
    """Audit con --json debe emitir JSON válido."""
    import json
    result = _run([python_executable, str(AUDIT_SCRIPT), "--json"])
    # Exit code puede ser 0 o 1 según drift, pero JSON debe parsear
    parsed = json.loads(result.stdout)
    assert "drift_detected" in parsed
    assert "tables" in parsed
    assert "catastro_modelos" in parsed["tables"]


def test_table_columns_consistency_with_pydantic_fields():
    """TABLE_COLUMNS debe coincidir con los campos de cada Pydantic model."""
    from kernel.catastro.schema_generated import (
        TABLE_COLUMNS,
        CatastroModeloRow,
        CatastroHistorialRow,
        CatastroEventoRow,
        CatastroNotaRow,
        CatastroCuradorRow,
    )

    mapping = {
        "catastro_modelos": CatastroModeloRow,
        "catastro_historial": CatastroHistorialRow,
        "catastro_eventos": CatastroEventoRow,
        "catastro_notas": CatastroNotaRow,
        "catastro_curadores": CatastroCuradorRow,
    }
    for table, cls in mapping.items():
        sql_cols = set(TABLE_COLUMNS[table])
        pyd_cols = set(cls.model_fields.keys())
        assert sql_cols == pyd_cols, (
            f"{table}: TABLE_COLUMNS != Pydantic fields. "
            f"diff={sql_cols.symmetric_difference(pyd_cols)}"
        )
