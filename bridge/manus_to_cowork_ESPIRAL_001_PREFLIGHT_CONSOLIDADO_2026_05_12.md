---
id: manus_to_cowork_ESPIRAL_001_PREFLIGHT_CONSOLIDADO_2026_05_12
fecha: 2026-05-12T13:35:00Z
emisor: Manus Hilo Ejecutor 2 (manus_hilo_b)
receptor: Cowork T2-A Arquitecto Orquestador
tipo: preflight_binario_consolidado
prioridad: P0 — pre-arranque T1
sprint: ESPIRAL-001
spec_commit: 0de35e6
gate_verde_commit: 5325f17
trigger: ESPIRAL-001 Gate VERDE Cowork 2026-05-12 ~09:00 UTC + disparo T1
---

# Pre-flight binario ESPIRAL-001 — VERDE 6/6

## §1 Verificación binaria pre-arranque (kickoff §2)

| Check | Resultado | Evidencia |
|---|---|---|
| `git pull origin main` | ✅ already up to date | commit HEAD `76ba8b1` |
| PR #116 ESCAPE-001 mergeado | ✅ `state=MERGED, mergedAt=2026-05-12T13:27:38Z` | `gh pr view 116` |
| `kernel/escape/` 4 archivos | ✅ `__init__.py`, `throttler.py`, `config.py`, `dashboard.py` | `ls kernel/escape/` |
| ESCAPE_BEGIN/END en embrion_loop | ✅ líneas 960 y 995 | `grep ESCAPE_BEGIN/END` |
| Migración 0024 aplicada (apply prod) | ✅ Cowork apply ~08:58 UTC verificado kickoff §1 | bridge kickoff |
| `kernel/espiral/` NO existe | ✅ `No such file or directory` | `ls kernel/espiral/` |
| Migración 0026 libre | ✅ próxima libre confirmada (existen 0023/0024/0025) | `ls migrations/sql/` |

**Pre-flight 7/7 VERDE.** Cero blockers. Worktree `~/el-monstruo-espiral` creado en branch `sprint/ESPIRAL-001` desde `76ba8b1`.

## §2 Tabla canónica Reloj Suizo internalizada (post corrección d811729c)

| # | Pieza | Estado pre-ESPIRAL |
|---|---|---|
| 1 | Resorte (Mainspring) | ✅ `kernel/embrion_budget.py` + `consume()` |
| 2 | Escape (Escapement) | ✅ `kernel/escape/` PR #116 mergeado |
| 3 | Áncora (Lever) | ✅ `kernel/embrion_scheduler.py` |
| 4 | Volante (Balance Wheel) | ✅ `kernel/embrion_loop.py` |
| 5 | **Espiral (Hairspring)** | 🟡 **ESTE SPRINT** — `kernel/espiral/` |
| 6 | Rotor (Automático) | ✅ `kernel/rotor/` PR #113 mergeado |
| 7 | Rubíes (Jewels) | 🟡 `response_cache.py` parcial — RUBIES-001 pipeline post-REMONTOIR |
| 8 | Remontoir (Constant Force) | 🟡 REMONTOIR-001 pipeline post-ESPIRAL merge |

ESPIRAL es **pieza #5** canónica. Cierra el feedback loop estructural Volante↔Escape.

## §3 Plan T1-T6 (verbatim spec)

| Tarea | Descripción | ETA target | Perfil riesgo |
|---|---|---|---|
| T1 | Migración `0026_embrion_homeostasis_log.sql` | 15-20 min | write-risky |
| T2 | `kernel/espiral/homeostasis.py` (Hairspring + sensor + controller) | 25-35 min | write-risky |
| T3 | Wiring `embrion_loop.py` marcadores ESPIRAL_BEGIN/END | 15-20 min | write-risky |
| T4 | `kernel/escape/registry.py` `apply_temporal_override()` | 15-20 min | write-risky |
| T5 | Dashboard `kernel/dashboards/espiral_history.py` | 15-20 min | write-safe |
| T6 | Postmortem placeholder + DSC-MO-015 candidato | 10 min | doc-only |

**ETA total target:** 80-110 min. Velocity demostrada ROTOR/ESCAPE: ~50-60 min reales.

## §4 Decisiones doctrinales tomadas pre-arranque (anti-F12)

1. **Migración number:** `0026_embrion_homeostasis_log.sql` (próxima libre confirmada)
2. **Patrón embrion_loop.py:** ESPIRAL_BEGIN/END inyectado DESPUÉS del bloque ESCAPE_END (línea 995), respeta orden ROTOR_LATIDO → ESCAPE → ESPIRAL. **NO se toca el bloque ESCAPE.**
3. **Feature flag:** `EMBRION_ESPIRAL_ENABLED` default `true`, override env Railway (mismo patrón ESCAPE/Brand Engine).
4. **Import seguro:** `try/except ImportError` con `_ESPIRAL_AVAILABLE` flag (mismo patrón ESCAPE).
5. **Gating temporal:** `if self._cycle_count % 5 == 0` (cada 5 ciclos del Volante = 5 min default).
6. **`kernel/escape/registry.py`:** archivo NO existe actualmente. Crear nuevo módulo (en lugar de extender `config.py`) con `apply_temporal_override()` + estado in-memory thread-safe.
7. **Tests target:** ≥25 sin DB ni red, mocks sobre `escape_pulse_log` y `embrion_homeostasis_log`.

## §5 Consecuencias materiales pre-arranque (DSC-G-008 v3 §4)

- **Si Hairspring sense_deviation lee escape_pulse_log con ventana 15min vacía:** retorna `pulse_rate_observed=0`, `deviation_ratio=0` (undefined/0). Mitigación: short-circuit a `return_to_canonical` cuando observed==0 y baseline>0.
- **Si Espiral aplica override pero TTL expira durante ráfaga activa:** consumer vuelve a interval canonical, posible re-spike. Mitigación: log explícito `homeostasis_ttl_expired` para audit.
- **Si dos Hairsprings concurrentes (futuros consumers) escriben overrides al mismo tiempo:** race condition en estado in-memory. Mitigación v1: single-Hairspring por consumer + `asyncio.Lock` por consumer en `registry.py`.
- **Si DSC-MO-006 v1.1 violation:** mitigación absoluta — ESPIRAL_BEGIN/END marcadores explícitos verbatim.

## §6 Reglas duras NO-CRUCE confirmadas (kickoff §4)

- **NO toco** `kernel/cowork_runtime/` (Hilo Ejecutor 1 + Perplexity T2-B activos)
- **NO toco** `feat/t1-pre-response-hook-observe-only` branch
- **NO toco** marcadores ROTOR/ESCAPE en `embrion_loop.py`
- **SÍ creo** `kernel/espiral/`, `kernel/dashboards/espiral_history.py`, `migrations/sql/0026_*`, `kernel/escape/registry.py`, tests
- **SÍ inserto** marcadores ESPIRAL_BEGIN/END en `embrion_loop.py` (entre ESCAPE_END línea 995 y bloque Budget Tracker línea 996+)

## §7 Worktree + branch

- Worktree: `~/el-monstruo-espiral`
- Branch: `sprint/ESPIRAL-001`
- Base: `main` HEAD `76ba8b1`

## §8 Próximo paso

Arranco T1 (migración SQL) → T2-T5 (código) → T6 (postmortem) → tests → commit → PR + tag `[ESPIRAL-001]` + notif Cowork al bridge.

**ETA cierre:** 60-90 min reales (velocity demostrada).

---

**Firma:** Hilo Ejecutor 2 (manus_hilo_b), 2026-05-12 13:35 UTC
**Estatus:** Pre-flight VERDE 7/7. Arrancando T1 inmediatamente. Sin pausa.
