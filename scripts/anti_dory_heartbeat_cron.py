#!/usr/bin/env python3
"""
Entrypoint del cron Railway para Anti-Dory HeartbeatWriter.

Sprint MANUS-ANTI-DORY-002 v1 FASE D3.
Doctrina §A.7 (HeartbeatWriter independencia crítica).

Ejecutado por Railway cron service cada 15 minutos:

    [deploy]
    cronSchedule = "*/15 * * * *"
    startCommand = "python scripts/anti_dory_heartbeat_cron.py"

GPT-5.5 Pro Modo Pro: "el black-box recorder NO puede depender del agente."
Si Manus está caído o congelado, este cron sigue corriendo y produciendo
snapshots útiles para recovery desde runtime_events recientes.

Decisiones técnicas:

1. NO depende de `tools/manus_bridge` ni `kernel/main` ni `kernel/engine`.
   Total NO-CRUCE con stack web principal.

2. Lee env vars al arrancar (Anti-F23 fail-fast):
   - ANTI_DORY_ENABLED (default "false")
   - ANTI_DORY_PROJECT_ID (default "el-monstruo")
   - ANTI_DORY_FRONT_IDS (CSV; default "MANUS-ANTI-DORY-002")
   - SUPABASE_URL + SUPABASE_SERVICE_KEY (vía build_default_broker_factory)

3. Si ANTI_DORY_ENABLED=false → exit 0 sin escribir nada (fail-open).

4. Si la conexión Supabase falla → exit 1 (Railway reintentará en el próximo tick).
   NO bloquea otros servicios.

5. Soporta múltiples frentes activos vía ANTI_DORY_FRONT_IDS=CSV.
   El cron itera cada front_id y emite un heartbeat por cada uno.

6. Exit codes:
   - 0: éxito o flag off
   - 1: error de conexión / RPC
   - 2: error de configuración

Logs a stdout (Railway los captura como log lines del servicio cron).
"""
from __future__ import annotations

import logging
import os
import sys
import time
from typing import List, Optional

# Configuración logging para Railway (stdout + level WARNING por defecto)
LOG_LEVEL = os.getenv("ANTI_DORY_CRON_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s anti_dory_cron %(levelname)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("anti_dory_cron")


def _parse_front_ids(csv: str) -> List[str]:
    """Parsea CSV de fronts. Vacío → ['default']."""
    items = [s.strip() for s in csv.split(",") if s.strip()]
    return items or ["default"]


def _is_enabled() -> bool:
    """Lee ANTI_DORY_ENABLED. Default false (fail-closed para evitar runtime no listo)."""
    raw = os.getenv("ANTI_DORY_ENABLED", "false").strip().lower()
    return raw in ("true", "1", "yes", "on")


def _load_writer():
    """Importa y construye HeartbeatWriter usando el factory canónico FASE D1.

    Aislado en función para que tests puedan monkey-patchear sin
    importar el módulo entero.
    """
    from kernel.anti_dory.supabase_client import build_default_broker
    from kernel.anti_dory.writers import HeartbeatWriter

    broker = build_default_broker()
    if broker is None:
        return None
    return HeartbeatWriter(broker._rpc, actor_type="system")


def tick_once(
    *,
    project_id: str,
    front_ids: List[str],
    writer=None,
    sleep_between_fronts_s: float = 0.0,
) -> int:
    """Ejecuta un tick por cada front_id. Retorna count de errores."""
    if writer is None:
        writer = _load_writer()
    if writer is None:
        logger.warning("anti_dory_cron: broker unavailable (env vars missing). Skipping tick.")
        return 0

    errors = 0
    for front_id in front_ids:
        t0 = time.monotonic()
        try:
            result = writer.tick(project_id=project_id, front_id=front_id)
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            if result.error:
                errors += 1
                logger.error(
                    "anti_dory_cron front=%s error=%s elapsed_ms=%d",
                    front_id, result.error, elapsed_ms,
                )
            else:
                logger.info(
                    "anti_dory_cron front=%s snapshot_id=%s accepted=%s elapsed_ms=%d",
                    front_id, result.snapshot_id, result.accepted, elapsed_ms,
                )
        except Exception as exc:  # noqa: BLE001 — cron debe seguir con otros frentes
            errors += 1
            logger.exception("anti_dory_cron front=%s fatal_exception=%s", front_id, exc)
        if sleep_between_fronts_s > 0:
            time.sleep(sleep_between_fronts_s)

    return errors


def main(argv: Optional[List[str]] = None) -> int:
    """Entrypoint principal."""
    if not _is_enabled():
        logger.info("anti_dory_cron: ANTI_DORY_ENABLED=false → exit 0 sin escribir.")
        return 0

    project_id = os.getenv("ANTI_DORY_PROJECT_ID", "el-monstruo").strip() or "el-monstruo"
    fronts_csv = os.getenv("ANTI_DORY_FRONT_IDS", "MANUS-ANTI-DORY-002")
    front_ids = _parse_front_ids(fronts_csv)

    logger.info(
        "anti_dory_cron: starting tick project=%s fronts=%s",
        project_id, front_ids,
    )

    errors = tick_once(project_id=project_id, front_ids=front_ids)
    if errors > 0:
        logger.error("anti_dory_cron: exit 1 (errors=%d)", errors)
        return 1
    logger.info("anti_dory_cron: exit 0 (success)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
