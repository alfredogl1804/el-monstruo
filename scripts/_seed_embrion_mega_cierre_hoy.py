"""Sembrar semilla embrion_memoria al cierre del Sprint MEGA-CIERRE-HOY (Hilo Catastro)."""
from __future__ import annotations
import os
import sys
import psycopg

CONTENIDO = (
    "Sprint MEGA-CIERRE-HOY Catastro TA1+TA2+TA5 CERRADO. "
    "_tmp_notif.md eliminado (commit afe3d41). "
    "Migration 0023 rotor_activity_log aplicada a Supabase prod con RLS + "
    "policy service_role_only + smoke 4/4 verde (commit c1d1fc0). "
    "Verificación runtime post-Ejecutor 1 TA3: V3 (Railway flags "
    "COWORK_HOOK_ENABLED/SESSION_PERSIST/PREFLIGHT_REQUIRED=true) y V4 "
    "(kernel /health healthy v0.84.8-sprint-memento, AsyncPostgresSaver activo, "
    "embrion_loop running) VERDES. V1 (cowork_sesiones) y V2 (t1_audit_log.jsonl) "
    "en estado t=0 esperando primer tráfico Cowork real. Conclusión: kernel asiste "
    "a Cowork ACTIVO via flags Fase 1 (T1+T4+T5 de COWORK-RUNTIME-001)."
)


def main() -> int:
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        print("ERROR: SUPABASE_DB_URL not set", file=sys.stderr)
        return 1
    with psycopg.connect(db_url, sslmode="require") as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.embrion_memoria (tipo, contenido, hilo_origen, importancia)
                VALUES (%s, %s, %s, %s)
                RETURNING id, created_at
                """,
                ("decision", CONTENIDO, "manus-hilo-catastro", 9),
            )
            row = cur.fetchone()
            conn.commit()
            print(f"[VERDE] semilla sembrada id={row[0]} created_at={row[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
