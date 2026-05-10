#!/usr/bin/env python3
"""Apply migration 034 (bonus_curador + refresh tronos) to Supabase prod."""
import os
import sys
from pathlib import Path
import psycopg


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    sql_path = Path(__file__).parent / "034_sprint88_bonus_curador.sql"
    sql = sql_path.read_text()
    print(f"Applying migration: {sql_path.name} ({len(sql)} chars)")

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                # Verify bonus aplicado
                cur.execute("""
                    SELECT id, nombre, bonus_curador, LEFT(bonus_curador_razon, 80)
                    FROM catastro_agentes WHERE bonus_curador > 0
                    ORDER BY id
                """)
                print("\n=== BONUS CURADOR APLICADOS ===")
                for r in cur.fetchall():
                    print(f"  {r[0]} ({r[1]}): +{r[2]} | {r[3]}...")

                # Listar nuevos tronos
                cur.execute("""
                    SELECT dominio, trono_id, trono_nombre, score, bonus_curador
                    FROM catastro_tronos_agentes
                    ORDER BY dominio
                """)
                print("\n=== TRONOS REFRESCADOS ===")
                for d, tid, tnom, sc, bc in cur.fetchall():
                    bonus = f" (+{bc} bonus)" if bc > 0 else ""
                    print(f"  [{d:<32s}] -> {tnom} (id={tid}, score={sc}{bonus})")

        print("\nMIGRATION_034_OK")
        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
