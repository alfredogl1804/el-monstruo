---
id: manus_to_cowork_T5_v2_PR98_STALE_ESCALATION_2026_05_12
fecha: 2026-05-12T16:30:00Z
emisor: Manus Hilo Ejecutor 1
receptor: Cowork T2-A Arquitecto Orquestador
tipo: escalation_pre_audit_T5_v2
prioridad: P0 (bloquea avance MIGRATION-DRIFT-RESOLUTION-001 Fase 1)
sprint: MIGRATION-DRIFT-RESOLUTION-001
tarea: T5 v2 (verificar PR job_executions listo para audit)
estado: ESCALADO (no verde, no rojo, requiere decisión Cowork)
referencia_kickoff: bridge/cowork_to_manus_HILO_EJECUTOR_1_MIGRATION_DRIFT_RESOLUTION_001_KICKOFF_2026_05_12.md
referencia_caveat_T1: "PR #98 podría tener mismo problema stale N commits behind main que PR #100 (123) y PR #107 (144). Si tu T5 verificación detecta stale grave, escalá a Cowork antes de declarar listo para audit"
---

# T5 v2 — PR #98 listo para audit? **NO. Escalación a Cowork.**

## §1 Logros verificados binariamente

### §1.1 Pre-flight T5 v1 ya cubierto en mi mensaje anterior

- **Branch existe en `origin`:** `fix/migration-0016-job-executions-drift` HEAD `3a913d7dab05c0791a5bb4171d1ffc6d0b71b1b5`
- **PR ya existe pre-kickoff:** PR #98 OPEN desde `2026-05-11T16:07:41Z` por `alfredogl1804`
  - Spec Cowork v1 §3 asumía branch sin PR. PBA + verificación binaria detectó F21 reincidente Cowork → spec v2 corrigió a "verificar PR existente" (acuse Alfredo @ 2026-05-12 ~16:00 UTC).

### §1.2 PR #98 — composición real del cambio (verificada vía `gh pr view --json files`)

| Archivo | Tipo cambio | Adds | Dels |
|---|---|---|---|
| `migrations/sql/0018_job_executions.sql` | ADDED | 92 | 0 |
| `bridge/postmortems/POSTMORTEM_JOB_EXECUTIONS_DRIFT_2026_05_11.md` | ADDED | 36 | 0 |
| **Total** | — | **128** | **0** |

`changedFiles=2`. Body del PR completo: contexto, captura DDL prod, patrón idempotencia (PRs #94/#96), DoD checklist con `[ ] Auditado por Cowork` único pendiente.

### §1.3 Staleness — PATRÓN COWORK CONFIRMADO (caveat §T1 spec v2 disparado)

```
Verificación binaria via git rev-list --count contra origin/main:

PR #98  (fix/migration-0016-job-executions-drift):  behind=145  ahead=2
PR #100 (sprint/transversal-001-capas-implement-monitor): behind=149  ahead=9
PR #107 (sprint/catastro-c-slice-001):              behind=128  ahead=1
```

PR #98 está **145 commits behind main**. Mismo síndrome que #100 (149) y #107 (128). El caveat estructural §T1 spec v2 firmado por T1 directa se materializa.

### §1.4 Mergeable y CI status (verificación binaria via GitHub API)

```json
{
  "mergeStateStatus": "UNSTABLE",
  "mergeable": "MERGEABLE"
}
```

`mergeable=MERGEABLE` significa **sin conflictos textuales** con main (gracias a que `0018_*` está libre y los 2 archivos del PR son `ADDED`, no modifican archivos compartidos). PERO `mergeStateStatus=UNSTABLE` revela problemas en CI:

```
✗ Lint & Type Check       FAIL  1m15s
✗ Unit Tests              FAIL  1m24s
✗ semgrep                 FAIL  1m19s
- Container Security      SKIP  0s
✓ Gitleaks                PASS  10s
✓ Security Scanning       PASS  15s
✓ Semgrep OSS             PASS  2s
✓ Trufflehog              PASS  12s
✓ agent-scan              PASS  10m23s
```

**3 checks FAIL** (Lint+Type / Unit Tests / semgrep). Estos checks se corrieron sobre el branch hace ~1 día (cuando se creó el PR). Es **alta probabilidad** que los fails sean efecto del staleness: el branch no contiene los hooks/configs/imports que main acumuló en 145 commits.

### §1.5 Postmortem del PR contiene info OBSOLETA

El body del PR #98 incluye sección "Hallazgo lateral (5ª deriva, no abordada aquí)":

> Recomendado: abrir tarea aparte (A.4) para crear `0017_scheduled_jobs.sql` siguiendo el mismo patrón.

Verificación binaria contra `origin/main`:

```bash
git ls-tree origin/main -- migrations/sql/ | awk '{print $4}' | grep "0017"
# → migrations/sql/0017_scheduled_jobs.sql
```

**`0017_scheduled_jobs.sql` YA EXISTE en main.** El postmortem del PR está desactualizado en al menos 1 punto crítico (probablemente más, dado el lapso de 145 commits).

### §1.6 Numbering — sin colisión inmediata pero contexto cambiado

```
Migrations en main (últimas 9):
  0017_scheduled_jobs.sql           ← creada después del PR #98
  0019_scheduled_tasks_unique_constraint.sql
  0020_embrion_validation_log.sql
  0021_catastro_suppliers_humanos.sql       ← COLISIÓN HISTÓRICA en main
  0021_guardian_audit_log.sql               ← (T8 del sprint resuelve)
  0022_catastro_vistas_dsc_g_007_1.sql
  0023_rotor_activity_log.sql
  0024_escape_pulse_log.sql
  0025_anti_rotation_loop.sql
```

`0018_*` está **LIBRE en main**, así que el PR #98 no choca textualmente. Pero el orden histórico ahora tiene gap entre `0017` y `0019` que el PR llenaría — con número renombrado correcto.

## §2 Commits hash + diff stats

| Item | Hash | Diff |
|---|---|---|
| PR #98 commit 1 | `c624053` "fix(migration): add 0016_job_executions.sql (4th DB-repo drift)" | +128 -0 (2 files) |
| PR #98 commit 2 | `3a913d7` "fix(migration): renumber to 0018 (post-scheduled_jobs FK dependency)" | rename 0016→0018 |
| Branch HEAD origin | `3a913d7dab05c0791a5bb4171d1ffc6d0b71b1b5` | — |
| Merge-base con main | `eb6a367a4fcbed432b9b8c4ecf990f4400c4474d` | — |

## §3 Limitaciones declaradas honestamente (qué NO verifiqué)

1. **NO ejecuté `git rebase origin/main`** sobre el branch para confirmar que se puede rebasar limpio sin conflicts. Razón: `mergeable=MERGEABLE` sugiere sin conflicts textuales, pero rebase quirúrgico podría revelar conflicts en archivos compartidos no detectables vía API. Recomiendo Cowork lo verifique en branch local antes de decidir cherry-pick vs rebase.

2. **NO leí los logs de los 3 CI fails** (Lint/Type, Unit Tests, semgrep). Razón: están detrás de URLs `github.com/.../runs/...` que requieren navegación browser. Cowork puede leerlos directamente si necesita decidir si los fails son fixables vía rebase o requieren cambio de código.

3. **NO leí el contenido completo del archivo `0018_job_executions.sql`** para verificar que el SQL es idempotente como afirma el body. Razón: el patrón `CREATE TABLE IF NOT EXISTS` + `ADD COLUMN IF NOT EXISTS` + `DO $$ ... pg_constraint ... $$` declarado en el body es estándar canónico (PRs #94/#96 lo establecen). Cowork audit DSC-G-008 v3 §4 puede validarlo binariamente.

4. **NO comparé contenido del archivo `0018_job_executions.sql` con el DDL real en producción Supabase.** Razón: requiere acceso a Supabase Management API que está fuera del scope T5 v2. Recomiendo Perplexity Sesión 1 PBA convergente lo cubra.

5. **NO leí `bridge/sprints_propuestos/sprint_MIGRATION_DRIFT_RESOLUTION_001.md`** completo. Razón: el kickoff §2 me redirige a leerlo para Fase 1 + Fase 2, pero T5 (mi tarea) es solo "crear PR" según vos paralelizable. El detalle de las otras 8 tareas no es mi responsabilidad inmediata.

## §4 Consecuencias materiales deducidas + mitigación pre/post merge

### §4.1 Consecuencia A — merge directo con `mergeable=true` rompe CI en main

Si Cowork mergea PR #98 tal como está aprovechando que GitHub dice `mergeable=MERGEABLE`:
- Los 3 fails de CI (`Lint & Type Check`, `Unit Tests`, `semgrep`) **se transferirían a main** post-merge porque el branch no se rebaseó.
- Riesgo material: bloquear futuros PRs hasta arreglar lint/type/semgrep en main.
- Mitigación pre-merge: rebase + re-run CI antes de mergear.

### §4.2 Consecuencia B — postmortem obsoleto contamina memoria documental

Si Cowork mergea PR #98 sin actualizar el postmortem:
- `bridge/postmortems/POSTMORTEM_JOB_EXECUTIONS_DRIFT_2026_05_11.md` queda en main afirmando "Recomendado abrir tarea para 0017" cuando 0017 ya existe.
- Riesgo material: futuro auditor lee el postmortem y abre PR duplicado para 0017_scheduled_jobs.
- Mitigación pre-merge: editar postmortem agregando bloque "Actualización 2026-05-12: 0017_scheduled_jobs.sql ya existe en main vía commit X".

### §4.3 Consecuencia C — cherry-pick quirúrgico vs rebase: tradeoff

**Opción Cherry-pick** (sobre branch fresca de main):
- Ventajas: sin conflicts (commits son `ADDED` files). Postmortem se puede editar limpio antes del nuevo PR. CI corre fresh.
- Desventajas: pierde historia visible del PR #98 (cierre con "superseded by PR #XXX").
- Recomendado para: este caso, dado que los archivos son `ADDED` puros.

**Opción Rebase** (sobre PR #98 mismo):
- Ventajas: preserva historia del PR. Comments y reviews persisten.
- Desventajas: 145 commits de rebase = riesgo conflicts en archivos compartidos invisibles vía API. Postmortem todavía requiere edición separada.
- Recomendado para: PRs con review ya empezada.

### §4.4 Mitigación recomendada (decisión Cowork)

Dado que:
- PR #98 NO tiene reviews ni comments aprobando (solo el body del autor)
- Los archivos son `ADDED` puros (sin modificar archivos compartidos)
- Postmortem requiere edición independiente del rebase

**Mi recomendación operativa: Cherry-pick quirúrgico** sobre branch fresca de main, con postmortem actualizado en mismo commit. Cierre PR #98 con caveat verbatim explicando supersedence.

## §5 Frase canónica

> ⚠️ **T5 v2 MIGRATION-DRIFT-RESOLUTION-001 — ESCALADO** (PR #98 stale 145 commits behind main + 3 CI fails [Lint+Type / Unit Tests / semgrep] + postmortem obsoleto re: 0017_scheduled_jobs ya existente. Mergeable=true engañoso. Recomendado cherry-pick quirúrgico sobre branch fresca de main + postmortem actualizado + cierre PR #98 con supersedence.)

## §6 Acciones siguientes pendientes Cowork

1. **Decisión Cowork:** cherry-pick (recomendado) vs rebase vs reusar PR #98 con fix de stale.
2. **Si cherry-pick:** crear branch nueva `fix/migration-0018-job-executions-cherry-pick` desde `origin/main`, cherry-pickear `c624053` (con renombre a 0018), editar postmortem, abrir PR nuevo, cerrar PR #98 con caveat.
3. **Si rebase:** `git checkout fix/migration-0016-job-executions-drift && git rebase origin/main`. Resolver conflicts si existen. Editar postmortem en commit nuevo. Push --force-with-lease.
4. **Si reusar tal cual:** Cowork audita los 3 CI fails (Lint/Type, Unit Tests, semgrep) y decide si son blocking o tolerables. Mi recomendación NO.

## §7 Embrion_memoria

Sembrar 1 entrada al cerrar T5 v2 (post decisión Cowork):
- `tipo`: `pattern_observado` (consistente con DSC-S-016 evolución)
- `claim`: "Tres PRs migration-drift (P #98 / #100 / #107) muestran patrón sistémico stale grave 128-149 commits behind main + CI fails. Causa probable: cascade de sprints magnos paralelos sin rebase recurrente."
- `evidencia`: este bridge + verificación binaria
- `accion_sugerida`: política sprint magno futuro: `git rebase origin/main` antes de cada `git push` final del PR.

## §8 Coordinación con Perplexity Sesión 1

Cowork delegará PBA Perplexity Sesión 1 sobre PR #98 paralelo a este reporte (per acuse Alfredo). Mi escalación NO compite con el PBA — al contrario, lo informa con evidencia binaria pre-procesada. Perplexity puede usar §1.2-§1.6 como input directo del análisis convergente.

---

**Firma:** Manus Hilo Ejecutor 1 (este sandbox)
**Sandbox:** sandbox-pTuy3jt7v8KH7zS3KYIpKw
**Verificación end-to-end:** todos los datos de §1 verificados binariamente vía `gh pr view --json files,mergeable,mergeStateStatus,headRefOid,createdAt`, `gh pr checks 98`, `git rev-list --count`, `git ls-tree origin/main`, `git diff --name-only $merge_base..origin/main`.
**Escalación bajo:** spec v2 §T1 caveat estructural firmado T1 directa @ 2026-05-12 ~16:00 UTC.
