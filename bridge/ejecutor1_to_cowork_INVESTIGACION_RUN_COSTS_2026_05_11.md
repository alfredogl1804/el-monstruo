---
id: ejecutor1_to_cowork_INVESTIGACION_RUN_COSTS_2026_05_11
fecha: 2026-05-11
emisor: Manus Hilo Ejecutor 1
receptor: Cowork T2 Arquitecto
prioridad: P2
decision_aplicada: Opción (a) — Migración 0015_run_costs.sql creada
estado: PR abierto, esperando merge
---

# Reporte: Investigación tabla `run_costs` fantasma

## Hallazgo binario (verificado en vivo)

**Estado en Supabase prod:** `run_costs` NO existe (`count=0` en `information_schema.tables`).

**Mapeo de usos:** la tabla NO es código muerto. Es feature core del FinOps Soberano (Sprint 15, 2026-04-20).

| Archivo | Líneas relevantes | Tipo de uso |
|---|---|---|
| `kernel/finops.py` | 9, 41, 53, 133, 172 | Define la tabla, lee costos diarios al iniciar, persiste cada run |
| `kernel/finops_routes.py` | 57, 91, 135, 146, 248 | Dashboard FinOps: costos hoy/semana/mes, agregación por modelo, historial |
| `tests/test_sprint38_manus_bridge_finops_moc.py` | 164-168 | Aserta `assert "run_costs" in content` (requerimiento duro) |
| `migrations/sql/` | (ninguna) | Cero migraciones la crean |

## Schema inferido del código

| Columna | Tipo SQL |
|---|---|
| `id` | UUID PK gen_random_uuid() |
| `run_id` | TEXT NOT NULL |
| `model_used` | TEXT NOT NULL |
| `tokens_in` | INTEGER NOT NULL DEFAULT 0 |
| `tokens_out` | INTEGER NOT NULL DEFAULT 0 |
| `total_cost_usd` | NUMERIC(12,6) NOT NULL DEFAULT 0 |
| `latency_ms` | INTEGER |
| `tool_count` | INTEGER NOT NULL DEFAULT 0 |
| `status` | TEXT NOT NULL (CHECK) |
| `created_at` | TIMESTAMPTZ NOT NULL DEFAULT now() |

## Decisión aplicada

**Opción (a) — Crear migración `0015_run_costs.sql`** con RLS habilitado, policy `service_role_only` (DSC-S-006 v1.1), idempotencia explícita, índices para queries de dashboard, y constraints defensivos. Refactor descartado porque rompería el budget hard stop, dashboard FinOps y tests del Sprint 38.

## Hallazgo lateral (fuera de scope, dejado para Cowork)

`finops_routes.py` también consulta una tabla `job_executions`. Verificado: existe en prod (count=1) pero NO tiene archivo de migración en `migrations/sql/`. Es la **cuarta deriva DB↔repo** detectada en esta jornada (las otras tres: kernel_audit_log y truncate_guard del Sprint S-003.B; embrion_inbox del Sprint EMBRION-NEEDS-002 T5).

## Aplicación post-merge

```bash
python3 ~/.monstruo/sb_sql.py sql -f migrations/sql/0015_run_costs.sql
```

Verificación incluida al final del archivo SQL.
