#!/usr/bin/env python3
"""Apply migration 041 — fix vista tronos VISION_GENERATIVA con UNNEST."""
import os
import sys
from pathlib import Path
import psycopg


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    sql_path = Path(__file__).parent / "041_sprint88_3_vision_tronos_multidominio.sql"
    sql = sql_path.read_text()
    print(f"Applying migration: {sql_path.name} ({len(sql)} chars)")

    try:
        with psycopg.connect(dsn, autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(sql)

            cur.execute("""
                SELECT subdominio, trono_id, trono_nombre, score, bonus_curador,
                       licensing_risk, consent_required
                FROM catastro_tronos_vision_generativa
                ORDER BY subdominio
            """)
            print("\n=== TRONOS VISION_GENERATIVA (post-fix) ===")
            for r in cur.fetchall():
                lic = f" lic={r[5]}" if r[5] != "low" else ""
                cons = " consent=true" if r[6] else ""
                print(f"  {r[0]:<40} -> {r[1]:<32} score={r[3]:>3} (+{r[4]}){lic}{cons}")

        print("\nMIGRATION_041_OK")
        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
