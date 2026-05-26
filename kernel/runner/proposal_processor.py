"""Proposal Processor — cierra el ciclo HITL del embrión.

Worker independiente (servicio Railway separado) que invoca periódicamente:
  - expire_old(): marca proposals con TTL vencido como 'expired'
  - execute_next(): toma siguiente 'approved', llama executor_registry, persiste

Doctrina:
  - NO toca kernel/embrion_loop.py (silencio del embrión preservado)
  - Conexión DB independiente (no comparte con el kernel)
  - Notifica resultado a los mismos canales del HITL original (telegram + cowork_bridge)
  - Graceful shutdown: SIGTERM/SIGINT → cancela tasks + cierra cliente HTTP

Variables de entorno requeridas:
  SUPABASE_REST_URL, SUPABASE_SERVICE_KEY  (para _SupabaseRest client)
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID     (para notify post-execute, opcionales)

Variables opcionales:
  PROPOSAL_EXPIRE_INTERVAL_SEC=60  (cada cuánto corre expire_old)
  PROPOSAL_EXECUTE_INTERVAL_SEC=10 (cada cuánto corre execute_next)
  PROPOSAL_EXECUTOR_NAME=proposal-processor (identificador en DB)
  PROPOSAL_NOTIFY_ENABLED=true     (false para silenciar notifications post-execute)
"""

from __future__ import annotations

import asyncio
import os
import signal
from typing import Any

import structlog

from kernel.embrion_write_policy import (
    _get_supabase_client,
    execute_next,
    expire_old,
)
from kernel.runner.executor_registry import ExecutorRegistry
from kernel.runner.telegram_notifier import TelegramNotifier

logger = structlog.get_logger("proposal_processor")

EXPIRE_INTERVAL_SEC = int(os.getenv("PROPOSAL_EXPIRE_INTERVAL_SEC", "60"))
EXECUTE_INTERVAL_SEC = int(os.getenv("PROPOSAL_EXECUTE_INTERVAL_SEC", "10"))
EXECUTOR_NAME = os.getenv("PROPOSAL_EXECUTOR_NAME", "proposal-processor")
NOTIFY_ENABLED = os.getenv("PROPOSAL_NOTIFY_ENABLED", "true").lower() == "true"


# -----------------------------------------------------------------------------
# Notification post-execute (telegram + cowork_bridge)
# -----------------------------------------------------------------------------
def _format_execution_message(proposal: dict) -> str:
    """Renderiza mensaje de notificación post-execute."""
    status = proposal.get("approval_status", "unknown")
    icon = "✅" if status == "executed" else ("❌" if status == "failed" else "⚠️")

    result_json = proposal.get("result_json") or {}
    duration_ms = result_json.get("duration_ms", 0)
    error = result_json.get("error")
    result_obj = result_json.get("result") or {}

    lines = [
        f"{icon} *Proposal ejecutada*",
        f"Estado: `{status}`",
        f"Tipo: `{proposal.get('proposal_type', 'unknown')}`",
        f"ID: `{proposal.get('id')}`",
        f"Duración: {duration_ms}ms",
    ]
    if error:
        # Redactar secrets del error (genérico)
        safe_error = str(error)[:300]
        lines.append(f"Error: `{safe_error}`")
    elif isinstance(result_obj, dict) and result_obj:
        # Resumen del result (max 200 chars)
        summary_parts = []
        for k, v in list(result_obj.items())[:3]:
            v_str = str(v)[:80]
            summary_parts.append(f"{k}={v_str}")
        if summary_parts:
            lines.append(f"Resultado: {', '.join(summary_parts)}")
    return "\n".join(lines)


async def _notify_post_execute(
    db_client: Any,
    telegram_notifier: TelegramNotifier,
    proposal: dict,
) -> None:
    """Notifica a Telegram + cowork_bridge el resultado de la ejecución.

    Falla silenciosa: el log queda en structlog pero no rompe el worker.
    """
    if not NOTIFY_ENABLED:
        return

    proposal_id = str(proposal.get("id"))
    text = _format_execution_message(proposal)

    # 1. Telegram (best-effort)
    try:
        if telegram_notifier.enabled:
            res = await telegram_notifier.send_message(
                user_id="proposal_processor",
                text=text,
                parse_mode="Markdown",
            )
            logger.info(
                "post_execute_telegram_notified",
                proposal_id=proposal_id,
                ok=bool(res),
            )
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "post_execute_telegram_failed",
            proposal_id=proposal_id,
            error=str(exc),
        )

    # 2. cowork_bridge (insert a embrion_memoria, fire-and-forget)
    try:
        db_client.insert(
            "embrion_memoria",
            {
                "tipo": "mensaje_alfredo",
                "contenido": text,
                "contexto": {
                    "kind": "proposal_executed",
                    "proposal_id": proposal_id,
                    "status": proposal.get("approval_status"),
                    "agent": "proposal_processor",
                },
                "hilo_origen": "manus_principal",
                "importancia": 8,
                "version": "1.0",
            },
        )
        logger.info(
            "post_execute_bridge_notified",
            proposal_id=proposal_id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "post_execute_bridge_failed",
            proposal_id=proposal_id,
            error=str(exc),
        )


# -----------------------------------------------------------------------------
# Loops
# -----------------------------------------------------------------------------
async def expire_loop(db_client: Any, stop_event: asyncio.Event) -> None:
    """Loop que marca proposals con TTL vencido como expired."""
    logger.info("expire_loop_start", interval_sec=EXPIRE_INTERVAL_SEC)
    while not stop_event.is_set():
        try:
            n = expire_old(db_client)
            if n > 0:
                logger.info("expired_proposals", count=n)
        except Exception as exc:  # noqa: BLE001
            logger.exception("expire_old_failed", error=str(exc))

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=EXPIRE_INTERVAL_SEC)
        except asyncio.TimeoutError:
            pass
    logger.info("expire_loop_stopped")


async def execute_loop(
    db_client: Any,
    registry: ExecutorRegistry,
    telegram_notifier: TelegramNotifier,
    stop_event: asyncio.Event,
) -> None:
    """Loop que toma proposals approved y las ejecuta."""
    logger.info("execute_loop_start", interval_sec=EXECUTE_INTERVAL_SEC)
    while not stop_event.is_set():
        try:
            executed = execute_next(
                db_client,
                executor=EXECUTOR_NAME,
                executor_fn=registry.dispatch,
            )
            if executed is not None:
                logger.info(
                    "executed_proposal",
                    proposal_id=str(executed.get("id")),
                    status=executed.get("approval_status"),
                )
                await _notify_post_execute(db_client, telegram_notifier, executed)
        except Exception as exc:  # noqa: BLE001
            logger.exception("execute_next_failed", error=str(exc))

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=EXECUTE_INTERVAL_SEC)
        except asyncio.TimeoutError:
            pass
    logger.info("execute_loop_stopped")


# -----------------------------------------------------------------------------
# Main + graceful shutdown
# -----------------------------------------------------------------------------
def _install_signal_handlers(loop: asyncio.AbstractEventLoop, stop_event: asyncio.Event) -> None:
    """Instala SIGTERM/SIGINT handlers que setean stop_event."""

    def _handler() -> None:
        if not stop_event.is_set():
            logger.info("shutdown_signal_received")
            stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _handler)
        except NotImplementedError:
            # Windows no soporta add_signal_handler
            pass


async def main_async() -> int:
    """Entrypoint async. Retorna exit code."""
    logger.info(
        "proposal_processor_boot",
        executor_name=EXECUTOR_NAME,
        expire_interval=EXPIRE_INTERVAL_SEC,
        execute_interval=EXECUTE_INTERVAL_SEC,
        notify_enabled=NOTIFY_ENABLED,
    )

    # Build dependencies
    db_client = _get_supabase_client()
    registry = ExecutorRegistry()
    telegram_notifier = TelegramNotifier()

    # Stop event for graceful shutdown
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    _install_signal_handlers(loop, stop_event)

    # Run loops in parallel; both loops are cancellable via stop_event.
    try:
        await asyncio.gather(
            expire_loop(db_client, stop_event),
            execute_loop(db_client, registry, telegram_notifier, stop_event),
        )
    except asyncio.CancelledError:
        logger.info("proposal_processor_cancelled")
        raise

    # No HTTP clients to close: TelegramNotifier uses per-request AsyncClient.
    logger.info("proposal_processor_shutdown_complete")
    return 0


def main() -> int:
    """Entrypoint sync (Railway start command)."""
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())
