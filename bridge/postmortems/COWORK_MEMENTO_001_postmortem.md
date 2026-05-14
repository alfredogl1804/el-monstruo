---
sprint_id: COWORK-MEMENTO-001
fecha_cierre: 2026-05-14
ejecutor: Manus Hilo Ejecutor (manus_hilo_b)
spec_firmado_commit: 78d1fb00
spec_path: bridge/sprints_propuestos/sprint_COWORK_MEMENTO_001.md
main_head_inicio: d95a7253
branch: feat/cowork-memento-001
estado: AUDIT_PENDIENTE — Cowork audit DSC-G-008 v3 §4 standby
---

# Postmortem COWORK-MEMENTO-001 — Claim calibration retrospectiva

## §1 Resumen ejecutivo

Pieza 1 anti-Dory (D2 + D3) implementada verbatim contra spec firmado T1 commit `78d1fb00`. Telemetría de calibration retrospectiva conforme Dirección 4 Opus 4.7 Thinking: cada afirmación factual de Cowork queda logueada con `verification_status` binario (`verified_pre` / `verified_post_match` / `verified_post_mismatch` / `unverified`) en `public.cowork_claims_calibration`, alimentando dataset para iterar mitigaciones futuras con evidencia, no hipótesis.

Cero modificación a `kernel/anti_dory/*` (FASE B+C ya mergeada PR #126 commit `d95a725`). Cero modificación a otros módulos `kernel/cowork_runtime/*` excepto inserción de markers `CLAIM_CALIBRATION_BEGIN/END` en `pre_response_hook.py` con fail-soft try/except.

## §2 Lo que funcionó

- **T0 audit binario** detectó D1 (migration 0028→0033) y D2 (markers AUTO-DISCIPLINE no pre-existían en main) antes de escribir código, evitando dos potenciales violaciones DSC-S-012.
- **Migration 0033 con DO block** replicó verbatim el patrón canónico de 0027 (DSC-S-006 v1.1).
- **`ClaimExtractor` con regex deterministas e id explícito** permite trazar qué regex capturó qué claim (`extraction_regex_id` columna) para iterar dataset retrospectivo (Opus Dirección 4 verbatim).
- **`ClaimLogger` fail-soft** garantiza que un fallo del logger NUNCA rompe el flujo Cowork (declarado L_A6 en §3).
- **Tests 18/18 PASS** en 0.04s, cero red, cero DB.
- **CLI sandbox-fallback** funciona sin credenciales Supabase para iteración local.

## §3 Divergencias spec↔realidad declaradas (DSC-S-016 — sin fabricar causalidad)

### D1 — Migration number 0028 → 0033

- **Spec asumió:** migration `0028_cowork_claims_calibration.sql` (basada en estado pre-merge PR #118).
- **Realidad al T0 binario:** main HEAD `d95a7253` con migrations hasta `0032_anti_dory_rpcs.sql` ya aplicadas. Migrations 0028-0032 ocupadas por sprints subsiguientes mergeados antes de COWORK-MEMENTO-001 (PR #118, RUNTIME-EVENTS, THREAD-SNAPSHOTS, PROJECT-RUNTIME-HEADS, ANTI-DORY-RPCS).
- **Resolución:** migration final = `0033_cowork_claims_calibration.sql`. Spec §3.1 cláusula fallback verbatim autoriza el ajuste binario. Divergencia documentada literal en el header del .sql (DSC-S-012 anti-deriva).

### D2 — Markers AUTO-DISCIPLINE no pre-existían en `pre_response_hook.py`

- **Spec asumió:** markers `AUTO_DISCIPLINE_BEGIN/END` ya en `pre_response_hook.py` (post-merge PR #118).
- **Realidad al T0 binario:** `grep -n "AUTO_DISCIPLINE" kernel/cowork_runtime/pre_response_hook.py` retorna **cero matches** en main HEAD `d95a7253`. La PR #118 mergeó `f21_patterns.py` (295 LOC) y `antipatterns.py` (199 LOC) pero NO insertó los markers en el hook ni renovó su interfaz al perfil que el test suite esperaba.
- **Resolución:** insertamos markers `CLAIM_CALIBRATION_BEGIN/END` propios sin asumir patrón pre-existente. Backward compat real preservada (los 42 tests que pasaban en main siguen pasando idénticos).

### D3 — Baseline `test_cowork_auto_discipline_integration.py` no es 50/50 PASS en main

- **Spec §6 check #5 asumió:** "50 passed in 0.10s (idéntico pre-MEMENTO)" como baseline pre-existente.
- **Realidad binaria verificada vía `git stash` + `git checkout main -- kernel/cowork_runtime/pre_response_hook.py`:** `8 failed, 42 passed` sobre main HEAD `d95a7253` SIN mis cambios.
  - Los 8 tests que fallan (`TestHookIntegration::test_hook_init_has_session_uuid`, `test_register_tool_call_prevents_false_positive`, `test_history_capped_at_max`, etc.) esperan una interfaz `CoworkPreResponseHook` (con `last_invocation_record`, `register_tool_call(name=, result=)`, `history_max`, `session_uuid` en `session_health`) que **NO existe en `pre_response_hook.py` en main**.
  - PR #118 mergeó los tests pero NO actualizó `pre_response_hook.py` con la interfaz esperada → tests fallan en main antes de tocar nada.
- **Resolución:** mis cambios COWORK-MEMENTO-001 NO rompen ningún test que estuviera pasando. Baseline binario real = `8 failed, 42 passed` en main; post-mis-cambios = `8 failed, 42 passed` idéntico. La regresión es cero. La discrepancia es deuda pre-existente de PR #118 que excede el scope de este sprint.

## §4 Métricas (LOC verbatim `wc -l`)

| Archivo | LOC |
|---|---|
| `migrations/sql/0033_cowork_claims_calibration.sql` | 166 |
| `kernel/cowork_runtime/claim_calibration.py` | 466 |
| `kernel/cowork_runtime/pre_response_hook.py` (delta agregada) | +103 (vs 356 main → 459 post-cambios) |
| `tools/cowork_calibration_report.py` | 199 |
| `tests/test_cowork_claim_calibration.py` | 325 |
| `reports/cowork_memento_pre_sprint_audit.json` | 92 |
| **TOTAL nuevo / modificado** | **~1351 LOC** |

| Tests | Resultado |
|---|---|
| `tests/test_cowork_claim_calibration.py` | **18/18 PASS** en 0.04s |
| `tests/test_cowork_auto_discipline_integration.py` (baseline pre-existente) | 8 failed / 42 passed — **idéntico a main puro** (regresión cero) |

| ETA |
|---|
| Estimado spec: 150-180 min |
| Real: ~90 min (más rápido por reutilización de patrón ESCAPE/ESPIRAL/0027) |

## §5 Verificación reproducible (5 checks §6 spec)

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

# Check #5 — Hook backward compat (vs main puro, no vs spec asumido)
.venv/bin/python -m pytest tests/test_cowork_auto_discipline_integration.py -q
# Esperado: 8 failed, 42 passed (idéntico baseline main HEAD d95a7253 SIN mis cambios)
# Audit reproducible vía: git stash && git checkout main -- kernel/cowork_runtime/pre_response_hook.py && pytest
```

## §6 DSC candidato nuevo (P0 si aplica)

**DSC-MO-019 candidato:** "Spec firmado con asunciones sobre estado de main pre-merge deben tener cláusula fallback binaria verbatim antes de firma T1". Patrón: D1 y D2 de este sprint demostraron que los specs firmados pre-merge a veces asumen estado que ya no existe al T0 de ejecución (merges paralelos). Mitigación: toda spec firmada con asunciones tipo "PR #N mergeada al T0" debe declarar comando exacto de verificación + comportamiento fallback. Spec COWORK-MEMENTO-001 §3.1 cláusula fallback es ejemplo correcto a canonizar.

## §7 Próximos pasos para Cowork (audit)

1. **Reproducir los 5 checks §5 verbatim** (sin leer este reporte como sustituto — F27 enforcement).
2. **Audit DSC-G-008 v3 §4** sobre branch `feat/cowork-memento-001` HEAD a determinar post-push.
3. **Si verde 6/6 + T1 firma final:** merge a main.
4. **Apply migration 0033 prod** vía MCP Supabase + verificar binariamente `rls=true, policy=1, columns=11, indexes=4`.
5. **MEMENTO-T+7:** primer report aggregation 7 días post-merge para validar cobertura ≥80%.
6. **Decisión binaria MEMENTO-T+14:** PIEZA 3 (CRUZ-001) vs PIEZA 4 (VERIFICADOR-001) basada en datos reales.

## §8 Frase canónica condicional (F27)

**Estado actual:** `📋 COWORK-MEMENTO-001 — AUDIT_PENDIENTE NO DECLARADO`

**Solo emitir `🏛️ COWORK-MEMENTO-001 — DECLARADO` tras Cowork reproducir binariamente los 5 checks de §5 + audit verde 6/6.**
