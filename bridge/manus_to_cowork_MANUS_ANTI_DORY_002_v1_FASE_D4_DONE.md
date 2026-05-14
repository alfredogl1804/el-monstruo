# 🔌 FASE D4 — DONE — AUDIT_PENDIENTE — Shadow Prod Blindado

**Sprint:** MANUS-ANTI-DORY-002 v1
**Fase:** D4 — Activación shadow prod del HeartbeatWriter
**Autor:** Manus (Ejecutor 1) bajo CONVERGENCIA TRIPLE Tier 1
**Fecha:** 2026-05-14
**Estado terminal:** `🔌 FASE D4 — AUDIT_PENDIENTE` (consolidado al cierre D6)

---

## §1. Resumen ejecutivo

D4 implementa **Opción A — Shadow Prod blindada** según convergencia triple:

- **T1 Alfredo** — Veredicto Cowork bd11733b aceptado.
- **Cowork T2-A** — Audit firmado con 10 condiciones (C1-C10) + 6 puntos ciegos (PC1-PC6) + plan operativo binario.
- **GPT-5.5 Pro Sabio Magna** — Convergencia con frase canónica: *"Shadow prod no es activación: es instrumentación reversible con cero hidratación hasta que el attachment real pase prueba binaria."*

D4 NO activa hidratación. NO toca el wire. NO afecta a usuarios. Solo instrumenta escritura observable de `runtime_events` + `thread_snapshots` desde un cron Railway aislado, con **kill switch DB + write budget hardcap + idempotency key + shadow namespace** explícitos.

---

## §2. Decisiones técnicas

| # | Decisión | Razón |
|---|---|---|
| 1 | **Rebase + rename 0033→0034** | Colisión con PR #128 MEMENTO (commit 24bc814). DSC-S-012 anti-deriva: verificación binaria post-merge mostró `0033_cowork_claims_calibration.sql` ocupado. Cowork bd11733b §7 ordenó rebase. |
| 2 | **4 flags separados** (C1) | `ANTI_DORY_ENABLED` (wire) ≠ `ANTI_DORY_CRON_ENABLED` (cron) ≠ `ANTI_DORY_HYDRATION_ENABLED` ≠ `ANTI_DORY_GUARDIAN_ENFORCE`. Permite activar SOLO el cron sin tocar el agente. |
| 3 | **Kill switch DB** (C2) | Tabla `anti_dory_runtime_flags` singleton + RPC `rpc_check_shadow_enabled()`. T1 puede flip a `false` desde SQL Editor sin tocar Railway. Latencia revert ≤15min. |
| 4 | **Write budget hardcap auto-disable** (C3) | Tabla `anti_dory_write_budget` 3 ventanas (10min/1h/24h: max 1/6/150). RPC `rpc_increment_write_budget()` atómico + self-disable automático si excede (UPDATE shadow_write_enabled=false). |
| 5 | **Idempotency key bucket 10min** (C4) | `f"{project_id}:{actor_type}:{ts//600}"` adjunto a cada payload. Mismo bucket dentro de 10min → misma key, permite dedup observacional. |
| 6 | **Shadow namespace explícito** (C5) | Payload incluye `mode=shadow_prod`, `hydration_active=false`, `user_impact=none`, `source=railway_cron`. Identificación inmutable forense. |
| 7 | **httpx timeout 10s + finally close** (GPT-5.5) | Anti-stuck Railway cron bug. `try/finally` cierra cliente HTTP siempre, incluso en exception. |
| 8 | **PC3 audit env segregation** | Whitelist de env vars permitidas + blacklist de vars prohibidas (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.). Warn al arranque si detecta leak. |
| 9 | **C7 smoke test local** | `--smoke-test` flag o `ANTI_DORY_CRON_SMOKE_TEST=true` corre dry_run sin Supabase. Valida payload structure + idempotency_key format. |
| 10 | **Cero self-merge** | PR D2-D3-D4 abierto contra `origin/main`. NO se mergea sin audit Cowork verde 6 gates DSC-G-008 v3. |

---

## §3. Artefactos entregados (commit bdf6a5c + commit fe96416)

### Código

| Archivo | Tipo | LOC | Estado |
|---|---|---|---|
| `migrations/sql/0034_anti_dory_grants.sql` | RENAMED de 0033 | 96 | ✅ Listo para apply |
| `migrations/sql/0035_anti_dory_runtime_flags.sql` | NUEVO | 343 | ✅ Listo para apply |
| `scripts/anti_dory_heartbeat_cron.py` | REWRITTEN | 350 | ✅ Smoke test PASS |
| `tests/anti_dory/test_heartbeat_cron.py` | REWRITTEN | 510 | ✅ 20/20 PASS |

### Bridge files

| Archivo | Propósito |
|---|---|
| `manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_D4_REVERT_PLAN.md` | 3 niveles de rollback con comandos exactos |
| `manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_D4_MIGRATIONS_APPLIED.md` | Template handoff Cowork → Manus + 7 métricas PC6 |
| `manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_D4_DONE.md` | Este reporte (audit input) |

---

## §4. Evidencia binaria

| Check | Esperado | Resultado |
|---|---|---|
| `python3.11 -m pytest tests/anti_dory/` | all pass | **48/48 PASS** (35 baseline + 13 D4) |
| Smoke test C7 sin Supabase | PASS | ✅ `--smoke-test` retorna 0 |
| DSC-G-008 grep secrets en archivos D4 | 0 hits | ✅ 0 hits |
| Migration 0034 `BEGIN/COMMIT` | balanceado | ✅ 1/1 |
| Migration 0035 `BEGIN/COMMIT` | balanceado | ✅ 1/1 |
| Migration 0035 `DO blocks` | 3 (2 triggers + 1 post-check) | ✅ 3 |
| Migration 0035 `RAISE EXCEPTION` | ≥7 | ✅ 7 |
| Migration 0035 RLS + policies | both tables + 2 policies | ✅ 2 RLS, 2 policies |
| Test C6 (no secret leak) | secret no en logs | ✅ PASS |
| Test T17 (PC3) | detecta env prohibidas | ✅ PASS |
| Test T18 (finally close) | finally cierra incluso en error | ✅ PASS |

---

## §5. Limitaciones esperadas (DSC-G-008 v3 §4)

- **L1**: D4 NO activa hidratación. El agente sigue su flujo legacy. La hidratación (D5) requiere FASE separada con audit Cowork independiente.
- **L2**: El cron es shadow writer only. NO lee thread_snapshots, NO reconstruye contexto, NO afecta task.create.
- **L3**: Budget hardcap es por ventana DB, no por ejecución cron. Si el cron schedule es agresivo (≤10min), el budget se autoprotege.
- **L4**: Idempotency key es **observacional** (no constraint UNIQUE en runtime_events). Permite dedup desde dashboards, no a nivel DB. Decisión consciente: evitar bloqueo de inserts legítimos.
- **L5**: PC3 env segregation es **warn**, no fail. Railway service deployment debe filtrar vars manualmente (decisión T1).

---

## §6. Consecuencias materiales

- **C1**: Cuando Cowork aplique 0034 + 0035 via MCP y verifique las 7 métricas PC6 verdes, Manus podrá crear el Railway service.
- **C2**: Primer deploy Railway con `ANTI_DORY_CRON_ENABLED=false` → cron corre cada 15min y hace exit 0 sin escribir. Validación operativa.
- **C3**: Flip `ANTI_DORY_CRON_ENABLED=true` por Manus + flip `shadow_write_enabled=true` por T1 → cron empieza a escribir. Monitoreo T+30min/T+2h/T+24h con 7 métricas PC6.
- **C4**: Cualquier alarma → L1/L2/L3 revert documentado en REVERT_PLAN.
- **C5**: Cierre D4 verde = base operativa para D5 (hidratación real bajo flag separado, ya no shadow).

---

## §7. Constraints respetados (10/10)

NO self-merge | NO aplicar Supabase prod | NO Railway service creado todavía | NO secrets | NO `ANTI_DORY_ENABLED` activado (wire intacto) | NO PR #118 tocado | NO Mac | NO-CRUCE total | F24 anti-fabricación (signatures Protocol respetadas) | F26 código ejecutable (48 tests + smoke test verificables)

---

## §8. Próximos pasos secuenciales

1. **Manus** → fuerza-push rama post-rebase + abre PR D2-D3-D4 (paso 7 del plan operativo Cowork)
2. **Cowork T2-A** → audit DSC-G-008 v3 con 6 gates sobre el PR
3. **Cowork T2-A** → si verde, aplica migrations 0034 + 0035 via MCP Supabase + llena `FASE_D4_MIGRATIONS_APPLIED.md` con 7 métricas verdes
4. **Manus** → crea Railway service con flag `ANTI_DORY_CRON_ENABLED=false` (no-op inicial)
5. **Manus** → flip flag Railway a `true` + verifica primer tick muestra "kill switch OFF → no-op"
6. **T1** → flip kill switch DB a `true` cuando autorice activación operativa
7. **Manus** → monitoreo T+30min/T+2h/T+24h con 7 métricas PC6 → reporte cierre D4

**Frase canónica al cierre D4 verde:** `🏛️ ANTI-DORY D4 SHADOW PROD — DECLARADO`

---

## §9. Riesgo residual reconocido

- **Bug latente en cron Railway no detectado por smoke test**: mitigado por kill switch DB (L1) que opera independientemente del cron logic.
- **Errores transitorios Supabase 5xx**: cron registra error log + continúa con próximo front. No-op safe.
- **Latencia inesperada >10s en RPC**: timeout httpx fuerza fail-closed. Cron termina sin escribir. Próximo tick reintenta.

Estos riesgos son **observables** vía las 7 métricas PC6 y **revertibles** vía L1/L2/L3.
