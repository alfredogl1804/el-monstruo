#!/usr/bin/env python3
"""Aplicar migración 0003 (extensión de loop_detection_log)."""

import os
import sys

import psycopg2

DB_URL = os.environ.get("SUPABASE_DB_URL")
if not DB_URL:
    print("FATAL: SUPABASE_DB_URL no esta seteada")
    sys.exit(99)

MIG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "migrations",
    "sql",
    "0003_loop_detection_log_self_verifier.sql",
)

with open(MIG) as f:
    sql = f.read()

print(f"Aplicando: {MIG}")
conn = psycopg2.connect(DB_URL)
conn.autocommit = False
try:
    with conn.cursor() as cur:
        cur.execute(sql)
    with conn.cursor() as cur:
        cur.execute("""
          SELECT column_name, data_type FROM information_schema.columns
          WHERE table_schema='public' AND table_name='loop_detection_log'
          ORDER BY ordinal_position
        """)
        cols = cur.fetchall()
    print(f"Columnas finales ({len(cols)}):")
    new_cols = {
        "cycle_id",
        "decision_purpose",
        "decision_novelty",
        "decision_verifiable",
        "votes_no",
        "aborted",
        "embrion_thought",
        "embrion_thought_hash",
        "similarity_match_id",
        "trigger_type",
        "reasoning",
    }
    found = set()
    for n, t in cols:
        marker = " ← NEW" if n in new_cols else ""
        print(f"  {n:25s} {t:30s}{marker}")
        if n in new_cols:
            found.add(n)
    missing = new_cols - found
    if missing:
        print(f"❌ FALTAN: {missing}")
        conn.rollback()
        sys.exit(2)
    conn.commit()
    print("\n✅ Migración 0003 aplicada exitosamente.")
finally:
    conn.close()
