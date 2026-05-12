---
id: cowork_to_manus_HILO_CATASTRO_SPRINT_MEGA_CIERRE_HOY_TA1_TA2_TA5_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Catastro (libre post S-CONTRATOS-001 6/6 VERDE + PR #115 abierto esperando T2-B convergencia)
tipo: kickoff_sprint_MEGA_CIERRE_HOY_paralelo
prioridad: P0 (cierre objetivo magno HOY "kernel asiste memoria persistente Cowork ACTIVO")
duracion_estimada: 30-45 min reales
autoridad_T1: Alfredo autorizó 2026-05-12 ~07:45 UTC ("si autorizo spring mega y recuerda que son 3 hilos")
autoridad_T2: Cowork T2-A firma split paralelo entre Catastro (TA1+TA2+TA5) + Ejecutor 1 (TA3) + Ejecutor 2 sigue standby ESCAPE
hilo_paralelo: Hilo Ejecutor 1 tomando TA3 simultáneamente
---

# Sprint MEGA-CIERRE-HOY — Catastro toma TA1 + TA2 + TA5

## §1 ¿Por qué este sprint existe?

**Objetivo magno T1 HOY:** que la memoria persistente del Monstruo (kernel) **ASISTA ACTIVAMENTE** a Cowork — no solo en próxima sesión, sino HOY.

Cowork canonizó hoy QW1 (sesión Supabase row `3a04e11b`) + QW2 (CLAUDE.md Paso 0/N/M). **Pero el gap binario crítico:** los 3 flags Railway de COWORK-RUNTIME-001 (`COWORK_HOOK_ENABLED`, `COWORK_SESSION_PERSIST`, `COWORK_PREFLIGHT_REQUIRED`) siguen en `enabled=false` shadow. Sin activarlos, el kernel NO intercepta respuestas Cowork ni persiste sesiones automáticamente.

**Cowork NO puede activar esos flags** (sin Railway CLI ni env vars). **Manus SÍ puede.** Este sprint cierra el gap.

Vos tomás 3 tareas no-Railway (cleanup + apply migración + verificación post-redeploy). Ejecutor 1 toma la activación de flags Railway.

## §2 Tu scope: TA1 + TA2 + TA5 (3 tareas paralelas a Ejecutor 1)

### TA1 — Cleanup `_tmp_notif.md` (5 min)

Bridge file detectado por T2-B en audit PR #114 como scope leak P3. Ejecutor 1 tenía la tarea TE pero NO la ejecutó.

```bash
cd ~/el-monstruo && git pull origin main
ls -la _tmp_notif.md  # confirmar existe (3525 bytes)
git rm _tmp_notif.md
git commit -m "chore(cleanup): rm _tmp_notif.md scope leak P3 detectado por T2-B audit PR #114 - era notif ROTOR-001 que entro por error en commit e33c23c mobile-realignment T2+T3 scaffolding"
git push origin main
```

**Verificación post-push:**
```bash
ls _tmp_notif.md 2>&1
# Esperado: "No such file or directory"
```

### TA2 — Apply migración 0023 `rotor_activity_log` a Supabase prod (15 min)

Sprint ROTOR-001 (PR #113 mergeado commit `43b26755`) creó `migrations/sql/0023_rotor_activity_log.sql` pero **NO se aplicó a prod aún**. El kernel `recharge_mainspring` cada 5 min necesita esa tabla.

**Verificación binaria pre-flight:**
```bash
cd ~/el-monstruo && git pull origin main
ls -la migrations/sql/0023_rotor_activity_log.sql  # debe existir
grep -E "DATE\(" migrations/sql/0023_rotor_activity_log.sql  # NO debe haber output (Ejecutor 2 ya respetó lección post-V25)
```

**Apply binario:**
```bash
# Opción 1 (preferida): script idempotente
python3 scripts/_apply_migration_NNNN.py 0023 || python3 -c "
import psycopg2, os
conn = psycopg2.connect(os.environ['SUPABASE_DB_URL'])
with open('migrations/sql/0023_rotor_activity_log.sql') as f:
    conn.cursor().execute(f.read())
conn.commit()
print('Migration 0023 applied')
"

# Opción 2 (fallback): sb_sql.py
python3 scripts/sb_sql.py migrations/sql/0023_rotor_activity_log.sql

# Smoke test (insert + select + delete cleanup)
python3 -c "
import psycopg2, os
conn = psycopg2.connect(os.environ['SUPABASE_DB_URL'])
cur = conn.cursor()
cur.execute(\"\"\"
INSERT INTO public.rotor_activity_log (source, actor, payload_jsonb, energy_units)
VALUES ('cowork_session', 'smoke_test_MEGA_CIERRE', '{}', 0.0)
RETURNING id;
\"\"\")
row_id = cur.fetchone()[0]
print(f'Insert OK: {row_id}')

cur.execute('DELETE FROM public.rotor_activity_log WHERE id=%s', (row_id,))
conn.commit()
print('Smoke cleanup OK')
"
```

**Criterio de éxito binario:**
- Tabla `rotor_activity_log` existe en prod con RLS habilitada + policy `service_role_only`
- Smoke insert + delete funciona
- Anti-IMMUTABLE check: cero `DATE(timestamptz)` directo en índices (verificá `grep "DATE\(" migrations/sql/0023*.sql`)

### TA5 — Verificación runtime activo post-redeploy Ejecutor 1 (10-15 min)

**Espera a que Ejecutor 1 termine TA3** (activar Railway flags + redeploy). Cuando él reporte al bridge, hacés vos verificación binaria:

```sql
-- Verificación 1: cowork_sesiones NUEVAS post-redeploy
-- (kernel debería empezar a poblar rows con T4 COWORK_SESSION_PERSIST=true)
SELECT count(*) AS new_sesiones_post_redeploy
FROM public.cowork_sesiones
WHERE fecha_inicio > NOW() - INTERVAL '30 minutes'
  AND id != '3a04e11b-e610-4958-964e-4a709f3a5c61';  -- excluir la mía

-- Esperado: >= 0 (puede ser 0 si Cowork no tuvo turnos post-flags, OK)
```

```bash
# Verificación 2: audit log JSONL existe (T1 COWORK_HOOK_ENABLED=true)
ls -la bridge/t1_audit_log.jsonl 2>&1
# Esperado: archivo existe + tamaño > 0 (o vacío si Cowork no envió outputs post-flags, OK)
```

```bash
# Verificación 3: Railway env vars seteados (post-Ejecutor 1)
railway variables list | grep -E "COWORK_HOOK_ENABLED|COWORK_SESSION_PERSIST|COWORK_PREFLIGHT_REQUIRED"
# Esperado: las 3 con valor "true"
```

```bash
# Verificación 4: kernel responde con pre_response_hook activo
curl -s "https://el-monstruo-kernel.railway.app/v1/health" | jq .
# Esperado: 200 + JSON con campo "cowork_hook_enabled": true
```

**Reporte final tuyo:** `bridge/manus_to_cowork_SPRINT_MEGA_CIERRE_HOY_CATASTRO_2026_05_12.md` con:
- §1 TA1 commit hash + verificación post-push
- §2 TA2 migration apply status + smoke result + RLS verificada
- §3 TA5 verificación runtime: 4 checks binarios verbatim
- §4 Estado final: kernel asiste Cowork ACTIVO ✅ / parcial / pendiente

## §3 Reglas duras

1. **NO tocar PR #115** (es tu propio PR esperando T2-B convergencia, no self-merge)
2. **NO tocar PR #110** (Perplexity, esperando CI + T2-B convergencia)
3. **NO tocar branches del Ejecutor 1** (su trabajo TA3 en paralelo)
4. **NO modificar código kernel** (TA2 es apply migración, NO modificar SQL)
5. **NO seteo Brand Engine flags** (TA4 está en espera de firma T1 explícita)
6. **NO seteo Telegram T3 flags** (3 valores son decisión T1 explícita)
7. **Push directo bajo D-4.8** para TA1 cleanup (housekeeping trivial)

## §4 Skill match Catastro

- TA1 cleanup git rm — trivial
- TA2 apply migración + smoke — skill match alto (Catastro hizo S-CONTRATOS-001 T4 con migración 0025 + smoke 3/3 verde HOY)
- TA5 verificación SQL + curl — skill match alto (audits + reportes estructurados son tu fortaleza)

## §5 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint MEGA-CIERRE-HOY Catastro TA1+TA2+TA5 CERRADO. _tmp_notif.md eliminado. Migration 0023 rotor_activity_log aplicada a Supabase prod con smoke verde. Verificación runtime activo post-Ejecutor 1 TA3: kernel asiste Cowork ACTIVO via COWORK-RUNTIME-001 flags Fase 1 (T1+T4+T5).',
  'manus-hilo-catastro',
  9
);
```

## §6 Coordinación con Ejecutor 1 paralelo

Tu TA1+TA2 son **independientes de TA3 Ejecutor 1**. Pueden correr simultáneo.

Tu TA5 **depende de** Ejecutor 1 cerrar TA3. Esperá a su reporte al bridge antes de empezar TA5.

Punto de sincronía: bridge file de Ejecutor 1 reportando TA3 verde → vos arrancás TA5.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 07:50 UTC

**Sprint MEGA-CIERRE-HOY paralelo entre Catastro + Ejecutor 1 cierra el gap binario "memoria persistente activa HOY" del objetivo magno T1.**
