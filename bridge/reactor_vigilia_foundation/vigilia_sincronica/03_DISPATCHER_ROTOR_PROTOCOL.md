# Dispatcher / Rotor Protocol

## Rol del Dispatcher
El Dispatcher es el orquestador central de la Vigilia Sincrónica. Es el único componente autorizado para activar loops.

## Reglas
1. **Coreografía, no Orquestación Distribuida:** Los loops no se llaman entre sí.
2. **Ciclo de Decisión:**
   - Leer `current_state` y `event_log`.
   - Evaluar qué loop debe correr (basado en pending decisions, blockers, etc.).
   - Preparar `handoff_packet`.
   - Invocar loop.
   - Recibir `loop_output` (event proposals).
   - Aplicar Reducer para generar nuevo `current_state` y `event_log.after`.
3. **Restricción:** El Dispatcher no toma decisiones de negocio, solo enruta y consolida estado.
