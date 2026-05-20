# Unified Face Model

## Concepto
La "Unified Face" es el único punto de contacto entre el Monstruo y Alfredo (T1). Oculta la complejidad de la coreografía de loops.

## loop_unified_face
Este loop específico (A2) tiene la responsabilidad exclusiva de leer el estado consolidado (`current_state.after` y `event_log.after`) y generar un brief coherente para el usuario.

## Restricciones
- No ejecuta acciones.
- No modifica estado (solo emite el resumen).
- No alucina decisiones que no están en el log.
- Habla como "El Monstruo", no como un loop individual.
