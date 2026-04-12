"""
El Monstruo — Contrato Soberano #5: CheckpointModel
=====================================================
Define el contrato para persistencia de estado y checkpoints.
Permite replay, recovery, y auditoría completa del sistema.

Principio: Si no puedes reconstruir tu estado, no puedes sobrevivir.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class CheckpointType(Enum):
    """Tipos de checkpoint."""
    AUTO = "auto"           # Creado automáticamente por el sistema
    MANUAL = "manual"       # Creado por solicitud explícita
    PRE_TOOL = "pre_tool"   # Antes de ejecutar una herramienta
    ON_ERROR = "on_error"   # Cuando ocurre un error
    PERIODIC = "periodic"   # Checkpoint periódico programado


class SystemHealth(Enum):
    """Estado de salud del sistema."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RECOVERING = "recovering"


@dataclass(frozen=True)
class CheckpointData:
    """
    Datos completos de un checkpoint.
    Contiene todo lo necesario para reconstruir el estado
    exacto del sistema en un momento dado.
    """
    checkpoint_id: UUID = field(default_factory=uuid4)
    checkpoint_type: CheckpointType = CheckpointType.AUTO
    run_id: Optional[UUID] = None
    step: int = 0

    # State snapshots
    kernel_state: dict[str, Any] = field(default_factory=dict)
    memory_state: dict[str, Any] = field(default_factory=dict)
    router_state: dict[str, Any] = field(default_factory=dict)
    policy_state: dict[str, Any] = field(default_factory=dict)

    # Context
    active_tools: list[str] = field(default_factory=list)
    pending_actions: list[dict[str, Any]] = field(default_factory=list)
    conversation_context: dict[str, Any] = field(default_factory=dict)

    # Metadata
    reason: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    ttl_hours: int = 168  # 7 days default


@dataclass
class SystemState:
    """
    Estado global del sistema en un momento dado.
    Usado para health checks y monitoreo.
    """
    state_id: UUID = field(default_factory=uuid4)
    health: SystemHealth = SystemHealth.HEALTHY
    active_runs: int = 0
    total_runs_today: int = 0
    total_cost_today_usd: float = 0.0
    total_tokens_today: int = 0
    models_available: list[str] = field(default_factory=list)
    models_degraded: list[str] = field(default_factory=list)
    last_error: Optional[str] = None
    uptime_seconds: float = 0.0
    checked_at: datetime = field(default_factory=datetime.utcnow)


# ── Checkpoint Store Contract ───────────────────────────────────────

class CheckpointStore(ABC):
    """
    Contrato soberano para persistencia de checkpoints.

    Responsabilidades:
        - Guardar y restaurar checkpoints
        - Limpiar checkpoints expirados
        - Listar checkpoints para auditoría
        - Mantener el estado global del sistema
    """

    @abstractmethod
    async def save(self, checkpoint: CheckpointData) -> UUID:
        """
        Guarda un checkpoint. Retorna el checkpoint_id.
        """
        ...

    @abstractmethod
    async def load(self, checkpoint_id: UUID) -> Optional[CheckpointData]:
        """
        Carga un checkpoint por ID. Retorna None si no existe o expiró.
        """
        ...

    @abstractmethod
    async def load_latest(
        self,
        run_id: Optional[UUID] = None,
    ) -> Optional[CheckpointData]:
        """
        Carga el checkpoint más reciente.
        Si run_id se especifica, el más reciente de esa ejecución.
        """
        ...

    @abstractmethod
    async def list_checkpoints(
        self,
        run_id: Optional[UUID] = None,
        checkpoint_type: Optional[CheckpointType] = None,
        limit: int = 20,
    ) -> list[CheckpointData]:
        """Lista checkpoints con filtros opcionales."""
        ...

    @abstractmethod
    async def delete(self, checkpoint_id: UUID) -> bool:
        """Elimina un checkpoint específico."""
        ...

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
        Elimina checkpoints expirados (según ttl_hours).
        Retorna cantidad eliminada.
        """
        ...

    # ── System State ────────────────────────────────────────────────

    @abstractmethod
    async def save_system_state(self, state: SystemState) -> None:
        """Guarda el estado actual del sistema."""
        ...

    @abstractmethod
    async def get_system_state(self) -> SystemState:
        """Obtiene el estado más reciente del sistema."""
        ...

    @abstractmethod
    async def get_system_health(self) -> SystemHealth:
        """Shortcut: obtiene solo el estado de salud."""
        ...
