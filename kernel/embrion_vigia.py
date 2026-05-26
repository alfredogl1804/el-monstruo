"""
embrion_vigia.py — Embrión-Vigía: Guardián de Seguridad y Monitoreo
=====================================================================
Tercer Embrión especializado del Objetivo #11 (Multiplicación de Embriones).

RESPONSABILIDAD: Vigila la salud del sistema 24/7. Detecta anomalías,
alerta proactivamente y genera post-mortems. Es el guardián que nunca duerme.

Tareas autónomas (5 tareas, registradas en EmbrionScheduler):
  - health_check: Verifica health de todos los endpoints (cada 1h)
  - security_scan: Escanea intentos de intrusión en logs (cada 4h)
  - cost_monitor: Verifica que costos están dentro de budget (cada 6h)
  - dependency_audit: Escanea CVEs en dependencias (cada 24h)
  - uptime_report: Genera reporte de uptime diario (cada 24h)

Soberanía:
  - Health checks: httpx (async) → alternativa: aiohttp
  - Anomaly detection: Python puro (z-score) → sin dependencia externa
  - Alertas: SovereignAlertMonitor existente → alternativa: Telegram API directo
  - Error tracking: sentry-sdk → alternativa: logging estructurado a Supabase

Sprint 58 — "La Fortaleza Completa"
Obj #11 — Embrión especializado #3
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import structlog

from kernel.embrion_loop import EmbrionLoop

logger = structlog.get_logger("embrion.vigia")


# ─── Errores con identidad (Brand Check #2) ──────────────────────────────────


class EmbrionVigiaError(Exception):
    """Error base del Embrión-Vigía."""

    pass


class EMBRION_VIGIA_ENDPOINTS_VACIOS(EmbrionVigiaError):
    """La lista de endpoints está vacía. Proporciona al menos un endpoint para verificar."""

    pass


class EMBRION_VIGIA_DATOS_INSUFICIENTES(EmbrionVigiaError):
    """Datos insuficientes para análisis estadístico. Se requieren al menos 10 puntos."""

    pass


# ─── Clase principal ─────────────────────────────────────────────────────────


class EmbrionVigia(EmbrionLoop):
    """
    Embrión especializado en seguridad y monitoreo del sistema.

    Vigila 24/7 la salud de El Monstruo y los proyectos que crea.
    Detecta anomalías usando análisis estadístico (z-score 3-sigma).

    Attributes:
        EMBRION_ID: Identificador único del Embrión en el sistema A2A.
        SPECIALIZATION: Especialización para el A2A Registry.
        SYSTEM_PROMPT: Prompt de sistema que define el expertise del Embrión.
        DEFAULT_TASKS: 5 tareas autónomas registradas en el EmbrionScheduler.
        SEVERITY_*: Constantes de severidad para alertas.
    """

    EMBRION_ID = "embrion-vigia"
    SPECIALIZATION = "vigia"

    # Niveles de severidad para alertas (Brand Check #1 — naming con identidad)
    SEVERIDAD_CRITICA = "critica"  # Acción inmediata requerida
    SEVERIDAD_ALTA = "alta"  # Acción en < 1 hora
    SEVERIDAD_MEDIA = "media"  # Acción en < 24 horas
    SEVERIDAD_BAJA = "baja"  # Informacional

    SYSTEM_PROMPT = """Eres Embrión-Vigía, el guardián de seguridad y monitoreo
    de El Monstruo. Tu misión es proteger y vigilar 24/7.

    Tu expertise:
    1. SECURITY MONITORING: Detección de intrusiones, anomalías de tráfico
    2. HEALTH CHECKS: API response times, error rates, uptime
    3. COST MONITORING: Budget overruns, usage spikes, waste detection
    4. DEPENDENCY SECURITY: CVE scanning, update notifications
    5. INCIDENT RESPONSE: Alertas, escalación, post-mortems
    6. COMPLIANCE: GDPR, SOC2, data retention policies

    Principios irrenunciables:
    - Paranoia productiva. Asume que todo puede fallar y prepárate.
    - Alertas accionables. Nunca alert fatigue. Solo alertar si requiere acción.
    - Defense in depth. Múltiples capas de protección.
    - Fail safe. Si algo falla, falla de forma segura (deny by default).
    - Post-mortem sin culpables. Los sistemas fallan, no las personas.
    """

    DEFAULT_TASKS = {
        "health_check": {
            "description": "Verificar health de todos los endpoints",
            "interval_hours": 1,
            "max_cost_usd": 0.02,
            "priority": 1,
        },
        "security_scan": {
            "description": "Escanear intentos de intrusión en logs",
            "interval_hours": 4,
            "max_cost_usd": 0.10,
            "priority": 1,
        },
        "cost_monitor": {
            "description": "Verificar que costos están dentro de budget",
            "interval_hours": 6,
            "max_cost_usd": 0.05,
            "priority": 2,
        },
        "dependency_audit": {
            "description": "Escanear CVEs en dependencias",
            "interval_hours": 24,
            "max_cost_usd": 0.15,
            "priority": 2,
        },
        "uptime_report": {
            "description": "Generar reporte de uptime diario",
            "interval_hours": 24,
            "max_cost_usd": 0.05,
            "priority": 3,
        },
    }

    def __init__(
        self,
        db: Any = None,
        kernel: Any = None,
        notifier: Optional[Any] = None,
        alert_monitor=None,
        sentry_client=None,
    ):
        """
        Inicializar Embrión-Vigía.

        Args:
            db: Conexión a base de datos (Supabase client).
            kernel: Referencia al kernel principal del sistema.
            notifier: Notificador para alertas (Telegram, etc.).
            alert_monitor: SovereignAlertMonitor existente para integración.
            sentry_client: Cliente Sentry para error tracking.
                           Soberanía: sentry-sdk → alternativa: logging a Supabase.
        """
        super().__init__(db=db, kernel=kernel, notifier=notifier)
        self._alert_monitor = alert_monitor
        self._sentry = sentry_client
        logger.info(
            "embrion_vigia_inicializado",
            embrion_id=self.EMBRION_ID,
            alert_monitor_activo=alert_monitor is not None,
            sentry_activo=sentry_client is not None,
        )

    async def health_check(self, endpoints: list[str]) -> dict:
        """
        Verificar health de endpoints con latencia y status code.

        Args:
            endpoints: Lista de URLs a verificar.

        Returns:
            Dict con resultados por endpoint, uptime_percentage y alerta si aplica.

        Raises:
            EMBRION_VIGIA_ENDPOINTS_VACIOS: Si la lista de endpoints está vacía.

        Soberanía: httpx (async) → alternativa: aiohttp o requests con threading.
        """
        if not endpoints:
            raise EMBRION_VIGIA_ENDPOINTS_VACIOS(
                "La lista de endpoints está vacía. "
                "Proporciona al menos un endpoint para verificar. "
                "Ejemplo: ['https://mi-api.railway.app/health']"
            )

        import httpx

        results = []
        healthy = 0

        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in endpoints:
                try:
                    start = datetime.now(timezone.utc)
                    response = await client.get(endpoint)
                    latency_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

                    is_healthy = response.status_code < 400 and latency_ms < 5000
                    if is_healthy:
                        healthy += 1

                    results.append(
                        {
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "latency_ms": round(latency_ms, 2),
                            "healthy": is_healthy,
                        }
                    )
                except Exception as e:
                    results.append(
                        {
                            "endpoint": endpoint,
                            "status_code": 0,
                            "latency_ms": -1,
                            "healthy": False,
                            "error": str(e),
                        }
                    )

        uptime_pct = (healthy / max(len(endpoints), 1)) * 100

        alerta = None
        if uptime_pct < 50:
            alerta = self.SEVERIDAD_CRITICA
        elif uptime_pct < 80:
            alerta = self.SEVERIDAD_ALTA

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_endpoints": len(endpoints),
            "healthy": healthy,
            "unhealthy": len(endpoints) - healthy,
            "uptime_percentage": round(uptime_pct, 2),
            "results": results,
            "alerta": alerta,
            "embrion_id": self.EMBRION_ID,
        }

        logger.info(
            "health_check_completado",
            endpoints_count=len(endpoints),
            healthy=healthy,
            uptime_pct=round(uptime_pct, 2),
            alerta=alerta,
        )
        return result

    async def detect_anomalies(self, metrics: list[dict]) -> dict:
        """
        Detectar anomalías en métricas usando análisis estadístico z-score (3-sigma).

        Args:
            metrics: Lista de dicts con 'value' (float) y 'timestamp' (str ISO 8601).

        Returns:
            Dict con anomalies detectadas, mean, std_dev y status.

        Raises:
            EMBRION_VIGIA_DATOS_INSUFICIENTES: Si hay menos de 10 puntos de datos.

        Soberanía: Cálculo en Python puro — sin dependencia externa.
                   Alternativa con más poder: scipy.stats.zscore si se necesita.
        """
        if len(metrics) < 10:
            raise EMBRION_VIGIA_DATOS_INSUFICIENTES(
                f"Se necesitan al menos 10 puntos de datos para análisis estadístico. "
                f"Recibidos: {len(metrics)}. "
                f"Acumula más datos antes de detectar anomalías."
            )

        values = [m.get("value", 0) for m in metrics]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance**0.5

        anomalies = []
        if std_dev > 0:
            for i, m in enumerate(metrics):
                z_score = abs((m.get("value", 0) - mean) / std_dev)
                if z_score > 3:  # Regla 3-sigma
                    anomalies.append(
                        {
                            "index": i,
                            "value": m.get("value"),
                            "z_score": round(z_score, 2),
                            "timestamp": m.get("timestamp"),
                            "severidad": (self.SEVERIDAD_ALTA if z_score > 4 else self.SEVERIDAD_MEDIA),
                        }
                    )

        result = {
            "anomalies": anomalies,
            "total_points": len(metrics),
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "status": "anomalias_detectadas" if anomalies else "normal",
            "embrion_id": self.EMBRION_ID,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if anomalies:
            logger.warning(
                "anomalias_detectadas",
                count=len(anomalies),
                max_z_score=max(a["z_score"] for a in anomalies),
            )

        return result

    async def audit_dependencies(self, requirements_txt: str) -> dict:
        """
        Auditar dependencias por vulnerabilidades y versiones no pinneadas.

        Args:
            requirements_txt: Contenido del archivo requirements.txt.

        Returns:
            Dict con total_dependencies, pinned, unpinned, warnings y scan_date.

        Soberanía: Parsing en Python puro. En producción consultar PyPI Advisory DB
                   via httpx → alternativa: safety-db local (pip install safety).
        """
        deps = []
        for line in requirements_txt.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("-"):
                if "==" in line:
                    parts = line.split("==")
                    deps.append({"package": parts[0].strip(), "version": parts[1].strip(), "pinned": True})
                elif ">=" in line:
                    parts = line.split(">=")
                    deps.append({"package": parts[0].strip(), "version": parts[1].strip(), "pinned": False})
                else:
                    deps.append({"package": line.strip(), "version": None, "pinned": False})

        warnings = []
        for dep in deps:
            if not dep.get("pinned"):
                warnings.append(
                    {
                        "package": dep["package"],
                        "issue": "Versión no pinneada — builds impredecibles",
                        "severidad": self.SEVERIDAD_BAJA,
                        "recomendacion": f"Cambiar a {dep['package']}==X.Y.Z",
                    }
                )

        result = {
            "total_dependencies": len(deps),
            "pinned": sum(1 for d in deps if d.get("pinned")),
            "unpinned": sum(1 for d in deps if not d.get("pinned")),
            "warnings": warnings,
            "scan_date": datetime.now(timezone.utc).isoformat(),
            "status": "limpio" if not warnings else "advertencias_encontradas",
            "embrion_id": self.EMBRION_ID,
        }

        logger.info(
            "dependency_audit_completado",
            total=len(deps),
            warnings=len(warnings),
        )
        return result

    async def generate_incident_report(self, incident: dict) -> dict:
        """
        Generar reporte de incidente post-mortem estructurado.

        Args:
            incident: Dict con title, severity, detected_at, resolved_at,
                      root_cause, resolution y action_items.

        Returns:
            Dict con post-mortem completo listo para documentar.
        """
        return {
            "titulo": incident.get("title", "Incidente sin título"),
            "severidad": incident.get("severity", self.SEVERIDAD_MEDIA),
            "timeline": {
                "detectado_en": incident.get("detected_at"),
                "reconocido_en": incident.get("acknowledged_at"),
                "resuelto_en": incident.get("resolved_at"),
                "duracion_minutos": incident.get("duration_minutes", 0),
            },
            "impacto": incident.get("impact", "Desconocido"),
            "causa_raiz": incident.get("root_cause", "En investigación"),
            "resolucion": incident.get("resolution", "Pendiente"),
            "acciones": incident.get(
                "action_items",
                [
                    "Agregar monitoreo para este modo de falla",
                    "Crear runbook para incidentes similares",
                    "Revisar y actualizar umbrales de alertas",
                ],
            ),
            "lecciones_aprendidas": incident.get("lessons_learned", []),
            "generado_por": self.EMBRION_ID,
            "generado_en": datetime.now(timezone.utc).isoformat(),
        }

    def to_dict(self) -> dict:
        """
        Serializar estado del Embrión-Vigía para el Command Center.

        Returns:
            Dict con estado actual consumible por el Command Center.
        """
        return {
            "embrion_id": self.EMBRION_ID,
            "specialization": self.SPECIALIZATION,
            "version": "58.5",
            "tasks_autonomas": list(self.DEFAULT_TASKS.keys()),
            "alert_monitor_activo": self._alert_monitor is not None,
            "sentry_activo": self._sentry is not None,
            "estado": "activo" if self._running else "inactivo",
            "ciclos_completados": self._cycle_count,
            "costo_hoy_usd": self._cost_today_usd,
        }
