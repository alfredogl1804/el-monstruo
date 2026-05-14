---
sprint_id: COWORK-MEMENTO-001
fecha_cierre: 2026-05-14
ejecutor: Manus Hilo Ejecutor (manus_hilo_b)
spec_firmado_commit: 78d1fb00
spec_path: bridge/sprints_propuestos/sprint_COWORK_MEMENTO_001.md
main_head_inicio: d95a7253
branch_head: 30760be
branch: feat/cowork-memento-001
pr_draft: https://github.com/alfredogl1804/el-monstruo/pull/128
estado: AUDIT_PENDIENTE NO DECLARADO
---

# 📋 COWORK-MEMENTO-001 — AUDIT_PENDIENTE NO DECLARADO

> *"Sin telemetría de calibration retrospectiva, todas las demás mitigaciones son cocción de hipótesis. Esta es la que recomiendo primero."* — Opus 4.7 Thinking, Dirección 4 verbatim

## §1 Resumen ejecutivo

Pieza 1 anti-Dory cross-sesión (D2 no-transfer cross-dominio + D3 asimetría costo verificar vs afirmar) implementada verbatim contra spec firmado T1 commit `78d1fb00`. Telemetría retrospectiva en `public.cowork_claims_calibration` ataca D2 + D3 con dataset, no doctrina.

**PR draft #128 creado.** Estado canónico condicional: `📋 AUDIT_PENDIENTE NO DECLARADO` — Cowork ejecuta audit DSC-G-008 v3 §4 reproduciendo binariamente los 5 checks para emitir `🏛️ DECLARADO` (F27 enforcement).

## §2 Status binario por tarea T0-T8

| Tarea | Archivo | LOC `wc -l` | Estado |
|---|---|---|---|
| T0 | `reports/cowork_memento_pre_sprint_audit.json` | 101 | ✅ — discrepancies D1 + D2 documentadas pre-código |
| T1 | `migrations/sql/0033_cowork_claims_calibration.sql` | 166 | ✅ — RLS + 1 policy + DO block + 4 índices |
| T2 | `kernel/cowork_runtime/claim_calibration.py` | 466 | ✅ — ClaimType (12) + VerificationStatus (4) + ClaimExtractor + ClaimLogger + infer_verification_status |
| T3 | `kernel/cowork_runtime/pre_response_hook.py` | +98 delta (vs 356 main → 454 post) | ✅ — markers CLAIM_CALIBRATION_BEGIN/END + fail-soft try/except |
| T4 | `tools/cowork_calibration_report.py` | 199 | ✅ — CLI con sandbox fallback |
| T5 | `tests/test_cowork_claim_calibration.py` | 325 | ✅ — **18/18 PASS** en 0.04s |
| T6 | `bridge/postmortems/COWORK_MEMENTO_001_postmortem.md` | 117 | ✅ — postmortem completo §1-§8 |
| T7 | `bridge/manus_to_cowork_COWORK_MEMENTO_001_DONE_2026_05_14.md` | (este archivo) | ✅ |
| T8 | branch + commit + push + PR draft #128 | — | ✅ |

**TOTAL `git diff --stat`:** 7 files changed, **+1472 insertions / -0 deletions**.

## §3 Limitaciones declaradas (DSC-G-008 v3 §4)

| Id | Limitación | Mitigación | Owner |
|---|---|---|---|
| L_A1 | Coverage limitada al output que el hook intercepta — claims pre-hook NO se loguean | VERIFICADOR-001 futuro extiende pre-hook | T1 firma futura |
| L_A2 | Regex extraction tiene falsos negativos (paths sin extensión, tablas en CTE complejas) | Iterar regex con datos T+7d | Cowork |
| L_A3 | verification_status post-hoc heurístico: tool result podría ser stale | Tag `tool_call_evidence` con timestamp + crítica visual | Cowork audit reports |
| L_A4 | Cobertura ≥80% es objetivo, no garantía — dataset T+7d puede demostrar menos | Re-evaluar threshold post-7d con datos reales | T1 |
| L_A5 | Migration number divergió de spec 0028 → 0033 (resuelto, documentado verbatim) | Resuelto en T0; D1 §3.1 spec ejercida | ✅ resuelto |
| L_A6 | Si `claim_calibration` falla al import o el logger crashea, el hook DEBE seguir funcionando (fail-soft) | try/except envolvente alrededor de `_record_claims_calibration` | implementado |

## §4 Consecuencias materiales deducidas (anti-Goodhart)

| Limitación | Consecuencia material | Mitigación | Owner |
|---|---|---|---|
| L_A1 | Subset de claims fuera del dataset | VERIFICADOR-001 (PIEZA 4) | T1 |
| L_A2 | F21 reales pueden quedar fuera del conteo | Iterar regex con dataset retrospectivo (Opus Dirección 4 aplicada) | Cowork |
| L_A3 | False verified_post_match si tool result obsoleto | `tool_call_evidence` snippet ±40 chars + audit visual Cowork | Cowork |
| L_A4 | Métrica éxito puede no alcanzarse en 7d | Re-evaluar threshold con datos reales, no hipótesis | T1 |
| L_A6 | Fail-soft puede ocultar errores del logger | `insert_count` + `error_count` expuestos como propiedades → CLI report puede alertar | Cowork dashboards |

## §5 Divergencias spec↔realidad (DSC-S-016 sin fabricar causalidad)

### D1 — Migration 0028 → 0033

- **Spec asumió:** `0028_cowork_claims_calibration.sql` (basada en estado pre-merge PR #118)
- **Realidad al T0 binario `ls migrations/sql/ | sort | tail -1` =** `0032_anti_dory_rpcs.sql`
- **Resolución:** procedemos con `0033`. Spec §3.1 cláusula fallback ejercida verbatim. Documentada literal en header del .sql.

### D2 — Markers AUTO-DISCIPLINE no pre-existían en `pre_response_hook.py`

- **Spec asumió:** patrón markers `AUTO_DISCIPLINE_BEGIN/END` ya en `pre_response_hook.py` post-PR #118
- **Realidad:** `grep -n "AUTO_DISCIPLINE" kernel/cowork_runtime/pre_response_hook.py` retorna **cero matches** en main `d95a7253`. PR #118 mergeó `f21_patterns.py` (295 LOC) y `antipatterns.py` (199 LOC) pero NO insertó markers en el hook.
- **Resolución:** insertamos markers `CLAIM_CALIBRATION_BEGIN/END` propios sin asumir patrón ausente. Backward compat real preservada.

### D3 — Baseline `test_cowork_auto_discipline_integration.py` no es 50/50 PASS en main

- **Spec §6 check #5 asumió:** "50 passed in 0.10s (idéntico pre-MEMENTO)" como baseline
- **Realidad binaria reproducible:**
  ```bash
  git stash
  git checkout main -- kernel/cowork_runtime/pre_response_hook.py
  .venv/bin/python -m pytest tests/test_cowork_auto_discipline_integration.py -q
  # Resultado: 8 failed, 42 passed (idéntico a post-mis-cambios)
  git stash pop
  ```
- **Resolución:** mi cambio NO rompe ningún test pasante. Baseline real = `8 failed, 42 passed`. Regresión cero. La discrepancia es deuda pre-existente de PR #118 que excede scope de este sprint.

## §6 5 checks de verificación reproducible (Cowork ejecuta en su turno F27)

```bash
# Check #1 — Migration applied + RLS verified (Cowork ejecuta vía MCP Supabase post-merge)
SELECT relrowsecurity AS rls_enabled,
       (SELECT COUNT(*) FROM pg_policies WHERE tablename='cowork_claims_calibration') AS policy_count
FROM pg_class WHERE relname='cowork_claims_calibration';
# Esperado: rls_enabled=true, policy_count=1

# Check #2 — Module imports OK
.venv/bin/python -c "from kernel.cowork_runtime.claim_calibration import ClaimLogger, ClaimExtractor, ClaimType, VerificationStatus; print('OK')"
# Esperado: OK

# Check #3 — Tests COWORK-MEMENTO-001 100% PASS
.venv/bin/python -m pytest tests/test_cowork_claim_calibration.py -v
# Esperado: 18 passed in <1s, 0 failed

# Check #4 — CLI standalone funciona con sandbox fallback
.venv/bin/python -m tools.cowork_calibration_report --days 1 --pretty
# Esperado: JSON con mode=sandbox, total_claims=0, by_type={}

# Check #5 — Hook backward compat (baseline real, no asumido)
.venv/bin/python -m pytest tests/test_cowork_auto_discipline_integration.py -q
# Esperado: 8 failed, 42 passed (idéntico a main puro pre-mis-cambios)
# Audit binario reproducible: git stash && git checkout main -- kernel/cowork_runtime/pre_response_hook.py && pytest
```

## §7 Reglas duras NO-CRUCE respetadas

- ✅ NO toqué `kernel/anti_dory/*` (FASE B+C ya mergeada PR #126 commit `d95a725`)
- ✅ NO toqué `f21_patterns.py`, `antipatterns.py`, `session_memory.py`, `rule_reinjection.py`, `companion_agent.py`, `drift_detector.py`, `alfredo_veto_channel.py`
- ✅ Solo `pre_response_hook.py` modificado vía markers `CLAIM_CALIBRATION_BEGIN/END` (rollback trivial)
- ✅ Self-merge NO

## §8 Próximas acciones (Cowork)

1. **Audit DSC-G-008 v3 §4** sobre branch `feat/cowork-memento-001` HEAD `30760be`
2. **Reproducir los 5 checks §6 binariamente** (NO leer este reporte como sustituto — F27 enforcement)
3. **Si verde 6/6 + T1 firma final:** convertir PR #128 draft → ready + merge a main
4. **Apply migration 0033 prod vía MCP Supabase** → verificar `rls=true, policy=1, columns=11, indexes=4`
5. **MEMENTO-T+7:** primer report aggregation 7 días post-merge para validar cobertura ≥80%
6. **MEMENTO-T+14:** decisión binaria PIEZA 3 (CRUZ-001) vs PIEZA 4 (VERIFICADOR-001) basada en datos reales

## §9 DSC candidato emergente (P0)

**DSC-MO-019 candidato:** "Spec firmado con asunciones sobre estado de main pre-merge debe tener cláusula fallback binaria verbatim antes de firma T1".

Patrón: D1 y D2 de este sprint demostraron que specs firmados pre-merge a veces asumen estado que ya no existe al T0 de ejecución (merges paralelos). Mitigación: toda spec firmada con asunciones tipo "PR #N mergeada al T0" debe declarar comando exacto de verificación + comportamiento fallback. Spec COWORK-MEMENTO-001 §3.1 cláusula fallback es ejemplo correcto a canonizar.

## §10 Frase canónica condicional (F27 enforcement)

**Estado actual:** `📋 COWORK-MEMENTO-001 — AUDIT_PENDIENTE NO DECLARADO`

**Solo emitir `🏛️ COWORK-MEMENTO-001 — DECLARADO` tras Cowork:**
1. Reproducir binariamente los 5 checks §6 en su turno (no leer este reporte)
2. Audit DSC-G-008 v3 §4 verde 6/6 confirmado
3. T1 firma final autorizando merge

---

**Branch:** `feat/cowork-memento-001` HEAD `30760be`
**PR draft:** https://github.com/alfredogl1804/el-monstruo/pull/128
**Base:** `main` HEAD `d95a7253`
