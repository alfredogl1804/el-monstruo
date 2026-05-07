---
id: DSC-S-005
proyecto: GLOBAL
tipo: politica
titulo: "Default a archive antes que delete — reversibilidad > expediencia para cleanup de namespace."
estado: firme
fecha: 2026-05-06
fuentes:
  - repo:bridge/sprints_propuestos/sprint_88_cierre_v1_producto.md (task 3.B.1 cleanup repos GitHub Pages)
  - chat:cowork-manus-2026-05-06 (decisión Opción D archive en lugar de delete cuando GitHub bloqueó por scope)
cruza_con: [DSC-S-001, DSC-G-008]
---

# Default a Archive Antes que Delete

## Decisión

Cuando se hace cleanup de namespace (repos, branches, tablas DB, archivos, env vars, jobs, pipelines), el default es **archive** — no delete. Delete solo después de archive + 30 días de monitoreo + scope ampliado explícitamente + confirmación humana.

Aplica a cualquier operación destructiva sobre recursos del ecosistema El Monstruo.

## Por qué

Detonado por Sprint 88 task 3.B.1 (cleanup repos GitHub Pages acumulados). El plan original era delete de 7 repos. Manus encontró que el token `gh` no tenía scope `delete_repo`, lo cual requería browser flow de Alfredo + ampliación de scope. Cowork propuso `gh repo archive` como alternativa, que cumple el mismo objetivo (limpiar namespace) sin requerir scope nuevo y siendo reversible.

Esa decisión expuso un principio general aplicable más allá del caso específico: **reversibilidad > expediencia**. Deletes irreversibles solo cuando hay certeza absoluta y registro forense completo. Archive permite rollback sin coordination cost.

## Reglas

### Operaciones que aplican

| Operación | Default | Delete después de |
|---|---|---|
| Repos GitHub | `gh repo archive` | 30 días sin uso + scope `delete_repo` + confirmación humana |
| Branches git | `git branch -m old-* archive/old-*` (rename a prefix) | 90 días sin merge needed + revisión |
| Tablas Supabase / Postgres | `ALTER TABLE x RENAME TO archived_x_<date>` | 90 días sin queries + DROP supervisado |
| Archivos en disco | `mv file file.archived.<timestamp>` o move a `archived/` directory | 30 días sin lectura + audit forense |
| Env vars Railway | rename a `<NAME>_DEPRECATED_<date>` | 30 días + servicio sin errores |
| Cron jobs / Background tasks | disable (no remove) | 30 días sin necesidad |
| Pipelines / Workflows | rename + disable | 30 días sin trigger needed |

### Excepciones (delete inmediato permitido)

Solo en estos casos delete sin pasar por archive:

1. **Datos personales bajo GDPR / CCPA right-to-delete** — confirmación legal + audit log.
2. **Secrets expuestos** — rotar + delete del valor viejo (NO archive del secret en plaintext).
3. **Tests temporales con prefijo claro** (`test_*`, `tmp_*`, `playground_*`) creados específicamente para descartar después — pueden delete sin archive.
4. **Recursos creados por error** (typo, equivocación) y removidos en la misma sesión — delete OK si nunca se usaron en producción.

### Snapshot forense obligatorio antes de cualquier cleanup

Aunque sea archive (no delete), antes de la operación crear registro auditable:

```markdown
## Snapshot forense — cleanup <descripción>
**Fecha:** YYYY-MM-DD
**Operación:** archive | delete
**Quién:** Manus | Cowork | Alfredo
**Recursos:** [lista exacta]
**Razón:** [por qué se hace cleanup]
**Reversible:** sí (archive) | no (delete)
**Plazo de delete tras archive:** N días
```

Pushear el snapshot al bridge (`bridge/snapshots_cleanup_<fecha>.md`) ANTES de ejecutar la operación.

## Implicaciones

- **Sprint 88 task 3.B.1** se ejecuta con `gh repo archive` (no delete). Repos archivados quedan listados con estado archived; pueden eliminarse en 30 días tras audit final.
- **Cleanup de memory tables (Sprint S-001 tarea S-1.3)** sigue el mismo principio: filas con secrets se sanitizan (UPDATE) en lugar de delete (DELETE) cuando posible. Si delete es necesario, primero crear `archived_thoughts` con copy.
- **Schema migrations** que eliminan tablas/columnas: archive primero (rename con prefix `archived_`), DROP en migración separada 30 días después tras confirmación de que ningún código las usa.
- **Cleanup de scripts en repo** (Sprint S-001 puede borrar scripts viejos): mover a `scripts/archived/` primero, delete físico en sprint posterior.

## Beneficios operativos

1. **Reversibilidad sin coordination cost.** Un archive accidental se revierte en 1 comando. Un delete accidental requiere recuperación desde GitHub support (90 días) o backup (no garantizado).
2. **Auditoría forense.** Recursos archivados quedan inspeccionables — útil si después se descubre que tenían información necesaria.
3. **Reduce scope de permisos.** Archive típicamente requiere scope menor que delete (ej: `gh repo archive` necesita solo `repo`, mientras que `gh repo delete` necesita `delete_repo`). Menos permisos = menor superficie de ataque si el token se filtra.
4. **Fricción positiva para deletes intencionales.** El paso extra de "archive primero, delete después" da tiempo para detectar errores antes de que sean irreversibles.

## Estado de validación

firme — fruto de la decisión operativa Sprint 88 task 3.B.1 del 2026-05-06, cuando bloqueó por scope `delete_repo` y Cowork propuso archive como alternativa equivalente. Política generalizada por Cowork al detectar el principio subyacente (reversibilidad > expediencia).
