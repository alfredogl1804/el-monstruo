#!/usr/bin/env python
"""Aplicar migración 0012_embrion_inbox.sql contra producción.

Sprint EMBRION-NEEDS-002 Tarea 5 (Embrión-Daddy bidireccional, implementación).
Autorizado por: kickoff Cowork T2 (bridge/cowork_to_manus_T5_EMBRION_DADDY_KICKOFF_2026_05_11.md).
Autor: Hilo Ejecutor 2 (manus_hilo_ejecutor_2).

Crea dos tablas:
  1) embrion_inbox        — Buzón Asíncrono Tipado (Daddy → Embrión).
  2) embrion_audit_log    — Trazabilidad del procesamiento del inbox.

Ambas con RLS service_role_only (DSC-S-006 v1.1).

Idempotente: CREATE TABLE IF NOT EXISTS + CREATE POLICY guardado con NOT EXISTS check.
Ejecutar dos veces seguidas NO rompe nada.
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

MIGRATION_PATH = "migrations/sql/0012_embrion_inbox.sql"
TABLES = ("embrion_inbox", "embrion_audit_log")

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
for table in TABLES:
    cur.execute(
        """
        SELECT c.relname, c.relrowsecurity,
               (SELECT count(*) FROM pg_policies
                WHERE schemaname='public' AND tablename = c.relname) AS policy_count
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relname = %s
        """,
        (table,),
    )
    row = cur.fetchone()
    if not row:
        print(f"    FAIL: tabla {table} no encontrada")
        sys.exit(3)
    name, rls, pol_count = row
    print(f"    table={name}  rls={rls}  policies={pol_count}")
    if not rls:
        print(f"    FAIL: RLS no quedó habilitado en {table}")
        sys.exit(4)
    if pol_count < 1:
        print(f"    FAIL: no hay policies activas en {table}")
        sys.exit(5)

print("[3] Policies específicas:")
cur.execute(
    """
    SELECT tablename, policyname, cmd, roles
    FROM pg_policies
    WHERE schemaname='public' AND tablename IN %s
    ORDER BY tablename, policyname
    """,
    (TABLES,),
)
for table, pname, cmd, roles in cur.fetchall():
    print(f"    {table}.{pname}  cmd={cmd}  roles={roles}")

print("[4] Índices creados:")
cur.execute(
    """
    SELECT indexname, tablename
    FROM pg_indexes
    WHERE schemaname='public' AND tablename IN %s
    ORDER BY tablename, indexname
    """,
    (TABLES,),
)
for indexname, tablename in cur.fetchall():
    print(f"    {tablename}.{indexname}")

print("[5] Auditoría RLS coverage global:")
cur.execute(
    """
    SELECT
      (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
       WHERE n.nspname = 'public' AND c.relkind = 'r') AS total_tables,
      (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
       WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relrowsecurity = true) AS tables_rls
    """
)
total, with_rls = cur.fetchone()
print(f"    {with_rls}/{total} tablas con RLS")
if with_rls != total:
    print(f"    FAIL: aún hay {total - with_rls} tabla(s) sin RLS")
    sys.exit(6)

print(f"\n=== MIGRACIÓN 0012 APLICADA — {with_rls}/{total} tablas con RLS ===")
