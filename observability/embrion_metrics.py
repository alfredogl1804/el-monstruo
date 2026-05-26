"""
El Monstruo — Embrión Metrics Collector (Sprint 56.4)
====================================================
Recolecta y agrega métricas de todos los Embriones.
Expone vía API para el Command Center dashboard.

Métricas por Embrión:
  - tasks_completed (counter)
  - tasks_failed (counter)
  - total_cost_usd (gauge)
  - avg_latency_ms (gauge)
  - quality_score (gauge, 0-1)
  - success_rate (gauge)
  - last_action_at (timestamp)

Métricas globales:
  - total_embriones_active
  - total_daily_cost_usd
  - predictions_validated_today
  - causal_events_seeded_today
  - scheduler_tasks_active

T3: get_global_metrics() retorna dashboard completo
T5: Command Center puede consumir /v1/embrion/metrics para dashboard
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("observability.embrion_metrics")


@dataclass
class EmbrionMetrics:
    """Métricas de un Embrión individual."""

    embrion_id: str = ""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_cost_usd: float = 0.0
    latencies_ms: list[float] = field(default_factory=list)
    quality_scores: list[float] = field(default_factory=list)
    last_action_at: Optional[str] = None
    started_at: Optional[str] = None

    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        # Usar últimas 100 mediciones para evitar memoria infinita
        recent = self.latencies_ms[-100:]
        return sum(recent) / len(recent)

    @property
    def avg_quality_score(self) -> float:
        if not self.quality_scores:
            return 0.0
        recent = self.quality_scores[-50:]
        return sum(recent) / len(recent)

    @property
    def success_rate(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 1.0
        return self.tasks_completed / total

    def to_dict(self) -> dict[str, Any]:
        return {
            "embrion_id": self.embrion_id,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "avg_quality_score": round(self.avg_quality_score, 3),
            "success_rate": round(self.success_rate, 3),
            "last_action_at": self.last_action_at,
            "started_at": self.started_at,
        }


class EmbrionMetricsCollector:
    """
    Recolector central de métricas de Embriones.
    In-memory con reset diario automático para métricas de hoy.
    """

    def __init__(self):
        self._metrics: dict[str, EmbrionMetrics] = {}
        self._global_events_today: int = 0
        self._global_predictions_today: int = 0
        self._day_started: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _get_or_create(self, embrion_id: str) -> EmbrionMetrics:
        """Obtener o crear métricas para un Embrión."""
        if embrion_id not in self._metrics:
            self._metrics[embrion_id] = EmbrionMetrics(
                embrion_id=embrion_id,
                started_at=datetime.now(timezone.utc).isoformat(),
            )
        return self._metrics[embrion_id]

    def record_task_success(
        self,
        embrion_id: str,
        latency_ms: float,
        cost_usd: float = 0.0,
        quality_score: Optional[float] = None,
    ) -> None:
        """Registrar tarea completada exitosamente."""
        m = self._get_or_create(embrion_id)
        m.tasks_completed += 1
        if latency_ms > 0:
            m.latencies_ms.append(latency_ms)
        m.total_cost_usd += cost_usd
        m.last_action_at = datetime.now(timezone.utc).isoformat()
        if quality_score is not None:
            m.quality_scores.append(quality_score)
        logger.debug(
            "embrion_task_success",
            embrion_id=embrion_id,
            latency_ms=round(latency_ms, 1),
            cost_usd=round(cost_usd, 4),
        )

    def record_task_failure(
        self,
        embrion_id: str,
        latency_ms: float = 0.0,
        error: Optional[str] = None,
    ) -> None:
        """Registrar tarea fallida."""
        m = self._get_or_create(embrion_id)
        m.tasks_failed += 1
        if latency_ms > 0:
            m.latencies_ms.append(latency_ms)
        m.last_action_at = datetime.now(timezone.utc).isoformat()
        logger.warning(
            "embrion_task_failure",
            embrion_id=embrion_id,
            error=error or "unknown",
        )

    def record_quality_score(self, embrion_id: str, score: float) -> None:
        """Registrar score de calidad (del judge)."""
        m = self._get_or_create(embrion_id)
        m.quality_scores.append(max(0.0, min(1.0, score)))

    def record_cost(self, embrion_id: str, cost_usd: float) -> None:
        """Registrar costo adicional."""
        m = self._get_or_create(embrion_id)
        m.total_cost_usd += cost_usd

    def record_causal_event_seeded(self, count: int = 1) -> None:
        """Registrar eventos causales sembrados hoy."""
        self._global_events_today += count

    def record_prediction_validated(self, count: int = 1) -> None:
        """Registrar predicciones validadas hoy."""
        self._global_predictions_today += count

    def get_embrion_metrics(self, embrion_id: str) -> dict[str, Any]:
        """
        Obtener métricas de un Embrión específico.
        T3: Accesible desde /v1/embrion/metrics/{embrion_id}
        """
        m = self._metrics.get(embrion_id)
        if not m:
            return {"embrion_id": embrion_id, "status": "not_found"}
        return m.to_dict()

    def get_global_metrics(self) -> dict[str, Any]:
        """
        Obtener métricas globales del sistema.
        T3: get_global_metrics() retorna dashboard completo.
        T5: Consumible desde /v1/embrion/metrics para Command Center.
        """
        total_cost = sum(m.total_cost_usd for m in self._metrics.values())
        total_completed = sum(m.tasks_completed for m in self._metrics.values())
        total_failed = sum(m.tasks_failed for m in self._metrics.values())
        total_tasks = total_completed + total_failed
        active = sum(1 for m in self._metrics.values() if m.last_action_at is not None)

        # Embrión más activo
        top_embrion = None
        if self._metrics:
            top_embrion = max(
                self._metrics.values(),
                key=lambda m: m.tasks_completed,
            ).embrion_id

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "day": self._day_started,
            "total_embriones": len(self._metrics),
            "active_embriones": active,
            "total_tasks_executed": total_tasks,
            "total_tasks_completed": total_completed,
            "total_tasks_failed": total_failed,
            "global_success_rate": round(total_completed / total_tasks, 3) if total_tasks > 0 else 1.0,
            "total_cost_usd": round(total_cost, 4),
            "causal_events_seeded_today": self._global_events_today,
            "predictions_validated_today": self._global_predictions_today,
            "top_embrion": top_embrion,
            "embriones": [m.to_dict() for m in self._metrics.values()],
        }

    def reset_daily_counters(self) -> None:
        """Resetear contadores diarios (llamar a medianoche UTC)."""
        self._global_events_today = 0
        self._global_predictions_today = 0
        self._day_started = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        logger.info("embrion_metrics_daily_reset", day=self._day_started)


# ── Singleton ──────────────────────────────────────────────────────

_collector_instance: Optional[EmbrionMetricsCollector] = None


def get_embrion_metrics_collector() -> Optional[EmbrionMetricsCollector]:
    """Obtener el singleton del EmbrionMetricsCollector."""
    return _collector_instance


def init_embrion_metrics_collector() -> EmbrionMetricsCollector:
    """
    Inicializar el EmbrionMetricsCollector singleton.
    Llamar desde el lifespan de main.py.
    """
    global _collector_instance
    _collector_instance = EmbrionMetricsCollector()
    logger.info("embrion_metrics_collector_initialized")
    return _collector_instance
