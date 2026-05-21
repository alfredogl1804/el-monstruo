# 12 EXAMPLES: STATE FABRIC IN ACTION

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Escenario 1: Mutación Exitosa
1. **Loop A3** lee `current_state.v0.json` y ve que no hay blockers.
2. Escribe un archivo nuevo en `bridge/doctrine_candidates/`.
3. Emite un evento `STATE_DELTA_PROPOSED` al `event_log.v0.jsonl` indicando que creó el archivo.
4. El **Reducer** procesa el log. Verifica que Loop A3 tiene permiso para esa acción.
5. El Reducer actualiza `current_state.v0.json` (ej. `last_event_id` y timestamp).

## Escenario 2: Rechazo por Policy
1. **Loop A3** intenta borrar un archivo en `src/`.
2. Emite un evento `STATE_DELTA_PROPOSED` al `event_log.v0.jsonl`.
3. El **Reducer** procesa el log. Ve que la acción requiere A5 y el path está prohibido para A3.
4. El Reducer marca el evento como `REJECTED` en su memoria interna y NO actualiza el estado de los archivos en `current_state.v0.json`. El evento queda en el log como evidencia del intento fallido.

## Escenario 3: Handoff
1. **Loop 1** emite `HANDOFF_READY` con `last_processed_event_id: 100`.
2. **Loop 2** arranca. Lee `loop_cursors.v0.json` y ve que su rol se quedó en el evento 100.
3. Lee el log desde el evento 101.
4. Encuentra un `TASK_CREATED` en el evento 105.
5. Inicia el trabajo en esa tarea.
