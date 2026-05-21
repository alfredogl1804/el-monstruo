# 06 SHELL RESEARCH PARKING LOT

## Estado
- RESEARCH_R0_CONCEPT
- DOCTRINE_CANDIDATE
- NO CRITICAL PATH

## Clasificación
SHELL (Micropolvo Semántico) no es infraestructura core (como Vigilia Sincrónica) ni comportamiento core (como Reactor de Vigilia). Es una **optimización de canal**.

## Decisión de Prioridad
1. No se bloqueará el desarrollo de la Vigilia Sincrónica esperando a que SHELL funcione.
2. El MVP de Vigilia Sincrónica usará JSON/YAML estructurado a través del State Fabric.
3. SHELL queda estacionado como un "Research R0" que puede correr en paralelo sin afectar la ruta crítica.

## Condiciones para retomar SHELL
- Cuando el tamaño del State Fabric cause latencia inaceptable en el Handoff Protocol.
- Cuando el costo de tokens de contexto entre loops supere el presupuesto.
- Cuando tengamos un framework algorítmico capaz de decodificar micropartículas semánticas de manera determinista (benchmark 50k funcional).
