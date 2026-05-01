"""
El Monstruo — El Guardián de los Objetivos (Sprint 61)
=======================================================
Meta-vigilancia perpetua que garantiza que los 13 objetivos se cumplan siempre.

El Guardián es el Objetivo #14 — observa a todos los demás objetivos
y dispara alertas cuando detecta desviaciones o riesgos de incumplimiento.

Ciclo de vigilancia:
1. Evalúa el estado de cada objetivo cada N horas
2. Detecta tendencias de degradación antes de que se conviertan en fallos
3. Emite alertas con severidad y recomendaciones accionables
4. Registra el historial de salud para análisis de tendencias

Objetivo #14: El Guardián de los Objetivos
Sprint 61 — 2026-05-01

Soberanía:
- Supabase → in-memory fallback si no hay SUPABASE_URL
- Sabios LLM → evaluación heurística si no hay API key
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import structlog

logger = structlog.get_logger("monstruo.guardian")


# ── Excepciones con identidad ──────────────────────────────────────────────

class GuardianObjetivoNoRegistrado(KeyError):
    """El objetivo solicitado no está registrado en el Guardián.

    Causa: objetivo_id inválido o no registrado.
    Sugerencia: Verificar el ID con list_objetivos().
    """


class GuardianEvaluacionFallida(RuntimeError):
    """La evaluación del objetivo falló.

    Causa: Métricas no disponibles o LLM no responde.
    Sugerencia: Verificar que los módulos del objetivo están activos.
    """


# ── Enums ──────────────────────────────────────────────────────────────────

class AlertSeverity(str, Enum):
    """Severidad de alertas del Guardián."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ObjetivoStatus(str, Enum):
    """Estado de salud de un objetivo."""
    HEALTHY = "healthy"       # Cumpliendo
    AT_RISK = "at_risk"       # En riesgo
    DEGRADED = "degraded"     # Degradado
    FAILING = "failing"       # Fallando


# ── Dataclasses ────────────────────────────────────────────────────────────

@dataclass
class ObjetivoHealth:
    """Estado de salud de un objetivo.

    Args:
        objetivo_id: ID del objetivo (1-14).
        nombre: Nombre del objetivo.
        status: Estado actual (ObjetivoStatus).
        score: Score de cumplimiento (0-100).
        metrics: Métricas que sustentan el score.
        trend: Tendencia ("improving", "stable", "degrading").
        last_evaluated: ISO 8601 UTC de la última evaluación.
    """
    objetivo_id: int
    nombre: str
    status: ObjetivoStatus
    score: float
    metrics: dict
    trend: str = "stable"
    last_evaluated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "objetivo_id": self.objetivo_id,
            "nombre": self.nombre,
            "status": self.status.value,
            "score": self.score,
            "metrics": self.metrics,
            "trend": self.trend,
            "last_evaluated": self.last_evaluated,
        }


@dataclass
class GuardianAlert:
    """Alerta emitida por el Guardián.

    Args:
        id: Identificador único de la alerta.
        objetivo_id: ID del objetivo afectado.
        severity: Severidad de la alerta.
        message: Descripción del problema detectado.
        recommendation: Acción recomendada para resolver.
        evidence: Evidencia que soporta la alerta.
    """
    id: str
    objetivo_id: int
    severity: AlertSeverity
    message: str
    recommendation: str
    evidence: dict
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "objetivo_id": self.objetivo_id,
            "severity": self.severity.value,
            "message": self.message,
            "recommendation": self.recommendation,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
            "resolved": self.resolved,
        }


# ── El Guardián ────────────────────────────────────────────────────────────

@dataclass
class GuardianDeObjetivos:
    """El Guardián de los Objetivos — meta-vigilancia perpetua.

    Observa los 14 objetivos del Monstruo y garantiza que se cumplan siempre.
    Es el Objetivo #14 — el único objetivo que observa a todos los demás.

    Args:
        _supabase: Cliente Supabase (opcional — fallback in-memory).
        _sabios: Motor LLM para evaluación (opcional).
        _notifier: Sistema de notificaciones (opcional).

    Soberanía:
        Sin Supabase: alertas en memoria (se pierden al reiniciar).
        Sin Sabios: evaluación heurística basada en métricas.
    """
    _supabase: Optional[object] = field(default=None, repr=False)
    _sabios: Optional[object] = field(default=None, repr=False)
    _notifier: Optional[object] = field(default=None, repr=False)
    _objetivos: dict[int, dict] = field(default_factory=dict)
    _health_history: dict[int, list[ObjetivoHealth]] = field(default_factory=dict)
    _active_alerts: list[GuardianAlert] = field(default_factory=list)
    _evaluations_count: int = 0

    def __post_init__(self):
        """Registrar los 14 objetivos al inicializar."""
        self._register_14_objetivos()

    def _register_14_objetivos(self) -> None:
        """Registrar los 14 Objetivos Maestros del Monstruo."""
        objetivos = [
            (1, "Crear Empresas Digitales Completas", ["pipeline_completions", "empresas_creadas"]),
            (2, "Nivel Apple/Tesla", ["design_audit_scores", "visual_quality_scores"]),
            (3, "Máximo Poder, Mínima Complejidad", ["onboarding_time_minutes", "user_satisfaction"]),
            (4, "Nunca se Equivoca Dos Veces", ["error_recurrence_rate", "learning_patterns_count"]),
            (5, "Gasolina Magna vs Premium", ["cost_per_project_usd", "roi_ratio"]),
            (6, "Vanguardia Perpetua", ["tech_radar_updates", "vanguard_scan_frequency"]),
            (7, "No Inventar la Rueda", ["research_queries", "reuse_rate"]),
            (8, "Inteligencia Emergente Colectiva", ["emergent_behaviors_detected", "debates_count"]),
            (9, "Transversalidad Total", ["capas_activas", "proyectos_con_todas_capas"]),
            (10, "Simulador Predictivo", ["predictions_accuracy", "causal_events_count"]),
            (11, "Multiplicación de Embriones", ["embriones_activos", "embriones_ciclos_hoy"]),
            (12, "Ecosistema de Monstruos", ["monstruos_en_red", "colaboraciones_activas"]),
            (13, "Del Mundo", ["idiomas_soportados", "paises_activos"]),
            (14, "El Guardián", ["objetivos_healthy", "alertas_resueltas_hoy"]),
        ]

        for obj_id, nombre, metrics_keys in objetivos:
            self._objetivos[obj_id] = {
                "id": obj_id,
                "nombre": nombre,
                "metrics_keys": metrics_keys,
                "evaluator": None,  # Se inyecta en runtime
            }
            self._health_history[obj_id] = []

        logger.info("guardian_14_objetivos_registrados", count=len(self._objetivos))

    # ── Evaluación ─────────────────────────────────────────────────────────

    async def evaluate_objetivo(self, objetivo_id: int,
                                 metrics: dict) -> ObjetivoHealth:
        """Evaluar el estado de salud de un objetivo.

        Args:
            objetivo_id: ID del objetivo a evaluar (1-14).
            metrics: Métricas actuales del objetivo.

        Returns:
            ObjetivoHealth con status, score y trend.

        Raises:
            GuardianObjetivoNoRegistrado: Si el objetivo_id no existe.
        """
        if objetivo_id not in self._objetivos:
            raise GuardianObjetivoNoRegistrado(
                f"Objetivo #{objetivo_id} no registrado. "
                "Verificar el ID con list_objetivos()."
            )

        self._evaluations_count += 1
        objetivo = self._objetivos[objetivo_id]

        # Calcular score
        score = self._calculate_score(objetivo_id, metrics)

        # Determinar status
        if score >= 80:
            status = ObjetivoStatus.HEALTHY
        elif score >= 60:
            status = ObjetivoStatus.AT_RISK
        elif score >= 40:
            status = ObjetivoStatus.DEGRADED
        else:
            status = ObjetivoStatus.FAILING

        # Calcular tendencia
        trend = self._calculate_trend(objetivo_id, score)

        health = ObjetivoHealth(
            objetivo_id=objetivo_id,
            nombre=objetivo["nombre"],
            status=status,
            score=score,
            metrics=metrics,
            trend=trend,
        )

        # Guardar en historial
        self._health_history[objetivo_id].append(health)
        if len(self._health_history[objetivo_id]) > 30:
            self._health_history[objetivo_id] = self._health_history[objetivo_id][-30:]

        # Emitir alertas si necesario
        await self._check_and_alert(health)

        # Persistir en Supabase
        if self._supabase:
            try:
                self._supabase.table("guardian_health").insert(
                    health.to_dict()
                ).execute()
            except Exception as e:
                logger.warning("guardian_health_persist_failed", error=str(e))

        logger.info("objetivo_evaluado", id=objetivo_id, nombre=objetivo["nombre"],
                    status=status.value, score=score, trend=trend)
        return health

    async def evaluate_all(self, metrics_by_objetivo: dict[int, dict]) -> dict[int, ObjetivoHealth]:
        """Evaluar todos los objetivos en un ciclo.

        Args:
            metrics_by_objetivo: Dict {objetivo_id: metrics_dict}.

        Returns:
            Dict {objetivo_id: ObjetivoHealth}.
        """
        results = {}
        for obj_id, metrics in metrics_by_objetivo.items():
            try:
                health = await self.evaluate_objetivo(obj_id, metrics)
                results[obj_id] = health
            except Exception as e:
                logger.error("objetivo_evaluation_failed", id=obj_id, error=str(e))

        return results

    def _calculate_score(self, objetivo_id: int, metrics: dict) -> float:
        """Calcular score de cumplimiento basado en métricas.

        Args:
            objetivo_id: ID del objetivo.
            metrics: Métricas actuales.

        Returns:
            Score 0-100.
        """
        objetivo = self._objetivos[objetivo_id]
        keys = objetivo["metrics_keys"]

        if not metrics:
            return 50.0  # Score neutral si no hay métricas

        # Calcular score basado en presencia y valores de métricas clave
        scores = []
        for key in keys:
            value = metrics.get(key)
            if value is None:
                scores.append(30.0)  # Penalización por métrica ausente
            elif isinstance(value, (int, float)):
                # Normalizar: valores > 0 son positivos
                scores.append(min(100.0, max(0.0, float(value) * 10)) if value <= 10
                               else min(100.0, 50.0 + float(value)))
            elif isinstance(value, bool):
                scores.append(100.0 if value else 0.0)
            else:
                scores.append(70.0)  # Score neutral para strings

        return round(sum(scores) / max(len(scores), 1), 1)

    def _calculate_trend(self, objetivo_id: int, current_score: float) -> str:
        """Calcular tendencia basada en historial.

        Args:
            objetivo_id: ID del objetivo.
            current_score: Score actual.

        Returns:
            "improving", "stable" o "degrading".
        """
        history = self._health_history.get(objetivo_id, [])
        if len(history) < 3:
            return "stable"

        recent_scores = [h.score for h in history[-3:]]
        avg_recent = sum(recent_scores) / len(recent_scores)

        if current_score > avg_recent + 5:
            return "improving"
        elif current_score < avg_recent - 5:
            return "degrading"
        else:
            return "stable"

    # ── Alertas ────────────────────────────────────────────────────────────

    async def _check_and_alert(self, health: ObjetivoHealth) -> None:
        """Verificar si se debe emitir alerta y emitirla.

        Args:
            health: Estado de salud del objetivo.
        """
        if health.status == ObjetivoStatus.HEALTHY:
            return

        severity = {
            ObjetivoStatus.AT_RISK: AlertSeverity.WARNING,
            ObjetivoStatus.DEGRADED: AlertSeverity.CRITICAL,
            ObjetivoStatus.FAILING: AlertSeverity.EMERGENCY,
        }.get(health.status, AlertSeverity.INFO)

        # No duplicar alertas recientes del mismo objetivo
        recent_alerts = [
            a for a in self._active_alerts
            if a.objetivo_id == health.objetivo_id and not a.resolved
        ]
        if recent_alerts and recent_alerts[-1].severity == severity:
            return

        recommendation = self._generate_recommendation(health)

        alert = GuardianAlert(
            id=str(uuid.uuid4())[:8],
            objetivo_id=health.objetivo_id,
            severity=severity,
            message=(
                f"Objetivo #{health.objetivo_id} ({health.nombre}) está en estado "
                f"'{health.status.value}' con score {health.score}/100. "
                f"Tendencia: {health.trend}."
            ),
            recommendation=recommendation,
            evidence=health.metrics,
        )
        self._active_alerts.append(alert)

        # Notificar
        if self._notifier:
            try:
                await self._notifier.send(
                    level=severity.value,
                    message=alert.message,
                    context={"objetivo_id": health.objetivo_id, "score": health.score},
                )
            except Exception as e:
                logger.warning("guardian_notify_failed", error=str(e))

        # Persistir en Supabase
        if self._supabase:
            try:
                self._supabase.table("guardian_alerts").insert(
                    alert.to_dict()
                ).execute()
            except Exception as e:
                logger.warning("guardian_alert_persist_failed", error=str(e))

        logger.warning("guardian_alerta_emitida", id=alert.id,
                       objetivo_id=health.objetivo_id, severity=severity.value,
                       score=health.score)

    @staticmethod
    def _generate_recommendation(health: ObjetivoHealth) -> str:
        """Generar recomendación accionable para un objetivo en riesgo.

        Args:
            health: Estado de salud del objetivo.

        Returns:
            Recomendación accionable en español.
        """
        recommendations = {
            1: "Verificar que el pipeline de creación de empresas está activo y completando ciclos.",
            2: "Ejecutar auditoría de diseño en los últimos proyectos generados.",
            3: "Revisar el flujo de onboarding — medir tiempo hasta primer valor.",
            4: "Verificar que el AdaptiveLearningEngine está registrando patrones de error.",
            5: "Analizar costos por proyecto — identificar operaciones costosas.",
            6: "Activar el TechRadar scan — verificar que VanguardScan está corriendo.",
            7: "Verificar que el EmbrionInvestigador está siendo consultado antes de implementar.",
            8: "Revisar el EmergentBehaviorTracker — verificar comunicación inter-embrión.",
            9: "Verificar que las 7 capas transversales están activas en proyectos nuevos.",
            10: "Verificar que CausalSeeder está corriendo y CausalKB tiene eventos recientes.",
            11: "Verificar que los 7 Embriones están activos y completando ciclos.",
            12: "Iniciar proceso de conexión con otros Monstruos en la red.",
            13: "Verificar que i18n Engine soporta los idiomas objetivo.",
            14: "El Guardián mismo está en riesgo — revisar ciclos de evaluación.",
        }
        return recommendations.get(
            health.objetivo_id,
            f"Revisar métricas del Objetivo #{health.objetivo_id} y activar módulos correspondientes."
        )

    # ── Resolución de Alertas ──────────────────────────────────────────────

    async def resolve_alert(self, alert_id: str) -> bool:
        """Marcar una alerta como resuelta.

        Args:
            alert_id: ID de la alerta a resolver.

        Returns:
            True si se resolvió, False si no se encontró.
        """
        for alert in self._active_alerts:
            if alert.id == alert_id:
                alert.resolved = True
                logger.info("guardian_alerta_resuelta", id=alert_id,
                            objetivo_id=alert.objetivo_id)
                return True
        return False

    # ── Estado para Command Center ─────────────────────────────────────────

    def get_dashboard(self) -> dict:
        """Obtener dashboard completo del Guardián.

        Returns:
            Dict con estado de todos los objetivos y alertas activas.
        """
        health_summary = {}
        for obj_id, history in self._health_history.items():
            if history:
                latest = history[-1]
                health_summary[obj_id] = {
                    "nombre": latest.nombre,
                    "status": latest.status.value,
                    "score": latest.score,
                    "trend": latest.trend,
                }
            else:
                health_summary[obj_id] = {
                    "nombre": self._objetivos[obj_id]["nombre"],
                    "status": "not_evaluated",
                    "score": None,
                    "trend": None,
                }

        active_alerts = [a for a in self._active_alerts if not a.resolved]

        return {
            "objetivos_registrados": len(self._objetivos),
            "evaluaciones_realizadas": self._evaluations_count,
            "alertas_activas": len(active_alerts),
            "alertas_emergencia": len([a for a in active_alerts if a.severity == AlertSeverity.EMERGENCY]),
            "objetivos_healthy": len([h for h in health_summary.values() if h.get("status") == "healthy"]),
            "objetivos_en_riesgo": len([h for h in health_summary.values() if h.get("status") in ["at_risk", "degraded", "failing"]]),
            "health_summary": health_summary,
            "active_alerts": [a.to_dict() for a in active_alerts[-10:]],
        }

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return self.get_dashboard()

    def list_objetivos(self) -> list[dict]:
        """Listar todos los objetivos registrados."""
        return [
            {"id": obj["id"], "nombre": obj["nombre"]}
            for obj in self._objetivos.values()
        ]


# ── Singleton ──────────────────────────────────────────────────────────────

_guardian_instance: Optional[GuardianDeObjetivos] = None


def get_guardian() -> Optional[GuardianDeObjetivos]:
    """Obtener instancia singleton del Guardián."""
    return _guardian_instance


def init_guardian(supabase=None, sabios=None, notifier=None) -> GuardianDeObjetivos:
    """Inicializar El Guardián de los Objetivos.

    Args:
        supabase: Cliente Supabase (opcional).
        sabios: Motor LLM para evaluación (opcional).
        notifier: Sistema de notificaciones (opcional).

    Returns:
        Instancia singleton de GuardianDeObjetivos.
    """
    global _guardian_instance
    _guardian_instance = GuardianDeObjetivos(
        _supabase=supabase,
        _sabios=sabios,
        _notifier=notifier,
    )
    logger.info("guardian_inicializado",
                con_supabase=supabase is not None,
                con_sabios=sabios is not None,
                objetivos=14)
    return _guardian_instance
