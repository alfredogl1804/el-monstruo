---
id: cowork_to_alfredo_COMANDOS_RAILWAY_PENDIENTES_T1_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Alfredo T1
tipo: comandos_listos_para_copy_paste
prioridad: P1 (decisiones T1 acumuladas, no bloqueantes pero pendientes)
sesion_origen: cowork_sesiones row 3a04e11b-e610-4958-964e-4a709f3a5c61
---

# Comandos Railway listos para tu firma T1

## §1 ¿Qué es este archivo?

3 conjuntos de comandos bash exactos para que vos T1 ejecutes en Railway cuando estés listo. Cero adivinanza, cero variables a llenar — copy/paste directo. Cowork preparó estos durante sesión 2026-05-12 ~07:30 UTC bajo objetivo magno "kernel asiste memoria persistente Cowork" (QW1+QW2 cerrados, esto es QW-bonus D).

**NO ejecutar todos al mismo tiempo.** Cada uno requiere firma T1 explícita + propio momento operativo. Documentados aquí para que cuando decidas activar, NO pierdas tiempo buscando sintaxis.

---

## §2 Comando 1 — Brand Engine canary shadow (post-PAR_BICEFALO_001)

### Contexto

PR #108 + #109 + #111 mergeados HOY (Perplexity T2-B audit). Brand Engine instalado como Embrión 2. **`BRAND_ENGINE_ENABLED=false` por default** (shadow mode = no procesa requests).

Activar a `enabled=true mode=shadow` significa: Brand Engine procesa requests pero NO emite respuestas al usuario, solo loguea qué habría dicho. Genera dataset comparativo Embrión 1 vs Embrión 2.

### Comando exacto

**Opción A — Vía Railway CLI** (si tenés `railway` instalado):

```bash
# Asegurate de estar en proyecto correcto
railway link  # selecciona el-monstruo-kernel

# Setear env vars
railway variables set BRAND_ENGINE_ENABLED=true
railway variables set BRAND_ENGINE_MODE=shadow

# Trigger redeploy para que aplique
railway redeploy
```

**Opción B — Vía Railway Dashboard** (UI):

1. Ir a https://railway.app/project/<tu-project-id>
2. Click servicio `el-monstruo-kernel`
3. Tab "Variables"
4. Agregar: `BRAND_ENGINE_ENABLED=true`
5. Agregar: `BRAND_ENGINE_MODE=shadow`
6. Click "Deploy" para redeploy

### Verificación post-activación

```sql
-- Después de redeploy, verifica rows en embrion_validation_log:
SELECT count(*) FROM public.embrion_validation_log WHERE mode='shadow';
-- Esperado: >0 después de 5-10 min de tráfico
```

### Cómo desactivar si algo falla

```bash
railway variables set BRAND_ENGINE_ENABLED=false
railway redeploy
```

---

## §3 Comando 2 — Telegram T3 GUARDIAN (alerting)

### Contexto

GUARDIAN-AUTONOMO-001 (PR #112) mergeado HOY. T3 alerting Telegram está en **stub fail-closed** porque requiere tu firma explícita de 3 valores binarios:

### 3 valores que vos decidís

1. **`TELEGRAM_CHAT_ID`** — chat donde llegan alertas Guardian. Para sacarlo:
   - Abrí Telegram, buscá tu bot existente del Monstruo (debería ser `@elmonstruo_bot` o similar)
   - Mandale `/start`
   - Ejecutá `curl "https://api.telegram.org/bot<TU_BOT_TOKEN>/getUpdates" | jq` (o similar)
   - El `chat.id` en la respuesta es tu valor

2. **Ventana horaria permitida** — ej: `8-22` (8am a 10pm hora MX). Fuera de esa ventana NO se envían alertas (silencio madrugada).

3. **Rate limit** — ej: `30` (1 alerta cada 30 min máximo). Deduplicación por `objective_id`.

### Comando exacto

```bash
railway variables set TELEGRAM_CHAT_ID=<TU_VALOR>
railway variables set TELEGRAM_ALERT_WINDOW=8-22
railway variables set TELEGRAM_RATE_LIMIT_MIN=30
railway redeploy
```

### Test post-activación

```bash
# Trigger manual de alerta Guardian (debería llegar a Telegram):
railway run python -m kernel.guardian_runner --force-alert-test
```

Si NO llega alerta en 1 min: rollback temporal con `railway variables set TELEGRAM_CHAT_ID=` (vacío) → degrada silenciosamente.

---

## §4 Comando 3 — Activar flags COWORK-RUNTIME-001 (DRIFT-010)

### Contexto

Sprint COWORK-RUNTIME-001 cerrado 2026-05-11 (PR #90) con **9 capabilities en `enabled=false` shadow mode**. DRIFT-010 declara: "decisión orden activación flags" pendiente desde entonces.

Mi recomendación binaria post-QW1/QW2 + V25 grave + F2+F21: activar primero **T1 + T4 + T5** porque cierran el problema de fragilidad Cowork directamente.

### Comando exacto (orden recomendado por Cowork)

```bash
# Fase 1: capability fundamentales (logger + persistencia + memento)
railway variables set COWORK_HOOK_ENABLED=true            # T1 pre-response hook (intercept + audit)
railway variables set COWORK_SESSION_PERSIST=true         # T4 persistencia sesiones a Supabase
railway variables set COWORK_PREFLIGHT_REQUIRED=true      # T5 pre-flight memento enforcer
railway redeploy

# Esperar 30 min de tráfico real + verificar audit log + cowork_sesiones rows

# Fase 2: detector semántico + antipattern (post-7 días si Fase 1 OK)
railway variables set COWORK_SEMANTIC_ENABLED=true        # T2 detector semántico
railway variables set COWORK_ANTIPATTERN_ENFORCE=true     # T6 F1-F22 enforced

# Fase 3: veto canal Telegram (post-firma T3 GUARDIAN arriba)
railway variables set COWORK_VETO_TELEGRAM=true           # M9 veto channel
```

### Verificación post-Fase-1

```sql
-- Después de 30 min: deberían poblarse rows en cowork_sesiones desde el kernel
SELECT count(*) FROM public.cowork_sesiones WHERE fecha_inicio > NOW() - INTERVAL '1 hour';
-- Esperado: >1 (la actual + nuevas)

-- Y entries en audit log JSONL:
ls -la bridge/t1_audit_log.jsonl
wc -l bridge/t1_audit_log.jsonl
```

### Si algo falla

```bash
# Rollback Fase 1 inmediato:
railway variables set COWORK_HOOK_ENABLED=false
railway variables set COWORK_SESSION_PERSIST=false
railway variables set COWORK_PREFLIGHT_REQUIRED=false
railway redeploy
```

---

## §5 Mi recomendación binaria sobre orden de activación

Si pudiera ejecutar yo mismo (no puedo — sandbox sin Railway CLI ni env vars):

**Orden óptimo binario:**

1. **PRIMERO: Comando 3 Fase 1** (T1+T4+T5 COWORK-RUNTIME) — porque cierra DRIFT-010 + V25 problem estructuralmente
2. **SEGUNDO: Comando 1** (Brand Engine shadow) — empieza dataset comparativo Embrión 1 vs 2
3. **TERCERO: Comando 2** (Telegram T3) — requiere tu firma específica de 3 valores

ETA total ejecución: ~10 min copy/paste + ~30 min wait redeploys + ~30 min verificación = ~70 min de tu tiempo real cuando decidas.

---

## §6 Reglas duras

1. **NO ejecutar los 3 comandos al mismo tiempo** — esperar verificación entre cada uno (10-30 min)
2. **Rollback siempre disponible** — cada comando tiene su `set X=false + redeploy` documentado
3. **Si dudas, NO ejecutes** — preguntá a Cowork antes
4. **Reportá en chat** post-ejecución de cada comando para que Cowork actualice memoria persistente con el estado nuevo

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 07:35 UTC

**Comandos preparados como QW-bonus D del objetivo magno HOY. Cero adivinanza al momento de ejecutar. Cuando decidas, copy/paste directo + verificación binaria + reporte al bridge.**
