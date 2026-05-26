#!/usr/bin/env python3
"""
Pre-commit hook anti-stale-audit del Guardian.
================================================
Sprint GUARDIAN-AUTONOMO-001 T6
Owner: Hilo Ejecutor 2 (manus_hilo_b)

Filosofia:
  - **No bloquear el commit**. El audit del Guardian corre en Railway con
    cron diario a las 03:00 UTC. Forzar un audit local antes de cada commit
    incrementaria el costo de iteracion sin beneficio proporcional.
  - **Pero**: si la ultima corrida en `guardian_audit_log` tiene > 48h,
    es senal de que el cron de Railway o la DB estan rotos. En ese caso
    emitimos un WARN visible al desarrollador.
  - Si no hay DB local (entorno dev sin secrets), el hook NO falla. Solo
    informa que no pudo verificar.

Exit codes:
  0 = OK (audit fresco o no-verificable sin DB, ambos no bloquean)
  0 = WARN visible (audit stale, pero NO bloquea por DSC-MO-006: no
      podemos asumir que un dev local puede arreglar un problema de
      infraestructura remota)
  2 = error de configuracion del hook (raro, e.g. import roto)

Configuracion en .pre-commit-config.yaml:

  - repo: local
    hooks:
      - id: guardian-stale-audit-warn
        name: Guardian Audit Stale Check (WARN only)
        entry: python scripts/_check_guardian_stale_audit.py
        language: system
        pass_filenames: false
        stages: [commit, push]
        verbose: true

Vars de entorno:
  SUPABASE_DB_URL: URL de Postgres (opcional, si falta el hook hace skip)
  GUARDIAN_STALE_HOURS: threshold de horas (default 48)
  GUARDIAN_STALE_HOOK_DISABLED: si "true", el hook no hace nada (escape hatch)
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

STALE_HOURS_DEFAULT = 48

# Codigos ANSI para WARN visible (la mayoria de terminales modernas)
YELLOW = "\033[33m"
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _print_banner(level: str, message: str) -> None:
    """Imprime un banner visible en stderr (pre-commit captura stdout)."""
    color = {"WARN": YELLOW, "ERROR": RED, "OK": GREEN}.get(level, "")
    print(
        f"\n{BOLD}{color}[guardian-stale-audit] {level}{RESET}{color} {message}{RESET}\n",
        file=sys.stderr,
    )


def main() -> int:
    # Escape hatch
    if os.environ.get("GUARDIAN_STALE_HOOK_DISABLED", "").lower() == "true":
        return 0

    db_url = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        # Dev sin DB local: no podemos verificar. No bloqueamos.
        _print_banner(
            "OK",
            "skip (sin SUPABASE_DB_URL/DATABASE_URL local; el audit corre en Railway)",
        )
        return 0

    try:
        threshold_hours = float(os.environ.get("GUARDIAN_STALE_HOURS", STALE_HOURS_DEFAULT))
    except ValueError:
        threshold_hours = STALE_HOURS_DEFAULT

    try:
        import psycopg2  # type: ignore[import-not-found]
    except ImportError:
        _print_banner(
            "OK",
            "skip (psycopg2 no instalado en el venv local; el audit corre en Railway)",
        )
        return 0

    sql = """
        SELECT MAX(created_at) AS last_run
        FROM public.guardian_audit_log
    """

    try:
        with psycopg2.connect(db_url, connect_timeout=5) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                row = cur.fetchone()
                last_run = row[0] if row else None
    except Exception as exc:
        _print_banner(
            "WARN",
            f"no se pudo conectar a DB ({type(exc).__name__}). "
            f"Hook no bloquea — el audit autoritativo corre en Railway.",
        )
        return 0

    if last_run is None:
        _print_banner(
            "WARN",
            "guardian_audit_log esta VACIO. "
            "Verificar que `daily_guardian_audit` esta registrado en "
            "scheduled_tasks y que el scheduler de Railway esta corriendo.",
        )
        return 0

    # Normalizar a UTC
    if last_run.tzinfo is None:
        last_run = last_run.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    age_hours = (now - last_run).total_seconds() / 3600.0

    if age_hours > threshold_hours:
        _print_banner(
            "WARN",
            f"ultima corrida del Guardian hace {age_hours:.1f}h "
            f"(threshold: {threshold_hours:.0f}h). "
            f"Posible causa: cron de Railway pausado, scheduled_tasks.paused=true, "
            f"o handler `daily_guardian_audit` no registrado. "
            f"Verificar: SELECT * FROM scheduled_tasks WHERE name='daily_guardian_audit';",
        )
        # NO bloqueamos (return 0). El warn es suficiente.
        return 0

    _print_banner(
        "OK",
        f"ultima corrida del Guardian hace {age_hours:.1f}h (fresco, threshold {threshold_hours:.0f}h)",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
