"""Verifica estado actual de catastro_agentes pre-migración 039.

Schema reales descubiertos:
  - PK = id (text, slug-style)
  - trono_dominio (numeric, NULL) NO se usa para flag de trono
  - vista catastro_tronos_agentes: dominio, trono_id, trono_nombre, score, bonus_curador
  - Total filas: 98
  - Macroárea CHECK: solo 'agentes'
"""

import os

import psycopg

DB_URL = os.environ["SUPABASE_DB_URL"]

with psycopg.connect(DB_URL) as conn, conn.cursor() as cur:
    print("=" * 80)
    print("ESTADO PRE-MIGRACION 039 — catastro_agentes")
    print("=" * 80)

    cur.execute("""
        SELECT dominio, COUNT(*) AS n
        FROM catastro_agentes
        GROUP BY dominio
        ORDER BY dominio
    """)
    print(f"\n{'dominio':<40} {'productos':>10}")
    print("-" * 55)
    total = 0
    for d, n in cur.fetchall():
        print(f"{d:<40} {n:>10}")
        total += n
    print(f"{'TOTAL':<40} {total:>10}")

    print("\n--- TRONOS ACTUALES (vista catastro_tronos_agentes) ---")
    cur.execute("""
        SELECT dominio, trono_id, trono_nombre, score, bonus_curador
        FROM catastro_tronos_agentes
        ORDER BY dominio
    """)
    for d, tid, tnom, sc, bc in cur.fetchall():
        bonus = f" (+{bc})" if bc and bc > 0 else ""
        print(f"  {d:<40} -> {tid:<28} ({tnom}) score={sc}{bonus}")

    print("\n--- PRODUCTOS CRITICOS (existencia + bonus) ---")
    slugs = [
        "devin",
        "canva-ai",
        "claude-cowork",
        "promptfoo",
        "arize-phoenix",
        "looka",
        "lakera",
        "braintrust",
        "manus",
        "higgsfield",
        "kimi-k2-6-agent-swarm",
        "perplexity-personal-computer",
        "lovable",
        "claude-ai",
        "n8n-llm-nodes",
        "clay",
    ]
    for slug in slugs:
        cur.execute(
            "SELECT id, nombre, dominio, tier_seed, bonus_curador, LEFT(COALESCE(bonus_curador_razon,''),80) FROM catastro_agentes WHERE id = %s",
            (slug,),
        )
        r = cur.fetchone()
        if r:
            print(f"  ✓ {r[0]:<32} dom={r[2]:<35} tier={r[3]} bonus={r[4]:>3}")
            if r[5]:
                print(f"     razon: {r[5]}...")
        else:
            print(f"  ✗ {slug:<32} — NO EXISTE")

    print("\n--- CONTEO catastro_modelos ---")
    cur.execute("SELECT COUNT(*) FROM catastro_modelos")
    n_modelos = cur.fetchone()[0]
    print(f"  Total: {n_modelos}")
    cur.execute("""
        SELECT id, nombre FROM catastro_modelos
        WHERE id IN ('kimi-k2-6', 'perplexity-sonar-pro', 'sora-2', 'veo-3-1')
        ORDER BY id
    """)
    print("  4 LLMs faltantes (Sprint 88.1):")
    for r in cur.fetchall():
        print(f"    ✓ {r[0]:<32} ({r[1]})")

print("\n" + "=" * 80)
print("FIN VERIFICACION")
print("=" * 80)
