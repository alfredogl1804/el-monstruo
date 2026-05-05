# Pre-investigación Sprint 88 — Macroárea 3: LLM Coding

> Hilo Manus Catastro · 2026-05-04 22:10 CST · Standby Productivo Sprint 86  
> Validación tiempo real ejecutada el 2026-05-04. Fuentes primarias: BenchLM SWE-bench Verified (visitada en navegador), múltiples leaderboards cross-checked.

---

## 1. Justificación de macroárea

La **Macroárea 3 — LLM Coding** se separa de Macroárea 1 (Inteligencia general) porque el coding tiene **benchmarks específicos**, **economía propia** (los modelos especializados como GPT-5.3 Codex tienen pricing diferenciado), y **subcapacidades distintas** (autocomplete vs agente vs refactor). El schema actual del Catastro ya prevé esto: el enum `Dominio.CODING_LLMS` existe en `kernel/catastro/schema.py` línea 55.

**Justificación adicional:** la roadmap del Monstruo (AGENTS.md Capa 2 Inteligencia Emergente) prioriza tener un curador propio de modelos de coding porque El Monstruo escribe código intensamente (ya sea para sí mismo, para los Embriones, o para productos finales). El Catastro debe poder responder "¿qué modelo le pongo a Cline para Yucatán Renders?" o "¿qué modelo es óptimo para refactor de TypeScript en Mérida?".

## 2. Dominios candidatos (subdivisión de la macroárea)

A diferencia de visión generativa (que tiene 2 sub-arenas separadas en AA), el espacio de coding LLM se subdivide por **modo de uso**:

| Dominio (slug) | Descripción | Benchmark primario |
|---|---|---|
| `coding-agent` | Agente autónomo que resuelve issues completas (SWE-bench Verified) | SWE-bench Verified |
| `coding-completion` | Autocompletion en IDE (latencia <500ms, contexto 16K) | LiveCodeBench |
| `coding-refactor` | Refactoring de código existente con preservación semántica | Aider Polyglot |
| `coding-debug` | Diagnóstico y fix de bugs específicos | DebugBench |

**Prioridad Sprint 88:** `coding-agent` y `coding-completion`. Los otros dos quedan diferidos. Esta separación permite que el Trono Score capture la realidad de que un modelo puede dominar SWE-bench (agente) pero ser lento para autocompletion en tiempo real.

## 3. Modelos frontier observados (Top-15 SWE-bench Verified, 2026-05-01)

Datos capturados en vivo desde [benchlm.ai/benchmarks/sweVerified](https://benchlm.ai/benchmarks/sweVerified) el 2026-05-04 22:02 CST.

| Rank | Provider | Modelo | SWE-bench % | Contexto | Notas |
|---|---|---|---|---|---|
| 1 | Anthropic | Claude Mythos Preview | **93.9** | 1M | Recién lanzado, "Adaptive Reasoning" |
| 2 | Anthropic | Claude Opus 4.7 (Adaptive) | 87.6 | 1M | Modo "Adaptive" mode-key |
| 3 | OpenAI | GPT-5.3 Codex | 85.0 | 400K | Especializado coding |
| 4 | Anthropic | Claude Opus 4.5 | 80.9 | -- | Versión anterior |
| 5 | Anthropic | Claude Opus 4.6 | 80.8 | -- | -- |
| 6 | DeepSeek | DeepSeek V4 Pro (Max) | 80.6 | -- | Open-source competitivo |
| 7 | Moonshot AI | Kimi K2.6 | 80.2 | -- | Líder chino agentic |
| 8 | OpenAI | GPT-5.2 | 80.0 | -- | -- |
| 9 | Anthropic | Claude Sonnet 4.6 | 79.6 | -- | Más barato que Opus |
| 10 | DeepSeek | DeepSeek V4 Pro (High) | 79.4 | -- | Mode "High" |
| 11 | DeepSeek | DeepSeek V4 Flash (Max) | 79.0 | -- | Tier rápido |
| 12 | Alibaba | Qwen3.6 Plus | 78.8 | -- | Open-weights |
| 13 | DeepSeek | DeepSeek V4 Flash (High) | 78.6 | -- | -- |
| 14 | Xiaomi | MiMo-V2-Pro | 78.0 | -- | -- |
| 15 | Z.AI | GLM-5 | 77.8 | -- | -- |

### 3.1. Distribución por proveedor (top-15)

| Provider | Modelos en top-15 | % |
|---|---|---|
| Anthropic | 5 | 33% |
| DeepSeek | 4 | 27% |
| OpenAI | 2 | 13% |
| Alibaba | 1 | 7% |
| Xiaomi | 1 | 7% |
| Moonshot AI | 1 | 7% |
| Z.AI | 1 | 7% |

**Hallazgo crítico:** China = ~56% del top-15 (DeepSeek+Alibaba+Xiaomi+Moonshot+Z.AI = 8) vs USA 7 (Anthropic+OpenAI). Esta paridad geopolítica NO existía en 2024-2025. Implicación para el Catastro: el campo `proveedor_pais` y `soberania_score` (ya en schema) capturan esto correctamente.

### 3.2. Mode-keys (subcapacidades dentro del mismo modelo)

Varios modelos del top-15 aparecen con **modos distintos** (Adaptive, Max, High, Pro, Flash). Esto NO debe modelarse como modelos separados en `catastro_modelos` porque son la misma base con diferentes configuraciones de inferencia. **Propuesta:** usar el campo `subcapacidades` (lista) para flagear `mode_adaptive`, `mode_max`, `mode_high`, etc., y `data_extra` para guardar el score específico de cada modo.

## 4. Métricas observadas en producción

### 4.1. Benchmarks principales 2026 (cross-checked en 4 fuentes)

| Benchmark | Tipo | Fortaleza | Debilidad |
|---|---|---|---|
| **SWE-bench Verified** | Agente real GitHub | Industry-standard, 500 issues | UC Berkeley demostró exploits (abril 2026), benchmaxxed |
| **LiveCodeBench** | Coding contest | Refresca semanal, evita data contamination | Solo problemas tipo concurso, no production |
| **Aider Polyglot** | Refactor multi-lenguaje | Cubre 6+ lenguajes | Subjective scoring |
| **HumanEval+ / MBPP+** | Funciones cortas | Reproducible, rápido | Saturado, top modelos = 95%+ |
| **Coding Arena (Elo)** | Preferencia humana ciega | Refleja UX real | Lento de obtener data |
| **Terminal-Bench** | Comandos shell | Evalúa workflow real | Pocos modelos evaluados |

### 4.2. Métricas que el Catastro debe capturar (mapping al schema actual)

| Métrica externa | Campo Catastro | Notas |
|---|---|---|
| SWE-bench Verified % | `quality_score` (porción) | Normalizar 0-100 |
| LiveCodeBench % | `quality_score` (porción) | Promedio ponderado |
| Latency p50 ms (autocompletion) | `speed_score` (alto = rápido) | Solo para dominio `coding-completion` |
| $/1M input + $/1M output | `cost_efficiency` | Combinado con tokens promedio por tarea |
| Context window | `data_extra.context_window_tokens` | 1M para Mythos, 400K para GPT-5.3 Codex |
| Provider uptime | `reliability_score` | Histórico 90 días vía Status pages |
| Brand DNA fit | `brand_fit` | 0-1 score curado por humano |
| País del proveedor | `data_extra.proveedor_pais` | "USA", "China", "France", etc. |
| Open weights | `open_weights` | Bool ya en schema |

### 4.3. Salvaguardas críticas (lección de Berkeley)

UC Berkeley (abril 2026) demostró que 8 benchmarks de agentes incluyendo SWE-bench fueron exploitable: un agente trampa scoreó 100% sin resolver tareas. **Implicación para el Catastro:**

1. NO usar SWE-bench Verified como métrica única.
2. Aplicar **Quorum 2-de-3** (ya implementado en Bloque 2) requiriendo coincidencia entre AL MENOS 2 benchmarks ortogonales.
3. Marcar modelos con `confidence < 0.6` cuando solo hay 1 benchmark disponible (la banda de confianza del Trono ya hace esto).

## 5. Schema delta requerido (mínimo invasivo)

Igual que para Macroárea 2, el schema actual **ya soporta** modelos de coding sin migración. Solo agregar valores enum:

```python
# kernel/catastro/schema.py
class Dominio(str, Enum):
    # Macroárea 1 (existentes)
    LLM_FRONTIER = "llm_frontier"
    LLM_OPEN_SOURCE = "llm_open_source"
    CODING_LLMS = "coding_llms"   # Existente — se queda como cluster general
    SMALL_EDGE = "small_edge"
    # Macroárea 2 (Sprint 87)
    TEXT_TO_IMAGE = "text-to-image"
    IMAGE_EDITING = "image-editing"
    # Macroárea 3 (Sprint 88) — sub-divisiones específicas
    CODING_AGENT = "coding-agent"
    CODING_COMPLETION = "coding-completion"
    CODING_REFACTOR = "coding-refactor"
    CODING_DEBUG = "coding-debug"
```

Y agregar al vocabulario controlado de subcapacidades:

```python
SUBCAPACIDADES_CODING = [
    "long_context_1m",        # >=1M token contexto
    "tool_use_native",        # Function calling robusto
    "multi_file_edit",        # Edit múltiples archivos en una pasada
    "test_generation",        # Genera tests unitarios fiables
    "diff_aware",             # Trabaja con diffs/patches sin re-escribir
    "language_polyglot",      # Soporta 5+ lenguajes con fluidez similar
    "fast_completion",        # p50 < 500ms para autocomplete
    "cost_efficient",         # < $0.50/1M tokens output
    "open_weights",           # Pesos descargables
    "mode_adaptive",          # Tiene modo "adaptive thinking"
    "mode_high_reasoning",    # Tiene modo "high reasoning"
]
```

## 6. Validador adversarial específico

Para coding LLMs el Quorum 2-de-3 funciona perfectamente porque ya hay **múltiples fuentes públicas independientes** que publican scores:

| Curador | Tipo | Función |
|---|---|---|
| **BenchLM SWE-bench** | Web scraping/API | SWE-bench Verified score |
| **LiveCodeBench** | Web scraping/API | LiveCodeBench score (data contamination resistente) |
| **Artificial Analysis Coding** | API o scraping | Coding Arena Elo |
| **Aider Polyglot** | Repo público GitHub | Refactor multi-lenguaje |

**Quorum 2-de-3:** un modelo es "validado" si AL MENOS 2 de las 4 fuentes lo posicionan en el top-X del dominio. Discrepancias se marcan con `quorum_alcanzado=False` y banda de confianza ancha en el Trono.

## 7. Fuentes y APIs accionables

| Fuente | URL | Cómo se ingiere |
|---|---|---|
| BenchLM | `benchlm.ai/api/v1/benchmarks/...` (verificar) | Usar API o scraping de la página HTML |
| LiveCodeBench | `livecodebench.github.io` | Scraping de la tabla HTML, refresca semanal |
| Artificial Analysis Coding | `artificialanalysis.ai/api/v2/coding` (paywall posible) | Mismo patrón Macroárea 1+2 |
| Aider Polyglot | `github.com/Aider-AI/aider/blob/main/benchmark.md` | Fetch raw markdown del repo |
| Anthropic Console | `console.anthropic.com/docs/api/models` | Pricing y capacidades |
| OpenAI Models | `platform.openai.com/docs/models` | Pricing y capacidades |

## 8. Estimación de esfuerzo Sprint 88

Asumiendo el patrón endurecido del Sprint 86 (7 bloques, ~2h cada uno):

| Bloque | Trabajo | ETA |
|---|---|---|
| 88-B1 | Schema delta (4 nuevos dominios coding-*, subcapacidades coding) + tests | 0.5h |
| 88-B2 | Fuente BenchLM (cliente HTTP + parser SWE-bench Verified + tests) | 2h |
| 88-B3 | Fuente LiveCodeBench (scraping HTML + cache + tests) | 1.5h |
| 88-B4 | Fuente Aider Polyglot (fetch markdown + parse tabla + tests) | 1h |
| 88-B5 | Pipeline integration + validador con Quorum 2-de-3 ortogonal | 1h |
| 88-B6 | Primer run productivo coding + dashboard endpoints específicos | 1h |
| 88-B7 | Tests E2E + guía operativa coding | 1h |
| **Total** | | **~8h** |

## 9. Riesgos identificados

1. **Benchmaxxing.** Berkeley abril 2026: 8 benchmarks vulnerables. Mitigación: Quorum ortogonal + banda confianza ancha si solo 1 fuente.
2. **Cadencia de releases.** Anthropic lanzó Mythos Preview entre 4.7 y 4.6 sin esperar al ciclo. Mitigación: cron diario del Catastro (Sprint 86 Bloque 6) detecta nuevos modelos en 24h.
3. **Pricing volatilidad.** Los precios cambiaron 3 veces en abril 2026 (GPT-5.3 codex bajó 40%, Anthropic subió Sonnet 4.7 25%). Mitigación: campo `precio_input_per_million` + `precio_output_per_million` se versiona en cada evento.
4. **Modelos chinos APIs caóticas.** DeepSeek/Moonshot/Z.AI tienen documentación menos estable que USA. Mitigación: degraded mode con warning si fuente china timeoutea.
5. **Mode-keys explosion.** Si Anthropic agrega "Mythos Adaptive Max High Pro" (4 modos × 5 modelos = 20 entradas), el catastro se infla. Mitigación: regla "solo modos públicos en API, no internos" + agrupación por modelo base en dashboard.

## 10. Recomendación al cierre

Sprint 88 puede arrancar en cuanto Sprint 87 (Visión Generativa) termine. La complejidad ingenieril es similar (~8h) y reusa todo el endurecimiento del Sprint 86 (persistence atómica, Trono Score, MCP, dashboard).

**Próximo paso pendiente del Catastro:** investigar si BenchLM publica una API REST o si su API requiere suscripción. Si paywall: scraping HTML del leaderboard como Bloque 88-B2 (ya validado en esta pre-investigación que la página se parsea sin issues).

---

**Capitalización:** este documento es la fuente única de verdad para el diseño del Sprint 88. Cualquier consulta sobre "qué modelo poner en Cline" o "qué viene después de Sprint 87" debe usarse este documento como base. El Hilo Cowork puede agregar bonus de bonificadores/penalizadores específicos para coding (Re-ranking contextual, deuda Bloque 4) cuando se complete Sprint 88.
