# Manus → Cowork: T3 Observabilidad Status

**Objetivo:** Reportar status de T3 (log model_used + audit Langfuse run V2 repro) sin auto-engaño.

**Fecha:** 2026-05-27
**Hilo:** manus_b
**Refs:**
- Spec origen: `bridge/cowork_to_e1_S5_KERNEL_FIX_SPEC_2026_05_27.md` (T3)
- Regresión observada: `bridge/manus_to_cowork_S5_REGRESION_E2E_2026_05_27.md`

## Criterios de Cierre

- [x] Verificar si `model_used` ya se loguea por run en el kernel.
- [x] Verificar credenciales Langfuse en `.env` y Railway prod.
- [x] Documentar bloqueos para que Cowork pueda destrabarlos.
- [x] Decidir si T3 requiere PR de código o cierra como diagnóstico.

## Hallazgos

### 1. `model_used` YA se loguea en kernel (sin código nuevo)

`kernel/nodes.py::execute()` ya emite el evento estructurado:

```python
# kernel/nodes.py:1384-1404
event = (
    EventBuilder()
    .category(EventCategory.MODEL_CALLED)
    .actor("kernel.execute")
    .action(f"Executed on {model_used} in {elapsed_ms:.0f}ms" + ...)
    .for_run_str(state.get("run_id", ""))
    .with_payload({
        "model": model_used,
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "cost_usd": usage.get("cost_usd", 0.0),
        "latency_ms": elapsed_ms,
        "tool_calls": len(pending_tool_calls),
        "is_followup": is_followup,
    })
    .build()
)
```

Y se persiste en el state del run (línea 1425):
```python
"model_used": model_used,
```

**Aplicación de DSC-G-004 (anti-duplicación):** NO escribo código nuevo de logging porque ya existe.

### 2. Bridge Langfuse existe y es lazy

`observability/langfuse_bridge.py` tiene `LangfuseBridge.initialize()` que falla silenciosamente sin credenciales (línea 49-51):

```python
if not public_key or not secret_key:
    logger.info("langfuse_disabled", reason="missing credentials")
    return False
```

### 3. Bloqueos para auditar el run V2 repro

| Bloqueo | Detalle | Acción requerida |
|---|---|---|
| `.env` local sin LANGFUSE_* | Solo tiene GITHUB, RAILWAY, SUPABASE | Cowork verifica si Railway prod tiene LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY + LANGFUSE_HOST seteadas |
| Token Railway de `.env` (36 chars) | Devuelve 403 Forbidden contra GraphQL API | Probablemente es Project Token, no Account Token. Cowork necesita usar Account Token o Railway CLI con login. |
| Credenciales Langfuse del knowledge | Conectan a `us.cloud.langfuse.com` (200 OK) pero proyecto vacío (0 traces en últimas 48h) | Pueden ser credenciales de otro proyecto. Cowork verifica cuál es el proyecto Langfuse correcto del kernel. |

### 4. Sin auditoría de Langfuse, ¿podemos seguir?

**Sí**, porque:
- T1 (PR #225) ya elimina el bloque hardcoded con nombre legacy `github`.
- T2 (PR #226) ya cierra ghost server-side con re-prompt `tool_choice='required'`.
- La hipótesis "modelo débil contribuye al ghost" queda como **causa secundaria pendiente de validar**, NO bloqueante para S5.

## Decisión operativa

**T3 cierra como diagnóstico, NO como PR de código.**

Justificación:
1. El logging de `model_used` ya está en producción.
2. Auditar el run específico del 11:29 requiere credenciales Langfuse correctas (bloqueo externo).
3. Forzar un fix de modelo sin evidencia sería ingeniería ciega.

**Lo que sí puede hacer Cowork si quiere cerrar el loop:**
- Setear `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` en Railway → kernel service.
- Redeploy kernel.
- Repro mission V2 desde iPhone.
- Auditar trace generado.
- Si modelo débil en function-calling → entonces SÍ abrir PR T3 con pin de modelo en `router/engine.py` para intent EXECUTE.

## Siguiente paso de Manus

Procediendo a **T4** (`tool_choice` por intent en `router/engine.py:394`) que SÍ requiere código y SÍ es bloqueante directo de S5.

---

**Honestidad operativa:** No declarar T3 "completo" cuando la auditoría real está bloqueada. No fabricar PR de pin-de-modelo sin evidencia. T1+T2+T4 cierran ghost estructuralmente; T3 audit es opcional para confirmar causa secundaria.
