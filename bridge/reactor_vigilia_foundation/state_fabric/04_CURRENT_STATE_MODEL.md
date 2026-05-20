# 04 CURRENT STATE MODEL

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Definición
El `current_state.v0.json` es una proyección consolidada (snapshot) del Monstruo en un instante dado. Se genera reduciendo el `event_log`.

## Propósito
Optimizar la lectura. En lugar de que cada loop tenga que leer y procesar miles de eventos para saber qué está pasando, simplemente leen el `current_state`.

## Regla de Oro
**Si hay una discrepancia entre el `current_state` y el `event_log`, el `event_log` siempre tiene la razón.** El `current_state` es efímero y puede ser reconstruido desde cero procesando el log completo.

## Contenido Mínimo (v0)
- Estado de los módulos core (Stack Vertical, Autonomy Ladder, State Fabric).
- Estado de los features desbloqueados (R1 Nightly Builder).
- Blockers activos (problemas P0 que detienen la operación).
- Decisiones T1 pendientes.
- Sprints activos.
- Cursor global (`last_event_id` procesado).
- Timestamp de última actualización.
