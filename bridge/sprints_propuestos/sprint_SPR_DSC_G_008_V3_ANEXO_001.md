# Sprint SPR-DSC-G-008-V3-ANEXO-001 — Anexo audit Cowork para missions y embrion_patches

**Estado:** PROPOSED
**Fecha de propuesta:** 2026-05-28
**Paradigm:** governance
**Capa:** C0
**Origen ejecutivo:** Derivado natural de T1-006 D + T1-007 C (PR #231 SHA `736b47e`)

**Objetivo:** Extender el scope de Cowork audit (DSC-G-008 v2) para cubrir las dos nuevas zonas operativas canonizadas: `bridge/missions/` y `bridge/embrion_patches/`.

## Tareas

1. Redactar anexo `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC_G_008_V3_ANEXO_MISSIONS_PATCHES.md`.
2. Update `DSC_G_008_V2.md` con nota referenciando el anexo.
3. Crear `tools/cowork_audit_checklist_v3.md` con checklist operativa.
4. Update README de `bridge/missions/` y `bridge/embrion_patches/`.
5. Coordinar firma con Cowork (Hilo A).

## Objetivos maestros tocados

- **OM-1** Soberanía operativa (Cowork audita capa viva, no solo PRs)
- **OM-9** Observabilidad ejecutable (audit de evidencia binaria)

## Alcance

DSC-G-008 v2 (vigente) define que Cowork audita **contenido** de archivos nuevos/modificados antes de declarar verde un sprint. La canonización de `bridge/missions/` (T1-007 C) y `bridge/embrion_patches/` (T1-006 D) crean dos nuevas zonas operativas que DSC-G-008 v2 no contempla explícitamente.

Este anexo extiende el scope de Cowork audit:

1. Para sprints que crean carpetas en `bridge/missions/SPR-*/`: Cowork audita los 7 directorios canónicos completos antes de declarar verde.
2. Para PRs que aplican parches en `bridge/embrion_patches/*/APPLIED/`: Cowork audita el patch original + el diff aplicado + el rationale.

### Entregables

1. Doc anexo: `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC_G_008_V3_ANEXO_MISSIONS_PATCHES.md`
2. Update `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC_G_008_V2.md` con referencia al anexo (no rewrite, solo nota).
3. Checklist Cowork audit: `tools/cowork_audit_checklist_v3.md`.
4. Update README de `bridge/missions/` y `bridge/embrion_patches/` con la nueva regla.

### Ejecutor sugerido

Manus B (cuenta `manus_b`) en sesión limpia. Doc-only. Riesgo bajo.

### Pre-requisitos

- T1-006 EMBRION-PATCHES-001 y T1-007 MISSIONS-CONSOLIDATOR-001 al menos en estado PROPOSED.
- Cowork (Hilo A) acepta el scope expandido.

### Estimación

~250 LOC markdown + 0 LOC código. ~3 horas de trabajo.

## Criterios de cierre

- Anexo DSC-G-008 v3 publicado.
- DSC-G-008 v2 referencia anexo.
- Checklist tools/cowork_audit_checklist_v3.md activo.
- READMEs de bridge/missions/ y bridge/embrion_patches/ actualizados.
- Cowork firma activacion.

## Cierre

Mover a `bridge/sprints_completados/`, registrar en `registry.yaml` con `aliases: [DSC-G-008-V3-ANEXO-001]`. Activación inmediata sobre `bridge/missions/` y `bridge/embrion_patches/`.
