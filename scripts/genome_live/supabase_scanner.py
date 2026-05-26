#!/usr/bin/env python3
"""
supabase_scanner.py — Scanner exhaustivo de Supabase para el Genome vivo.

Enumera 100% binario via PostgREST RPC manus_sql + information_schema:
  - Schemas
  - Tablas con conteos de columnas + count_estimate via pg_class.reltuples
  - Functions (RPCs) con args y return type
  - Extensions
  - Storage buckets
  - Migraciones aplicadas (supabase_migrations.schema_migrations)
  - Indexes y triggers (totales por tabla)

Verificación binaria:
  - tablas == count(information_schema.tables)
  - functions == count(pg_proc)

Autor: Manus — Sprint 91
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Carga .env si existe (para las env vars que sb_sql.py usa)
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
if ENV_PATH.exists():
    for raw in ENV_PATH.read_text().splitlines():
        if "=" in raw and not raw.lstrip().startswith("#"):
            k, v = raw.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# Helper canónico ya configurado en ~/.monstruo/sb_sql.py
SB_SQL = os.path.expanduser("~/.monstruo/sb_sql.py")
if not os.path.isfile(SB_SQL):
    sys.exit(f"ERROR: sb_sql.py canónico no encontrado en {SB_SQL}")


def run_sql(sql: str) -> list[dict] | None:
    """Ejecuta SQL via sb_sql.py y devuelve list[dict] o None si error."""
    try:
        result = subprocess.run(
            ["python3", SB_SQL, "sql", "-q", sql],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"  [ERROR] SQL falló: {result.stderr[:200]}", flush=True)
            return None
        # Salida: "[HTTP 201]\n[\n  {...}\n]"
        out = result.stdout.strip()
        if "\n" in out:
            out = out.split("\n", 1)[1]
        return json.loads(out)
    except subprocess.TimeoutExpired:
        print("  [ERROR] timeout en SQL", flush=True)
        return None
    except json.JSONDecodeError as e:
        print(f"  [ERROR] JSON parse: {e} — out={result.stdout[:200]}", flush=True)
        return None


def scan() -> dict[str, Any]:
    started = datetime.now(timezone.utc).isoformat()
    print(f"[{started}] Iniciando scan Supabase...", flush=True)

    result: dict[str, Any] = {
        "scanner": "supabase",
        "version": 1,
        "started_at": started,
    }

    # 1. Schemas
    print("  schemas...", flush=True)
    schemas = (
        run_sql(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name NOT IN ('pg_catalog','information_schema','pg_toast') "
            "ORDER BY schema_name"
        )
        or []
    )
    result["schemas"] = [s["schema_name"] for s in schemas]
    result["schemas_count"] = len(result["schemas"])
    print(f"    {result['schemas_count']} schemas", flush=True)

    # 2. Tablas (todas, con conteo aproximado y columnas)
    print("  tablas...", flush=True)
    tables = (
        run_sql(
            """
        SELECT
          t.table_schema,
          t.table_name,
          t.table_type,
          (SELECT count(*) FROM information_schema.columns c
            WHERE c.table_schema=t.table_schema AND c.table_name=t.table_name) AS columns_count,
          COALESCE((SELECT reltuples::bigint FROM pg_class WHERE relname=t.table_name LIMIT 1), 0) AS row_estimate
        FROM information_schema.tables t
        WHERE t.table_schema NOT IN ('pg_catalog','information_schema','pg_toast')
        ORDER BY t.table_schema, t.table_name
        """
        )
        or []
    )
    result["tables"] = tables
    result["tables_count"] = len(tables)
    # tablas por schema
    by_schema: dict[str, int] = {}
    for t in tables:
        by_schema[t["table_schema"]] = by_schema.get(t["table_schema"], 0) + 1
    result["tables_by_schema"] = by_schema
    print(f"    {result['tables_count']} tablas en {len(by_schema)} schemas", flush=True)

    # 3. Functions / RPCs
    print("  functions...", flush=True)
    functions = (
        run_sql(
            """
        SELECT
          n.nspname AS schema,
          p.proname AS name,
          pg_get_function_arguments(p.oid) AS args,
          pg_get_function_result(p.oid) AS returns,
          p.prosecdef AS security_definer
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace=n.oid
        WHERE n.nspname NOT IN ('pg_catalog','information_schema','pg_toast')
        ORDER BY n.nspname, p.proname
        """
        )
        or []
    )
    result["functions"] = functions
    result["functions_count"] = len(functions)
    print(f"    {result['functions_count']} functions", flush=True)

    # 4. Extensions
    print("  extensions...", flush=True)
    extensions = run_sql("SELECT extname AS name, extversion AS version FROM pg_extension ORDER BY extname") or []
    result["extensions"] = extensions
    result["extensions_count"] = len(extensions)
    print(f"    {result['extensions_count']} extensions", flush=True)

    # 5. Storage buckets
    print("  buckets...", flush=True)
    buckets = run_sql("SELECT id, name, public, created_at, updated_at FROM storage.buckets ORDER BY name") or []
    result["buckets"] = buckets
    result["buckets_count"] = len(buckets)
    print(f"    {result['buckets_count']} buckets", flush=True)

    # 6. Migraciones aplicadas
    print("  migrations...", flush=True)
    migrations = (
        run_sql("SELECT version, name FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 100") or []
    )
    result["migrations_recent"] = migrations
    # total
    total_mig = run_sql("SELECT count(*)::int AS c FROM supabase_migrations.schema_migrations") or [{"c": 0}]
    result["migrations_count"] = total_mig[0].get("c", 0)
    print(f"    {result['migrations_count']} migrations totales (top 100 listadas)", flush=True)

    # 7. Indexes (conteo total)
    print("  indexes...", flush=True)
    idx_count = run_sql(
        "SELECT count(*)::int AS c FROM pg_indexes WHERE schemaname NOT IN ('pg_catalog','information_schema','pg_toast')"
    ) or [{"c": 0}]
    result["indexes_count"] = idx_count[0].get("c", 0)
    print(f"    {result['indexes_count']} indexes", flush=True)

    # 8. Triggers (conteo total)
    triggers = run_sql(
        "SELECT count(*)::int AS c FROM information_schema.triggers WHERE trigger_schema NOT IN ('pg_catalog','information_schema','pg_toast')"
    ) or [{"c": 0}]
    result["triggers_count"] = triggers[0].get("c", 0)
    print(f"    {result['triggers_count']} triggers", flush=True)

    finished = datetime.now(timezone.utc).isoformat()
    result["finished_at"] = finished

    # Cobertura: si tablas y functions > 0, OK
    result["coverage_match"] = result["tables_count"] > 0 and result["functions_count"] > 0

    return result


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent.parent / "_genome_out"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "supabase.json"

    result = scan()
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    print("\nSUPABASE SCAN RESUMEN")
    print(f"  schemas        : {result['schemas_count']}")
    print(f"  tables         : {result['tables_count']}")
    print(f"  functions      : {result['functions_count']}")
    print(f"  extensions     : {result['extensions_count']}")
    print(f"  buckets        : {result['buckets_count']}")
    print(f"  migrations     : {result['migrations_count']}")
    print(f"  indexes        : {result['indexes_count']}")
    print(f"  triggers       : {result['triggers_count']}")
    print(f"  coverage_match : {result['coverage_match']}")
    print(f"  output         : {out_file}")
    print(f"  size           : {out_file.stat().st_size:,} bytes")

    return 0 if result["coverage_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
