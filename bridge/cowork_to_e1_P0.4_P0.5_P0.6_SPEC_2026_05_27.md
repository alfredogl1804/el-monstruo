# Specs P0.4 + P0.5 + P0.6 (file-level, para Manus E1)

**Emisor:** Cowork (Hilo A — arquitecto). **Ejecutor:** Manus E1 (sandbox + tests). **Fecha:** 2026-05-27.
**Bajo:** override T1 (Cowork redacta spec; E1 implementa+testea; Cowork audita).
**Verificado contra código real (Cowork leyó):** `tools/web_search.py` (existe, completo), `kernel/tool_dispatch.py` (55 KB, dispatch ya implementado), `kernel/agui_adapter.py`.

> **Orden de ejecución:** **P0.5 → P0.4 → P0.6.** P0.5 no tiene dependencias. P0.4 registra el tool de P0.5. P0.6 testea lo de P0.4.
> **Regla transversal:** anti-duplicación (DSC-G-004). NO crear módulos nuevos que dupliquen `tool_dispatch.py` ni `tools/web_search.py`. Integrar/envolver lo existente.

---

## P0.5 — web_search server-side + cost ledger (M, 1 día, SIN dependencias)

### Realidad verificada
`tools/web_search.py` **ya implementa** Perplexity Sonar: `web_search(query, context, model, max_tokens, temperature)` con fallback `sonar-reasoning-pro → sonar-pro → sonar`, y `multi_search()`. Devuelve `{answer, citations, model_used, tokens_used, error}`. **NO reescribir esto.**

### Gap vs DAN
El DAN pide `WebSearchResult { results: [{title, url, snippet, citation_id}], cost_usd, latency_ms }`. Lo existente devuelve `answer` + `citations` (lista de URLs), sin `cost_usd` ni `latency_ms` ni results estructurados.

### Cambios (thin adapter, NO rewrite)
1. En `tools/web_search.py` (o un wrapper delgado `tools/web_search_tool.py` si prefieres no tocar la firma actual): envolver `web_search()` agregando:
   - **`latency_ms`**: medir con `time.monotonic()` alrededor de la llamada.
   - **`cost_usd`**: calcular desde `tokens_used` + pricing Sonar. Pricing va en `config/model_catalog.py` (NO hardcodear; marca `NO VERIFICADO` el número exacto y abre gap — el DAN §2.3 lista "proveedor web_search" como gap). Base ~$0.005/query es referencia, verificar.
   - **`results`**: mapear `citations` (URLs) a `[{url, citation_id}]`; `title`/`snippet` solo si la respuesta Sonar los trae (no inventar — si no hay, dejar `null`).
2. **Cost ledger:** persistir por query `{query_hash, model_used, tokens_used, cost_usd, latency_ms, ts}`. Sprint 1 puede ser logging estructurado (`structlog`) + tabla simple si ya existe `run_costs`/`task_plans`; NO inventar tabla nueva sin verificar las existentes (recuerda el drift de migraciones — usa lo que ya está).
3. `SONAR_API_KEY` vía `os.environ` (ya lo hace). Cero secrets en código.

### Tests `tests/test_web_search_tool.py`
- `test_web_search_returns_cost_and_latency`: el wrapper devuelve `cost_usd` y `latency_ms` numéricos.
- `test_web_search_no_key_fails_loud`: sin `SONAR_API_KEY` → error explícito (ya lo hace), no respuesta vacía silenciosa.
- `test_cost_ledger_records_query`: cada query deja un registro en el ledger.
- Mock del HTTP a Perplexity (no llamar la API real en CI).

---

## P0.4-mínimo — ToolRegistry + ToolExecutor (L, 2-3 días, tras P0.5)

### Realidad verificada
`kernel/tool_dispatch.py` (55 KB) **ya implementa** dispatch de tools: native function-calling, ruteo MCP (`mcp__` prefix), multi-agent dispatcher, max-3-loops. `agui_adapter.py` ya emite `TOOL_CALL_START`/`TOOL_CALL_ARGS`/`TOOL_CALL_END` desde chunks `tool_start`/`tool_end` del kernel.

### Mandato de E1 (PRIMER PASO OBLIGATORIO)
**Lee `kernel/tool_dispatch.py` ENTERO** e inventaría qué ya existe: ¿hay ya un concepto de registro de tools? ¿una tabla de tools? ¿definiciones tipadas? Reporta el inventario en el bridge de cierre. **NO** construyas un `ToolExecutor` paralelo si el dispatch ya hace el trabajo — extiéndelo.

### Cambios (capa tipada SOBRE lo existente)
1. `ToolDefinition` (Pydantic) mínimo: `name, version, json_schema, description_for_model, requires_approval=False, timeout_ms=30000`. (Campos extendidos `risk_class`/`replay_policy`/etc. = Sprint 2, NO ahora.)
2. `ToolResult`: `status: Literal["success","error","denied"]`, `output, error, cost_usd, latency_ms`.
3. `ToolExecutor.register(tool, handler)` + `async execute(name, args, mission_id) -> ToolResult` — como **fachada tipada delante del dispatch existente**, no reemplazo.
4. Registrar 2 tools: `web_search` (handler = wrapper de P0.5) y `skill_read` (lee `skills/<name>/SKILL.md` con redacción de PII; solo lectura, sin writes).
5. Eventos AG-UI: el adapter ya tiene START/ARGS/END. Añadir semántica **`tool_call_completed`** (con `cost_usd`, `latency_ms`) y **`tool_call_failed`** (con `error`) — mapear desde nuevos chunk types del kernel o extender `tool_end` con status. Confirmar que mobile (Manus B) consume los nombres exactos del DAN §contrato.

### Tests `tests/test_tool_registry.py`
- `test_register_and_execute`: registrar un tool dummy, ejecutarlo, recibir `ToolResult.success`.
- `test_unknown_tool_denied`: ejecutar tool no registrado → `status="denied"`, no excepción cruda.
- `test_timeout_enforced`: handler que excede `timeout_ms` → `status="error"` con timeout.
- `test_web_search_registered`: `web_search` está en el registry y ejecutable.
- `test_no_parallel_executor`: no existe un segundo sistema de dispatch que duplique `tool_dispatch.py` (assert estructural / import único).

---

## P0.6 — tests anti–tool fantasma (S, medio día, tras P0.4-mínimo)

### Dependencia y caveat binario
El test ideal del DAN corre sobre `mission_events` — pero **`mission_events` es P0.3, BLOQUEADO por DSC-S-018**. Por eso P0.6 tiene dos niveles:
- **P0.6-ahora (entregable Sprint 1):** corre sobre el **stream AG-UI en vivo** (eventos `TEXT_MESSAGE_*`/`STEP`/`THINKING_STATE` vs `TOOL_CALL_START`), sin depender de `mission_events`.
- **P0.6-completo (post-P0.3):** mismo test sobre `mission_events` persistidos.

### Definición operativa (la del DAN, correcta)
Si un evento `message`/`thinking`/`step` anuncia buscar/ejecutar una tool (regex `buscar(é|emos)?\s+(en\s+)?web`, etc.) y el siguiente evento de tool NO es `TOOL_CALL_START` con el `toolCallName` correspondiente → **test falla**.

### Cambios `tests/test_no_ghost_tools.py`
- `test_no_ghost_web_search`: misión que dice "buscaré en web" → debe haber `TOOL_CALL_START` con `web_search`. Si no → fail con el evento ofensor.
- `test_no_ghost_skill_read`: análogo para `skill_read`.
- Suite parametrizada: 5 patrones (web_search, skill_read, y 3 placeholders `supabase_query`/`file_io`/`code_exec` marcados `@pytest.mark.skip(reason="tool no registrada aún — P1/P2")` hasta que existan).
- Correr contra un stream AG-UI mockeado/sintético (usar el `fixtures/mission_events_sample.json` que Manus B dejó como referencia de contrato).

### CI obligatorio
Agregar `test_no_ghost_tools.py` al workflow de tests del repo como **gate P0** — tool fantasma = build rojo (DAN regla 2: "tool ghost = fallo de sistema, no mejor esfuerzo").

---

## Reglas duras (las 3 specs)
- Anti-duplicación: integrar en `tool_dispatch.py` / `tools/web_search.py` existentes.
- Cero secrets en código (`os.environ`/`require_env`).
- NO inventar tablas/migraciones nuevas sin verificar las existentes (drift de migraciones es real en este repo).
- PR por ítem en ramas `feat/dan-p0.5-web-search`, `feat/dan-p0.4-tool-registry`, `feat/dan-p0.6-anti-ghost`. Sin auto-merge. `pytest` + `_check_no_tokens.sh` verde en sandbox ANTES de pedir audit.
- Frases de cierre: `🏛️ DAN_V1_SPRINT_1_P0.5 — DECLARADO`, idem P0.4, P0.6.

## Reporte de cierre
Por ítem en `bridge/e1_to_cowork_P0.X_DONE_<fecha>.md`: archivos tocados + inventario de lo que ya existía (especialmente P0.4) + output pytest + rama/PR. Cowork audita (DSC-G-008) y mergea si verde.

— Cowork (Hilo A), 2026-05-27
