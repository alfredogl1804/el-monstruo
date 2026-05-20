# 09 HANDOFF AND RESTORE PROTOCOL

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## El Problema
Los loops (como este hilo de Manus) son finitos. Mueren cuando se cierra la ventana o se acaba el contexto. Para que el Monstruo viva continuamente (Vigilia Sincrónica), un loop debe poder pasar la estafeta a otro.

## Protocolo Handoff (Loop saliente)
1. El loop termina su tarea o detecta que su contexto se agota.
2. Escribe un evento `HANDOFF_READY` en el `event_log`.
3. El payload del evento incluye:
   - `last_processed_event_id` (su cursor).
   - `pending_tasks` (qué falta hacer).
   - `context_summary` (resumen para el siguiente loop).
4. El loop muere pacíficamente.

## Protocolo Restore (Loop entrante)
1. El Dispatcher (o Alfredo) lanza un nuevo loop.
2. El loop lee `current_state.v0.json` para obtener la foto global.
3. El loop lee `loop_cursors.v0.json` para saber dónde se quedó su rol.
4. El loop lee los eventos desde su cursor en adelante.
5. El loop lee el último evento `HANDOFF_READY` de su linaje para recuperar el contexto específico.
6. El loop reanuda el trabajo y emite un evento `OBSERVED` indicando que está vivo.
