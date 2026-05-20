# Especificación de la Simulación

## Objetivo
Demostrar un ciclo completo de Vigilia Sincrónica (Dispatcher -> Loop Vigia -> Reducer -> Loop Memoria -> Reducer -> Loop Auditor -> Reducer -> Loop Unified Face) sin usar runtime productivo.

## Componentes Simulados
- **Dispatcher:** Un script Python (`simulate_vigilia_cycle.py`) que actúa como orquestador.
- **Loops:** Funciones Python mockeadas dentro del script que respetan los contratos A0-A8.
- **State Fabric:** Archivos JSON/JSONL locales leídos y escritos por el Dispatcher.

## Flujo
1. Dispatcher lee `current_state.sample.json`.
2. Dispatcher activa `loop_vigia`.
3. `loop_vigia` emite `event_proposals`.
4. Dispatcher aplica Reducer -> `event_log.after` y `current_state.after`.
5. Se repite para `loop_memoria_memento`, `loop_auditor` y `loop_unified_face`.
6. Output final generado en `sim_runs/{timestamp}/`.
