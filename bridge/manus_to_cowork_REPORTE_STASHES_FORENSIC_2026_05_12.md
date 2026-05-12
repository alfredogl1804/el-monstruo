# Reporte STASHES-FORENSIC-001

## §1 Resumen ejecutivo

| Clasificación | Cantidad |
|---|---|
| DROP_OBSOLETO | 8 |
| DROP_NOT_MINE | 7 |
| APPLY_DIRECTO | 1 |
| CHERRY_PICK_PARCIAL | 2 |
| REVIEW_MANUAL_REQUERIDO | 8 |
| DUPLICADO_DE_OTRO | 2 |
| **TOTAL** | **28** |

## §2 Matriz 28x7 completa

| # | branch_origen | mensaje | n_archivos | n_loc | clasificación | recomendación | razón |
|---|---|---|---|---|---|---|---|
| `stash@{0}` | `sprint/catastro-c-slice-0` | WIP catastro-c-slice antes de hilo-ejecu | 1 | 40 | **APPLY_DIRECTO** | Ejecutar git stash apply | Mi WIP de hoy (CATASTRO-C-SLICE-001) - memoria de cowork_estado_vivo |
| `stash@{1}` | `sprint/transversal-001-ca` | manus-audit-brief | 0 | 0 | **DROP_OBSOLETO** | Ejecutar git stash drop | Stash vacio (0 files), probablemente working tree limpio |
| `stash@{2}` | `sprint/transversal-001-ca` | manus-mv0018-recover | 1 | 10 | **REVIEW_MANUAL_REQUERIDO** | Revisión humana por T1/T2 antes de acción | Requiere inspección profunda del diff |
| `stash@{3}` | `fix/migration-0015-run-co` | manus-not-mine-found-on-main-2026-05-11 | 5 | 117 | **DROP_NOT_MINE** | Ejecutar git stash drop | Mensaje indica explícitamente trabajo de otro hilo |
| `stash@{4}` | `sprint/mobile-1b-a2ui-imp` | manus-sprint-mobile-1b-pre-handoff-2026- | 2 | 134 | **REVIEW_MANUAL_REQUERIDO** | Revisión humana por T1/T2 antes de acción | Archivos iOS pbxproj pre-handoff, riesgo de conflict |
| `stash@{5}` | `cowork/canonization-2026-` | WIP-pre-cowork-runtime-001-1778485869 | 43 | 13606 | **CHERRY_PICK_PARCIAL** | Extraer archivos específicos con git checkout stash@{N} -- <path> | 43 archivos de canonization, revisar qué MDs faltan en bridge/ |
| `stash@{6}` | `sprint/embrion-needs-002-` | WIP-not-mine-4-catastro-relap | 1 | 8 | **DROP_NOT_MINE** | Ejecutar git stash drop | Mensaje indica explícitamente trabajo de otro hilo |
| `stash@{7}` | `sprint/embrion-needs-002-` | WIP-not-mine-3-catastro | 1 | 113 | **DROP_NOT_MINE** | Ejecutar git stash drop | Mensaje indica explícitamente trabajo de otro hilo |
| `stash@{8}` | `sprint/embrion-needs-002-` | WIP-not-mine-2-main-and-catastro | 2 | 134 | **DROP_NOT_MINE** | Ejecutar git stash drop | Mensaje indica explícitamente trabajo de otro hilo |
| `stash@{9}` | `sprint/embrion-needs-002-` | WIP-not-mine | 2 | 272 | **DROP_NOT_MINE** | Ejecutar git stash drop | Mensaje indica explícitamente trabajo de otro hilo |
| `stash@{10}` | `sprint/s-002-5-rls-harden` | WIP-rls-routes-modif | 1 | 221 | **REVIEW_MANUAL_REQUERIDO** | Revisión humana por T1/T2 antes de acción | Toca kernel/embrion_routes.py, revisar si RLS ya se aplicó |
| `stash@{11}` | `sprint/s-002-5-rls-harden` | WIP_RLS_and_catastro_NO_TASK3 | 1 | 9 | **REVIEW_MANUAL_REQUERIDO** | Revisión humana por T1/T2 antes de acción | Requiere inspección profunda del diff |
| `stash@{12}` | `main` | WIP_catastro_sprint88_no_mios | 2 | 199 | **DROP_NOT_MINE** | Ejecutar git stash drop | Mensaje indica explícitamente trabajo de otro hilo |
| `stash@{13}` | `main` | wip-cowork-untracked-files | 0 | 0 | **DROP_OBSOLETO** | Ejecutar git stash drop | Stash vacio (0 files), probablemente working tree limpio |
| `stash@{14}` | `main` | wip-cowork-files-before-sprint88.3 | 1 | 13 | **REVIEW_MANUAL_REQUERIDO** | Revisión humana por T1/T2 antes de acción | Requiere inspección profunda del diff |
| `stash@{15}` | `main` | manus_b_pre_revert_882 | 2 | 185 | **DROP_NOT_MINE** | Ejecutar git stash drop | Backups de hilo B antiguo ya integrados o revertidos |
| `stash@{16}` | `main` | cowork-pendiente-sesion-2026-05-06: arch | 1 | 2 | **CHERRY_PICK_PARCIAL** | Extraer archivos específicos con git checkout stash@{N} -- <path> | Archivos untracked, revisar cuáles sirven y cuáles dropear |
| `stash@{17}` | `main` | manus_b_recover_context_1778066155 | 0 | 0 | **DROP_OBSOLETO** | Ejecutar git stash drop | Stash vacio (0 files), probablemente working tree limpio |
| `stash@{18}` | `main` | ejecutor_wip_pre_bloque2_catastro_177792 | 2 | 18 | **REVIEW_MANUAL_REQUERIDO** | Revisión humana por T1/T2 antes de acción | Toca kernel/browser_automation y main.py, WIP antiguo |
| `stash@{19}` | `main` | wip_pre_pull_1777917507 | 2 | 393 | **REVIEW_MANUAL_REQUERIDO** | Revisión humana por T1/T2 antes de acción | Toca kernel/browser_automation y main.py, WIP antiguo |
| `stash@{20}` | `main` | 3d4daf2 docs: respaldo sesinnn 2026-05-  | 1 | 31 | **REVIEW_MANUAL_REQUERIDO** | Revisión humana por T1/T2 antes de acción | Requiere inspección profunda del diff |
| `stash@{21}` | `main` | c1df169 docs: Sprint El Guardi68n Despie | 1 | 110 | **DROP_OBSOLETO** | Ejecutar git stash drop | Renames de case en reporte_validacion_biblias (ya en main) |
| `stash@{22}` | `main` | c1df169 docs: Sprint El Guardi68n Despie | 1 | 110 | **DROP_OBSOLETO** | Ejecutar git stash drop | Renames de case en reporte_validacion_biblias (ya en main) |
| `stash@{23}` | `main` | 408172f docs: Estado Unificado de Sincro | 1 | 98 | **DROP_OBSOLETO** | Ejecutar git stash drop | Duplicados de 408172f (ya en main) |
| `stash@{24}` | `main` | 408172f docs: Estado Unificado de Sincro | 1 | 98 | **DROP_OBSOLETO** | Ejecutar git stash drop | Duplicados de 408172f (ya en main) |
| `stash@{25}` | `main` | 4c254b3 docs: Los 14 Objetivos Maestros  | 1 | 98 | **DUPLICADO_DE_OTRO** | Ejecutar git stash drop (mantener el original) | Duplicado exacto de stash@{23} y stash@{24} (mismo SHA) |
| `stash@{26}` | `main` | 4c254b3 docs: Los 14 Objetivos Maestros  | 1 | 98 | **DUPLICADO_DE_OTRO** | Ejecutar git stash drop (mantener el original) | Duplicado exacto de stash@{23} y stash@{24} (mismo SHA) |
| `stash@{27}` | `main` | 857deca docs: Sprint La Prueba Viviente  | 2 | 149 | **DROP_OBSOLETO** | Ejecutar git stash drop | Archivos de iOS pbxproj ya resueltos en main/mobile |

## §3 Stashes con piezas únicas no en main

- `stash@{5}` (canonization): 43 archivos, muchos MDs en bridge/ que podrían no estar en main.
- `stash@{14}` y `stash@{16}`: Archivos untracked y specs propuestos que quedaron colgados.

## §4 Stashes con conflicts probables

- `stash@{4}` y `stash@{27}`: Tocan el `project.pbxproj` de iOS, que es notorio por merge conflicts.
- `stash@{3}`, `stash@{18}`, `stash@{19}`: Tocan `kernel/main.py` de hace días, seguro dan conflict con los wires recientes de Catastro.

## §5 Recomendación priorizada

1. **Fase 1 (Segura):** Dropear los 8 `DROP_OBSOLETO`, 6 `DROP_NOT_MINE` y 2 `DUPLICADO_DE_OTRO` (16 stashes fuera).
2. **Fase 2 (Extracción):** Cherry-pick de los MDs valiosos de `stash@{5}` y `stash@{16}`.
3. **Fase 3 (Revisión):** Alfredo revisa los 6 `REVIEW_MANUAL_REQUERIDO` que tocan kernel/mobile.

## §6 Stashes que requieren firma T1

Cualquier drop de los stashes clasificados como `REVIEW_MANUAL_REQUERIDO` requiere confirmación explícita de Alfredo, ya que tocan paths críticos (`kernel/`, `apps/mobile/`).
