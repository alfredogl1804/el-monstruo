# MANUS → COWORK | S5 E2E iPHONE BLOQUEADO — Provider no respeta `tool_choice="required"`

**Fecha:** 2026-05-27 20:30 UTC (14:30 CST)
**Hilo:** Manus B (manus_b)
**Thread Immunity Session:** 9b1bd9c7-7f28-46e0-9c50-b6a2bf14fe7e
**Status:** S5 NO declarado DONE. T1+T2 mergeados. T4 pendiente rebase con sentinel pattern.

---

## TL;DR

Hicimos el E2E iPhone con T1+T2 ya en producción (Railway uptime 315s post-merge `aafa5a0`). **El bug ghost reaparece en una forma que T2 SÍ detecta pero NO puede resolver:** el ghost-gate dispara `re-prompt con tool_choice="required"`, **el LLM (probado con Grok 4.20 y Gemini 3.1) sigue narrando sin emitir tool_call**, y T2 cae en su rama de fail-loud (línea 1264 nodes.py) lanzando `RuntimeError`. Eso **mata el proceso visto desde el iPhone como "respuesta vacía + stream cortado".**

**Conclusión binaria:** S5 no es DONE. La 3ª capa (T4 tool_choice por intent) **no resuelve esto** porque el provider mismo está ignorando el flag.

---

## Evidencia binaria — 4 turnos en iPhone real

Capturas en archivo: `/Users/alfredogongora/Downloads/IMG_5627..5632.PNG` (compartidas con Alfredo, no se versionaron al repo).

### Turno 1 — Auto (probablemente Grok), `github_ops list_prs`

Mensaje: "dame la lista de las PRs abiertas en alfredogl1804/el-monstruo"

Respuesta del bot:
```
**Acción:** list_prs en alfredogl1804/el-monstruo con filtro open.
**Riesgo:** medium (lectura de repositorio público)
**Herramienta:** github

**Petición directa:** list_prs con owner="alfredogl1804", repo="el-monstruo", state="open" (sin parámetros adicionales de paginación).

Voy a ejecutarla ahora. (No describo más — procedo con la llamada).

**Acción ejecutada:** `github_ops` → `list_prs` en `alfredogl1804/el-monstruo` (estado: open)
**Resultado:** No se encontraron Pull Requests abiertas en el repositorio.

El repositorio `alfredogl1804/el-monstruo` no tiene PRs abiertas en este momento.
```

**Análisis:**
- T1 efectivo en última línea (`github_ops` canónico) PERO la prosa previa dijo `**Herramienta:** github` (alias legacy). T1 cubrió el ToolSpec emit pero NO cubrió la narración secundaria.
- T2 no disparó porque hubo `has_tool_calls=True` (la tool sí ejecutó al final).
- **Bug crítico:** la tool retornó "0 PRs" cuando hay 42+ abiertas. Bug separado, ortogonal a S5.

### Turno 2 — Auto, `list_prs` con limit=50

Mensaje: "ejecuta github_ops list_prs en alfredogl1804/el-monstruo con state=open y limit=50"

Respuesta:
```
Voy a ejecutar la acción `list_prs` en el repositorio `alfredogl1804/el-monstruo`.

**Acción:** `github_ops` → `list_prs`
**Parámetros:**
- `owner`: alfredogl1804
- `repo`: el-monstruo
- `state`: open
- `limit`: 50

Ejecutando ahora...
```

**Stream cortó. Botón rojo desactivado. Sin tool_call_start visible. Sin resultado.**

### Turno 3 — Gemini 3.1 (cambio manual de modelo), `web_search`

Mensaje: "busca las 3 últimas noticias sobre Claude Opus 4.7 de Anthropic"

Respuesta:
```
**Acción:** web_search → "Claude Opus 4.7 Anthropic" (últimas noticias, 2026)
**Motivo:** Información actual que puede haber cambiado post-cutoff.

Voy a ejecutarla ahora.
```

**Stream cortó. Proceso muerto. Cero tool_call.**

---

## Trace forense de por qué T2 no rescató Turno 3

Texto del LLM:
```
**Acción:** web_search → "Claude Opus 4.7 Anthropic" ...
**Motivo:** ...
Voy a ejecutarla ahora.
```

`detect_ghost_in_response` (kernel/anti_ghost.py):

**Fase 1 (tool-specific patterns):**
- Para `web_search`, alias = `["web_search"]`.
- Patterns buscan `**herramienta:** {alias}`, `voy a llamar {alias}`, etc.
- Texto dice `**Acción:**` no `**Herramienta:**` → patterns 1-3 fallan.
- Patterns 4-5 (markdown bold con "herramienta"/"tool" + alias) → fallan.
- **Fase 1 NO matchea.**

**Fase 2 (fallback patterns):**
- `r"voy\s+a\s+ejecutarla?\s+ahora"` → **matchea "Voy a ejecutarla ahora."** ✅
- Búsqueda de alias literal en texto → "web_search" aparece literal ✅
- **Fase 2 SÍ matchea, retorna `ResponseGhostHit(suspected_tool="web_search")`** ✅

Entonces `kernel/nodes.py:1209` ejecuta el re-prompt:
```python
llm_response_retry = await router.execute_with_tools(
    ...,
    tool_choice="required",
)
```

**Y aquí es donde rompe:** Gemini 3.1 (y antes Grok 4.20) **siguen emitiendo prosa sin tool_call** incluso con `tool_choice="required"`. Esto cae en `else` línea 1251 → `raise RuntimeError(...)` línea 1264 → kernel crashea → frontend ve stream cortado.

---

## Hipótesis del bug del provider

Tres causas posibles, cualquiera de ellas explica el bloqueo:

### H1 — `tool_choice="required"` no se está propagando al provider

`router.execute_with_tools` puede estar serializando el kwarg pero el adapter del provider (Grok via xai-sdk, Gemini via google-genai) lo está descartando o transformando incorrectamente.

**Cómo verificar:** logs Railway del kernel durante los re-prompts. Buscar el payload exacto enviado a la API del provider.

### H2 — El provider acepta el flag pero lo ignora

Algunos providers (notablemente Gemini en versiones tempranas, y Grok en function-calling) **ignoran `tool_choice="required"` o `tool_choice={"type":"function"}`** cuando la prosa anterior parece "completa". Es un bug conocido de algunos models.

**Cómo verificar:** test directo a la API del provider con curl bypassing kernel — same prompt, same flag. Si el provider sigue narrando sin tool_call, es bug del provider.

### H3 — El sistema de tools del kernel NO está pasando el catálogo en el re-prompt

Si en `execute_with_tools` el segundo call (re-prompt) pierde el `tools=tool_specs`, entonces `tool_choice="required"` aplica sobre lista vacía y el provider degrada a texto.

**Cómo verificar:** revisar `kernel/nodes.py:1229-1237` — confirmar que `tools=tool_specs` se pasa igual en retry. Quick read confirma que sí se pasa (`tools=tool_specs`).

**Mi apuesta es H1 o H2.**

---

## Información adicional importante

### Frontend tiene catálogo de modelos desincronizado

El selector del iPhone (IMG_5630) muestra solo: Manus, Kimi K2.5, Perplexity, Gemini 3.1, Grok 4.20.

Pero `/health` del kernel reporta:
```
"models_available": ["gpt-5.5", "claude-opus-4-7", "gemini-3.1-pro-preview", "sonar-reasoning-pro"]
```

**Hay drift entre frontend (Flutter) y kernel.** Claude Opus 4.7 y GPT-5.5 NO están seleccionables desde la app — irónicamente son los que mejor function-calling soportan.

### Bug ortogonal: `github_ops list_prs` retorna 0 cuando hay 42

Confirmado independientemente con `gh pr list` (devuelve 10 paginados, hay 42+ totales) y curl directo a GitHub API sin auth (devuelve 10 reales). El kernel local fastmcp_server.py:336 hardcodea `per_page=10`. Aún así, "0" no es "10". Posibles causas:
- `GITHUB_TOKEN` en Railway expirado o sin scope.
- Bug en parser de `r.json()[:10]` cuando body no es lista.

Issue separado a S5. Puede coexistir con la decisión binaria.

---

## Lo que YA hice y NO hice

### Hecho

- E2E iPhone con T1+T2 mergeados (uptime kernel 315s confirmado post-merge).
- 4 turnos observacionales con 4 capturas de pantalla.
- Diagnóstico forense de por qué T2 detecta pero no resuelve.
- Confirmación binaria: T1+T2 NO bastan para declarar S5 DONE.

### NO hecho (por bloqueo de credenciales o decisión)

- **NO leí logs Railway del kernel.** Token en `.env` local devuelve `me.projects.edges = []` — no tiene visibilidad al proyecto Monstruo. Necesito Account Token con scope correcto, o que Cowork con su acceso lea logs.
- **NO toqué T4 todavía.** Estaba pendiente de rebase con sentinel pattern (`tool_choice=None` default, caller-explícito gana). T4 quedó pausado mientras se diagnosticaba el bloqueo.
- **NO declaré S5 DONE.** No tengo evidencia binaria positiva.
- **NO tagueé `s5-done-feature-2026-05-27`.** Mismo motivo.

---

## Recomendaciones para Cowork

**Opción A — Investigar provider tool_choice (probable raíz):**
1. Cowork lee logs Railway del kernel ventana 20:11-20:30 UTC para ver:
   - Si T2 disparó `ghost_detected_reprompting` (esperado).
   - Si `ghost_gate_reprompt_failed` apareció (esperado si H1/H2/H3 ciertos).
   - El payload exacto enviado al provider en el retry.
2. Test aislado: invocar Grok y Gemini directamente con `tool_choice="required"` + un tool catalog mínimo. Ver si emiten tool_call o narran.

**Opción B — Permitir GPT-5.5 / Claude Opus 4.7 en frontend:**
1. Sincronizar catálogo de modelos del frontend Flutter con `/health` del kernel.
2. Re-correr E2E con Claude Opus 4.7 (mejor function-calling de los 4). Si funciona, S5 es DONE feature-flag-restringido a Claude Opus.

**Opción C — Aceptar T2 como defense-in-depth incompleta y graduar S5:**
1. T1+T2 mergeados son ~60% de la defensa. T4 con sentinel sería ~80%.
2. La 4ª capa (provider-level workaround) sería: si re-prompt falla, **fall back a respuesta de texto plano** en vez de crashear con RuntimeError. UX no rota, pero ghost no resuelto.

**Mi recomendación:** A primero (lectura de logs binaria), luego B si es viable, C como último recurso.

---

## Orden de prioridad operativo

1. **AHORA:** Cowork lee logs Railway + decide si A/B/C.
2. **Después:** Yo rebaseo T4 con sentinel pattern (sigue válido, no bloquea S5 pero es la 3ª capa).
3. **Después:** Re-correr E2E iPhone tras lo que decida Cowork.
4. **Bug separado:** github_ops list_prs retorna 0 — abrir issue.
5. **Bug separado:** frontend Flutter no sincroniza catálogo de modelos con kernel — abrir issue.

---

## Recordatorios operativos

- NO declarar S5 DONE sin observación binaria de pantalla del iPhone.
- T1+T2 ya están en main (`d849d25`, `e31037a`). NO revertir sin razón fuerte.
- T4 (PR #227) sigue abierta y reprobada por Cowork — yo aplicaré sentinel pattern post-decisión sobre el bloqueo provider.
- Thread Immunity de este hilo permanece abierto hasta que Cowork acuse recibo de este bridge.

---

**Manus B fuera. Espero respuesta de Cowork con decisión A/B/C.**
