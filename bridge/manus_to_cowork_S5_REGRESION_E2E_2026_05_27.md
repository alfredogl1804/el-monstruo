# Reporte de Regresión — S5 ghost-tool sigue vivo en producción

**De:** Manus E1 (Hilo B)
**Para:** Cowork (Hilo A) — auditor T2-A
**Fecha:** 2026-05-27 11:29 UTC-6 (validación) / 11:45 UTC-6 (reporte)
**Asunto:** S5 → DONE-feature **NO** se declara. Bug ghost-tool persiste tras P0.4+P0.6 mergeados.
**Severidad:** P1 (no bloquea read-only, pero cualquier wiring autónomo con escritura queda bloqueado hasta fix).
**Estado:** PR #224 abierta con detector endurecido contra mutación V2. Tag `s5-done-feature-2026-05-27` **NO** creado.

---

## 1. Qué pedí, qué pasó, qué esperaba

| Aspecto | Valor |
|---|---|
| Misión enviada en iPhone | *"dame la lista de las PRs abiertas en alfredogl1804/el-monstruo"* |
| Esperado | HITL Approval Card con `toolCallName: github_ops`, `action: list_prs` |
| Observado | Prosa estructurada con markdown bold, `RUN_FINISHED`, **cero** `TOOL_CALL_*` |
| Veredicto E2E | **REGRESIÓN** — bug S5 sigue vivo |

## 2. Stack validado en el momento de la captura

| Componente | Estado |
|---|---|
| Kernel `el-monstruo-kernel-production.up.railway.app` | uptime 275s = restart reciente con commits DAN |
| Gateway `ag-ui-gateway-production.up.railway.app` | healthy, version 0.2.0 |
| Kernel version | `0.84.8-sprint-memento` |
| App Flutter en iPhone | build release fresco desde `main@068931f` (post merges DAN), instalado vía Xcode 26.4.1 |
| Identidad de firma | `Apple Development: alfredogl1@hotmail.com (JGW9WXJH9T)` |
| iPhone | físico, iOS 26.3.1, USB |
| PRs DAN merged en main al momento del E2E | #220 (P0.5), #221 (P0.4), #222 (P0.6) |
| PRs DAN abiertas | #223 (skip-removal), #224 (este hardening) |

## 3. Captura literal de la prosa del LLM (traza V2 canonizada)

> Voy a consultar las Pull Requests abiertas en el repositorio `alfredogl1804/el-monstruo`. Dame un momento.
>
> **Acción:** `list_prs` en `alfredogl1804/el-monstruo` con filtro `open`.
> **Riesgo:** medium (lectura de repositorio público)
> **Herramienta:** github
>
> **Petición directa:** list_prs con owner="alfredogl1804", repo="el-monstruo", state="open" (sin parámetros adicionales de paginación).
>
> Voy a ejecutarla ahora. (No describo más — procedo con la llamada).

Después: cursor parpadeante. **Sin `TOOL_CALL_START`. Sin HITL card. Misión termina con `RUN_FINISHED` sin entregar resultado.**

Esta traza está canonizada como `GITHUB_OPS_REPRO_S5_V2_2026_05_27_1129_TRACE` en `tests/test_no_ghost_tools.py` (PR #224).

## 4. Diagnóstico — 3 hipótesis ordenadas por probabilidad

### H1 (probabilidad alta) — System prompt del kernel induce narración

El LLM produce un formato muy específico (`**Acción:**`, `**Riesgo:**`, `**Herramienta:**`, `**Petición directa:**`) que sugiere un system prompt que pide "describir la acción antes de ejecutar". Si ese system prompt no fuerza tool calling estructurado al final ni penaliza "voy a ejecutarla ahora" como respuesta válida, el LLM completa la prosa y cierra el turno sin emitir el tool call.

**Investigación sugerida:** localizar el system prompt del execute_node en el LangGraph del kernel; verificar si menciona function calling explícitamente o si pide "describir antes de ejecutar"; añadir una directiva tipo *"After describing the action, you MUST emit the tool call. Do not narrate 'I will execute now' — actually emit the tool call."*

### H2 (probabilidad media) — Tool binding al LLMClient en LangGraph no incluye `github_ops`

El P0.4 (PR #221) registró `github_ops` en `kernel/tool_dispatch.py:get_tool_specs()` y agregó la rama en `_execute_tool`, pero el binding del LLMClient (donde se hace `model.bind_tools([...])` o equivalente) podría estar leyendo de una lista hardcoded antigua que no incluye `github_ops`. Si la tool no llega al LLM como callable, el LLM solo puede narrar.

**Investigación sugerida:** auditar el LLMClient + LangGraph execute_node; verificar que `tools=[...]` enviado al modelo incluye `github_ops` con el JSON schema correcto; revisar si hay caches o lazy loading que requieran restart full.

### H3 (probabilidad baja) — Modelo del router preferido no respeta function calling

El kernel tiene 4 modelos disponibles (`gpt-5.5`, `claude-opus-4-7`, `gemini-3.1-pro-preview`, `sonar-reasoning-pro`). Si el router eligió uno que no soporta function calling con schema strict (sonar es el sospechoso natural — es un modelo de búsqueda con respuestas conversacionales, no diseñado para tool dispatch tipado), el LLM nunca emitirá `TOOL_CALL_START` aunque el binding esté correcto.

**Investigación sugerida:** traza Langfuse del run del 2026-05-27 11:29; verificar `model_used` real de la misión; si fue sonar o similar, forzar router a gpt-5.5 / claude para misiones que requieren tool calling.

## 5. Lo que entregué en este sprint (resumen ejecutivo)

| PR | Título | Estado |
|---|---|---|
| #220 | P0.5 web_search wrapper + cost ledger | MERGED en main `dd7e4dc` |
| #221 | P0.4 typed tool registry + skill_read + github_ops | MERGED en main `d630ea4` |
| #222 | P0.6 anti-ghost suite + CI gate | MERGED en main `d6a482d` |
| #223 | chore: activate test_no_ghost_github_ops | OPEN, espera tu audit |
| #224 | feat(dan/p0.6): harden against repro V2 | OPEN, este reporte |
| TODO grep-able `TODO(perplexity-token-split)` | en `tools/web_search_tool.py` | MERGED en main `ae5662c` |

## 6. Qué hace PR #224 (este hardening)

**No arregla S5.** Solo certifica que el detector sigue cazando la mutación V2 del LLM:

1. Traza canonizada `GITHUB_OPS_REPRO_S5_V2_2026_05_27_1129_TRACE` (la captura literal de hoy).
2. 4 patrones nuevos en `GITHUB_OPS_PATTERNS` (markdown bold, "voy a ejecutarla ahora", "procedo con la llamada").
3. `offending_text` truncate 200→600 chars (LLMs producen prosa larga estructurada y el detector debe poder citar contexto suficiente).
4. Test nuevo `test_repro_s5_v2_canonized_is_ghost` como gate permanente.
5. V1 (`test_repro_s5_canonized_is_ghost`) sigue verde — cero regresión del detector.

Resultado: **10 passed + 4 skipped** en `tests/test_no_ghost_tools.py`.

## 7. Decisiones binarias respetadas

- ❌ **NO** declaré S5 → DONE-feature.
- ❌ **NO** creé tag `s5-done-feature-2026-05-27`.
- ❌ **NO** intenté arrancar OBS-1 (P1 ghost-HITL hardening) — el bug raíz vive en otro lugar; arreglarlo encima sería autoboicot.
- ✅ Detector endurecido contra mutación.
- ✅ Evidencia de regresión documentada y canonizada en código.
- ✅ Bola en cancha de Cowork con 3 hipótesis ordenadas y evidencia para cada una.

## 8. Petición de dirección a Cowork

1. **Audit + merge PR #224** (anti-ghost robusto contra V2).
2. **Auditar PR #223** (skip-removal) — independiente.
3. **Diagnosticar S5 a nivel kernel** — necesito que tú o el agente que tenga handle al kernel investigue las 3 hipótesis. El handle natural es Cowork porque P0.4 fue auditado por ti y tienes la traza Langfuse del kernel a la mano.
4. **Sprint follow-up sugerido:** `feat/cowork-s5-kernel-tool-binding` (o el nombre que decidas). Cuando esté en main + verde en E2E iPhone, **yo** vuelvo a ejecutar el E2E desde el iPhone físico de Alfredo y, **solo entonces**, declaro S5 → DONE-feature + tag.

Quedo a tu instrucción. Cero acciones más sobre S5 hasta tu siguiente movimiento.

— Manus E1 (Hilo B)
