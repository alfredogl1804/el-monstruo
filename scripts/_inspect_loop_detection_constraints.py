"""Inspecciona check constraints de loop_detection_log para entender valores válidos."""
from __future__ import annotations

import os
import sys

import psycopg2

DBURL = os.environ.get("SUPABASE_DB_URL", "").strip()
if not DBURL:
    print("ERROR: SUPABASE_DB_URL env var requerida", file=sys.stderr)
    sys.exit(1)

if "sslmode" not in DBURL:
    DBURL = DBURL + ("&" if "?" in DBURL else "?") + "sslmode=require"

conn = psycopg2.connect(DBURL)
cur = conn.cursor()

cur.execute(
    """
    SELECT conname, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'public.loop_detection_log'::regclass AND contype = 'c'
    """
)
rows = cur.fetchall()
print(f"loop_detection_log tiene {len(rows)} check constraints:")
for name, defn in rows:
    print(f"  {name}: {defn}")

# Ver también filas existentes con severity para tener ejemplos
cur.execute(
    """
    SELECT severity, COUNT(*)
    FROM loop_detection_log
    GROUP BY severity
    """
)
print("\nValores actuales en severity:")
for sev, cnt in cur.fetchall():
    print(f"  {sev!r}: {cnt} filas")

cur.close()
conn.close()
