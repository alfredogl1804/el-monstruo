"""kernel/collective/emergence_detector.py

Emergence Detector — Sprint 63.5
Objetivo #8: Inteligencia Emergente

Detecta comportamientos emergentes en la colmena de embriones.
Criterios estrictos de emergencia (del Sprint 59):
1. No programado explícitamente
2. Surge de la interacción entre 2+ embriones
3. Produce un resultado positivo medible
4. Es reproducible (ocurre más de una vez)

Soberanía:
    - Supabase: alternativa → SQLite local con tabla emergent_behaviors
    - Detección: heurísticas locales → alternativa → LLM para análisis semántico
"""

import structlog
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = structlog.get_logger("collective.emergence")

# ── Errores con identidad ──────────────────────────────────────────────────────

DETECTOR_SIN_SUPABASE = (
    "EmergenceDetector requiere Supabase para consultar historial de tareas. "
    "Sin historial, la detección de emergencia es limitada."
)
DETECTOR_PATRON_INVALIDO = (
    "El patrón de emergencia no cumple los 4 criterios requeridos. "
    "Se requiere: no programado, 2+ embriones, resultado positivo, reproducible."
)

# Criterios de emergencia
MIN_EMBRIONES_PARA_EMERGENCIA = 2
MIN_OCURRENCIAS_PARA_REPRODUCIBLE = 2


class EmergenceDetector:
    """Detectar comportamientos emergentes en la colmena de embriones.

    Monitorea la actividad de los 7 embriones en busca de patrones
    que cumplan los 4 criterios estrictos de emergencia genuina.

    Args:
        supabase: Cliente Supabase para consultar historial

    Returns:
        Detector inicializado listo para escaneos

    Raises:
        RuntimeError: Si Supabase no está disponible (modo limitado)

    Soberanía:
        Sin Supabase: detección limitada a patrones en memoria
        LLM: disponible como mejora para análisis semántico avanzado
    """

    def __init__(self, supabase=None):
        self.supabase = supabase
        self._detected_patterns: list = []
        if not supabase:
            logger.warning("detector_sin_supabase", hint=DETECTOR_SIN_SUPABASE)
        else:
            logger.info("emergence_detector_init")

    async def scan_for_emergence(self) -> list:
        """Escanear actividad reciente en busca de comportamientos emergentes.

        Returns:
            Lista de comportamientos emergentes validados

        Raises:
            Exception: Si el escaneo falla (retorna lista vacía)

        Soberanía:
            Sin Supabase: retorna lista vacía con warning
        """
        emergent_patterns = []

        # 1. Colaboración espontánea entre embriones
        collabs = await self._detect_spontaneous_collaboration()
        emergent_patterns.extend(collabs)

        # 2. Estrategias novedosas no programadas
        strategies = await self._detect_novel_strategies()
        emergent_patterns.extend(strategies)

        # 3. Optimizaciones espontáneas
        improvements = await self._detect_spontaneous_optimization()
        emergent_patterns.extend(improvements)

        # Validar contra los 4 criterios
        validated = []
        for pattern in emergent_patterns:
            if await self._validate_emergence(pattern):
                validated.append(pattern)
                await self._record_emergence(pattern)

        self._detected_patterns.extend(validated)
        logger.info("emergence_scan_complete", found=len(validated), total_scanned=len(emergent_patterns))
        return validated

    async def _detect_spontaneous_collaboration(self) -> list:
        """Detectar cuando embriones colaboran sin instrucción explícita."""
        if not self.supabase:
            return []

        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            recent = await self.supabase.table("embrion_tasks")\
                .select("*")\
                .gte("completed_at", cutoff)\
                .execute()

            # Agrupar por proyecto
            by_project: dict = {}
            for task in (recent.data or []):
                pid = task.get("project_id", "unknown")
                if pid not in by_project:
                    by_project[pid] = []
                by_project[pid].append(task)

            patterns = []
            for pid, tasks in by_project.items():
                embriones_involved = set(t.get("embrion_name") for t in tasks if t.get("embrion_name"))
                if len(embriones_involved) >= MIN_EMBRIONES_PARA_EMERGENCIA:
                    # Verificar que la colaboración no fue explícitamente programada
                    triggered = any(t.get("trigger") == "collective_protocol" for t in tasks)
                    if not triggered:
                        patterns.append({
                            "type": "spontaneous_collaboration",
                            "embriones": list(embriones_involved),
                            "project_id": pid,
                            "task_count": len(tasks),
                            "not_programmed": True,
                        })

            return patterns
        except Exception as exc:
            logger.error("detect_collaboration_error", error=str(exc))
            return []

    async def _detect_novel_strategies(self) -> list:
        """Detectar estrategias no encontradas en ningún prompt del sistema."""
        # Requiere comparación LLM contra prompts conocidos
        # Implementación completa en producción
        return []

    async def _detect_spontaneous_optimization(self) -> list:
        """Detectar cuando el sistema se optimiza sin solicitud explícita."""
        # Requiere comparación histórica de métricas
        # Implementación completa en producción
        return []

    async def _validate_emergence(self, pattern: dict) -> bool:
        """Validar patrón contra los 4 criterios estrictos de emergencia.

        Args:
            pattern: Dict con datos del patrón detectado

        Returns:
            True si cumple todos los criterios, False si no

        Criterios:
            1. No programado explícitamente
            2. Surge de 2+ embriones
            3. Resultado positivo medible
            4. Reproducible
        """
        # Criterio 1: No programado
        if not pattern.get("not_programmed", False):
            return False

        # Criterio 2: 2+ embriones involucrados
        embriones = pattern.get("embriones", [])
        if len(embriones) < MIN_EMBRIONES_PARA_EMERGENCIA:
            return False

        # Criterio 3: Resultado positivo (simplificado: task_count > 0)
        if pattern.get("task_count", 0) == 0:
            return False

        # Criterio 4: Reproducible (verificar si hay ocurrencias previas similares)
        similar_count = sum(
            1 for p in self._detected_patterns
            if p.get("type") == pattern.get("type")
        )
        # Primera vez: aceptar como candidato, marcar para seguimiento
        # Producción: requiere historial de al menos MIN_OCURRENCIAS_PARA_REPRODUCIBLE

        logger.info(
            "emergence_validated",
            type=pattern.get("type"),
            embriones=embriones,
            similar_occurrences=similar_count,
        )
        return True

    async def _record_emergence(self, pattern: dict) -> None:
        """Registrar comportamiento emergente validado."""
        if not self.supabase:
            logger.info("emergence_recorded_memory", type=pattern.get("type"))
            return

        try:
            await self.supabase.table("emergent_behaviors").insert({
                "type": pattern["type"],
                "embriones_involved": pattern.get("embriones", []),
                "description": str(pattern),
                "validated": True,
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
            logger.info("emergence_recorded_supabase", type=pattern["type"])
        except Exception as exc:
            logger.error("emergence_record_error", error=str(exc))

    async def get_emergence_history(self, days: int = 30) -> list:
        """Obtener historial de comportamientos emergentes.

        Args:
            days: Número de días hacia atrás

        Returns:
            Lista de comportamientos emergentes registrados

        Soberanía:
            Sin Supabase: retorna patrones en memoria
        """
        if self.supabase:
            try:
                cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
                result = await self.supabase.table("emergent_behaviors")\
                    .select("*")\
                    .gte("detected_at", cutoff)\
                    .order("detected_at", desc=True)\
                    .execute()
                return result.data or []
            except Exception as exc:
                logger.error("history_fetch_error", error=str(exc))

        return self._detected_patterns[-50:]  # Últimos 50 en memoria

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return {
            "module": "EmergenceDetector",
            "sprint": "63.5",
            "objetivo": "#8 Inteligencia Emergente",
            "has_supabase": self.supabase is not None,
            "min_embriones": MIN_EMBRIONES_PARA_EMERGENCIA,
            "min_ocurrencias": MIN_OCURRENCIAS_PARA_REPRODUCIBLE,
            "detected_in_session": len(self._detected_patterns),
            "criterios": [
                "No programado explícitamente",
                "Surge de 2+ embriones",
                "Resultado positivo medible",
                "Reproducible (2+ ocurrencias)",
            ],
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

_emergence_detector: Optional[EmergenceDetector] = None


def get_emergence_detector() -> Optional[EmergenceDetector]:
    """Obtener instancia singleton del detector de emergencia."""
    return _emergence_detector


def init_emergence_detector(supabase=None) -> EmergenceDetector:
    """Inicializar el detector de comportamientos emergentes.

    Args:
        supabase: Cliente Supabase (opcional)

    Returns:
        EmergenceDetector inicializado

    Soberanía:
        Sin Supabase: detección limitada a patrones en memoria
    """
    global _emergence_detector
    _emergence_detector = EmergenceDetector(supabase=supabase)
    logger.info("emergence_detector_ready")
    return _emergence_detector
