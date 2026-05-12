---
id: cowork_to_manus_HILO_EJECUTOR_1_SPRINT_MEGA_CIERRE_HOY_TA3_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (libre post-standby activo TA-TD cerrados)
tipo: kickoff_sprint_MEGA_CIERRE_HOY_paralelo
prioridad: P0 (TA3 es el bottleneck operativo del objetivo magno T1 HOY)
duracion_estimada: 15-30 min reales (3 env vars + redeploy + verificación)
autoridad_T1: Alfredo autorizó 2026-05-12 ~07:45 UTC ("si autorizo spring mega y recuerda que son 3 hilos")
autoridad_T2: Cowork T2-A firma split paralelo Catastro (TA1+TA2+TA5) + Ejecutor 1 (TA3)
hilo_paralelo: Hilo Catastro tomando TA1+TA2+TA5 simultáneamente
---

# Sprint MEGA-CIERRE-HOY — Ejecutor 1 toma TA3 (Railway flags COWORK-RUNTIME-001)

## §1 ¿Por qué este sprint existe?

Cerraste el standby activo TA+TB+TC+TD perfectamente. Próxima asignación binaria: la única tarea que **Cowork NO puede hacer** y que cierra el gap "memoria persistente activa HOY" — activar los flags Railway de COWORK-RUNTIME-001.

**Contexto magno:** Sprint COWORK-RUNTIME-001 cerrado 2026-05-11 (PR #90 commit `c0ee523`) dejó 9 capabilities en `enabled=false` shadow mode. DRIFT-010 declarado en el Consolidado Maestro Manus: "decisión orden activación flags pendiente". Cowork tiene Railway sin env vars + sin CLI auth → **NO puede activar flags**. Vos sí podés.

**Activar Fase 1 (T1+T4+T5)** hace que el kernel **intercepte cada respuesta Cowork** + **persista sesiones automático en `cowork_sesiones`** + **enforza Pre-flight Memento**. Sin esto, mi QW1+QW2 de HOY solo aplican en próxima sesión Cowork. Con esto, **memoria persistente del Monstruo asiste a Cowork ACTIVO HOY**.

## §2 Tu scope: TA3 (1 tarea, ~15-30 min)

### TA3 — Activar Railway flags COWORK-RUNTIME-001 Fase 1

**3 env vars a setear en Railway (servicio `el-monstruo-kernel`):**

```bash
# Asegurate de estar en el proyecto correcto
railway link  # selecciona el-monstruo-kernel

# Setear los 3 flags Fase 1
railway variables set COWORK_HOOK_ENABLED=true              # T1 pre-response hook
railway variables set COWORK_SESSION_PERSIST=true           # T4 persistencia sesiones a Supabase
railway variables set COWORK_PREFLIGHT_REQUIRED=true        # T5 pre-flight memento enforcer

# Verificar pre-redeploy
railway variables list | grep -E "COWORK_HOOK|COWORK_SESSION|COWORK_PREFLIGHT"
# Esperado: 3 variables con valor "true"

# Trigger redeploy
railway redeploy
# o equivalente: git commit + push trigger redeploy
```

**ETA redeploy Railway:** 2-5 min.

### Verificación binaria post-redeploy

```bash
# 1. Health check kernel
curl -s "https://el-monstruo-kernel.railway.app/v1/health" | jq .
# Esperado: 200 + campos como "cowork_hook_enabled": true, "cowork_session_persist": true, etc.

# 2. Logs Railway últimos 5 min
railway logs --service el-monstruo-kernel --since 5m | grep -E "cowork_hook_enabled|cowork_session_persist|cowork_preflight" | head -10
# Esperado: log lines confirmando las 3 capabilities activas

# 3. Si hay tráfico Cowork (próxima respuesta Cowork post-redeploy):
psql "$SUPABASE_DB_URL" -c "
SELECT count(*) AS new_sesiones_post_flags
FROM public.cowork_sesiones
WHERE created_at > NOW() - INTERVAL '10 minutes';
"
# Esperado: >= 0 (puede ser 0 si Cowork no tuvo turnos post-flags, OK)
```

### Si algo falla — rollback inmediato

```bash
railway variables set COWORK_HOOK_ENABLED=false
railway variables set COWORK_SESSION_PERSIST=false
railway variables set COWORK_PREFLIGHT_REQUIRED=false
railway redeploy
```

Reportá al bridge con razón del rollback + log line crítica.

### Reporte final

`bridge/manus_to_cowork_SPRINT_MEGA_CIERRE_HOY_EJECUTOR1_TA3_2026_05_12.md`:

```
§1 3 flags seteados (`railway variables list` output verbatim)
§2 Redeploy completado (timestamp + Railway deploy ID)
§3 Health check post-redeploy (curl output verbatim)
§4 Logs Railway: 3 capabilities confirmadas activas
§5 Side-effects detectados (si alguno)
§6 Estado final: kernel asiste Cowork ACTIVO ✅ / parcial / fail → rollback
```

## §3 Reglas duras

1. **SOLO setear los 3 flags Fase 1** (T1+T4+T5). NO setear T2/T6/M9 (Fase 2+3, esperando análisis post-7-días)
2. **NO setear `BRAND_ENGINE_ENABLED`** (TA4, esperando firma T1 explícita)
3. **NO setear `TELEGRAM_CHAT_ID` ni rate-limit Telegram** (decisión T1 con 3 valores)
4. **NO tocar PR #110 ni PR #115** (Cowork en queue T2-B)
5. **NO tocar branches Catastro** (TA1+TA2+TA5 en paralelo)
6. **NO modificar código kernel** (TA3 es solo env vars + redeploy)
7. **Rollback inmediato** si algo falla — fail-soft, no esperar autorización

## §4 Skill match Ejecutor 1

- Railway CLI + env vars management — skill match alto (hiciste D-4/D-5/D-6 con Railway redeploy + logs)
- Verificación binaria post-redeploy con SQL + curl — skill match perfecto

## §5 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint MEGA-CIERRE-HOY Ejecutor 1 TA3 CERRADO. Railway flags COWORK-RUNTIME-001 Fase 1 activados: COWORK_HOOK_ENABLED=true + COWORK_SESSION_PERSIST=true + COWORK_PREFLIGHT_REQUIRED=true. Redeploy completado. Health check verde post. Kernel asiste Cowork ACTIVO via T1+T4+T5. DRIFT-010 cerrado parcialmente (Fase 1 activa; Fase 2+3 pendientes post-7-días observación).',
  'manus-hilo-ejecutor-1',
  9
);
```

## §6 Coordinación con Catastro paralelo

Tu TA3 + Catastro TA1+TA2 son **independientes**. Pueden correr simultáneo.

Catastro TA5 **depende de** vos cerrar TA3 (verificación runtime). Cuando reportés al bridge TA3 verde, Catastro arranca TA5.

Punto de sincronía: tu reporte → Catastro TA5 verificación binaria de runtime activo.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 07:50 UTC

**Sprint MEGA-CIERRE-HOY Ejecutor 1 TA3 cierra el bottleneck operativo de "memoria persistente activa HOY". 3 env vars Railway = unlock del kernel asistiendo Cowork en tiempo real.**
