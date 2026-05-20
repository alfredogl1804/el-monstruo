# 06 LOOP CURSOR MODEL

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## El Problema del Dory Distribuido
Si un loop se despierta y no sabe qué eventos del log ya procesó, volverá a procesar todo desde el principio (amnesia) o se perderá eventos recientes (desconexión). Esto es letal para la Vigilia Sincrónica.

## La Solución: Cursores
El `loop_cursors.v0.json` mantiene un registro de hasta qué `event_id` ha leído y procesado cada loop activo.

## Mecánica
1. Un loop se despierta y lee su cursor.
2. Lee el `event_log` desde ese cursor hacia adelante.
3. Procesa los eventos relevantes para su rol.
4. Emite un evento `CURSOR_UPDATED` (o lo incluye en su `HANDOFF_READY`).
5. El State Fabric actualiza el `loop_cursors.v0.json`.

## Regla de Seguridad
Si un loop no puede demostrar su cursor actual (ej. crash, corrupción), se le revoca automáticamente la autonomía A3+ hasta que un proceso de recuperación valide su estado. No puede escribir a ciegas.
