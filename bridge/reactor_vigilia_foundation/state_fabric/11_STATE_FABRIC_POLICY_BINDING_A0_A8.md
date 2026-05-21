# 11 STATE FABRIC POLICY BINDING A0-A8

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Integración con SPR-AUTONOMY-LADDER-001
El State Fabric no es ciego; está íntimamente ligado al Policy Engine.

## Reglas de Binding
1. **Eventos Tipados por Autonomía:** Cada evento en el `event_log` debe declarar el `autonomy_level` de la acción que representa.
2. **Rechazo en Reducción:** Si un evento declara una acción A7, pero el loop que lo emitió solo tiene contrato A3 en el `loop_registry`, el Reducer marca el evento como `STATUS: REJECTED_BY_POLICY` y no altera el `current_state`.
3. **Firmas T1 en el Fabric:** El archivo `decisions_pending.v0.json` es la fuente oficial para que el Policy Engine verifique si una acción `t1_required: true` ha sido aprobada. Si el status es `SIGNED`, el Policy Engine autoriza el evento.
4. **Bloqueo por Default:** Si el State Fabric está corrupto o no se puede leer, el Policy Engine asume nivel A8 (bloqueo total) para todas las operaciones de escritura.
