# 08 STATE REDUCER RULES

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## El Reducer Conceptual
El Reducer es la función pura que transforma el `event_log` en el `current_state`. En v0, esto puede ser un script Python (o simplemente una convención manual documentada) que lee el log de arriba hacia abajo.

## Reglas de Reducción
1. **Inmutabilidad:** El reducer no altera el log. Solo calcula un estado en memoria y lo vuelca a `current_state.v0.json`.
2. **Idempotencia:** Ejecutar el reducer sobre el mismo log 100 veces debe producir exactamente el mismo `current_state`.
3. **Manejo de SUPERSEDED:** Si el evento N tiene `supersedes_event_id: M`, el reducer debe ignorar el efecto del evento M en el estado final.
4. **Manejo de BLOCKERS:** Un evento `BLOCKER_DECLARED` agrega un blocker a la lista activa. Un evento `STATE_DELTA_PROPOSED` que resuelva el blocker lo elimina de la lista activa.

## Firma del Reducer
`current_state = reduce(initial_state, event_log, policy_engine)`

El Reducer invoca al Policy Engine. Si un evento en el log no cumple con la política (ej. intentó una acción A7 pero el loop era A3), el Reducer **ignora** ese evento y no muta el `current_state`, dejando un warning en el log de errores deltas.
