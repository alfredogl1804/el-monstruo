# STATE FABRIC DECISION QUEUE v0.1

**Loop Owner:** `loop_state_fabric`
**Status:** Productive Local

## Objetivo
Proveer un mecanismo seguro, basado en archivos locales (file-based), para que T1 pueda inyectar decisiones de aprobación o rechazo de sprints en el reactor sin necesidad de APIs, bases de datos o interfaces web activas.

## Arquitectura
1. **Queue Directory:** `bridge/state_fabric/queue/`
2. **Decision File:** Archivos JSON que contienen la decisión de T1.
3. **Queue Reader:** Un módulo Python que el reactor lee al inicio de cada ciclo para procesar decisiones pendientes.

## Esquema de Decisión (`decision_schema.yaml`)
```yaml
decision_schema:
  version: "0.1"
  type: object
  properties:
    sprint_id:
      type: string
    decision:
      type: string
      enum: [APPROVE, REJECT, MODIFY]
    signature:
      type: string
      enum: [T1]
    timestamp:
      type: string
  required:
    - sprint_id
    - decision
    - signature
```

## Reglas de Procesamiento
1. El reactor solo procesa archivos con extensión `.json`.
2. El archivo debe cumplir con el esquema.
3. La firma debe ser estrictamente `T1`.
4. Una vez procesado, el archivo se mueve a `bridge/state_fabric/queue/archive/`.
5. Si la decisión es `APPROVE`, el reactor cambia el estado del `work_packet` a `READY` y lo agenda para ejecución en el siguiente ciclo.

## Restricciones
- El reactor **NUNCA** escribe en la cola, solo lee.
- T1 es la **ÚNICA** entidad autorizada para escribir en la cola (manualmente vía shell o script externo).
