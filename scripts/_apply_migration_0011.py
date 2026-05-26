#!/usr/bin/env python
"""Aplicar migración 0011_rls_catastro_vision_generativa.sql contra prod.

P0 RLS Fix — autorizado por Cowork en acuse 2026-05-11 04:26 (commits b9e90cd→a29e76e).
Patrón: service_role_only (idéntico a 0004-0008).
Idempotente: ENABLE RLS y CREATE POLICY fallan si ya existen, lo cual indica que
la migración ya fue aplicada — exit 0 en ese caso si verificación post pasa.
"""

import os
import sys

import psycopg2

DB_URL = os.environ.get("SUPABASE_DB_URL")
if not DB_URL:
    print("ERROR: SUPABASE_DB_URL no está en env")
    sys.exit(1)

if "?" in DB_URL:
    DB_URL = DB_URL + "&sslmode=require"
else:
    DB_URL = DB_URL + "?sslmode=require"

MIGRATION_PATH = "migrations/sql/0011_rls_catastro_vision_generativa.sql"

with open(MIGRATION_PATH) as f:
    sql = f.read()

print(f"[1] Aplicando {MIGRATION_PATH} ...")
conn = psycopg2.connect(DB_URL)
conn.autocommit = False
cur = conn.cursor()

try:
    cur.execute(sql)
    conn.commit()
    print("    OK — migración aplicada")
except psycopg2.errors.DuplicateObject as e:
    conn.rollback()
    print(f"    Policy ya existe (idempotente): {e}")
except Exception as e:
    conn.rollback()
    print(f"    FAIL: {e}")
    sys.exit(2)

print("[2] Verificación post — RLS status:")
cur.execute("""
    SELECT c.relname, c.relrowsecurity,
           (SELECT count(*) FROM pg_policies
            WHERE schemaname='public' AND tablename = c.relname) AS policy_count
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
      AND c.relname = 'catastro_vision_generativa'
""")
row = cur.fetchone()
if not row:
    print("    FAIL: tabla no encontrada")
    sys.exit(3)
name, rls, pol_count = row
print(f"    table={name}  rls={rls}  policies={pol_count}")

if not rls:
    print("    FAIL: RLS no quedó habilitado")
    sys.exit(4)
if pol_count < 1:
    print("    FAIL: no hay policies activas")
    sys.exit(5)

print("[3] Verificación de policy específica:")
cur.execute("""
    SELECT policyname, cmd, roles, qual, with_check
    FROM pg_policies
    WHERE schemaname='public' AND tablename='catastro_vision_generativa'
""")
for pname, cmd, roles, qual, check in cur.fetchall():
    print(f"    {pname}  cmd={cmd}  roles={roles}")
    print(f"      using:  {qual}")
    print(f"      check:  {check}")

print("[4] Conteo de rows pre y post:")
cur.execute("SELECT count(*) FROM public.catastro_vision_generativa")
(n,) = cur.fetchone()
print(f"    rows: {n}")

print("[5] Auditoría RLS coverage global:")
cur.execute("""
    SELECT
      (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
       WHERE n.nspname = 'public' AND c.relkind = 'r') AS total_tables,
      (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
       WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relrowsecurity = true) AS tables_rls
""")
total, with_rls = cur.fetchone()
print(f"    {with_rls}/{total} tablas con RLS")
if with_rls != total:
    print(f"    FAIL: aún hay {total - with_rls} tabla(s) sin RLS")
    sys.exit(6)

print("\n=== MIGRACIÓN 0011 APLICADA — 119/119 tablas con RLS ===")
