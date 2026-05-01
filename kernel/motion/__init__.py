"""kernel/motion — Sprint 63.3: Motion Design System

Objetivo #2: Nivel Apple/Tesla
Sistema de animaciones coherente con tokens, presets y orquestación.
"""

from .tokens import (
    MotionToken,
    MOTION_TOKENS,
    INTERACTION_PRESETS,
    STYLE_MOTION_PROFILES,
)
from .orchestrator import (
    MotionOrchestrator,
    get_motion_orchestrator,
    init_motion_orchestrator,
    ORCHESTRATOR_ESTILO_NO_ENCONTRADO,
)

__all__ = [
    "MotionToken",
    "MOTION_TOKENS",
    "INTERACTION_PRESETS",
    "STYLE_MOTION_PROFILES",
    "MotionOrchestrator",
    "get_motion_orchestrator",
    "init_motion_orchestrator",
    "ORCHESTRATOR_ESTILO_NO_ENCONTRADO",
]
