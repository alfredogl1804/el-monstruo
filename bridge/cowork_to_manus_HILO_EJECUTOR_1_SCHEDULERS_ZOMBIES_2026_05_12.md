---
id: cowork_to_manus_HILO_EJECUTOR_1_SCHEDULERS_ZOMBIES_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2 Arquitecto
receptor: Manus Hilo Ejecutor 1 (libre HOY según T1 Alfredo)
tipo: spec_operativo_de_diagnostico
prioridad: P1
duracion_estimada: 1-3h
autoridad_T1: Alfredo autorizó 2026-05-12 02:55 UTC ("se haria hoy daselo a hilo ejecutor 1 esta libre")
context_previo: PR #104 latido_autonomo MERGEADO commit 807eda4a — NO TOCAR esa branch
---

# Spec — Diagnóstico de 3 Schedulers con `last_run` Antiguo

## §1 Contexto

Cowork detectó hoy 2026-05-12 02:50 UTC que **3 tareas del `embrion_scheduler` tienen `last_run` sospechosamente antiguo** comparado con su periodicidad declarada. Pero **Cowork NO confirmó binariamente que estén caídas**. Solo confirmó que la telemetría parece rara. Necesitamos diagnóstico con logs reales.

## §2 Data binaria de Supabase (verificada por Cowork 2026-05-12 02:50 UTC)

Query ejecutada: `SELECT name, status, paused, consecutive_failures, total_runs, last_run, next_run, handler, max_cost_usd FROM scheduled_tasks ORDER BY name;`

| Task | status | paused | consec_failures | total_runs | last_run | next_run | Análisis |
|---|---|---|---|---|---|---|---|
| causal_seeding (6h periodic) | active | false | **0** | **1** | 11-may 00:03 | 11-may 06:03 | next_run 27h en pasado. Si periodic 6h y existe desde 10-may → debería haber ~9 runs, tiene 1 |
| prediction_validation (daily 3am) | active | false | **0** | **1** | 6-may 03:00 | 7-may 03:00 | next_run 5 días en pasado. Si daily desde 6-may → debería haber 6 runs, tiene 1 |
| vanguard_scan (daily 6am) | active | false | **0** | **1** | 9-may 06:00 | 10-may 06:00 | next_run 2 días en pasado. Si daily desde 9-may → debería haber 3 runs, tiene 1 |
| system_health_check (2h periodic) | active | false | 0 | **1** | 12-may 01:05 | 12-may 03:05 | **SANA** (corrió hace ~2h) — pero total_runs=1 también es raro si corre cada 2h |
| memory_consolidation (daily 2am) | active | false | 0 | **1** | 12-may 02:00 | 13-may 02:00 | **SANA** (corrió hace ~50min) — pero total_runs=1 raro |
| latido_autonomo (6h periodic) | active | false | 0 | 0 | null | 12-may 08:50 | recién agregada hoy, esperado |

## §3 4 Hipótesis a verificar (NO inventar causa raíz, probar)

**H1 — Caídas reales:** las 3 tasks NO están ejecutándose. `consecutive_failures=0` engaña porque los handlers son STUBS que solo loguean y nunca lanzan excepción.

**H2 — Bug en persistencia de `total_runs`/`last_run`:** las tasks SÍ corren pero el contador no acumula y el `last_run` no se actualiza. Evidencia: TODAS las tasks (incluyendo las 2 sanas) tienen `total_runs=1`. Inconsistente con periodicidad declarada (system_health_check debería tener ~24+ runs).

**H3 — Daily budget exhausto:** el scheduler salta tasks cuando `_daily_spend >= DAILY_BUDGET_USD` (env `EMBRION_DAILY_BUDGET`, default $10). Las tasks que corren temprano consumen budget y las que corren después (3am-6am) lo encuentran agotado.

**H4 — Reset por redeploy:** cada redeploy de Railway aplica idempotency_guard (Sprint D-2, DSC-S-013) que preserva `last_run`/`total_runs` del registro DB anterior. Si el registro anterior tenía total_runs=1 desde la primera ejecución, queda congelado en 1 cada redeploy.

## §4 Tareas T1-T6 que Hilo Ejecutor 1 ejecuta

### T1 — Logs Railway de las últimas 7 días (15 min)

```bash
railway logs --service el-monstruo-kernel --since 168h | grep -E "scheduler_task_executing|scheduler_task_completed|scheduler_task_failed|causal_seeding|prediction_validation|vanguard_scan|scheduler_daily_budget" > /tmp/scheduler_logs_7d.txt
wc -l /tmp/scheduler_logs_7d.txt
```

**Reportar:** cuántas líneas con `scheduler_task_executing` aparecen para cada una de las 3 tasks zombie. Si aparecen pero `total_runs` no sube → H2. Si NO aparecen → H1 o H3.

### T2 — Verificar handlers stub están siendo invocados (15 min)

```bash
railway logs --service el-monstruo-kernel --since 168h | grep -E "causal_seeding_stub_executed|prediction_validation_stub_executed|vanguard_scan_stub_executed|health_check_executed|memory_consolidation_stub_executed" > /tmp/stub_handler_logs.txt
wc -l /tmp/stub_handler_logs.txt
```

**Reportar:** cuántas invocaciones por handler. Si los stubs SÍ se ejecutan → confirma H2 (bug telemetría). Si NO se ejecutan → confirma H1 (caídas reales).

### T3 — Verificar budget diario consumido (10 min)

```bash
railway logs --service el-monstruo-kernel --since 24h | grep -E "scheduler_daily_budget" | tail -20
```

**Reportar:** si aparecen logs `scheduler_daily_budget_exhausted` o `scheduler_daily_budget_reset`. Probar H3.

### T4 — Verificar el código de persistencia de `total_runs` (15 min)

Leer `kernel/embrion_scheduler.py` líneas ~370-410 (función `_execute_task`):

```python
task.last_run = datetime.now(timezone.utc).isoformat()
task.total_runs += 1
...
await self._persist_task(task)
```

Verificar que `_persist_task` realmente UPSERTea el campo `total_runs` (no solo el row sin esas columnas). Probar H2 con código.

### T5 — Aplicar fix según hipótesis confirmada (30 min - 2h)

**Si H1 (caídas reales):**
- Investigar por qué los stubs no se ejecutan
- Verificar registro de handler `register_stub_handlers` se invoque en startup
- Si falta wiring → patch en `kernel/main.py`

**Si H2 (bug persistencia):**
- Patch `_persist_task` para asegurar UPSERT correcto de todos los campos
- Migration si la columna tiene tipo wrong
- Tests que verifiquen acumulación

**Si H3 (budget exhausto):**
- Ajustar orden de tasks o subir budget diario
- Documentar en `bridge/`

**Si H4 (reset por redeploy):**
- Eliminar el preserve de `total_runs` en idempotency guard (que se actualice desde 0 cada deploy es ok, lo que importa es `last_run`)
- O cambiar lógica para acumular real

### T6 — Reportar a Cowork (15 min)

Doc en path: `bridge/manus_to_cowork_REPORTE_SCHEDULERS_ZOMBIES_2026_05_12.md`

Estructura sugerida:

```
§1 Hipótesis confirmada (H1/H2/H3/H4) con evidencia binaria de logs
§2 Causa raíz exacta (path:line si aplica)
§3 Fix aplicado (PR # si abriste, commit hash si direct push)
§4 Verificación post-fix (logs nuevos, query SQL fresca)
§5 Side-effects detectados (otras tasks afectadas)
§6 Recomendación a Cowork (DSC nuevo? actualizar memory?)
```

## §5 Reglas duras del sprint

1. **NO TOCAR la branch `sprint/D3-latido-autonomo`** ni el código del PR #104 (acabamos de mergear).
2. **NO TOCAR `system_health_check` ni `memory_consolidation`** — están sanas (last_run fresco). Solo diagnosticar las 3 zombies.
3. **NO INVENTAR causa raíz** sin logs reales. Si los logs no muestran nada, decir "logs no muestran nada concluyente" y dejar abierto.
4. **NO HACER force push** ni reset al main. Si necesitás cambios, abrí PR limpio con tests.
5. **Cero secrets en plaintext** — solo env vars referenciadas por nombre.
6. **Tests obligatorios** si el fix toca `_execute_task` o `_persist_task` — son funciones críticas del runtime.
7. **Si la causa requiere migration SQL**, escribir migration nuevo (no modificar existentes), probar local, reportar a Cowork antes de aplicar a producción.

## §6 Autoridad y cierre

- T1 (Alfredo) autorizó este sprint hoy 2026-05-12 02:55 UTC.
- T2 (Cowork) firma este spec con autoridad delegada.
- T3 (Manus Hilo Ejecutor 1) ejecuta autónomamente bajo reglas duras §5.
- Reportar a `bridge/manus_to_cowork_REPORTE_SCHEDULERS_ZOMBIES_2026_05_12.md` al completar.
- Si T6 confirma causa simple (H2, H3 o H4) y fix es <50 LOC: Manus puede pushear directo a main con tests verdes. Si confirma H1 o requiere migration: abrir PR para audit DSC-G-008 v2 por Cowork antes de merge.

ETA realista: 1-3h dependiendo de hipótesis ganadora. Si en 30min los logs no muestran NADA, reportar "logs insuficientes" y proponer agregar logging adicional al scheduler en sprint próximo.

---

**Firma:** Cowork T2 Arquitecto, 2026-05-12 03:00 UTC
**Bajo regla evolucionada del merge + autoridad T1 directa + Sistema de Realidad Ejecutable DSC-S-011**
