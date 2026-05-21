# POLICY: Heartbeat R0

## Reglas de Ejecución del Latido

1. **Local-First One-Shot:**
   El latido se ejecuta una vez y muere. No puede programar su propia re-ejecución ni dejar hilos vivos.

2. **Lectura Universal, Escritura Restringida:**
   El latido puede leer cualquier archivo del State Fabric, Loop Registry, o catálogos de riesgo. Solo puede escribir en su propio directorio (`reactor_heartbeat_r0/`) y hacer append en `event_log.v0.jsonl`.

3. **Sin Asunciones:**
   El latido no asume contexto implícito. Todas las precondiciones deben ser verificadas explícitamente al inicio del ciclo (Wake).

4. **Delegación de Permisos:**
   El latido no bypassa el Dispatcher. Si el latido decide ejecutar una cadena R0, cada paso de la cadena sigue solicitando permiso al Dispatcher.

## Acciones Prohibidas (Hard Blocks)

El latido **NUNCA** puede decidir ejecutar las siguientes acciones, independientemente del estado:

- `RUN_M2_API_REALTIME`
- `RUN_SCHEDULER`
- `RUN_DAEMON`
- `WRITE_CODE` (A5)
- `OPEN_PR` (A6)
- `DEPLOY` (A7)
- `TOUCH_SUPABASE`
- `TOUCH_MEMORY`
- `CANONIZE`

Cualquier intento de seleccionar estas acciones debe resultar en un fallo inmediato del gate de validación.
