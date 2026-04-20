"""
El Monstruo — Contrato Soberano #2: MemoryInterface
=====================================================
Define el contrato para la capa de memoria soberana.
La memoria es PROPIA: event log canónico sobre Postgres/Supabase.
Ningún framework externo (Mem0, Cognee, etc.) es source of truth.

Principio: Si no controlas qué recuerdas, no eres soberano.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

# ── Memory Types ────────────────────────────────────────────────────


class MemoryType(Enum):
    """Tipos de memoria que El Monstruo puede almacenar."""

    EPISODIC = "episodic"  # Conversaciones, interacciones
    SEMANTIC = "semantic"  # Hechos, conocimiento, entidades
    PROCEDURAL = "procedural"  # Cómo hacer cosas, workflows aprendidos
    POLICY = "policy"  # Decisiones de gobernanza, reglas aplicadas
    TOOL_CALL = "tool_call"  # Historial de herramientas ejecutadas
    INCIDENT = "incident"  # Errores, fallos, recuperaciones


class EntityType(Enum):
    """Tipos de entidades en el grafo de conocimiento."""

    PERSON = "person"
    ORGANIZATION = "organization"
    PROJECT = "project"
    CONCEPT = "concept"
    TOOL = "tool"
    LOCATION = "location"
    EVENT = "event"
    CUSTOM = "custom"


# ── Data Models ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class MemoryEvent:
    """
    Unidad atómica de memoria. Todo lo que El Monstruo recuerda
    pasa por aquí. Event sourcing: nunca se borra, solo se agrega.
    """

    event_id: UUID = field(default_factory=uuid4)
    memory_type: MemoryType = MemoryType.EPISODIC
    run_id: Optional[UUID] = None
    user_id: str = ""
    channel: str = ""
    content: str = ""
    embedding: Optional[list[float]] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class Entity:
    """Entidad en el grafo de conocimiento soberano."""

    entity_id: UUID = field(default_factory=uuid4)
    entity_type: EntityType = EntityType.CUSTOM
    name: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class Relation:
    """Relación entre dos entidades en el grafo."""

    relation_id: UUID = field(default_factory=uuid4)
    source_id: UUID = field(default_factory=uuid4)
    target_id: UUID = field(default_factory=uuid4)
    relation_type: str = ""  # "works_at", "owns", "manages", etc.
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    valid_from: datetime = field(default_factory=datetime.utcnow)
    valid_to: Optional[datetime] = None  # None = still valid


@dataclass
class Episode:
    """
    Agrupación de eventos en un episodio coherente.
    Una conversación completa, una sesión de trabajo, etc.
    """

    episode_id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    channel: str = ""
    events: list[MemoryEvent] = field(default_factory=list)
    summary: str = ""
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


@dataclass
class SearchResult:
    """Resultado de búsqueda en memoria."""

    event: MemoryEvent
    score: float = 0.0
    source: str = ""  # "vector", "keyword", "graph", "hybrid"


# ── Memory Contract ─────────────────────────────────────────────────


class MemoryInterface(ABC):
    """
    Contrato soberano de Memoria.

    La implementación usa Postgres/Supabase con pgvector como
    almacenamiento, pero este contrato es agnóstico al backend.

    Capacidades:
        - Event log append-only (event sourcing)
        - Búsqueda semántica (vector similarity)
        - Búsqueda por keywords
        - Grafo de conocimiento (entidades + relaciones)
        - Episodios (agrupación de eventos)
        - Replay (reconstruir cualquier estado desde eventos)
    """

    # ── Event Log ───────────────────────────────────────────────────

    @abstractmethod
    async def append(self, event: MemoryEvent) -> UUID:
        """
        Agrega un evento al log. Nunca se modifica ni se borra.
        Retorna el event_id asignado.
        """
        ...

    @abstractmethod
    async def append_batch(self, events: list[MemoryEvent]) -> list[UUID]:
        """Agrega múltiples eventos en una sola transacción."""
        ...

    # ── Search ──────────────────────────────────────────────────────

    @abstractmethod
    async def search_semantic(
        self,
        query: str,
        user_id: Optional[str] = None,
        memory_types: Optional[list[MemoryType]] = None,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[SearchResult]:
        """Búsqueda por similitud vectorial."""
        ...

    @abstractmethod
    async def search_keyword(
        self,
        query: str,
        user_id: Optional[str] = None,
        memory_types: Optional[list[MemoryType]] = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Búsqueda por keywords (full-text search)."""
        ...

    @abstractmethod
    async def search_hybrid(
        self,
        query: str,
        user_id: Optional[str] = None,
        memory_types: Optional[list[MemoryType]] = None,
        limit: int = 10,
        vector_weight: float = 0.7,
    ) -> list[SearchResult]:
        """Búsqueda híbrida: vector + keyword con pesos configurables."""
        ...

    # ── Knowledge Graph ─────────────────────────────────────────────

    @abstractmethod
    async def upsert_entity(self, entity: Entity) -> UUID:
        """Crea o actualiza una entidad en el grafo."""
        ...

    @abstractmethod
    async def add_relation(self, relation: Relation) -> UUID:
        """Agrega una relación entre entidades."""
        ...

    @abstractmethod
    async def get_entity_graph(
        self,
        entity_id: UUID,
        depth: int = 2,
    ) -> tuple[list[Entity], list[Relation]]:
        """
        Obtiene el subgrafo alrededor de una entidad.
        depth=1: solo relaciones directas.
        depth=2: relaciones de relaciones.
        """
        ...

    @abstractmethod
    async def find_entities(
        self,
        query: str,
        entity_type: Optional[EntityType] = None,
        limit: int = 10,
    ) -> list[Entity]:
        """Busca entidades por nombre o atributos."""
        ...

    # ── Episodes ────────────────────────────────────────────────────

    @abstractmethod
    async def start_episode(
        self,
        user_id: str,
        channel: str,
    ) -> Episode:
        """Inicia un nuevo episodio."""
        ...

    @abstractmethod
    async def end_episode(
        self,
        episode_id: UUID,
        summary: Optional[str] = None,
    ) -> Episode:
        """Cierra un episodio y opcionalmente genera resumen."""
        ...

    @abstractmethod
    async def get_recent_episodes(
        self,
        user_id: str,
        limit: int = 5,
    ) -> list[Episode]:
        """Obtiene los episodios más recientes de un usuario."""
        ...

    # ── Replay ──────────────────────────────────────────────────────

    @abstractmethod
    async def replay(
        self,
        run_id: UUID,
    ) -> list[MemoryEvent]:
        """
        Reconstruye la secuencia completa de eventos de una ejecución.
        Permite auditoría y debugging.
        """
        ...

    @abstractmethod
    async def get_event_count(
        self,
        user_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
    ) -> int:
        """Cuenta total de eventos, opcionalmente filtrados."""
        ...
