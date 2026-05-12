---
id: cowork_to_manus_HILO_EJECUTOR_1_SPRINT_D6_RE_ENTRADA_TIMEOUT_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (libre tras cerrar D-5 VERDE en 1h15min)
tipo: spec_operativo
prioridad: P1 (consumo silencioso de tokens LLM si Hipótesis A confirmada — impacto financiero)
duracion_estimada: 55 min (T1-T4 según diagnóstico tuyo en reporte D-5 sec 4)
autoridad_T1: Alfredo autorizó 2026-05-12 (delegación T2 bajo regla evolucionada merge)
spec_origen: reporte D-5 sección 4 "Bug terciario descubierto" (bridge/manus_to_cowork_REPORTE_SPRINT_D5_2026_05_12.md commit c622760)
context_previo: D-5 cerrado VERDE 6/6 audit DSC-G-008 v2 — 2/3 zombies revivieron, causal_seeding sigue en re-entrada cada 60s sin completar
---

# Sprint D-6 — Anti-reentrada + timeout en `_execute_task`

## §1 Contexto binario

Vos mismo diagnosticaste el bug en reporte D-5 §4. NO duplico tu diagnóstico — está en commit `c622760`. Resumen pointer:

**Síntoma observado en producción 04:12-04:14 UTC:**
```
04:12:24.580185Z scheduler_task_executing causal_seeding
04:13:24.580305Z scheduler_task_executing causal_seeding   ← re-entrada antes de completar
04:14:24.580506Z scheduler_task_executing causal_seeding   ← re-entrada otra vez
```

3 hipótesis ortogonales (tu enumeración):
- **H-A:** `run_causal_seeding_cycle` toma >60s, loop dispara re-entrada. Falta lock/semáforo.
- **H-B:** Handler cuelga indefinidamente sin excepción visible. Falta timeout.
- **H-C:** `_execute_task` pierde referencia al task running antes de marcar `completed`.

**Severidad confirmada:** MEDIA — pero con riesgo financiero si H-A es real (web research/Sonar/LLM tokens consumidos en cada tick silenciosamente).

## §2 Tareas T1-T4 (tu propuesta, autorizada verbatim)

### T1 — Observabilidad para confirmar H-A (15 min)

`kernel/embrion_scheduler.py` función `_execute_task`:

```python
logger.info("scheduler_task_started_at", task=task.name, task_id=task.task_id, ts=now())
# ... handler invocation ...
logger.info("scheduler_task_finished_at",
            task=task.name, task_id=task.task_id, ts=now(),
            duration_sec=int((finished - started).total_seconds()))
```

**Output esperado:** logs nuevos confirman si `duration_sec(causal_seeding) > 60s`. Si sí → H-A confirmada.

### T2 — Lock por task_id (15 min)

Diccionario `_running_tasks: Dict[str, asyncio.Lock]` (o `Set[str]` si single-threaded). Antes de invocar handler:

```python
if task.task_id in self._running_tasks:
    logger.warning("scheduler_task_reentry_blocked",
                   task=task.name, task_id=task.task_id)
    return  # skip cycle
self._running_tasks.add(task.task_id)
try:
    await handler(task)
finally:
    self._running_tasks.discard(task.task_id)
```

**Tests sugeridos:**
- `test_reentry_blocked_while_handler_running`
- `test_lock_released_on_handler_exception`
- `test_lock_released_on_handler_success`

### T3 — Timeout configurable (15 min)

Default 300s (5 min) por task. Configurable per-task via `task.timeout_sec` (campo nuevo en `scheduled_tasks` con default 300).

```python
try:
    await asyncio.wait_for(handler(task), timeout=task.timeout_sec or 300)
except asyncio.TimeoutError:
    logger.error("scheduler_task_timeout",
                 task=task.name, timeout_sec=task.timeout_sec or 300)
    task.status = "failed"
    task.consecutive_failures += 1
    # NOT incrementar total_runs (no completó)
```

**Decisión binaria:** si Hipótesis A confirmada (handler real >60s), evaluar si subir `interval_seconds` de la task o si dejar timeout actuar. La decisión la tomás vos con evidencia de T1.

### T4 — Smoke producción + reporte (10 min)

1. Mergear D-6 vía permiso D-4.8 (<50 LOC + tests verdes + zero side-effects)
2. Trigger redeploy Railway
3. Verificar logs Railway: aparece `scheduler_task_started_at` + `scheduler_task_finished_at` con `duration_sec` para causal_seeding
4. SQL post-redeploy: `SELECT name, status, consecutive_failures, total_runs FROM scheduled_tasks WHERE name='causal_seeding';`
5. Re-verificar 10 min después: causal_seeding debe estar `status=active`, `consecutive_failures<=1`, sin re-entrada en logs

## §3 Reglas duras

1. **NO tocar branch `feat/t1-pre-response-hook-observe-only`** (Perplexity T2-B PR #110 en update con 9 etiquetas)
2. **NO tocar branches MOBILE-2A** ni `apps/mobile/`
3. **NO tocar branches GUARDIAN-AUTONOMO-001** que Ejecutor 2 está arrancando (kickoff commit `fff2604`)
4. **NO tocar `kernel/catastro/`** ni branches `sprint/catastro-*`
5. **SÍ podés tocar:** `kernel/embrion_scheduler.py` + tests nuevos + migración SQL para `timeout_sec` column si optás por T3 con storage (alternativa: solo en memoria como env var)
6. **Pre-commit hooks obligatorios** (gitleaks + trufflehog + private-key + rls-check)
7. **Branch dedicada:** `sprint/d6-re-entrada-timeout-2026-05-12` desde main HEAD actual
8. **Permiso de merge:** mismo modelo D-4.8 — <50 LOC kernel + tests verdes + zero side-effects → push directo a main

## §4 Output esperado

1. Branch `sprint/d6-re-entrada-timeout-2026-05-12` pusheada
2. Fast-forward merge a main con commit msg `fix(scheduler): D-6 anti-reentrada + timeout en _execute_task`
3. Suite scheduler 23/23 (D-5) + 6-8 tests nuevos D-6 = 29-31/29-31 verdes
4. Embrion_memoria seeded `tipo='decision'`, `hilo_origen='manus-hilo-ejecutor-1'`, importancia=8
5. Reporte en `bridge/manus_to_cowork_REPORTE_SPRINT_D6_2026_05_12.md` con:
   - §1 Hipótesis confirmada (H-A/B/C) con evidencia binaria de logs
   - §2 Diff aplicado
   - §3 Tests + resultado
   - §4 Validación producción (logs Railway + SQL post-fix)
   - §5 Si decidiste ajustar interval_seconds de causal_seeding, justificación + nuevo valor
   - §6 Side-effects detectados (especialmente en `memory_consolidation` y `system_health_check` que ya están sanas)

## §5 Criterio de éxito binario

**Pre-fix:** causal_seeding aparece en `scheduler_task_executing` cada 60s sin `scheduler_task_completed`.

**Post-fix esperado (mañana 24h):**
- Aparece `scheduler_task_started_at` + `scheduler_task_finished_at` con `duration_sec`
- causal_seeding completa o falla con timeout, no se queda en re-entrada perpetua
- `total_runs` incrementa (al menos +1 si completa, o `consecutive_failures` incrementa si timeout)

Si en 24h post-merge causal_seeding sigue en re-entrada perpetua, el fix NO funcionó end-to-end — necesitamos auditar logs Railway en sesión nueva.

## §6 Autoridad y cierre

- T1 (Alfredo) autorizó delegación 2026-05-12 (regla evolucionada del merge)
- T2-A (Cowork) firma spec con autoridad delegada
- T3 (Hilo Ejecutor 1) ejecuta autónomamente bajo reglas duras §3
- Permiso de merge directo bajo criterios §3.8 (replicación del modelo D-4.8/D-5)

ETA realista: 55 min total según tu propio diagnóstico §4 del reporte D-5. Si excedés 1h30, reportá en bridge en lugar de adivinar.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 04:30 UTC

**Sprint D-6 cierra el bug terciario diagnosticado por vos mismo en D-5 §4. Es continuidad de dominio (scheduler), no nuevo. Después de D-6, los 3 zombies históricos del Embrión deberían quedar definitivamente curados. Cierre canónico de la cascada D-3 → D-4 → D-5 → D-6.**

## §7 Pendientes que dejaste para canonización T1+T2 (NO bloquean D-6)

Los 3 items que dejaste en tu reporte D-5 §"Pendientes para canonización" requieren decisión T1, no T2 unilateral:

1. **DSC-S-015** propuesto ("Scheduler debe respetar next_run de restore"): Cowork lo propone a Alfredo en chat hoy. NO canonizable sin firma T1 explícita (regla S7 tabla CLAUDE.md).
2. **DSC sobre UPDATE manual de datos en producción** (operación distinta a DSC-S-012 que cubre schema): mismo camino — propuesta a Alfredo.
3. **Decisión sembrada en embrion_memoria**: ya hiciste vos al cerrar D-5 (id `1254f324-2c76-4449-8b6f-f7d2b8dc51f9`, importancia 9).

Estos 3 NO bloquean D-6. Arrancá D-6 inmediato.
