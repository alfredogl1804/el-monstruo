# 02 SINGLE WRITER PRINCIPLE

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## El Problema del Split-Brain
Si múltiples loops de IA (ej. un hilo de Manus y un hilo de Cowork) intentan modificar el estado global del Monstruo al mismo tiempo, ocurrirá una condición de carrera (race condition) o un "split-brain", donde el sistema no sabrá cuál es la verdad.

## La Solución: Single-Writer
El State Fabric opera bajo el principio de Single-Writer estricto:

1. **Los loops NO escriben el estado:** Ningún loop (sea ejecutor, auditor, perito o vigía) tiene permiso para sobrescribir `current_state.v0.json` directamente.
2. **Los loops proponen eventos:** Un loop que desea cambiar el estado debe emitir un evento (ej. `STATE_DELTA_PROPOSED`) y agregarlo al `event_log.v0.jsonl`.
3. **El State Fabric consolida:** Un proceso único, síncrono y centralizado (el Reducer) lee el `event_log`, procesa los eventos en orden cronológico, y emite un nuevo `current_state.v0.json`.
4. **Unified Face:** Cuando el usuario (Alfredo) o un nuevo loop consulta el estado del Monstruo, siempre lee el `current_state.v0.json` consolidado por el Single-Writer, nunca un estado intermedio de otro loop.

## Implementación en v0
En esta fase file-backed, el Single-Writer es un concepto. En la práctica, significa que cualquier script que consolide el estado debe bloquear (lock) el archivo para asegurar procesamiento secuencial de los eventos.
