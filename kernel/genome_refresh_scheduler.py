"""
Genome Refresh Scheduler — Sprint 91.9
=======================================

Scheduler interno que mantiene `_genome_out/genome_now.json` actualizado
ejecutando `scripts/genome_live/run_all.py` cada 6 horas dentro del kernel.

Por qué interno (no GitHub Actions):
- No depende de Actions estando UP (incidente HTTP 500 de hoy lo demostró).
- No requiere subir `MONSTRUO_API_KEY` como secret externo.
- Sobrevive reinicios de Railway: APScheduler se inicia con cada lifespan.

Por qué BackgroundScheduler (no AsyncIOScheduler):
- run_all.py es un subprocess externo (~8-12 min). Lo corremos en thread
  para no bloquear el event loop FastAPI.
- Single-flight protegido: el endpoint `?refresh=full` y este scheduler
  comparten el mismo `state` de `kernel/genome_now_routes.py`.

Trigger:
- Boot: 5 minutos después de startup (warmup).
- Recurrente: cada 6 horas.

Si run_all.py falla, se loguea pero el scheduler sigue corriendo. El próximo
ciclo lo reintenta. Sin retry inmediato para evitar loops.

Ref: bridge/sprint_91_progress.md, kernel/genome_now_routes.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import structlog

logger = structlog.get_logger("kernel.genome_refresh")

ROOT = Path(__file__).resolve().parent.parent
RUN_ALL = ROOT / "scripts" / "genome_live" / "run_all.py"

# Intervalo en segundos: 6 horas.
DEFAULT_INTERVAL_HOURS = float(os.environ.get("GENOME_REFRESH_INTERVAL_HOURS", "6"))
DEFAULT_BOOT_DELAY_MIN = float(os.environ.get("GENOME_REFRESH_BOOT_DELAY_MIN", "5"))
DEFAULT_TIMEOUT_SEC = int(os.environ.get("GENOME_REFRESH_TIMEOUT_SEC", "900"))  # 15 min


def _run_genome_refresh() -> None:
    """
    Ejecuta scripts/genome_live/run_all.py como subprocess.

    Comparte el state global con `kernel/genome_now_routes.py` para que
    `?refresh=full` manual y este scheduler no entren en race conditions.
    """
    # Import lazy para evitar circular import en startup.
    # Compartir _JOB_STATE + _JOB_LOCK con genome_now_routes para single-flight.
    try:
        from kernel.genome_now_routes import _JOB_LOCK, _JOB_STATE as state
    except Exception:
        _JOB_LOCK = None
        state = None

    # Single-flight: si endpoint /refresh=full ya está corriendo, skip.
    if _JOB_LOCK is not None and not _JOB_LOCK.acquire(blocking=False):
        logger.info(
            "genome_refresh_skipped_lock_held",
            kind=state.get("kind") if state else None,
        )
        return

    if state is not None:
        if state.get("active"):
            # Defensa: si lock está libre pero active=True (ej. lock fue
            # liberado pero state no actualizado), saltamos para no romper
            # estado de un job en curso real.
            logger.info(
                "genome_refresh_skipped_already_running",
                kind=state.get("kind"),
                started_at=state.get("started_at"),
            )
            if _JOB_LOCK is not None:
                _JOB_LOCK.release()
            return
        state["active"] = True
        state["status"] = "running"
        state["kind"] = "full"  # Mismo kind que ?refresh=full manual.
        state["started_at"] = datetime.now(timezone.utc).isoformat()
        state["finished_at"] = None
        state["duration_sec"] = None
        state["last_error"] = None

    started_ts = time.time()
    logger.info(
        "genome_refresh_start",
        run_all=str(RUN_ALL),
        timeout_sec=DEFAULT_TIMEOUT_SEC,
    )

    if not RUN_ALL.exists():
        msg = f"run_all.py no encontrado en {RUN_ALL}"
        logger.warning("genome_refresh_missing_script", path=str(RUN_ALL))
        if state is not None:
            state["status"] = "failed"
            state["last_error"] = msg
            state["active"] = False
            state["finished_at"] = datetime.now(timezone.utc).isoformat()
        return

    try:
        proc = subprocess.run(
            [sys.executable, str(RUN_ALL)],
            cwd=str(ROOT),
            timeout=DEFAULT_TIMEOUT_SEC,
            capture_output=True,
            text=True,
            check=False,
        )
        duration = round(time.time() - started_ts, 1)
        if proc.returncode == 0:
            logger.info(
                "genome_refresh_success",
                duration_sec=duration,
                stdout_tail=proc.stdout[-300:] if proc.stdout else "",
            )
            if state is not None:
                state["status"] = "success"
                state["last_error"] = None
        else:
            err_tail = (proc.stderr or proc.stdout or "")[-500:]
            logger.warning(
                "genome_refresh_failed",
                returncode=proc.returncode,
                duration_sec=duration,
                stderr_tail=err_tail,
            )
            if state is not None:
                state["status"] = "failed"
                state["last_error"] = f"exit={proc.returncode}: {err_tail}"
    except subprocess.TimeoutExpired:
        logger.warning("genome_refresh_timeout", timeout_sec=DEFAULT_TIMEOUT_SEC)
        if state is not None:
            state["status"] = "failed"
            state["last_error"] = f"timeout {DEFAULT_TIMEOUT_SEC}s"
    except Exception as e:
        logger.warning("genome_refresh_exception", error=str(e))
        if state is not None:
            state["status"] = "failed"
            state["last_error"] = str(e)
    finally:
        if state is not None:
            duration = round(time.time() - started_ts, 1)
            state["active"] = False
            state["finished_at"] = datetime.now(timezone.utc).isoformat()
            state["duration_sec"] = duration
        if _JOB_LOCK is not None:
            try:
                _JOB_LOCK.release()
            except RuntimeError:
                # Lock already released (defensive).
                pass


def start_genome_refresh_scheduler():
    """
    Inicia el BackgroundScheduler. Idempotente (safe-call múltiple).

    Devuelve el scheduler o None si APScheduler no está disponible o el
    flag GENOME_REFRESH_DISABLED=1 está seteado.
    """
    if os.environ.get("GENOME_REFRESH_DISABLED", "").strip() in ("1", "true", "TRUE"):
        logger.info("genome_refresh_disabled_by_env")
        return None

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.interval import IntervalTrigger
    except ImportError:
        logger.warning("genome_refresh_apscheduler_not_installed")
        return None

    scheduler = BackgroundScheduler(timezone="UTC", daemon=True)

    interval_hours = DEFAULT_INTERVAL_HOURS
    boot_delay_min = DEFAULT_BOOT_DELAY_MIN

    # Boot run: warmup delay para evitar correr durante el startup.
    from datetime import timedelta

    first_run = datetime.now(timezone.utc) + timedelta(minutes=boot_delay_min)

    scheduler.add_job(
        _run_genome_refresh,
        trigger=IntervalTrigger(hours=interval_hours, start_date=first_run),
        id="genome_refresh_recurring",
        name="Genome Refresh (run_all.py) cada N horas",
        max_instances=1,  # Single-flight: si tarda >intervalo, no encola otro.
        coalesce=True,    # Si se perdieron N ejecuciones, solo corre 1 vez.
        misfire_grace_time=3600,  # 1h de gracia para misfires.
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        "genome_refresh_scheduler_started",
        interval_hours=interval_hours,
        boot_delay_min=boot_delay_min,
        first_run=first_run.isoformat(),
        timeout_sec=DEFAULT_TIMEOUT_SEC,
    )
    return scheduler


def shutdown_genome_refresh_scheduler(scheduler) -> None:
    """Apaga el scheduler limpiamente al lifespan shutdown."""
    if scheduler is None:
        return
    try:
        scheduler.shutdown(wait=False)
        logger.info("genome_refresh_scheduler_shutdown")
    except Exception as e:
        logger.warning("genome_refresh_scheduler_shutdown_failed", error=str(e))
