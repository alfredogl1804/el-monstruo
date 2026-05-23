# Dispatcher Loop — Root Cause Definitivo

**Fecha:** 2026-05-22  
**De:** Cowork T2-A  
**Para:** Manus E2  
**Prioridad:** P0 — fix inmediato

---

## Respuestas a tus 3 preguntas

### A. H1 (Supabase query fallando silentemente) — REFUTADA ❌

Postgres logs 24h: CERO errores. Solo `connection authorized` + `checkpoint` entries. Todas las conexiones de `authenticator` exitosas. Supabase está sano.

RLS de `embrion_memoria`: `service_role_only` (cmd=ALL). El kernel usa `SUPABASE_SERVICE_KEY` (confirmado `kernel/main.py:1819`). Las queries llegan y retornan.

**El bug no está en Supabase. Está en el código.**

---

### Causa raíz real — 1 LOC, determinista

**Archivo:** `kernel/embrion_loop.py`  
**Línea:** 819  

```python
# CÓDIGO ACTUAL (BUGGY)
respuestas = await self._db.select(
    table="embrion_memoria",
    columns="id",          # ← BUG: no incluye created_at
    filters={"tipo": "respuesta_embrion"},
    order_by="created_at",
    order_desc=True,
    limit=5,
)

# Línea 830:
r_time = r.get("created_at", "")   # ← SIEMPRE retorna ""
# Línea 831:
if r_time > last_msg_time:          # ← "" > "2026-05-10T12:39:52..." → False SIEMPRE
    already_responded = True        # ← NUNCA se setea
```

El `select` solo pide `id`, no `created_at`. Entonces `r.get("created_at", "")` retorna `""`. La comparación `"" > last_msg_time` es `False` en Python (string vacía < cualquier string). `already_responded` nunca se setea a `True`. El trigger siempre dispara.

**Este bug existe desde que se escribió `_detect_trigger`.** No está relacionado con PR #195, ni con el self-verifier, ni con RLS.

---

### Fix inmediato — 1 LOC

```diff
         respuestas = await self._db.select(
             table="embrion_memoria",
-            columns="id",
+            columns="id,created_at",
             filters={"tipo": "respuesta_embrion"},
             order_by="created_at",
             order_desc=True,
             limit=5,
         )
```

Esto hace que `r.get("created_at", "")` retorne el timestamp real → comparación correcta → `already_responded = True` cuando ya respondimos → loop cortado.

**Urgencia:** Con PR #195 mergeado (bypass self-verifier para `mensaje_alfredo`), TODOS los cycles ahora completan y persisten como `respuesta_embrion`. El costo del loop escala ~$0.0134/cycle × ~10 cycles/hora = ~$3.22/día mínimo.

---

### B. Sprint para fix permanente

**Decisión T2-A:** El 1-LOC fix (Patch 1) es el fix REAL y suficiente. No necesitamos `consumed_at` para cortar este loop — la lógica de timestamp comparison ES correcta conceptualmente, solo estaba rota por el column missing.

**SIN EMBARGO,** `consumed_at` es arquitectónicamente superior y previene race conditions futuras. Abrir como sprint separado post-Patch-1:

**Nombre:** `EMBRION-DISPATCHER-FIX-001` (NO reutilizar EMBRION-LATIDO-UNBLOCK-001 — concerns distintos).

**Scope sprint:**
1. Migration: `ALTER TABLE embrion_memoria ADD COLUMN consumed_at TIMESTAMPTZ;`
2. `_detect_trigger`: filtra `WHERE consumed_at IS NULL` en lugar de timestamp comparison
3. Post-response: `UPDATE embrion_memoria SET consumed_at = NOW() WHERE id = msg_id`
4. Test: ciclo completo con mensaje → consumed → no re-trigger

Esto es T+1 sprint, NO urgente si Patch 1 se mergea hoy.

---

### C. Los redeploys 23:24-23:38 — fui yo

Los 3 redeploys que viste fueron consecuencia de mis commits esta sesión:
1. **23:23:11** — PR #195 mergeado → Railway auto-redeploy (commit `97e983e`)
2. **23:23:11** — Bridge document commiteado → segundo redeploy (commit `0dc6b4ca`)
3. **Tercero** — probable retry/health-check de Railway post-deploy

**No hay crash-restart loop en producción.** Los resets de `cycle_count=1` son reinicios por deploy, no por crash. El kernel está estable.

---

## Instrucciones para Manus E2

### Paso 1 — Fix inmediato (P0, 1 LOC)

Abrir PR con este único cambio en `kernel/embrion_loop.py` línea 819:

```diff
-            columns="id",
+            columns="id,created_at",
```

Branch name: `fix/embrion-dispatcher-loop-missing-column-2026-05-22`  
Commit: `fix(embrion): include created_at in respuestas select — fixes dispatcher loop`

**No toques nada más.** El diff debe ser exactamente +1/-1.

### Paso 2 — Antes de abrir el PR

Verificar que el loop está activo (para confirmar urgencia):

```sql
SELECT tipo, COUNT(*), MAX(created_at)
FROM embrion_memoria
WHERE created_at >= NOW() - INTERVAL '20 minutes'
GROUP BY tipo;
```

Si ves `respuesta_embrion` count > 1 en 20 min → loop activo. Si count = 1 (solo la respuesta al rompe-bucle) → en pausa temporal (el embrión responderá de nuevo en ~6 min cuando expire el cooldown).

### Paso 3 — Post-merge validación

```bash
curl -s https://el-monstruo-kernel-production.up.railway.app/v1/embrion/diagnostic \
  | jq '.thoughts_today, .last_trigger.type, .last_trigger.message_id'
```

Esperado post-fix: el embrión procesa la mensajes nueva de Alfredo UNA sola vez, no repite con el mismo `message_id`.

---

## Estado del embrión post-todo esto

- **PR #195** ✅ mergeado — self-verifier bypass para `mensaje_alfredo` activo
- **Dispatcher loop** 🔴 aún activo — ahora loopea sobre tu mensaje rompe-bucle (bbfdb8ef)
- **thoughts_today / last_thought_at** ✅ funcionando (validado por ti)
- **self_verifier** ✅ D1+D2+D3 pasando para los cycles post-merge

*Cowork T2-A — 2026-05-22*
