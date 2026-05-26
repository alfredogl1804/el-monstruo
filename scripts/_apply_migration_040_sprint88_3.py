#!/usr/bin/env python3
"""Apply migration 040 — Sprint 88.3 macroárea VISION_GENERATIVA."""

import os
import sys
from pathlib import Path

import psycopg


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    sql_path = Path(__file__).parent / "040_sprint88_3_vision_generativa.sql"
    sql = sql_path.read_text()
    print(f"Applying migration: {sql_path.name} ({len(sql)} chars)")

    try:
        with psycopg.connect(dsn, autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(sql)

            # Verificar resultado
            cur.execute("""
                SELECT subdominio_primario, COUNT(*) AS n
                FROM catastro_vision_generativa
                GROUP BY subdominio_primario
                ORDER BY subdominio_primario
            """)
            print("\n=== PRODUCTOS POR SUBDOMINIO ===")
            for sd, n in cur.fetchall():
                print(f"  {sd:<40} {n}")

            cur.execute("""
                SELECT subdominio, trono_id, trono_nombre, score, bonus_curador,
                       licensing_risk, consent_required
                FROM catastro_tronos_vision_generativa
                ORDER BY subdominio
            """)
            print("\n=== TRONOS VISION_GENERATIVA ===")
            for r in cur.fetchall():
                lic = f" lic={r[5]}" if r[5] != "low" else ""
                cons = " consent=true" if r[6] else ""
                print(f"  {r[0]:<40} -> {r[1]:<32} score={r[3]:>3} (+{r[4]}){lic}{cons}")

            cur.execute("SELECT COUNT(*) FROM catastro_vision_generativa")
            total = cur.fetchone()[0]
            print(f"\n=== TOTAL PRODUCTOS VISION_GENERATIVA: {total} ===")

        print("\nMIGRATION_040_OK")
        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
