# Contrato del Dispatcher Mínimo (SPR-DISPATCHER-MINIMAL-001)

## 1. Visión y Responsabilidad
El Dispatcher es el único componente autorizado para orquestar la ejecución de los loops en Vigilia Sincrónica y evaluar sus intenciones de acción. 
**Responsabilidad principal**: Conectar el `Policy Engine` (preflight_check) con el `State Fabric` (event_log y current_state) de manera pura y predecible.

## 2. Flujo de Ejecución (Action Request Lifecycle)

1. **Loop solicita acción**: Un loop emite un `action_request` (ej. querer escribir código).
2. **Dispatcher recibe**: El Dispatcher extrae el `loop_contract` desde el `loop_registry`.
3. **Validación (Policy Engine)**: El Dispatcher llama a `preflight_check(loop_contract, action_request, registry)`.
4. **Mutación de Estado (State Fabric)**:
   - Si `ALLOW`: El Dispatcher acepta la acción, genera un evento `STATE_DELTA_PROPOSED` o específico, lo anexa al `event_log` y actualiza el `last_event_id` en `current_state`.
   - Si `DENY`: El Dispatcher rechaza la acción, genera un evento `BLOCKER_DECLARED` o `AUDIT_REQUIRED` con el motivo del rechazo, lo anexa al log, y detiene la ejecución del loop.
5. **Respuesta al Loop**: El Dispatcher devuelve la decisión (`True/False`, `motivo`) al loop para que este reaccione.

## 3. Interfaces (Python)

### Clase `Dispatcher`

```python
class MinimalDispatcher:
    def __init__(self, state_fabric_dir, policy_registry_dir):
        # Carga el registry de acciones, el current_state y el loop_registry
        pass
        
    def dispatch_action(self, loop_id: str, action_request: dict) -> tuple[bool, str, dict]:
        """
        Evalúa y procesa una solicitud de acción de un loop.
        Retorna: (is_allowed, reason, event_generated)
        """
        pass
        
    def _record_event(self, event_type: str, loop_id: str, action_request: dict, reason: str, is_allowed: bool) -> dict:
        """
        Crea y anexa un evento al event_log.v0.jsonl y actualiza current_state.v0.json
        """
        pass
```

## 4. Estructura de Datos

**Input `action_request`**:
```json
{
  "action": "write_code",
  "target_path": "src/module.py",
  "has_evidence": true,
  "t1_approval_present": false,
  "auditor_lineage_id": null
}
```

**Output Event (ALLOW)**:
```json
{
  "event_id": 102,
  "created_at": "2026-05-20T16:00:00Z",
  "source_loop": "dispatcher",
  "source_lineage": "dispatcher_core",
  "event_type": "STATE_DELTA_PROPOSED",
  "subject": "Action Allowed: write_code",
  "summary": "Loop loop_ejecutor authorized to write_code at src/module.py",
  "autonomy_level": "A5",
  "status": "ACCEPTED",
  "dedupe_key": "dispatch_102"
}
```

**Output Event (DENY)**:
```json
{
  "event_id": 103,
  "created_at": "2026-05-20T16:01:00Z",
  "source_loop": "dispatcher",
  "source_lineage": "dispatcher_core",
  "event_type": "BLOCKER_DECLARED",
  "subject": "Action Denied: write_code",
  "summary": "REJECT: Autonomy Exceeded. Action requires A5, loop is A3.",
  "autonomy_level": "A8",
  "status": "ACCEPTED",
  "dedupe_key": "dispatch_103"
}
```

## 5. Criterios de Aceptación
1. `MinimalDispatcher` debe poder instanciarse apuntando a los directorios existentes de `state_fabric` y `policy_engine`.
2. Al llamar a `dispatch_action`, debe consultar correctamente `preflight_check`.
3. Debe escribir físicamente en `event_log.v0.jsonl` y `current_state.v0.json` (actualizando `last_event_id`).
4. Los tests unitarios deben cubrir casos de ALLOW y DENY, verificando la persistencia de estado.
