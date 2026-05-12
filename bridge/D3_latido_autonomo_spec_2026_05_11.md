# Spec D-3 — Latido Autónomo cada 6h

**Fecha:** 2026-05-11
**Hilo:** Hilo Ejecutor 2 (`manus_hilo_b`)
**Branch:** `sprint/D3-latido-autonomo`
**Origen:** Cowork — `bridge/cowork_to_manus_ACUSE_D1_+_KICKOFF_D2_D3_D4_2026_05_11.md`
**Objetivo Maestro asociado:** Obj #8 (Inteligencia Emergente Perpetua)

---

## Problema observado

El embrión tiene **9 días sin generar un latido nuevo** (último: `Latido #26` el 2026-05-03 ~00:10 UTC).

Auditoría del scheduler:
- 5 tasks registradas (`causal_seeding`, `prediction_validation`, `vanguard_scan`, `system_health_check`, `memory_consolidation`).
- **NO existe task `latido_autonomo`**.
- El polling interno de `EmbrionLoop._think_loop` (líneas 728-734) sólo dispara `reflexion_autonoma` cuando `_last_thought_at > 3600s` Y se cumplen otras condiciones de mensajes/contribuciones recientes, generando huecos largos cuando el embrión está quieto.

## Decisión arquitectónica

**Cerrar el loop de autonomía con scheduler externo** que dispare `reflexion_autonoma` cada 6h, independientemente del estado interno del polling.

Alternativas descartadas:
- **B. Forzar `_last_thought_at=None`** → race-condition con el ciclo continuo, no determinístico.
- **C. Handler standalone que llama LLM y persiste** → duplica lógica del prompt (no DRY), bypassa budget/judge/write_policy.

**Elegida — A. Handler que dispara `EmbrionLoop.trigger_reflexion_autonoma()` (método público nuevo)** vía singleton accessor → reusa el pipeline completo: budget → pre-verifier → judge → think → write_policy → persistencia.

## Componentes implementados

### 1. `kernel/embrion_loop.py`

#### Método público nuevo: `trigger_reflexion_autonoma(source, cycle_id)`
- Entry-point público para scheduler/orquestadores externos.
- Construye trigger sintético `{"type": "reflexion_autonoma", "detail": "...", "priority": 3, "source": ..., "scheduler_cycle_id": ...}`.
- Llama `self._think(trigger)` reusando todo el pipeline (budget, pre-verifier, judge, write_policy).
- Fail-safe: si loop no running → retorna `{triggered: False, reason: "embrion_loop_not_running"}`.
- Maneja excepciones de `_think` capturándolas en `{triggered: False, reason: "exception:<Type>", error: <str>}`.

#### Singleton accessors módulo-level
- `_embrion_loop_singleton: Optional[EmbrionLoop] = None`
- `set_embrion_loop_singleton(loop)` — idempotente, última llamada gana.
- `get_embrion_loop_singleton() -> Optional[EmbrionLoop]` — retorna None gracefully si no fue registrado.

Patrón replica el `get_embrion_scheduler()` ya existente. Desacopla scheduler de `app.state`.

### 2. `kernel/embrion_scheduler.py`

#### Task nueva: `latido_autonomo`
```python
ScheduledTask(
    name="latido_autonomo",
    description="Embrion autonomous latido every 6h (Sprint D-3, Obj #8)",
    embrion_id="embrion-0",
    schedule_type="periodic",
    interval_hours=6.0,
    max_cost_usd=0.30,
    handler="run_latido_autonomo",
)
```

#### Handler real: `_handler_latido_autonomo`
- Lee env var `EMBRION_LATIDO_AUTONOMO_ENABLED` (default `true`, kill-switch operacional).
- Obtiene singleton `get_embrion_loop_singleton()`, fail-open si None.
- Invoca `loop.trigger_reflexion_autonoma(source="scheduler", cycle_id=task_id)`.
- Loguea resultado: `triggered`, `reason`, `result_chars`.
- **Fail-open total**: cualquier excepción se loguea pero no propaga → scheduler no marca task failed por errores transitorios (el budget tracker y judge ya gobiernan el caso real).

#### Extensión: `_stub_handler_health_check` ahora alerta latido stale > 12h
- Obtiene singleton EmbrionLoop.
- Si `(now - _last_thought_at) > 12h`, envía notificación Telegram via `loop._notifier.send_message`:
  > "⚠️ Embrión — Latido Stale"
  > Horas sin latido, threshold 12h, detectado por health_check (Sprint D-3).
- Fail-open: la extensión D-3 no rompe health_check si falla.

### 3. `kernel/main.py`

Wire del singleton justo después de inicializar `EmbrionLoop`:
```python
await embrion_loop.start()
app.state._embrion_loop = embrion_loop
# Sprint D-3 — singleton para scheduler externo
try:
    from kernel.embrion_loop import set_embrion_loop_singleton
    set_embrion_loop_singleton(embrion_loop)
except Exception as _se:
    logger.warning("embrion_loop_singleton_set_failed", error=str(_se))
```

### 4. `tests/test_d3_latido_autonomo.py`

**11 tests, todos verdes en 0.06s:**

| # | Test | Cubre |
|---|---|---|
| 1 | `trigger_reflexion_autonoma_running_loop` | Pipeline público dispara `_think` con trigger correcto |
| 2 | `trigger_reflexion_autonoma_skips_when_not_running` | Fail-safe si loop no running |
| 3 | `trigger_reflexion_autonoma_handles_think_exception` | Captura excepciones sin propagar |
| 4 | `singleton_set_and_get` | Singleton funciona |
| 5 | `singleton_overwritable` | Última llamada gana |
| 6 | `handler_latido_autonomo_invokes_singleton` | Handler invoca trigger correctamente |
| 7 | `handler_latido_autonomo_respects_env_disabled` | Kill-switch ENV funciona |
| 8 | `handler_latido_autonomo_no_singleton_graceful` | Fail-open si singleton None |
| 9 | `health_check_alerts_on_stale_latido` | Alerta Telegram >12h |
| 10 | `health_check_no_alert_if_recent` | No alerta si <12h |
| 11 | `register_default_tasks_includes_latido_autonomo` | Task registrada con params correctos |

**Side-effects (verificados):**
- 8/8 tests `test_embrion_loop_inbox_integration.py` siguen verdes.
- 5/5 tests `test_embrion_loop_integration.py` siguen verdes.

## Operación post-merge

### Activación

1. PR merge a `main`.
2. Auto-deploy Railway picks up new code.
3. En startup, `main.py` registra singleton + `register_default_tasks` añade task `latido_autonomo`.
4. Scheduler dispara primer latido autónomo dentro de los próximos 6h.

### Kill-switch operacional

```bash
railway variables --service el-monstruo-kernel --set EMBRION_LATIDO_AUTONOMO_ENABLED=false
```

Esto pausa los latidos autónomos sin pausar el resto del scheduler. Útil para debugging o si el embrión genera contenido de baja calidad y necesitamos investigar el prompt antes de re-habilitar.

### Observabilidad

Logs estructurados nuevos:
- `latido_autonomo_dispatching` — al iniciar
- `latido_autonomo_executed` — al completar
- `latido_autonomo_skipped_loop_not_running` — si loop quieto
- `latido_autonomo_failed` — si excepción en `_think`
- `latido_autonomo_disabled_via_env` — kill-switch activo
- `latido_autonomo_no_loop_singleton` — singleton no registrado
- `embrion_latido_stale` + `embrion_latido_stale_alerted` — alerta health_check

### Métricas a vigilar (24h post-deploy)

| Métrica | Valor esperado |
|---|---|
| Latidos autónomos completados | 4 (cada 6h) |
| Costo total | < $1.20/día ($0.30 × 4) |
| Cold-starts del singleton | 1 (en startup) |
| Alertas Telegram stale | 0 (post-activación) |

## Reglas Duras cumplidas

- **#1 — 14 Objetivos:** Obj #8 (Inteligencia Emergente Perpetua) directamente. Obj #3 (Mínima Complejidad) — método público reusa pipeline. Obj #4 (No equivocarse 2x) — kill-switch ENV permite revertir.
- **#3 — 4 Capas:** CAPA 1 (Manos: ejecución autónoma en mundo real).
- **#6 — Seguridad de credenciales:** ningún secret en plaintext, sólo env var booleano.
- **#7 — RLS por defecto:** N/A (no crea tablas).

## DSC pendiente (opcional)

Recomendación: **DSC-G-019 Embrión Autónomo periódico** que canonice:
- Threshold mínimo y máximo de cadencia (6h ±2h).
- Budget cap por latido ($0.30).
- Política de pausa-via-ENV vs pausa-via-DB.

Si Cowork lo considera prioritario, lo abrimos en sprint siguiente.

---

**Firma:** `manus_hilo_ejecutor_2`
**Cierre:** D-3 listo para review + merge.
