"""
Cowork capturer — extrae sesiones cerradas de cowork_sesiones → rotor_activity_log.

Sprint: ROTOR-001 (T2.4)
Trigger: trigger SQL on cowork_sesiones AFTER UPDATE (cuando ended_at se setea),
o polling cada 60s del worker.
"""

from __future__ import annotations

from typing import Any, Mapping

from kernel.rotor.capturers import BaseCapturer
from kernel.rotor.energy_calculator import RotorActivity, RotorSource


class CoworkCapturer(BaseCapturer):
    """Captura una sesión cerrada de Cowork y produce RotorActivity."""

    SOURCE: str = RotorSource.COWORK_SESSION.value
    DEFAULT_ACTOR: str = "cowork"

    def capture(self, raw_event: Mapping[str, Any]) -> RotorActivity:
        """
        raw_event esperado (subset cowork_sesiones row tras cierre):
          {
            "session_id": "uuid",
            "started_at": "2026-05-12T10:00:00+00:00",
            "ended_at": "2026-05-12T13:30:00+00:00",
            "duration_seconds": 12600,
            "actor": "cowork-arquitecto-t2-a",
            "decisiones_count": 3
          }
        """
        actor = str(raw_event.get("actor", self.DEFAULT_ACTOR))
        duration_seconds = int(raw_event.get("duration_seconds", 0))

        payload = {
            "session_id": str(raw_event.get("session_id", "")),
            "started_at": str(raw_event.get("started_at", "")),
            "ended_at": str(raw_event.get("ended_at", "")),
            "duration_seconds": duration_seconds,
            "decisiones_count": int(raw_event.get("decisiones_count", 0)),
        }

        return RotorActivity(source=self.SOURCE, actor=actor, payload=payload)


__all__ = ["CoworkCapturer"]
