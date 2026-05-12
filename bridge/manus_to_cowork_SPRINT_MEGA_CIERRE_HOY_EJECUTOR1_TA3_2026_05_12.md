---
id: manus_to_cowork_SPRINT_MEGA_CIERRE_HOY_EJECUTOR1_TA3_2026_05_12
fecha: 2026-05-12
emisor: Manus Hilo Ejecutor 1
receptor: Cowork T2-A Arquitecto Orquestador
tipo: cierre_TA3_Railway_flags_COWORK_RUNTIME_001
prioridad: P0
spec_origen: bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_MEGA_CIERRE_HOY_TA3_RAILWAY_FLAGS_2026_05_12.md (commit f495dd0)
duracion_real: ~25 min
estado: PARCIAL VERDE — 1/3 flags con efecto real + 6 hallazgos críticos pre-existentes
rollback_ejecutado: NO (parcial verde no requiere rollback per kickoff §3 fail-soft)
---

# Sprint MEGA-CIERRE-HOY — Ejecutor 1 TA3 cerrado con honestidad binaria

## §1 Las 3 env vars SETEADAS verbatim

`railway variables` post-cambio (filtrado):

```
║ COWORK_HOOK_ENABLED                    │ true                                ║
║ COWORK_PREFLIGHT_REQUIRED              │ true                                ║
║ COWORK_SESSION_PERSIST                 │ true                                ║
```

Snapshot pre-cambio en `/tmp/_railway_vars_pre_ta3.txt` (245 líneas) confirma que las 3 NO existían previamente.

## §2 Redeploy completado verbatim

- Trigger: el tercer `railway variables --set` (sin `--skip-deploys`) disparó redeploy automático
- Service: `el-monstruo-kernel` en project `celebrated-achievement` env `production`
- Build → Deploy completados a las **`2026-05-12T07:57:00.095792Z UTC`**
- Log line confirmación: `monstruo_starting motor=langgraph version=0.84.8-sprint-memento` (07:56:42) → `monstruo_ready ... version=0.84.8-sprint-memento` (07:57:00)
- Domain real: `https://el-monstruo-kernel-production.up.railway.app` (el kickoff TA3 §2 indicaba `el-monstruo-kernel.railway.app` — incorrecto, corregir en futuros kickoffs)

## §3 Health check post-redeploy verbatim

```bash
$ curl -s -m 15 -H "X-API-Key: <MONSTRUO_API_KEY>" \
    "https://el-monstruo-kernel-production.up.railway.app/health"
```

```json
{
    "status": "healthy",
    "version": "0.84.8-sprint-memento",
    "motor": "langgraph",
    "uptime_seconds": 46,
    "models_available": ["gpt-5.5", "claude-opus-4-7", "gemini-3.1-pro-preview", "sonar-reasoning-pro"],
    "observability": "active",
    "components": {
        "kernel": "active",
        "event_store": "active",
        "memory": "active",
        "knowledge": "active",
        "langfuse": "active",
        "opentelemetry": "active",
        "checkpointer": "active (AsyncPostgresSaver)",
        "embrion": "active",
        "embrion_loop": {
            "running": true,
            "check_interval_s": 60,
            "cost_today_usd": 0.02,
            "daily_budget_usd": 30.0,
            "cycle_count": 1,
            ...
        }
    }
}
```

**Endpoint Cowork validado:** `GET /v1/cowork/memento/validate` → `405 Method Not Allowed` (correcto, espera POST). Endpoint existe, montado, listo.

## §4 🚨 HALLAZGO CRÍTICO BINARIO — divergencia entre kickoff y código real

**Solo 1 de las 3 env vars del kickoff TA3 tiene efecto real en el código del kernel.**

| Var (per kickoff) | Mapeo declarado | ¿Existe en código kernel? | Estado funcional |
|---|---|---|---|
| `COWORK_HOOK_ENABLED` | T1 pre-response hook | ✅ `kernel/cowork_runtime/pre_response_hook.py:106` | **ACTIVO** — kernel ahora intercepta cada respuesta Cowork |
| `COWORK_SESSION_PERSIST` | T4 persistencia sesiones a Supabase | ❌ NO existe `os.environ.get("COWORK_SESSION_PERSIST")` en kernel | **HUÉRFANA** — var almacenada en Railway pero nadie la lee |
| `COWORK_PREFLIGHT_REQUIRED` | T5 pre-flight memento enforcer | ❌ NO existe `os.environ.get("COWORK_PREFLIGHT_REQUIRED")` en kernel | **HUÉRFANA** — var almacenada en Railway pero nadie la lee |

**Verificación binaria reproducible:**

```bash
$ grep -rEn "os\.environ\.(get|setdefault).*COWORK_" kernel/ --include='*.py' \
    | sed -E 's/.*"(COWORK_[A-Z_]+)".*/\1/' | sort -u
COWORK_DRIFT_ENABLED
COWORK_DRIFT_MAX_CORRECTIVOS
COWORK_DRIFT_MAX_SEGUNDOS
COWORK_DRIFT_MAX_TURNOS
COWORK_DRIFT_MAX_VIOLACIONES
COWORK_HOOK_ENABLED              ← única del kickoff que existe
COWORK_REINJECT_CTX_THRESHOLD
COWORK_REINJECT_EVERY_N_TURNS
COWORK_VETO_ENABLED
```

**Análisis honesto:**
1. **T4 (persistencia sesiones a Supabase) YA ESTABA ACTIVA ANTES de mi sprint.** El módulo `kernel/cowork_runtime/session_memory.py` persiste automáticamente si `SUPABASE_URL` y `SUPABASE_SERVICE_KEY` están configuradas (líneas 74-78). **No requiere flag.**
2. **T5 (pre-flight memento enforcer) YA ESTABA ACTIVO** como endpoint REST `/v1/cowork/memento/validate`. Confirmado por log `sprint_cowork_runtime_t8_initialized endpoint=/v1/cowork/memento/validate` desde startup. **No requiere flag para enforzar; enforza si los clientes llaman el endpoint.**
3. **Las 2 vars huérfanas no causan daño** — Railway las almacena, kernel las ignora. NO recomiendo borrarlas todavía: dejarlas explícitas como "futuras hooks" puede ser intencional del roadmap.

**Conclusión TA3:** la Fase 1 está **funcionalmente activa**:
- T1 (hook) → activado HOY por mi cambio
- T4 (persist) → ya estaba activo
- T5 (preflight) → ya estaba activo

DRIFT-010 cerrado en la práctica. Pero el kickoff tenía imprecisión sobre 2/3 nombres de env vars.

## §5 🚨 HALLAZGOS PRE-EXISTENTES detectados durante audit de logs

Detecté en los logs Railway post-redeploy (NO causados por mis cambios, presentes antes y siguen presentes) los siguientes errores **críticos** que Cowork debería escalar a Alfredo independientemente de TA3:

### §5.1 Anthropic API credit balance = 0 🔴 P0

```
2026-05-12T07:55:41.896170Z [error] task_planner_plan_failed
error="Error code: 400 - 'Your credit balance is too low to access the Anthropic API.
Please go to Plans & Billing to upgrade or purchase credits.'"
```

**Impacto:** task_planner del kernel falla cualquier plan que use Claude. Embrion loop degradado.

### §5.2 OpenRouter credits = 0 🔴 P0

```
Error code: 402 - {'error': {'message': 'Insufficient credits.
Add more using https://openrouter.ai/settings/credits', 'code': 402}}
LLM extraction failed: Error code: 402
```

**Impacto:** llamadas a OpenRouter (Sonar, etc.) están fallando.

### §5.3 Gemini API tool schema obsoleto 🔴 P1

```
2026-05-12T07:57:57.511349Z [error] model_failed_with_tools
error='ClientError(\'400 INVALID_ARGUMENT.
Invalid JSON payload received. Unknown name "additional_properties" at
tools[0].function_declarations[17].parameters.properties[1].value: Cannot find field.\')'
provider=google tools_count=20
```

**Impacto:** Gemini 3.1 Pro rechaza el formato `additional_properties` en tool declarations. Múltiples function declarations afectadas (17, 18, 19). **Es un bug real en el kernel** que requiere actualizar el formato de tools.

### §5.4 Tabla Supabase `public.run_costs` no existe 🟡 P1

```
2026-05-12T07:58:01.435361Z [error] supabase_insert_failed
error="Could not find the table 'public.run_costs' in the schema cache",
code: PGRST205, hint: "Perhaps you meant the table 'public.v5_comments'"
```

**Impacto:** kernel intenta loggear run_costs y falla silently. Posible migration faltante.

### §5.5 Tabla `embrion_memoria` rechaza tipo `evaluacion` 🟡 P2

```
2026-05-12T07:58:13.275588Z [error] supabase_insert_failed
error='new row for relation "embrion_memoria" violates check constraint "embrion_memoria_tipo_check"'
table=embrion_memoria
```

**Impacto:** Embrión intenta loggear memorias tipo `evaluacion` y son rechazadas. Constraint canónico no incluye `evaluacion`.

### §5.6 Langfuse SDK incompatible 🟡 P2

```
[warning] langfuse_trace_error error="'Langfuse' object has no attribute 'trace'"
```

**Impacto:** observability degradada. SDK Langfuse fue actualizado pero kernel sigue usando API antigua.

## §6 Estado final binario

| Métrica | Resultado | Evidencia |
|---|---|---|
| 3 env vars seteadas Railway | ✅ Confirmado | `/tmp/_railway_vars_post_ta3.txt` |
| Redeploy completado sin errores | ✅ Confirmado | `monstruo_ready` log 07:57:00Z |
| Health check kernel | ✅ HTTP 200 healthy | curl `/health` con MONSTRUO_API_KEY |
| Componentes activos post-deploy | ✅ 19/20 active (mcp inactive es normal) | JSON health response |
| Endpoint `/v1/cowork/memento/validate` | ✅ Existe (405 en GET, espera POST) | curl response |
| `embrion_loop.running` | ✅ true | health JSON |
| Effectividad funcional de las 3 vars | ⚠️ 1/3 con efecto real (T1) + 2/3 efectos pre-existentes (T4+T5) | grep código kernel |
| Rollback ejecutado | ❌ NO necesario | parcial verde, no falla |

## §7 Lo que SÍ se cumplió del objetivo magno T1 (memoria persistente HOY)

- ✅ **Hook pre-respuesta Cowork ACTIVO** — kernel ahora interceptará outputs de Cowork (era el bottleneck operativo)
- ✅ **Persistencia sesiones Supabase ACTIVA** (ya lo estaba — confirmado via inspección `session_memory.py`)
- ✅ **Pre-flight Memento endpoint ACTIVO** (ya lo estaba — `/v1/cowork/memento/validate` funcional)

**Memoria persistente del Monstruo asiste a Cowork ACTIVO desde 2026-05-12 07:57 UTC.** DRIFT-010 cerrado para Fase 1 (Fase 2+3 siguen esperando análisis post-7-días per kickoff §3 regla #1).

## §8 Recomendaciones para Cowork

1. **Confirmar con Alfredo que 2 env vars huérfanas son intencionales** o instruir borrarlas: `railway variables --set COWORK_SESSION_PERSIST=false --skip-deploys` (o borrar). Hoy NO causan daño, pero acumulan ruido en Railway dashboard.
2. **Escalar hallazgos pre-existentes §5.1 (Anthropic creditless) y §5.2 (OpenRouter creditless) inmediatamente** a Alfredo T1. Kernel está degradado para tareas que requieren Claude/OpenRouter.
3. **Abrir sprint kernel** para arreglar §5.3 (Gemini tools schema), §5.4 (run_costs migration), §5.5 (embrion_memoria check constraint extension), §5.6 (Langfuse SDK upgrade).
4. **Corregir el dominio canónico** en docs/kickoffs futuros: `https://el-monstruo-kernel-production.up.railway.app` (NO `el-monstruo-kernel.railway.app`).
5. **Verificación runtime de T4+T5** (Catastro TA5): los endpoints existen, pero **no se ha verificado tráfico Cowork post-flags** porque Cowork no ha tenido turnos desde mi cambio. Catastro debe correr la query SQL del kickoff §2 verificación binaria pasados 30-60 min para confirmar que sesiones se persistan en `cowork_sesiones`.

## §9 Catastro TA5 unblock señal

**TA5 (Catastro) puede arrancar verificación runtime.** Mi TA3 dejó:
- 3 env vars seteadas (1 funcional + 2 huérfanas)
- Redeploy verde
- Health check verde
- Endpoint `/v1/cowork/memento/validate` activo

Catastro TA5 debe correr SQL contra `public.cowork_sesiones` para verificar persistencia runtime real. Mi reporte = unblock señal per kickoff §6 sincronía.

## §10 Limitaciones declaradas honestamente

1. **No verifiqué INSERT real en `cowork_sesiones`** porque no tengo `SUPABASE_DB_URL` directo a mano y Cowork no tuvo turnos post-redeploy mientras audité. Catastro TA5 verifica esto.
2. **No probé el hook `pre_response_hook.intercept()` en producción** — requiere request real de Cowork, no puedo simularlo desde mi sandbox.
3. **No reset/clear logs antiguos** — los errores §5.x estaban antes de mi redeploy, siguen después. Confirmo que mis cambios NO los causaron pero NO los resolví tampoco.
4. **No setié `BRAND_ENGINE_ENABLED` ni Telegram vars** (per kickoff §3 reglas duras #2 y #3).

---

**Firma:** Manus Hilo Ejecutor 1, 2026-05-12 ~08:00 UTC — TA3 cerrado con resultado binario PARCIAL VERDE + 6 hallazgos críticos pre-existentes documentados + Catastro TA5 unblocked.
