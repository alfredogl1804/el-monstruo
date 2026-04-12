"""
El Monstruo — Contratos Soberanos
==================================
Los 5 contratos que definen la soberanía del sistema.
Cualquier implementación DEBE cumplir estos contratos.
Si el motor cambia, los contratos permanecen.
"""

from .kernel_interface import (
    Checkpoint,
    IntentType,
    KernelInterface,
    RunInput,
    RunOutput,
    RunStatus,
)
from .memory_interface import (
    Entity,
    EntityType,
    Episode,
    MemoryEvent,
    MemoryInterface,
    MemoryType,
    Relation,
    SearchResult,
)
from .event_envelope import (
    EventBuilder,
    EventCategory,
    EventEnvelope,
    Severity,
)
from .policy_hook import (
    PolicyContext,
    PolicyDecision,
    PolicyHook,
    PolicyPhase,
    PolicyPipeline,
    PolicyVerdict,
)
from .checkpoint_model import (
    CheckpointData,
    CheckpointStore,
    CheckpointType,
    SystemHealth,
    SystemState,
)

__all__ = [
    # Kernel
    "KernelInterface", "RunInput", "RunOutput", "RunStatus",
    "IntentType", "Checkpoint",
    # Memory
    "MemoryInterface", "MemoryEvent", "MemoryType", "Entity",
    "EntityType", "Relation", "Episode", "SearchResult",
    # Events
    "EventEnvelope", "EventCategory", "EventBuilder", "Severity",
    # Policy
    "PolicyHook", "PolicyPipeline", "PolicyContext",
    "PolicyDecision", "PolicyVerdict", "PolicyPhase",
    # Checkpoint
    "CheckpointStore", "CheckpointData", "CheckpointType",
    "SystemState", "SystemHealth",
]
