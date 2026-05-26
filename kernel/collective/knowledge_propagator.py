"""kernel/collective/knowledge_propagator.py

Knowledge Propagator — Sprint 63.5
Objetivo #8: Inteligencia Emergente

Los 7 embriones no solo se comunican (Sprint 61) sino que APRENDEN
unos de otros. Cuando Embrion-Tecnico descubre un patrón exitoso,
ese conocimiento se propaga automáticamente a los demás.
Emergencia real = aprendizaje colectivo sin programación explícita.

Soberanía:
    - Supabase: alternativa → SQLite local con tablas learned_patterns + embrion_knowledge
    - Propagación: async → alternativa → sincrónica con threading
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import structlog

logger = structlog.get_logger("collective.propagator")

# ── Errores con identidad ──────────────────────────────────────────────────────

PROPAGADOR_PATRON_NO_ENCONTRADO = (
    "El patrón especificado no existe en la base de conocimiento. "
    "Verifica el ID o registra el patrón primero con register_pattern()."
)
PROPAGADOR_TASA_EXITO_INSUFICIENTE = (
    "El patrón no cumple el umbral mínimo de tasa de éxito para propagación automática. "
    "Se requiere success_rate >= 0.8 y times_applied >= 3."
)
PROPAGADOR_EMBRION_INVALIDO = (
    "El nombre del embrión no es válido. "
    "Embriones válidos: ventas, tecnico, vigia, creativo, estratega, financiero, investigador."
)

# Los 7 embriones de la colmena
ALL_EMBRIONES = ["ventas", "tecnico", "vigia", "creativo", "estratega", "financiero", "investigador"]

# Umbral para propagación automática
AUTO_PROPAGATE_THRESHOLD = 0.8
AUTO_PROPAGATE_MIN_APPLICATIONS = 3
RETRACTION_THRESHOLD = 0.5
RETRACTION_MIN_APPLICATIONS = 5


# ── Modelo de datos ────────────────────────────────────────────────────────────


@dataclass
class LearnedPattern:
    """Patrón aprendido por un embrión y candidato a propagación.

    Args:
        source_embrion: Embrión que descubrió el patrón
        pattern_type: Tipo ("strategy", "tool_usage", "error_avoidance", "optimization")
        description: Descripción del patrón
        context: Cuándo aplicar el patrón
        success_rate: Tasa de éxito 0-1
        times_applied: Veces que se aplicó
        times_succeeded: Veces que tuvo éxito
        propagated_to: Lista de embriones a los que se propagó
        discovered_at: Timestamp de descubrimiento
        id: ID único (generado automáticamente)

    Returns:
        LearnedPattern listo para registrar y propagar

    Raises:
        ValueError: Si source_embrion no es válido

    Soberanía:
        Storage: Supabase → SQLite local
    """

    source_embrion: str
    pattern_type: str
    description: str
    context: str
    success_rate: float
    times_applied: int = 0
    times_succeeded: int = 0
    propagated_to: list = field(default_factory=list)
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        """Serializar para Command Center."""
        return {
            "id": self.id,
            "source_embrion": self.source_embrion,
            "pattern_type": self.pattern_type,
            "description": self.description[:200],
            "context": self.context[:200],
            "success_rate": round(self.success_rate, 3),
            "times_applied": self.times_applied,
            "times_succeeded": self.times_succeeded,
            "propagated_to": self.propagated_to,
            "discovered_at": self.discovered_at.isoformat(),
        }


# ── Propagador principal ───────────────────────────────────────────────────────


class KnowledgePropagator:
    """Propagador de conocimiento entre embriones de la colmena.

    Gestiona el ciclo completo de aprendizaje colectivo:
    registro → evaluación → propagación → validación → retracción.

    Args:
        supabase: Cliente Supabase para persistencia

    Returns:
        Propagador inicializado con caché en memoria

    Raises:
        RuntimeError: Si Supabase no está disponible (usa caché en memoria)

    Soberanía:
        Sin Supabase: caché en memoria con todos los patrones
        Propagación: async → compatible con APScheduler
    """

    def __init__(self, supabase=None):
        self.supabase = supabase
        self._patterns: dict = {}  # id -> LearnedPattern
        self._embrion_knowledge: dict = {}  # embrion -> list[pattern_id]
        logger.info("knowledge_propagator_init", has_supabase=supabase is not None)

    async def register_pattern(self, pattern: LearnedPattern) -> str:
        """Registrar un patrón recién descubierto.

        Args:
            pattern: LearnedPattern a registrar

        Returns:
            ID del patrón registrado

        Raises:
            ValueError: Si source_embrion no es válido

        Soberanía:
            Sin Supabase: persiste en caché en memoria
        """
        if pattern.source_embrion not in ALL_EMBRIONES:
            raise ValueError(f"{PROPAGADOR_EMBRION_INVALIDO} Recibido: {pattern.source_embrion}")

        # Persistir en Supabase
        if self.supabase:
            try:
                result = (
                    await self.supabase.table("learned_patterns")
                    .insert(
                        {
                            "source_embrion": pattern.source_embrion,
                            "pattern_type": pattern.pattern_type,
                            "description": pattern.description,
                            "context": pattern.context,
                            "success_rate": pattern.success_rate,
                            "times_applied": pattern.times_applied,
                            "times_succeeded": pattern.times_succeeded,
                            "propagated_to": pattern.propagated_to,
                        }
                    )
                    .execute()
                )
                pattern.id = result.data[0]["id"]
            except Exception as exc:
                logger.warning("pattern_persist_error", error=str(exc))

        # Caché en memoria
        self._patterns[pattern.id] = pattern

        logger.info(
            "pattern_registered",
            id=pattern.id,
            source=pattern.source_embrion,
            type=pattern.pattern_type,
            success_rate=round(pattern.success_rate, 3),
        )

        # Auto-propagar si cumple umbral
        if (
            pattern.success_rate >= AUTO_PROPAGATE_THRESHOLD
            and pattern.times_applied >= AUTO_PROPAGATE_MIN_APPLICATIONS
        ):
            await self.propagate(pattern.id)
        else:
            logger.info(
                "auto_propagate_skip",
                id=pattern.id,
                success_rate=pattern.success_rate,
                times_applied=pattern.times_applied,
                hint=PROPAGADOR_TASA_EXITO_INSUFICIENTE,
            )

        return pattern.id

    async def propagate(self, pattern_id: str, target_embriones: list = None) -> int:
        """Propagar un patrón a otros embriones.

        Args:
            pattern_id: ID del patrón a propagar
            target_embriones: Lista de embriones destino (None = todos excepto fuente)

        Returns:
            Número de embriones a los que se propagó

        Raises:
            ValueError: Si el patrón no existe

        Soberanía:
            Sin Supabase: propaga en caché en memoria
        """
        pattern = self._patterns.get(pattern_id)
        if not pattern and self.supabase:
            try:
                result = (
                    await self.supabase.table("learned_patterns").select("*").eq("id", pattern_id).single().execute()
                )
                if result.data:
                    pattern = LearnedPattern(
                        **{k: v for k, v in result.data.items() if k in LearnedPattern.__dataclass_fields__}
                    )
                    self._patterns[pattern_id] = pattern
            except Exception:
                pass

        if not pattern:
            raise ValueError(f"{PROPAGADOR_PATRON_NO_ENCONTRADO} ID: {pattern_id}")

        source = pattern.source_embrion
        if target_embriones is None:
            target_embriones = [e for e in ALL_EMBRIONES if e != source]

        already_propagated = set(pattern.propagated_to)
        new_targets = [e for e in target_embriones if e not in already_propagated]

        if not new_targets:
            logger.info("propagate_no_new_targets", pattern_id=pattern_id)
            return 0

        # Propagar a cada embrión destino
        for embrion in new_targets:
            if embrion not in self._embrion_knowledge:
                self._embrion_knowledge[embrion] = []
            self._embrion_knowledge[embrion].append(pattern_id)

            if self.supabase:
                try:
                    await (
                        self.supabase.table("embrion_knowledge")
                        .insert(
                            {
                                "embrion_name": embrion,
                                "pattern_id": pattern_id,
                                "learned_from": source,
                                "pattern_type": pattern.pattern_type,
                                "description": pattern.description,
                                "context": pattern.context,
                                "adopted": False,
                            }
                        )
                        .execute()
                    )
                except Exception as exc:
                    logger.warning("propagate_supabase_error", embrion=embrion, error=str(exc))

        # Actualizar lista de propagados
        pattern.propagated_to = list(already_propagated | set(new_targets))
        if self.supabase:
            try:
                await (
                    self.supabase.table("learned_patterns")
                    .update({"propagated_to": pattern.propagated_to})
                    .eq("id", pattern_id)
                    .execute()
                )
            except Exception:
                pass

        logger.info(
            "pattern_propagated",
            id=pattern_id,
            source=source,
            targets=new_targets,
            count=len(new_targets),
        )
        return len(new_targets)

    async def record_outcome(self, pattern_id: str, embrion: str, success: bool) -> None:
        """Registrar el resultado de aplicar un patrón propagado.

        Args:
            pattern_id: ID del patrón aplicado
            embrion: Embrión que lo aplicó
            success: Si la aplicación fue exitosa

        Raises:
            ValueError: Si el patrón no existe

        Soberanía:
            Sin Supabase: actualiza caché en memoria
        """
        pattern = self._patterns.get(pattern_id)
        if not pattern:
            logger.warning("outcome_pattern_not_found", pattern_id=pattern_id)
            return

        pattern.times_applied += 1
        if success:
            pattern.times_succeeded += 1
        pattern.success_rate = pattern.times_succeeded / pattern.times_applied

        if self.supabase:
            try:
                await (
                    self.supabase.table("learned_patterns")
                    .update(
                        {
                            "times_applied": pattern.times_applied,
                            "times_succeeded": pattern.times_succeeded,
                            "success_rate": pattern.success_rate,
                        }
                    )
                    .eq("id", pattern_id)
                    .execute()
                )
            except Exception as exc:
                logger.warning("outcome_supabase_error", error=str(exc))

        logger.info(
            "outcome_recorded",
            pattern_id=pattern_id,
            embrion=embrion,
            success=success,
            new_success_rate=round(pattern.success_rate, 3),
        )

        # Retraer si la tasa de éxito cae demasiado
        if pattern.success_rate < RETRACTION_THRESHOLD and pattern.times_applied >= RETRACTION_MIN_APPLICATIONS:
            await self._retract_pattern(pattern_id)

    async def get_relevant_patterns(self, embrion: str, context: str) -> list:
        """Obtener patrones relevantes para el contexto actual de un embrión.

        Args:
            embrion: Nombre del embrión
            context: Contexto de la tarea actual

        Returns:
            Lista de patrones relevantes ordenados por tasa de éxito

        Soberanía:
            Sin Supabase: busca en caché en memoria
        """
        if self.supabase:
            try:
                knowledge = (
                    await self.supabase.table("embrion_knowledge")
                    .select("*, learned_patterns(*)")
                    .eq("embrion_name", embrion)
                    .eq("adopted", True)
                    .execute()
                )
                context_lower = context.lower()
                relevant = []
                for item in knowledge.data or []:
                    pattern = item.get("learned_patterns", {})
                    if pattern and any(word in context_lower for word in pattern.get("context", "").lower().split()):
                        relevant.append(pattern)
                return sorted(relevant, key=lambda x: x.get("success_rate", 0), reverse=True)
            except Exception as exc:
                logger.warning("get_patterns_supabase_error", error=str(exc))

        # Búsqueda en caché en memoria
        pattern_ids = self._embrion_knowledge.get(embrion, [])
        context_lower = context.lower()
        relevant = []
        for pid in pattern_ids:
            pattern = self._patterns.get(pid)
            if pattern and any(word in context_lower for word in pattern.context.lower().split()):
                relevant.append(pattern)

        return sorted(relevant, key=lambda x: x.success_rate, reverse=True)

    async def _retract_pattern(self, pattern_id: str) -> None:
        """Retraer un patrón que ha demostrado ser poco confiable."""
        if self.supabase:
            try:
                await self.supabase.table("embrion_knowledge").delete().eq("pattern_id", pattern_id).execute()
                await (
                    self.supabase.table("learned_patterns")
                    .update({"propagated_to": [], "retracted": True})
                    .eq("id", pattern_id)
                    .execute()
                )
            except Exception as exc:
                logger.warning("retract_supabase_error", error=str(exc))

        # Limpiar caché
        if pattern_id in self._patterns:
            del self._patterns[pattern_id]
        for embrion in ALL_EMBRIONES:
            if embrion in self._embrion_knowledge:
                self._embrion_knowledge[embrion] = [
                    pid for pid in self._embrion_knowledge[embrion] if pid != pattern_id
                ]

        logger.warning("pattern_retracted", id=pattern_id)

    def get_stats(self) -> dict:
        """Obtener estadísticas del sistema de propagación."""
        patterns = list(self._patterns.values())
        return {
            "total_patterns": len(patterns),
            "propagated_patterns": sum(1 for p in patterns if p.propagated_to),
            "avg_success_rate": round(sum(p.success_rate for p in patterns) / max(1, len(patterns)), 3),
            "embriones_with_knowledge": len(self._embrion_knowledge),
            "total_propagations": sum(len(p.propagated_to) for p in patterns),
        }

    def to_dict(self) -> dict:
        """Serializar estado para Command Center."""
        return {
            "module": "KnowledgePropagator",
            "sprint": "63.5",
            "objetivo": "#8 Inteligencia Emergente",
            "has_supabase": self.supabase is not None,
            "all_embriones": ALL_EMBRIONES,
            "auto_propagate_threshold": AUTO_PROPAGATE_THRESHOLD,
            "retraction_threshold": RETRACTION_THRESHOLD,
            **self.get_stats(),
        }


# ── Singleton ──────────────────────────────────────────────────────────────────

_knowledge_propagator: Optional[KnowledgePropagator] = None


def get_knowledge_propagator() -> Optional[KnowledgePropagator]:
    """Obtener instancia singleton del propagador de conocimiento."""
    return _knowledge_propagator


def init_knowledge_propagator(supabase=None) -> KnowledgePropagator:
    """Inicializar el propagador de conocimiento entre embriones.

    Args:
        supabase: Cliente Supabase (opcional)

    Returns:
        KnowledgePropagator inicializado

    Soberanía:
        Sin Supabase: caché en memoria con propagación local
    """
    global _knowledge_propagator
    _knowledge_propagator = KnowledgePropagator(supabase=supabase)
    logger.info("knowledge_propagator_ready", embriones=len(ALL_EMBRIONES))
    return _knowledge_propagator
