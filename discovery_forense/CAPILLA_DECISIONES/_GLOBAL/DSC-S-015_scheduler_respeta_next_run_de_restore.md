---
id: DSC-S-015
proyecto: GLOBAL
tipo: restriccion_dura
titulo: "Scheduler debe respetar next_run de restore — nunca recalcular incondicionalmente (lección Sprint D-5)"
estado: borrador
fecha: 2026-05-12
fecha_firma_T1: PENDIENTE
autor_borrador: Cowork T2-A (post-D-5 cierre por Hilo Ejecutor 1)
autor_propuesta_original: Manus Hilo Ejecutor 1 (durante Sprint D-5 reporte sección "Pendientes para canonización")
autorización_T1: PENDIENTE
fuentes:
  - bridge/manus_to_cowork_REPORTE_SPRINT_D5_2026_05_12.md (Hilo Ejecutor 1 cierre VERDE 23/23 tests)
  - kernel/embrion_scheduler.py commit 63767ef (_restore_from_supabase fix)
  - kernel/embrion_scheduler.py commit f6ed3be (add_task complementario)
cruza_con: [DSC-MO-006 v1.1, DSC-G-008 v2, DSC-S-012, DSC-MO-011]
contrato_ejecutable_propuesto: tests/test_scheduler_restore_overdue_d5.py (ya existe) + tests/test_add_task_after_restore_preserves_overdue_next_run.py (ya existe)
contrato_ejecutable_estado: cumplido — tests de regresión protegen la regla post-D-5/D-6 cascada
---

# DSC-S-015 — Scheduler respeta next_run de restore (anti-recálculo)

## Decisión

**Cuando `embrion_scheduler` restaura tasks desde Supabase post-startup o restart, el `next_run` persistido debe respetarse verbatim — incluso si está en el pasado (overdue). Ninguna función puede recalcular `next_run` incondicionalmente al futuro durante restore o registro.**

Reglas duras derivadas:

1. **`_restore_from_supabase` NUNCA recalcula `next_run` al futuro** para tasks restored. Si `next_run < now()`, la task se ejecuta en el próximo ciclo del loop (≤60s). Log estructurado: `scheduler_task_overdue_at_restore` con `seconds_overdue` + `will_execute_in='<= 60s'`.

2. **`add_task` debe preservar `existing.next_run` para tasks reutilizadas idempotentemente.** Solo calcula `next_run = _calculate_next_run(task)` cuando `existing is None`. Para reuso idempotente desde restore, `task.next_run = existing.next_run` verbatim.

3. **Comportamiento canónico de scheduler resiliente:** tasks vencidas tras downtime/restart deben ejecutarse en el próximo ciclo del loop, no diferirse al futuro. Esto preserva semántica temporal real, no comportamiento "siempre futuro" que ocultaba scheduler dormido por días.

4. **Prohibido cualquier código que rompa esta regla** sin DSC explícito de derogación firmado por T1.

---

## Por qué

### Evidencia binaria del bug previo (Sprint D-4/D-5/D-6 cascada)

Pre-fix Sprint D-5, `kernel/embrion_scheduler.py` tenía:

```python
# Línea ~211 pre-D-5 (BUG):
if task.next_run and task.next_run < datetime.now(timezone.utc).isoformat():
    task.next_run = self._calculate_next_run(task)  # ← BUG: empuja al futuro
```

Y `add_task:332` post-D-5 principal:

```python
# Línea 332 pre-D-5 complementario (BUG REMANENTE):
task.next_run = self._calculate_next_run(task)  # incondicional, incluso para reuso idempotente
```

**Impacto verificado en producción:**
- 3 daily tasks (`causal_seeding`, `prediction_validation`, `vanguard_scan`) quedaron en **loop perpetuo**: nunca alcanzaban su `next_run` antes del próximo redeploy, que las empujaba otra vez al futuro
- `prediction_validation` 1 latido en 5 días (last_run=6-may, total_runs=1)
- `vanguard_scan` 1 latido en 2 días (last_run=9-may)
- `causal_seeding` 1 latido en 1 día (last_run=11-may)

Hilo Ejecutor 1 detectó el bug binariamente en Sprint D-4 (audit zombies) + propuso fix en D-5. Aplicación reveló bug remanente en `add_task:332` que detectó en validación E2E pos-merge D-5 principal → cerró con D-5 complementario `f6ed3be`.

### Fix aplicado (commits canonizados)

**D-5 principal** (`63767ef`):
```python
if task.next_run and task.next_run < now:
    seconds_overdue = int((now - parse(task.next_run)).total_seconds())
    logger.info('scheduler_task_overdue_at_restore',
                task=task.name, seconds_overdue=seconds_overdue,
                will_execute_in='<= 60s')
    # next_run permanece en pasado -> loop dispara inmediatamente
```

**D-5 complementario** (`f6ed3be`):
```python
if existing is None:
    task.next_run = self._calculate_next_run(task)
else:
    task.next_run = existing.next_run  # preservado por restore
```

### Tests de regresión que enforzan la regla

- `tests/test_scheduler_restore_overdue_d5.py::test_restore_keeps_overdue_next_run_in_past`
- `tests/test_scheduler_restore_overdue_d5.py::test_overdue_task_executes_within_one_loop_cycle`
- `tests/test_scheduler_restore_overdue_d5.py::test_add_task_after_restore_preserves_overdue_next_run`
- Suite scheduler completa: 23/23 verdes post-D-5

Si alguien intenta reintroducir el recálculo incondicional, los tests rompen.

---

## Contrato ejecutable

**Estado:** cumplido (DSC-G-017 satisfied)

Implementación: `kernel/embrion_scheduler.py` commits `63767ef` + `f6ed3be`.
Tests: `tests/test_scheduler_restore_overdue_d5.py` (4 tests + 1 regresión E2E).

**Verificación binaria post-firma T1:** ejecutar `pytest tests/test_scheduler_restore_overdue_d5.py` debe pasar 4/4 + suite scheduler completa 23/23.

---

## Trazabilidad

- **Origen:** propuesto por Hilo Ejecutor 1 al cerrar Sprint D-5 con honestidad ejemplar sobre add_task:332 complementario
- **Cruza con:** DSC-MO-006 v1.1 (doctrina del silencio embrion_loop, scheduler tiene reglas paralelas) + DSC-G-008 v2 (gate de evidencia para canonizar) + DSC-S-012 (anti-deriva migraciones — patrón análogo de "respeta lo persistido")
- **Cierra deuda del Consolidado Maestro:** DRIFT-008 (latido autónomo) confirmado resuelto post-cascada D-3 → D-4 → D-5 → D-6

---

**estado:** borrador — pendiente firma T1 explícita de Alfredo en chat. Cowork redactó bajo PBA trigger 4 (DSC nuevo). Requiere audit T2-B pre-canonización + firma T1 + actualización `_dsc_contracts_index.yaml`.

**Sin firma T1, este DSC permanece como `borrador` indefinidamente.** Cowork NO canoniza unilateralmente.
