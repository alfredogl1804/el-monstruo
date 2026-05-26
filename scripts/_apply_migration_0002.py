#!/usr/bin/env python3
"""
Aplicar migración 0002_embrion_budget_state.sql.

Idempotente: usa CREATE TABLE IF NOT EXISTS y CREATE INDEX IF NOT EXISTS.
Reentrante: se puede correr múltiples veces sin efectos secundarios.
"""

import os
import sys

import psycopg2

DB_URL = os.environ.get("SUPABASE_DB_URL")
if not DB_URL:
    print("FATAL: SUPABASE_DB_URL no esta seteada")
    sys.exit(99)

MIGRATION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "migrations",
    "sql",
    "0002_embrion_budget_state.sql",
)

with open(MIGRATION_PATH) as f:
    sql_content = f.read()

print(f"Aplicando migración: {MIGRATION_PATH}")
print(f"Tamaño: {len(sql_content)} bytes, {sql_content.count(chr(10))} lineas")
print()

conn = psycopg2.connect(DB_URL)
conn.autocommit = False
try:
    with conn.cursor() as cur:
        cur.execute(sql_content)

    # Verificación post: la tabla existe y tiene las columnas esperadas
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'embrion_budget_state'
            ORDER BY ordinal_position;
        """)
        cols = cur.fetchall()

    if not cols:
        print("ERROR: tabla embrion_budget_state NO existe post-migración")
        conn.rollback()
        sys.exit(2)

    print(f"Tabla embrion_budget_state OK ({len(cols)} columnas):")
    for name, dtype, nullable in cols:
        print(f"  {name:30s} {dtype:25s} nullable={nullable}")

    # Verificar índices
    with conn.cursor() as cur:
        cur.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname='public' AND tablename='embrion_budget_state'
            ORDER BY indexname;
        """)
        idxs = cur.fetchall()

    print(f"\nÍndices ({len(idxs)}):")
    for name, defn in idxs:
        print(f"  {name}: {defn[:80]}")

    # Confirmar comentarios (auto-doc)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT obj_description('public.embrion_budget_state'::regclass, 'pg_class');
        """)
        comment = cur.fetchone()[0]
    print(f"\nComment de tabla: {comment[:120]}")

    conn.commit()
    print("\n✅ Migración 0002 aplicada exitosamente.")
except Exception as e:
    conn.rollback()
    print(f"❌ Error aplicando migración: {e}")
    raise
finally:
    conn.close()
