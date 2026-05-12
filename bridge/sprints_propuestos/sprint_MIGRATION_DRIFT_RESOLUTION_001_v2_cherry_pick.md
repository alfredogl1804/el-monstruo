<!-- lint_strict -->

# Sprint MIGRATION-DRIFT-RESOLUTION-001 v2 — Cherry-pick quirúrgico (deroga v1)

**estado:** FIRME T1 directa ("si autorizado" 2026-05-12 ~11:15 UTC)
**fecha_firma_T1:** 2026-05-12 ~11:15 UTC
**autor_borrador:** Cowork T2-A Arquitecto Orquestador post-T2-B PBA Sesión 1 (bloqueo PR #100 + PR #107)
**deroga:** `sprint_MIGRATION_DRIFT_RESOLUTION_001.md` (v1 commit `3b37b547`) por hallazgos T2-B branches stale 123 + 144 commits behind main — merge directo destruiría 10 migrations recientes
**Hilo principal:** Manus Hilo Ejecutor 1 (queue post T5 actual + corrección 3 docs Cowork)
**ETA recalibrado:** 3-5h reales (3 cherry-picks + 2 renumbers forensic + 2 PRs obsoletos cerrar)
**Objetivo Maestro:** #4 (No equivocarse dos veces) + #11 (Autonomía progresiva) + #12 (Soberanía)
**Bloqueos pre-arranque:** ninguno. Ejecutor 1 standby post corrección-3-docs encadenada.
**Resultado esperado:** drift DB↔repo cerrado vía cherry-pick atómico (cero rebase masivo) + colisiones numéricas resueltas + PRs obsoletos cerrados doctrinalmente.

---

## 0. Audit pre-sprint (DSC-G-008 v3 §1)

**Hallazgos T2-B Sesión 1 verificados binariamente 2026-05-12 ~11:00 UTC:**

| PR | Behind main | Diff migrations | Veredicto T2-B |
|---|---|---|---|
| #100 trend_signals | **123 commits stale** | -1187/+199 (destruiría 10 migrations) | BLOQUEAR |
| #107 catastro_repos | **144 commits stale** | -918/+107 (destruiría 8 migrations) | BLOQUEAR |

Merge directo de PRs como están borraría: 0015 + 0017 + 0019 + 0020 + 0021×2 + 0022 + 0023 + 0024 + 0025. **Inaceptable.**

**Positivo doctrinal T2-B:** `0018_catastro_repos.sql` es **modelo doctrinal superior** (DO blocks idempotentes + policy idempotente + función idempotente + REVOKE/GRANT explícito + BEGIN/COMMIT). Estandariza para futuros migrations.

## 1. Estrategia v2 — Cherry-pick quirúrgico

**No rebase masivo.** Crear PRs atómicos nuevos con solo el migration SQL canonónico de cada branch + refs mínimas kernel necesarias. Cerrar PRs originales como obsoletos post-cherry verde.

Renumber forensic conservador:
- `0013_trend_signals.sql` → `0026_trend_signals.sql`
- `0018_catastro_repos.sql` → `0027_catastro_repos.sql`
- `0018_job_executions.sql` → `0028_job_executions.sql`

+ Renumber colisiones main históricas (Fase 2):
- `0004_enable_rls_p0_critico.sql` → `0029_enable_rls_p0_critico.sql`
- `0021_catastro_suppliers_humanos.sql` → `0030_catastro_suppliers_humanos.sql`

## 2. Tareas T1-T9

### T1 — Cherry-pick trend_signals (30-45 min)

**perfil_riesgo:** write-risky
**Owner:** Ejecutor 1

```bash
git checkout -b sprint/migration-drift-cherry-trend-signals
git checkout origin/sprint/transversal-001-capas-implement-monitor -- migrations/sql/0013_trend_signals.sql
git mv migrations/sql/0013_trend_signals.sql migrations/sql/0026_trend_signals.sql
# Verificar idempotencia CREATE POLICY (T2-B P2 sobre PR #100):
# Si NO idempotente, agregar DROP POLICY IF EXISTS + CREATE POLICY (patrón 0018_catastro_repos.sql modelo doctrinal)
sed -i 's|0013_trend_signals|0026_trend_signals|g' bridge/ tools/ scripts/ 2>/dev/null  # update refs
git commit -m "feat(migration): MIGRATION-DRIFT-RESOLUTION-001 v2 T1 cherry-pick 0013→0026 trend_signals + DO block policy idempotente (modelo doctrinal 0018_catastro_repos.sql)"
gh pr create --base main --title "[MIGRATION-DRIFT-RESOLUTION-001 T1] cherry-pick trend_signals 0013→0026 + policy idempotente"
```

**Audit Cowork DSC-G-008 v3 + PBA Perplexity Sesión 1 + Cowork merge si verde.**

### T2 — Cherry-pick catastro_repos (25-35 min)

**perfil_riesgo:** write-risky
**Owner:** Ejecutor 1

Identical patrón T1 con `0018_catastro_repos.sql` → `0027_catastro_repos.sql`. Migration es modelo doctrinal limpio, copy-paste verbatim + renumber + refs update.

### T3 — Cherry-pick job_executions (30-40 min)

**perfil_riesgo:** write-risky
**Owner:** Ejecutor 1

Identical T1 con `0018_job_executions.sql` → `0028_job_executions.sql`. Verificar idempotencia (T2-B no auditó binariamente este por brevedad, requiere check).

### T4 — Renumber colisión main 0004 (15-20 min)

**perfil_riesgo:** write-risky
**Owner:** Ejecutor 1

```bash
git checkout -b sprint/migration-drift-renumber-0004
git mv migrations/sql/0004_enable_rls_p0_critico.sql migrations/sql/0029_enable_rls_p0_critico.sql
grep -rln "0004_enable_rls_p0_critico" . --include="*.py" --include="*.md" --include="*.yaml" | xargs sed -i 's|0004_enable_rls_p0_critico|0029_enable_rls_p0_critico|g'
git commit -m "refactor(migration): MIGRATION-DRIFT-RESOLUTION-001 v2 T4 renumber 0004→0029 enable_rls_p0_critico (ganador timestamp 04:41 vs perdedor 05:02)"
```

Audit Cowork + PBA T2-B + merge.

### T5 — Renumber colisión main 0021 (15-20 min)

**perfil_riesgo:** write-risky
**Owner:** Ejecutor 1

Identical T4 con `0021_catastro_suppliers_humanos.sql` → `0030_catastro_suppliers_humanos.sql`.

### T6 — Cerrar PR #100 + PR #107 obsoletos (10 min)

**perfil_riesgo:** write-safe
**Owner:** Cowork T2-A (rol arquitecto: cierre PRs obsoletos)

```bash
# Post T1-T3 verdes (3 cherry-picks mergeados a main):
gh pr close 100 --comment "PR #100 superseded by MIGRATION-DRIFT-RESOLUTION-001 v2 T1 cherry-pick 0026_trend_signals.sql. Original branch 123 commits stale, merge directo hubiera destruido 10 migrations recientes. Cherry-pick quirúrgico aplicado."
gh pr close 107 --comment "PR #107 superseded by MIGRATION-DRIFT-RESOLUTION-001 v2 T2 cherry-pick 0027_catastro_repos.sql. Original branch 144 commits stale."
```

Cowork ejecuta via `mcp__github-monstruo__update_issue`.

### T7 — Canonización validation_log 29/30/31 leave-as-is (10 min)

**perfil_riesgo:** write-safe
**Owner:** Cowork T2-A (canonización doctrinal)

Documentar verbatim en `bridge/cowork_validation_log_rows_29_30_31_canonizacion_doctrinal_2026_05_12.md`:
- Existen en Supabase prod (verificado T2-B)
- Pertenecen a TRANSVERSAL-001 T5
- Inserted by manus_hilo_ejecutor_2
- Esquema real: claim_type/claim_fingerprint/claim_value/validator/evidence_url/timestamp_unix/ttl_seconds/metadata/created_at (sin columna decision)
- Acción: leave as is

### T8 — F21 propio Cowork reconocido (5 min)

**perfil_riesgo:** write-safe
**Owner:** Cowork T2-A (DSC-S-016 self-correction)

Reconocimiento embrion_memoria importancia 9: spec v1 T6 fabriqué query SQL con columnas inexistentes (decision/source/payload/timestamp) en validation_log. T2-B Sesión 1 detectó + corrigió con esquema real. F21 reincidente sin verificar binariamente schema antes de afirmar.

### T9 — Reporte cierre + DSC-G-008 v3 §4 (10-15 min)

**Owner:** Ejecutor 1

Reporte verbatim en `bridge/manus_to_cowork_MIGRATION_DRIFT_RESOLUTION_001_v2_FINAL_2026_05_12.md`. §1 logros + §2 commits + §3 limitaciones + §4 consecuencias materiales. Frase canónica: `🏛️ MIGRATION-DRIFT-RESOLUTION-001 v2 — DECLARADO (9/9 verde) — drift DB↔repo cerrado vía cherry-pick + colisiones renumeradas + PRs obsoletos cerrados`.

## 3. Criterios de cierre verde

- 3 PRs nuevos mergeados (T1+T2+T3) con audits Cowork DSC-G-008 v3 §4 + PBA T2-B Sesión 1 verdes
- 2 renumbers forensic main mergeados (T4+T5)
- 2 PRs originales cerrados obsoletos (T6) con comments verbatim
- validation_log canonizado leave-as-is (T7)
- F21 propio reconocido (T8)
- Reporte final §4 explícito (T9)

## 4. Out-of-scope (sprint separado)

- DSC-S-012 enforcement (script + pre-commit + workflow) → sprint MIGRATION-DRIFT-ENFORCEMENT-002
- 0001_validation_log CREATE POLICY idempotency fix → sprint MIGRATION-IDEMPOTENCY-AUDIT-001 (T2-B P0 sobre PR #100 caveat)
- Sprint 89 reanudación → Catastro queue post-DSC-S-005 spike

---

**Firma:** Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa, 2026-05-12 ~11:15 UTC
**Spec v2 cherry-pick magna.** Reemplaza v1 spec erróneo (asumí merge directo viable, falso). T2-B PBA Sesión 1 funcionando estructuralmente.
