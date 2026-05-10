#!/usr/bin/env python3
"""
Extrae el bucle de eco activo del 10-may (cycles 76-216) y muestras del
bucle 30-abr → 1-may para usar como fixtures en los tests del Self-Verifier.

Output: tests/fixtures/embrion_loop_samples.json
"""
import json, os, sys
import psycopg2
import psycopg2.extras

DB_URL = os.environ.get("SUPABASE_DB_URL")
if not DB_URL: print("FATAL"); sys.exit(99)

conn = psycopg2.connect(DB_URL)
out = {}

# 1) Bucle activo 10-may, cycles 76-216
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("""
        SELECT id, contenido, created_at, tipo, contexto
        FROM embrion_memoria
        WHERE tipo IN ('respuesta_embrion','pensamiento','latido')
          AND created_at >= '2026-05-10T02:00:00+00:00'
          AND created_at <= '2026-05-10T05:00:00+00:00'
        ORDER BY created_at ASC
        LIMIT 80
    """)
    rows = cur.fetchall()

# Convertir UUIDs a str y datetime a iso
def serialize(row):
    o = {}
    for k,v in row.items():
        if hasattr(v, "isoformat"): o[k] = v.isoformat()
        else: o[k] = str(v) if hasattr(v, "hex") else v
    return o

out["bucle_10_may_02h_05h"] = [serialize(r) for r in rows]

# 2) Bucle 30-abr → 1-may (10 ciclos similares)
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("""
        SELECT id, contenido, created_at, tipo
        FROM embrion_memoria
        WHERE tipo IN ('respuesta_embrion','pensamiento')
          AND created_at >= '2026-04-30T00:00:00+00:00'
          AND created_at <= '2026-05-01T23:59:59+00:00'
        ORDER BY created_at ASC
        LIMIT 30
    """)
    rows = cur.fetchall()
out["bucle_30_abr_1_may"] = [serialize(r) for r in rows]

# 3) Muestras de pensamientos/respuestas claramente útiles (no eco)
# Buscamos los que mencionen archivos, commits, o decisiones
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("""
        SELECT id, contenido, created_at, tipo
        FROM embrion_memoria
        WHERE tipo IN ('respuesta_embrion','pensamiento')
          AND (
            contenido ILIKE '%escrib%' OR
            contenido ILIKE '%commit%' OR
            contenido ILIKE '%implemen%' OR
            contenido ILIKE '%decid%'
          )
        ORDER BY created_at DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
out["muestras_utiles"] = [serialize(r) for r in rows]

OUT = "tests/fixtures/embrion_loop_samples.json"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"Bucle activo 10-may: {len(out['bucle_10_may_02h_05h'])} filas")
print(f"Bucle 30-abr→1-may:  {len(out['bucle_30_abr_1_may'])} filas")
print(f"Muestras útiles:     {len(out['muestras_utiles'])} filas")
print(f"Saved: {OUT}")
print()
# Mostrar 3 muestras del bucle activo (para inspección humana)
print("--- 3 muestras del bucle activo (¿son idénticas?) ---")
for r in out["bucle_10_may_02h_05h"][:3]:
    print(f"  [{r['tipo']:20s}] {r['created_at']} :: {(r['contenido'] or '')[:120]}")

conn.close()
