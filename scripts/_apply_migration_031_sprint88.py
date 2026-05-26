#!/usr/bin/env python3
"""
Sprint 88 - Aplica migración 031_sprint88_dominios_expandidos.sql.

Expande el CHECK constraint de catastro_agentes.dominio de 5 a 9 dominios
(agrega vibe_coding, creacion_audiovisual, branding_diseno, marketing_ventas).

Ejecutar via:
    railway run --service el-monstruo-kernel python3 scripts/_apply_migration_031_sprint88.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg


def main() -> int:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1

    sql_path = Path(__file__).parent / "031_sprint88_dominios_expandidos.sql"
    if not sql_path.exists():
        print(f"ERROR: SQL file not found: {sql_path}", file=sys.stderr)
        return 1

    sql = sql_path.read_text()
    print(f"Applying migration: {sql_path.name} ({len(sql)} bytes)")

    try:
        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                print("MIGRATION_OK")

                # Verificar el constraint expandido
                cur.execute(
                    """
                    SELECT pg_get_constraintdef(oid)
                    FROM pg_constraint
                    WHERE conname = 'chk_dominio_valido'
                      AND conrelid = 'catastro_agentes'::regclass
                    """
                )
                row = cur.fetchone()
                if row:
                    constraint_def = row[0]
                    print(f"NEW_CONSTRAINT: {constraint_def}")
                    # Verificar los 9 dominios
                    expected = [
                        "agentes_desarrollo",
                        "agentes_investigacion",
                        "agentes_ejecutores",
                        "agentes_multi_swarm",
                        "interfaces_usuario",
                        "agentes_vibe_coding",
                        "agentes_creacion_audiovisual",
                        "agentes_branding_diseno",
                        "agentes_marketing_ventas",
                    ]
                    missing = [d for d in expected if d not in constraint_def]
                    if missing:
                        print(f"WARNING: dominios faltantes: {missing}", file=sys.stderr)
                        return 1
                    print("VERIFICATION_OK: 9 dominios válidos en constraint")
                else:
                    print("ERROR: chk_dominio_valido no encontrado", file=sys.stderr)
                    return 1

        return 0
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
