"""
Sprint 87.2 Bloque 4 — Run migration 028 (e2e_traffic table).

Idempotente: re-run safe.

Uso desde repo root:
    python3 scripts/run_migration_028.py
    python3 scripts/run_migration_028.py --dry-run

Brand DNA en errores: e2e_migration_028_*_failed.
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


class E2EMigration028Error(Exception):
    code = "e2e_migration_028_failed"


class E2EMigration028ConnectionFailed(E2EMigration028Error):
    code = "e2e_migration_028_connection_failed"


class E2EMigration028SchemaFailed(E2EMigration028Error):
    code = "e2e_migration_028_schema_failed"


def _read_sql() -> str:
    path = os.path.join(
        os.path.dirname(__file__), "028_sprint87_2_e2e_traffic_schema.sql"
    )
    with open(path, encoding="utf-8") as f:
        return f.read()


def _connect() -> Any:
    db_url = os.environ.get("DATABASE_URL") or (
        "postgresql://postgres.xsumzuhwmivjgftsneov:0SsKDCchJpN5GhO3"
        "@aws-1-us-east-2.pooler.supabase.com:5432/postgres?sslmode=require"
    )
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        return conn
    except Exception as e:
        raise E2EMigration028ConnectionFailed(str(e)) from e


def apply_schema(conn: Any) -> None:
    sql = _read_sql()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cur.execute(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = 'e2e_traffic' ORDER BY ordinal_position"
            )
            cols = cur.fetchall()
            if not cols:
                raise E2EMigration028SchemaFailed(
                    "tabla e2e_traffic no aparece post-migration"
                )
            print("  schema OK:")
            for name, dtype in cols:
                print(f"    {name:14s} {dtype}")
    except E2EMigration028SchemaFailed:
        raise
    except Exception as e:
        raise E2EMigration028SchemaFailed(str(e)) from e


def main() -> int:
    parser = argparse.ArgumentParser(description="Sprint 87.2 migration 028 runner")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN — Schema migration 028:")
        print("=" * 60)
        print(_read_sql())
        return 0

    print("Sprint 87.2 — Migration 028 runner (e2e_traffic)")
    try:
        conn = _connect()
    except E2EMigration028Error as e:
        print(f"ERROR [{e.code}] {e!s}", file=sys.stderr)
        return 1

    try:
        apply_schema(conn)
    except E2EMigration028Error as e:
        print(f"ERROR [{e.code}] {e!s}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    print("\nMigration 028 COMPLETED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
