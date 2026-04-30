"""
El Monstruo — MOC Sintetizador (Sprint 36)
==========================================
Motor de Orquestación Central (MOC) — Sintetizador de Ciclos.

Consolida los resultados de múltiples ciclos de ejecución del
AutonomousRunner en insights accionables para Alfredo.

Responsabilidades:
  1. Leer job_executions de las últimas N horas
  2. Identificar patrones: qué funcionó, qué falló, qué tardó más
  3. Generar un resumen ejecutivo con el modelo de síntesis
  4. Guardar el insight en Supabase (tabla moc_insights)
  5. Notificar al usuario si hay algo urgente

Principio: El Sintetizador es la "conciencia" del MOC — convierte
datos de ejecución en conocimiento accionable.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.moc.sintetizador")

# Modelo de síntesis — usar el más económico que pueda razonar bien
SYNTHESIS_MODEL = "gemini-3.1-flash-lite"

# Ventana de análisis por defecto (horas)
DEFAULT_WINDOW_HOURS = 24


class Sintetizador:
    """
    Consolida resultados de ciclos de ejecución en insights accionables.

    Uso:
        sintetizador = Sintetizador(db=db_client, router=router)
        insight = await sintetizador.sintetizar(window_hours=24)
    """

    def __init__(self, db: Any, router: Any):
        self._db = db
        self._router = router

    async def sintetizar(
        self,
        window_hours: int = DEFAULT_WINDOW_HOURS,
        user_id: str = "anonymous",
    ) -> dict[str, Any]:
        """
        Genera un insight consolidado de los últimos `window_hours` de ejecución.

        Returns:
            Dict con keys: summary, patterns, alerts, recommendations, metadata
        """
        start_time = time.monotonic()
        since = datetime.now(timezone.utc) - timedelta(hours=window_hours)

        logger.info("moc_sintetizador_start", window_hours=window_hours)

        # 1. Leer ejecuciones recientes
        executions = await self._get_recent_executions(since)

        if not executions:
            logger.info("moc_sintetizador_no_executions")
            return {
                "summary": "No hay ejecuciones en el período analizado.",
                "patterns": [],
                "alerts": [],
                "recommendations": [],
                "metadata": {
                    "window_hours": window_hours,
                    "executions_analyzed": 0,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
            }

        # 2. Calcular métricas básicas
        metrics = self._calcular_metricas(executions)

        # 3. Generar síntesis con LLM
        synthesis = await self._generar_sintesis_llm(executions, metrics)

        # 4. Guardar insight en Supabase
        insight_id = await self._guardar_insight(synthesis, metrics, window_hours, user_id)

        elapsed_ms = (time.monotonic() - start_time) * 1000
        logger.info(
            "moc_sintetizador_completed",
            insight_id=insight_id,
            executions_analyzed=len(executions),
            latency_ms=elapsed_ms,
        )

        return {
            **synthesis,
            "metadata": {
                "insight_id": insight_id,
                "window_hours": window_hours,
                "executions_analyzed": len(executions),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "latency_ms": round(elapsed_ms, 0),
                **metrics,
            },
        }

    async def _get_recent_executions(self, since: datetime) -> list[dict[str, Any]]:
        """Lee las ejecuciones recientes de job_executions."""
        try:
            executions = await self._db.select(
                "job_executions",
                filters={"status": "completed"},
                order_by="started_at",
                order_desc=True,
                limit=50,
            )
            # Filtrar por ventana de tiempo
            result = []
            for ex in executions:
                started_at_str = ex.get("started_at", "")
                if started_at_str:
                    try:
                        started_at = datetime.fromisoformat(started_at_str.replace("Z", "+00:00"))
                        if started_at >= since:
                            result.append(ex)
                    except (ValueError, TypeError):
                        pass
            return result
        except Exception as e:
            logger.warning("moc_get_executions_failed", error=str(e))
            return []

    def _calcular_metricas(self, executions: list[dict[str, Any]]) -> dict[str, Any]:
        """Calcula métricas básicas de las ejecuciones."""
        if not executions:
            return {}

        total = len(executions)
        completadas = sum(1 for e in executions if e.get("status") == "completed")
        fallidas = sum(1 for e in executions if e.get("status") == "failed")

        # Latencias
        latencias = []
        for ex in executions:
            started = ex.get("started_at")
            finished = ex.get("finished_at")
            if started and finished:
                try:
                    s = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    f = datetime.fromisoformat(finished.replace("Z", "+00:00"))
                    latencias.append((f - s).total_seconds())
                except (ValueError, TypeError):
                    pass

        avg_latency_s = sum(latencias) / len(latencias) if latencias else 0.0
        max_latency_s = max(latencias) if latencias else 0.0

        # Tokens usados
        total_tokens = sum(ex.get("tokens_used", 0) or 0 for ex in executions)

        return {
            "total_executions": total,
            "completed": completadas,
            "failed": fallidas,
            "success_rate": round(completadas / total, 2) if total > 0 else 0.0,
            "avg_latency_s": round(avg_latency_s, 1),
            "max_latency_s": round(max_latency_s, 1),
            "total_tokens": total_tokens,
        }

    async def _generar_sintesis_llm(
        self,
        executions: list[dict[str, Any]],
        metrics: dict[str, Any],
    ) -> dict[str, Any]:
        """Usa el LLM para generar una síntesis inteligente."""
        try:
            from contracts.kernel_interface import IntentType

            # Preparar resumen de ejecuciones para el LLM
            exec_summary = []
            for ex in executions[:20]:  # Limitar para no exceder contexto
                exec_summary.append({
                    "job_id": ex.get("scheduled_job_id", "?"),
                    "status": ex.get("status", "?"),
                    "tokens": ex.get("tokens_used", 0),
                    "result_preview": (ex.get("result_summary") or "")[:200],
                })

            prompt = (
                "Eres el Motor de Orquestación Central (MOC) de El Monstruo. "
                "Analiza las siguientes métricas y ejecuciones recientes del sistema y genera:\n\n"
                "1. **Resumen ejecutivo** (2-3 oraciones)\n"
                "2. **Patrones detectados** (lista de 2-5 patrones)\n"
                "3. **Alertas** (si hay algo urgente o anómalo)\n"
                "4. **Recomendaciones** (acciones concretas para mejorar el sistema)\n\n"
                f"Métricas:\n{json.dumps(metrics, indent=2, ensure_ascii=False)}\n\n"
                f"Ejecuciones recientes:\n{json.dumps(exec_summary, indent=2, ensure_ascii=False)}\n\n"
                "Responde en JSON con keys: summary, patterns (list), alerts (list), recommendations (list)."
            )

            response, _ = await self._router.execute(
                message=prompt,
                model=SYNTHESIS_MODEL,
                intent=IntentType.BACKGROUND,
                context={"system_prompt": "Eres un analista de sistemas de IA. Responde SOLO en JSON válido."},
            )

            # Intentar parsear JSON
            try:
                # Limpiar posibles bloques de código markdown
                clean = response.strip()
                if clean.startswith("```"):
                    clean = clean.split("```")[1]
                    if clean.startswith("json"):
                        clean = clean[4:]
                parsed = json.loads(clean)
                return {
                    "summary": parsed.get("summary", ""),
                    "patterns": parsed.get("patterns", []),
                    "alerts": parsed.get("alerts", []),
                    "recommendations": parsed.get("recommendations", []),
                }
            except json.JSONDecodeError:
                # Si no es JSON válido, usar el texto como summary
                return {
                    "summary": response[:500],
                    "patterns": [],
                    "alerts": [],
                    "recommendations": [],
                }

        except Exception as e:
            logger.warning("moc_sintesis_llm_failed", error=str(e))
            return {
                "summary": f"Error al generar síntesis: {str(e)[:200]}",
                "patterns": [],
                "alerts": [f"Fallo en síntesis LLM: {str(e)[:100]}"],
                "recommendations": [],
            }

    async def _guardar_insight(
        self,
        synthesis: dict[str, Any],
        metrics: dict[str, Any],
        window_hours: int,
        user_id: str,
    ) -> Optional[str]:
        """Guarda el insight en la tabla moc_insights de Supabase."""
        try:
            from uuid import uuid4

            insight_id = str(uuid4())
            await self._db.insert(
                "moc_insights",
                {
                    "id": insight_id,
                    "user_id": user_id,
                    "window_hours": window_hours,
                    "summary": synthesis.get("summary", ""),
                    "patterns": json.dumps(synthesis.get("patterns", []), ensure_ascii=False),
                    "alerts": json.dumps(synthesis.get("alerts", []), ensure_ascii=False),
                    "recommendations": json.dumps(synthesis.get("recommendations", []), ensure_ascii=False),
                    "metrics": json.dumps(metrics, ensure_ascii=False),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            logger.info("moc_insight_saved", insight_id=insight_id)
            return insight_id
        except Exception as e:
            logger.warning("moc_insight_save_failed", error=str(e))
            return None
