"""
El Monstruo — Contrato Soberano #1: KernelInterface
=====================================================
Define el contrato que CUALQUIER motor de orquestación debe cumplir.
El Kernel es el corazón soberano: controla flujo, estado y ejecución.
Si el motor subyacente cambia (Semantic Kernel → PydanticAI → custom),
este contrato NO cambia.

Principio: El Monstruo define sus transiciones. El motor las ejecuta.
"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Callable, Optional
from uuid import UUID, uuid4


# ── Run States ──────────────────────────────────────────────────────

class RunStatus(enum.Enum):
    """Estados posibles de una ejecución del Kernel."""
    PENDING = "pending"
    ROUTING = "routing"
    EXECUTING = "executing"
    AWAITING_TOOL = "awaiting_tool"
    AWAITING_HUMAN = "awaiting_human"
    STREAMING = "streaming"
    CHECKPOINTED = "checkpointed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IntentType(enum.Enum):
    """Tipos de intención detectados por el Router."""
    CHAT = "chat"
    DEEP_THINK = "deep_think"
    EXECUTE = "execute"
    BACKGROUND = "background"
    SYSTEM = "system"


# ── Data Models ─────────────────────────────────────────────────────

@dataclass(frozen=True)
class RunInput:
    """Entrada canónica para iniciar una ejecución."""
    run_id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    channel: str = "telegram"  # telegram | console | api
    message: str = ""
    attachments: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    parent_run_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RunOutput:
    """Salida canónica de una ejecución."""
    run_id: UUID = field(default_factory=uuid4)
    status: RunStatus = RunStatus.COMPLETED
    intent: IntentType = IntentType.CHAT
    model_used: str = ""
    response: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class Checkpoint:
    """Snapshot del estado de una ejecución para replay y recovery."""
    checkpoint_id: UUID = field(default_factory=uuid4)
    run_id: UUID = field(default_factory=uuid4)
    step: int = 0
    status: RunStatus = RunStatus.CHECKPOINTED
    state: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


# ── Kernel Contract ─────────────────────────────────────────────────

class KernelInterface(ABC):
    """
    Contrato soberano del Kernel.

    Cualquier implementación (Semantic Kernel, PydanticAI, state machine
    propia) DEBE cumplir este contrato. El Monstruo nunca importa
    directamente el motor — solo habla con esta interfaz.

    Métodos obligatorios:
        start_run   → Inicia una nueva ejecución
        step        → Avanza un paso en la ejecución
        checkpoint  → Guarda estado para replay/recovery
        resume      → Reanuda desde un checkpoint
        cancel      → Cancela una ejecución (kill switch)
        stream      → Streaming de tokens para respuesta en tiempo real
    """

    @abstractmethod
    async def start_run(self, input: RunInput) -> RunOutput:
        """
        Inicia una nueva ejecución completa.
        Detecta intención → routea modelo → ejecuta → retorna resultado.
        """
        ...

    @abstractmethod
    async def step(self, run_id: UUID, input: dict[str, Any]) -> RunOutput:
        """
        Avanza un paso en una ejecución multi-step.
        Usado para tool calls, human-in-the-loop, y ejecuciones largas.
        """
        ...

    @abstractmethod
    async def checkpoint(self, run_id: UUID) -> Checkpoint:
        """
        Guarda el estado actual de una ejecución.
        Permite replay y recovery ante fallos.
        """
        ...

    @abstractmethod
    async def resume(self, checkpoint: Checkpoint) -> RunOutput:
        """
        Reanuda una ejecución desde un checkpoint guardado.
        """
        ...

    @abstractmethod
    async def cancel(self, run_id: UUID, reason: str = "") -> bool:
        """
        Kill switch: cancela una ejecución inmediatamente.
        Retorna True si se canceló exitosamente.
        """
        ...

    @abstractmethod
    async def stream(self, input: RunInput) -> AsyncIterator[str]:
        """
        Streaming de tokens para respuesta en tiempo real.
        Yield de cada token/chunk conforme el modelo los genera.
        """
        ...

    @abstractmethod
    async def get_status(self, run_id: UUID) -> RunStatus:
        """Consulta el estado actual de una ejecución."""
        ...

    @abstractmethod
    async def register_hook(
        self,
        event: str,
        callback: Callable[..., Any],
    ) -> None:
        """
        Registra un hook para eventos del ciclo de vida.
        Eventos: pre_route, post_route, pre_execute, post_execute,
                 pre_tool, post_tool, on_error, on_cancel.
        """
        ...
