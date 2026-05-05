#!/usr/bin/env python3.11
"""
Runner Migration 020 — Sprint Memento Bloque 6
==============================================

Ejecuta scripts/020_memento_contamination_index.sql contra Supabase production.
Aplica preflight Memento (operation="kernel_admin_call") antes de tocar la DB.

Uso:
    SUPABASE_DB_URL=postgresql://... python3.11 scripts/run_migration_020.py
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

# Path setup para imports locales
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import psycopg2  # type: ignore

from tools.memento_preflight import preflight_check, MementoPreflightError

MIGRATION_SQL_FILE = Path(__file__).parent / "020_memento_contamination_index.sql"
HILO_ID = "manus_ejecutor_run_migration_020"
OPERATION = "kernel_admin_call"


def _run_preflight(db_url: str) -> bool:
    """Pre-flight Memento ANTES de tocar DB. Retorna True si seguir."""
    # Hash primeros 8 chars de la URL para auditoría sin exponer credenciales
    cred_hash = hashlib.sha256(db_url.encode("utf-8")).hexdigest()[:8]
    try:
        result = preflight_check(
            operation=OPERATION,
            context_used={
                "endpoint_target": "supabase_db_direct",
                "credential_hash_first_8": cred_hash,
                "host": (db_url.split("@")[1].split(":")[0] if "@" in db_url else "unknown"),
                "migration_file": MIGRATION_SQL_FILE.name,
            },
            hilo_id=HILO_ID,
            intent_summary=(
                f"Ejecutar migration {MIGRATION_SQL_FILE.name} (idx + COMMENT) "
                f"contra Supabase production."
            ),
        )
    except MementoPreflightError as exc:
        print(f"❌ Pre-flight Memento BLOQUEADO: {exc}", file=sys.stderr)
        return False

    if not result.proceed:
        print(
            f"❌ Pre-flight Memento NO autoriza: status={result.validation_status} "
            f"validation_id={result.validation_id}",
            file=sys.stderr,
        )
        return False

    print(
        f"✓ Pre-flight Memento OK: validation_id={result.validation_id} "
        f"freshness_s={result.context_freshness_seconds}"
    )
    return True


def _run_migration(db_url: str) -> int:
    """Ejecuta el SQL. Retorna 0 si OK, !=0 si error."""
    sql = MIGRATION_SQL_FILE.read_text(encoding="utf-8")

    print(f"→ Conectando a Supabase…")
    try:
        conn = psycopg2.connect(db_url)
    except Exception as exc:
        print(f"❌ No se pudo conectar a Supabase: {exc}", file=sys.stderr)
        return 1

    try:
        with conn:
            with conn.cursor() as cur:
                print(f"→ Ejecutando {MIGRATION_SQL_FILE.name}…")
                cur.execute(sql)

                # Verificar el índice
                cur.execute(
                    """
                    SELECT indexname FROM pg_indexes
                    WHERE tablename = 'memento_validations'
                      AND indexname = 'idx_memento_validations_contamination_warning'
                    """
                )
                row = cur.fetchone()
                if row:
                    print(f"✓ Índice creado/verificado: {row[0]}")
                else:
                    print("⚠️ Índice no encontrado tras la migration.")
                    return 2

        print("✓ Migration 020 completada con éxito.")
        return 0

    finally:
        conn.close()


def main() -> int:
    # Pre-flight: leer SUPABASE_DB_URL fresh (anti-Dory)
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        print(
            "❌ SUPABASE_DB_URL no está en el entorno. Exportala antes de ejecutar.",
            file=sys.stderr,
        )
        return 3

    if not _run_preflight(db_url):
        return 3

    return _run_migration(db_url)


if __name__ == "__main__":
    sys.exit(main())
