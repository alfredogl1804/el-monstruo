# Diseño del Loop: Oráculo de IAs (SPR-EMBRION-PERITO-LOOP-001)

## 1. Visión General
El **Oráculo de IAs** es el primer Embrión Perito (M1/M2) implementado como un loop real en Vigilia Sincrónica. Su rol es analizar capacidades emergentes de IA y proponer aplicaciones (Power Stacks) para El Monstruo.

A diferencia de los loops mockeados en `simulate_vigilia_cycle.py`, este loop **interactuará con el `MinimalDispatcher` real** para solicitar permisos antes de actuar.

## 2. Contrato en `loop_registry.v0.yaml` (Existente)
- **loop_id**: `loop_oraculo_ias`
- **max_autonomy_level**: `A3`
- **allowed_write_paths**: `["bridge/doctrine_candidates/"]`
- **forbidden_actions**: `["touch_supabase", "modify_kernel"]`

## 3. Flujo de Ejecución del Loop

El loop recibe un `handoff_packet` del Dispatcher (o del simulador) y ejecuta el siguiente ciclo interno:

1. **Analizar Contexto**: Revisa el `current_state` y `recent_events` para saber si debe actuar.
2. **Generar Catálogo (Simulado)**: Genera un pequeño catálogo de nuevas capacidades IA (ej. "GPT-4o Vision Audit").
3. **Solicitar Permiso (Action Request)**: 
   - Llama a `dispatcher.dispatch_action("loop_oraculo_ias", action_request)`
   - `action_request` = `{"action": "create_state_fabric_draft", "target_path": "bridge/doctrine_candidates/oraculo_output.json", "has_evidence": True}`
4. **Reaccionar a la Decisión**:
   - Si `ALLOW`: Procede a escribir físicamente el archivo de output. Retorna `SUCCESS` con propuestas de eventos.
   - Si `DENY`: Cancela la escritura. Retorna `BLOCKED` con el motivo.

## 4. Estructura del Código (`loop_oraculo_ias.py`)

```python
import json
import os

class OraculoIALoop:
    def __init__(self, dispatcher, output_dir):
        self.dispatcher = dispatcher
        self.output_dir = output_dir
        self.loop_id = "loop_oraculo_ias"

    def run(self, handoff_packet):
        # 1. Generar contenido
        catalog = {
            "capabilities": [
                {"model": "GPT-4o", "feature": "Real-time Vision", "application": "UI Audit"}
            ]
        }
        
        target_file = os.path.join(self.output_dir, "oraculo_catalog.json")
        
        # 2. Solicitar permiso al Dispatcher
        action_request = {
            "action": "create_state_fabric_draft",
            "target_path": "bridge/doctrine_candidates/oraculo_catalog.json",
            "has_evidence": True
        }
        
        is_allowed, reason, event = self.dispatcher.dispatch_action(self.loop_id, action_request)
        
        # 3. Ejecutar si fue permitido
        if is_allowed:
            with open(target_file, 'w') as f:
                json.dump(catalog, f, indent=2)
                
            return {
                "loop_id": self.loop_id,
                "status": "SUCCESS",
                "event_proposals": [event], # Propagamos el evento del dispatcher
                "next_suggested_loop": "loop_auditor",
                "message": "Oraculo catalog created successfully."
            }
        else:
            return {
                "loop_id": self.loop_id,
                "status": "BLOCKED",
                "event_proposals": [event],
                "next_suggested_loop": "STOP",
                "message": f"Action blocked by dispatcher: {reason}"
            }
```

## 5. Simulación End-to-End (`simulate_oraculo_e2e.py`)

Crearemos un script que:
1. Instancia el `MinimalDispatcher`.
2. Instancia el `OraculoIALoop` pasándole el dispatcher.
3. Ejecuta `oraculo.run(handoff)`.
4. Verifica que el archivo `oraculo_catalog.json` se haya creado y que el `event_log` tenga el evento `STATE_DELTA_PROPOSED`.
