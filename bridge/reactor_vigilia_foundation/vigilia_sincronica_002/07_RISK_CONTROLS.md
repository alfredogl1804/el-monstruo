# Controles de Riesgo (Risk Controls)

**SPRINT:** SPR-VIGILIA-SINCRONICA-002
**Estado:** DOCTRINE_CANDIDATE

## 1. Prevención de Autonomy Creep

El mayor riesgo de una cadena de ejecución es que un loop asuma permisos que no tiene, basándose en los resultados de un loop anterior. Para mitigar esto, se implementan controles estrictos en el Orquestador y el Dispatcher.

## 2. Aislamiento de Ejecución (Sandboxing)

- **Event Log Delta:** La cadena no escribe en el `event_log.v0.jsonl` principal. Usa un `chain_event_log_delta.v0_1.jsonl` aislado. Esto permite simular y validar sin contaminar el estado base.
- **Sin Runtime Daemon:** La cadena es un script Python (`run_vigilia_chain_v0.py`) que inicia, ejecuta la secuencia y termina. No hay hilos persistentes ni timers.

## 3. Barreras de Handoff (Handoff Gates)

El Orquestador inyecta banderas explícitas en cada Handoff Packet:

- `not_realtime_verified: true` — Obliga a los loops receptores (Auditor, Risk) a tratar la evidencia como estática.
- `no_m2_unlock: true` — Impide que cualquier loop proponga transicionar el estado a M2.

## 4. Policy Engine Binding

El `MinimalDispatcher` está atado a la Escalera de Autonomía (`action_registry_v0.yaml`).
- El Oráculo está limitado a A3.
- El Auditor está limitado a A3.
- La Unified Face está limitada a A2.

Si cualquier loop intenta una acción superior (ej. `write_code` A5, o `touch_supabase` A8), el Dispatcher retornará `DENY` y la cadena abortará.

## 5. Validación Post-Cadena

El script `validate_vigilia_chain_v0.py` ejecuta 12 gates independientes sobre los artefactos resultantes para garantizar que ningún control de riesgo fue violado durante la ejecución. Si un solo gate falla, el sprint no puede ser declarado verde.
