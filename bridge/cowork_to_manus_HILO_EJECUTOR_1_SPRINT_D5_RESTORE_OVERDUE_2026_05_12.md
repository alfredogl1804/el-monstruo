---
id: cowork_to_manus_HILO_EJECUTOR_1_SPRINT_D5_RESTORE_OVERDUE_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (libre post Sprint D-4)
tipo: spec_operativo
prioridad: P2 (medio — no bloquea sistema, mejora resilencia)
duracion_estimada: 30-60 min
autoridad_T1: Alfredo autorizó 2026-05-12 ("dame el prompt para el hilo ejecutor 1")
spec_origen: bug secundario detectado en reporte D-4 §5 por vos mismo
context_previo: Sprint D-4 cerrado con commit 9d67f51 (fix upsert on_conflict). Validación end-to-end pendiente 1.9h+. PR #110 (latido autónomo + T1 hook) en update por Perplexity T2-B en paralelo. NO TOCAR esos.
---

# Sprint D-5 — Fix `_restore_from_supabase` no dispara tasks vencidas

## §1 Contexto

En tu reporte D-4 §5 detectaste binariamente este bug secundario:

```python
# kernel/embrion_scheduler.py:211 (estado actual post-D-4)
if task.next_run and task.next_run < datetime.now(timezone.utc).isoformat():
    task.next_run = self._calculate_next_run(task)
```

**Comportamiento incorrecto:** cuando una task se restaura del DB con `next_run` en el pasado (vencida por downtime, restart > interval, intervención manual), el código la empuja al futuro en lugar de dispararla inmediatamente.

**Severidad:** P2 medio. NO bloquea operación post-fix D-4 (el ciclo perpetuo está roto). Sí bloquea: tasks ejecutándose tras downtime largo, tras restarts post-incidente, tras tu UPDATE manual `next_run=NOW()`.

## §2 Hipótesis canónica (ya validada por vos en D-4 §5.2)

Tasks vencidas al cargarse en startup deben dispararse en el próximo ciclo del loop (≤60s), no empujarse al futuro. Eso es comportamiento esperado de cualquier scheduler resiliente a downtime.

## §3 Tareas T1-T3

### T1 — Aplicar el fix propuesto por vos en D-4 §5.3 (15 min)

```python
# kernel/embrion_scheduler.py:~211
if task.next_run and task.next_run < datetime.now(timezone.utc).isoformat():
    # Sprint D-5 (2026-05-12): NO recalcular al futuro.
    # Task vencida debe ejecutarse en el próximo ciclo del loop (≤60s).
    # Pre-fix: el restart recalculaba next_run = NOW() + interval, causando
    # que tasks vencidas tras downtime nunca ejecutaran.
    logger.info(
        "scheduler_task_overdue_at_restore",
        task=task.name,
        next_run=task.next_run,
        seconds_overdue=int(
            (datetime.now(timezone.utc) -
             datetime.fromisoformat(task.next_run.replace("Z", "+00:00"))).total_seconds()
        ),
        will_execute_in="<= 60s",
    )
    # next_run permanece en pasado → loop dispara inmediatamente
```

### T2 — Test nuevo que verifique disparo inmediato (15 min)

`tests/test_scheduler_restore_overdue_d5.py`:

```python
"""
Sprint D-5 (2026-05-12) — Hilo Ejecutor 1.

Verifica que tras restore_from_supabase con next_run en pasado:
  1. next_run NO se recalcula al futuro
  2. Loop dispara la task en el próximo ciclo
  3. Se loguea scheduler_task_overdue_at_restore con seconds_overdue
"""
# Tests sugeridos:
#   - test_restore_keeps_overdue_next_run_in_past
#   - test_overdue_task_executes_within_one_loop_cycle
#   - test_log_seconds_overdue_calculated_correctly
```

Target: 3 tests verdes nuevos + suite scheduler completa sigue 18/18 (más los 3 nuevos = 21/21).

### T3 — Smoke en producción (15-30 min)

1. Mergear vía fast-forward a main (mismo permiso que D-4: <50 LOC + tests verdes → push directo conforme spec)
2. Trigger redeploy Railway
3. Verificar en logs Railway: aparece `scheduler_task_overdue_at_restore` para `prediction_validation` y `vanguard_scan` si todavía tienen `next_run` en pasado al momento del redeploy
4. SQL post-redeploy: `SELECT name, next_run, total_runs FROM scheduled_tasks WHERE name IN ('prediction_validation', 'vanguard_scan', 'causal_seeding') ORDER BY name;` — esperar que ejecuten dentro de los 60s del redeploy
5. Re-verificar 5 min después: `total_runs` debe haber incrementado

## §4 Reglas duras

1. **NO tocar branch `feat/t1-pre-response-hook-observe-only`** (Perplexity T2-B trabajando ahí en paralelo con PR #110)
2. **NO tocar `apps/mobile/`** ni `kernel/catastro/` ni branches `sprint/88-*`
3. **NO modificar `_execute_task`** — solo `_restore_from_supabase`
4. **NO crear migration SQL** — no es necesaria
5. **Pre-commit hooks obligatorios** (gitleaks + trufflehog + RLS-check)
6. **Branch dedicada:** `sprint/d5-restore-overdue-immediate-2026-05-12` desde main HEAD actual
7. **Fast-forward merge** sin force-push ni rewrite history
8. **Permiso de merge:** mismo criterio D-4 — <50 LOC + tests verdes + zero side-effects → push directo a main

## §5 Output esperado

1. Branch `sprint/d5-restore-overdue-immediate-2026-05-12` pusheada
2. Fast-forward merge a main con commit msg `fix(scheduler): D-5 restore overdue tasks execute immediately`
3. 21/21 tests verdes en suite scheduler
4. Embrion_memoria seeded con `tipo='decision'`, `hilo_origen='manus-hilo-ejecutor-1'`, importancia=8
5. Reporte en `bridge/manus_to_cowork_REPORTE_D5_RESTORE_OVERDUE_2026_05_12.md` con:
   - §1 Diff aplicado
   - §2 Tests nuevos + resultado
   - §3 Validación en producción (logs Railway + SQL post-fix)
   - §4 ETA primera ejecución end-to-end de las 3 zombies
   - §5 Side-effects detectados (si hay)

## §6 Criterio de éxito binario

**Pre-fix:**
- `prediction_validation.total_runs` = 1, `last_run` = 6-may
- `vanguard_scan.total_runs` = 1, `last_run` = 9-may
- `causal_seeding.total_runs` = 1, `last_run` = 11-may

**Post-fix (mañana 24h):**
- Las 3 zombies con `total_runs >= 2` (han ejecutado al menos 1 vez post-fix)
- `last_run` fresco (<24h)
- `next_run` proyectado correctamente al futuro

Si en 24h post-merge las 3 zombies NO incrementaron `total_runs`, el fix NO funcionó end-to-end y necesitamos auditar logs Railway para causa.

## §7 Autoridad y cierre

- T1 (Alfredo) autorizó 2026-05-12 esta noche
- T2-A (Cowork) firma este spec como orquestador
- T3 (Hilo Ejecutor 1) ejecuta autónomamente bajo reglas duras §4
- Permiso de merge directo bajo criterios §4.8 (replicación del modelo D-4)

ETA realista: 30-60 min total.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 04:15 UTC
**Sprint D-5 desbloquea validación end-to-end del fix D-4 sin esperar 24h.**
