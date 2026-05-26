#!/usr/bin/env python3
"""Apply migration 039 (Sprint 88.3 — documentar tronos definitivos AGENTES)."""

import os
import sys
from pathlib import Path

import psycopg


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    sql_path = Path(__file__).parent / "039_sprint88_3_documentar_tronos_definitivos.sql"
    sql = sql_path.read_text()
    print(f"Applying migration: {sql_path.name} ({len(sql)} chars)")

    try:
        with psycopg.connect(dsn, autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(sql)

            # Verificar tronos post-migración
            cur.execute("""
                SELECT dominio, trono_id, trono_nombre, score, bonus_curador
                FROM catastro_tronos_agentes
                ORDER BY dominio
            """)
            print("\n=== TRONOS POST-039 ===")
            for d, tid, tnom, sc, bc in cur.fetchall():
                bonus = f" (+{bc})" if bc and bc > 0 else ""
                print(f"  {d:<35} -> {tid:<32} score={sc}{bonus}")

            # Verificar bonus razones documentadas
            cur.execute("""
                SELECT id, bonus_curador, LEFT(bonus_curador_razon, 100)
                FROM catastro_agentes
                WHERE id IN ('claude-cowork','devin','promptfoo','arize-phoenix','manus')
                ORDER BY id
            """)
            print("\n=== BONUS_RAZON DOCUMENTADAS ===")
            for r in cur.fetchall():
                print(f"  {r[0]:<25} bonus={r[1]:>3}: {r[2]}...")

        print("\nMIGRATION_039_OK")
        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
