#!/usr/bin/env python3
"""Apply migration 033 (normalize CHECK constraints) to Supabase prod."""
import os
import sys
from pathlib import Path
import psycopg


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    sql_path = Path(__file__).parent / "033_sprint88_normalizar_checks.sql"
    sql = sql_path.read_text()
    print(f"Applying migration: {sql_path.name} ({len(sql)} chars)")

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                # Re-list constraints
                cur.execute("""
                    SELECT con.conname, pg_get_constraintdef(con.oid)
                    FROM pg_constraint con
                    JOIN pg_class rel ON rel.oid = con.conrelid
                    WHERE rel.relname = 'catastro_agentes' AND con.contype = 'c'
                    ORDER BY con.conname
                """)
                print("=== CHECKs después de migración 033 ===")
                for n, d in cur.fetchall():
                    print(f"  {n}: {d}")
        print("MIGRATION_033_OK")
        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
