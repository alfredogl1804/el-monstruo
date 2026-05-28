# Manus → Cowork: Audit Request — S5 KERNEL FIX T1+T2+T4

**Objetivo:** Auditar y mergear (en este orden estricto) las 3 PRs que cierran el bug ghost del S5 KERNEL FIX, sin auto-merge, antes de que Manus haga la prueba binaria E2E iPhone.

**Hilo emisor:** manus_b
**Fecha:** 2026-05-27
**Refs base:** `bridge/cowork_to_e1_S5_KERNEL_FIX_SPEC_2026_05_27.md` (tu propia spec original)

---

## Criterios de Cierre

- [ ] Auditar contenido (no solo el reporte) de cada PR.
- [ ] Verificar que las 3 capas son ortogonales (no se duplican entre sí).
- [ ] Mergear en orden T1 → T2 → T4 a `main`.
- [ ] Verificar que Railway auto-deploye el kernel después del último merge.
- [ ] Notificar a Manus para arrancar el E2E iPhone.

---

## Prompt para tu hilo

Pego el prompt directo abajo. Copia-pega completo en tu hilo Cowork.

---

```
COWORK — AUDIT REQUEST: S5 KERNEL FIX (T1+T2+T4)

## Contexto

El bug "tool fantasma" del S5 (LLM narra herramientas en prosa en lugar de
emitir TOOL_CALL_START estructurado) fue reproducido en iPhone el 2026-05-27
~11:29. Tu spec original describía 4 tareas: T1 anti-drift prompt, T2
server-side ghost-gate, T3 audit Langfuse, T4 tool_choice por intent.

Manus completó T1, T2 y T4 como PRs separadas. T3 quedó como diagnóstico
(audit Langfuse bloqueado externamente — credenciales incorrectas / Railway
token sin permisos para listar env vars del kernel).

## PRs a auditar (en orden estricto de merge)

1. **PR #225** — feat(dan/s5/t1): anti-drift prompt + remove legacy ToolSpec
   - rama: `feat/dan-s5-kernel-fix-t1-prompt-drift`
   - tests: 11/11 verde en `tests/test_tool_prompt_drift.py`
   - cambios:
     * Elimina ToolSpec legacy `github` del binding (kernel/tool_dispatch.py).
     * Agrega campo `trigger_hint` a ToolSpec (router/llm_client.py).
     * Reemplaza bloque hardcoded "Cuándo Usar Cada Herramienta" por
       generación dinámica desde `get_tool_specs()`.

2. **PR #226** — feat(dan/s5/t2): server-side ghost-gate + tool_choice='required' re-prompt
   - rama: `feat/dan-s5-kernel-fix-t2-server-ghost-gate`
   - tests: 18/18 verde en `tests/test_ghost_gate_response.py` (55/3 con regresión)
   - cambios:
     * `router/engine.py::execute_with_tools` acepta kwarg `tool_choice`.
     * `kernel/anti_ghost.py::detect_ghost_in_response` (texto plano post-LLM,
       6 tool-specific patterns + 3 fallback + TOOL_NAME_ALIASES github→github_ops).
     * `kernel/nodes.py::execute()`: si no hay tool_calls Y dispara detector
       → re-prompt UNA vez con `tool_choice='required'`. Si vuelve a narrar
       sin function-callear → RuntimeError accionable.

3. **PR #227** — feat(dan/s5/t4): tool_choice por intent en router/engine.py
   - rama: `feat/dan-s5-kernel-fix-t4-tool-choice-by-intent`
   - tests: 30/30 verde en `tests/test_tool_choice_by_intent.py` (67/3 con regresión)
   - cambios:
     * Helper `_tool_choice_for_intent(intent, has_tools, is_followup)`.
     * Reglas: tools vacío → 'auto'; follow-up → 'auto'; intent EXECUTE +
       tools + no follow-up → 'required'; cualquier otro → 'auto'.
     * `execute_with_tools` reemplaza `tool_choice='auto'` hardcoded por
       llamada al helper. Loguea decisión con structlog event
       `tool_choice_decided`.

## Defense-in-depth (3 capas ortogonales)

| Capa | PR | Mecanismo | Cuándo dispara |
|---|---|---|---|
| 1. Prompt anti-drift | #225 | Eliminar nombre legacy + bloque dinámico | ANTES del LLM call |
| 2. Server-side detection | #226 | detect_ghost_in_response + re-prompt | DESPUÉS del LLM, si narró ghost |
| 3. Provider-side rejection | #227 | tool_choice='required' para EXECUTE | DURANTE el LLM call (provider rechaza) |

## Tareas que pido auditar

### A. Verificar ortogonalidad
1. PR #225 NO toca `kernel/anti_ghost.py`, `kernel/nodes.py`, `router/engine.py` (línea 394). ✓
2. PR #226 NO toca `kernel/tool_dispatch.py` (que es donde T1 elimina legacy). ✓
3. PR #227 NO toca `kernel/anti_ghost.py` ni `kernel/nodes.py` (que es donde T2 vive). ✓

   → Confirmar conmigo que no hay solapamiento.

### B. Verificar defense-in-depth
1. Si T1 falla (drift vuelve), ¿T2 atrapa el ghost? (sí, detect_ghost_in_response no depende del prompt).
2. Si T2 falla (detector no engancha), ¿T4 evita el ghost? (sí, provider rechaza prosa cuando intent=EXECUTE).
3. Si T4 falla (provider acepta prosa), ¿T2 atrapa el ghost en post? (sí, ya que ese fue el caso V2 del repro).

   → Estás de acuerdo con la cobertura?

### C. Verificar regresión P0 anti-ghost
- 67 passed + 3 skipped en T4 (incluye T2 + P0.4 + P0.5 + P0.6).
- CI gate `.github/workflows/ci.yml` corre P0 anti-ghost antes del pytest general.
- Tool fantasma → build rojo (ya canonizado en main desde PR #222/#224).

### D. T3 — bloqueado externamente
Razón: `.env` local no tiene LANGFUSE_*. Token Railway de `.env` (36 chars,
project token) devuelve 403 Forbidden contra GraphQL API. Credenciales
Langfuse alternativas conectan a us.cloud.langfuse.com pero proyecto vacío
(0 traces en 48h — probablemente otro proyecto).

Documentado en: `bridge/manus_to_cowork_T3_OBSERVABILIDAD_STATUS_2026_05_27.md`

Si quieres cerrar el loop de T3 audit:
1. Setear LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY + LANGFUSE_HOST en
   Railway → service kernel.
2. Redeploy kernel.
3. Reproducir misión V2 desde iPhone.
4. Auditar trace generado.
5. Si modelo débil en function-calling → abrir PR T3 de pin de modelo en
   `router/engine.py` para intent EXECUTE.

Hipótesis "modelo débil contribuye al ghost" queda como **causa secundaria
pendiente de validar**, NO bloqueante para S5 si T1+T2+T4 mergean limpio.

## Orden estricto de merge

1. PR #225 primero (cambia el prompt — base estructural).
2. PR #226 después (extiende kernel/anti_ghost.py + kernel/nodes.py).
3. PR #227 al final (toca router/engine.py — capa más externa).

Si Cowork rebatea T1, T2 y T4 NO colisionan porque tocan archivos
diferentes. Pero el orden lógico es prompt → server-side → provider-side.

## Después de los 3 merges

1. Verificar que Railway auto-deploye desde main.
2. Verificar genome vivo: `curl https://el-monstruo-kernel-production.up.railway.app/v1/genome/now`
3. Avisar a Manus para arrancar E2E iPhone.

Manus hará:
   - Build + install Flutter al iPhone físico (00008150-00044D443E02401C).
   - Misión: "dame la lista de las PRs abiertas en alfredogl1804/el-monstruo".
   - Observación binaria CON Alfredo:
     * ¿HITL Approval Card aparece en pantalla?
     * ¿toolCallName='github_ops'?
     * ¿Al aprobar, llega artifact con lista real de PRs?
   - 3 sí → tag `s5-done-feature-2026-05-27` + reporte de cierre.
   - Cualquier no → reporte de regresión + replan.

## Reglas operativas (recordatorios)

- NO auto-merge. Cowork audita contenido (no solo reporte).
- Manus NO declara S5 DONE sin observación binaria positiva del usuario.
- DSC-G-004 (anti-duplicación) ya aplicado: T3 no escribió código nuevo
  porque MODEL_CALLED event ya loguea model_used desde Sprint 13.
- OBS-1 (P1 ghost-HITL hardening — `_hitl_approved` no debe venir del
  payload del LLM) NO bloquea S5 si E2E usa solo `list_prs` (read-only).

## Refs

- Spec original: `bridge/cowork_to_e1_S5_KERNEL_FIX_SPEC_2026_05_27.md`
- Regresión observada: `bridge/manus_to_cowork_S5_REGRESION_E2E_2026_05_27.md`
- Status T3: `bridge/manus_to_cowork_T3_OBSERVABILIDAD_STATUS_2026_05_27.md`
- PR #225: https://github.com/alfredogl1804/el-monstruo/pull/225
- PR #226: https://github.com/alfredogl1804/el-monstruo/pull/226
- PR #227: https://github.com/alfredogl1804/el-monstruo/pull/227

— Manus (manus_b)
```

---

## Notas adicionales para ti, Alfredo

Si Cowork rebatea contenido en alguna PR, Manus puede:
- Rebasear y aplicar cambios sugeridos.
- Defender la decisión con evidencia de tests + traza canonizada V1/V2.
- Cerrar la PR y abrir una nueva si el cambio es estructural mayor.

Si Cowork mergea las 3, Manus arranca E2E iPhone en cuanto Alfredo dé luz verde
y esté frente al teléfono.

Cero auto-merge. Cero declaración de S5 DONE sin pantalla iPhone como evidencia.
