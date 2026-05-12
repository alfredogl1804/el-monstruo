---
id: cowork_to_manus_HILO_CATASTRO_SPRINT_STASHES_FORENSIC_001_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Catastro (libre, MOBILE-2A reasignado a Hilo Ejecutor 1 por skill match)
tipo: spec_operativo_de_audit_forense
prioridad: P1
duracion_estimada: 1-2h
autoridad_T1: Alfredo autorizó 2026-05-12 04:55 UTC ("ok si")
context_previo: DRIFT-013 del Consolidado Maestro — 27 stashes en reporte original 02:00 UTC, verificado fresco 28 stashes a las 04:53 UTC (+1 del propio Hilo Catastro durante CATASTRO-C-SLICE-001, ejemplo binario de V23). Resolver este DRIFT desbloquea informadamente DRIFT-010 (decisión orden activación flags COWORK-RUNTIME-001) según §4 del acuse de absorción Consolidado.
---

# Sprint STASHES-FORENSIC-001 — Audit Estructurado de 28 Stashes

## §1 Contexto y rationale

Tu reporte CATASTRO-C-SLICE-001 demostró que el barrido forense de branches **antes** de inventar código rescató ~450 LOC de duplicación. La misma metodología aplica acá: **antes de drop ciego o apply automático, audit estructurado.** 28 stashes pueden contener piezas valiosas que cayeron sin merge (precedente PR #93 que rescató 36 archivos del stash hace 24h).

**Estado binario verificado a 04:53 UTC:**

```
$ git stash list | wc -l
28
```

Composición rápida (sin leer diffs):
- 17 stashes en `main` (varios WIP_catastro, manus_b_pre/recover, cowork-untracked, duplicados `{21}={22}`, `{23}={24}`, `{25}={26}`)
- 4 stashes `sprint/embrion-needs-002-tareas-2-5` ("WIP-not-mine" 1-4)
- 2 stashes `sprint/s-002-5-rls-hardening`
- 1 stash `sprint/mobile-1b-a2ui-implementation` (pre-handoff)
- 1 stash `cowork/canonization-2026-05-11` (pre-cowork-runtime-001)
- 1 stash `fix/migration-0015-run-costs` ("not-mine-found-on-main-2026-05-11")
- 1 stash `sprint/transversal-001-capas-implement-monitor` (audit-brief)
- 1 stash `sprint/transversal-001-capas-implement-monitor` (mv0018-recover)
- 1 stash `sprint/catastro-c-slice-001` (WIP de hoy — tuyo)

## §2 Tarea binaria — Audit estructurado, NO cleanup destructivo

### T1 — Para cada stash @{0}–@{27}, generar fila de matriz (1.5h)

Por cada `stash@{N}`, ejecutar:

```bash
git stash show --stat stash@{N} | head -20
git stash show -p stash@{N} | head -100
```

Llenar tabla con estas columnas:

| # | branch_origen | mensaje | n_archivos | n_loc | clasificación | recomendación | razón |
|---|---|---|---|---|---|---|---|

**Clasificaciones canónicas (elegir UNA por stash):**

- `DROP_OBSOLETO` — referencia branches que ya no existen o cambios ya en main
- `DROP_NOT_MINE` — mensaje "WIP-not-mine" o "manus_b_pre_revert" indica trabajo de otro hilo
- `APPLY_DIRECTO` — cambio limpio, branch existe, sin conflicts esperados
- `CHERRY_PICK_PARCIAL` — solo algunos archivos del stash valen, otros descartar
- `REVIEW_MANUAL_REQUERIDO` — contiene paths sensibles (kernel/catastro/, kernel/embrion_*, credentials, migrations)
- `DUPLICADO_DE_OTRO` — mismo diff que otro stash (caso `{21}={22}` por ejemplo)

### T2 — Generar reporte estructurado (15 min)

Path: `bridge/manus_to_cowork_REPORTE_STASHES_FORENSIC_2026_05_12.md`

Estructura:
```
§1 Resumen ejecutivo (tabla agregada: cuántos DROP, cuántos APPLY, etc.)
§2 Matriz 28×7 completa
§3 Stashes con piezas únicas no en main (lista de stash_id → archivos)
§4 Stashes con conflicts probables si se aplican (lista + razón)
§5 Recomendación priorizada: orden de procesamiento
§6 Stashes que requieren tu firma T1 antes de drop (sensibles)
```

### T3 — NO ejecutar drop ni apply automático

**Regla dura del sprint:** este es audit, NO cleanup. NO ejecutar:
- `git stash drop`
- `git stash pop`
- `git stash apply`
- ningún comando destructivo sobre stashes

El audit produce **recomendaciones**. Alfredo T1 + Cowork T2 procesan caso por caso después del reporte.

### T4 — Seedeá embrion_memoria al cerrar (5 min)

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES ('decision', 'Sprint STASHES-FORENSIC-001 cerrado. 28 stashes auditados estructuralmente. Matriz N×7 en bridge/manus_to_cowork_REPORTE_STASHES_FORENSIC_2026_05_12.md. Recomendaciones: X DROP_OBSOLETO, Y DROP_NOT_MINE, Z APPLY_DIRECTO, W CHERRY_PICK, V REVIEW_MANUAL, U DUPLICADO. Bloqueante para activación flags COWORK-RUNTIME-001 desbloqueado.', 'manus-hilo-catastro', 8);
```

## §3 Reglas duras del sprint

1. **NO ejecutar `git stash drop|pop|apply`** ni ningún comando destructivo sobre stashes durante el audit
2. **NO tocar código** de `kernel/`, `apps/mobile/`, `migrations/` durante este sprint
3. **NO crear branch dedicada** — todo el audit es read-only sobre stashes existentes
4. **Pre-commit hooks irrelevantes** — solo escribís el reporte en `bridge/`
5. **Sin push directo** — el reporte se commitea normalmente en main (es `bridge/`, no kernel)
6. **Honestidad anti-autoboicot:** si encontrás un stash que YA NO PODÉS LEER (corrupto, conflict de schema), reportalo como `REVIEW_MANUAL_REQUERIDO` sin adivinar contenido
7. **El stash@{0} es tuyo de hoy** — autoclasificalo honestamente (probablemente `REVIEW_MANUAL_REQUERIDO` o `APPLY_DIRECTO` según contenga el WIP de CATASTRO-C-SLICE-001)

## §4 Criterio de éxito binario

Output esperado al cerrar:

- ✅ Matriz 28 filas × 7 columnas completa
- ✅ Total de stashes clasificados = 28 (no 27, no 29)
- ✅ Cada clasificación tiene razón explícita (1 línea)
- ✅ Stashes con piezas únicas listados con paths exactos
- ✅ Cero comandos destructivos ejecutados
- ✅ Reporte pusheado a main bajo `bridge/manus_to_cowork_REPORTE_STASHES_FORENSIC_2026_05_12.md`
- ✅ embrion_memoria seeded con resumen

**Métrica que esperamos identificar:**

```
N DROP_OBSOLETO    + 
M DROP_NOT_MINE    + 
P APPLY_DIRECTO    + 
Q CHERRY_PICK      + 
R REVIEW_MANUAL    + 
S DUPLICADO        = 28
```

Si la suma NO da 28, el audit está incompleto. Si una clasificación es ambigua, usar `REVIEW_MANUAL_REQUERIDO`.

## §5 Skill match y autoridad

Esta tarea es **Python + bash + git + análisis estructurado**, exactamente tu fortaleza demostrada en CATASTRO-C-SLICE-001. NO requiere Dart, NO requiere Flutter. Es **misma metodología forense** que usaste para detectar `coding_classifier.py` antes de reinventar.

- T1 (Alfredo) autorizó 2026-05-12 04:55 UTC con "ok si"
- T2-A (Cowork) firma spec como orquestador
- T3 (Hilo Catastro) ejecuta autónomamente bajo reglas duras §3
- NO permiso de merge — este sprint NO modifica código, solo produce reporte
- Reporte queda como input canónico para sprint posterior (drops y applies decididos por T1+T2)

ETA realista: 1-2h dependiendo de cuántos diffs requieren lectura profunda.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 04:58 UTC
**Sprint STASHES-FORENSIC-001 cierra DRIFT-013 del Consolidado Maestro (deuda crítica #3) y desbloquea decisión informada sobre DRIFT-010 (orden activación flags COWORK-RUNTIME-001).**
