# 03 EVENT LOG APPEND-ONLY

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Definición
El `event_log.v0.jsonl` es la fuente única de la verdad absoluta (Source of Truth) del Monstruo. Es un archivo de texto donde cada línea es un objeto JSON válido que representa un evento inmutable ocurrido en el tiempo.

## Reglas Estrictas
1. **Append-Only:** Los eventos solo se pueden agregar al final del archivo. NUNCA se borra ni se modifica un evento existente.
2. **Correcciones:** Si un evento fue erróneo, se emite un nuevo evento que invalida o corrige el anterior (usando el campo `supersedes_event_id`).
3. **No Authority by Event:** El hecho de que un evento esté en el log no significa que su acción fue ejecutada o autorizada. El Policy Engine evalúa la autoridad del evento al momento de procesarlo.

## Eventos Mínimos Permitidos
- `OBSERVED`: Un loop notó algo relevante (no muta estado).
- `STATE_DELTA_PROPOSED`: Un loop sugiere un cambio en el estado.
- `BLOCKER_DECLARED`: Un loop declara que no puede avanzar.
- `HANDOFF_READY`: Un loop terminó su trabajo y pasa el control.
- `TASK_CREATED` / `TASK_UPDATED` / `TASK_BLOCKED`
- `RESTORE_TEST_PASSED` / `RESTORE_TEST_FAILED`
- `T1_DECISION_REQUIRED` / `T1_DECISION_RECORDED`
- `AUDIT_REQUIRED` / `AUDIT_COMPLETED`
- `SUPERSEDED`: Invalida un evento anterior.

## Data-as-Instruction Prevention
Los eventos pueden contener payloads de datos externos, pero deben marcarse explícitamente como DATA. El State Fabric no ejecuta instrucciones ocultas en los payloads de los eventos (mitigación de prompt injection).
