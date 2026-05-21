# SPRINT COMPILER v0.1

**Loop Owner:** `loop_sprint_compiler`
**Action Class:** A3_CREATE_NON_PRODUCTIVE_ARTIFACT

## Objetivo
Tomar los `sprint_candidates` generados por el Oráculo v0.4 y compilarlos en `Sprint Drafts` altamente estructurados y listos para ser ejecutados por los agentes (Manus/loops).

## Funciones
1. Extraer los Top 3 `sprint_candidates` del output del Oráculo.
2. Formatear cada candidato según el esquema de `Sprint Draft`.
3. Guardar los drafts en `bridge/sprint_compiler/compiled_sprints/`.
4. Los drafts generados **NO** están firmados, **NO** son canon, y **NO** se ejecutan automáticamente. Son propuestas listas para la decisión de T1.

## Reglas de Compilación
Cada Sprint Draft debe incluir obligatoriamente:
- **Objective:** Qué se va a lograr.
- **Scope:** Límites de la implementación.
- **Allowed Files:** Qué archivos se pueden crear/modificar.
- **Forbidden Files:** Qué archivos NO se pueden tocar (ej. `main`, `APP_VISION.md`).
- **Expected Artifacts:** Entregables tangibles (código, tests, reportes).
- **Tests:** Criterios de validación automatizada.
- **Gates:** Puntos de control o validación manual.
- **Rollback:** Plan de reversión en caso de fallo.
- **T1 Decision Needed:** Qué debe aprobar T1 antes de ejecutar.
- **No-Go List:** Qué acciones provocarían un aborto inmediato.
- **Estimated Cost:** Presupuesto asignado.
- **Definition of Done:** Criterios de éxito para cerrar el sprint.

## Restricciones
- El Sprint Compiler **NUNCA** crea Documentos de Sistema Canonizados (DSC).
- El Sprint Compiler **NUNCA** abre Pull Requests.
- El Sprint Compiler **NUNCA** ejecuta el código o el sprint compilado.
