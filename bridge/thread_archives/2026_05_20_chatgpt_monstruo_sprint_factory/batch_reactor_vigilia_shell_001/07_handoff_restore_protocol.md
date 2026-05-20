# Handoff / Restore Protocol

## El Problema
El "Dory distribuido": cuando un loop termina y otro empieza, el contexto se puede perder o diluir.

## La Solución
El Dispatcher empaqueta un `Handoff Packet` estricto para el loop entrante.

## Contenido del Handoff
1. El `current_state` (o una vista relevante de él).
2. Los `recent_events` (del Event Log).
3. El `loop_contract` del loop entrante (sus límites).
4. `active_blockers` y decisiones T1 pendientes.

## Validación
El loop entrante debe ejecutar un "Restore Test" implícito. Si no puede validar su estado o restricciones, aborta. No opera a ciegas.
