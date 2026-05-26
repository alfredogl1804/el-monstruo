#!/usr/bin/env python3
"""
Sprint 88 - Aplica la migracion 030_sprint88_catastro_agentes.sql a Supabase prod.

Ejecutar via:
    railway run --service el-monstruo-kernel python3 scripts/_apply_migration_030_sprint88.py

Requiere:
    - SUPABASE_DB_URL en env (provisto por Railway)
    - psycopg[binary] instalado
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    sql_path = Path(__file__).parent / "030_sprint88_catastro_agentes.sql"
    if not sql_path.exists():
        print(f"ERROR: SQL file not found: {sql_path}", file=sys.stderr)
        return 1

    sql = sql_path.read_text()
    print(f"Applying migration: {sql_path.name} ({len(sql)} bytes)")

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                print("MIGRATION_OK")

                # Verificar que la tabla existe y esta vacia
                cur.execute("SELECT count(*) FROM catastro_agentes")
                count = cur.fetchone()[0]
                print(f"VERIFICATION: catastro_agentes has {count} rows (expected 0 on first run)")

                # Verificar invariante CHECK constraint
                cur.execute(
                    """
                    SELECT conname FROM pg_constraint
                    WHERE conrelid = 'catastro_agentes'::regclass
                    """
                )
                constraints = [r[0] for r in cur.fetchall()]
                print(f"CONSTRAINTS: {constraints}")

                # Verificar indices
                cur.execute(
                    """
                    SELECT indexname FROM pg_indexes
                    WHERE tablename = 'catastro_agentes'
                    ORDER BY indexname
                    """
                )
                indexes = [r[0] for r in cur.fetchall()]
                print(f"INDEXES: {indexes}")

        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
