"""Apply migration 0023 (rotor_activity_log) + smoke test + RLS verification.

TA2 del Sprint MEGA-CIERRE-HOY (Hilo Catastro).

Usar via: railway run --service el-monstruo-kernel python3 scripts/_apply_and_smoke_0023_rotor_activity_log.py
"""
from __future__ import annotations

import os
import sys
import psycopg2

MIGRATION_PATH = "migrations/sql/0023_rotor_activity_log.sql"


def apply_migration(conn) -> None:
    print(f"[1/4] Applying migration {MIGRATION_PATH}...")
    with open(MIGRATION_PATH) as f:
        sql = f.read()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    print("      Migration applied + committed.")


def verify_table(conn) -> None:
    print("[2/4] Verifying table exists + RLS habilitada + policy service_role_only...")
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM information_schema.tables
              WHERE table_schema='public' AND table_name='rotor_activity_log') AS table_exists,
            (SELECT relrowsecurity FROM pg_class
              WHERE relname='rotor_activity_log' AND relnamespace=(SELECT oid FROM pg_namespace WHERE nspname='public')) AS rls_enabled,
            (SELECT COUNT(*) FROM pg_policies
              WHERE schemaname='public' AND tablename='rotor_activity_log') AS policies_count
        """
    )
    row = cur.fetchone()
    cur.close()
    print(f"      table_exists={row[0]}, rls_enabled={row[1]}, policies_count={row[2]}")
    assert row[0] == 1, "Tabla rotor_activity_log NO existe en prod"
    assert row[1] is True, "RLS NO está habilitada"
    assert row[2] >= 1, "No hay policies declaradas"


def smoke_test(conn) -> str:
    print("[3/4] Smoke test: insert + select + delete...")
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO public.rotor_activity_log
            (source, actor, payload_jsonb, energy_units)
        VALUES
            ('cowork_session', 'smoke_test_MEGA_CIERRE_HOY', '{"smoke": true}'::jsonb, 0.0)
        RETURNING id
        """
    )
    row_id = cur.fetchone()[0]
    print(f"      Insert OK: id={row_id}")

    cur.execute(
        "SELECT actor, energy_units FROM public.rotor_activity_log WHERE id = %s",
        (row_id,),
    )
    row = cur.fetchone()
    print(f"      Select OK: actor={row[0]}, energy={row[1]}")

    cur.execute("DELETE FROM public.rotor_activity_log WHERE id = %s", (row_id,))
    conn.commit()
    print(f"      Delete OK: cleanup completed.")
    cur.close()
    return str(row_id)


def anti_immutable_check(conn) -> None:
    print("[4/4] Anti-IMMUTABLE check: revisar índices con DATE() expression...")
    cur = conn.cursor()
    cur.execute(
        """
        SELECT indexname, indexdef
          FROM pg_indexes
         WHERE schemaname='public' AND tablename='rotor_activity_log'
        """
    )
    rows = cur.fetchall()
    cur.close()
    bad_indexes = [r for r in rows if "DATE(" in r[1].upper().replace("DATE_", "")]
    print(f"      Total indexes: {len(rows)}")
    for name, defn in rows:
        print(f"        - {name}")
    if bad_indexes:
        print("      WARN: índices sospechosos con DATE():")
        for name, defn in bad_indexes:
            print(f"        - {name}: {defn}")
    else:
        print("      OK: cero índices con DATE(timestamptz) directo.")


def main() -> None:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        sys.exit(1)
    conn = psycopg2.connect(dsn)
    try:
        apply_migration(conn)
        verify_table(conn)
        smoke_test(conn)
        anti_immutable_check(conn)
        print("\n[VERDE] TA2 migration 0023 rotor_activity_log applied + verified.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
