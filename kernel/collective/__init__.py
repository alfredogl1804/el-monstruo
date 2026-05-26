"""Módulo de Inteligencia Colectiva — El Monstruo Sprint 61 + 63.5."""

from .emergence_detector import (
    DETECTOR_SIN_SUPABASE,
    EmergenceDetector,
    get_emergence_detector,
    init_emergence_detector,
)
from .knowledge_propagator import (
    ALL_EMBRIONES,
    PROPAGADOR_PATRON_NO_ENCONTRADO,
    PROPAGADOR_TASA_EXITO_INSUFICIENTE,
    KnowledgePropagator,
    LearnedPattern,
    get_knowledge_propagator,
    init_knowledge_propagator,
)
from .protocol import (
    ColectivaDebateNoEncontrado,
    ColectivaMensajeInvalido,
    ColectivaProtocol,
    ColectivaVotacionCerrada,
    DebateSession,
    DecisionMethod,
    EmbrionMessage,
    MessageType,
    VoteSession,
    get_colectiva_protocol,
    init_colectiva_protocol,
)

__all__ = [
    # Sprint 61
    "ColectivaProtocol",
    "ColectivaMensajeInvalido",
    "ColectivaDebateNoEncontrado",
    "ColectivaVotacionCerrada",
    "EmbrionMessage",
    "DebateSession",
    "VoteSession",
    "MessageType",
    "DecisionMethod",
    "get_colectiva_protocol",
    "init_colectiva_protocol",
    # Sprint 63.5
    "KnowledgePropagator",
    "LearnedPattern",
    "get_knowledge_propagator",
    "init_knowledge_propagator",
    "PROPAGADOR_PATRON_NO_ENCONTRADO",
    "PROPAGADOR_TASA_EXITO_INSUFICIENTE",
    "ALL_EMBRIONES",
    "EmergenceDetector",
    "get_emergence_detector",
    "init_emergence_detector",
    "DETECTOR_SIN_SUPABASE",
]
