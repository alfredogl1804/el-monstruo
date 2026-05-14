"""
kernel/anti_dory — Attachment operativo verificable.

Sprint: MANUS-ANTI-DORY-002 v1 FASE B.
Doctrina canónica: "Anti-Dory no es memoria. Es attachment operativo
verificable antes del primer pensamiento del agente."

Componentes:
- context_broker: hidrata el prompt ANTES de task.create. Externo al agente.
- writers: AgentExplicitWriter (4 modos), HeartbeatWriter (independiente),
  ExternalPollingWriter (lectura de runtime_events para reconstrucción).
- guardian: AttachmentVerdict + verify_attachment_contract + HALT_ATTACHMENT_MISMATCH.
- recovery: Recovery Mode con pregunta binaria (NO reexplicación humana).

NO importa cowork_runtime ni cowork_guardian. NO-CRUCE estricto.
Feature flag de entrada: ANTI_DORY_ENABLED (default False mientras no hay
migrations aplicadas en Supabase). El agente cae a flujo legacy si flag=False.
"""
from __future__ import annotations

import os

ANTI_DORY_ENABLED: bool = os.environ.get("ANTI_DORY_ENABLED", "false").lower() == "true"

__all__ = ["ANTI_DORY_ENABLED"]
