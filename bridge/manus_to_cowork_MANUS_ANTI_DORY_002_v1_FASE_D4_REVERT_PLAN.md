# 🔌 FASE D4 — REVERT PLAN — 3 niveles de rollback

**Sprint:** MANUS-ANTI-DORY-002 v1
**Fase:** D4 — Shadow Prod (Opción A blindada)
**Autor:** Manus (Ejecutor 1) bajo convergencia TRIPLE Tier 1
**Fecha:** 2026-05-14
**Estado terminal:** `🔌 FASE D4 — REVERT_PLAN_READY`

---

## §1. Filosofía del revert

> **Shadow prod no es activación — es instrumentación reversible con cero hidratación.**
> — GPT-5.5 Pro Sabio Magna

Si CUALQUIER métrica binaria PC6 falla (ver `FASE_D4_MIGRATIONS_APPLIED.md`), T1 (o Cowork bajo delegación T1) ejecuta el nivel mínimo de revert necesario. La doctrina canónica es: **revert reversible primero, destructivo solo bajo evidencia binaria**.

Los 3 niveles van de menor a mayor impacto:

| Nivel | Acción | Tiempo de ejecución | Reversible | Cuándo usar |
|---|---|---|---|---|
| **L1** | Flip kill switch DB | 5s | ✅ Sí | Cualquier anomalía (latencia, error rate, payload extraño) |
| **L2** | Flip flag Railway + redeploy | 60s | ✅ Sí | L1 insuficiente, sospecha de bug en cron logic |
| **L3** | DROP service Railway + REVOKE GRANTs | 5min | ⚠️ Parcial | Compromiso de seguridad (secret leak, role-membership inesperada) |

NO se contempla L4 (DROP migrations) sin firma T1 explícita y postmortem documentado. Las migrations 0034 y 0035 quedan **siempre presentes** en main; el revert opera sobre **operación**, no sobre **schema**.

---

## §2. Nivel L1 — Kill switch DB (5 segundos)

### Cuándo usar
Cualquier de estas 7 métricas binarias (PC6) en alarma:

| # | Métrica | Threshold | Esperado |
|---|---|---|---|
| M1 | `count(*) FROM runtime_events WHERE actor_type='system' AND payload->>'mode'='shadow_prod' last 1h` | `> 8` | `<= 6` (budget 1h) |
| M2 | `count(*) FROM thread_snapshots WHERE writer_mode='heartbeat' last 24h` | `> 100` | `<= 96` (cada 15min) |
| M3 | `max(elapsed_ms) en logs Railway cron last 30min` | `> 15000` | `< 12000` |
| M4 | `count(*) DISTINCT idempotency_key WHERE ts > now()-interval '10min'` per project_id | `> 1` | `= 1` |
| M5 | Errores HTTP 4xx/5xx en logs Railway cron last 1h | `> 3` | `<= 1` |
| M6 | `shadow_write_enabled` flag DB | `false unexpected` | `true` |
| M7 | Cualquier env var ANTHROPIC_API_KEY/OPENAI_API_KEY visible en `printenv` Railway service | `present` | `absent` |

### Cómo ejecutar (T1 desde Supabase SQL Editor o Cowork via MCP)

```sql
-- Apaga shadow writer instantáneamente. NO toca cron, NO toca Railway.
-- El próximo tick (≤15min) verá kill switch OFF y hará no-op.
UPDATE public.anti_dory_runtime_flags
   SET shadow_write_enabled = false,
       last_disabled_at = now(),
       last_disabled_by = 'T1_manual',
       kill_reason = 'L1 revert by T1 — razón: <DETALLE_AQUI>'
 WHERE singleton_lock = 'anti_dory_singleton';

-- Verificación binaria post-flip
SELECT shadow_write_enabled, last_disabled_at, last_disabled_by, kill_reason
  FROM public.anti_dory_runtime_flags
 WHERE singleton_lock = 'anti_dory_singleton';
-- Esperado: shadow_write_enabled = false
```

### Garantías L1
- **Latencia:** cron tarda máximo 15min en ver el flip (próximo tick).
- **Reversibilidad:** flip a `true` con un UPDATE re-activa shadow sin redeploy.
- **No-impacto Web:** L1 NO toca wire (`ANTI_DORY_ENABLED`); el agente sigue su flujo legacy intacto.
- **Auditoría:** `last_disabled_by` y `kill_reason` quedan en DB para forense.

---

## §3. Nivel L2 — Flag Railway + redeploy (60 segundos)

### Cuándo usar
- L1 ejecutado pero cron sigue escribiendo (bug en lectura del kill switch)
- Sospecha de bug en cron logic que ignora flag DB
- Necesidad de pausar TODO el cron service, no solo el shadow write

### Cómo ejecutar (T1 desde Railway dashboard o `railway variables` CLI)

```bash
# Vía Railway CLI (token T1)
export RAILWAY_TOKEN=<T1_personal_token>
cd ~/el-monstruo
railway link --project e9f5d5f6-61ac-4efb-92d2-5c63dc93f1f4
railway service "anti-dory-heartbeat-cron"

# Apagar cron flag (segregado del wire flag)
railway variables --set "ANTI_DORY_CRON_ENABLED=false"

# Redeploy con flag nuevo (Railway cron job reflectará en próxima ejecución)
railway redeploy

# Verificación binaria
railway logs --tail 50 | grep "ANTI_DORY_CRON_ENABLED=false → exit 0"
```

### Vía dashboard (sin CLI)
1. Railway dashboard → Project `el-monstruo` → Service `anti-dory-heartbeat-cron`
2. Variables → `ANTI_DORY_CRON_ENABLED` → flip a `false`
3. Deployments → Redeploy (botón manual)
4. Logs próxima ejecución → debe ver línea `exit 0 sin escribir`

### Garantías L2
- **Latencia:** redeploy ~30-60s. Siguiente tick respeta flag inmediatamente.
- **Reversibilidad:** flip a `true` + redeploy.
- **No-impacto Web:** el wire flag `ANTI_DORY_ENABLED` permanece intacto (segregación C1).

---

## §4. Nivel L3 — DROP service + REVOKE GRANTs (5 minutos)

### Cuándo usar
- Compromiso de seguridad confirmado (secret leak en logs Cowork detecta, role-membership inesperada en `pg_has_role`)
- L1+L2 insuficientes (cron service compromitido en sí)
- Postmortem decision T1: revertir D4 completo y replanificar

### Cómo ejecutar

#### 4.1 Pausar y eliminar Railway service
```bash
railway service "anti-dory-heartbeat-cron"
railway service:delete  # confirma con --yes después de verificar
```

#### 4.2 REVOKE GRANTs SQL (Supabase)
```sql
BEGIN;

-- Revoke role membership (revertir migration 0034)
REVOKE anti_dory_writer_role FROM service_role;
REVOKE anti_dory_reader_role FROM service_role;

-- Revoke RPC executes
REVOKE EXECUTE ON FUNCTION public.rpc_check_shadow_enabled() FROM service_role;
REVOKE EXECUTE ON FUNCTION public.rpc_increment_write_budget(TIMESTAMPTZ) FROM service_role;

-- Apagar kill switch como medida extra
UPDATE public.anti_dory_runtime_flags
   SET shadow_write_enabled = false,
       last_disabled_at = now(),
       last_disabled_by = 'T1_L3_security_revoke',
       kill_reason = 'L3 emergency: <DETALLE>'
 WHERE singleton_lock = 'anti_dory_singleton';

COMMIT;
```

#### 4.3 Verificación binaria L3
```sql
-- Esperado: ambos FALSE (membresía revocada)
SELECT pg_has_role('service_role', 'anti_dory_writer_role', 'MEMBER') AS writer,
       pg_has_role('service_role', 'anti_dory_reader_role', 'MEMBER') AS reader;
```

### Garantías L3
- Cron Railway eliminado, ya no consume créditos ni invoca RPCs.
- `service_role` pierde permisos sobre los RPCs Anti-Dory.
- Schema (tablas, RPCs, migrations 0029-0035) **permanece** para evitar destrucción no-reversible.
- Re-activación requiere nuevo PR + audit Cowork + re-creación service Railway.

---

## §5. Decision tree binario para T1

```
¿Alguna métrica PC6 en alarma?
├─ NO → no-op, monitoreo continúa
└─ SÍ → ¿Es problema de operación (volumen, errores) O de seguridad (leak, perms)?
        ├─ Operación → L1 (kill switch DB)
        │              └─ ¿Resuelve en 30min?
        │                  ├─ SÍ → cerrar incidente, postmortem L1
        │                  └─ NO → escalar a L2 (Railway flag + redeploy)
        │                          └─ ¿Resuelve en 1h?
        │                              ├─ SÍ → cerrar incidente, postmortem L2
        │                              └─ NO → L3 (seguridad o escalar a T1)
        └─ Seguridad → L3 directo (DROP service + REVOKE)
                       └─ Postmortem obligatorio + DSC firmado
```

---

## §6. Tabla de comandos de emergencia (copy-paste ready)

### L1 (SQL Editor Supabase)
```sql
UPDATE public.anti_dory_runtime_flags SET shadow_write_enabled = false, last_disabled_at = now(), last_disabled_by = 'T1_manual', kill_reason = '<DETALLE>' WHERE singleton_lock = 'anti_dory_singleton';
```

### L2 (Railway CLI)
```bash
railway variables --set "ANTI_DORY_CRON_ENABLED=false" && railway redeploy
```

### L3 (SQL Editor Supabase)
```sql
BEGIN; REVOKE anti_dory_writer_role FROM service_role; REVOKE anti_dory_reader_role FROM service_role; UPDATE public.anti_dory_runtime_flags SET shadow_write_enabled = false, last_disabled_by = 'T1_L3_security_revoke', kill_reason = '<DETALLE>' WHERE singleton_lock = 'anti_dory_singleton'; COMMIT;
```

---

## §7. Compromiso anti-deuda

Si CUALQUIER nivel de revert se ejecuta, Manus (Ejecutor 1) NO re-activa D4 sin:
1. Postmortem documentado en `discovery_forense/INCIDENTES/`
2. DSC firmado T1 + Cowork con cambios identificados
3. Audit Cowork explícito sobre los cambios
4. Re-validación de las 7 métricas PC6 en staging-like (si aplicable)

NO auto-escalamiento a D5/D6 mientras un revert esté pendiente de cierre.
