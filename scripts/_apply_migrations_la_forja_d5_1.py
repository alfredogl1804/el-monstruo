#!/usr/bin/env python3
"""Apply La Forja D5.1 migrations 0038-0046 (9 tablas forja_*).

Sprint: LA-FORJA-001 D5.1
Autor: Manus E1 (T1)
Fecha: 2026-05-17

Aplica las 9 migraciones forja_* en orden, idempotentes, y verifica
binariamente RLS+policies post-aplicación. Patrón canónico: psycopg
directo sobre SUPABASE_DB_URL (env de Railway o local .env).

Uso:
    SUPABASE_DB_URL="postgresql://..." python3 scripts/_apply_migrations_la_forja_d5_1.py

Exit codes:
    0 — todas las migraciones aplicadas y RLS verificado en las 9 tablas
    1 — error en migración o verificación RLS falla
    2 — env var SUPABASE_DB_URL no configurada
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

# 9 migraciones D5.1 en orden de aplicación
MIGRATIONS = [
    ("0038_la_forja_profiles.sql", "forja_profiles"),
    ("0039_la_forja_threads.sql", "forja_threads"),
    ("0040_la_forja_messages.sql", "forja_messages"),
    ("0041_la_forja_sprints.sql", "forja_sprints"),
    ("0042_la_forja_actions.sql", "forja_actions"),
    ("0043_la_forja_telemetry.sql", "forja_telemetry"),
    ("0044_la_forja_simulations.sql", "forja_simulations"),
    ("0045_la_forja_validations.sql", "forja_validations"),
    ("0046_la_forja_budget.sql", "forja_budget"),
]

REPO_ROOT = Path(__file__).parent.parent
SQL_DIR = REPO_ROOT / "migrations" / "sql"


def apply_migration(cur, sql_filename: str) -> None:
    """Aplica un archivo SQL idempotentemente."""
    sql_path = SQL_DIR / sql_filename
    if not sql_path.exists():
        raise FileNotFoundError(f"Migration file not found: {sql_path}")
    sql = sql_path.read_text(encoding="utf-8")
    print(f"  Applying {sql_filename} ({len(sql)} chars)...")
    cur.execute(sql)
    print(f"  ✓ {sql_filename} applied")


def verify_rls_enabled(cur, table_name: str) -> bool:
    """Verifica que RLS esté habilitado en la tabla."""
    cur.execute(
        """
        SELECT relrowsecurity
        FROM pg_class
        WHERE relname = %s AND relnamespace = 'public'::regnamespace
        """,
        (table_name,),
    )
    row = cur.fetchone()
    if row is None:
        print(f"  ✗ Table {table_name} not found in pg_class", file=sys.stderr)
        return False
    return bool(row[0])


def verify_policies(cur, table_name: str) -> int:
    """Retorna el número de policies en la tabla."""
    cur.execute(
        """
        SELECT COUNT(*) FROM pg_policies
        WHERE schemaname = 'public' AND tablename = %s
        """,
        (table_name,),
    )
    row = cur.fetchone()
    return int(row[0]) if row else 0


def verify_constraints(cur, table_name: str) -> int:
    """Retorna el número de CHECK constraints en la tabla."""
    cur.execute(
        """
        SELECT COUNT(*) FROM pg_constraint c
        JOIN pg_class t ON t.oid = c.conrelid
        WHERE t.relname = %s
          AND t.relnamespace = 'public'::regnamespace
          AND c.contype = 'c'
        """,
        (table_name,),
    )
    row = cur.fetchone()
    return int(row[0]) if row else 0


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 2

    print(f"=== La Forja D5.1: Aplicando 9 migraciones forja_* ===")
    print(f"DB host: {dsn.split('@')[-1].split('/')[0] if '@' in dsn else 'unknown'}")
    print()

    try:
        with psycopg.connect(dsn, autocommit=True) as conn, conn.cursor() as cur:
            # Aplicar las 9 migraciones en orden
            for sql_filename, _ in MIGRATIONS:
                apply_migration(cur, sql_filename)

            print()
            print("=== Verificación binaria post-aplicación ===")

            all_ok = True
            for _, table_name in MIGRATIONS:
                rls = verify_rls_enabled(cur, table_name)
                policies = verify_policies(cur, table_name)
                checks = verify_constraints(cur, table_name)

                status = "OK" if (rls and policies >= 2) else "FAIL"
                if not rls or policies < 2:
                    all_ok = False

                print(
                    f"  {table_name:<20} RLS={rls!s:<5} "
                    f"policies={policies} checks={checks} → {status}"
                )

            if not all_ok:
                print()
                print("FAIL: una o más tablas no cumplen RLS+policies>=2", file=sys.stderr)
                return 1

            print()
            print("MIGRATIONS_LA_FORJA_D5_1_OK (9/9 tablas con RLS+policies>=2)")
            return 0

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
