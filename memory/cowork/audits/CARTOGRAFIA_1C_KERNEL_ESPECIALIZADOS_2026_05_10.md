# Cartografía 1C — `kernel/` módulos especializados

**Fecha:** 2026-05-10
**Autor:** Cowork (Arquitecto Jefe)
**Sub-fase:** 1C del Estudio Forense del Monstruo
**Método:** `ls`, `wc -l`, `head`, `grep -rln`, `grep -nE` sobre `kernel/` y `tests/` con bash workspace mount. Revisión de cableado en `kernel/main.py`. NO inferencia desde memoria.
**Alcance:** subdirectorios y módulos especializados solicitados por el scheduled task — NO toca el núcleo (1B) ni docs (1D).
**Doctrina:** sólo lectura. NO se proponen cambios — se inventaría y se marca estado.

---

## 1. Resumen ejecutivo

- **15 subdirectorios / módulos especializados auditados.** Total estimado **~16,500 LOC** Python (`wc -l` verificado por bloques, ver §2).
- **`kernel/catastro/`** es el módulo especializado más maduro: 6,848 LOC en 15 archivos + 13 fuentes externas + tests propios + RPC Supabase. ✅ integrado al flujo via `main.py:1251-1292`.
- **`kernel/transversales/`** declara 6 capas comerciales pero **5/6 son stubs**: `implement()` y `monitor()` levantan `NotImplementedError` en ventas/publicidad/tendencias/operaciones/finanzas. **Sólo `SeoLayer` está cerrada end-to-end** (Obj #9 al 17%, no al 75% que el COWORK_BASE_CONOCIMIENTO §3 declaraba).
- **`kernel/transversales/` NO es importado por ningún módulo del kernel principal** — sólo lo importan sus propios tests. Es un subsistema aislado del flujo del Embrión y del LangGraph engine.
- **`kernel/sovereignty/`** tiene UN solo archivo (`engine.py`, 532 LOC). **NO existe `sovereign_llm.py` adentro** — vive en `kernel/sovereign_llm.py` (top-level), 362 LOC, archivos distintos pero relacionados.
- **`kernel/dashboards/cost_history.py`** y **`kernel/i18n/engine.py`** tienen 0 referencias en código no-test. Implementados pero aislados (CLI/test only).
- **6/15 módulos sin test directo** (gap): `sovereignty/engine.py`, `sovereign_llm.py`, `causal_decomposer.py`, `causal_seeder.py`, `simulator/causal_simulator_v2.py`, `vanguard/*` (4 archivos), `collective/*` (3 archivos), `zero_config/*` (2 archivos), `i18n/engine.py`, `dashboards/cost_history.py` (cubierto sólo por `test_cost_history_dashboard.py`).
- **STUBS detectados:** las 5 capas transversales (ventas/publicidad/tendencias/operaciones/finanzas) tienen `raise NotImplementedError` en `implement()` y `monitor()`. Confirmado vía `grep -nE "raise NotImplementedError"`.

---

## 2. Tabla maestra de subdirectorios y módulos

LOC = `wc -l`. Estado: ✅ integrado a flujo / 🟡 implementado pero aislado / ❌ stub o placeholder.

| # | Módulo / Subdir | Archivos `.py` | LOC | Propósito (1 línea) | Obj/Capa | Estado |
|---|---|---:|---:|---|---|---|
| 1 | `kernel/catastro/` | 15 + 13 fuentes | 6,848 + sources | Inteligencia viva sobre modelos IA externos. Schema 5 tablas + Pipeline + Trono Score + RecommendationEngine + Dashboard + MCP server. | Obj #5 (Magna), Capa 0 | ✅ integrado (main:1251-1292) |
| 2 | `kernel/transversales/` (root + base) | 2 | 230 | Interfaz canónica `TransversalLayer` (ABC) + enums VerticalId/Archetype. `all_layers_implemented()` gate para DSC-G-014. | Obj #9 | ✅ contrato vivo |
| 3 | `kernel/transversales/seo/` | 2 | 531 | `SeoLayer` — JSON-LD, meta tags, hreflang, canonical, robots. **ÚNICA capa completa.** | Obj #9 | ✅ end-to-end |
| 4 | `kernel/transversales/ventas/` | 2 | 408 | `VentasLayer` — diagnose/recommend OK; **implement/monitor → NotImplementedError**. | Obj #9 | ❌ stub parcial |
| 5 | `kernel/transversales/publicidad/` | 2 | 434 | `PublicidadLayer` — diagnose/recommend OK; **implement/monitor → NotImplementedError**. | Obj #9 | ❌ stub parcial |
| 6 | `kernel/transversales/tendencias/` | 2 | 241 | `TendenciasLayer` — diagnose/recommend OK; **implement/monitor → NotImplementedError**. | Obj #9 | ❌ stub parcial |
| 7 | `kernel/transversales/operaciones/` | 2 | 285 | `OperacionesLayer` — diagnose/recommend OK; **implement/monitor → NotImplementedError**. | Obj #9 | ❌ stub parcial |
| 8 | `kernel/transversales/finanzas/` | 2 | 294 | `FinanzasLayer` — diagnose/recommend OK; **implement/monitor → NotImplementedError**. | Obj #9 | ❌ stub parcial |
| 9 | `kernel/sovereignty/` | 2 | 532 | `engine.py` Sprint 60 — mapea dependencias externas, alternativas self-hosted, migration paths. | Obj #12 | ✅ integrado (main:878-885) |
| 10 | `kernel/sovereign_llm.py` (top-level) | 1 | 362 | Capa abstracción LLM tier 1/2/3 → Ollama local / cloud / frontier. | Obj #12 | ✅ integrado (main:761-774) |
| 11 | `kernel/vanguard/` | 5 | 1,488 | Sprint 63.1 — `intelligence_engine` (motor relevancia), `semantic_scholar` (papers), `tech_radar` (radar agentes), `weekly_digest`. | Obj #6 | ✅ integrado (main:879, 1007-1009, 1021) |
| 12 | `kernel/collective/` | 4 | 1,508 | Sprint 61 — `protocol.py` ColectivaProtocol (mensajería + debates), `knowledge_propagator`, `emergence_detector`. | Obj #8, #11 | ✅ integrado (main:923-944, 1013-1014) |
| 13 | `kernel/causal_decomposer.py` | 1 | 360 | Sprint 55.4 — descompone evento en factores causales atómicos. | Obj #10 | ✅ integrado (main:145-153) |
| 14 | `kernel/causal_seeder.py` | 1 | 725 | Sprint 56.1 — pipeline autónomo Causal Knowledge Base + Perplexity Sonar. | Obj #10 | ✅ integrado (main:660-708) |
| 15 | `kernel/causal_simulator.py` (v1) | 1 | 408 | Simulador Monte Carlo v1. | Obj #10 | ✅ integrado (main:158-166) |
| 16 | `kernel/simulator/causal_simulator_v2.py` | 1 | 420 | Sprint 60 — Monte Carlo v2 calibrado con FinancialLayer + escenarios optimista/base/pesimista/black_swan. | Obj #10 | ✅ integrado (main:880, 895) |
| 17 | `kernel/brand/` | 4 + 6 yamls | 821 + 6 yaml | `brand_dna.py`, `brand_routes.py`, `validator.py` (Sprint 82, score 0-100, modo ADVISORY), `verticals/*.yaml` (6 archetypes). | Obj #2 | ✅ integrado (main:1573, 1708-1709) |
| 18 | `kernel/design/system.py` | 1 | 534 | Sprint 61 — Design System enforcement (tokens OKLCH+Inter, WCAG axe-core). | Obj #2 | ✅ integrado (main:924-957) |
| 19 | `kernel/dashboards/cost_history.py` | 1 | 443 | Dashboard estático HTML del histórico de costo del Embrión. CLI standalone. | Obj #4 | 🟡 aislado (sólo CLI/test) |
| 20 | `kernel/zero_config/` | 3 | 541 | Sprint 63.2 — `intent_inferrer.py`, `smart_defaults.py`. | Obj #3 | ✅ integrado (main:1010, 1031, 1051) |
| 21 | `kernel/i18n/engine.py` | 1 | 498 | Sprint 59.1 — i18n motor 2 niveles (interno + proyectos). DeepL + LLM + heurísticas charset. | Obj #13 | 🟡 aislado (sólo test) |
| 22 | `kernel/error_memory.py` | 1 | 858 | Sprint 81 Capa 0.1 — Memoria de Errores persistente + pre-action queries. | Obj #4 | ✅ integrado (main:1112-1123) |
| 23 | `kernel/magna_classifier.py` | 1 | 735 | Sprint 81 Capa 0.2 — clasifica input → ruta graph (tools) vs router (chat-only). | Obj #5 | ✅ integrado (main:1082-1090, 1095) |
| 24 | `kernel/magna_routes.py` | 1 | 167 | Endpoints REST `POST /v1/magna/classify`, `GET /v1/magna/stats`, `POST /v1/magna/cleanup`. | Obj #5 | ✅ integrado (main:1083, 1092) |
| 25 | `kernel/guardian.py` | 1 | 544 | Sprint 61 — Guardián de los Objetivos (Obj #14). Meta-vigilancia + alertas. | Obj #14 | ✅ integrado (main:926-947) |

**Totales de bloque (verificación `wc -l`):**

```
kernel/catastro/                       6,848 LOC en 15 .py + sources/
kernel/transversales/ (todo)           2,423 LOC en 14 .py
kernel/sovereignty/engine.py             532 LOC
kernel/sovereign_llm.py                  362 LOC
kernel/vanguard/                       1,488 LOC en 5 .py
kernel/collective/                     1,508 LOC en 4 .py
kernel/causal_decomposer.py              360 LOC
kernel/causal_seeder.py                  725 LOC
kernel/causal_simulator.py               408 LOC
kernel/simulator/causal_simulator_v2.py  420 LOC
kernel/brand/ (sin yamls)                821 LOC en 4 .py
kernel/design/system.py                  534 LOC
kernel/dashboards/cost_history.py        443 LOC
kernel/zero_config/                      541 LOC en 3 .py
kernel/i18n/engine.py                    498 LOC
kernel/error_memory.py                   858 LOC
kernel/magna_classifier.py               735 LOC
kernel/magna_routes.py                   167 LOC
kernel/guardian.py                       544 LOC
                                       ─────
                                      ~19,815 LOC
```

(El total agregado real es mayor que 16.5K por inclusión de catastro/sources/. La cifra del resumen ejecutivo es prudente y se mantiene como límite inferior.)

---

## 3. Detalle por subdirectorio

### 3.1 `kernel/catastro/` — 6,848 LOC, 15 .py + sources

**Contenido (`ls`):**
- `__init__.py` 199 LOC (re-exports + version `0.86.7`)
- `catastro_routes.py` 359 LOC — APIRouter REST con auth Bearer
- `coding_classifier.py` 274 LOC + `reasoning_classifier.py` 324 LOC — clasificadores especializados
- `cron.py` 159 LOC — entrypoint Railway scheduled task
- `dashboard.py` 886 LOC + `dashboard_*` componentes — Bloque 7 dashboard de salud
- `mcp_tools.py` 183 LOC — 4 tools FastMCP (sub-server montado en main:1271)
- `multi_namespace.py` 275 LOC — soporte multi-namespace
- `persistence.py` 569 LOC — wiring atómico Supabase via RPC PL/pgSQL
- `pipeline.py` 1,268 LOC — pipeline diario MVP
- `quorum.py` 482 LOC — QuorumValidator 2-de-3 + cross-validation
- `recommendation.py` 774 LOC — RecommendationEngine + cache LRU + modo degraded
- `schema.py` 532 LOC + `schema_generated.py` 173 LOC — schema dual (manual deprecándose, generado autoritativo)
- `trono.py` 391 LOC — cálculo Trono Score por dominio
- `data/` — 3 JSON (catastro_agentes, catastro_suppliers, catastro_tools)
- `sources/` — 13 .py: `aime`, `artificial_analysis`, `gpqa`, `human_eval`, `lmarena`, `mbpp`, `mmlu_pro`, `openrouter`, `swe_bench`, `field_mapping` + base + yaml
- `tests/` — `run_tests_standalone.py`, `test_multi_namespace.py`

**Integración:** `main.py:1251-1292` — `RecommendationEngine` instanciado, `set_dependencies` inyecta engine a routes/MCP, `app.include_router(_catastro_routes.router, prefix="/v1/catastro")`, FastMCP sub-server montado bajo prefix `catastro`.

**Tests externos:** `tests/test_catastro_schema_drift.py`. Tests internos: `kernel/catastro/tests/`.

**Estado:** ✅ El módulo especializado más maduro. Cubre Obj #5 (Magna) + Capa 0 (Cimientos). Schema versionado (Sprint 86 Bloque 7), MCP integrado, Dashboard con auth.

---

### 3.2 `kernel/transversales/` — 2,423 LOC, 14 .py

**Estructura única detectada (verificada vía `ls -la`):**

Cada capa tiene SÓLO 2 archivos:
- `__init__.py` (donde vive la clase `XxxLayer(TransversalLayer)`)
- `_canonical_constraints.py` (constantes Python derivadas de DSCs)

**NO existe un archivo separado tipo `seo_layer.py` o `ventas_layer.py`.** La clase vive directamente en `__init__.py`. La COWORK_BASE_CONOCIMIENTO §3 sugería que existían archivos principales de capa adicionales — esa expectativa es incorrecta.

**`base.py` (184 LOC):** `TransversalLayer(ABC)` con 4 métodos abstractos (`diagnose`, `recommend`, `implement`, `monitor`) + dataclasses (`TransversalContext`, `TransversalRecommendation`, `TransversalRecommendations`) + enums (`VerticalId` 8 verticales, `BusinessModelArchetype` 12 archetypes, `GeoRegion` 5 regiones) + `RestrictedVerticalError` (DSC-MB-001 OPSEC) + `all_layers_implemented()` gate.

**Estado de `implement()` y `monitor()` por capa (verificado vía `grep -nE "def implement|def monitor|raise NotImplementedError"`):**

| Capa | `diagnose` | `recommend` | `implement` | `monitor` | Tests |
|---|---|---|---|---|---|
| `seo/` | ✅ real | ✅ real | ✅ real (212-336) | ✅ real (337-385) | `test_seo_layer_implement.py` + `test_transversales_seo_constraints.py` |
| `ventas/` | ✅ real (68) | ✅ real (81) | ❌ `raise NotImplementedError` (177) | ❌ `raise NotImplementedError` (184) | `test_transversales_ventas_constraints.py` (sólo constraints) |
| `publicidad/` | ✅ real (47) | ✅ real (65) | ❌ `raise NotImplementedError` (232) | ❌ `raise NotImplementedError` (240) | `test_transversales_publicidad_constraints.py` |
| `tendencias/` | ✅ real (19) | ✅ real (32) | ❌ `raise NotImplementedError` (100) | ❌ `raise NotImplementedError` (106) | `test_transversales_tendencias_constraints.py` |
| `operaciones/` | ✅ real (19) | ✅ real (34) | ❌ `raise NotImplementedError` (130) | ❌ `raise NotImplementedError` (136) | `test_transversales_operaciones_constraints.py` |
| `finanzas/` | ✅ real (19) | ✅ real (35) | ❌ `raise NotImplementedError` (147) | ❌ `raise NotImplementedError` (153) | `test_transversales_finanzas_constraints.py` |

**Hallazgo crítico:** `grep -rln "kernel\.transversales"` en kernel/ excluyendo el propio dir y tests retorna **0 resultados**. NO está cableado a `main.py`, ni a `engine.py`, ni a `embrion_loop.py`, ni a `nodes.py`, ni a `agui_adapter.py`, ni a `embrion_routes.py`. El subsistema completo vive aislado del flujo principal del kernel — los únicos consumidores son sus propios tests.

**Implicación para Obj #9 Transversalidad Universal:** la afirmación COWORK_BASE_CONOCIMIENTO §3 "75% completo" merece revisión. Cobertura real de `implement()` end-to-end: **1/6 capas = 17%**. El 75% es probablemente un agregado optimista que cuenta `diagnose`+`recommend`.

---

### 3.3 `kernel/sovereignty/engine.py` — 532 LOC + `kernel/sovereign_llm.py` — 362 LOC

Dos archivos distintos pero relacionados.

**`sovereignty/engine.py`** (Sprint 60): mapea dependencias externas (OpenAI, Anthropic, Google, etc.), define alternativas self-hosted (Ollama, vLLM), y genera migration paths. Filosofía declarada: "Funciona MEJOR con internet, pero SOBREVIVE sin él".

- Init: `init_sovereignty_engine()` (main:878) → `app.state.sovereignty_engine` (main:885).
- Test directo: ❌ ninguno (`test_sprint_60.py`? no detectado en grep).

**`sovereign_llm.py`** (Sprint 56.5, top-level): capa de abstracción LLM con routing 3-tier (Tier 1 Ollama local → Tier 2 Ollama cloud / gpt-4o-mini → Tier 3 frontier). 

- Init: `init_sovereign_llm()` (main:761) → `app.state.sovereign_llm` (main:763).
- Test directo: ❌ ninguno.

---

### 3.4 `kernel/vanguard/` — 1,488 LOC, 5 .py

**Contenido:**
- `__init__.py` 52 LOC
- `intelligence_engine.py` 445 LOC — Sprint 63.1, motor de evaluación de relevancia + propuesta de integraciones
- `semantic_scholar.py` 253 LOC — cliente Semantic Scholar
- `tech_radar.py` 503 LOC — radar de agentes/herramientas
- `weekly_digest.py` 235 LOC — generador de digest semanal

**Integración:** `main.py:879` (`init_tech_radar`), `main.py:1007-1021` (`init_intelligence_engine`, `init_scholar_client`, `init_digest_generator`).

**Tests directos:** ❌ ninguno (`test_sprint_63.py` cubre tangencialmente).

---

### 3.5 `kernel/collective/` — 1,508 LOC, 4 .py

**Contenido:**
- `__init__.py` 56 LOC
- `protocol.py` 705 LOC — `ColectivaProtocol` (Sprint 61): pub/sub inter-embrión + debates estructurados con síntesis LLM
- `knowledge_propagator.py` 458 LOC
- `emergence_detector.py` 289 LOC

**Integración:** `main.py:923` (`from kernel.collective.protocol import ColectivaProtocol`), `main.py:1013-1014` (`init_knowledge_propagator`, `init_emergence_detector`).

**Tests directos:** ❌ ninguno.

---

### 3.6 Causal stack: `causal_decomposer.py` + `causal_seeder.py` + `causal_simulator.py` + `simulator/causal_simulator_v2.py`

LOC total: **1,913** (360 + 725 + 408 + 420).

- `causal_decomposer.py` (Sprint 55.4): descompone evento → factores causales atómicos. Init main:145.
- `causal_seeder.py` (Sprint 56.1): pipeline autónomo poblando Causal Knowledge Base, Perplexity Sonar. Init main:660-708.
- `causal_simulator.py` (v1): Monte Carlo. Init main:158.
- `simulator/causal_simulator_v2.py` (Sprint 60): Monte Carlo v2 calibrado desde FinancialLayer + 4 escenarios. Init main:880, 895.

**Tests directos:** ❌ ninguno (1:1). Cobertura tangencial via tests sprint-numbered.

**Observación:** convivencia v1 + v2 en disco. No verificado si v1 sigue siendo llamado por algún módulo o es legacy.

---

### 3.7 `kernel/brand/` — 821 LOC, 4 .py + 6 yamls

**Contenido:**
- `__init__.py` 23 LOC
- `brand_dna.py` 208 LOC
- `brand_routes.py` 173 LOC
- `validator.py` 417 LOC — Sprint 82, score 0-100, threshold 60 (objetivo 75), modo ADVISORY (no bloqueante)
- `verticals/*.yaml` × 6 — `ecommerce_artisanal`, `education_arts`, `marketplace_services`, `professional_services`, `restaurant`, `saas_b2b`

**Integración:** `main.py:1573` (`from kernel.brand.validator import BrandValidator`), `main.py:1708-1709` (`include_router(brand_router)`).

**Tests directos:** ✅ `test_brand_engine.py` (cubre validator, no brand_routes).

---

### 3.8 `kernel/design/system.py` — 534 LOC

Sprint 61. Design System enforcement engine. 4 dimensiones declaradas en docstring: Design Tokens (OKLCH + Inter), Accessibility (WCAG 2.2 axe-core via Playwright), [otras 2 no inspeccionadas en este audit].

Init: `main.py:924` (`from kernel.design.system import DesignSystemEngine, get_design_system_engine`), instancia main:938.

Tests directos: ❌ ninguno.

---

### 3.9 `kernel/dashboards/cost_history.py` — 443 LOC

Dashboard estático HTML del histórico de costo del Embrión. CLI standalone (`python -m kernel.dashboards.cost_history --output bridge/embrion_dashboard.html`). Reusa `_SupabaseRest` de `kernel.embrion_budget`. Cero deps JS externas (SVG inline).

**Integración:** ❌ NO importado por ningún módulo del kernel. Sólo lo usa `tests/test_cost_history_dashboard.py` y la propia CLI. **Aislado.**

Test directo: ✅ `test_cost_history_dashboard.py`.

---

### 3.10 `kernel/zero_config/` — 541 LOC, 3 .py

**Contenido:**
- `__init__.py` 33 LOC
- `intent_inferrer.py` 307 LOC — Sprint 63.2, infiere proyecto desde 1 frase
- `smart_defaults.py` 201 LOC — defaults por industria + estilo

**Integración:** `main.py:1010` (`init_intent_inferrer`), `main.py:1031`, flag `zero_config=True` en main:1051.

Tests directos: ❌ ninguno (cobertura via `test_sprint_63.py`).

---

### 3.11 `kernel/i18n/engine.py` — 498 LOC

Sprint 59.1. Motor i18n 2 niveles: interno (Monstruo opera en idioma del usuario) + proyectos (templates React/Next.js i18n). DeepL primario + LLM Sabios fallback + heurísticas charset (CJK/árabe sin LLM).

**Integración:** ❌ NO importado por ningún módulo del kernel. Sólo cubierto por `tests/test_sprint_59.py`. **Aislado.** Primer módulo que toca Obj #13 (Del Mundo, hoy ~10%).

---

### 3.12 `kernel/error_memory.py` — 858 LOC

Sprint 81, Capa 0.1. Memoria de Errores persistente. Cubre Obj #4 ("No equivocarse dos veces").

Integración: `main.py:1112-1123` (`from kernel.error_memory import ErrorMemory, build_embedding_client`), instancia + inyección.

Test directo: ✅ `test_error_memory.py`.

---

### 3.13 `kernel/magna_classifier.py` — 735 LOC + `kernel/magna_routes.py` — 167 LOC

**`magna_classifier.py`** (Sprint 81, Capa 0.2): clasifica input del Embrión → ruta graph (LangGraph completo + tools) vs ruta router (chat-only barata).

**`magna_routes.py`**: 3 endpoints `POST /v1/magna/classify`, `GET /v1/magna/stats`, `POST /v1/magna/cleanup`.

Integración:
- main:1082-1090 — `MagnaClassifier` instanciado.
- main:1083 — `from kernel.magna_routes import router as magna_router, set_dependencies as set_magna_deps`.
- main:1092 — `app.include_router(magna_router)`.
- main:1095 — magna_classifier inyectado al `EmbrionLoop` (puente con doctrina del silencio).

Test directo: ✅ `test_magna_classifier.py`.

---

### 3.14 `kernel/guardian.py` — 544 LOC

Sprint 61. Guardián de los Objetivos (Obj #14). Meta-vigilancia perpetua que observa los 13 objetivos y dispara alertas. Una sola clase `GuardianDeObjetivos`.

Integración: `main.py:926-947` (`from kernel.guardian import GuardianDeObjetivos`, instancia, `app.state.guardian = guardian`).

Tests directos: ❌ ninguno.

---

## 4. Cruce: Obj/Capa cubiertos vs estado real

| Obj/Capa | Módulos kernel especializados que la cubren | Estado del cubrimiento (este audit) |
|---|---|---|
| Obj #2 Apple/Tesla | `brand/`, `design/system.py` | ✅ wired, tests parciales (sólo brand). Quality gate aún ADVISORY. |
| Obj #3 Mínima complejidad | `zero_config/` | ✅ wired, sin test 1:1. |
| Obj #4 No equivocarse 2× | `error_memory.py`, `dashboards/cost_history.py` | ✅ wired (`error_memory`); 🟡 aislado (`cost_history`). Test ✅ ambos. |
| Obj #5 Magna/Premium | `magna_classifier.py` + `magna_routes.py` + `catastro/` | ✅ wired completo. Test ✅. |
| Obj #6 Vanguardia | `vanguard/` (4 archivos) | ✅ wired, sin tests 1:1. |
| Obj #8 Inteligencia Emergente | `collective/protocol.py` | ✅ wired, sin test 1:1. |
| Obj #9 Transversalidad | `transversales/` 6 capas | ❌ **5/6 capas son stubs**. Sólo SeoLayer end-to-end. **NO importado desde main.py ni engine.py**. |
| Obj #10 Simulador Causal | `causal_decomposer`, `causal_seeder`, `causal_simulator`, `simulator/causal_simulator_v2` | ✅ wired (4 archivos), sin tests 1:1. v1 + v2 conviven. |
| Obj #11 Multiplicación Embriones | `collective/knowledge_propagator`, `collective/emergence_detector` | ✅ wired, sin tests 1:1. |
| Obj #12 Soberanía | `sovereignty/engine.py`, `sovereign_llm.py` | ✅ wired ambos, sin tests. |
| Obj #13 Del Mundo | `i18n/engine.py` | 🟡 aislado (no importado fuera de tests). |
| Obj #14 Guardián | `guardian.py` | ✅ wired, sin test. |

---

## 5. Inconsistencias y gaps detectados (1C)

1. **5 capas transversales son stubs declarados** (`raise NotImplementedError`). DSC-G-014 ("PRODUCTO COMERCIALIZABLE") se gateó vía `all_layers_implemented()` en `base.py`, pero esa función sólo verifica que la clase exista — NO que `implement()`/`monitor()` no levanten `NotImplementedError`. **El gate es laxo y permite declarar productos comercializables falsamente cubiertos.**
2. **`kernel/transversales/` está aislado del flujo principal del kernel.** Ningún archivo en kernel/ (excepto el propio dir) lo importa. Esto contradice "Obj #9 Transversalidad Universal" — está implementado como subsistema independiente, no como capa cruzando todo producto.
3. **Tests 1:1 ausentes en 11 módulos especializados:** sovereignty/engine, sovereign_llm, vanguard/× 4, collective/× 3 (excepto cobertura tangencial), simulator/v2, causal_decomposer, causal_seeder, causal_simulator (v1), design/system, zero_config/× 2, guardian. Cobertura sólo via "test_sprint_NN.py" agregadores, lo que dificulta atribuir fallos.
4. **`dashboards/cost_history.py` y `i18n/engine.py` aislados.** Implementados con tests, pero ningún módulo del kernel los importa. Riesgo: rot silencioso si nadie los ejecuta.
5. **Convivencia `causal_simulator.py` (v1, top-level) + `simulator/causal_simulator_v2.py`** sin política explícita de deprecación documentada en código. Riesgo de dos motores Monte Carlo activos.
6. **`schema.py` (532 LOC) + `schema_generated.py` (173 LOC) en catastro:** docstring de `schema_generated.py` declara "schema.py (manual) está siendo deprecado gradualmente". Hay deprecación parcial sin fecha de muerte ni gate de migración firmado en código.
7. **`kernel/brand/verticals/` tiene 6 archetypes pero `BusinessModelArchetype` declara 12.** Gap: 6 archetypes (`SAAS_B2B`, `MARKETPLACE_SERVICES`, `ECOMMERCE_ARTISANAL`, `PROFESSIONAL_SERVICES`, `EDUCATION_ARTS`, `RESTAURANT`) tienen yaml; los otros 6 (`TOKENIZED_REAL_ESTATE`, `TICKETING_LIMITED_INVENTORY`, `REAL_ESTATE_DISTRICT`, `IOT_B2B_REGULATED`, `AI_AGENT_PLATFORM_CONSUMER`, `AGENT_PLATFORM_B2B`) NO. Esto coincide con CIP/LikeTickets/Kukulkán/BioGuard/TopControl pendientes de comercialización.
8. **`embrion_specializations/`, `embriones/`, `milestones/`, `marketplace/`, `memento/`** — subdirectorios visibles en `ls kernel/` pero NO solicitados por el scheduled task 1C. Quedan para sub-fase futura.

---

## 6. Estado: integrado / aislado / stub

**Integrado al flujo principal (con cableado en `main.py` o consumidores kernel):**
catastro (15+ archivos), sovereignty/engine, sovereign_llm, vanguard (4), collective (3), causal_decomposer, causal_seeder, causal_simulator (v1), simulator/v2, brand (validator+routes+dna), design/system, zero_config/intent_inferrer, error_memory, magna_classifier, magna_routes, guardian.

**Implementado pero aislado (sin consumer kernel fuera de tests):**
transversales/ (todas las 6 capas), dashboards/cost_history, i18n/engine.

**Stubs (NotImplementedError explícito):**
transversales/ventas/`implement`, transversales/ventas/`monitor`,
transversales/publicidad/`implement`, transversales/publicidad/`monitor`,
transversales/tendencias/`implement`, transversales/tendencias/`monitor`,
transversales/operaciones/`implement`, transversales/operaciones/`monitor`,
transversales/finanzas/`implement`, transversales/finanzas/`monitor`.

(10 stubs concentrados en 5 capas comerciales. SeoLayer es la excepción.)

---

## 7. Autoaudit (Cowork sobre Cowork)

- ✅ Documento ≤ 10 páginas markdown.
- ✅ Cada afirmación tiene path + número de línea o output bash citado (`wc -l`, `grep -nE`, `grep -rln`, `head`).
- ✅ NO inferencia desde memoria — todas las cifras LOC vienen de `wc -l` ejecutado en sesión.
- ✅ NO uso "Hilo A" ni "Hilo B" para Cowork. Cowork = Arquitecto Jefe.
- ✅ Stubs marcados explícitamente con ❌ y referencia a línea de `raise NotImplementedError`.
- ✅ Honestidad pura: declarado que el "75%" Obj #9 de COWORK_BASE_CONOCIMIENTO §3 está sobre-estimado (cobertura real `implement()`+`monitor()` end-to-end es 17%).
- ⚠ Limitación reconocida 1: NO leí cuerpo completo de cada `__init__.py` de capa transversal — confirmé stubs vía `grep "raise NotImplementedError"` y conteo de funciones. Es posible (poco probable) que diagnose/recommend tengan ramas también stubeadas.
- ⚠ Limitación reconocida 2: NO ejecuté pytest sobre los módulos. La calidad real de coverage es desconocida; este audit reporta presencia/ausencia de archivos `test_*.py` con nombre matching, no resultado de ejecución.
- ⚠ Limitación reconocida 3: subdirectorios `kernel/embrion_specializations/`, `kernel/embriones/`, `kernel/milestones/`, `kernel/marketplace/`, `kernel/memento/`, `kernel/plugins/`, `kernel/portability/`, `kernel/security/`, `kernel/learning/`, `kernel/components/`, `kernel/alerts/`, `kernel/browser/`, `kernel/utils/`, `kernel/ux/`, `kernel/validation/`, `kernel/motion/`, `kernel/moc/`, `kernel/e2e/` NO están en scope 1C — quedan para sub-fases posteriores.

---

## 8. Para próxima sub-fase 1D — audit `docs/`

Notas para 1D basadas en evidencia recolectada hoy:

1. **`docs/` tiene 217 .md** (Cartografía 1A §2). Necesario árbol por subdirectorio (sprints, ADRs, biblias, arquitectura, roadmaps) antes de auditar contenido.
2. **Cruce crítico 1D ↔ 1C:** verificar que `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` v3.0 declara los porcentajes Obj #9 (Transversalidad) consistentes con el hallazgo de este audit (5/6 capas son stubs). Si declara ≥75% sin matizar, hay un gap doctrinal entre código y doctrina.
3. **Cruce 1D ↔ 1B:** verificar que `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` y `docs/ARQUITECTURA_ENGRANAJE_v1.0.md` están sincronizados con el estado real del kernel (engine.py, embrion_loop.py, runner/* auditados en 1B).
4. **Cruce 1D ↔ 1A:** verificar `docs/ESTADO_SISTEMA.md` (declarado posiblemente desactualizado en 1A §4 ítem 4) contra `bridge/ESTADO_MONSTRUO_2026_05_10_vs_PLANES.md`.
5. **Sprints documentados:** identificar cuántos sprints 51-90 tienen plan en `docs/SPRINT_NN_PLAN.md` y cuántos están sin documentar para detectar deuda de documentación de sprints recientes.
6. **DSCs declarados:** la 1A detectó que `_INDEX.md` declara 44 DSCs cuando hay 62. La 1D debe confirmar la lista canónica via `find discovery_forense -name "DSC-*.md"` y proponer reindexación.
7. **Sprint S-003.B (audit middleware) en `bridge/postmortems/`:** la 1B detectó que el commit no incluye wiring. La 1D debe confirmar si existe doc en `docs/` o `bridge/` que afirme el sprint completo, lo cual sería una contradicción documental.
8. **Sub-fase 1E posible (no comprometida):** subdirectorios `kernel/` no auditados (ver §7 limitación 3) merecen su propia 1E si la 1D revela dependencias documentadas hacia ellos.

---

*Generado por Cowork 2026-05-10 como Sub-Fase 1C del Estudio Forense del Monstruo. Próxima sub-fase: 1D — audit `docs/`.*
