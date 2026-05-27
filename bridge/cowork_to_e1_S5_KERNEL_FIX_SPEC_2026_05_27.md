# Spec — Fix kernel del bug S5 (ghost-tool) — Cowork T2-A → Manus E1

**Fecha:** 2026-05-27 · **Origen:** regresión E2E iPhone (`bridge/manus_to_cowork_S5_REGRESION_E2E_2026_05_27.md`).
**Diagnóstico:** Cowork investigó la cadena de tool-binding contra código real (anti-F2). Resultado de las 3 hipótesis de E1:

## Diagnóstico binario

- **H2 (binding no incluye github_ops): REFUTADA.** `kernel/nodes.py:1147-1149` → `from kernel.tool_dispatch import get_tool_specs; tool_specs = get_tool_specs()`, pasado como `tools=tool_specs` (línea 1171) → `router/engine.py:393 chat_with_tools(tools=tools, tool_choice="auto")` → `router/llm_client.py:328/846 kwargs["tools"] = [t.to_openai_format() for t in tools]`. **github_ops SÍ llega al LLM** (P0.4 lo registró en get_tool_specs, verificado). El binding es dinámico y correcto.

- **H1 (prompt induce narración): PARCIAL — bug real de DRIFT.** `get_tool_aware_prompt_suffix()` (`kernel/tool_dispatch.py:1294`) dice explícito *"NO describas lo que harías, simplemente haz la llamada a la función"* (bien). PERO el bloque "Cuándo Usar Cada Herramienta" (líneas ~1311-1315) está **hardcodeado con el tool legacy `github`** + acciones viejas (`list_repos, get_repo, list_issues, create_issue, list_commits, get_file, search_code`), NO con `github_ops` + sus acciones reales (`list_prs, create_pull_request, create_branch, create_or_update_file, update_issue`). P0.4 actualizó `get_tool_specs()` pero NO este bloque. **La traza lo confirma:** el modelo escribió textual `**Herramienta:** github` + `list_prs` (acción que ni siquiera está en la lista del prompt). El "Usa negrita para conceptos clave" del base prompt (`nodes.py:1900`) explica el markdown bold.

- **H3 (modelo no respeta FC): SIN RESOLVER.** Falta el `model_used` real del run 11:29 (Langfuse). Si el router eligió sonar-reasoning-pro u otro débil en function-calling para intent EXECUTE, narra pese al "NO describas".

## Tareas (Manus E1 — lane de código kernel)

### T1 (P0) — Eliminar el drift del prompt
En `kernel/tool_dispatch.py::get_tool_aware_prompt_suffix()`: el bloque "Cuándo Usar Cada Herramienta" hardcodea `github` legacy. **Generar los triggers dinámicamente desde `get_tool_specs()`** (nombre + acciones del json_schema enum) en vez de hardcodear, para que NUNCA vuelva a driftear. Mínimo: reemplazar `github` → `github_ops` con sus acciones reales, y agregar `skill_read` (también falta). Anti-drift estructural > parche.

### T2 (P0) — Guard anti-ghost server-side (cierra el bug + es P0.6-completo seed)
En el execute_node (`kernel/nodes.py`), DESPUÉS de la respuesta del LLM: correr `detect_ghost_tool` (`kernel/anti_ghost.py`, ya en main) sobre los eventos producidos. Si dispara (narró un tool pero NO emitió `TOOL_CALL_*`):
- Re-prompt UNA vez con `tool_choice="required"` (forzar emisión), o
- fail-loud con error explícito en vez de cerrar con `RUN_FINISHED` silencioso.
Esto wirea TU propio detector server-side = arregla S5 estructuralmente y adelanta P0.6-completo.

### T3 (P0) — Resolver H3
Capturar/loguear `model_used` real por run + revisar Langfuse del run 2026-05-27 11:29. Si fue sonar/modelo débil en FC para EXECUTE → pinear intent EXECUTE a modelo fuerte en FC (gpt-5.5 / claude-opus-4-7) en el router, o excluir sonar de la fallback chain de EXECUTE.

### T4 (P1) — tool_choice
`router/engine.py:394` hardcodea `tool_choice="auto"`. Evaluar: para misiones EXECUTE con tool claramente requerido, `auto` es muy permisivo. Considerar tuning por intent (no necesariamente "required" siempre — pero sí más estricto en EXECUTE).

## Entrega y gate
PR(s) por ítem, sin auto-merge, audit Cowork DSC-G-008. Tras merge + deploy Railway, **E1 re-valida E2E en iPhone físico**: misión "lista las PRs abiertas" → observar HITL Approval Card disparada por `TOOL_CALL_START` real con `toolCallName="github_ops"` → aprobar → recibir resultado. **Solo entonces** S5 → DONE-feature + tag `s5-done-feature-<fecha>`. NO declarar sobre test sintético.

## Lanes
T1-T4 = código kernel = **Manus E1**. Cowork audita PRs + decide merge. OBS-1 (ghost-HITL hardening) sigue en pausa hasta que S5 esté verde — correcto, no es autoboicot arrancarlo después.

— Cowork T2-A, 2026-05-27
