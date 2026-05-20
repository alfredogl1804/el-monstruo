# Handoff / Restore Protocol

## El Paquete de Handoff
Cuando un loop despierta, debe recibir todo el contexto necesario para actuar sin "Síndrome de Dory". Esto se empaca en el `handoff_packet`.

## Contenido Obligatorio del Handoff
- `current_state` (resumido o relevante).
- `recent_events` (del `event_log`).
- `loop_contract` (max_autonomy_level, forbidden_actions).
- `active_blockers` y `pending_t1_decisions`.

## Validación (Restore)
El loop debe demostrar que asimiló el handoff. Si no puede validar sus restricciones o su estado actual, debe abortar con `HANDOFF_FAILED`. No operar ciego`.
