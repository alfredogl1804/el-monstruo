# Sprint SPR-T1-006-EMBRION-PATCHES-001 — Embrión Sandbox Patches

**Estado:** PROPOSED
**Fecha de propuesta:** 2026-05-28
**Paradigm:** kernel + tooling
**Capa:** C0 + C2
**Origen ejecutivo:** T1-MAGNA-006 Opción D firmada (PR #231 SHA `736b47e`)

**Objetivo:** Implementar el protocolo Embrión Sandbox Patches firmado en T1-MAGNA-006 D: el embrión NO crea PRs autónomos; emite patches estructurados que un humano revisa y aplica.

## Tareas

1. Definir `schemas/embrion_patch.schema.json` (action, target_path, diff, rationale, blast_radius, signature).
2. Implementar `tools/embrion_patch_writer.py` (script que el embrión llama).
3. Implementar `tools/embrion_patch_reviewer.py` (CLI interactivo humano).
4. Crear `bridge/embrion_patches/README.md` con doctrina ciclo de vida.
5. Tests: golden patches + smoke aplicar/rechazar.
6. Doc `docs/EMBRION_PATCH_PROTOCOL.md` con contrato completo.

## Objetivos maestros tocados

- **OM-3** Reuso jerárquico (cero PRs autónomos del embrión)
- **OM-9** Observabilidad ejecutable (patches auditables)
- **OM-12** Soberanía operativa (sandbox patches en lugar de PRs ciegos)

## Alcance

Implementar la decisión D firmada de T1-006: el embrión NO crea PRs directos; en su lugar emite **sandbox patches** estructurados en `bridge/embrion_patches/` que un operador humano (Manus B o Cowork) revisa y aplica.

### Entregables

1. `tools/embrion_patch_writer.py` — script que el embrión ejecuta para emitir un patch (no commit, no PR).
2. `schemas/embrion_patch.schema.json` — schema canónico de un sandbox patch (action, target_path, diff, rationale, blast_radius, signature).
3. `tools/embrion_patch_review
er.py` — script que un humano ejecuta para revisar/aplicar/rechazar un patch (interactivo CLI).
4. `bridge/embrion_patches/README.md` — doctrina: ciclo de vida (PROPOSED → REVIEWED → APPLIED | REJECTED).
5. Tests: golden patches + smoke de aplicar/rechazar.
6. Doc: `docs/EMBRION_PATCH_PROTOCOL.md` con el contrato completo.

### Ejecutor sugerido

Manus B (cuenta `manus_b`) en sesión limpia. Backend Python + scripts. Bajo riesgo (NO toca embrión runtime, solo agrega capa).

### Pre-requisitos

- Cowork audita el schema antes de implementar (DSC-G-008 v2).
- Coordinación con DSC-G-008 v3 anexo (sub-sprint independiente que extiende audit a `bridge/embrion_patches/`).

### Estimación

~600 LOC Python + ~150 LOC tests + ~80 LOC docs. 1 día.

## Criterios de cierre

- Schema embrion_patch.schema.json firmado.
- Writer y reviewer tests pasan en CI.
- README + protocol doc publicados.
- Cowork audit verde.
- Activacion solo despues de DSC-G-008 v3 mergeado.

## Cierre

Mover a `bridge/sprints_completados/`, registrar en `registry.yaml` con `aliases: [T1-006-EMBRION-PATCHES-001]`. Activar el flujo en producción solo cuando DSC-G-008 v3 esté mergeado.
