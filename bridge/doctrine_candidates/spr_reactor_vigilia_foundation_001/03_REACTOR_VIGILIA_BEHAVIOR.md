# 03 REACTOR VIGILIA BEHAVIOR

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Concepto Central
La infraestructura de Vigilia Sincrónica provee el tiempo. El Reactor de Vigilia define **qué se hace con ese tiempo**. Es el motor de comportamiento autónomo.

## La Dual Task Queue
El corazón del comportamiento es una cola de tareas bifurcada:

### 1. User Mission Queue (Prioridad P0)
- Tareas explícitamente solicitadas por T1 (Alfredo).
- Ejecución síncrona o asíncrona según el requerimiento.
- Consumen el 100% de la capacidad de procesamiento cuando están activas.

### 2. Self-Evolution Queue (Prioridad P1-P3)
- Tareas propias generadas por el Monstruo.
- Se ejecutan en "tiempo muerto" (cuando la User Mission Queue está vacía o bloqueada esperando input).
- Ejemplos de tareas propias:
  - Auditar thread archives por inconsistencias.
  - Detectar drift entre código y documentación.
  - Actualizar el Oráculo de IAs con nuevos modelos.
  - Consolidar pericia en los Embriones Peritos.
  - Preparar el Daily Brief para T1.

## Economía de Potencia (Absorción de Reactor Soberano)
El comportamiento se evalúa usando la métrica PAU (Potencia Autónoma Útil).
El Reactor de Vigilia busca maximizar la PAU:
`PAU = (valor generado × reusabilidad) - (fricción + atención humana consumida)`
Una tarea de Self-Evolution solo es válida si incrementa la PAU futura (ej. mejorar un prompt reusable) sin consumir atención humana presente.

## Protocolo de Intervención Viva
T1 no necesita matar el proceso para alterar el comportamiento. T1 inyecta eventos de alta prioridad en la cola:
- `PAUSE`: Congela los loops actuales.
- `REDIRECT`: Cambia el objetivo de la misión en vuelo.
- `FORCE_AUDIT`: Pausa ejecución y genera reporte de estado inmediato.
