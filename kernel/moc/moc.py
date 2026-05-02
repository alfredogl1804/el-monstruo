"""
El Monstruo — MOC (Motor de Orquestación Central) — Sprint 36
==============================================================
El MOC es la "mente directora" del AutonomousRunner.

Arquitectura:
  AutonomousRunner (ejecuta jobs) ← MOC (decide qué ejecutar)
                                      ├── Priorizador (ordena jobs)
                                      └── Sintetizador (consolida resultados)

El MOC se integra al ciclo de vida del kernel:
  1. Al iniciar: arranca el AutonomousRunner con priorización MOC
  2. Cada SYNTHESIS_INTERVAL_H horas: genera un insight de ciclos
  3. Expone /v1/moc/status y /v1/moc/insights para observabilidad

Principio: El MOC no es un scheduler nuevo — es una capa de inteligencia
sobre el scheduler existente.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

from kernel.moc.priorizador import Priorizador
from kernel.moc.sintetizador import Sintetizador

logger = structlog.get_logger("kernel.moc")

# Intervalo de síntesis (horas)
SYNTHESIS_INTERVAL_H = int(os.environ.get("MOC_SYNTHESIS_INTERVAL_H", "6"))

# Ventana de análisis para síntesis (horas)
SYNTHESIS_WINDOW_H = int(os.environ.get("MOC_SYNTHESIS_WINDOW_H", "24"))


class MOC:
    """
    Motor de Orquestación Central.

    Integra el Priorizador y el Sintetizador para dirigir al AutonomousRunner.

    Dependencias (inyectadas):
        - db: SupabaseClient
        - router: RouterEngine (para síntesis LLM)
        - runner: AutonomousRunner (para priorización de jobs)
        - notifier: TelegramNotifier (para alertas urgentes)
    """

    def __init__(
        self,
        db: Any,
        router: Any,
        runner: Any,
        notifier: Optional[Any] = None,
    ):
        self._db = db
        self._router = router
        self._runner = runner
        self._notifier = notifier
        self._priorizador = Priorizador(db=db)
        self._sintetizador = Sintetizador(db=db, router=router)
        self._running = False
        self._synthesis_task: Optional[asyncio.Task] = None
        self._last_synthesis_at: Optional[datetime] = None
        self._insights_generated = 0

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "synthesis_interval_h": SYNTHESIS_INTERVAL_H,
            "synthesis_window_h": SYNTHESIS_WINDOW_H,
            "insights_generated": self._insights_generated,
            "last_synthesis_at": (self._last_synthesis_at.isoformat() if self._last_synthesis_at else None),
        }

    async def start(self) -> None:
        """Inicia el MOC: arranca el loop de síntesis periódica."""
        if self._running:
            logger.warning("moc_already_running")
            return
        self._running = True
        self._synthesis_task = asyncio.create_task(self._synthesis_loop())
        logger.info("moc_started", synthesis_interval_h=SYNTHESIS_INTERVAL_H)

    async def stop(self) -> None:
        """Detiene el MOC."""
        self._running = False
        if self._synthesis_task:
            self._synthesis_task.cancel()
            try:
                await self._synthesis_task
            except asyncio.CancelledError:
                pass
        logger.info("moc_stopped")

    async def priorizar_jobs(
        self,
        jobs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Prioriza una lista de jobs usando el Priorizador.
        Llamado por el AutonomousRunner antes de ejecutar jobs.
        """
        # Obtener gasto del día para el factor de presupuesto
        gasto_hoy = await self._get_gasto_hoy()
        return await self._priorizador.priorizar(jobs, gasto_hoy_usd=gasto_hoy)

    async def sintetizar_ciclos(
        self,
        window_hours: int = SYNTHESIS_WINDOW_H,
        user_id: str = "anonymous",
    ) -> dict[str, Any]:
        """
        Genera un insight consolidado de los ciclos recientes.
        Puede llamarse manualmente o por el loop periódico.
        """
        insight = await self._sintetizador.sintetizar(
            window_hours=window_hours,
            user_id=user_id,
        )

        self._last_synthesis_at = datetime.now(timezone.utc)
        self._insights_generated += 1

        # Notificar si hay alertas urgentes
        alerts = insight.get("alerts", [])
        if alerts and self._notifier:
            alert_text = "\n".join(f"⚠️ {a}" for a in alerts[:3])
            try:
                await self._notifier.send_message(
                    chat_id="anonymous",
                    text=f"🧠 **MOC Alert**\n{alert_text}",
                )
            except Exception as e:
                logger.warning("moc_notify_failed", error=str(e))

        return insight

    async def _synthesis_loop(self) -> None:
        """Loop periódico de síntesis — corre cada SYNTHESIS_INTERVAL_H horas."""
        interval_s = SYNTHESIS_INTERVAL_H * 3600
        while self._running:
            try:
                await asyncio.sleep(interval_s)
                if self._running:
                    logger.info("moc_synthesis_triggered", interval_h=SYNTHESIS_INTERVAL_H)
                    await self.sintetizar_ciclos()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("moc_synthesis_loop_error", error=str(e))

    async def _get_gasto_hoy(self) -> float:
        """Obtiene el gasto acumulado del día en USD desde Supabase."""
        try:
            today = datetime.now(timezone.utc).date().isoformat()
            rows = await self._db.select(
                "job_executions",
                filters={"status": "completed"},
                order_by="started_at",
                order_desc=True,
                limit=200,
            )
            gasto = 0.0
            for row in rows:
                started = row.get("started_at", "")
                if started and started.startswith(today):
                    # Estimar costo por tokens (aprox $0.000002 por token)
                    tokens = row.get("tokens_used", 0) or 0
                    gasto += tokens * 0.000002
            return gasto
        except Exception as e:
            logger.warning("moc_get_gasto_failed", error=str(e))
            return 0.0
