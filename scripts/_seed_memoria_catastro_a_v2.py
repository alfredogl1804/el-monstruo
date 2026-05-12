"""Semilla embrion_memoria para cierre CATASTRO-A v2.

Sprint CATASTRO-A v2 (post-S89 v2 Opción B).
Ejecutar via: railway run python3 scripts/_seed_memoria_catastro_a_v2.py
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone

import psycopg2

RESUMEN = (
    "Sprint CATASTRO-A v2 CERRADO 3/3 verde post-S89 v2 Opción B. "
    "TA audit verde sobre 3 vistas (catastro_modelos_llm=41, catastro_agentes_2026=98, "
    "catastro_herramientas_ai=58) + 1 tabla (catastro_suppliers_humanos). "
    "TB poblamiento catastro_suppliers_humanos: 30 rows (6 reales verificados "
    "Colegio Notarial Yucatán + CICY con validation_status=verified_real_official, "
    "24 placeholders active=false con validation_status=pending_realtime_verification "
    "bajo DSC-V-002). PII metadata-only (verification_url, no email/phone directos). "
    "TC kernel/catastros/interfaces.py (~365 LOC) con 3 interfaces semánticas "
    "(CatastroLookupInterface, CatastroSearchInterface, CatastroOrchestrationInterface) "
    "+ 19/19 tests pass. Composición sobre las 4 abstracciones DSC-G-007.1 de Ejecutor 1. "
    "Reglas duras NO-CRUCE respetadas (migraciones 0021/0022, scaffolding 4 clases, "
    "PR #110 intactos). Deuda P2: diversificar suppliers (arq/valuador/contratista) "
    "convirtiendo placeholders a reales en próximo sprint. "
    "Handoff: Embrión puede consumir catastros via build_interfaces() pattern."
)


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL ausente", file=sys.stderr)
        return 1

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # Verificar schema embrion_memoria
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name='embrion_memoria'
            ORDER BY ordinal_position
        """)
        cols = cur.fetchall()
        print("Schema embrion_memoria:")
        for c in cols:
            print(f"  {c[0]} :: {c[1]} (nullable={c[2]})")

        # Insert
        seed_id = str(uuid.uuid4())
        import json
        contexto_json = json.dumps({
            "sprint": "CATASTRO-A v2",
            "fecha": "2026-05-12",
            "estado": "DECLARADO_3_DE_3_VERDE",
            "post": "S89 v2 Opción B",
            "commits": ["90c1696", "55afc06"],
            "reportes": [
                "bridge/manus_to_cowork_REPORTE_CATASTRO_A_v2_2026_05_12.md",
                "bridge/manus_to_cowork_CATASTRO_A_v2_TA_DONE_2026_05_12.md",
                "bridge/manus_to_cowork_CATASTRO_A_v2_TB_PROPUESTA_SUPPLIERS_2026_05_12.md",
            ],
            "deuda_p2": "diversificar suppliers (arq/valuador/contratista)",
        })
        cur.execute("""
            INSERT INTO public.embrion_memoria
              (id, tipo, importancia, hilo_origen, contenido, contexto, created_at)
            VALUES
              (%s, %s, %s, %s, %s, %s::jsonb, %s)
            RETURNING id
        """, (
            seed_id,
            "decision",
            8,
            "manus-hilo-catastro",
            RESUMEN,
            contexto_json,
            datetime.now(timezone.utc),
        ))
        new_id = cur.fetchone()[0]
        conn.commit()
        print(f"\nSemilla insertada: id={new_id}")
        print(f"Resumen ({len(RESUMEN)} chars): {RESUMEN[:200]}...")
        return 0

    except Exception as exc:
        conn.rollback()
        print(f"ERROR — rolled back: {exc}", file=sys.stderr)
        # Probablemente columna distinta; intentar con campos mínimos
        try:
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='embrion_memoria'")
            print("Cols disponibles:", [r[0] for r in cur.fetchall()])
        except Exception:
            pass
        return 2
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
