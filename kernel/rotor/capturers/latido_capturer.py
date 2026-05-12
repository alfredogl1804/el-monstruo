"""
Latido capturer — hook directo en embrion_loop.py para auto-recarga.

Sprint: ROTOR-001 (T2.6)
Trigger: hook al final de cada cycle del Embrión, dentro de marcadores
ROTOR_LATIDO_BEGIN/END en kernel/embrion_loop.py para revert trivial.

Doctrina del silencio sobre embrion_loop.py: solo agregar marcadores +
1 línea de import + 1 línea de invocación. Sin tocar lógica core del Volante.
"""

from __future__ import annotations

from typing import Any, Mapping

from kernel.rotor.capturers import BaseCapturer
from kernel.rotor.energy_calculator import RotorActivity, RotorSource


class LatidoCapturer(BaseCapturer):
    """
    Captura el resultado de un cycle del Embrión.

    Auto-recarga lenta ($0.01/latido success, -$0.05/latido aborted).
    """

    SOURCE: str = RotorSource.EMBRION_LATIDO.value
    DEFAULT_ACTOR: str = "embrion"

    def capture(self, raw_event: Mapping[str, Any]) -> RotorActivity:
        """
        raw_event esperado (al final de embrion_loop cycle):
          {
            "cycle_id": 12345,
            "status": "success" | "aborted",
            "duration_ms": 850,
            "aborted_reason": null | "self_verifier_block" | "budget_exhausted"
          }
        """
        actor = self.DEFAULT_ACTOR  # siempre el embrión mismo
        status = str(raw_event.get("status", "unknown")).lower()

        payload = {
            "cycle_id": int(raw_event.get("cycle_id", 0)),
            "status": status,
            "duration_ms": int(raw_event.get("duration_ms", 0)),
            "aborted_reason": raw_event.get("aborted_reason"),
        }

        return RotorActivity(source=self.SOURCE, actor=actor, payload=payload)


__all__ = ["LatidoCapturer"]
