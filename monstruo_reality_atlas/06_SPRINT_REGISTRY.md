# 06 — SPRINT REGISTRY

**Este archivo es un agregador delgado. La fuente primaria de sprints está en el Context Fabric.**

---

## Fuente primaria

- **`interfaces_context_fabric/maps/SPRINT_REGISTRY.yaml`** (131 líneas, formato YAML estructurado)
- **`interfaces_context_fabric/context_packs/PACK_08_SPRINTS_PENDIENTES.md`** (sprints UI pendientes con prosa densa)
- **`interfaces_context_fabric/maps/DECISIONS_PENDING_T1.yaml`** (decisiones T1 magna que destraban sprints)

URL verificable:
https://github.com/alfredogl1804/el-monstruo/blob/interfaces-context-fabric-001/interfaces_context_fabric/maps/SPRINT_REGISTRY.yaml

ChatGPT y cualquier sabio que necesite el estado de sprints debe consultar el fabric.

## Qué agrega el Reality Atlas sobre los sprints del fabric

El Reality Atlas no duplica el catálogo de sprints. Lo que aporta es la **vista cruzada con realidad de código y producción**: el archivo `maps/07_SPRINT_TO_CODE_MAP.md` (que se construye en este atlas) mapea cada sprint propuesto al directorio o archivo del repo que ese sprint debería modificar, y al servicio en producción que ese sprint impactaría. Esta vista cruzada no existe en el fabric.

## Sprint en vuelo activo al cierre de iter 001 atlas

Al momento de cierre de esta iteración del atlas (2026-05-17), hay un sprint en vuelo: **`la-forja-001-d4`**. Es la rama actual checked out en el disco del Mac. Implementa Google OAuth + JWT session backend. DSC asociado: DSC-LF-008.

Este sprint NO está documentado en el fabric porque el fabric cierra antes del 12-may. El Reality Atlas lo captura como dato de realidad presente.

## Sprints completados al 2026-05-17

- **Memento Protocol implementación** (referenciado en SRC-008, código en `kernel/memento/`).
- **Sprint S001 hardening seguridad** (postmortem P0, originó AGENTS.md Regla 6). DSC-S-001 a DSC-S-008.

## Sprints propuestos sin firma

La cola de 14 sprints propuestos sin firma se documenta en el fabric. Los más críticos por destrabar bloques completos son: `CRONOS_1`, `CRONOS_2`, `CRONOS_3`, `AUTH_TIERS_001` (Shamir), `MOBILE_1B_A2UI_IMPLEMENTATION`, `SPR-BRAND-001` (resuelve drift binario), `SPR-CAP-001`, `SPR-SMP-001`, `SPR-DAILY-001`, `SPR-COCKPIT-001`, `SPR-TOGGLE-001`, `SPR-COMMAND-CENTER-EXT`, `SPR-MEMENTO-EXT`, `SPR-EMBRION-CRONOS-001`. Detalle completo en el fabric.

## Sprints que NO existen pero deberían (gap detectado por el Reality Atlas)

Son tres sprints que ningún agente ha propuesto formalmente y que el atlas detecta como necesarios. El primero es un sprint de **reconciliación drift Command Center** que documente formalmente las 5-8 superficies faltantes (12-15 canon menos las 7 actuales). El segundo es un sprint de **canonización Schema-First** dado que es Capa 03 emergente del fabric pero no tiene sprint asociado. El tercero es un sprint de **implementación SMP código** completo (SPR-SMP-001 propuesto solo cubre el inicio).

Estos tres se elevan en `09_GAPS_AND_UNKNOWN_UNKNOWNS.md` como gap operativo.

## Prioridad para firma T1 magna

Si Alfredo decide firmar sprints en orden de impacto destrabador, la prioridad recomendada por el atlas es:

| Prioridad | Sprint | Destraba |
|---|---|---|
| 1 | `CRONOS_1` | CRONOS_2, CRONOS_3, SPR-MEMENTO-EXT, SPR-EMBRION-CRONOS-001 |
| 2 | `AUTH_TIERS_001` (Shamir) | Habilita Modo Cripta legado familiar |
| 3 | `MOBILE_1B_A2UI_IMPLEMENTATION` | SPR-DAILY-001, SPR-COCKPIT-001 |
| 4 | `SPR-BRAND-001` | Resuelve drift binario |
| 5 | `SPR-CAP-001` | Inicia capabilities transversales |

---

*Procedé con `07_ALIAS_LEDGER.yaml`.*
