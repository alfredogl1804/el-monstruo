# Sprint Registry Schema — Fuente Única de Verdad

## Propósito

`sprints/registry.yaml` en `main` del repo `el-monstruo` es la **única fuente de verdad** sobre qué sprints existen, su estado y su metadata. Cualquier otra fuente (archivos `.md`, fabric YAMLs, scripts hardcoded) es **derivada o histórica**, nunca autoritativa.

## Reglas duras

1. **Un sprint, un ID, un solo lugar.** El registry mantiene un único entry por sprint. Los archivos `.md` son opcionales y se referencian por path.
2. **Identificadores canónicos en `SCREAMING_SNAKE_CASE`.** Nada de mezclar guiones y underscores. Migración normaliza una sola vez.
3. **Estado único.** Un sprint está en exactamente un estado del enum, sin ambigüedad.
4. **CI valida consistencia.** Cada PR que toque sprints debe actualizar el registry; si no, falla.

## Schema YAML

```yaml
version: 1
generated_at: "2026-05-26T15:00:00Z"
sprints:
  - id: MOBILE_REALIGNMENT_001                    # SCREAMING_SNAKE_CASE, único
    title: "Mobile Realignment - Forja Theme"     # Human-readable
    status: COMPLETED                              # enum estricto
    paradigm: transversal                          # enum: transversal | acto_1_pantallas | acto_2_calm_tech | capa_transversal_comercial | vanguardia_perpetua | obsoleto_pendiente_decision
    objetivos_maestros: [10]                       # lista de enteros 1-15
    capas_transversales: []                        # lista de C1-C8
    priority: P1                                   # enum: P0 | P1 | P2 | P3 | BACKLOG
    eta_days: 5                                    # null si no estimado
    owner: "Hilo B"                                # texto libre
    path: "bridge/sprints_completados/sprint_mobile_realignment_001.md"  # null si no tiene .md
    pr_merged: 114                                 # null si no mergeado
    completed_at: "2026-05-12T18:30:00Z"           # null si no completado
    bloquea_a: []                                  # lista de IDs de otros sprints
    bloqueado_por: [T1_MAGNA_001]                  # lista de decisiones T1 o sprints
    aliases:                                       # IDs alternos que apuntaban al mismo sprint
      - MOBILE-REALIGNMENT-001
      - mobile_realignment_001
    notes: "Theme cyan/púrpura corregido a Forja Industrial."
```

## Enum `status`

| Estado | Descripción | Visualización en Tablero |
|---|---|---|
| `PROPOSED` | Borrador, no firmado por T1/T2 | Backlog rojo apagado |
| `SIGNED` | Firmado por T1 magna o por contrato canónico, listo para ejecutar | Backlog ámbar |
| `IN_PROGRESS` | En ejecución activa (rama abierta, PR draft) | WIP cian |
| `BLOCKED` | Bloqueado por decisión T1 magna pendiente o por dependencia | Rojo intenso |
| `COMPLETED` | Mergeado a main, validado | NO aparece en backlog (vive en otros distritos como código real) |
| `CANCELLED` | Descartado tras decisión doctrinal o reemplazado | NO aparece en Tablero |

## Reglas de transición de estado

- `PROPOSED` → `SIGNED` (firma T1 magna o por contrato existente)
- `SIGNED` → `IN_PROGRESS` (cuando se abre rama de trabajo)
- `IN_PROGRESS` → `COMPLETED` (cuando PR mergea a main)
- `*` → `BLOCKED` (cuando se descubre dependencia bloqueante)
- `BLOCKED` → estado previo (cuando se desbloquea)
- `*` → `CANCELLED` (decisión explícita firmada)

## Validaciones obligatorias

1. `id` único en todo el registry.
2. `status` en el enum.
3. `paradigm` en el enum.
4. `objetivos_maestros` ⊆ {1..15}.
5. Si `status == COMPLETED`, debe haber `pr_merged` o `completed_at`.
6. Si `status == BLOCKED`, debe haber al menos un entry en `bloqueado_por`.
7. Si `path` no es null, el archivo debe existir en main.
8. `aliases` no puede contener el `id` propio.
9. Sin `aliases` repetidos entre sprints.

## Migración inicial: política de deduplicación

Cuando dos fuentes apuntan al mismo sprint con IDs ligeramente distintos:

1. **Normalizar**: uppercase, `-` → `_`, eliminar prefijos `SPRINT_` o `SPEC_`.
2. **Match exacto** post-normalización → mismo sprint, archivos en `sprints_completados/` ganan sobre los demás (tienen evidencia de cierre).
3. **Match parcial** (similitud > 85%) → reportar conflicto en `migration_conflicts.md`, no auto-resolver.
4. **Sufijos especiales** como `_cierre`, `_KICKOFF`, `_v1`, `_FIRMADO`: tratarlos como **mismo sprint** (un sprint puede tener varios archivos de fase).

## CI Workflow

`.github/workflows/sprint-registry-validate.yml`:

- Trigger: PR que toque `bridge/sprints_*` o `sprints/registry.yaml`.
- Pasos:
  1. Lint del YAML (schema check con jsonschema).
  2. Validación de unicidad de IDs.
  3. Verificación de paths referenciados.
  4. Verificación de aliases sin colisiones.
  5. Si el PR agrega/mueve archivos `.md` sin actualizar el registry → falla.

## Reescritura de `build_board_data.py`

- Nueva función `_load_sprint_registry()` que parsea `sprints/registry.yaml` del mount FUSE.
- `project_canonical_backlog_sprints()` ahora itera SOLO sprints con `status in {PROPOSED, SIGNED, BLOCKED}`.
- `IN_PROGRESS` proyectados como WIP.
- `COMPLETED` y `CANCELLED` ignorados en backlog (siguen visibles en otros distritos por su contenido real).
- Eliminado `_FALLBACK_BACKLOG_SPRINTS` por completo.
