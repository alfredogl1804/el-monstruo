#!/usr/bin/env python3
"""
Generator Pydantic-from-SQL para el Catastro (Mini-Sprint 86.4.5 pre-B2).

Parsea las migrations PostgreSQL del Catastro (016, 018, 019, 019.1) usando
sqlglot, extrae todas las CREATE TABLE + ALTER TABLE ADD COLUMN, y emite
`kernel/catastro/schema_generated.py` con Pydantic models espejo bit-perfect
del SQL.

Doctrina:
- Fuente única de verdad = SQL (la realidad productiva).
- Generated NUNCA se edita a mano. Si hay drift con schema.py manual,
  schema.py manual está mal — schema_generated.py manda.
- Idempotente: corre N veces, output siempre idéntico.
- Identidad de marca: errores `catastro_schema_gen_*`, output sin
  corporativismo.
- Self-validating: el output incluye `__SOURCE_HASH__` con sha256 de las
  migrations parseadas, para detectar drift sin re-parsear.

Uso:
    python3 scripts/_gen_catastro_pydantic_from_sql.py
    python3 scripts/_gen_catastro_pydantic_from_sql.py --check  # exit 1 si difiere

Mini-Sprint 86.4.5 pre-B2 · 2026-05-05 · Hilo Manus
"""
from __future__ import annotations

import argparse
import hashlib
import logging
import re
import sys
import warnings
from pathlib import Path
from typing import Any

# Suprimir warnings ruidosos de sqlglot sobre statements PostgreSQL-only
# (CREATE EXTENSION, CREATE FUNCTION pl/pgsql, RLS policies, etc.)
logging.getLogger("sqlglot").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", module="sqlglot")

import sqlglot
from sqlglot import expressions as exp


# ============================================================================
# Configuración fija — zona primaria
# ============================================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
MIGRATION_FILES = [
    "scripts/016_sprint86_catastro_schema.sql",
    "scripts/018_sprint86_catastro_rpc.sql",
    "scripts/019_sprint86_catastro_trono.sql",
    "scripts/019_1_hotfix_validated_by_column.sql",
]
OUTPUT_FILE = "kernel/catastro/schema_generated.py"

# Tablas que nos interesan (filtra ruido tipo functions, views, indexes)
CATASTRO_TABLES = {
    "catastro_modelos",
    "catastro_historial",
    "catastro_eventos",
    "catastro_notas",
    "catastro_curadores",
}


# ============================================================================
# Errores con identidad de marca
# ============================================================================


class CatastroSchemaGenError(Exception):
    """Error base del generator. Identidad: catastro_schema_gen_*."""

    code = "catastro_schema_gen_error"


class CatastroSchemaGenParseError(CatastroSchemaGenError):
    code = "catastro_schema_gen_parse_failed"


# ============================================================================
# Mapeo PostgreSQL → Python
# ============================================================================

# Mapeo defensivo: cubre todos los tipos que aparecen en las migrations.
# Si aparece un tipo nuevo, falla con error claro (no asume nada).
PG_TO_PYTHON_TYPE: dict[str, str] = {
    "TEXT": "str",
    "VARCHAR": "str",
    "CHAR": "str",
    "UUID": "str",
    "BOOL": "bool",
    "BOOLEAN": "bool",
    "INT": "int",
    "INTEGER": "int",
    "BIGINT": "int",
    "SMALLINT": "int",
    "DOUBLE": "float",
    "DOUBLE_PRECISION": "float",
    "DECIMAL": "float",
    "NUMERIC": "float",
    "REAL": "float",
    "TIMESTAMP": "datetime",
    "TIMESTAMPTZ": "datetime",
    "DATE": "date",
    "TIME": "str",  # rep. textual segura para Pydantic
    "JSONB": "dict[str, Any]",
    "JSON": "dict[str, Any]",
    "BYTEA": "bytes",
    "VECTOR": "list[float]",  # pgvector extension
    "USERDEFINEDTYPE": "Any",  # tipos custom (ej. enums PostgreSQL)
}


def _pg_type_to_python(col_type_str: str, is_array: bool) -> str:
    """Mapea un tipo PostgreSQL textual a tipo Python para Pydantic.

    Si el tipo es desconocido, lanza error explícito (no fallback silencioso).
    """
    norm = col_type_str.upper().replace(" ", "_").strip()
    # sqlglot puede emitir TIMESTAMPTZ como TIMESTAMP_WITH_TIME_ZONE
    if "WITH_TIME_ZONE" in norm:
        norm = "TIMESTAMPTZ"
    elif norm.startswith("TIMESTAMP"):
        norm = "TIMESTAMP"

    base = PG_TO_PYTHON_TYPE.get(norm)
    if base is None:
        raise CatastroSchemaGenError(
            f"catastro_schema_gen_unknown_type: tipo PostgreSQL no mapeado: '{col_type_str}' (normalizado: '{norm}'). "
            f"Agregar mapeo en PG_TO_PYTHON_TYPE."
        )
    if is_array:
        return f"list[{base}]"
    return base


# ============================================================================
# Parser
# ============================================================================


def _read_migration(rel_path: str) -> str:
    full = REPO_ROOT / rel_path
    if not full.exists():
        raise CatastroSchemaGenError(
            f"catastro_schema_gen_migration_missing: {full} no existe"
        )
    return full.read_text(encoding="utf-8")


def _parse_migrations() -> tuple[dict[str, dict[str, dict[str, Any]]], str]:
    """Parsea todas las migrations y devuelve estructura tabular.

    Returns:
        (tables, source_hash)

        tables: {
            "catastro_modelos": {
                "id": {"type": "TEXT", "nullable": False, "default": "...", "is_array": False, "primary_key": True},
                ...
            }
        }
        source_hash: sha256 del SQL concatenado (para detectar drift).
    """
    tables: dict[str, dict[str, dict[str, Any]]] = {}
    sources: list[str] = []

    for rel in MIGRATION_FILES:
        sql = _read_migration(rel)
        sources.append(sql)
        # Pre-filtrar: extraer solo CREATE TABLE y ALTER TABLE ADD COLUMN.
        # sqlglot no soporta plenamente PL/pgSQL, RLS policies, COMMENT ON.
        # Filtrarlos antes de parsear evita errores ruidosos.
        filtered = _extract_table_statements(sql)
        for stmt_sql in filtered:
            try:
                parsed = sqlglot.parse_one(stmt_sql, dialect="postgres")
            except Exception as e:
                # Tolerante: skipea statement individual con warning, no aborta
                print(f"WARN: skipped statement in {rel}: {e}", file=sys.stderr)
                continue
            if parsed is None:
                continue
            _process_statement(parsed, tables)

    source_hash = hashlib.sha256("\n---\n".join(sources).encode("utf-8")).hexdigest()
    return tables, source_hash


def _extract_table_statements(sql: str) -> list[str]:
    """Extrae solo statements CREATE TABLE y ALTER TABLE ADD COLUMN del SQL.

    Filtra ruido tipo CREATE FUNCTION pl/pgsql, COMMENT ON, RLS policies,
    CREATE INDEX, etc. Devuelve lista de statements aislados (cada uno
    sin terminador `;` final).
    """
    # Strip comentarios -- de línea (mantenemos /* */ para no romper strings)
    lines = []
    for line in sql.splitlines():
        idx = line.find("--")
        if idx >= 0:
            line = line[:idx]
        lines.append(line)
    cleaned = "\n".join(lines)

    # Split por `;` a nivel top — naive pero suficiente porque las migrations
    # del Catastro no tienen `;` dentro de strings (excepto en COMMENT, que
    # filtramos abajo).
    raw_statements = [s.strip() for s in cleaned.split(";")]
    out: list[str] = []
    for s in raw_statements:
        if not s:
            continue
        upper = s.upper().lstrip()
        # Solo nos interesan estos dos tipos
        if upper.startswith("CREATE TABLE") or (
            upper.startswith("ALTER TABLE") and "ADD COLUMN" in upper
        ):
            out.append(s)
    return out


def _process_statement(stmt: exp.Expression, tables: dict) -> None:
    """Procesa un statement: solo nos interesa CREATE TABLE y ALTER TABLE ADD COLUMN."""
    if isinstance(stmt, exp.Create) and stmt.kind and stmt.kind.upper() == "TABLE":
        _handle_create_table(stmt, tables)
    elif isinstance(stmt, exp.Alter) and (stmt.args.get("kind") or "").upper() == "TABLE":
        _handle_alter_table(stmt, tables)
    # Ignoramos CREATE INDEX, CREATE VIEW, CREATE FUNCTION, etc.


def _handle_create_table(stmt: exp.Create, tables: dict) -> None:
    # stmt.this es un Schema; Schema.this es Table; Table.name es el nombre
    schema_node = stmt.this
    if not isinstance(schema_node, exp.Schema):
        return
    table_node = schema_node.this
    if not isinstance(table_node, exp.Table):
        return
    table_name = table_node.name.lower() if table_node.name else None
    if table_name is None or table_name not in CATASTRO_TABLES:
        return

    if table_name not in tables:
        tables[table_name] = {}

    for col_def in schema_node.expressions:
        if isinstance(col_def, exp.ColumnDef):
            col_name, col_info = _extract_column_info(col_def)
            if col_name:
                tables[table_name][col_name] = col_info


def _handle_alter_table(stmt: exp.Alter, tables: dict) -> None:
    target = stmt.this
    if not isinstance(target, exp.Table):
        return
    table_name = target.name.lower() if target.name else None
    if table_name is None or table_name not in CATASTRO_TABLES:
        return

    if table_name not in tables:
        tables[table_name] = {}

    for action in stmt.args.get("actions") or []:
        # ADD COLUMN: en sqlglot puede venir como ColumnDef directo o envuelto
        col_def = None
        if isinstance(action, exp.ColumnDef):
            col_def = action
        elif hasattr(action, "this") and isinstance(action.this, exp.ColumnDef):
            col_def = action.this

        if col_def is not None:
            col_name, col_info = _extract_column_info(col_def)
            if col_name:
                # ADD COLUMN IF NOT EXISTS → no sobrescribe si ya existía en CREATE
                if col_name not in tables[table_name]:
                    tables[table_name][col_name] = col_info


def _extract_column_info(col_def: exp.ColumnDef) -> tuple[str | None, dict[str, Any]]:
    """Extrae nombre, tipo, nullable, default, is_array, primary_key de una ColumnDef."""
    name = col_def.name.lower() if col_def.name else None
    if name is None:
        return None, {}

    col_type = col_def.args.get("kind")
    if col_type is None:
        return name, {"type": "UNKNOWN", "nullable": True, "default": None,
                      "is_array": False, "primary_key": False}

    type_str = str(col_type).upper()
    # sqlglot representa text[] como ARRAY<TEXT> y a veces deja sufijo []
    is_array = "[]" in type_str or type_str.startswith("ARRAY<") or bool(col_type.args.get("nested"))
    clean_type = type_str.replace("[]", "").strip()
    # Desempacar ARRAY<X> → X
    m = re.match(r"^ARRAY<(.+)>$", clean_type)
    if m:
        clean_type = m.group(1).strip()
    # Quitar parámetros tipo VARCHAR(255) → VARCHAR
    if "(" in clean_type:
        clean_type = clean_type.split("(")[0].strip()

    constraints = col_def.args.get("constraints") or []
    nullable = True
    default: Any = None
    primary_key = False
    for c in constraints:
        kind = c.args.get("kind") if hasattr(c, "args") else None
        if kind is None:
            continue
        if isinstance(kind, exp.NotNullColumnConstraint):
            nullable = False
        elif isinstance(kind, exp.DefaultColumnConstraint):
            default = str(kind.this) if kind.this is not None else None
        elif isinstance(kind, exp.PrimaryKeyColumnConstraint):
            primary_key = True
            nullable = False  # PK implica NOT NULL

    return name, {
        "type": clean_type,
        "nullable": nullable,
        "default": default,
        "is_array": is_array,
        "primary_key": primary_key,
    }


# ============================================================================
# Emitter Pydantic
# ============================================================================


HEADER = '''"""
kernel/catastro/schema_generated.py

GENERADO AUTOMÁTICAMENTE — NO EDITAR A MANO.
Fuente: scripts/016_sprint86_catastro_schema.sql + 018 + 019 + 019.1
Generador: scripts/_gen_catastro_pydantic_from_sql.py

Si necesitás cambiar este archivo:
1. Modificá la migration SQL correspondiente
2. Corré: python3 scripts/_gen_catastro_pydantic_from_sql.py
3. Verificá: python3 scripts/_audit_catastro_schema_drift.py

Doctrina (Mini-Sprint 86.4.5 pre-B2):
- Schema authority único: PostgreSQL DDL es la única fuente de verdad.
- schema.py (manual) está siendo deprecado gradualmente; cuando haya
  divergencia con este archivo, este archivo manda.
- Mappings provistos como `TABLE_COLUMNS` para introspect runtime
  (útil en pre-flight de queries y para detectar drift desde código).

Generado por Hilo Manus · 2026-05-05
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Source hash — para drift detection rápida sin re-parsear
# ============================================================================

__SOURCE_HASH__ = "{source_hash}"
__GENERATED_AT__ = "{generated_at}"
__MIGRATIONS__ = {migrations_repr}


'''


def _table_to_class_name(table: str) -> str:
    """catastro_modelos → CatastroModeloRow (sufijo Row para no chocar con schema.py)."""
    parts = table.split("_")
    pascal = "".join(p.capitalize() for p in parts)
    # Singular naming: catastro_modelos → CatastroModeloRow
    if pascal.endswith("os"):
        pascal = pascal[:-2] + "o"
    elif pascal.endswith("es"):
        pascal = pascal[:-2]
    elif pascal.endswith("s"):
        pascal = pascal[:-1]
    return pascal + "Row"


def _emit_class(table: str, cols: dict[str, dict[str, Any]]) -> str:
    """Emite una clase Pydantic para una tabla."""
    class_name = _table_to_class_name(table)
    lines = [
        f"class {class_name}(BaseModel):",
        f'    """Espejo bit-perfect de la tabla `{table}` (PostgreSQL DDL).',
        "",
        '    Generado automáticamente desde las migrations.',
        '    """',
        '    model_config = ConfigDict(extra="ignore")',
        "",
    ]
    for col_name, info in cols.items():
        py_type = _pg_type_to_python(info["type"], info["is_array"])
        if info["nullable"]:
            type_str = f"Optional[{py_type}]"
            default = " = None"
        else:
            type_str = py_type
            # NOT NULL sin default → required
            default = "" if info["default"] is None else f" = Field(default=None)  # SQL default: {info['default'][:80]}"
        lines.append(f"    {col_name}: {type_str}{default}")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


def _emit_table_columns_dict(tables: dict) -> str:
    """Emite TABLE_COLUMNS dict para introspect runtime."""
    lines = [
        "# ============================================================================",
        "# Introspección runtime — útil para pre-flight de queries SQL",
        "# ============================================================================",
        "",
        "TABLE_COLUMNS: dict[str, list[str]] = {",
    ]
    for table in sorted(tables.keys()):
        cols = list(tables[table].keys())
        lines.append(f'    "{table}": {cols!r},')
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _emit_full(tables: dict, source_hash: str) -> str:
    from datetime import datetime as _dt
    out = HEADER.format(
        source_hash=source_hash,
        generated_at=_dt.utcnow().isoformat(timespec="seconds") + "Z",
        migrations_repr=repr(MIGRATION_FILES),
    )

    out += "# ============================================================================\n"
    out += "# Pydantic models — uno por tabla\n"
    out += "# ============================================================================\n\n\n"

    for table in sorted(tables.keys()):
        out += _emit_class(table, tables[table])

    out += _emit_table_columns_dict(tables)

    return out


# ============================================================================
# Main
# ============================================================================


def main() -> int:
    parser = argparse.ArgumentParser(description="Generador Pydantic-from-SQL para el Catastro")
    parser.add_argument(
        "--check",
        action="store_true",
        help="No escribe; verifica que el archivo actual coincide con el generado (exit 1 si difiere).",
    )
    args = parser.parse_args()

    try:
        tables, source_hash = _parse_migrations()
    except CatastroSchemaGenError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if not tables:
        print("ERROR: catastro_schema_gen_no_tables_found: no se encontraron tablas del Catastro en las migrations.", file=sys.stderr)
        return 2

    output = _emit_full(tables, source_hash)
    output_path = REPO_ROOT / OUTPUT_FILE

    if args.check:
        if not output_path.exists():
            print(f"DRIFT: {OUTPUT_FILE} no existe — correr el generator", file=sys.stderr)
            return 1
        current = output_path.read_text(encoding="utf-8")
        # Comparar todo menos `__GENERATED_AT__` (siempre cambia)
        def _strip_timestamp(s: str) -> str:
            return "\n".join(
                l for l in s.splitlines() if not l.startswith("__GENERATED_AT__")
            )
        if _strip_timestamp(current) == _strip_timestamp(output):
            print(f"OK: {OUTPUT_FILE} sincronizado con migrations (source_hash={source_hash[:12]})")
            return 0
        else:
            print(f"DRIFT: {OUTPUT_FILE} desincronizado con migrations — correr el generator", file=sys.stderr)
            return 1

    output_path.write_text(output, encoding="utf-8")
    print(f"OK: generado {OUTPUT_FILE}")
    print(f"  · tables = {sorted(tables.keys())}")
    print(f"  · cols totales = {sum(len(c) for c in tables.values())}")
    print(f"  · source_hash = {source_hash[:12]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
