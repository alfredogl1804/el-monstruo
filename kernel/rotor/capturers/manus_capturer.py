"""
Manus capturer — extrae actividad de hilos Manus desde embrion_memoria.

Sprint: ROTOR-001 (T2.5)
Trigger: polling cada 60s de embrion_memoria filtrando hilo_origen LIKE 'manus_%'
con cursor incremental (created_at).
"""

from __future__ import annotations

from typing import Any, Mapping

from kernel.rotor.capturers import BaseCapturer
from kernel.rotor.energy_calculator import RotorActivity, RotorSource

# Tipos de embrion_memoria que indican "sprint cerrado con PR mergeado"
PR_MERGED_TYPES = frozenset({"sprint_closure", "pr_merged", "decision"})


class ManusCapturer(BaseCapturer):
    """Captura actividad de hilos Manus y produce RotorActivity."""

    SOURCE: str = RotorSource.MANUS_SESSION.value
    DEFAULT_ACTOR: str = "manus_unknown"

    def capture(self, raw_event: Mapping[str, Any]) -> RotorActivity:
        """
        raw_event esperado (subset embrion_memoria row con hilo_origen='manus_%'):
          {
            "id": "uuid",
            "tipo": "sprint_closure" | "decision" | "pr_merged",
            "contenido": "Sprint X CERRADO. PR #N mergeado.",
            "hilo_origen": "manus_hilo_b",
            "importancia": 9,
            "created_at": "2026-05-12T05:30:00+00:00"
          }
        """
        actor = str(raw_event.get("hilo_origen", self.DEFAULT_ACTOR))
        tipo = str(raw_event.get("tipo", "")).lower()
        contenido = str(raw_event.get("contenido", ""))
        importancia = int(raw_event.get("importancia", 0))

        # Heurística PR mergeado: tipo + keyword "mergeado" o "merged" en contenido
        # + importancia >= 7 (filtro anti-noise)
        contenido_lower = contenido.lower()
        pr_merged = (
            tipo in PR_MERGED_TYPES
            and ("mergeado" in contenido_lower or "merged" in contenido_lower or "pr #" in contenido_lower)
            and importancia >= 7
        )

        payload = {
            "memoria_id": str(raw_event.get("id", "")),
            "tipo": tipo,
            "hilo_origen": actor,
            "importancia": importancia,
            "pr_merged": pr_merged,
            "created_at": str(raw_event.get("created_at", "")),
        }

        return RotorActivity(source=self.SOURCE, actor=actor, payload=payload)


__all__ = ["ManusCapturer", "PR_MERGED_TYPES"]
