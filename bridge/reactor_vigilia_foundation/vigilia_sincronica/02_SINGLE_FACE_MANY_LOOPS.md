# Un solo rostro, muchas mentes

## La Ilusión de Continuidad
El usuario (Alfredo/T1) interactúa con "El Monstruo". No interactúa con `loop_vigia`, `loop_auditor`, o `loop_oraculo`. La arquitectura oculta la multiplicidad de procesos detrás de una **Unified Face**.

## Especialización de Loops
Cada loop es una mente especializada, finita y efímera. Nace, recibe contexto (Handoff), ejecuta su tarea (dentro de su nivel A0-A8), propone cambios de estado, y muere o se suspende.

## Prevención de Split-Brain
Para que muchas mentes actúen como una sola, es imperativo que:
1. Ningún loop escriba directamente en la base de datos de estado.
2. Todo pase por el **State Fabric** (Reducer).
3. El **Dispatcher** decida el turno de ejecución. No hay comunicación "peer-to-peer" directa entre loops.
