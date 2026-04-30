"""
El Monstruo — MOC Priorizador (Sprint 36)
==========================================
Motor de Orquestación Central (MOC) — Priorizador Dinámico.

Lee los scheduled_jobs de Supabase y asigna prioridades dinámicas
basándose en:
  - Urgencia temporal (cuánto tiempo lleva pendiente)
  - Tipo de tarea (impacto en el sistema)
  - Estado del sistema (presupuesto diario, carga actual)
  - Historial de ejecuciones (tasa de éxito, latencia promedio)

Principio: El MOC no reemplaza al AutonomousRunner — lo dirige.
El Runner ejecuta. El MOC decide qué ejecutar primero.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.moc.priorizador")

# ── Pesos de priorización ────────────────────────────────────────────
# Cada factor contribuye a un score final (0-100).
# Score más alto = mayor prioridad.

WEIGHT_URGENCY = 0.40       # Cuánto tiempo lleva pendiente
WEIGHT_IMPACT = 0.30        # Tipo de tarea / impacto en sistema
WEIGHT_BUDGET = 0.20        # Costo estimado vs presupuesto disponible
WEIGHT_HISTORY = 0.10       # Tasa de éxito histórica

# Impacto por tipo de tarea (0-10)
TASK_IMPACT_MAP: dict[str, float] = {
    "embrion_cycle": 9.0,       # Ciclos del Embrión — máxima prioridad
    "deep_think": 8.0,          # Análisis profundo
    "memory_consolidation": 7.5, # Consolidación de memoria
    "knowledge_graph": 7.0,     # Actualización del grafo de conocimiento
    "report": 6.0,              # Generación de reportes
    "notification": 5.0,        # Notificaciones al usuario
    "maintenance": 4.0,         # Tareas de mantenimiento
    "default": 5.0,             # Tarea genérica
}

# Presupuesto diario del sistema (USD)
DAILY_BUDGET_USD = float(2.00)


class Priorizador:
    """
    Asigna prioridades dinámicas a los scheduled_jobs pendientes.

    Uso:
        priorizador = Priorizador(db=db_client)
        jobs_priorizados = await priorizador.priorizar(jobs_pendientes)
    """

    def __init__(self, db: Any):
        self._db = db

    async def priorizar(
        self,
        jobs: list[dict[str, Any]],
        gasto_hoy_usd: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Recibe una lista de jobs pendientes y retorna la lista ordenada
        por prioridad descendente (mayor score primero).

        Args:
            jobs: Lista de jobs de Supabase (tabla scheduled_jobs).
            gasto_hoy_usd: Gasto acumulado del día en USD.

        Returns:
            Lista de jobs con campo `moc_priority_score` añadido, ordenada.
        """
        if not jobs:
            return []

        now = datetime.now(timezone.utc)
        presupuesto_restante = max(0.0, DAILY_BUDGET_USD - gasto_hoy_usd)
        presupuesto_ratio = presupuesto_restante / DAILY_BUDGET_USD  # 0.0 - 1.0

        scored_jobs = []
        for job in jobs:
            score = self._calcular_score(job, now, presupuesto_ratio)
            job_con_score = dict(job)
            job_con_score["moc_priority_score"] = round(score, 2)
            scored_jobs.append(job_con_score)

        # Ordenar por score descendente
        scored_jobs.sort(key=lambda j: j["moc_priority_score"], reverse=True)

        logger.info(
            "moc_priorizador_scored",
            total_jobs=len(scored_jobs),
            top_job_id=scored_jobs[0].get("id") if scored_jobs else None,
            top_score=scored_jobs[0].get("moc_priority_score") if scored_jobs else None,
        )

        return scored_jobs

    def _calcular_score(
        self,
        job: dict[str, Any],
        now: datetime,
        presupuesto_ratio: float,
    ) -> float:
        """Calcula el score de prioridad para un job individual."""

        # Factor 1: Urgencia temporal
        urgency_score = self._score_urgencia(job, now)

        # Factor 2: Impacto del tipo de tarea
        impact_score = self._score_impacto(job)

        # Factor 3: Presupuesto disponible
        # Si el presupuesto está bajo, penalizamos tareas costosas
        budget_score = self._score_presupuesto(job, presupuesto_ratio)

        # Factor 4: Historial de éxito
        history_score = self._score_historial(job)

        # Score final ponderado (0-100)
        final_score = (
            urgency_score * WEIGHT_URGENCY
            + impact_score * WEIGHT_IMPACT
            + budget_score * WEIGHT_BUDGET
            + history_score * WEIGHT_HISTORY
        ) * 10  # Escalar a 0-100

        return final_score

    def _score_urgencia(self, job: dict[str, Any], now: datetime) -> float:
        """
        Score de urgencia basado en cuánto tiempo lleva el job esperando.
        Retorna 0-10.
        """
        run_at_str = job.get("run_at")
        if not run_at_str:
            return 5.0  # Default medio

        try:
            run_at = datetime.fromisoformat(run_at_str.replace("Z", "+00:00"))
            # Tiempo de espera en minutos
            wait_minutes = (now - run_at).total_seconds() / 60

            if wait_minutes <= 0:
                return 3.0  # No está vencido aún
            elif wait_minutes < 5:
                return 5.0
            elif wait_minutes < 15:
                return 7.0
            elif wait_minutes < 60:
                return 8.5
            else:
                return 10.0  # Muy retrasado — máxima urgencia
        except (ValueError, TypeError):
            return 5.0

    def _score_impacto(self, job: dict[str, Any]) -> float:
        """
        Score de impacto basado en el tipo de tarea.
        Retorna 0-10.
        """
        # Intentar detectar el tipo de tarea desde el título o metadata
        title = (job.get("title") or "").lower()
        task_type = job.get("task_type") or job.get("type") or ""

        # Buscar coincidencias en el mapa de impacto
        for key, impact in TASK_IMPACT_MAP.items():
            if key in title or key in task_type.lower():
                return impact

        return TASK_IMPACT_MAP["default"]

    def _score_presupuesto(self, job: dict[str, Any], presupuesto_ratio: float) -> float:
        """
        Score de presupuesto. Tareas costosas se penalizan cuando el
        presupuesto está bajo.
        Retorna 0-10.
        """
        costo_estimado = job.get("estimated_cost_usd", 0.0) or 0.0

        if presupuesto_ratio >= 0.5:
            # Presupuesto abundante — no penalizar
            return 8.0
        elif presupuesto_ratio >= 0.2:
            # Presupuesto moderado — penalizar tareas costosas
            if costo_estimado > 0.10:
                return 4.0
            return 7.0
        else:
            # Presupuesto crítico — solo tareas baratas o críticas
            if costo_estimado > 0.05:
                return 2.0
            return 6.0

    def _score_historial(self, job: dict[str, Any]) -> float:
        """
        Score basado en el historial de ejecuciones del job.
        Jobs con alta tasa de éxito tienen prioridad sobre los que fallan.
        Retorna 0-10.
        """
        success_rate = job.get("success_rate")
        if success_rate is None:
            return 7.0  # Sin historial — asumir bueno

        if success_rate >= 0.9:
            return 9.0
        elif success_rate >= 0.7:
            return 7.0
        elif success_rate >= 0.5:
            return 5.0
        else:
            return 3.0  # Alta tasa de fallo — baja prioridad
