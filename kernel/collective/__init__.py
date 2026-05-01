"""Módulo de Inteligencia Colectiva — El Monstruo Sprint 61 + 63.5."""
from .protocol import (
    ColectivaProtocol,
    ColectivaMensajeInvalido,
    ColectivaDebateNoEncontrado,
    ColectivaVotacionCerrada,
    EmbrionMessage,
    DebateSession,
    VoteSession,
    MessageType,
    DecisionMethod,
    get_colectiva_protocol,
    init_colectiva_protocol,
)
from .knowledge_propagator import (
    KnowledgePropagator,
    LearnedPattern,
    get_knowledge_propagator,
    init_knowledge_propagator,
    PROPAGADOR_PATRON_NO_ENCONTRADO,
    PROPAGADOR_TASA_EXITO_INSUFICIENTE,
    ALL_EMBRIONES,
)
from .emergence_detector import (
    EmergenceDetector,
    get_emergence_detector,
    init_emergence_detector,
    DETECTOR_SIN_SUPABASE,
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
