---
id: cowork_to_manus_HILO_EJECUTOR_2_GATE_VERDE_ESCAPE_001_y_BRAND_ENGINE_CANARY_2026_05_12
fecha: 2026-05-12T07:58:00Z
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 2 (libre post-ROTOR-001 PR #113 mergeado)
tipo: gate_verde_multi_decision
prioridad: P0
autoridad_T1: Alfredo firmó 5 decisiones simultáneas 2026-05-12 ~07:55 UTC ("te firmo los 5 incluyendo el 5 de xcode")
---

# Gate VERDE Multi-Decisión para Ejecutor 2 — ESCAPE-001 + Brand Engine Canary

## §1 — Resumen ejecutivo

Alfredo firmó hace ~5 min cinco decisiones agrupadas en un mensaje verbatim **"te firmo los 5 incluyendo el 5 de xcode"**:

1. ✅ **DSC-S-015** canonizado firme (Scheduler respeta next_run de restore) — commit `51d6017`
2. ✅ **DSC-OPS-001** canonizado firme (UPDATE manual prod requires bridge report) — commit `1eb375c`
3. ✅ **DSC-S-016** canonizado firme (Anti-fabricación causalidad sin grep) — commit `54ddd6f`
4. ✅ **ESCAPE-001 spec FIRME T1** — commit `ff8716f` ← **gate (a) verde para vos**
5. ✅ **Brand Engine canary** autorización aplicar (resta dar valores Telegram explícitos para T3)
6. (Quinto del verbatim: T7 smoke binario Mac PR #114 — Alfredo ejecuta en Mac local, no afecta tu sprint)

## §2 — Gate (a) ESCAPE-001 VERDE

El spec firmado está en `bridge/sprints_propuestos/sprint_ESCAPE_001_throttler_deterministico.md` con estado actualizado:

```
**estado:** FIRME T1 — firmado Alfredo 2026-05-12 ~07:55 UTC
**fecha_firma_T1:** 2026-05-12 ~07:55 UTC
```

**Bloqueo restante para arrancar:** PR #113 ROTOR-001 MERGEADO a main. Verificá con:
```bash
gh pr view 113 --json state,merged
# Esperado: state=MERGED, merged=true
```

Si PR #113 está merged, podés arrancar T1 (migración 0026 escape_pulse_log) inmediatamente.

## §3 — Brand Engine canary autorización

PAR_BICEFALO_001 cerró tres PRs (#108/#109/#111) con 84/84 tests y `enabled=false` shadow. Alfredo autoriza **arrancar canary en modo shadow controlado** post-ESCAPE-001.

**Comando Railway que Alfredo ejecuta (vos solo notificás cuando ESCAPE-001 cierre):**
```bash
railway variables set BRAND_ENGINE_CANARY=true --service el-monstruo-kernel
railway variables set BRAND_ENGINE_MODE=shadow --service el-monstruo-kernel
railway variables set BRAND_ENGINE_SAMPLE_RATE=0.1 --service el-monstruo-kernel  # 10% requests
```

**Bloqueo:** valores `BRAND_ENGINE_TELEGRAM_CHAT_ID` + `BRAND_ENGINE_TELEGRAM_WINDOW_HOURS` + `BRAND_ENGINE_TELEGRAM_RATE_LIMIT` pendientes firma explícita Alfredo (solo él tiene los valores chat_id privado). Una vez Alfredo me los da, los pongo en bridge.

**Tu acción Brand Engine:** ninguna ahora. Foco 100% en ESCAPE-001. Yo notifico cuando los valores Telegram lleguen y pasan a vos como Tarea TA4 post-cierre ESCAPE.

## §4 — Reglas duras NO-CRUCE actualizadas 2026-05-12 ~07:58 UTC

Hay 4 hilos en vuelo simultáneos. **NO tocar:**

1. **Hilo Catastro Sprint MEGA-CIERRE-HOY** trabajando en TA1 cleanup `_tmp_notif.md` + TA2 apply migration 0023 escape_pulse_log... ESPERA — **revisar conflict con tu T1**:
   - Catastro TA2 aplica migración SQL ya escrita en main (S-CONTRATOS-001 0023+0024+0025)
   - Tu T1 ESCAPE-001 crea 0026 NUEVA — no overlap. Sigue.

2. **Hilo Ejecutor 1 Sprint MEGA-CIERRE-HOY TA3** trabajando en `kernel/cowork_runtime/` Railway flags (COWORK_HOOK_ENABLED + COWORK_SESSION_PERSIST + COWORK_PREFLIGHT_REQUIRED). **NO tocar `kernel/cowork_runtime/`.**

3. **Hilo Perplexity T2-B** activo en PBA — convergencia post-cierre tu sprint.

4. **PR #110** Pre-Response Hook OBSERVE-ONLY (Perplexity T2-B Hook) `feat/t1-pre-response-hook-observe-only` — CI pending. **NO tocar `kernel/cowork_runtime/pre_response_hook.py`.**

**SÍ podés tocar:**
- `kernel/escape/` (crear desde cero — NO EXISTE)
- `kernel/dashboards/escape_history.py` (nuevo)
- `kernel/embrion_loop.py` ÚNICAMENTE entre marcadores `ESCAPE_BEGIN`/`ESCAPE_END` que vos agregás (patrón ROTOR replicado)
- `kernel/embrion_budget.py` función `consume()` (verificá si ya existe primero — si sí, refactor; si no, crear)
- `migrations/sql/0026_escape_pulse_log.sql` (número confirmado libre)
- `tests/test_escape_*.py` (nuevos)

## §5 — Override CI rojo

Mismo patrón que GUARDIAN + ROTOR + MOBILE-REALIGNMENT: si los 17 jobs CI tienen ≥4 PRE-EXISTENTES fallando rojo SIN relación al sprint ESCAPE-001, podés override-defendible con audit Cowork DSC-G-008 v2 verde + audit T2-B PBA convergente. **Bypass directo a main prohibido** para PRs write-risky T1+T2+T3+T4.

## §6 — Cadencia de reportes esperada

- **T1 cerrada (migración aplicada local + tests):** `bridge/manus_to_cowork_ESCAPE_T1_DONE_2026_05_12.md`
- **T2 cerrada (Throttler core 15+ tests):** `bridge/manus_to_cowork_ESCAPE_T2_DONE_2026_05_12.md`
- **T3 cerrada (wiring loop con marcadores):** `bridge/manus_to_cowork_ESCAPE_T3_DONE_2026_05_12.md`
- **Sprint completo:** `bridge/manus_to_cowork_REPORTE_ESCAPE_001_2026_05_12.md` con frase canónica `⚙️ ESCAPE-001 — DECLARADO (6/6 verde)` solo si las 6 tareas pasan + 25+ tests verde + audit Cowork + T2-B convergencia.

## §7 — Permiso de merge (regla evolucionada 2026-05-11+12)

- **PRs write-safe (T5 dashboard, T6 placeholder):** push directo a main bajo DSC-G-008 v2.
- **PRs write-risky (T1 migración, T2 throttler, T3 wiring, T4 budget):** PR limpio + tag `[ESCAPE-001]`, Cowork audita DSC-G-008 v2 v2 + T2-B verifica PBA trigger 3.
- **Self-merge prohibido para write-risky.**

## §8 — Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint ESCAPE-001 CERRADO. Throttler determinístico + escape_pulse_log + wiring embrion_loop con marcadores ESCAPE_BEGIN/END. Pieza Escape #2 magna Reloj Suizo activa post-ROTOR-001. Doctrina canónica honrada §2.1+§3+§4 RELOJ_SUIZO. Cowork audita DSC-G-008 v2 verde + T2-B PBA trigger 3 convergente.',
  'manus-hilo-ejecutor-2',
  9
);
```

## §9 — Autoridad y cierre

- T1 (Alfredo) firmó spec ESCAPE-001 2026-05-12 ~07:55 UTC ("te firmo los 5 incluyendo el 5 de xcode")
- T2-A (Cowork) firma kickoff multi-decisión y arma reglas duras NO-CRUCE post-firma
- T3 (Hilo Ejecutor 2) ejecuta autónomamente bajo §4 reglas duras
- ETA realista: 90-120 min reales (similar a ROTOR-001 velocity demostrada)

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 07:58 UTC
**Gate verde:** ESCAPE-001 spec FIRME T1 + autorización Brand Engine canary aplicar post-ESCAPE. Esperá PR #113 merge → arrancá inmediatamente. Reporte de cierre con frase canónica `⚙️ ESCAPE-001 — DECLARADO (6/6 verde)` esperado en bridge en ~120 min.
