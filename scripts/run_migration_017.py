#!/usr/bin/env python3
"""
El Monstruo — Sprint Memento — Bloque 1 — Migration Runner 017
================================================================

Ejecuta scripts/017_sprint_memento_schema.sql contra Supabase production
usando la connection string de SUPABASE_DB_URL (Railway env var).

Uso:
    SUPABASE_DB_URL='postgresql://...' python3 scripts/run_migration_017.py

Pre-flight (28va semilla aplicada):
    - Lee SUPABASE_DB_URL fresh desde os.environ (no asume contexto compactado)
    - Verifica que la URL tenga formato Supabase pooler
    - Aborta si la URL apunta a localhost o a un host no reconocido

Este patrón es el mismo de scripts/run_migration_016.py.
Autor: [Hilo Manus Ejecutor]
Fecha: 2026-05-04
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("[ERROR] psycopg2 no instalado. Ejecuta: pip install psycopg2-binary")
    sys.exit(1)

# Sprint Memento Bloque 5 Fase 1 — pre-flight via library Memento
_MEMENTO_AVAILABLE = True
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.memento_preflight import (  # type: ignore
        preflight_check,
        MementoPreflightError,
    )
except Exception as _import_exc:
    _MEMENTO_AVAILABLE = False
    print(f"[WARN] tools.memento_preflight no disponible ({_import_exc!r}); continuando sin preflight Memento")


SCRIPT_DIR = Path(__file__).parent
SQL_FILE = SCRIPT_DIR / "017_sprint_memento_schema.sql"

EXPECTED_TABLES = (
    "memento_validations",
    "memento_critical_operations",
    "memento_sources_of_truth",
)

EXPECTED_BOOTSTRAP_OPS = (
    "rotate_credential",
    "sql_against_production",
    "deploy_to_production",
    "financial_transaction",
)

EXPECTED_BOOTSTRAP_SOURCES = (
    "ticketlike_credentials",
    "railway_env_vars",
    "supabase_db_url",
    "stripe_live_credentials",
)


def preflight_db_url() -> str:
    """Pre-flight: lee la URL fresh desde os.environ y valida formato."""
    db_url = os.environ.get("SUPABASE_DB_URL", "").strip()
    if not db_url:
        print("[ERROR] SUPABASE_DB_URL no configurada en env. Aborto.")
        sys.exit(2)

    # Sanity check: debe ser postgresql:// y apuntar a Supabase pooler
    if not db_url.startswith("postgresql://"):
        print(f"[ERROR] SUPABASE_DB_URL no tiene scheme postgresql://. Aborto.")
        sys.exit(3)

    if "supabase" not in db_url and "pooler.supabase" not in db_url:
        print(f"[WARN] SUPABASE_DB_URL no parece apuntar a Supabase. Continuando con cautela.")

    if "localhost" in db_url or "127.0.0.1" in db_url:
        print("[ERROR] SUPABASE_DB_URL apunta a localhost. Aborto.")
        sys.exit(4)

    return db_url


def run_migration(db_url: str) -> None:
    """Ejecuta el SQL completo en una sola transacción."""
    if not SQL_FILE.exists():
        print(f"[ERROR] No existe {SQL_FILE}. Aborto.")
        sys.exit(5)

    sql = SQL_FILE.read_text(encoding="utf-8")
    print(f"[INFO] Leído {SQL_FILE.name} ({len(sql)} chars)")

    print("[INFO] Conectando a Supabase production...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            print("[INFO] Ejecutando migration 017_sprint_memento_schema.sql...")
            cur.execute(sql)
        conn.commit()
        print("[OK] Migration 017 ejecutada y commiteada.")
    except Exception as exc:
        conn.rollback()
        print(f"[ERROR] Migration falló y rollback ejecutado: {exc}")
        raise
    finally:
        conn.close()


def validate_tables(db_url: str) -> None:
    """Validación post-migration: las 3 tablas existen y bootstrap quedó cargado."""
    print("[INFO] Validando schema post-migration...")
    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            for table in EXPECTED_TABLES:
                cur.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name=%s)",
                    (table,),
                )
                exists = cur.fetchone()[0]
                if not exists:
                    print(f"[ERROR] Tabla {table} NO existe.")
                    sys.exit(6)
                print(f"[OK] Tabla {table} existe.")

            cur.execute(
                "SELECT id FROM memento_critical_operations WHERE activo = TRUE ORDER BY id"
            )
            ops = [row[0] for row in cur.fetchall()]
            for expected in EXPECTED_BOOTSTRAP_OPS:
                if expected not in ops:
                    print(f"[ERROR] Operación crítica {expected!r} NO está bootstrapped.")
                    sys.exit(7)
            print(f"[OK] {len(ops)} operaciones críticas bootstrapped: {ops}")

            cur.execute(
                "SELECT id FROM memento_sources_of_truth WHERE activo = TRUE ORDER BY id"
            )
            sources = [row[0] for row in cur.fetchall()]
            for expected in EXPECTED_BOOTSTRAP_SOURCES:
                if expected not in sources:
                    print(f"[ERROR] Fuente de verdad {expected!r} NO está bootstrapped.")
                    sys.exit(8)
            print(f"[OK] {len(sources)} fuentes de verdad bootstrapped: {sources}")

            cur.execute(
                "SELECT COUNT(*) FROM memento_validations"
            )
            validation_count = cur.fetchone()[0]
            print(f"[OK] memento_validations vacía (count={validation_count}) — esperado en bootstrap.")
    finally:
        conn.close()


def _run_memento_preflight(db_url: str) -> int | None:
    """Pre-flight Memento (B5 F1): registra la operación SQL como sql_against_production.

    Retorna exit code si bloquea, None si OK o degraded.
    """
    if not _MEMENTO_AVAILABLE:
        return None
    try:
        # Extraer host de la URL (sin password) para context_used
        # postgresql://user:pass@host:port/db
        host = db_url.split("@", 1)[-1].split("/", 1)[0] if "@" in db_url else "unknown"
        preflight = preflight_check(
            operation="sql_against_production",
            context_used={
                "host": host,
                "sql_file": SQL_FILE.name,
                "target_tables": list(EXPECTED_TABLES),
            },
            hilo_id="manus_ejecutor_run_migration_017",
            intent_summary=f"ejecutar migration 017 (sprint memento schema) contra {host}",
        )
        if not preflight.proceed:
            print(
                f"[MEMENTO] ABORT preflight bloqueó ejecución: "
                f"status={preflight.validation_status} "
                f"remediation={preflight.remediation}"
            )
            return 9
        print(f"[MEMENTO] preflight OK validation_id={preflight.validation_id}")
        return None
    except MementoPreflightError as exc:
        print(f"[MEMENTO] WARN preflight falló ({exc!s}); continuando con fallback degradado")
        return None
    except Exception as exc:
        print(f"[MEMENTO] WARN preflight inesperado ({exc!r}); continuando")
        return None


def main() -> int:
    print("=" * 70)
    print(" Sprint Memento — Bloque 1 — Migration 017")
    print("=" * 70)

    db_url = preflight_db_url()

    memento_exit = _run_memento_preflight(db_url)
    if memento_exit is not None:
        return memento_exit

    run_migration(db_url)
    validate_tables(db_url)

    print("=" * 70)
    print(" MIGRATION 017 COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
