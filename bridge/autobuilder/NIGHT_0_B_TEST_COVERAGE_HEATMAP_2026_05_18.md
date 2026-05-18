# Night 0 Complex Shadow Run — Carril B: Test Coverage Heatmap

**Fecha:** 2026-05-18
**Oportunidad:** OPP-NB-018
**Risk Class:** R0
**Carril:** B de 4
**Artifact type:** Reporte (read-only, cero side effects)
**base_sha (main):** `bed77d9acb832ce0e735b104e2ae60ba50079457`
**base_sha (atlas branch):** `5f880054278942dd7f9f97036a109ae1679e57d4`

---

## Metodología

Heatmap generado por grep estático (NO ejecución de pytest --cov). Se contabilizó cuántos archivos de test referencian cada módulo/archivo kernel. Esto mide **intención de cobertura**, no cobertura de líneas real.

---

## files_read

| Archivo | Fuente |
|---|---|
| `tests/test_*.py` (listado completo, 112 archivos) | origin/main |
| `kernel/` (40 subdirectorios + 72 archivos top-level .py) | origin/main |

---

## commands_or_searches_run

1. `find tests/ -name "test_*.py" -o -name "*_test.py" | sort`
2. `find kernel/ -maxdepth 1 -type d | sort`
3. `grep -rl "$mod" tests/ | wc -l` (por cada módulo/archivo)
4. `find kernel/$mod -name "*.py" -exec cat {} + | wc -l` (LOC por módulo)
5. `wc -l < kernel/${file}.py` (LOC por archivo top-level sin test)

---

## Heatmap: Subdirectorios kernel/ (por test file references)

| Módulo | LOC | Test files referencing | Cobertura relativa | Riesgo |
|---|---|---|---|---|
| `kernel/catastro/` | 9,186 | 40 | 🟢 ALTA | — |
| `kernel/embriones/` | 5,650 | 25 | 🟢 MEDIA-ALTA | — |
| `kernel/e2e/` | 4,230 | 62 | 🟢 ALTA | — |
| `kernel/cowork_runtime/` | 3,666 | 24 | 🟢 ALTA | — |
| `kernel/transversales/` | 2,423 | 22 | 🟢 MEDIA-ALTA | — |
| `kernel/anti_dory/` | 1,628 | 23 | 🟢 ALTA | — |
| `kernel/runner/` | 1,449 | 14 | 🟡 MEDIA | — |
| `kernel/memento/` | 1,349 | 30 | 🟢 ALTA | — |
| `kernel/brand/` | 821 | 38 | 🟢 ALTA | — |
| `kernel/moc/` | 689 | 129 | 🟢 SATURADA | — |
| `kernel/alerts/` | 520 | 6 | 🟡 MEDIA | — |
| `kernel/browser/` | 441 | 14 | 🟢 ALTA | — |
| **`kernel/a2ui/`** | **228** | **0** | **🔴 CERO** | **P1** |
| **`kernel/embrion_specializations/`** | (no medido) | **0** | **🔴 CERO** | **P2** |
| **`kernel/milestones/`** | (no medido) | **0** | **🔴 CERO** | **P2** |

---

## Heatmap: Archivos top-level kernel/*.py SIN TESTS (0 test file references)

| Archivo | LOC | Función inferida | Riesgo |
|---|---|---|---|
| `causal_seeder.py` | 725 | Siembra causal para simulador | P1 — LOC alto sin cobertura |
| `prediction_validator.py` | 676 | Validación de predicciones | P1 — LOC alto sin cobertura |
| `mcp_client.py` | 538 | Cliente MCP | P1 — LOC alto sin cobertura |
| `usage_tracker.py` | 525 | Tracking de uso/costos | P1 — LOC alto sin cobertura |
| `openai_adapter.py` | 482 | Adaptador OpenAI | P1 — LOC alto sin cobertura |
| `agui_adapter.py` | 440 | Adaptador AG-UI | P2 |
| `sovereign_llm.py` | 362 | LLM soberano | P2 |
| `causal_decomposer.py` | 360 | Descomposición causal | P2 |
| `deployments_routes.py` | 333 | Rutas de deployments | P2 |
| `a2a_registry.py` | 316 | Registro A2A | P2 |
| `memory_routes.py` | 288 | Rutas de memoria | P2 — **Carril D target** |
| `rate_limiter.py` | 262 | Rate limiting | P2 |
| `spec_driven.py` | 241 | Motor spec-driven | P3 |
| `autonomy_routes.py` | 233 | Rutas de autonomía | P3 |
| `seeds_sprint_84_7.py` | 230 | Seeds legacy | P3 |
| `mission_routes.py` | 229 | Rutas de misiones | P3 |
| `usage_routes.py` | 225 | Rutas de uso | P3 |
| `tool_registry.py` | 208 | Registro de tools | P3 |
| `mcp_hub_config.py` | 199 | Config MCP hub | P3 |
| `reranker.py` | 190 | Re-ranking | P3 |
| `seeds_sprint_84_5.py` | 182 | Seeds legacy | P3 |
| `magna_routes.py` | 167 | Rutas magna | P3 |
| `a2a_routes.py` | 164 | Rutas A2A | P3 |
| `output_sanitizer.py` | 152 | Sanitización output | P3 |
| `moc_routes.py` | 139 | Rutas MOC | P3 |

---

## Métricas consolidadas

| Métrica | Valor |
|---|---|
| Total archivos test | 112 |
| Total subdirectorios kernel/ | 40 |
| Total archivos top-level kernel/*.py | 72 |
| Subdirectorios con 0 test references | **3** (a2ui, embrion_specializations, milestones) |
| Archivos top-level con 0 test references | **25** |
| LOC total sin cobertura (top-level, >200 LOC) | **~7,900** |
| LOC total sin cobertura (top 5 P1) | **~2,946** |
| Ratio test files / kernel modules | 112 / 112 = ~1:1 |

---

## Hallazgos clave

1. **El kernel tiene 7,900+ LOC en archivos top-level sin ningún test.** Esto es ~15% del kernel total estimado (~50K LOC).

2. **Los 5 archivos P1 más riesgosos** (causal_seeder, prediction_validator, mcp_client, usage_tracker, openai_adapter) suman 2,946 LOC sin cobertura y son componentes críticos de runtime.

3. **`memory_routes.py` (288 LOC, 0 tests)** es exactamente el target del Carril D de este Shadow Run.

4. **Sobre-testing en `kernel/moc/`** — 129 test file references para 689 LOC. Ratio 5.3:1 (posible duplicación de tests legacy).

5. **3 subdirectorios completos sin tests:** `a2ui/` (228 LOC), `embrion_specializations/`, `milestones/`. Estos son módulos enteros sin validación.

---

## Qué NO inferir

- **NO inferir que 0 test references = 0 cobertura real.** Algunos archivos pueden estar cubiertos indirectamente por tests de integración que importan el módulo sin nombrarlo explícitamente.
- **NO inferir que los archivos legacy (seeds_sprint_*) necesitan tests.** Pueden ser código muerto pendiente de cleanup.
- **NO inferir que el ratio 1:1 es bueno o malo.** Sin `pytest --cov` real, no se puede medir cobertura de líneas.

---

## stop_reason

```
SCAN_COMPLETE — grep estático agotado. Para cobertura real se requiere pytest --cov (fuera de scope Night 0 R0).
```

---

## cost_estimate

| Recurso | Consumo |
|---|---|
| Tool calls | ~5 (find, grep, wc) |
| LLM tokens | ~3000 output |
| API calls externas | 0 |
| DB queries | 0 |
| Side effects | 0 |

---

## Confirmación de cero side effects

- ✅ Cero archivos escritos en el repo
- ✅ Cero branches creadas
- ✅ Cero PRs abiertos
- ✅ Cero tests ejecutados
- ✅ Cero queries a Supabase
- ✅ Cero secrets accedidos
- ✅ Cero deploys
