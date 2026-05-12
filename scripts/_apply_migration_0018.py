#!/usr/bin/env python
"""Aplicar migracion 0018_catastro_repos.sql contra produccion.
Sprint CATASTRO-C-SLICE-001.

Idempotente: CREATE TABLE IF NOT EXISTS + CREATE POLICY guarded.
Ejecutar dos veces seguidas NO rompe nada.

Requiere SUPABASE_DB_URL en env (lo trae railway run).
"""
import os
import sys

DB_URL = os.environ.get("SUPABASE_DB_URL")
if not DB_URL:
    print("ERROR: SUPABASE_DB_URL no esta en env. Usar 'railway run python ...'.", file=sys.stderr)
    sys.exit(1)

if "?" in DB_URL:
    DB_URL = DB_URL + "&sslmode=require"
else:
    DB_URL = DB_URL + "?sslmode=require"

try:
    import psycopg2  # noqa: F401
except ImportError:
    print("ERROR: psycopg2 no instalado. pip install psycopg2-binary", file=sys.stderr)
    sys.exit(1)

import psycopg2  # noqa: E402

MIGRATION_PATH = "migrations/sql/0018_catastro_repos.sql"
TABLES = ("catastro_repos",)

with open(MIGRATION_PATH) as f:
    sql = f.read()

print(f"[1] Aplicando {MIGRATION_PATH} ...")
conn = psycopg2.connect(DB_URL)
conn.autocommit = False
cur = conn.cursor()
try:
    cur.execute(sql)
    conn.commit()
    print("    OK -- migracion aplicada")
except psycopg2.errors.DuplicateObject as e:
    conn.rollback()
    print(f"    Object ya existe (idempotente OK): {e}")
except Exception as e:
    conn.rollback()
    print(f"    ERROR: {e}", file=sys.stderr)
    cur.close(); conn.close()
    sys.exit(2)

# Verificar
print("\n[2] Verificacion post-migracion:")
for t in TABLES:
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name=%s", (t,)
    )
    exists = cur.fetchone()[0] > 0
    print(f"    tabla {t}: {'OK existe' if exists else 'FAIL no existe'}")
    if exists:
        cur.execute(
            "SELECT relrowsecurity FROM pg_class WHERE relname=%s AND relnamespace = "
            "(SELECT oid FROM pg_namespace WHERE nspname='public')", (t,)
        )
        rls = cur.fetchone()
        print(f"    RLS habilitado: {bool(rls and rls[0])}")
        cur.execute(
            "SELECT policyname FROM pg_policies WHERE schemaname='public' AND tablename=%s", (t,)
        )
        policies = [r[0] for r in cur.fetchall()]
        print(f"    Policies: {policies}")

cur.close()
conn.close()
print("\nDONE.")
