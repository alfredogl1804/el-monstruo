# Protocolo de Secuencia del Dispatcher

**SPRINT:** SPR-VIGILIA-SINCRONICA-002
**Estado:** DOCTRINE_CANDIDATE

## 1. El Rol del Dispatcher en la Cadena

El `MinimalDispatcher` actúa como la aduana obligatoria para cada acción que cualquier loop intente realizar dentro de la cadena. Ningún archivo se escribe y ningún estado cambia sin que el Dispatcher retorne `ALLOW`.

## 2. Flujo de Secuencia (Sequence Flow)

Para cada loop en la cadena, el protocolo de interacción con el Dispatcher es idéntico:

1. **Intención:** El loop determina que necesita realizar una acción (ej. escribir un reporte).
2. **Request:** El loop construye un `action_request` (ver `action_registry_v0.yaml`).
3. **Dispatch:** El loop llama a `dispatcher.dispatch_action(self.LOOP_ID, action_request)`.
4. **Preflight:** El Dispatcher consulta al `Policy Engine` (`preflight_check`).
5. **Log:** El Dispatcher escribe la decisión (ALLOW/DENY) en el Event Log del State Fabric.
6. **Ejecución:** Solo si la respuesta es ALLOW, el loop procede a ejecutar la acción física (ej. `open(file, 'w')`).

## 3. Autorización de Handoffs

Los Handoff Packets son creados por el Orquestador (Rotor), no por los loops individuales. Sin embargo, para mantener la coherencia del State Fabric, el Orquestador también debe someter la creación del Handoff Packet al Dispatcher.

- **Acción:** `create_handoff_packet`
- **Actor:** `orquestador_cadena_v0`
- **Nivel:** A2

## 4. Registro de Eventos en Cadena

Para aislar la simulación del estado global de producción, la cadena de este sprint utiliza un Event Log Delta (`chain_event_log_delta.v0_1.jsonl`).

El Dispatcher será instanciado apuntando a este delta. La secuencia de eventos esperada en el log es:

1. `STATE_DELTA_PROPOSED` (Oráculo escribe catálogo)
2. `STATE_DELTA_PROPOSED` (Oráculo escribe reporte)
3. `BLOCKER_DECLARED` (Oráculo intenta write_code - DENY esperado)
4. `ORACLE_CHAIN_STEP_COMPLETED` (Orquestador)
5. `HANDOFF_READY` (Orquestador prepara paquete para Auditor)
6. `STATE_DELTA_PROPOSED` (Auditor escribe findings)
7. `STATE_DELTA_PROPOSED` (Auditor escribe gate log)
8. `AUDIT_CHAIN_STEP_COMPLETED` (Orquestador)
9. `HANDOFF_READY` (Orquestador prepara paquete para Risk)
10. `STATE_DELTA_PROPOSED` (Risk escribe overlay)
11. `RISK_CLASSIFICATION_CHAIN_STEP_COMPLETED` (Orquestador)
12. `HANDOFF_READY` (Orquestador prepara paquete para Unified Face)
13. `STATE_DELTA_PROPOSED` (Unified Face escribe summary)
14. `CHAIN_EXECUTION_COMPLETED` (Orquestador finaliza cadena)

## 5. Prevención de Falsificación de Autoridad

El Dispatcher validará estrictamente que ningún loop en la cadena intente usar acciones que requieran autoridad humana (`t1_required: true`) sin la firma correspondiente. Si el Oráculo intenta marcar el catálogo como `REALTIME_VERIFIED` o `T1_SIGNED`, el Dispatcher emitirá un DENY inmediato, rompiendo la cadena.
