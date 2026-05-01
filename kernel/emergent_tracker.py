"""
El Monstruo — Emergent Behavior Tracker (Sprint 59.5)
======================================================
Detecta y registra comportamientos emergentes del sistema:
patrones que no fueron programados explícitamente pero surgen
de la interacción entre Embriones, Sabios y el pipeline.

¿Qué es un comportamiento emergente?
  - Un Embrión que descubre una estrategia de ventas no programada
  - Dos Embriones que colaboran espontáneamente sin instrucción explícita
  - El sistema que genera un output de calidad superior al esperado
  - Una solución creativa que ningún componente individual podría haber producido

Objetivo: #8 — Inteligencia Emergente Colectiva
Sprint: 59 — "El Monstruo Habla al Mundo"
Fecha: 2026-05-01

Soberanía:
  - Supabase (persistencia de comportamientos)
  - structlog (observabilidad)
  - Sin dependencia de LLM para detección básica (heurísticas propias)
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any

import structlog

logger = structlog.get_logger("monstruo.emergent_tracker")


# ── Errores con identidad ──────────────────────────────────────────────────────

class EMERGENT_TRACKER_SIN_SUPABASE(RuntimeError):
    """No hay cliente Supabase configurado para persistir comportamientos.
    
    Sugerencia: Inyecta _supabase al instanciar EmergentBehaviorTracker.
    Los comportamientos se acumularán en memoria hasta que se configure Supabase.
    """


class EMERGENT_TRACKER_COMPORTAMIENTO_INVALIDO(ValueError):
    """El comportamiento registrado no tiene los campos mínimos requeridos.
    
    Campos requeridos: embrion_id, behavior_type, description.
    """


# ── Enums ──────────────────────────────────────────────────────────────────────

class BehaviorType(str, Enum):
    """Tipos de comportamiento emergente detectables."""
    COLABORACION_ESPONTANEA = "colaboracion_espontanea"
    ESTRATEGIA_NO_PROGRAMADA = "estrategia_no_programada"
    OPTIMIZACION_AUTONOMA = "optimizacion_autonoma"
    SOLUCION_CREATIVA = "solucion_creativa"
    PATRON_REPETITIVO = "patron_repetitivo"
    ANOMALIA_POSITIVA = "anomalia_positiva"
    ANOMALIA_NEGATIVA = "anomalia_negativa"
    APRENDIZAJE_TRANSFERIDO = "aprendizaje_transferido"


class BehaviorSignificance(str, Enum):
    """Nivel de significancia del comportamiento emergente."""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


# ── Dataclasses ────────────────────────────────────────────────────────────────

@dataclass
class EmergentBehavior:
    """Comportamiento emergente detectado en el sistema.
    
    Args:
        id: UUID único del comportamiento.
        embrion_id: ID del Embrión que generó el comportamiento.
        behavior_type: Tipo de comportamiento (BehaviorType).
        description: Descripción detallada del comportamiento observado.
        context: Contexto en el que ocurrió (inputs, estado del sistema).
        significance: Nivel de significancia (BehaviorSignificance).
        reproducible: Si el comportamiento es reproducible de forma consistente.
        metadata: Datos adicionales específicos del comportamiento.
        detected_at: Timestamp de detección.
    """
    id: str
    embrion_id: str
    behavior_type: BehaviorType
    description: str
    context: dict
    significance: BehaviorSignificance
    reproducible: bool = False
    metadata: dict = field(default_factory=dict)
    detected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        """Serializar para el Command Center y Supabase."""
        return {
            "id": self.id,
            "embrion_id": self.embrion_id,
            "behavior_type": self.behavior_type.value,
            "description": self.description,
            "context": self.context,
            "significance": self.significance.value,
            "reproducible": self.reproducible,
            "metadata": self.metadata,
            "detected_at": self.detected_at,
        }


# ── Tracker principal ──────────────────────────────────────────────────────────

@dataclass
class EmergentBehaviorTracker:
    """Tracker de comportamientos emergentes del sistema El Monstruo.
    
    Detecta, registra y analiza patrones de comportamiento no programados
    que emergen de la interacción entre los componentes del sistema.
    
    Args:
        _supabase: Cliente Supabase para persistencia (soberanía: in-memory fallback).
        _sabios: Cliente de Sabios para análisis de patrones (opcional).
        significance_threshold: Nivel mínimo para alertar (default: MEDIA).
    
    Soberanía:
        - Supabase → in-memory list si no está configurado
        - LLM pattern analysis → heurísticas de frecuencia si Sabios no disponible
    """
    _supabase: Optional[object] = field(default=None, repr=False)
    _sabios: Optional[object] = field(default=None, repr=False)
    significance_threshold: BehaviorSignificance = BehaviorSignificance.MEDIA
    _behaviors_in_memory: list[EmergentBehavior] = field(default_factory=list, repr=False)
    _total_registered: int = field(default=0, repr=False)
    _total_by_type: dict = field(default_factory=dict, repr=False)

    async def register(
        self,
        embrion_id: str,
        behavior_type: BehaviorType,
        description: str,
        context: Optional[dict] = None,
        significance: BehaviorSignificance = BehaviorSignificance.MEDIA,
        reproducible: bool = False,
        metadata: Optional[dict] = None,
    ) -> EmergentBehavior:
        """Registrar un comportamiento emergente detectado.
        
        Args:
            embrion_id: ID del Embrión que generó el comportamiento.
            behavior_type: Tipo de comportamiento emergente.
            description: Descripción detallada del comportamiento.
            context: Contexto en el que ocurrió (opcional).
            significance: Nivel de significancia del comportamiento.
            reproducible: Si el comportamiento es reproducible.
            metadata: Datos adicionales (opcional).
        
        Returns:
            EmergentBehavior registrado con ID único.
        
        Raises:
            EMERGENT_TRACKER_COMPORTAMIENTO_INVALIDO: Si faltan campos requeridos.
        """
        if not embrion_id or not description:
            raise EMERGENT_TRACKER_COMPORTAMIENTO_INVALIDO(
                "embrion_id y description son campos requeridos para registrar un comportamiento."
            )

        behavior = EmergentBehavior(
            id=str(uuid.uuid4()),
            embrion_id=embrion_id,
            behavior_type=behavior_type,
            description=description,
            context=context or {},
            significance=significance,
            reproducible=reproducible,
            metadata=metadata or {},
        )

        # Persistir en Supabase o in-memory
        if self._supabase:
            try:
                await self._persist_to_supabase(behavior)
            except Exception as _e:
                logger.warning(
                    "supabase_persist_fallback",
                    error=str(_e)[:100],
                    behavior_id=behavior.id,
                )
                self._behaviors_in_memory.append(behavior)
        else:
            self._behaviors_in_memory.append(behavior)

        # Actualizar métricas
        self._total_registered += 1
        self._total_by_type[behavior_type.value] = (
            self._total_by_type.get(behavior_type.value, 0) + 1
        )

        # Log según significancia
        log_level = "info"
        if significance in (BehaviorSignificance.ALTA, BehaviorSignificance.CRITICA):
            log_level = "warning"

        getattr(logger, log_level)(
            "comportamiento_emergente_detectado",
            behavior_id=behavior.id,
            embrion_id=embrion_id,
            type=behavior_type.value,
            significance=significance.value,
            reproducible=reproducible,
        )

        return behavior

    async def _persist_to_supabase(self, behavior: EmergentBehavior) -> None:
        """Persistir comportamiento en tabla emergent_behaviors de Supabase.
        
        Args:
            behavior: EmergentBehavior a persistir.
        
        Soberanía: Si Supabase falla, el comportamiento se guarda in-memory.
        """
        data = behavior.to_dict()
        # Supabase client puede ser sync o async — intentamos ambos
        try:
            result = self._supabase.table("emergent_behaviors").upsert(data).execute()
            if hasattr(result, "error") and result.error:
                raise RuntimeError(f"Supabase error: {result.error}")
        except AttributeError:
            # Cliente async
            await self._supabase.table("emergent_behaviors").upsert(data).execute()

    async def get_recent_behaviors(
        self,
        limit: int = 20,
        embrion_id: Optional[str] = None,
        behavior_type: Optional[BehaviorType] = None,
    ) -> list[dict]:
        """Obtener comportamientos recientes con filtros opcionales.
        
        Args:
            limit: Máximo de comportamientos a retornar.
            embrion_id: Filtrar por Embrión específico (opcional).
            behavior_type: Filtrar por tipo de comportamiento (opcional).
        
        Returns:
            Lista de comportamientos serializados como dicts.
        """
        if self._supabase:
            try:
                query = (
                    self._supabase.table("emergent_behaviors")
                    .select("*")
                    .order("detected_at", desc=True)
                    .limit(limit)
                )
                if embrion_id:
                    query = query.eq("embrion_id", embrion_id)
                if behavior_type:
                    query = query.eq("behavior_type", behavior_type.value)

                result = query.execute()
                return result.data or []
            except Exception as _e:
                logger.warning("supabase_query_fallback", error=str(_e)[:100])

        # Fallback in-memory
        behaviors = self._behaviors_in_memory
        if embrion_id:
            behaviors = [b for b in behaviors if b.embrion_id == embrion_id]
        if behavior_type:
            behaviors = [b for b in behaviors if b.behavior_type == behavior_type]

        return [b.to_dict() for b in sorted(
            behaviors,
            key=lambda x: x.detected_at,
            reverse=True,
        )[:limit]]

    async def analyze_patterns(self) -> dict:
        """Analizar patrones en los comportamientos emergentes registrados.
        
        Detecta comportamientos repetitivos, colaboraciones frecuentes
        y anomalías que merecen atención.
        
        Returns:
            Dict con patrones detectados, frecuencias y recomendaciones.
        """
        recent = await self.get_recent_behaviors(limit=100)

        if not recent:
            return {
                "total_analyzed": 0,
                "patterns": [],
                "recommendations": ["Aún no hay suficientes datos para análisis de patrones."],
            }

        # Análisis de frecuencia por tipo
        type_freq: dict[str, int] = {}
        embrion_freq: dict[str, int] = {}
        for b in recent:
            t = b.get("behavior_type", "unknown")
            e = b.get("embrion_id", "unknown")
            type_freq[t] = type_freq.get(t, 0) + 1
            embrion_freq[e] = embrion_freq.get(e, 0) + 1

        patterns = []
        for t, count in sorted(type_freq.items(), key=lambda x: -x[1]):
            if count >= 3:
                patterns.append({
                    "pattern": f"Comportamiento '{t}' repetido {count} veces",
                    "frequency": count,
                    "significance": "alta" if count >= 10 else "media",
                })

        # Si hay Sabios, enriquecer el análisis
        recommendations = []
        if self._sabios and patterns:
            try:
                prompt = f"""Analyze these emergent behavior patterns in an AI agent system:
{json.dumps(patterns, indent=2)}

Provide 3 specific recommendations to:
1. Amplify positive patterns
2. Mitigate negative ones
3. Improve the system based on what's emerging

Respond in JSON array of strings."""
                response = await self._sabios.ask(prompt)
                json_str = response.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0]
                recommendations = json.loads(json_str)
            except Exception as _e:
                logger.warning("pattern_analysis_llm_fallback", error=str(_e)[:100])
                recommendations = [
                    f"El tipo de comportamiento más frecuente es '{max(type_freq, key=type_freq.get)}'.",
                    f"El Embrión más activo es '{max(embrion_freq, key=embrion_freq.get)}'.",
                ]

        return {
            "total_analyzed": len(recent),
            "type_frequencies": type_freq,
            "embrion_frequencies": embrion_freq,
            "patterns": patterns,
            "recommendations": recommendations,
        }

    def to_dict(self) -> dict:
        """Estado del tracker para consumo del Command Center.
        
        Returns:
            Dict serializable con estado actual del EmergentBehaviorTracker.
        """
        return {
            "componente": "emergent_behavior_tracker",
            "version": "1.0.0-sprint59",
            "objetivo": "#8 Inteligencia Emergente Colectiva",
            "estado": "activo",
            "persistencia": "supabase" if self._supabase else "in_memory",
            "significance_threshold": self.significance_threshold.value,
            "metricas": {
                "total_registrados": self._total_registered,
                "in_memory_count": len(self._behaviors_in_memory),
                "por_tipo": self._total_by_type,
            },
            "behavior_types": [e.value for e in BehaviorType],
        }


# ── Singleton global ───────────────────────────────────────────────────────────

_emergent_tracker: Optional[EmergentBehaviorTracker] = None


def get_emergent_tracker() -> EmergentBehaviorTracker:
    """Obtener la instancia global del EmergentBehaviorTracker.
    
    Returns:
        Instancia global del tracker.
    
    Raises:
        RuntimeError: Si el tracker no ha sido inicializado.
    """
    if _emergent_tracker is None:
        raise RuntimeError(
            "EmergentBehaviorTracker no inicializado. "
            "Llama a init_emergent_tracker() en el lifespan de main.py."
        )
    return _emergent_tracker


def init_emergent_tracker(
    supabase_client: Optional[object] = None,
    sabios_client: Optional[object] = None,
) -> EmergentBehaviorTracker:
    """Inicializar el singleton global del EmergentBehaviorTracker.
    
    Args:
        supabase_client: Cliente Supabase para persistencia (opcional).
        sabios_client: Cliente de Sabios para análisis de patrones (opcional).
    
    Returns:
        Instancia inicializada del tracker.
    """
    global _emergent_tracker
    _emergent_tracker = EmergentBehaviorTracker(
        _supabase=supabase_client,
        _sabios=sabios_client,
    )
    logger.info(
        "emergent_tracker_inicializado",
        persistencia="supabase" if supabase_client else "in_memory",
        sabios=sabios_client is not None,
    )
    return _emergent_tracker
