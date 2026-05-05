"""
Sprint 86.8 — Run migrations 027 (schema + assignment).

Ejecuta:
  1. 027_sprint86_8_confidentiality_tier_schema.sql (ALTER TABLE + INDEX)
  2. 027_sprint86_8_assign_confidentiality_tiers.sql (UPDATEs por categoría)

Idempotente: re-run safe.

Uso desde repo root:
    python3 scripts/run_migration_027.py
    python3 scripts/run_migration_027.py --dry-run

Brand DNA en errores: catastro_migration_027_*_failed
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any

try:
    import psycopg2
except ImportError:
    print("psycopg2 not installed — install with: pip install psycopg2-binary", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Errores con identidad de marca
# ---------------------------------------------------------------------------

class CatastroMigration027Error(Exception):
    """Base error class. Brand DNA: catastro_migration_027_*."""

    code = "catastro_migration_027_failed"


class CatastroMigration027ConnectionFailed(CatastroMigration027Error):
    code = "catastro_migration_027_connection_failed"


class CatastroMigration027SchemaFailed(CatastroMigration027Error):
    code = "catastro_migration_027_schema_failed"


class CatastroMigration027AssignmentFailed(CatastroMigration027Error):
    code = "catastro_migration_027_assignment_failed"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_sql(path: str) -> str:
    full = os.path.join(os.path.dirname(__file__), path)
    with open(full, encoding="utf-8") as f:
        return f.read()


def _connect() -> Any:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        # Fallback histórico del repo (Sprint 81+)
        db_url = (
            "postgresql://postgres.xsumzuhwmivjgftsneov:0SsKDCchJpN5GhO3"
            "@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
            "?sslmode=require"
        )
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        return conn
    except Exception as e:
        raise CatastroMigration027ConnectionFailed(
            f"No se pudo conectar a Supabase: {e!s}"
        ) from e


# ---------------------------------------------------------------------------
# Pasos
# ---------------------------------------------------------------------------

def apply_schema(conn: Any) -> None:
    sql = _read_sql("027_sprint86_8_confidentiality_tier_schema.sql")
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cur.execute(
                "SELECT column_name, data_type, column_default "
                "FROM information_schema.columns "
                "WHERE table_name = 'catastro_modelos' "
                "AND column_name = 'confidentiality_tier'"
            )
            row = cur.fetchone()
            if not row:
                raise CatastroMigration027SchemaFailed(
                    "confidentiality_tier no aparece en catastro_modelos post-migration"
                )
            print(f"  schema OK: {row}")
    except CatastroMigration027SchemaFailed:
        raise
    except Exception as e:
        raise CatastroMigration027SchemaFailed(
            f"Schema migration falló: {e!s}"
        ) from e


def apply_assignment(conn: Any) -> None:
    sql = _read_sql("027_sprint86_8_assign_confidentiality_tiers.sql")
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cur.execute(
                "SELECT confidentiality_tier, COUNT(*) "
                "FROM catastro_modelos "
                "GROUP BY confidentiality_tier "
                "ORDER BY confidentiality_tier"
            )
            rows = cur.fetchall()
            print("  assignment distribution:")
            for tier, count in rows:
                print(f"    {tier:24s} -> {count}")
    except Exception as e:
        raise CatastroMigration027AssignmentFailed(
            f"Assignment falló: {e!s}"
        ) from e


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Sprint 86.8 migration runner")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo imprime el SQL; no toca la DB",
    )
    parser.add_argument(
        "--skip-assignment",
        action="store_true",
        help="Solo aplica el schema, omite UPDATEs de asignación",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN — Schema migration:")
        print("=" * 60)
        print(_read_sql("027_sprint86_8_confidentiality_tier_schema.sql"))
        print()
        print("=" * 60)
        print("DRY RUN — Assignment:")
        print("=" * 60)
        print(_read_sql("027_sprint86_8_assign_confidentiality_tiers.sql"))
        return 0

    print("Sprint 86.8 — Migration 027 runner")
    print("Connecting to Supabase...")
    try:
        conn = _connect()
    except CatastroMigration027Error as e:
        print(f"ERROR [{e.code}] {e!s}", file=sys.stderr)
        return 1

    try:
        print("\n[1/2] Aplicando schema (ALTER TABLE + INDEX)...")
        apply_schema(conn)
        print("[1/2] OK")

        if args.skip_assignment:
            print("\n[2/2] Skipped (flag --skip-assignment)")
        else:
            print("\n[2/2] Aplicando asignación inicial conservadora...")
            apply_assignment(conn)
            print("[2/2] OK")
    except CatastroMigration027Error as e:
        print(f"ERROR [{e.code}] {e!s}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    print("\nMigration 027 COMPLETED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
