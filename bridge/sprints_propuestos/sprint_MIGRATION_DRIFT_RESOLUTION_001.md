<!-- lint_strict -->

# Sprint MIGRATION-DRIFT-RESOLUTION-001 — Cierre estructural drift DB↔repo + renumber forensic

**estado:** FIRME T1 directa ("opcion A, voy con tu recomendacion" 2026-05-12 ~10:45 UTC)
**fecha_firma_T1:** 2026-05-12 ~10:45 UTC
**autor_borrador:** Cowork T2-A Arquitecto Orquestador post forensic Perplexity T2-B Sesión 1 + caveat 0013 verificado
**Hilo principal:** Manus Hilo Ejecutor 1 (queue post corrección-3-docs-Cowork post-Brand-Canary)
**ETA recalibrado:** 2-3h reales Fase 1 + 1-2h Fase 2 mínima = 3-5h total
**Objetivo Maestro:** #4 (No equivocarse dos veces) + #5 (Documentación Magna/Premium) + #11 (Autonomía progresiva)
**Bloqueos pre-arranque:** ninguno. Ejecutor 1 standby post TA-BRAND-CANARY-001 + corrección 3 docs encadenada. Perplexity T2-B Sesión 1 libre.
**Resultado esperado:** **drift DB↔repo completamente cerrado** (3 tablas huérfanas mergeadas a main) + colisiones numéricas migration resueltas (0004 + 0021 renumber forensic) + sin fantasmas paralelos validation_log.

---

## 0. Audit pre-sprint (DSC-G-008 v3 §1)

**Hallazgos forensic Perplexity T2-B Sesión 1 verificados binariamente 2026-05-12 ~10:30 UTC:**

| Tabla prod | SQL canónico vive en | PR estado | Acción |
|---|---|---|---|
| `trend_signals` | `migrations/sql/0013_trend_signals.sql` en branch `transversal-001` commit `de7375d` | **PR #100 OPEN** SHA `cfae78f` | Re-audit + PBA + merge |
| `job_executions` | `0018_job_executions.sql` en branch `fix/migration-0016-job-executions-drift` | **SIN PR** | Crear PR + audit + PBA + merge |
| `catastro_repos` | `0018_catastro_repos.sql` en branch `sprint/catastro-c-slice-001` commit `8a65651` | **PR #107 OPEN** SHA `8a65651` | Re-audit + PBA + merge |

**Colisiones numéricas en main (T2-B forensic original):**
- 0004: `0004_embrion_write_proposals.sql` commit `1023049` (ganador timestamp) + `0004_enable_rls_p0_critico.sql` commit `fcfabe7` (perdedor)
- 0021: `0021_guardian_audit_log.sql` commit `1508b83` (ganador timestamp) + `0021_catastro_suppliers_humanos.sql` commit `1bcb2c0` (perdedor)

**Caveat Perplexity:** verificar también validation_log rows 29/30/31 mencionados en commit `de7375d` para no dejar fantasmas paralelos.

## 1. Fase 1 — Cierre drift DB↔repo (T1-T5)

### T1 — Re-audit DSC-G-008 v3 §4 PR #100 trend_signals (20-30 min)

**perfil_riesgo:** read-only + Cowork audit

Cowork audita binariamente PR #100 (branch `transversal-001` head SHA `cfae78f`):
- Diff completo vs main (gh pr diff)
- Verificar SQL `0013_trend_signals.sql` 85 LOC RLS + 3 índices + policy service_role_only
- Verificar scope: NO debe incluir cambios kernel fuera de los necesarios para tendencias
- Verificar no overlap con PR #110 cowork_runtime + PR #92 mobile-1b

Reporte audit comment en PR #100 con §3 limitaciones + §4 consecuencias materiales (DSC-G-008 v3 obligatorio).

### T2 — PBA Perplexity T2-B Sesión 1 sobre PR #100 (15-20 min Perplexity)

Cowork delega audit independiente a Perplexity Sesión 1 (libre post trend_signals). Convergencia ≥5/6 VERDE requerida para merge.

### T3 — Re-audit DSC-G-008 v3 §4 PR #107 catastro_repos (15-25 min)

Mismo patrón T1: Cowork audit binario + comment PR.

### T4 — PBA Perplexity T2-B Sesión 1 sobre PR #107 (15-20 min)

Mismo patrón T2: convergencia ≥5/6 VERDE.

### T5 — Crear PR + audit + merge job_executions (30-40 min)

**perfil_riesgo:** write-risky (PR nuevo)

Ejecutor 1:
1. `git checkout origin/fix/migration-0016-job-executions-drift`
2. `gh pr create --base main --head fix/migration-0016-job-executions-drift --title "feat(kernel): MIGRATION-DRIFT-RESOLUTION-001 T5 job_executions - cerrar drift DB↔repo (tabla en prod desde 2026-05-11, SQL en branch sin PR)"`
3. Cowork audit DSC-G-008 v3 §4 + Perplexity Sesión 1 PBA
4. Merge si verde

### T6 — Audit validation_log fantasmas 29/30/31 (10-15 min)

**perfil_riesgo:** read-only audit

Perplexity Sesión 1 (post-T2/T4 audits) o Cowork directamente:
```sql
SELECT id, timestamp, source, payload->>'tipo' AS tipo
FROM validation_log
WHERE id IN (29, 30, 31);
```
Reportar binariamente: ¿existen? ¿son fantasmas (sin commit asociado en repo)? ¿requieren cleanup destructivo o canonización doctrinal?

### T7 — Merge 3 PRs (Cowork ejecuta post verde) (5-10 min)

Post T1-T6 verdes:
- Merge PR #100 squash con caveats verbatim T2-B en commit body
- Merge PR #107 squash con caveats verbatim T2-B
- Merge PR job_executions squash con caveats verbatim
- Verificar binariamente las 3 tablas siguen funcionando prod post-merge

## 2. Fase 2 — Renumber forensic colisiones (T8-T9)

### T8 — Renumber 0004 colisión (15-25 min)

**perfil_riesgo:** write-risky (rename SQL canónico)

Ejecutor 1:
```bash
git mv migrations/sql/0004_enable_rls_p0_critico.sql migrations/sql/0026_enable_rls_p0_critico.sql
# (asumiendo 0026 libre post Fase 1 — verificar con ls migrations/sql/ | sort | tail)
# Update referencias internas:
grep -rln "0004_enable_rls_p0_critico" . --include="*.py" --include="*.md" --include="*.yaml" | xargs sed -i 's|0004_enable_rls_p0_critico|0026_enable_rls_p0_critico|g'
# Commit
git commit -m "refactor(migrations): MIGRATION-DRIFT-RESOLUTION-001 T8 - rename 0004_enable_rls_p0_critico.sql to 0026 resolviendo colisión con 0004_embrion_write_proposals.sql (ganador timestamp 2026-05-10 04:41 vs perdedor 05:02)"
```

PR atómico tag `[MIGRATION-DRIFT-T8]` + audit Cowork + PBA + merge.

### T9 — Renumber 0021 colisión (15-25 min)

Mismo patrón T8 con `0021_catastro_suppliers_humanos.sql` → `0027` (o slot libre verificado).

## 3. Contratos ejecutables que adjunta

| DSC enforzado | Contrato producido | Tarea |
|---|---|---|
| DSC-G-008 v3 §4 | Audit Cowork con §3 + §4 explícito por cada PR | T1 + T3 + T5 |
| DSC-MO-006 v1.1 PBA | Convergencia T2-B sobre 3 PRs + validation_log | T2 + T4 + T6 |
| DSC-S-006 v1.1 | RLS preservada en 3 tablas mergeadas | Verificación post-merge T7 |
| DSC-S-012 | Migraciones en main post-merge sin colisiones | Fase 2 T8 + T9 |
| DSC-S-016 | Verificación binaria pre-afirmación de cifras | Todo el sprint |
| DSC-G-017 | DSC-as-contract: _dsc_contracts_index.yaml actualizado | Post-T8 + T9 |

## 4. Criterios de cierre verde

- 3 PRs mergeados (PR #100 + PR #107 + PR job_executions) con audits Cowork DSC-G-008 v3 + PBA T2-B convergentes verbatim
- 2 colisiones renumeradas (0004 + 0021) sin breaking references
- Validation_log fantasmas 29/30/31 auditados + decisión binaria (cleanup o canonización)
- Drift DB↔repo CERRADO: las 3 tablas prod tienen SQL canónico en main
- Frase canónica: `🏛️ MIGRATION-DRIFT-RESOLUTION-001 — DECLARADO (9/9 verde) — drift DB↔repo cerrado + 2 colisiones resueltas`

## 5. Owner y timing

**Owner técnico principal:** Manus Hilo Ejecutor 1 (post Brand-Canary + corrección-3-docs encadenadas)
**Owner arquitectónico:** Cowork T2-A (audits DSC-G-008 v3 §4 por cada PR)
**Owner verificación independiente:** Perplexity T2-B Sesión 1 (PBA 3 PRs + validation_log)
**Owner humano final:** Alfredo T1 (firma ratificación + override CI si aplica)
**Timing:** arranca post Ejecutor 1 cierre corrección-3-docs (~30-45 min adelante).

## 6. Permiso de merge

- **PRs write-risky** (PR #100 + #107 + job_executions): audit DSC-G-008 v3 + PBA T2-B convergente obligatorios
- **T8 + T9 renumber PRs**: audit DSC-G-008 v3 + PBA T2-B + verify ningún script/CI rompa por path cambio
- **Bypass T1 directo**: NO autorizado para esta cascada (drift estructural histórico, no urgent operacional)

## 7. Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint MIGRATION-DRIFT-RESOLUTION-001 CERRADO. Drift DB↔repo CERRADO: trend_signals + job_executions + catastro_repos mergeadas a main via PR #100 + PR #107 + PR job_executions nuevo. Colisiones 0004 + 0021 renumeradas a 0026 + 0027 forensic. Validation_log fantasmas 29/30/31 auditados + decisión binaria aplicada. DSC-G-008 v3 §4 + PBA T2-B convergencia cada PR verbatim caveats. DSC-S-012 enforcement pendiente sprint separado MIGRATION-DRIFT-ENFORCEMENT-002 (deadline 2026-06-10).',
  'manus-hilo-ejecutor-1',
  10
);
```

## 8. Out-of-scope (sprint separado post-cierre)

MIGRATION-DRIFT-ENFORCEMENT-002 cubrirá DSC-S-012 activation completa:
- `tools/_check_migration_drift.py` script ejecutable
- `.pre-commit-config.yaml` hook migration-drift-check
- `.github/workflows/migration-drift-audit.yml` workflow CI semanal

Esto previene futuros drifts pero NO es bloqueante de este sprint cierre.

---

**Firma:** Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa, 2026-05-12 ~10:45 UTC
**Sprint magno estructural.** Cierra drift DB↔repo histórico + colisiones numéricas pendientes desde 2026-05-10. Owner Ejecutor 1 + audits Cowork + PBA Perplexity Sesión 1.
