# Pre-investigación Sprint 86.5 — Macroárea 3: LLM Coding

> Hilo Manus Catastro · 2026-05-04 · Standby Productivo continuo
> Refinado tras audit Cowork (re-priorización: Sprint 86.5 = Coding, Sprint 86.6 = Visión)
> Validación tiempo real ejecutada el 2026-05-04. Fuentes primarias: BenchLM SWE-bench Verified (visitada en navegador), múltiples leaderboards cross-checked.

---

## 1. Justificación de macroárea

La **Macroárea 3 — LLM Coding** se separa de Macroárea 1 (Inteligencia general) porque el coding tiene **benchmarks específicos**, **economía propia** (los modelos especializados como GPT-5.3 Codex tienen pricing diferenciado) y **subcapacidades distintas** (autocomplete vs agente vs refactor). El schema actual del Catastro ya prevé esto: el enum `DominioInteligencia.CODING_LLMS` existe en `kernel/catastro/schema.py` línea 55 desde el Bloque 1.

**Justificación adicional:** la roadmap del Monstruo (AGENTS.md Capa 2 Inteligencia Emergente) prioriza tener un curador propio de modelos de coding porque El Monstruo escribe código intensamente (ya sea para sí mismo, para los Embriones, o para productos finales). El Catastro debe poder responder "¿qué modelo le pongo a Cline para Yucatán Renders?" o "¿qué modelo es óptimo para refactor de TypeScript en Mérida?".

**Por qué Cowork puso este sprint primero (decisión post-audit standby):** Cowork necesita el dominio Coding poblado para diseñar el nuevo Sprint 87 global (Ejecución Autónoma E2E del Hilo Ejecutor), y el hallazgo UC Berkeley sobre exploits SWE-bench urge tener el dominio activo bajo Quorum 2-de-3.

## 2. Dominios candidatos (subdivisión de la macroárea)

A diferencia de visión generativa (que tiene 2 sub-arenas separadas en AA), el espacio de coding LLM se subdivide por **modo de uso**:

| Dominio (slug) | Descripción | Benchmark primario | Prioridad 86.5 |
|---|---|---|---|
| `coding-agent` | Agente autónomo que resuelve issues completas (SWE-bench Verified) | SWE-bench Verified | ALTA |
| `coding-completion` | Autocompletion en IDE (latencia <500ms, contexto 16K) | LiveCodeBench | ALTA |
| `coding-refactor` | Refactoring de código existente con preservación semántica | Aider Polyglot | MEDIA (diferida) |
| `coding-debug` | Diagnóstico y fix de bugs específicos | DebugBench | BAJA (diferida) |

**Prioridad Sprint 86.5:** `coding-agent` y `coding-completion`. Los otros dos quedan diferidos a un Sprint 86.5.x si surge demanda. Esta separación permite que el Trono Score capture la realidad de que un modelo puede dominar SWE-bench (agente) pero ser lento para autocompletion en tiempo real.

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

**Hallazgo crítico:** China = ~56% del top-15 (DeepSeek+Alibaba+Xiaomi+Moonshot+Z.AI = 8) vs USA 7 (Anthropic+OpenAI). Esta paridad geopolítica NO existía en 2024-2025. Implicación para el Catastro: el campo `data_extra.proveedor_pais` y `sovereignty` (ya en schema) capturan esto correctamente.

### 3.2. Mode-keys (subcapacidades dentro del mismo modelo)

Varios modelos del top-15 aparecen con **modos distintos** (Adaptive, Max, High, Pro, Flash). Esto NO debe modelarse como modelos separados en `catastro_modelos` porque son la misma base con diferentes configuraciones de inferencia. **Propuesta:** usar el campo `subcapacidades` (lista) para flagear `mode-adaptive`, `mode-max`, `mode-high`, etc., y `data_extra` para guardar el score específico de cada modo.

## 4. Métricas observadas en producción

### 4.1. Benchmarks principales 2026 (cross-checked en 4 fuentes)

| Benchmark | Tipo | Fortaleza | Debilidad |
|---|---|---|---|
| **SWE-bench Verified** | Agente real GitHub | Industry-standard, 500 issues | UC Berkeley demostró exploits (abril 2026), benchmaxxed |
| **SWE-bench Lite** | Sub-set 300 issues fáciles | Menor varianza, faster eval | Saturado más rápido |
| **SWE-bench Multimodal** | Issues con imágenes/diagramas | Útil para frontend | Pocos modelos evaluados |
| **SWE-bench Multilingual** | 9 lenguajes | Mide fluidez polyglot | Dataset reciente (Nov 2024) |
| **LiveCodeBench** | Coding contest | Refresca semanal, evita data contamination | Solo problemas tipo concurso, no production |
| **Aider Polyglot** | Refactor multi-lenguaje | Cubre 6+ lenguajes | Subjective scoring |
| **HumanEval+ / MBPP+** | Funciones cortas | Reproducible, rápido | Saturado, top modelos = 95%+ |
| **Coding Arena (Elo)** | Preferencia humana ciega | Refleja UX real | Lento de obtener data |
| **Terminal-Bench** | Comandos shell | Evalúa workflow real | Pocos modelos evaluados |

### 4.2. SWE-bench subscores (decomposición obligatoria post-Berkeley)

UC Berkeley demostró que el score agregado SWE-bench Verified es exploitable. La defensa probada es **NO usar el score agregado**, sino los **subscores ortogonales**:

```yaml
swe_bench_subscores:        # Vive en data_extra cuando macroarea=coding
  verified_pct: 87.6        # 500 issues verificados, fuente primaria
  lite_pct: 91.2            # 300 issues fáciles, sanity check
  multimodal_pct: 72.4      # Issues con imágenes/diagramas (frontend)
  multilingual_pct:         # Por lenguaje, dict
    python: 89.1
    typescript: 84.3
    go: 78.2
    rust: 71.5
    java: 76.8
    cpp: 68.4
  drift_flag: false         # True si el modelo muestra drift entre versiones del mismo benchmark
  evaluator: "anthropic-internal"  # Quién corrió el benchmark
  evaluated_at: "2026-04-15T00:00:00Z"
```

**Heurística anti-exploit:** un modelo solo se considera "validado" en `coding-agent` si:
1. Tiene Verified ≥ 70% Y Lite ≥ Verified (Lite siempre debe ser >= Verified, sino hay anomalía)
2. Tiene Multilingual.python ≥ Verified - 10pp (sino sospecha de overfit a un lenguaje)
3. `evaluator` es "official" o pasa el quórum de 2 evaluadores independientes

### 4.3. Métricas que el Catastro debe capturar (mapping al schema actual)

| Métrica externa | Campo Catastro | Notas |
|---|---|---|
| SWE-bench Verified % | `quality_score` (porción) | Normalizar 0-100 |
| SWE-bench subscores | `data_extra.swe_bench_subscores` | dict completo (sec 4.2) |
| LiveCodeBench % | `quality_score` (porción) | Promedio ponderado |
| Latency p50 ms (autocompletion) | `speed_score` (alto = rápido) | Solo para dominio `coding-completion` |
| $/1M input + $/1M output | `cost_efficiency` | Combinado con tokens promedio por tarea |
| Context window | `data_extra.max_context_window_tokens` | 1M para Mythos, 400K para GPT-5.3 Codex |
| Lenguajes soportados | `data_extra.languages_supported` | Lista (sec 5.1 convención) |
| Agentic capable | `subcapacidades` con tag `agentic-capable` | Bool implícito por presencia |
| Provider uptime | `reliability_score` | Histórico 90 días vía Status pages |
| Brand DNA fit | `brand_fit` | 0-1 score curado por humano |
| País del proveedor | `data_extra.proveedor_pais` | "USA", "China", "France", etc. |
| Open weights | `open_weights` | Bool ya en schema |

### 4.4. Salvaguardas críticas (lección de Berkeley)

UC Berkeley (abril 2026) demostró que 8 benchmarks de agentes incluyendo SWE-bench fueron exploitable: un agente trampa scoreó 100% sin resolver tareas. **Implicación para el Catastro:**

1. **NO** usar SWE-bench Verified como métrica única.
2. Aplicar **Quorum 2-de-3** (ya implementado en Bloque 2) requiriendo coincidencia entre AL MENOS 2 benchmarks ortogonales.
3. Marcar modelos con `confidence < 0.6` cuando solo hay 1 benchmark disponible (la banda de confianza del Trono ya hace esto).
4. **Validar coherencia interna de subscores** (sec 4.2 heurística anti-exploit).

## 5. Schema delta: Opción A vs Opción B

El schema actual del Catastro **ya soporta** modelos de coding sin migración SQL. Hay dos caminos posibles para capturar los nuevos campos `languages_supported`, `max_context_window_tokens`, `agentic_capable`, `swe_bench_subscores`. Cowork debe decidir cuál antes de Sprint 86.5 Bloque 1.

### 5.1. Opción A — Convención de keys en `data_extra` (recomendada para v1.0)

**Cero migración SQL, cero código nuevo, máxima flexibilidad.** Definimos un contrato de keys obligatorias para `data_extra` cuando `macroarea ∈ {coding}`:

```python
# kernel/catastro/conventions.py (NUEVO archivo, ~30 líneas)
"""
Convención de keys obligatorias en data_extra por macroárea.
NO impuesto por Pydantic — validado por test de integridad y warning soft.
"""
DATA_EXTRA_KEYS_CODING = {
    "languages_supported": list,            # Ej. ["python", "typescript", "go", "rust"]
    "max_context_window_tokens": int,       # Ej. 1_000_000
    "agentic_capable": bool,                # True si el modelo soporta tool-use nativo
    "swe_bench_subscores": dict,            # Dict según sec 4.2
    "proveedor_pais": str,                  # ISO 3166-1 alpha-3, ej. "USA", "CHN"
    "release_date": str,                    # ISO 8601, ej. "2026-04-15"
    "documentation_url": str,               # URL canónica del modelo
}

def validate_coding_data_extra(data_extra: dict) -> list[str]:
    """Devuelve lista de warnings (no errores). Vacía = OK."""
    warnings = []
    for key, expected_type in DATA_EXTRA_KEYS_CODING.items():
        if key not in data_extra:
            warnings.append(f"missing recommended key: {key}")
        elif not isinstance(data_extra[key], expected_type):
            warnings.append(f"{key} should be {expected_type.__name__}, got {type(data_extra[key]).__name__}")
    return warnings
```

**Pros:**
- Zero migración SQL (no toca producción).
- Zero refactor del schema Pydantic.
- Extensible para futuras macroáreas (agregar `DATA_EXTRA_KEYS_VISION`, `DATA_EXTRA_KEYS_VOZ`, etc.).
- Compatible con runs ya existentes.

**Contras:**
- Queries SQL para "modelos con context_window > 500K" requieren `WHERE data_extra->>'max_context_window_tokens' > '500000'` (más verboso).
- No hay validación a nivel DB (solo en Python).

### 5.2. Opción B — Migration 020 con campos first-class

ALTER TABLE agregando 4 columnas typed con índices. Requiere migración SQL Y bump de schema Pydantic.

```sql
-- scripts/020_sprint86_5_catastro_coding_fields.sql (PROPUESTA, no ejecutado)
ALTER TABLE catastro_modelos
  ADD COLUMN languages_supported TEXT[] NOT NULL DEFAULT '{}',
  ADD COLUMN max_context_window_tokens INT,
  ADD COLUMN agentic_capable BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN swe_bench_subscores JSONB;

CREATE INDEX idx_catastro_languages_gin
  ON catastro_modelos USING GIN (languages_supported);

CREATE INDEX idx_catastro_context_window
  ON catastro_modelos (max_context_window_tokens DESC NULLS LAST);

CREATE INDEX idx_catastro_agentic
  ON catastro_modelos (agentic_capable) WHERE agentic_capable = TRUE;

COMMENT ON COLUMN catastro_modelos.languages_supported IS
  'Sprint 86.5 — Lenguajes soportados por modelos coding. Vacío para no-coding.';
COMMENT ON COLUMN catastro_modelos.max_context_window_tokens IS
  'Sprint 86.5 — Context window en tokens. NULL si desconocido.';
COMMENT ON COLUMN catastro_modelos.agentic_capable IS
  'Sprint 86.5 — True si el modelo soporta tool-use nativo robusto (function calling).';
COMMENT ON COLUMN catastro_modelos.swe_bench_subscores IS
  'Sprint 86.5 — Subscores decompuestos según sec 4.2 de la pre-investigación.';
```

```python
# kernel/catastro/schema.py — campos a agregar a CatastroModelo
languages_supported: list[str] = Field(default_factory=list)
max_context_window_tokens: Optional[int] = Field(None, ge=0)
agentic_capable: bool = False
swe_bench_subscores: Optional[dict[str, Any]] = None
```

**Pros:**
- Queries SQL nativas y rápidas (`WHERE 'python' = ANY(languages_supported)`).
- Validación a nivel DB (NOT NULL, defaults).
- Mejor para dashboards complejos del Sprint 86.5 Bloque 7.
- Reduce uso de `data_extra` (que actualmente es escape-hatch genérico).

**Contras:**
- Requiere migración 020 ejecutada por Hilo Ejecutor (otra dependencia externa).
- Cambia Pydantic schema → bump version + tests adicionales.
- Riesgo de conflicto con runs en flight si la migración corre a media operación.

### 5.3. Recomendación del Hilo Catastro

**Opción A para v1.0 del Sprint 86.5.** Razones:
1. El bloqueo externo del Hilo Ejecutor sigue activo (4 pendientes del Sprint 86 sin cerrar). Agregar una migración 020 más amplía el bloqueo, no lo resuelve.
2. La validación de keys en `data_extra` puede formalizarse con `validate_coding_data_extra` y un test que falle si un run productivo de coding tiene warnings.
3. Si en producción detectamos que las queries SQL son cuello de botella, hacemos Opción B en Sprint 86.5.x como deuda técnica menor (ALTER TABLE no destructivo, downtime mínimo).
4. Mantiene el principio Cowork: "no over-engineer hasta que haya data observada".

**Decisión final espera firma de Cowork.**

## 6. Vocabulario controlado de subcapacidades coding

Para que `subcapacidades` sea consistente y queryable, definir vocabulario:

```python
# kernel/catastro/vocabulary.py (NUEVO, ~20 líneas)
SUBCAPACIDADES_CODING = {
    "long-context-1m",          # >=1M token contexto
    "long-context-400k",        # >=400K token contexto
    "tool-use-native",          # Function calling robusto
    "multi-file-edit",          # Edit múltiples archivos en una pasada
    "test-generation",          # Genera tests unitarios fiables
    "diff-aware",               # Trabaja con diffs/patches sin re-escribir
    "language-polyglot",        # Soporta 5+ lenguajes con fluidez similar
    "fast-completion",          # p50 < 500ms para autocomplete
    "cost-efficient",           # < $0.50/1M tokens output
    "open-weights",             # Pesos descargables
    "agentic-capable",          # Mismo flag que data_extra.agentic_capable
    "mode-adaptive",            # Tiene modo "adaptive thinking"
    "mode-high-reasoning",      # Tiene modo "high reasoning"
    "mode-max",                 # Tiene modo "max" (mayor compute)
    "specialized-coding",       # Variante "Codex" / "Code" del modelo base
}
```

Usar guiones (no underscores) para alinear con la convención de slugs del schema (`schema.py` línea 170-172).

## 7. Validador adversarial específico (Quorum 2-de-3 ortogonal)

Para coding LLMs el Quorum 2-de-3 funciona perfectamente porque ya hay **múltiples fuentes públicas independientes**:

| Curador | Tipo | Cobertura | Estado |
|---|---|---|---|
| **BenchLM SWE-bench** | Web scraping/HTML | SWE-bench Verified score | ALTA prioridad |
| **LiveCodeBench** | GitHub Pages scraping | LiveCodeBench score (data contamination resistente) | ALTA prioridad |
| **Artificial Analysis Coding** | API o scraping | Coding Arena Elo | MEDIA (paywall posible) |
| **Aider Polyglot** | Repo público GitHub | Refactor multi-lenguaje | MEDIA |

**Quorum 2-de-3:** un modelo es "validado" si AL MENOS 2 de las 4 fuentes lo posicionan en el top-X del dominio. Discrepancias se marcan con `quorum_alcanzado=False` y banda de confianza ancha en el Trono.

**Curadores específicos coding (catastro_curadores entries):**
```yaml
- id: "claude-opus-4.7-coding"
  macroarea: "inteligencia"   # No existe macroarea coding aún (futuro)
  modelo_llm: "claude-opus-4.7"
  proveedor: "anthropic"
  rol: "curador"
  trust_score: 1.00
- id: "gpt-5.5-coding"
  modelo_llm: "gpt-5.5"
  proveedor: "openai"
  rol: "validador"
- id: "deepseek-v4-pro-coding"
  modelo_llm: "deepseek-v4-pro"
  proveedor: "deepseek"
  rol: "validador"
```

3 curadores de 3 proveedores distintos = sin colusión vendor.

## 8. Fuentes y APIs accionables

| Fuente | URL | Cómo se ingiere |
|---|---|---|
| BenchLM | `benchlm.ai/api/v1/benchmarks/...` (verificar) | Usar API o scraping de la página HTML |
| LiveCodeBench | `livecodebench.github.io` | Scraping de la tabla HTML, refresca semanal |
| Artificial Analysis Coding | `artificialanalysis.ai/api/v2/coding` (paywall posible) | Mismo patrón Macroárea 1 |
| Aider Polyglot | `github.com/Aider-AI/aider/blob/main/benchmark.md` | Fetch raw markdown del repo |
| Anthropic Console | `console.anthropic.com/docs/api/models` | Pricing y capacidades |
| OpenAI Models | `platform.openai.com/docs/models` | Pricing y capacidades |
| SWE-bench Multimodal | `github.com/swe-bench/multimodal` | Repo oficial con scores |
| SWE-bench Multilingual | `github.com/swe-bench/multilingual` | Repo oficial con scores por lenguaje |

## 9. Estimación de esfuerzo Sprint 86.5

Asumiendo el patrón endurecido del Sprint 86 (7 bloques) + Opción A elegida:

| Bloque | Trabajo | ETA |
|---|---|---|
| 86.5-B1 | Schema delta + conventions.py + vocabulary.py + tests | 1h |
| 86.5-B2 | Fuente BenchLM (cliente HTTP + parser SWE-bench Verified + tests) | 2h |
| 86.5-B3 | Fuente LiveCodeBench (scraping HTML + cache + tests) | 1.5h |
| 86.5-B4 | Fuente Aider Polyglot (fetch markdown + parse tabla + tests) | 1h |
| 86.5-B5 | Pipeline integration + validador con Quorum 2-de-3 ortogonal coding | 1h |
| 86.5-B6 | Primer run productivo coding + dashboard endpoints específicos | 1h |
| 86.5-B7 | Tests E2E + guía operativa coding + capitulo en CATASTRO_OPERATIONAL_GUIDE | 1h |
| **Total** | | **~8.5h** |

Si Cowork elige **Opción B**, agregar 1.5h al B1 (migración 020 + bump schema + tests adicionales) → total ~10h.

## 10. Riesgos identificados

1. **Benchmaxxing.** Berkeley abril 2026: 8 benchmarks vulnerables. Mitigación: Quorum ortogonal + banda confianza ancha si solo 1 fuente + heurística anti-exploit (sec 4.2).
2. **Cadencia de releases.** Anthropic lanzó Mythos Preview entre 4.7 y 4.6 sin esperar al ciclo. Mitigación: cron diario del Catastro (Sprint 86 Bloque 6) detecta nuevos modelos en 24h.
3. **Pricing volatilidad.** Los precios cambiaron 3 veces en abril 2026 (GPT-5.3 codex bajó 40%, Anthropic subió Sonnet 4.7 25%). Mitigación: campo `precio_input_per_million` + `precio_output_per_million` se versiona en cada evento.
4. **Modelos chinos APIs caóticas.** DeepSeek/Moonshot/Z.AI tienen documentación menos estable que USA. Mitigación: degraded mode con warning si fuente china timeoutea.
5. **Mode-keys explosion.** Si Anthropic agrega "Mythos Adaptive Max High Pro" (4 modos × 5 modelos = 20 entradas), el catastro se infla. Mitigación: regla "solo modos públicos en API, no internos" + agrupación por modelo base en dashboard.
6. **Subscores faltantes.** Muchos modelos solo publican el agregado SWE-bench Verified, no los subscores. Mitigación: `data_extra.swe_bench_subscores` permite parcialmente lleno + heurística anti-exploit usa lo disponible.

## 11. Recomendación al cierre

Sprint 86.5 puede arrancar en cuanto los criterios Cowork se cumplan (Sprint Memento cerrado ✓, bloqueos externos del Hilo Ejecutor cerrados ⏳, primer run real ⏳, 7+ días sin incidentes ⏳, firma Cowork "🟢 GREEN LIGHT SPRINT 86.5" ⏳).

**Próximo paso pendiente del Catastro (este standby):** diseñar el Quorum 2-de-3 multimodal para Macroárea 2 Visión (Sprint 86.6) — siguiente entregable del standby tras este refinamiento.

---

**Capitalización:** este documento es la fuente única de verdad para el diseño del Sprint 86.5. Cualquier consulta sobre "qué modelo poner en Cline" o "qué viene después del bloqueo Ejecutor" debe usarse este documento como base. El Hilo Cowork puede agregar bonus de bonificadores/penalizadores específicos para coding (Re-ranking contextual, deuda Bloque 4) cuando se complete Sprint 86.5.
