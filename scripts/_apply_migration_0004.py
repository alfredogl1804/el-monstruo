#!/usr/bin/env python
"""Aplicar migración 0004_embrion_write_proposals.sql contra prod (idempotente)."""

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

MIGRATION_PATH = "migrations/sql/0004_embrion_write_proposals.sql"

with open(MIGRATION_PATH) as f:
    sql = f.read()

print(f"[1] Aplicando {MIGRATION_PATH} ...")
conn = psycopg2.connect(DB_URL)
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute(sql)
    print("    OK")
except Exception as e:
    print(f"    FAIL: {e}")
    sys.exit(2)

print("[2] Verificación post — columnas:")
cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'embrion_write_proposals'
    ORDER BY ordinal_position
""")
cols = cur.fetchall()
for c, t in cols:
    print(f"    {c}: {t}")

print(f"[3] Total columnas: {len(cols)} (esperadas: 22)")

cur.execute("""
    SELECT indexname FROM pg_indexes
    WHERE tablename = 'embrion_write_proposals'
""")
idx = cur.fetchall()
print(f"[4] Índices ({len(idx)}):")
for (name,) in idx:
    print(f"    {name}")

cur.execute("""
    SELECT trigger_name FROM information_schema.triggers
    WHERE event_object_table = 'embrion_write_proposals'
""")
trg = cur.fetchall()
print(f"[5] Triggers ({len(trg)}):")
for (name,) in trg:
    print(f"    {name}")

cur.execute("SELECT count(*) FROM embrion_write_proposals")
(n,) = cur.fetchone()
print(f"[6] Filas actuales: {n}")

print("\n=== MIGRACIÓN 0004 APLICADA ===")
