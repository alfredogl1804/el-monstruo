"""
MinimalDispatcher — SPR-DISPATCHER-MINIMAL-001
El Monstruo — Vigilia Sincrónica

El Dispatcher es el único componente autorizado para evaluar y registrar
las intenciones de acción de los loops. Conecta:
  - Policy Engine (preflight_check) → decide ALLOW/DENY
  - State Fabric (event_log, current_state) → persiste la decisión

Principios:
  - Función pura: no toma decisiones de negocio, solo evalúa y registra.
  - Single Writer: solo el Dispatcher escribe en event_log y current_state.
  - Fail-loud: si no puede cargar estado, lanza excepción.
"""

import json
import os
from datetime import datetime, timezone

from .loader import load_yaml
from .preflight import preflight_check


class MinimalDispatcher:
    """
    Dispatcher mínimo que:
    1. Recibe un action_request de un loop.
    2. Consulta preflight_check con el contrato del loop.
    3. Registra el resultado como evento en State Fabric.
    4. Retorna (is_allowed, reason, event).
    """

    def __init__(self, state_fabric_dir, policy_base_dir):
        """
        Args:
            state_fabric_dir: Ruta al directorio de State Fabric (contiene
                              event_log.v0.jsonl, current_state.v0.json,
                              loop_registry.v0.yaml).
            policy_base_dir:  Ruta base del reactor_vigilia_foundation
                              (contiene autonomy_ladder/action_registry_v0.yaml).
        """
        self.state_fabric_dir = state_fabric_dir
        self.policy_base_dir = policy_base_dir

        # Cargar action registry
        registry_path = os.path.join(policy_base_dir, "autonomy_ladder", "action_registry_v0.yaml")
        if not os.path.exists(registry_path):
            raise FileNotFoundError(f"Action registry not found: {registry_path}")
        self.action_registry = load_yaml(registry_path)

        # Cargar loop registry
        loop_registry_path = os.path.join(state_fabric_dir, "loop_registry.v0.yaml")
        if not os.path.exists(loop_registry_path):
            raise FileNotFoundError(f"Loop registry not found: {loop_registry_path}")
        self.loop_registry = load_yaml(loop_registry_path)

        # Cargar current_state
        current_state_path = os.path.join(state_fabric_dir, "current_state.v0.json")
        if not os.path.exists(current_state_path):
            raise FileNotFoundError(f"Current state not found: {current_state_path}")
        with open(current_state_path, "r", encoding="utf-8") as f:
            self.current_state = json.load(f)

        # Paths de persistencia
        self._event_log_path = os.path.join(state_fabric_dir, "event_log.v0.jsonl")
        self._current_state_path = current_state_path

    def get_loop_contract(self, loop_id):
        """
        Extrae el contrato de un loop desde el loop_registry.
        Retorna dict con campos necesarios para preflight_check.
        """
        if loop_id not in self.loop_registry:
            return None

        entry = self.loop_registry[loop_id]
        return {
            "loop_id": entry.get("loop_id", loop_id),
            "max_autonomy_level": entry.get("max_autonomy_level", "A0"),
            "lineage_id": entry.get("owner", "unknown"),
            "forbidden_paths": entry.get("forbidden_actions", []),
            "allowed_paths": entry.get("allowed_write_paths", []),
        }

    def dispatch_action(self, loop_id, action_request):
        """
        Evalúa y procesa una solicitud de acción de un loop.

        Args:
            loop_id: Identificador del loop solicitante.
            action_request: Dict con al menos 'action' y opcionalmente
                           'target_path', 'has_evidence', 't1_approval_present',
                           'auditor_lineage_id'.

        Returns:
            Tuple (is_allowed: bool, reason: str, event: dict)
        """
        # 1. Obtener contrato del loop
        loop_contract = self.get_loop_contract(loop_id)
        if loop_contract is None:
            reason = f"REJECT: Loop '{loop_id}' not found in loop_registry."
            event = self._record_event(
                event_type="BLOCKER_DECLARED",
                loop_id=loop_id,
                action_request=action_request,
                reason=reason,
                is_allowed=False,
            )
            return False, reason, event

        # 2. Consultar Policy Engine
        is_allowed, reason = preflight_check(loop_contract, action_request, self.action_registry)

        # 3. Registrar evento
        if is_allowed:
            event = self._record_event(
                event_type="STATE_DELTA_PROPOSED",
                loop_id=loop_id,
                action_request=action_request,
                reason=reason,
                is_allowed=True,
            )
        else:
            event = self._record_event(
                event_type="BLOCKER_DECLARED",
                loop_id=loop_id,
                action_request=action_request,
                reason=reason,
                is_allowed=False,
            )

        return is_allowed, reason, event

    def _record_event(self, event_type, loop_id, action_request, reason, is_allowed):
        """
        Crea un evento, lo anexa al event_log.v0.jsonl y actualiza
        current_state.v0.json (last_event_id, last_updated_at).

        Returns:
            El evento generado (dict).
        """
        # Calcular next event_id
        last_id = self.current_state.get("last_event_id", 0)
        new_id = last_id + 1

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        action_name = action_request.get("action", "unknown")
        target_path = action_request.get("target_path", "")

        event = {
            "event_id": new_id,
            "created_at": now,
            "source_loop": "dispatcher",
            "source_lineage": "dispatcher_core",
            "event_type": event_type,
            "subject": f"Action {'Allowed' if is_allowed else 'Denied'}: {action_name}",
            "summary": f"Loop {loop_id} {'authorized' if is_allowed else 'denied'} "
            f"to {action_name}"
            f"{' at ' + target_path if target_path else ''}. "
            f"Reason: {reason}",
            "autonomy_level": action_request.get("autonomy_level_used", "A0"),
            "authority_required": "T1_SIGNED" if action_request.get("t1_approval_present") else "NONE",
            "t1_required": action_request.get("t1_approval_present", False),
            "risk_class": "LOW" if is_allowed else "MEDIUM",
            "confidence": 1.0,
            "status": "ACCEPTED",
            "supersedes_event_id": None,
            "dedupe_key": f"dispatch_{new_id}_{action_name}_{loop_id}",
            "ttl_hours": None,
            "forbidden_inferences": [],
        }

        # Persist: append to event_log
        with open(self._event_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        # Persist: update current_state
        self.current_state["last_event_id"] = new_id
        self.current_state["last_updated_at"] = now
        with open(self._current_state_path, "w", encoding="utf-8") as f:
            json.dump(self.current_state, f, indent=2)

        return event
