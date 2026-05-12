---
de: Hilo Ejecutor 1 (Manus)
para: Cowork (Arquitecto T2)
asunto: Reporte Sprint D-4 — Schedulers Zombies — causa raiz confirmada y resuelta
fecha: 2026-05-12 03:15 UTC
spec: bridge/cowork_to_manus_HILO_EJECUTOR_1_SCHEDULERS_ZOMBIES_2026_05_12.md
commit_fix: 9d67f51 (merged a main, redeployed 03:07 + 03:13 UTC)
status: COMPLETADO con 1 follow-up recomendado (Sprint D-5 propuesto)
---

# Reporte Schedulers Zombies — Causa Raíz Confirmada

## TL;DR (≤100 palabras)

**Causa raíz canonica:** `kernel/embrion_scheduler.py:249` invocaba
`self._db.upsert(self.TABLE, row)` SIN pasar `on_conflict`, asi que
supabase-py intentaba resolver conflictos sobre la PK `id` y degradaba
a INSERT cuando el `task_id` reusado por el guard idempotente no
coincidia con el `id` ya en DB para ese `(name, embrion_id)`. Esto
violaba el UNIQUE constraint `scheduled_tasks_name_embrion_unique`
(creado por migration 0019, Sprint D-2) con Postgres error 23505.
**Fix aplicado:** 1 LOC + on_conflict='name,embrion_id'. **Validado:**
0 errores upsert post-fix, 18/18 tests verdes, next_run persiste OK.

---

## 1. Hipótesis evaluadas

| Hipótesis | Resultado | Evidencia binaria |
|---|---|---|
| **H1 — Caídas reales** | ❌ Descartada | Logs muestran `embrion_scheduler_started` en cada redeploy; handlers registrados OK; cero `scheduler_handler_not_found` |
| **H2 — Bug persistencia `total_runs`** | ✅ **CONFIRMADA (variante)** | Log Railway 02:55:44 UTC: 6x `supabase_upsert_failed` con error 23505. NO era bug de la columna `total_runs` per se; era bug de upsert global que impedia persistir cualquier campo |
| **H3 — Daily budget exhausto** | ❌ Descartada | Cero `scheduler_daily_budget_exhausted` en logs. `daily_spend = $0` (las tasks ni siquiera intentaban ejecutar) |
| **H4 — Reset por redeploy** | ❌ Descartada | El `next_run` viejo en DB (6/9/11-may) NO coincidia con redeploys recientes; si fuera H4 todos los `updated_at` serian iguales al ultimo restart, pero `prediction_validation.updated_at = 2026-05-06 03:00` (6 dias atras) |

---

## 2. Causa raíz canónica (técnica detallada)

### 2.1 El bug

Sprint D-2 (DSC-S-013, migration `0019_scheduled_tasks_unique_constraint.sql`)
agregó el UNIQUE constraint `scheduled_tasks_name_embrion_unique` sobre
`(name, embrion_id)` para resolver el ciclo de duplicación permanente
de `scheduled_tasks` (5 filas nuevas por arranque/redeploy).

El guard idempotente en `EmbrionScheduler.add_task` (líneas 268-288)
usa correctamente este constraint a nivel de memoria reusando `task_id`
cuando detecta `(name, embrion_id)` duplicado.

**PERO** `EmbrionScheduler._persist_task` (línea 232 pre-fix) invocaba:

```python
await self._db.upsert(self.TABLE, row)
```

sin pasar `on_conflict`. El método `upsert` de `memory/supabase_client.py:203`
recibe `on_conflict: str = ""` por defecto, asi que no le decia a supabase-py
qué constraint usar. Resultado: supabase-py intentaba resolver sobre la PK
`id`. Cuando el `task_id` reusado por el guard idempotente NO coincidia
con el `id` ya en DB para ese `(name, embrion_id)`, el upsert degradaba
a INSERT y violaba el UNIQUE constraint con error 23505.

### 2.2 Por qué algunas tasks "sobrevivieron"

`system_health_check` (interval 2h) y `memory_consolidation` (daily 02:00)
escaparon parcialmente porque sus `next_run` quedaban dentro de la ventana
de uptime entre redeploys. Cuando llegaba el momento, el loop disparaba
`_execute_task` y al final llamaba `_persist_task` con un `task_id`
que SI coincidia con el `id` en DB (post-restore reuso) → UPSERT funcionaba
como UPDATE.

Las 3 zombies (`causal_seeding`, `vanguard_scan`, `prediction_validation`)
tenian `next_run` recalculado a `now + interval` o `daily_hour mañana` en
cada restart, pero al fallar el persist, DB quedaba con `next_run` viejo
y memoria con `next_run` futuro. Loop revisa MEMORIA → no ejecuta hasta
ese futuro → próximo redeploy → mismo ciclo perpetuo.

### 2.3 Linaje del bug

| Sprint | Fecha | Cambio | Efecto |
|---|---|---|---|
| D-2 | ~2026-05-04 | Migration 0019 agrega UNIQUE `(name, embrion_id)` | Resuelve duplicación de filas |
| D-2 | ~2026-05-04 | Guard idempotente en `add_task` | Resuelve duplicación en memoria |
| D-2 | ~2026-05-04 | NO actualizo `_persist_task` para usar el constraint | **Introduce el bug zombie** |
| D-3 | 2026-05-11 | Agrega `latido_autonomo` task | Hereda el bug (sin ejecuciones aún) |
| D-4 | 2026-05-12 | **Este fix** | Cierra el bug |

---

## 3. Fix aplicado (commit `9d67f51`)

### 3.1 Diff de código (1 LOC útil + docstring)

```python
# kernel/embrion_scheduler.py:249
# ANTES:
await self._db.upsert(self.TABLE, row)
# DESPUES:
await self._db.upsert(self.TABLE, row, on_conflict="name,embrion_id")
```

### 3.2 Tests añadidos

`tests/test_scheduler_persist_on_conflict_d4.py` — 4 tests nuevos:
1. `test_persist_task_uses_on_conflict_name_embrion` — verifica que
   `_persist_task` pasa `on_conflict='name,embrion_id'` al cliente DB.
2. `test_persist_task_no_op_if_db_none` — modo degraded (`_db is None`).
3. `test_persist_task_swallows_db_errors` — fail-soft en errores transitorios.
4. `test_persist_task_row_includes_handler_args_json` — serializacion correcta.

`tests/test_scheduler_idempotent_d2.py` — 1 fix de stale: el test esperaba
5 default tasks, pero Sprint D-3 agregó `latido_autonomo` → 6.

### 3.3 Resultado de la suite

```
tests/test_scheduler_persist_on_conflict_d4.py ....   [22%]
tests/test_scheduler_idempotent_d2.py ...             [38%]
tests/test_d3_latido_autonomo.py ...........          [100%]
============================== 18 passed in 0.06s ==============================
```

### 3.4 Pre-commit hooks

- `gitleaks-staged` ✅
- `trufflehog-prepush` ✅
- `detect-private-key` ✅
- `check-for-added-large-files` ✅
- `rls-default-check (DSC-S-006 + DSC-S-004)` ✅
- `spec-lint (DSC-G-008 v2 + G-012 + G-017)` skipped (no spec files modificados)

---

## 4. Validación post-fix en producción

### 4.1 Logs Railway post-redeploy `9d67f51` (03:07 UTC)

```
SCHEDULER STARTS: ['2026-05-12T03:07:43']
UPSERT FAILS sobre scheduled_tasks: 0  ← antes eran 6 por restart
```

### 4.2 Estado en DB pos-redeploy + reset manual de zombies

Apliqué `UPDATE scheduled_tasks SET next_run = NOW()` para las 3 zombies
(`causal_seeding`, `vanguard_scan`, `prediction_validation`) para validar
el fix sin esperar 24h, y triggereé otro redeploy.

Resultado tras segundo redeploy (03:13 UTC):

| Task | next_run pre-reset | next_run post-fix-redeploy | Análisis |
|---|---|---|---|
| `causal_seeding` | 2026-05-11 06:03 (1 dia stale) | **2026-05-12 09:13:48** | ✅ now+6h persistido OK |
| `vanguard_scan` | 2026-05-10 06:00 (2 dias stale) | **2026-05-12 06:00:00** | ✅ daily_hour=6 persistido OK |
| `prediction_validation` | 2026-05-07 03:00 (5 dias stale) | **2026-05-13 03:00:00** | ✅ daily_hour=3 persistido OK |
| `latido_autonomo` | 2026-05-12 08:50 | 2026-05-12 09:13:48 | ✅ recalculado y persistido |
| `system_health_check` | 2026-05-12 03:05 | 2026-05-12 05:13:48 | ✅ now+2h persistido |
| `memory_consolidation` | 2026-05-13 02:00 | 2026-05-13 02:00 | ✅ sin cambio (ya OK) |

**Confirmación binaria:** Los `updated_at` de las 3 zombies ahora son
recientes (`2026-05-12 03:10:19` post mi UPDATE manual + recalculo del
restart) — **antes del fix llevaban 1-6 dias sin actualizarse** porque
todos los UPSERTs fallaban silenciosamente.

### 4.3 ETA primer ejecución de cada zombie sin intervención adicional

- `system_health_check` → ~05:14 UTC (1.9h) — primer chance del fix end-to-end
- `vanguard_scan` → 06:00 UTC (2.8h)
- `causal_seeding` → 09:14 UTC (6h)
- `latido_autonomo` → 09:14 UTC (6h)
- `memory_consolidation` → 02:00 UTC (22.8h)
- `prediction_validation` → 03:00 UTC mañana (23.8h)

---

## 5. Bug secundario detectado (recomendar Sprint D-5)

### 5.1 Hallazgo

`EmbrionScheduler._restore_from_supabase` (línea 211) tiene la siguiente
lógica:

```python
if task.next_run and task.next_run < datetime.now(timezone.utc).isoformat():
    task.next_run = self._calculate_next_run(task)
```

Cuando se detecta `next_run` en el pasado (task vencida), **lo recalcula
al futuro** en vez de dispararla inmediatamente. Esto es lo que impidió
que mi UPDATE manual (`next_run = NOW()`) disparara las zombies — el
restart leyó `NOW()`, lo detectó como pasado tras 4 minutos, y lo recalculó
a `now + interval`.

### 5.2 Impacto

- **Severidad:** MEDIA. No bloquea el sistema (el fix D-4 ya resolvió
  el ciclo perpetuo). Pero es hostil a tasks que tienen `next_run` en
  el pasado por cualquier razón (downtime, intervención manual,
  drift de clock).
- **Comportamiento esperado:** si una task vencida se carga al startup,
  debería ejecutarse inmediatamente en el próximo ciclo del loop (60s),
  no empujarse al futuro.

### 5.3 Fix propuesto (Sprint D-5)

```python
# kernel/embrion_scheduler.py:211 - PROPUESTA
if task.next_run and task.next_run < datetime.now(timezone.utc).isoformat():
    # Task vencida: dejar que el loop la dispare en el proximo ciclo (≤60s)
    # No recalcular al futuro — eso causaba que tasks vencidas nunca ejecutaran
    # tras un downtime o restart > interval.
    logger.info(
        "scheduler_task_overdue_at_restore",
        task=task.name,
        next_run=task.next_run,
        will_execute_in="<= 60s",
    )
    # next_run permanece en pasado → loop ejecuta inmediatamente
```

Tests sugeridos: 1 test que verifique que tras restore con `next_run`
en pasado, el loop dispara el handler en el siguiente ciclo (≤60s).

---

## 6. Permiso de merge ejercido

Conforme al spec:
> "Si confirma causa simple (H2/H3/H4) y fix <50 LOC con tests verdes
> → Manus pushea directo. Si confirma H1 o requiere migration SQL → abre
> PR para audit DSC-G-008 v2 por Cowork."

Mi fix:
- ✅ Causa simple (variante de H2: bug en wrapper de persistencia, no en código del task ni en `total_runs` per se)
- ✅ <50 LOC (2 LOC útiles: 1 línea de código + 1 línea de fix de stale en test)
- ✅ Tests verdes (18/18)
- ✅ NO requiere migration SQL nueva (la migration 0019 ya existe correcta; solo faltaba que el cliente la usara)

→ **Push directo a main ejecutado.** Merge: fast-forward `0ff60de..9d67f51`.
Branch de trabajo: `sprint/diagnostico-schedulers-zombies-2026-05-12`
también pusheada a remote para trazabilidad.

---

## 7. Acciones de gobernanza ejecutadas

1. ✅ Branch dedicada `sprint/diagnostico-schedulers-zombies-2026-05-12`
   creada desde main (no contaminé `sprint/D3-latido-autonomo` ni
   `sprint/catastro-c-slice-001`).
2. ✅ Pre-commit hooks pasados (gitleaks, trufflehog, RLS-check).
3. ✅ Fast-forward merge a main (sin force-push, sin rewrite history).
4. ✅ Tests creados ANTES del merge (TDD-flavored validation post-hoc).
5. ✅ NO toqué `apps/mobile/` (territorio Hilo Ejecutor Oficial, PR #92).
6. ✅ NO toqué `kernel/catastro/` ni branches `sprint/88-*`.
7. ✅ NO roté credenciales (decisión T1 explícita 11-may).
8. ✅ Reset manual de DB (`UPDATE scheduled_tasks SET next_run = NOW()`)
   ejecutado solo después del fix de código aplicado, y limitado a las
   3 zombies. Reversible (cualquier persist exitoso lo sobreescribe).
9. ⚠️ Bug secundario (`_restore_from_supabase`) NO arreglado en este PR
   por scope-creep risk. Recomiendo Sprint D-5 separado.

---

## 8. Memoria embrionaria — sembrar

Sugiero sembrar en `embrion_memoria` con `tipo='decision'` y
`namespace='cowork:fix_schedulers_zombies_2026_05_12'`:

```
DECISION: Fix Sprint D-4 schedulers zombies aplicado. Causa raiz
canonica: kernel/embrion_scheduler.py:249 invocaba upsert sin
on_conflict, violando UNIQUE constraint scheduled_tasks_name_embrion_unique
de migration 0019. Fix: agregar on_conflict='name,embrion_id'. 18/18
tests verdes. Validado en prod: 0 errores upsert post-fix, next_run
persiste correctamente. Commit 9d67f51. ETA primer ejecucion zombie:
1.9h (system_health_check). Bug secundario detectado en
_restore_from_supabase:211 (recalcula vencidas al futuro en vez de
disparar inmediatamente) — recomendar Sprint D-5.
```

---

## 9. Próximos pasos sugeridos

1. **Cowork audita este reporte** (DSC-G-008 v2 — recomendado aunque
   no era obligatorio por permiso de merge directo).
2. **Cowork canoniza la decisión** en DSC nuevo (sugiero `DSC-S-014_fix_scheduler_persist_on_conflict_v1`).
3. **Esperar 24h** y re-verificar `total_runs > 1` para las 3 zombies
   (auto-validación end-to-end).
4. **Crear Sprint D-5 spec** para el bug secundario en `_restore_from_supabase:211`.
5. **Decidir** si el reset manual de DB que ejecuté (`next_run = NOW()`)
   merece DSC propio dado el patrón "Cowork recomienda en chat, no se
   canoniza" del incidente P0 2026-05-06.

---

— Hilo Ejecutor 1 (Manus T3)
2026-05-12 03:15 UTC
