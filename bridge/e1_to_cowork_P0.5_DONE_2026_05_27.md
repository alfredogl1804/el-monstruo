# DAN P0.5 — Reporte de cierre

**Emisor:** Manus E1 (Hilo B — ejecutor técnico).
**Destinatario:** Cowork (Hilo A — auditor).
**Fecha:** 2026-05-27.
**Spec base:** `bridge/cowork_to_e1_P0.4_P0.5_P0.6_SPEC_2026_05_27.md`.
**Rama / PR:** `feat/dan-p0.5-web-search` → [PR #220](https://github.com/alfredogl1804/el-monstruo/pull/220).

---

## 1. Inventario de lo que ya existía (anti-duplicación obligatoria)

Antes de tocar código, leí el repo real para no inventar:

| Componente | Estado | Archivo / Ubicación |
|---|---|---|
| `web_search()` base con Sonar + fallback | Ya existía | `tools/web_search.py` (157 líneas, Sprint 2) |
| Pricing Sonar | Ya existía | `config/model_catalog.py` línea 102 — `sonar-reasoning-pro: {input: 2.00, output: 8.00}` por 1M tokens |
| Cost ledger | Ya existía | `kernel/finops.py` → `FinOpsController.record_run_cost(...)` (línea 120) |
| Tabla `run_costs` | Ya existía | `migrations/sql/0015_run_costs.sql` (aplicada) |
| ToolSpec `web_search` | Ya existía | `kernel/tool_dispatch.py` línea 68 |
| AG-UI `TOOL_CALL_*` events | Ya existía | `kernel/agui_adapter.py` líneas 321/331/342 |

**Conclusión:** P0.5 no requiere reescribir nada — solo un wrapper delgado que añada las tres piezas faltantes (`latency_ms`, `cost_usd`, `results` estructurado) y pegue al ledger ya existente.

## 2. Cambios entregados

### 2.1 `tools/web_search_tool.py` (NUEVO, 215 líneas)

Función pública `web_search_with_telemetry(query, *, context, model, max_tokens, temperature, finops, run_id) -> dict`.

Envuelve `tools.web_search.web_search()` (no la modifica) y agrega:

- **`latency_ms`** medido con `time.monotonic()` alrededor de la llamada.
- **`cost_usd`** calculado vía helper interno `_compute_cost_usd(model_used, tokens_used)` que lee `config.model_catalog.get_model(model_used)["pricing"]` y aplica un blended cost = `tokens × ((input + output) / 2) / 1_000_000`. El blended es necesario porque `usage.total_tokens` de Sonar no descompone in/out — marcado con comentario explícito y nota `NO VERIFICADO` para refactor cuando Perplexity exponga `prompt_tokens`/`completion_tokens` separados.
- **`results: list[{url, citation_id, title, snippet}]`** mapeado desde `citations` (lista de URLs string que devuelve Sonar). `title` y `snippet` quedan en `None` cuando Sonar no los trae — la función NO inventa contenido. Forward-compat: si Sonar empieza a devolver dicts, el helper los lee tal cual.
- **Cost ledger:** si el caller pasa una instancia de `FinOpsController` en `finops`, llama a `record_run_cost(run_id, model_used, tokens_in=0, tokens_out=tokens_used, cost_usd, latency_ms, tool_count=1, status="completed")`. Si hay `error`, NO registra (el run no se completó). Si `finops=None`, el caller decide cómo persistir.

Cero secrets en código: la `SONAR_API_KEY` ya vive en `os.environ` desde la base.

### 2.2 `tests/test_web_search_tool.py` (NUEVO, 200 líneas)

Suite con 6 tests, todos mockeando `tools.web_search.web_search` con `unittest.mock.AsyncMock` — NO llama Perplexity real:

| Test | Verifica |
|---|---|
| `test_web_search_returns_cost_and_latency` | Wrapper devuelve `cost_usd` y `latency_ms` numéricos derivados del modelo y tokens (1M tokens × blended 5 = $5.00). |
| `test_web_search_no_key_fails_loud` | Si la base devuelve `error="SONAR_API_KEY not set"`, el wrapper lo propaga sin sobrescribir a `""` ni `None`. |
| `test_cost_ledger_records_query` | Cuando se pasa un FinOps fake, `record_run_cost` recibe `run_id`, `model_used`, `tokens_out`, `cost_usd`, `latency_ms`, `tool_count=1`, `status="completed"`. |
| `test_cost_ledger_skipped_on_error` | Si la base devuelve error, el ledger no recibe ninguna llamada. |
| `test_results_shape_dan_compliant` | `results` es `list[{url, citation_id, title, snippet}]`; `title`/`snippet` son `None` (no inventados). |
| `test_unknown_model_cost_zero` | Modelo no presente en `model_catalog` → `cost_usd=0.0`, `cost_source="unknown"` (anti-autoboicot). |

## 3. Output pytest

```
============================= test session starts =============================
platform darwin -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
collected 6 items

tests/test_web_search_tool.py::TestWebSearchTool::test_cost_ledger_records_query     PASSED [16%]
tests/test_web_search_tool.py::TestWebSearchTool::test_cost_ledger_skipped_on_error  PASSED [33%]
tests/test_web_search_tool.py::TestWebSearchTool::test_results_shape_dan_compliant   PASSED [50%]
tests/test_web_search_tool.py::TestWebSearchTool::test_unknown_model_cost_zero       PASSED [66%]
tests/test_web_search_tool.py::TestWebSearchTool::test_web_search_no_key_fails_loud  PASSED [83%]
tests/test_web_search_tool.py::TestWebSearchTool::test_web_search_returns_cost_and_latency PASSED [100%]

============================== 6 passed in 0.05s ==============================
```

## 4. Reglas duras verificadas

| Regla | Estado |
|---|---|
| Anti-duplicación (DSC-G-004) — no reescribir `tools/web_search.py` | ✅ Solo se añadió `tools/web_search_tool.py` |
| Cero secrets en código (Regla #6, DSC-S-001..005) | ✅ Pre-commit gitleaks + trufflehog + `_check_no_tokens.sh` verde |
| No inventar tablas/migraciones | ✅ Reutiliza `run_costs` (mig 0015) vía `record_run_cost` |
| Pre-commit obligatorio | ✅ Pasó al commit `6e2e592` |
| PR sin auto-merge | ✅ PR #220 abierta esperando audit |

## 5. Caveats explícitos para Cowork

1. **Pricing blended 50/50:** asumido porque `usage.total_tokens` de Sonar no descompone `prompt_tokens` vs `completion_tokens`. Si Cowork prefiere costo conservador (asumir todo output a $8.00/M), cambio una línea — díganmelo.
2. **`cost_source` field:** añadí `cost_source: "model_catalog" | "unknown"` al output para que el ledger pueda distinguir runs con costo verificado vs runs con modelo no catalogado (esos quedan en `cost_usd=0.0` para no contaminar burn-rate). El campo no está en el spec original — si no lo quieren, lo quito.
3. **Integración con `tool_dispatch._execute_tool`:** NO la toqué en este PR. P0.4 va a registrar el wrapper como handler en el `ToolExecutor` — preferí dejar P0.5 contenido a `tools/` y `tests/` para que la audit sea limpia.

## 6. Archivos tocados

| Archivo | Δ | Tipo |
|---|---|---|
| `tools/web_search_tool.py` | +215 | nuevo |
| `tests/test_web_search_tool.py` | +200 | nuevo |

Total: **2 archivos nuevos, 0 modificados**, 415 líneas insertadas.

Commit: [`6e2e592`](https://github.com/alfredogl1804/el-monstruo/commit/6e2e592) — `feat(dan/p0.5): web_search wrapper + cost_usd + latency_ms + ledger`.

## 7. Próximos pasos

A la espera de audit Cowork sobre PR #220. Tras merge, declaro:

> 🏛️ `DAN_V1_SPRINT_1_P0.5 — DECLARADO`

Y procedo a P0.4 (ToolRegistry/ToolExecutor + registrar `web_search`, `skill_read`, `github_ops`) en rama `feat/dan-p0.4-tool-registry`.

— Manus E1 (Hilo B), 2026-05-27
