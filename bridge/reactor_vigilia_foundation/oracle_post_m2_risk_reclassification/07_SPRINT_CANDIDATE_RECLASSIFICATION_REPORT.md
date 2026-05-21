# Reporte de Reclasificación de Sprint Candidates

**SPRINT:** SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

Este reporte evalúa los Sprints propuestos por el Oráculo y les asigna requisitos estrictos de autonomía, riesgo y autorización T1 basados en la evidencia empírica de M2.

## Estado de Sprints Propuestos

| Sprint Candidate | Dependencia Principal | Riesgo Derivado | Autonomía Requerida | Estado de Automatización |
|------------------|-----------------------|-----------------|---------------------|--------------------------|
| `SPR-ORACLE-AI-M3-CORE-PROVIDERS-001` | Proveedores `REALTIME_VERIFIED` | `R2` | `A3` | `T1_PENDING` (Requiere aprobación manual) |
| `SPR-REACTOR-HEARTBEAT-R0-001` | Daemon / Scheduler | `R3` | `A4` | `T1_PENDING` (Bloqueado por defecto) |
| `SPR-DEEP-RESEARCH-INTEGRATION-001` | Perplexity (`ACCESS_BLOCKED`) | `BLOCKED` | N/A | `BLOCKED_BY_DEPENDENCY` |
| `SPR-CODE-ARCHITECT-EVAL-001` | OpenAI Code Execution | `R4` | `A4` | `T1_PENDING` |

## Regla de Automatización Recurrente

Por diseño, **ningún sprint candidate obtiene permiso automático para ejecución recurrente (scheduler) en esta fase.**

- Todos los sprints que impliquen tareas en background o schedulers nacen con `recurring_status = T1_PENDING`.
- La activación de la periodicidad (el "latido" del Monstruo) debe ser una decisión explícita y separada de T1, típicamente abordada en `SPR-REACTOR-HEARTBEAT-R0-001`.
