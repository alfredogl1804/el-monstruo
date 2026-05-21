# 04 STATE FABRIC SINGLE WRITER

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## El Problema del Estado Distribuido
En un sistema con múltiples loops efímeros (Vigilia Sincrónica), si cada loop mantiene su propia versión de la realidad, el sistema sufre de "Split-Brain" y "Dory Distribuido". 

## La Solución: State Fabric Single-Writer
El State Fabric es el único repositorio autorizado del estado actual del Monstruo.

### Principios de Diseño
1. **Single-Writer por Dominio:** Solo un loop (o el Dispatcher) puede tener el *lock* de escritura para una sección específica del State Fabric en un momento dado.
2. **Lectura Universal:** Todos los loops activos pueden leer el State Fabric completo al nacer (Boot Context).
3. **Estructura Estricta:** No es un chat o un log de texto libre. Es un árbol de estado estructurado (JSON/YAML) que define:
   - Misión actual.
   - Restricciones activas.
   - Descubrimientos recientes.
   - Bloqueos.

### El Handoff Protocol
Cuando un loop termina su ciclo de vida (TTL expirado o tarea completada):
1. El loop solicita el lock de escritura.
2. Escribe su "Delta de Estado" (qué cambió, qué aprendió, dónde se quedó).
3. Libera el lock.
4. Muere.

El siguiente loop instanciado por el Dispatcher lee el State Fabric actualizado, garantizando la ilusión de una conciencia operativa ininterrumpida para T1.
