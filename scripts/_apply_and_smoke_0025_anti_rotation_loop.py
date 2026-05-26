"""Aplicar migración 0025 + smoke test del constraint UNIQUE anti-bucle.

Ejecutar via:
    railway run --service el-monstruo-kernel python3 scripts/_apply_and_smoke_0025_anti_rotation_loop.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2 import errors as pg_errors

MIGRATION_PATH = "migrations/sql/0025_anti_rotation_loop.sql"


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL / DATABASE_URL ausentes", file=sys.stderr)
        return 1

    with open(MIGRATION_PATH, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    cur = conn.cursor()

    # ── Aplicar migración ────────────────────────────────────────
    print(f"[1/3] Aplicando {MIGRATION_PATH}...")
    try:
        cur.execute(sql)
        conn.commit()
        print("       Migración aplicada (commit OK).")
    except Exception as exc:
        conn.rollback()
        print(f"ERROR aplicando migración: {exc}", file=sys.stderr)
        return 2

    # ── Verificación post-migración ─────────────────────────────
    print("[2/3] Verificando objetos creados...")
    cur.execute("""
        SELECT
            EXISTS(SELECT 1 FROM information_schema.tables
                   WHERE table_schema='public' AND table_name='credential_rotations') AS tabla,
            EXISTS(SELECT 1 FROM pg_constraint
                   WHERE conname='unique_rotation_per_day_per_credential') AS constraint_,
            EXISTS(SELECT 1 FROM information_schema.columns
                   WHERE table_schema='public' AND table_name='credential_rotations'
                     AND column_name='rotated_at_date') AS gen_col,
            (SELECT rowsecurity FROM pg_tables
             WHERE schemaname='public' AND tablename='credential_rotations') AS rls,
            (SELECT COUNT(*) FROM pg_policies
             WHERE schemaname='public' AND tablename='credential_rotations') AS policies
    """)
    row = cur.fetchone()
    if not row:
        print("ERROR: no se obtuvo verificación", file=sys.stderr)
        return 3
    tabla, constraint_, gen_col, rls, policies = row
    print(f"       tabla={tabla} constraint={constraint_} gen_col={gen_col} rls={rls} policies={policies}")
    if not all([tabla, constraint_, gen_col, rls, policies and policies >= 1]):
        print("ERROR: verificación post-migración FALLÓ", file=sys.stderr)
        return 4

    # ── Smoke test del constraint UNIQUE ────────────────────────
    print("[3/3] Smoke test del constraint UNIQUE anti-bucle...")
    test_key = "TEST_SMOKE_S_CONTRATOS_001_T4"
    # Cleanup previo (idempotencia)
    cur.execute("DELETE FROM public.credential_rotations WHERE credential_id=%s", (test_key,))
    conn.commit()

    # 3.1 Insert hoy → debe pasar
    cur.execute(
        """
        INSERT INTO public.credential_rotations
        (credential_id, rotated_by, razon, rotated_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id, rotated_at_date
    """,
        (test_key, "smoke", "manual", datetime.now(timezone.utc)),
    )
    id1, date1 = cur.fetchone()
    conn.commit()
    print(f"       3.1 Insert #1 hoy → OK (id={id1}, date={date1})")

    # 3.2 Insert hoy otra vez → debe FALLAR con UniqueViolation
    sp = conn.cursor()
    try:
        sp.execute(
            """
            INSERT INTO public.credential_rotations
            (credential_id, rotated_by, razon, rotated_at)
            VALUES (%s, %s, %s, %s)
        """,
            (test_key, "smoke", "manual", datetime.now(timezone.utc) + timedelta(hours=1)),
        )
        conn.commit()
        print("       3.2 Insert #2 hoy → ERROR: NO truena (constraint roto)", file=sys.stderr)
        return 5
    except pg_errors.UniqueViolation:
        conn.rollback()
        print("       3.2 Insert #2 hoy → OK (UniqueViolation esperada)")
    finally:
        sp.close()

    # 3.3 Insert AYER (mismo key) → debe pasar (rotated_at_date diferente)
    cur.execute(
        """
        INSERT INTO public.credential_rotations
        (credential_id, rotated_by, razon, rotated_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id, rotated_at_date
    """,
        (test_key, "smoke", "manual", datetime.now(timezone.utc) - timedelta(days=1)),
    )
    id3, date3 = cur.fetchone()
    conn.commit()
    print(f"       3.3 Insert ayer (mismo key) → OK (id={id3}, date={date3})")

    # 3.4 Cleanup
    cur.execute("DELETE FROM public.credential_rotations WHERE credential_id=%s", (test_key,))
    conn.commit()
    print("       3.4 Cleanup OK")

    cur.close()
    conn.close()
    print("\n✓ T4 (DSC-G-011) VERDE: tabla + constraint UNIQUE + columna generada IMMUTABLE + smoke 3/3.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
