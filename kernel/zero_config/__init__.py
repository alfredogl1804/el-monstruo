"""kernel/zero_config — Sprint 63.2: Zero-Config Experience

Objetivo #3: Mínima Complejidad
Crea proyectos funcionales en <60 segundos desde una sola frase.
"""

from .intent_inferrer import (
    INFERRER_CONFIANZA_BAJA,
    INFERRER_INPUT_VACIO,
    InferredProject,
    IntentInferrer,
    get_intent_inferrer,
    init_intent_inferrer,
)
from .smart_defaults import (
    SMART_DEFAULTS,
    ProjectDefaults,
    get_defaults,
    list_available_combinations,
)

__all__ = [
    "IntentInferrer",
    "InferredProject",
    "get_intent_inferrer",
    "init_intent_inferrer",
    "INFERRER_INPUT_VACIO",
    "INFERRER_CONFIANZA_BAJA",
    "ProjectDefaults",
    "SMART_DEFAULTS",
    "get_defaults",
    "list_available_combinations",
]
