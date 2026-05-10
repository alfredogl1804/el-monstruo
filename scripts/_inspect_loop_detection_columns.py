"""Lista columnas reales de loop_detection_log usando psycopg directo."""
from __future__ import annotations

import os
import sys

import psycopg2

DBURL = os.environ.get("SUPABASE_DB_URL", "").strip()
if not DBURL:
    print("ERROR: SUPABASE_DB_URL env var requerida", file=sys.stderr)
    sys.exit(1)

# Forzar sslmode si no está
if "sslmode" not in DBURL:
    DBURL = DBURL + ("&" if "?" in DBURL else "?") + "sslmode=require"

conn = psycopg2.connect(DBURL)
cur = conn.cursor()

cur.execute(
    """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'loop_detection_log'
    ORDER BY ordinal_position
    """
)
rows = cur.fetchall()
print(f"loop_detection_log tiene {len(rows)} columnas:")
for col_name, data_type, is_nullable, default in rows:
    print(f"  {col_name:30s} {data_type:25s} nullable={is_nullable:5s} default={default}")

cur.close()
conn.close()
