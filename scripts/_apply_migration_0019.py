#!/usr/bin/env python
"""Aplicar migración 0019_scheduled_tasks_unique_constraint.sql contra producción.

Sprint D-2 cleanup destructivo scheduled_tasks (Hilo Ejecutor 2 = manus_hilo_b).
Autorizado por: DSC-S-013_scheduled_tasks_cleanup_destructivo_v1.

Agrega UNIQUE(name, embrion_id) a public.scheduled_tasks. Esta migration
SOLO se puede aplicar cuando la tabla NO tiene duplicados — si hay
duplicados, Postgres rechaza la creación del constraint con
unique_violation (23505). Por lo tanto la migration es prueba binaria
post-cleanup.

Idempotente: el SQL usa DO $$ block que sale sin error si el constraint
ya existe.

Ejecutar dos veces seguidas NO rompe nada.

Usage:
  python3 scripts/_apply_migration_0019.py
"""
import os
import sys

try:
    import psycopg2
    from psycopg2 import errors as pg_errors
except ImportError:
    print("ERROR: psycopg2 no instalado. Instalar con: pip install psycopg2-binary")
    sys.exit(1)


DB_URL = os.environ.get("SUPABASE_DB_URL")
if not DB_URL:
    print("ERROR: SUPABASE_DB_URL no está en env")
    sys.exit(1)

# Agregar sslmode=require si no está
if "?" in DB_URL:
    if "sslmode" not in DB_URL:
        DB_URL = DB_URL + "&sslmode=require"
else:
    DB_URL = DB_URL + "?sslmode=require"

MIGRATION_PATH = "migrations/sql/0019_scheduled_tasks_unique_constraint.sql"
TARGET_TABLE = "scheduled_tasks"
TARGET_CONSTRAINT = "scheduled_tasks_name_embrion_unique"

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
except pg_errors.UniqueViolation as e:
    conn.rollback()
    print("    FAIL: la tabla scheduled_tasks tiene duplicados.")
    print(f"    Detalle: {e}")
    print()
    print("    El constraint UNIQUE(name, embrion_id) no puede crearse")
    print("    porque hay filas con la misma combinación (name, embrion_id).")
    print()
    print("    Acción requerida: ejecutar primero")
    print("      python3 scripts/_cleanup_scheduled_tasks_duplicates.py --apply")
    print("    (con EMBRION_D2_CLEANUP_AUTHORIZED=true en env)")
    print()
    print("    Luego reintentar este applier.")
    sys.exit(2)
except Exception as e:
    conn.rollback()
    print(f"    FAIL: {e}")
    sys.exit(3)

# Verificación post: el constraint existe
print("[2] Verificación post — constraint:")
cur.execute(
    """
    SELECT conname, contype, conrelid::regclass::text AS tabla,
           pg_get_constraintdef(oid) AS definicion
    FROM pg_constraint
    WHERE conrelid = 'public.scheduled_tasks'::regclass
      AND conname = %s
    """,
    (TARGET_CONSTRAINT,),
)
row = cur.fetchone()
if not row:
    print(f"    FAIL: constraint {TARGET_CONSTRAINT} no encontrado post-aplicación")
    sys.exit(4)
print(f"    OK — constraint={row[0]} tipo={row[1]} tabla={row[2]}")
print(f"    def: {row[3]}")

# Verificación: total rows y unique names
print("[3] Estado actual de scheduled_tasks:")
cur.execute(
    """
    SELECT
      COUNT(*) AS total_rows,
      COUNT(DISTINCT name) AS unique_names,
      COUNT(DISTINCT (name, embrion_id)) AS unique_pairs
    FROM scheduled_tasks
    """
)
row = cur.fetchone()
total, names, pairs = row
print(f"    total_rows={total}  unique_names={names}  unique_pairs={pairs}")
if total != pairs:
    print(f"    WARN: total_rows ({total}) != unique_pairs ({pairs}) — debería ser igual post-cleanup")

cur.close()
conn.close()
print()
print("DONE — migration 0019 aplicada y verificada.")
