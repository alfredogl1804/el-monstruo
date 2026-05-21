# INDEX MAESTRO: BATCH 006 + 007 (ANTI-DORY ACCELERATION)

## Estado Actual
- **Batch 006 (Apply/Merge Plan):** `DESIGN_READY`
- **Batch 007 (Canary Readiness):** `DESIGN_READY`

## Ramas y Commits (Batch 006)

| Célula | Módulo | Rama | Estado |
|---|---|---|---|
| **A** | Supabase Apply Plan | `control-tower/2026-05-20-batch-006-apply-plan` | Documentado |
| **B** | Merge Plan | `control-tower/2026-05-20-batch-006-merge-plan` | Documentado |
| **C** | Post-Merge Test Matrix | `control-tower/2026-05-20-batch-006-post-merge-tests` | Documentado |
| **D** | Rollback Plan | `control-tower/2026-05-20-batch-006-rollback-plan` | Documentado |

## Ramas y Commits (Batch 007)

| Célula | Módulo | Rama | Estado |
|---|---|---|---|
| **E** | Mini Bench 100 Cases | `control-tower/2026-05-20-batch-007-mini-bench` | Documentado |
| **F** | Hidden Fixtures Design | `control-tower/2026-05-20-batch-007-hidden-fixtures` | Documentado |
| **G** | CVDS Smoke Methodology | `control-tower/2026-05-20-batch-007-cvds-smoke` | Documentado |
| **H** | Canary Readiness Gate | `control-tower/2026-05-20-batch-007-canary-readiness` | Documentado |
| **I** | Index Maestro | `control-tower/2026-05-20-batch-006-007-index` | Documentado |

## Decisiones T1 Incorporadas
- Se prioriza un mega-PR de integración para Batch 005 en lugar de merges aislados.
- Se asume un FPR (falsos positivos) tolerable en Fase 1 (< 10%) a favor de la seguridad.
- Los Hidden Fixtures NUNCA tocarán el repositorio ni el chat.

## Qué Sigue Bloqueado (Requiere Firma T1 para Ejecución)
1. Ejecución del Merge Plan (Crear PR de Batch 005 a main).
2. Ejecución del Supabase Apply Plan (Migraciones 0050 y 0051).
3. Ejecución de la Matriz Post-Merge.
4. Ejecución del CVDS Smoke Test (Known Cases + Hidden Fixtures).
5. Activación de Fase 1 (Canary).

## Confirmaciones
- No apply ✅
- No main ✅
- No PR ✅
- No deploy ✅
- No Fase 1 ✅
- No Dory muerto ✅
- No R1 ✅
- No secrets expuestos ✅
- No paid APIs ✅
