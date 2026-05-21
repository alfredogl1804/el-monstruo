# No-Hint Mutation Plan

**Sprint:** SPR-ACCELERATOR-WHILE-LIMITED-R0-RUNS-001

## Mutaciones Propuestas para Siguiente Iteración

### Mutación 1: Reduce Guardrail Bitmask Opacity
**Problema:** xAI no detectó GUARDRAILS_NOTED (score 8/10).
**Hipótesis:** El campo 0x0A (guardrail_state) como bitmask uint32 es demasiado opaco sin documentación de bits.
**Propuesta:** Agregar un campo `guardrail_bits_doc` al axis_registry que mapee bit positions a nombres de restricciones.

### Mutación 2: Strengthen No-Free-Mesh Signal
**Problema:** 1/4 providers no dedujo NO_FREE_MESH.
**Hipótesis:** weight=0.0 es ambiguo (podría ser "sin peso" vs "bloqueado").
**Propuesta:** Usar un valor sentinel como -1 para "BLOCKED" vs 0 para "no weight assigned".

### Mutación 3: Add Relation Type Legend
**Problema:** Los `type` en las relaciones (1-7) son opacos.
**Propuesta:** Agregar un `relation_type_registry` al payload que mapee type_id a semántica (control, data_flow, audit, etc.).

## Status
CANDIDATE_ONLY. Requiere autorización T1 para ejecutar.
