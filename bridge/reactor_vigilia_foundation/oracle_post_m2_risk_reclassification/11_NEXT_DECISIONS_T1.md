# Próximas Decisiones (T1)

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Este documento es un resumen ejecutivo para T1 (Alfredo) tras la conclusión de la reclasificación post-M2.

## El Estado Actual
El Monstruo ha completado el ciclo de validación empírica:
1. **M1 (Catálogo):** Inventario teórico (Todo en `R0`).
2. **M2 (Probes):** Verificación real de que las APIs responden.
3. **Post-M2 (Este Sprint):** Asignación de riesgo operativo real (`R1-R4`) basado en la evidencia.

El sistema está listo para operar con estas APIs, pero **está intencionalmente pausado** esperando tus órdenes de automatización.

## Lo que necesitas decidir ahora (Ver `09_T1_DECISION_PACK.md`)

1. **Aprobar la Matriz Core:** ¿Confirmas que OpenAI, Anthropic y Gemini son la base (Core) del Monstruo?
2. **Resolver Bloqueos:** ¿Quieres inyectar llaves para Perplexity/DeepSeek ahora, o avanzamos sin ellos?
3. **El Latido (Scheduler):** ¿Autorizas la creación del daemon/cron para que el Monstruo ejecute tareas recurrentes en background?
4. **Persistencia (Supabase):** ¿Autorizas mover esta inteligencia desde archivos JSON a la base de datos Postgres para que otras UIs la consuman?

## Recomendación del Hilo
Mi recomendación es proceder con **SPR-REACTOR-HEARTBEAT-R0-001** para construir el scheduler. El Monstruo ya tiene "ojos" (APIs verificadas) y "cerebro" (Policy Engine + Risk Classification). Lo único que le falta para ser un agente autónomo es el "latido" (la capacidad de despertarse solo sin que tú corras un script).
