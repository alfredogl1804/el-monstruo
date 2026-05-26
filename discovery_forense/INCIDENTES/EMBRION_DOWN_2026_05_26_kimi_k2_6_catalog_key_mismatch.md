---
id: INCIDENTE-EMBRION-DOWN-2026-05-26
tipo: incidente_operativo_p1
proyecto: EL-MONSTRUO
componente: kernel/embrion_loop + kernel/catastro
estado: abierto
severidad: P1 (afecta autonomía pero no datos)
fecha_deteccion: 2026-05-26
detectado_por: manus_b (durante auditoría pre-articulación T1-MAGNA-005/006/007)
afecta_a:
  - T1-MAGNA-006 (precondición operativa)
  - FORJA-OMEGA-VISUAL Bloque B (componente EmbryoWorkerCard)
  - autonomy scheduler nightly jobs
fuentes_verificadas:
  - genome:/v1/genome/now (live24h.json: 8+ ciclos consecutivos failing)
  - codigo:kernel/embrion_loop.py:104 (ACTOR_MODEL default = "gpt-5.5", env: EMBRION_ACTOR_MODEL)
  - codigo:kernel/embrion_loop.py:_select_model_via_catastro (helper que consulta Catastro)
  - codigo:kernel/catastro/sources/lmarena.py:287 (registra "kimi-k2.6" con punto)
  - codigo:kernel/external_agents.py:183 (modelo OpenRouter "moonshot/kimi-k2.5")
  - codigo:kernel/fallback_engine.py:103 (fallback con "kimi-k2.5")
  - sintoma:All models failed for intent chat. Tried: ['kimi-k2-6']. Last error: None
---

# Incidente — Embrion Loop down: catalog key mismatch `kimi-k2-6` vs `kimi-k2.6` / `kimi-k2.5`

## Resumen ejecutivo

El `embrion_loop` lleva al menos 8 ciclos consecutivos fallando con el error literal:

> *All models failed for intent chat. Tried: ['kimi-k2-6']. Last error: None*

El loop sigue **vivo** (cycle_count crece, late cada 60s, gasta tiempo de CPU), pero **no produce pensamientos** porque ningún modelo responde. El presupuesto diario del embrion (`EMBRION_DAILY_BUDGET=30.0` USD) se está quemando en intentos fallidos sin output.

Causa raíz preliminar: **mismatch entre el catalog key que el `Catastro RecommendationEngine` retorna (`kimi-k2-6` con guion) y los identifiers reales en la red de modelos** (`moonshot/kimi-k2.5` o `kimi-k2.6` con punto). El embrion intenta llamar un modelo que no existe en ningún provider, recibe `Last error: None` (porque todos los providers ni siquiera intentan resolverlo) y declara fallo total.

Severidad: P1 (afecta autonomía pero no datos persistidos; no hay corrupción, solo parálisis).

## Evidencia técnica

### Síntoma observable

Endpoint `https://el-monstruo-kernel-production.up.railway.app/v1/genome/now/health` devuelve `{"ok":true,"binario_100":true,...,"refresh_job":{"status":"running","kind":"full"}}` pero internamente `live24h.json` registra el siguiente patrón consecutivo:

```json
{
  "intent": "chat",
  "error": "All models failed for intent chat. Tried: ['kimi-k2-6']. Last error: None",
  "cycle_id": "...",
  "thought_actionable": null,
  "cost_usd": 0.0
}
```

(8+ entradas consecutivas, cycle_id creciente, todas sin output)

### Configuración actual

`kernel/embrion_loop.py:104`:

```python
ACTOR_MODEL = os.environ.get("EMBRION_ACTOR_MODEL", "gpt-5.5")
```

El default es `gpt-5.5` (catalog key del catálogo canónico de sabios). En producción, la env var no parece estar fijando explícitamente este modelo, lo que delegaría al fallback. **Pero** existe un wiring (Sprint CATASTRO-WIRING-001 firmado por Cowork 2026-05-18) que reemplaza este default consultando al Catastro en runtime:

```python
EMBRION_CATASTRO_ENABLED = os.environ.get("EMBRION_CATASTRO_ENABLED", "true")
```

Cuando `EMBRION_CATASTRO_ENABLED=true`, el embrion llama `_select_model_via_catastro(use_case="autonomous_thought", fallback=ACTOR_MODEL)`. Si el Catastro retorna un modelo válido, lo usa. Si retorna error o None, cae al fallback `gpt-5.5`.

### Inconsistencia detectada en los datos del Catastro

`kernel/catastro/sources/lmarena.py:30` registra ranking actual:

> *gpt-5.5 (#6), gemini-3.1-pro (#13), kimi-k2.6 (#10).*

`kernel/catastro/sources/lmarena.py:287`:

```python
"model_name": "kimi-k2.6",
```

Es decir: en LMArena la naming es **`kimi-k2.6` con punto**. Pero el embrion intenta llamar **`kimi-k2-6` con guion**. Hipótesis: el `RecommendationEngine` o algún normalizador entre el Catastro y el helper `_select_model_via_catastro` está convirtiendo el punto a guion (probablemente para sanitizar como filename o database key) sin mantener un mapeo bidireccional.

`kernel/external_agents.py:183`:

```python
model="moonshot/kimi-k2.5"
```

Aquí el provider real (Moonshot via OpenRouter) usa **`kimi-k2.5` (versión anterior)**. Es decir: el catálogo del Monstruo registra `kimi-k2.6` pero el SDK de OpenRouter expone `kimi-k2.5`. **Doble mismatch**: el ranking dice 2.6, el provider tiene 2.5, y el embrion pide 2-6.

`kernel/fallback_engine.py:103`:

```python
"models": ["deepseek-r1-0528", "kimi-k2.5"]
```

El fallback engine también usa `kimi-k2.5` (sin guion, con versión vieja). El embrion no llega aquí porque su error es de modelo no resoluble en el primer intento, no fallback chain.

### Cadena de fallo reconstruida

1. Embrion empieza ciclo, llama `_select_model_via_catastro("autonomous_thought", fallback="gpt-5.5")`.
2. El Catastro `RecommendationEngine` consulta su data interna, retorna que el mejor modelo para `autonomous_thought` es **`kimi-k2-6`** (con guion, normalizado).
3. El embrion intenta resolver `kimi-k2-6` contra el dispatcher de modelos (OpenRouter, Anthropic SDK, OpenAI SDK).
4. Ningún provider conoce `kimi-k2-6`. OpenRouter conoce `moonshot/kimi-k2.5`. Anthropic no tiene Kimi. OpenAI no tiene Kimi.
5. El dispatcher devuelve "no provider for model" sin error específico.
6. El loop captura `All models failed` y registra `Last error: None`.
7. **El fallback `gpt-5.5` no se intenta** porque el bug está en la resolución del primer intento, no en la cascada de fallback.

## Impacto

- **Autonomía del Monstruo paralizada**: el embrion no piensa, no genera thoughts, no consolida, no consulta sabios.
- **Presupuesto desperdiciado**: cada ciclo cuenta como intento aunque no haya consumo LLM real, pero hay overhead de CPU + DB writes + log writes.
- **T1-MAGNA-006 bloqueada operativamente**: cualquier opción B/C/D queda suspendida hasta que el embrion piense de nuevo.
- **Tablero muestra datos engañosos**: `LivePulse` reporta embrion vivo (cycle_count creciente), pero la operación cognitiva está rota.

## Causa raíz: tres hipótesis ordenadas por probabilidad

### Hipótesis 1 (alta probabilidad): normalización de catalog key con guion

El `RecommendationEngine` o un pre-procesador en `kernel/catastro/recommendation_engine.py` está aplicando `name.replace(".", "-")` para sanitizar el catalog key (probablemente para que sea un identifier válido en variables Python o columnas SQL). Pero el dispatcher de modelos espera el nombre original con punto. **Falta el mapeo de vuelta** al consultar el provider.

### Hipótesis 2 (media probabilidad): el Catastro registró kimi-k2.6 pero el provider real es kimi-k2.5

LMArena reporta `kimi-k2.6` como el modelo nuevo. Pero OpenRouter aún expone `moonshot/kimi-k2.5`. El catálogo del Monstruo se actualiza con la información de LMArena más rápido de lo que los providers se actualizan. **Drift entre fuente de ranking y proveedor de inferencia.**

### Hipótesis 3 (baja probabilidad): env var EMBRION_ACTOR_MODEL fijada manualmente con valor incorrecto

Alguien (o algún sprint anterior) fijó `EMBRION_ACTOR_MODEL=kimi-k2-6` en Railway directamente, bypassing el Catastro. Esto sería visible en Railway dashboard.

## Verificaciones inmediatas para confirmar causa raíz

```bash
# 1. Ver env vars del servicio en Railway
railway variables --service el-monstruo-kernel-production | grep EMBRION

# 2. Buscar el normalizador que convierte . → -
grep -rn "replace(\".\", \"-\")\|replace('.', '-')" kernel/catastro/ --include="*.py"

# 3. Ver qué key específica retorna el Catastro
curl -sS https://el-monstruo-kernel-production.up.railway.app/v1/catastro/recommend \
  -H "X-API-Key: $MONSTRUO_WRITE_TOKEN" \
  -d '{"use_case":"autonomous_thought"}' | python3 -m json.tool

# 4. Ver si OpenRouter expone kimi-k2.6 hoy
curl -sS https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" | grep -i kimi
```

## Fix propuesto (4 niveles, ascendente)

### Fix nivel 1 — Workaround inmediato (5 minutos)

Fijar env var en Railway: `EMBRION_CATASTRO_ENABLED=false`. Esto rompe el wiring del Catastro y el embrion vuelve al hardcode `gpt-5.5`. **Reversible, no toca código.** Costo: el embrion pierde la inteligencia adaptativa del Catastro temporalmente.

### Fix nivel 2 — Forzar fallback explícito (15 minutos)

Patch en `kernel/embrion_loop.py:_select_model_via_catastro`: si el catalog key retornado contiene `kimi` pero no se puede resolver, log warning y caer a fallback inmediatamente sin reportar `All models failed`. **Mejora resiliencia sin tocar el bug raíz.**

### Fix nivel 3 — Corregir el normalizador (1 hora)

Identificar el código que convierte `.` → `-` en el catalog key (Hipótesis 1) y agregar el mapping inverso al consultar el provider. Test unitario: `assert resolve_provider_key("kimi-k2-6") == "moonshot/kimi-k2.5"` (o similar). **Resuelve el bug raíz.**

### Fix nivel 4 — Sincronización Catastro ↔ providers (1 sprint)

Construir un job nightly que verifique para cada modelo registrado en el Catastro si está disponible en al menos un provider (OpenRouter, Anthropic, OpenAI). Si no, marcar como `unavailable: true` en el Catastro y excluir de las recomendaciones. **Previene este tipo de bugs en el futuro.**

## Recomendación de Hilo B

**Aplicar Fix nivel 1 ahora mismo (Railway env var)** mientras se diagnostica con detalle Fix nivel 3. El embrion vuelve a operar en menos de 5 minutos con `gpt-5.5` hardcoded. Esto desbloquea la precondición operativa de T1-MAGNA-006.

En paralelo, ejecutar las 4 verificaciones para confirmar la hipótesis correcta. Una vez identificado el normalizador, aplicar Fix nivel 3 con tests. Fix nivel 4 queda como sprint propio si decides invertir en prevención sistémica.

## Acción requerida del operador

1. Acceder a Railway dashboard del servicio `el-monstruo-kernel-production`.
2. Agregar/modificar env var: `EMBRION_CATASTRO_ENABLED=false`.
3. Reiniciar servicio (Railway lo hace solo al cambiar env).
4. Confirmar en `/v1/genome/now` (live24h) que los próximos 3 ciclos no fallan.
5. Notificar a Hilo B en este hilo o vía bridge para que diagnostique Fix nivel 3.

## Cierre del incidente

Este issue se cierra cuando:

1. `live24h.json` muestra 30 ciclos consecutivos sin error de modelo.
2. Se identifica y documenta la causa raíz exacta (cuál de las 3 hipótesis).
3. Se aplica fix nivel ≥3 (no solo workaround).
4. Se agrega test de regresión que prevenga reaparición.
5. Si aplica, se firma DSC nuevo sobre la política de naming/normalización de catalog keys.

## Notas finales

Este incidente fue detectado **incidentalmente** durante la articulación de T1-MAGNA-005/006/007. No estaba reportado por el sistema de alertas. Implica que **el observatorio del Monstruo no tiene alerta sobre "embrion vivo pero sin output"** — solo alerta sobre "embrion muerto" o "embrion sin lock".

Recomendación derivada (sub-issue): construir métrica `embrion_thoughts_per_hour` con threshold mínimo (ej: 1/h). Si el threshold se rompe pero el loop sigue vivo, alerta P1 automática. Esto sería un sub-sprint dentro de la Capa 1 (Manos / Observabilidad completa).

---

**Detectado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Fecha de detección:** 2026-05-26
**Asignar a:** Hilo B (diagnóstico Fix nivel 3) + Operador (Fix nivel 1 manual en Railway)
**Bloquea:** T1-MAGNA-006 precondición operativa, autonomía del Monstruo
**Tiempo estimado de resolución:** 5 minutos (Fix 1) + 1 hora (Fix 3) = 1.5 horas
**Thread Immunity Session:** 8af84475-598b-4d14-aa79-7d5e0c0c589c
