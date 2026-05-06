"""
Sprint 88 Tarea 3.B.2 — Run migration 029 (e2e_runs.deploy_provider).

Agrega columna `deploy_provider` a e2e_runs para reflejar el provider real
del deploy en el rollup del run (no solo en e2e_step_log.output_payload).

Idempotente: re-run safe (uses ADD COLUMN IF NOT EXISTS).

Uso desde repo root:
    python3 scripts/run_migration_029.py
    python3 scripts/run_migration_029.py --dry-run

Brand DNA en errores: e2e_migration_029_*_failed.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any

try:
    import psycopg2
except ImportError:
    print("psycopg2 not installed — pip install psycopg2-binary", file=sys.stderr)
    sys.exit(2)


class E2EMigration029Error(Exception):
    code = "e2e_migration_029_failed"


class E2EMigration029ConnectionFailed(E2EMigration029Error):
    code = "e2e_migration_029_connection_failed"


class E2EMigration029SchemaFailed(E2EMigration029Error):
    code = "e2e_migration_029_schema_failed"


def _read_sql() -> str:
    path = os.path.join(
        os.path.dirname(__file__), "029_sprint88_e2e_runs_deploy_provider.sql"
    )
    with open(path, encoding="utf-8") as f:
        return f.read()


def _connect() -> Any:
    db_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("SUPABASE_DB_URL")
    )
    if not db_url:
        raise E2EMigration029ConnectionFailed(
            "DATABASE_URL/SUPABASE_DB_URL no configurada en el entorno"
        )
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        return conn
    except Exception as e:
        raise E2EMigration029ConnectionFailed(str(e)) from e


def apply_schema(conn: Any) -> None:
    sql = _read_sql()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cur.execute(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = 'e2e_runs' AND column_name = 'deploy_provider'"
            )
            cols = cur.fetchall()
            if not cols:
                raise E2EMigration029SchemaFailed(
                    "columna deploy_provider no aparece post-migration"
                )
            print("  schema OK:")
            for name, dtype in cols:
                print(f"    {name:18s} {dtype}")

            # Verificar backfill cosmético
            cur.execute(
                "SELECT COUNT(*) FROM e2e_runs WHERE deploy_provider IS NOT NULL"
            )
            count_with_provider = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM e2e_runs")
            total = cur.fetchone()[0]
            print(f"  backfill: {count_with_provider}/{total} runs con deploy_provider poblado")
    except E2EMigration029SchemaFailed:
        raise
    except Exception as e:
        raise E2EMigration029SchemaFailed(str(e)) from e


def main() -> int:
    parser = argparse.ArgumentParser(description="Sprint 88 migration 029 runner")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN — Schema migration 029:")
        print("=" * 60)
        print(_read_sql())
        return 0

    print("Sprint 88 — Migration 029 runner (e2e_runs.deploy_provider)")
    try:
        conn = _connect()
    except E2EMigration029Error as e:
        print(f"ERROR [{e.code}] {e!s}", file=sys.stderr)
        return 1

    try:
        apply_schema(conn)
    except E2EMigration029Error as e:
        print(f"ERROR [{e.code}] {e!s}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    print("\nMigration 029 COMPLETED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
