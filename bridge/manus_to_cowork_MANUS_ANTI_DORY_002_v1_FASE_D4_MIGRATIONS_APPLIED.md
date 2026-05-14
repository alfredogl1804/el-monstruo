# 🔌 FASE D4 — MIGRATIONS APPLIED — Template + 7 Métricas Binarias PC6

**Sprint:** MANUS-ANTI-DORY-002 v1
**Fase:** D4 — Shadow Prod
**Estado al crear este archivo:** `AUDIT_PENDIENTE` (Cowork llenará este template tras aplicar)
**Autor template:** Manus (Ejecutor 1)
**Fecha:** 2026-05-14

---

## §1. Propósito

Este archivo es el **handoff binario verificable** entre Cowork T2-A (aplica migrations via MCP) y Manus (activa el cron Railway). Cowork llena este template tras aplicar `0034` y `0035`; Manus NO procede a crear el servicio Railway hasta que las 7 métricas PC6 estén en verde aquí.

---

## §2. Migrations a aplicar (orden estricto)

| Orden | Migration | Tabla/RPC | Aplicada | Timestamp UTC | Aplicada por |
|---|---|---|---|---|---|
| 1 | `0034_anti_dory_grants.sql` | GRANT writer + reader → service_role | ☐ | `__________` | __________ |
| 2 | `0035_anti_dory_runtime_flags.sql` | anti_dory_runtime_flags + anti_dory_write_budget + 2 RPCs | ☐ | `__________` | __________ |

### Comandos de aplicación (Cowork T2-A via MCP Supabase)

```bash
# Vía MCP Supabase (preferido)
manus-mcp-cli tool call apply_migration --server supabase \
    --input '{"name": "0034_anti_dory_grants", "query": "<contenido_0034.sql>"}'

manus-mcp-cli tool call apply_migration --server supabase \
    --input '{"name": "0035_anti_dory_runtime_flags", "query": "<contenido_0035.sql>"}'
```

---

## §3. 7 Métricas Binarias Pre-Activación PC6

Cowork verifica **antes** de declarar este handoff verde:

### M1 — Singleton flag existe + default OFF

```sql
SELECT shadow_write_enabled, last_disabled_at, created_at
  FROM public.anti_dory_runtime_flags
 WHERE singleton_lock = 'anti_dory_singleton';
```

| Campo | Esperado | Observado | Pass? |
|---|---|---|---|
| `shadow_write_enabled` | `false` | `_______` | ☐ |
| Row count | `1` | `_______` | ☐ |

### M2 — RPCs creados y ejecutables por service_role

```sql
SELECT proname,
       pg_has_role('service_role', oid, 'EXECUTE') AS service_role_can_exec
  FROM pg_proc
 WHERE proname IN ('rpc_check_shadow_enabled', 'rpc_increment_write_budget')
   AND pronamespace = 'public'::regnamespace;
```

| RPC | Esperado | Observado | Pass? |
|---|---|---|---|
| `rpc_check_shadow_enabled` | `true` | `_______` | ☐ |
| `rpc_increment_write_budget` | `true` | `_______` | ☐ |

### M3 — RLS habilitado en ambas tablas

```sql
SELECT c.relname, c.relrowsecurity
  FROM pg_class c JOIN pg_namespace n ON c.relnamespace = n.oid
 WHERE n.nspname = 'public'
   AND c.relname IN ('anti_dory_runtime_flags', 'anti_dory_write_budget');
```

| Tabla | Esperado | Observado | Pass? |
|---|---|---|---|
| `anti_dory_runtime_flags` | `true` | `_______` | ☐ |
| `anti_dory_write_budget` | `true` | `_______` | ☐ |

### M4 — Policies service_role-only existen

```sql
SELECT tablename, policyname, roles, cmd
  FROM pg_policies
 WHERE schemaname = 'public'
   AND tablename IN ('anti_dory_runtime_flags', 'anti_dory_write_budget');
```

| Esperado | Observado | Pass? |
|---|---|---|
| 2 policies (1 por tabla) `{service_role}` `ALL` | `_______` | ☐ |

### M5 — Role membership writer + reader

```sql
SELECT pg_has_role('service_role', 'anti_dory_writer_role', 'MEMBER') AS writer,
       pg_has_role('service_role', 'anti_dory_reader_role', 'MEMBER') AS reader;
```

| Campo | Esperado | Observado | Pass? |
|---|---|---|---|
| `writer` | `true` | `_______` | ☐ |
| `reader` | `true` | `_______` | ☐ |

### M6 — Smoke test rpc_check_shadow_enabled retorna false por default

```sql
SELECT rpc_check_shadow_enabled();
```

| Esperado | Observado | Pass? |
|---|---|---|
| `false` | `_______` | ☐ |

### M7 — Smoke test rpc_increment_write_budget incrementa + retorna within_budget

```sql
SELECT * FROM rpc_increment_write_budget(now());
-- Repetir 2 veces para verificar idempotencia upsert
```

| Esperado primer call | Observado | Pass? |
|---|---|---|
| `within_budget = true`, `w10min_count = 1` | `_______` | ☐ |

| Esperado segundo call | Observado | Pass? |
|---|---|---|
| `within_budget = false`, `exceeded_window = 'w10min'`, `w10min_count = 2` | `_______` | ☐ |

| Side effect esperado | Observado | Pass? |
|---|---|---|
| Singleton flag flip a `shadow_write_enabled = false`, `last_disabled_by = 'self_disable_budget_w10min'` | `_______` | ☐ |

**IMPORTANTE: después de M7, Cowork debe LIMPIAR el estado para Manus**:
```sql
-- Limpiar contador de prueba (M7 generó write_count=2 en w10min)
DELETE FROM public.anti_dory_write_budget WHERE window_kind IN ('w10min', 'w1h', 'w24h');

-- Reset flag pero DEJAR shadow_write_enabled=false (Manus lo flipará a true manualmente al activar)
UPDATE public.anti_dory_runtime_flags
   SET last_disabled_at = NULL,
       last_disabled_by = NULL,
       kill_reason = NULL
 WHERE singleton_lock = 'anti_dory_singleton';
```

---

## §4. Resultado consolidado

| # | Métrica | Pass / Fail | Notas |
|---|---|---|---|
| M1 | Singleton flag default OFF | ☐ | |
| M2 | RPCs creados | ☐ | |
| M3 | RLS habilitado | ☐ | |
| M4 | Policies service_role | ☐ | |
| M5 | Role membership | ☐ | |
| M6 | rpc_check default false | ☐ | |
| M7 | rpc_increment idempotente + self-disable | ☐ | |

### Veredicto Cowork T2-A

- ☐ **VERDE 7/7** → Manus autorizado a proceder con Paso 9 (crear Railway service)
- ☐ **AMARILLO** → Resolver gaps específicos antes de proceder
- ☐ **ROJO** → Rollback migrations y abrir incidente

**Cowork firma:** `__________________`
**Timestamp UTC:** `__________________`
**Frase canónica:** `🔌 FASE D4 — MIGRATIONS APPLIED + 7 PC6 VERDES`

---

## §5. Compromiso Manus post-handoff

Si veredicto = VERDE, Manus procede SOLO con:
1. Crear servicio Railway `anti-dory-heartbeat-cron` con env vars **mínimas** (lista PC3 whitelist)
2. Flag inicial: `ANTI_DORY_CRON_ENABLED=false` (primer deploy no-op por seguridad)
3. Esperar primer tick exitoso → verificar logs muestran "exit 0 sin escribir"
4. Flip flag a `true` + redeploy → seguir monitoreo T+30min/T+2h/T+24h
5. T1 flip kill switch DB a `true` cuando T1 firme la activación operativa

Si en CUALQUIER punto Manus detecta anomalía, ejecuta el L1 del REVERT_PLAN inmediatamente y notifica a T1+Cowork.
