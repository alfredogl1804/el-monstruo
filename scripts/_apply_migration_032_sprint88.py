#!/usr/bin/env python3
"""Apply migration 032 (tier_seed column) to Supabase prod via Railway DSN."""
import os
import sys
from pathlib import Path
import psycopg


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    sql_path = Path(__file__).parent / "032_sprint88_tier_seed.sql"
    sql = sql_path.read_text()
    print(f"Applying migration: {sql_path.name} ({len(sql)} chars)")

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                # Verify
                cur.execute("""
                    SELECT column_name, data_type, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'catastro_agentes' AND column_name = 'tier_seed'
                """)
                row = cur.fetchone()
                if row:
                    print(f"OK: tier_seed column exists: {row}")
                else:
                    print("ERROR: tier_seed column not found after migration", file=sys.stderr)
                    return 1
        print("MIGRATION_032_OK")
        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
