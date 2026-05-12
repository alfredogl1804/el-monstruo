# Reporte T6: Audit de Specs Legacy (DSC-G-008 v2 Backfill)

**Fecha:** 2026-05-12
**Ejecutor:** Hilo Catastro
**Sprint:** S-CONTRATOS-001

## Resumen Ejecutivo

Se ejecutó `tools/spec_lint.py` sobre los 57 specs existentes en `bridge/sprints_propuestos/` y `bridge/cowork_to_manus_*.md`.

**Resultado:** 133 errores de estructura, 70 warnings (principalmente `perfil_riesgo` faltante).

## Hallazgos Principales

1. **Estructura ausente:** La gran mayoría de los specs de Cowork a Manus (ej. `cowork_to_manus_SESION_*.md`, `cowork_to_manus_URGENT_*.md`) carecen de la estructura canónica requerida por DSC-G-008 v2 (Estado, Objetivo, Tareas, Criterios de Cierre).
2. **Perfil de Riesgo:** 70 warnings indican que las tareas dentro de los specs no declaran el `perfil_riesgo` obligatorio (read-only, write-safe, write-risky, requiere-coordinacion-humana) dictado por DSC-G-012.
3. **Contratos Ejecutables:** Varios specs mencionan producir DSCs pero omiten la sección `## Contratos ejecutables` exigida por DSC-G-017.

## Estrategia de Backfill Recomendada

Dado el volumen masivo (57 specs afectados), un backfill manual bloqueante paralizaría la ejecución. Se recomienda:

1. **Amnistía Legacy:** Declarar los 57 specs actuales como "legacy" y eximirlos de la validación estricta de `spec_lint.py`.
2. **Enforcement Futuro:** Activar el pre-commit hook `dsc-contract-check` (T5) para rechazar cualquier **nuevo** spec o modificación que no cumpla con DSC-G-008 v2, DSC-G-012 y DSC-G-017.
3. **Backfill Oportunista:** Si un hilo debe modificar un spec legacy para una tarea, está obligado a "limpiarlo" y adaptarlo a la norma antes de hacer commit.

Esta estrategia (amnistía + enforcement estricto futuro) es coherente con el principio de "No detener el progreso por deuda técnica del pasado, pero no permitir nueva deuda".
