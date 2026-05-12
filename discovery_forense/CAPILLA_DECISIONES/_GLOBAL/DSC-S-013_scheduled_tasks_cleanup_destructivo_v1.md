---
id: DSC-S-013_scheduled_tasks_cleanup_destructivo_v1
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica_de_seguridad_operacional
estado: firme
fecha: 2026-05-11
autor: Cowork T2 Arquitecto (kickoff) + Hilo Ejecutor 2 (manus_hilo_b, implementación)
referencias:
  - bridge/cowork_to_manus_ACUSE_D1_+_KICKOFF_D2_D3_D4_2026_05_11.md
  - DSC-S-006_rls_por_defecto_v1.md
  - DSC-S-010_hardening_operacional_integrado.md
  - DSC-S-012_anti_deriva_migraciones_supabase.md
  - DSC-G-008_validacion_pre_spec_pre_cierre_v2.md
gate_evidencia: aplicado
binario_pre_estado:
  total_rows: 17700
  unique_names: 5
  system_health_check: 14369
  memory_consolidation: 923
  vanguard_scan: 895
  causal_seeding: 862
  prediction_validation: 651
binario_post_estado_objetivo:
  total_rows: 5
  unique_names: 5
  ratio_pre_post: "3540:1"
---

# DSC-S-013 — Cleanup destructivo de `scheduled_tasks` (16,943 → 5 filas) + idempotencia permanente

## Contexto

Una auditoría binaria con SQL contra producción reveló que la tabla `public.scheduled_tasks` tiene **17,700 filas** distribuidas en solo **5 nombres únicos** de tareas. La acumulación crece en tiempo real (+757 filas en ~30 min entre el kickoff de Cowork y el inicio de implementación). El nombre `system_health_check` solo concentra **14,369 filas activas**, todas con `paused=false` y `status='active'`. El scheduler las está disparando todas, lo que es duplicación masiva de trabajo y costo.

## Causa raíz binaria

En `kernel/embrion_scheduler.py`:

1. `register_default_tasks()` (línea 534) registra 5 tareas vía `scheduler.add_task(ScheduledTask(...))`.
2. `ScheduledTask` usa `field(default_factory=lambda: str(uuid4()))` para `task_id`, generando un UUID nuevo en cada construcción.
3. `add_task()` (línea 250) llama `_persist_task` que hace `upsert(TABLE, row)` por PK `id` con el nuevo UUID.
4. Resultado: cada arranque/reinicio/redeploy del kernel inserta **5 filas nuevas** en `scheduled_tasks`. Cada healthcheck o restart triggerea más.
5. Cero guard de unicidad por `(name, embrion_id)` ni a nivel SQL (no hay constraint) ni a nivel app (no hay SELECT-before-INSERT).

## Decisión

Se autoriza un cleanup destructivo de `public.scheduled_tasks` que reduzca 17,700+ filas a exactamente **5 filas canónicas** (una por `(name, embrion_id)` único), **bajo las siguientes condiciones de seguridad obligatorias y no negociables**:

### 1. Snapshot forense ANTES del delete

Backup completo de la tabla a `discovery_forense/SNAPSHOTS/2026_05_11_pre_cleanup_scheduled_tasks.sql.gz` con dump completo (data + schema). El snapshot es la prueba de reversibilidad — si el cleanup destruye algo crítico, se restaura desde aquí.

### 2. Script con `--dry-run` por default

`scripts/_cleanup_scheduled_tasks_duplicates.py` debe:

- Default `--dry-run=true`.
- Lógica: para cada `(name, embrion_id)`, conservar la fila con `MAX(last_run)`; si `last_run` IS NULL para todas, conservar `MAX(created_at)`; borrar las demás.
- Log estructurado a `discovery_forense/SNAPSHOTS/scheduled_tasks_cleanup_log_2026_05_11.txt`.
- Modo `--apply` requiere flag explícito Y la env var `EMBRION_D2_CLEANUP_AUTHORIZED=true` simultáneamente. Doble llave.

### 3. Migration de constraint idempotente

`migrations/sql/0019_scheduled_tasks_unique_constraint.sql`:

```sql
BEGIN;
ALTER TABLE public.scheduled_tasks
  ADD CONSTRAINT scheduled_tasks_name_embrion_unique UNIQUE(name, embrion_id);
COMMIT;
```

Aplicada vía `scripts/_apply_migration_0019.py` siguiendo template `_apply_migration_0012.py`. La migration **NO puede aplicarse si hay duplicados** — Postgres rechazará la creación del constraint. Es decir, la migration es prueba binaria post-cleanup.

### 4. Patch a `register_default_tasks()` con guard de idempotencia

En `kernel/embrion_scheduler.py`, antes de cada `scheduler.add_task(...)`:

- Buscar existing por `(name, embrion_id)` en `self._tasks` (in-memory) o en Supabase.
- Si existe, reusar `task_id` existente y solo actualizar campos volátiles (`next_run`, `interval_hours`, `handler_args`, `description`).
- Si no existe, crear nuevo.

Esto rompe el ciclo de duplicación incluso si el constraint no existiera.

### 5. PR único a `main` con título

`[P0 Cleanup] scheduled_tasks idempotencia + cleanup 16,943 → 5 filas`

Que contenga los 5 artefactos: DSC, migration, applier, script, patch scheduler.

### 6. Cleanup masivo SOLO bajo confirmación humana explícita

El comando `--apply` se ejecuta **solo después** de:
- PR mergeado a `main`.
- Migration 0019 aplicada (que falla si hay duplicados, así forma parte del flujo).
- Confirmación humana en chat o bridge sobre la ventana.

Si la migration 0019 se aplica **antes** del cleanup, fallará por duplicados — eso es OK, sirve como freno binario. El cleanup debe correr primero, luego migration, luego el patch idempotente queda permanente.

## Plan de rollback

Si después del cleanup el scheduler queda en estado roto:

1. `gunzip -c discovery_forense/SNAPSHOTS/2026_05_11_pre_cleanup_scheduled_tasks.sql.gz | psql $SUPABASE_DB_URL` reintroduce las 17,700 filas.
2. `ALTER TABLE public.scheduled_tasks DROP CONSTRAINT scheduled_tasks_name_embrion_unique;` quita la constraint si fue aplicada.
3. Revert del PR en `main` revierte el patch al scheduler.

ETA rollback: <5 min. Reversibilidad binaria garantizada por el snapshot.

## Métricas binarias post

Verificación a +5min después de aplicar el cleanup:

```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT name) AS unique_names,
  COUNT(DISTINCT (name, embrion_id)) AS unique_pairs
FROM scheduled_tasks;
```

**Resultado esperado:** `total_rows=5, unique_names=5, unique_pairs=5`.

Verificación a +24h después de aplicar (control de no-regresión):

```sql
SELECT COUNT(*) FROM scheduled_tasks;
-- Esperado: 5 (sin crecimiento)
```

Si crece en las primeras 24h, el patch idempotente está roto y debe revertirse.

## Política reusable derivada

Esta decisión queda como precedente para **todas las tablas de configuración con default-seed**:

| Patrón | Implementación obligatoria |
|---|---|
| Lookup keys naturales | UNIQUE constraint a nivel SQL |
| Seed en código | SELECT-before-INSERT (idempotencia) |
| Persistencia background | Try `_persist_task` con `ON CONFLICT DO UPDATE` |
| Snapshot pre-destructivo | `pg_dump --data-only --column-inserts` antes de DELETE masivo |
| DSC firmado | Para cualquier DELETE >1 fila en prod |

## Firma

**Cowork T2 Arquitecto** — kickoff aprobando el cleanup destructivo bajo estas condiciones, 2026-05-11.

**Hilo Ejecutor 2 (`manus_hilo_b`)** — implementación 2026-05-11 con valores binarios reales validados contra producción.

DSC firmado bajo Gate de Evidencia DSC-G-008 v2: 1) auditoría binaria SQL pre-decisión ✓, 2) causa raíz identificada en código fuente ✓, 3) plan de rollback con prueba ejecutable ✓, 4) métricas post objetivas ✓, 5) política reusable derivada ✓.
