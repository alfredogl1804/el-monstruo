#!/usr/bin/env python3
"""
Auditar estructura de la tabla budget_state y vecinas para Tarea 1.
Hace SELECT * LIMIT 3 vía PostgREST y reporta columnas + tipos inferidos.
"""
import json
import os
import sys
import requests

SUPA_URL = "https://xsumzuhwmivjgftsneov.supabase.co"
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
if not SUPA_KEY:
    print("FATAL: SUPABASE_SERVICE_KEY no seteada"); sys.exit(99)

HEADERS = {
    "apikey": SUPA_KEY,
    "Authorization": f"Bearer {SUPA_KEY}",
}

TABLES = [
    "budget_state",
    "embrion_memoria",
    "loop_detection_log",
    "error_memory",
]

for t in TABLES:
    print()
    print("=" * 70)
    print(f"Tabla: {t}")
    print("=" * 70)
    r = requests.get(
        f"{SUPA_URL}/rest/v1/{t}",
        headers={**HEADERS, "Prefer": "count=exact"},
        params={"limit": "3", "select": "*"},
        timeout=15,
    )
    print(f"  HTTP={r.status_code}")
    cr = r.headers.get("Content-Range", "?/?")
    print(f"  Content-Range: {cr}")
    if r.status_code != 200:
        print(f"  body: {r.text[:300]}")
        continue
    try:
        rows = r.json()
    except Exception as e:
        print(f"  parse fail: {e}")
        continue
    if not rows:
        print("  (sin filas)")
        continue
    cols = list(rows[0].keys())
    print(f"  Columnas ({len(cols)}):")
    for c in cols:
        sample = rows[0].get(c)
        if isinstance(sample, (dict, list)):
            ts = type(sample).__name__
            preview = json.dumps(sample, default=str)[:60]
        else:
            ts = type(sample).__name__
            preview = str(sample)[:60] if sample is not None else "NULL"
        print(f"    - {c:30s} {ts:10s} sample: {preview}")

    print(f"  Filas mostrandas: {len(rows)}")
    print(f"  Primera fila completa:")
    print("  " + json.dumps(rows[0], indent=2, default=str)[:600].replace("\n", "\n  "))
