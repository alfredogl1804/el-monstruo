"""
Supabase capturer — polling de kernel_audit_log → rotor_activity_log.

Sprint: ROTOR-001 (T2.2)
Trigger: Worker cada 60s polling kernel_audit_log con cursor incremental.
"""

from __future__ import annotations

from typing import Any, Mapping

from kernel.rotor.capturers import BaseCapturer
from kernel.rotor.energy_calculator import RotorActivity, RotorSource

# Queries triviales (health checks, etc.) que NO suman energía
TRIVIAL_QUERY_PATTERNS = ("SELECT 1", "select 1", "BEGIN", "COMMIT", "ROLLBACK")
HEALTH_CHECK_TABLES = frozenset({"pg_class", "pg_namespace", "pg_stat_activity"})


class SupabaseCapturer(BaseCapturer):
    """Captura una query de kernel_audit_log y produce RotorActivity."""

    SOURCE: str = RotorSource.SUPABASE_QUERY.value
    DEFAULT_ACTOR: str = "cowork_mcp"

    def capture(self, raw_event: Mapping[str, Any]) -> RotorActivity:
        """
        raw_event esperado (subset de kernel_audit_log row):
          {
            "actor": "cowork" | "manus_hilo_b" | ...,
            "table_name": "embrion_memoria",
            "query_type": "INSERT",
            "query_text": "INSERT INTO ...",
            "rows_affected": 1,
            "duration_ms": 45
          }
        """
        actor = str(raw_event.get("actor", self.DEFAULT_ACTOR))
        table_name = str(raw_event.get("table_name", ""))
        query_type = str(raw_event.get("query_type", "UNKNOWN")).upper()
        query_text = str(raw_event.get("query_text", ""))

        # Detectar queries triviales (no suman energía)
        trivial = (
            table_name in HEALTH_CHECK_TABLES
            or any(query_text.startswith(p) for p in TRIVIAL_QUERY_PATTERNS)
            or int(raw_event.get("rows_affected", 0)) == 0
            and query_type == "SELECT"
        )

        payload = {
            "table": table_name,
            "query_type": query_type,
            "rows_affected": int(raw_event.get("rows_affected", 0)),
            "duration_ms": int(raw_event.get("duration_ms", 0)),
            "trivial": trivial,
        }

        return RotorActivity(source=self.SOURCE, actor=actor, payload=payload)


__all__ = ["SupabaseCapturer", "TRIVIAL_QUERY_PATTERNS", "HEALTH_CHECK_TABLES"]
