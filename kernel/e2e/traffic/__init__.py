"""
Sprint 87.2 Bloque 4 — Traffic soberano del Monstruo.

Cierra deuda #5 del Sprint 87 NUEVO: stub vigia → instrumentación propia.
Privacy-first: cero tracking externo. Cookie de primera parte.
"""
from kernel.e2e.traffic.repository import (
    TrafficEvent,
    TrafficIngestFailed,
    TrafficRepository,
    TrafficSummary,
)

__all__ = [
    "TrafficEvent",
    "TrafficIngestFailed",
    "TrafficRepository",
    "TrafficSummary",
]
