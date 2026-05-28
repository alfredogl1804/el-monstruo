# Sprint SPR-T1-007-MISSIONS-CONSOLIDATOR-001 — Consolidador de bridge/missions/

**Estado:** PROPOSED
**Fecha de propuesta:** 2026-05-28
**Paradigm:** tooling + governance
**Capa:** C0 + C2
**Origen ejecutivo:** T1-MAGNA-007 Opción C firmada (PR #231 SHA `736b47e`)

**Objetivo:** Implementar el consolidador de `bridge/missions/` firmado en T1-MAGNA-007 C: verifica integridad estructural de cada misión y bloquea merge a main si la evidencia está incompleta.

## Tareas

1. Implementar `tools/missions_consolidator.py` (verifica 7 directorios canónicos por misión).
2. GitHub Action o git pre-merge hook que invoca consolidador.
3. Implementar `tools/missions_lint.py` (linter markdown CLI).
4. Tests con fixtures de misiones válidas/inválidas.
5. Doc formal `docs/BRIDGE_MISSIONS_PROTOCOL.md`.
6. Activación con label `mission-required` en sprints aplicables.

## Objetivos maestros tocados

- **OM-1** Soberanía operativa (capa de ejecución viva canonizada)
- **OM-3** Reuso jerárquico (`registry.yaml + bridge/missions/ + sprints_completados/` coexisten sin solapar)
- **OM-9** Observabilidad ejecutable (cada misión deja artefactos firmados)

## Alcance

Implementar la doctrina T1-007 C que canonizó `bridge/missions/` como capa viva. Falta el **consolidador** que verifica que misiones no se quedan huérfanas y que su evidencia se cierra antes de permitir merge a main.

### Entregables

1. `tools/missions_consolidator.py` — verifica integridad de `bridge/missions/SPR-*/`: existen los 7 directorios canónicos, `0_intent.md` válido, `6_outcomes.md` cerrado si el sprint está COMPLETED.
2. `.git/hooks/pre-merge` (o GitHub Action) que llama al consolidador y bloquea merge si una misión está incompleta.
3. `tools/missions_lint.py` — linter de markdown de misiones (CLI).
4. Tests: fixtures de misiones válidas/inválidas.
5. Doc: `docs/BRIDGE_MISSIONS_PROTOCOL.md` con el contrato completo (ya hay README v1, falta protocol formal).

### Ejecutor sugerido

Manus B (cuenta `manus_b`) en sesión limpia. Python + CI. Riesgo medio (toca CI).

### Pre-requisitos

- Cowork audita pre-arranque (DSC-G-008 v2).
- Coordinar con DSC-G-008 v3 anexo (extiende audit Cowork a `bridge/missions/`).

### Estimación

~400 LOC Python + ~100 LOC YAML CI + ~120 LOC tests + ~80 LOC docs. 1 día.

## Criterios de cierre

- Consolidador y linter pasan tests con fixtures.
- GitHub Action o git hook activado en repo.
- Doc protocol publicado.
- Cowork audit verde.
- Label `mission-required` aplicado a sprints aplicables.

## Cierre

Mover a `bridge/sprints_completados/`, registrar en `registry.yaml` con `aliases: [T1-007-MISSIONS-CONSOLIDATOR-001]`. Activar pre-merge hook con label `mission-required` para sprints que crean carpeta en `bridge/missions/`.
