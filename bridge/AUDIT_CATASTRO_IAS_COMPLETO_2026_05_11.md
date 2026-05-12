---
id: AUDIT_CATASTRO_IAS_COMPLETO_2026_05_11
fecha: 2026-05-11
emisor: Hilo Catastro (Manus B / Ejecutor Técnico)
proposito: Cruzar el plan ORIGINAL del catastro de IAs (DSC-G-007 v1.1 + DSC-MO-009 + 8 specs sprint 86-89) contra el ESTADO REAL HOY para identificar todos los ángulos que mi propuesta CATASTRO-C anterior dejaba fuera.
metodologia: Lectura binaria de DSCs + grep en código + queries reales contra Supabase prod via Railway env + curl al kernel vivo.
firma: NO declarado verde — sólo audit. Las decisiones las toma Cowork/Alfredo.
---

# Audit completo del Plan Catastro de IAs vs Estado Real

## TL;DR

El plan original del **Catastro de IAs** es mucho más ambicioso de lo que mi propuesta CATASTRO-C cubría. La doctrina firmada (DSC-G-007 v1.1) declara **4 catastros paralelos** + un sistema de fuentes múltiples con quorum + **5 macroáreas pobladas o planeadas** + radar GitHub absorbido + tronos calibrados por sabios. Hoy hay **3 macroáreas pobladas** (inteligencia, agentes, vision_generativa), **2 macroáreas más con spec firmado pero sin ejecutar** (LLM Coding, Razonamiento Estructurado), y **5 fuentes API ausentes** + **el radar 0 ejecuciones** + **catastros JSON standalone sin wire-up al engine**.

Mi propuesta CATASTRO-C anterior se quedaba en wire-up + radar + Sprint 89. **Faltaban 4 ángulos completos del plan original.**

---

## 1. Plan original mapeado (qué declaran las DSCs)

### DSC-G-007 v1.1 — Cuatro Catastros Paralelos

| # | Catastro | Estado declarado | Cantidad inicial planeada |
|---|---|---|---|
| 1 | **Modelos LLM** | Madura, pipeline completo, dashboard | 50+ modelos |
| 2 | **Agentes 2026** | NUEVO en v1.1 (gap detectado por Manus) | 21 biblias canónicas |
| 3 | **Herramientas AI Verticales** | Catalogadas vía CATASTRO-A | 16-25 fresh |
| 4 | **Suppliers Humanos** | Catalogadas vía CATASTRO-A | 30+ entries Sureste MX |

### DSC-MO-009 — Arsenal seleccionable por Catastro (embrión consume)

Embrión bicéfalo opera con arsenal de herramientas externas seleccionadas por catastro. **Pre-requisito explícito:** Sprint 88 macroárea AGENTES (HECHO). **Pre-requisito implícito:** Sprint EMBRION-NEEDS-002 (integrar consulta al catastro extendido en flujo de decisión del embrión) — **NO ejecutado**.

### DSC-G-007.2 + DSC-G-007.5 — Macroáreas pobladas

| Macroárea | DSC | Sprint | Productos | Tronos | Estado |
|---|---|---|---|---|---|
| `inteligencia` | G-007 | Sprint 86 | 41 modelos | 4 dominios | ✅ Maduro |
| `agentes` | G-007.2 | Sprint 88 | 98 productos (12 dominios) | 12 tronos | ✅ Calibrado por 4 sabios |
| `vision_generativa` | G-007.5 | Sprint 88.3 | 38 productos | 12 tronos | ✅ Validado vs Perplexity |
| `llm_coding` | (spec) | Sprint 86.5 propuesto | — | — | 🟡 Spec firmado, no ejecutado |
| `razonamiento_estructurado` | (spec) | Sprint 86.7 propuesto | — | — | 🟡 Spec firmado, no ejecutado |

### Specs adicionales del plan que NO mapeaba

| Spec | Path | Decisión |
|---|---|---|
| Integración Radar↔Catastro | `bridge/sprint86_5_preinvestigation/spec_integracion_radar_catastro.md` | Sexta tabla `catastro_repos` + cliente `radar_ingest.py` con LLM-as-parser + 2 eventos automáticos |
| Pre-investigación fuentes | `bridge/sprint86_preinvestigation/[Hilo Manus Catastro]_02_pre_investigacion_fuentes.md` | 6 de 8 fuentes son APIs REST oficiales — **5 clientes faltan** (replicate, fal, together, huggingface_hub, benchlm) |
| Confidentiality tier | `bridge/sprint_86_8_preinvestigation/spec_catastro_confidentiality_tier.md` | Sprint 86.8 — clasificar productos por tier de confidencialidad |
| Sprint 89 CatastroBase genérica | `bridge/sprints_propuestos/sprint_89_catastros_extension_suppliers_herramientas_ai.md` | Refactor a `Generic[T]` + wire-up engine + credential_resolver |

---

## 2. Estado REAL hoy (verificado binariamente)

### 2.1 Kernel vivo (HTTP 200, uptime 13min al momento del audit)

```
version: 0.84.8-sprint-memento
componentes activos: 14/15 (mcp inactive)
embrion_loop: running, cycle 12, thoughts_today 2, cost $0.057
radar: cycles_since=12, total_checks=0, last_at=null
sabios: cycles_since=12, total_consultations=0, last_at=null
```

### 2.2 Supabase prod — Catastros pobladas

```
catastro_modelos: 41 productos
catastro_agentes: 98 productos
catastro_vision_generativa: 38 productos
catastro_eventos: 148 eventos (todos tipo 'new_model', curador_origen=NULL en todos)
catastro_repos: ❌ NO EXISTE LA TABLA
embrion_radar_checks: ❌ NO EXISTE LA TABLA
vanguard_discoveries: ❌ NO EXISTE LA TABLA
```

### 2.3 Sources implementadas en `kernel/catastro/sources/`

| Source | Estado | LOC |
|---|---|---|
| artificial_analysis | ✅ | 250 |
| lmarena | ✅ | 322 |
| openrouter | ✅ | 296 |
| aime, gpqa, mmlu_pro, mbpp, human_eval, swe_bench | ✅ benchmarks | 95-133 cada uno |
| **replicate** | ❌ **MISSING** | — |
| **fal** | ❌ **MISSING** | — |
| **together** | ❌ **MISSING** | — |
| **huggingface_hub** | ❌ **MISSING** | — |
| **benchlm** | ❌ **MISSING** | — |
| **radar_ingest** | ❌ **MISSING** | — |

### 2.4 Catastros JSON standalone (CATASTRO-A v2)

```
kernel/catastro/data/catastro_agentes.json     17 KB (21 entries históricos)
kernel/catastro/data/catastro_tools.json       12 KB (24 entries)
kernel/catastro/data/catastro_suppliers.json   21 KB (36 entries)
```

**Wire-up al engine: 0 referencias.** Ni `kernel/main.py` ni `engine.py` consume estos JSONs.

### 2.5 CatastroBase genérica

```
kernel/catastro_base.py: ❌ NO EXISTE
kernel/security/credential_resolver.py: ❌ NO EXISTE (solo input_guard.py)
kernel/security/env_validator.py: ❌ NO EXISTE
```

### 2.6 Radar (agents_radar.py)

- **Tool existe** `tools/agents_radar.py` (Sprint 45, MCP cliente)
- **Embrión tiene** `_check_agents_radar()` en `kernel/embrion_loop.py:2104`
- **Vanguard tiene** `intelligence_engine.run_daily_scan()` en línea 271
- **`run_daily_scan()` invocaciones reales fuera de tests: 0**
- **Embrión `total_checks` en prod: 0** (en runtime actual; no hay tabla histórica para confirmar otros runs)
- **`embrion_memoria` tipo `radar_check`: 0 entries en 1842 totales**

### 2.7 DSC-V-001 — 6 Sabios canónicos

Doctrina declara 6 (8) sabios verificados. Embrión `total_consultations: 0` en runtime actual. La consulta a sabios para validación adversarial Tier 1 (44 productos) está **diferida** según DSC-G-007.2.

---

## 3. Cruce: Gaps por ángulo del plan original

### Ángulo A — Catastro Modelos LLM (Sprint 86)

**Cubierto:** ✅ pipeline 8-pasos, quorum 2-de-3, trono z-scores, dashboard, 3 sources (AA, LMArena, OpenRouter), 6 benchmarks (AIME/GPQA/MMLU-Pro/MBPP/HumanEval/SWE-Bench).

**Gaps:**
- 5 fuentes API del plan original NO implementadas (Replicate, FAL.ai, Together.ai, HuggingFace Hub leaderboards, BenchLM)
- 5 credenciales NUEVAS NO solicitadas a Alfredo (`REPLICATE_API_TOKEN`, `FAL_API_KEY`, `TOGETHER_API_KEY`, `HF_TOKEN`, `ARTIFICIAL_ANALYSIS_API_KEY` quizá ya esté pero no verificado)
- Solo 41 modelos catalogados vs el target de 50+

### Ángulo B — Catastro Agentes 2026 (Sprint 88)

**Cubierto:** ✅ 98 productos, 12 dominios, tronos calibrados con consenso de 4 sabios, schema Pydantic completo.

**Gaps:**
- 21 biblias en `docs/biblias_agentes_2026/` — **refinement de fidelidad media** (la biblia de Manus v3 tiene ~70% completitud según handoff, falta profundizar)
- Validación adversarial 3 sabios sobre 44 productos Tier 1 — **diferida** (DSC-G-007.2 Risks)
- Wire-up con embrión (consulta al catastro): solo dispatcher manual en `kernel/external_agents.py`

### Ángulo C — Catastro Herramientas AI + Suppliers (CATASTRO-A v2)

**Cubierto:** ✅ JSONs poblados (24 tools + 36 suppliers).

**Gaps:**
- **`CatastroBase` genérica NO existe** (Sprint 89 propuesto, no ejecutado)
- **Wire-up engine 0** — los JSONs están huérfanos
- **`credential_resolver.py` fail-loud NO existe**
- **`env_validator.py` startup NO existe**
- Falta tabla SQL espejo (los datos viven solo en JSON, no en Supabase)

### Ángulo D — Radar GitHub/AI (Sprint 45 + Sprint 86.5 spec)

**Cubierto:** ✅ Tool `tools/agents_radar.py` existe con 7 report types, 10 fuentes.

**Gaps:**
- **Tabla `catastro_repos` NO existe** (sexta tabla del Sprint 86.5 — diferida)
- **Cliente `kernel/catastro/sources/radar_ingest.py` NO existe** (con LLM-as-parser)
- **2 eventos automáticos NO conectados** (`new_open_source_model_detected`, `open_source_release_v2`)
- **0 ejecuciones** del radar en runtime actual (P0 documentado por Cowork)
- `vanguard_discoveries` table NO existe a pesar de que `intelligence_engine.py` la asume

### Ángulo E — Macroárea LLM Coding (Sprint 86.5 spec)

**Cubierto:** Spec firmado en `bridge/sprint86_5_preinvestigation/macroarea_3_llm_coding.md`.

**Gaps:**
- 4 dominios (`coding-agent`, `coding-completion`, `coding-refactor`, `coding-debug`) NO en enum
- Quorum entre BenchLM/LiveCodeBench/AA Coding/Aider Polyglot NO configurado
- Top-15 modelos coding NO catalogados

### Ángulo F — Macroárea Razonamiento Estructurado (Sprint 86.7 spec)

**Cubierto:** Spec firmado, audit Cowork sprint 86.7 indica que classifier YA fue ejecutado (31/31 tests).

**Gaps a verificar:**
- ¿Tag `reasoning-overfit-suspected` activo en producción?
- ¿Macroárea como tal en enum `Macroarea`? **NO** (sólo INTELIGENCIA, AGENTES, VISION_GENERATIVA en código)
- Anti-gaming v2 cross-area NO confirmado

### Ángulo G — Confidentiality Tier (Sprint 86.8 spec)

**Cubierto:** Spec firmado en `bridge/sprint_86_8_preinvestigation/spec_catastro_confidentiality_tier.md`. Migración `027_sprint86_8_assign_confidentiality_tiers.sql` aplicada.

**Gap:** Verificar si los 173 productos tienen tier asignado y si el embrión consume este tier para decisiones HITL.

### Ángulo H — Wire-up Embrión↔Catastro (DSC-MO-009)

**Cubierto:** Hooks en `embrion_loop.py` (`_check_agents_radar`, sabios consult).

**Gaps:**
- **Sprint EMBRION-NEEDS-002 NO ejecutado** (consulta al catastro extendido en flujo de decisión)
- Embrión NO consulta `/v1/catastro/recommend` antes de elegir LLM
- `external_agents.py` dispatcher es manual, no consulta `catastro_agentes`

---

## 4. Resumen de gaps clasificados por prioridad

### P0 (bloquean visión "El Monstruo decide qué herramienta usar")
1. **Wire-up engine ↔ 3 catastros JSON standalone** (agentes/tools/suppliers) — Sprint 89 Tarea 4
2. **CatastroBase genérica** — Sprint 89 Tarea 1
3. **credential_resolver + env_validator** — Sprint 89 Tarea 3

### P1 (bloquean autonomía y descubrimiento)
4. **Activar radar (run_daily_scan + cron)** — sin esto el embrión no descubre nada nuevo
5. **Tabla `catastro_repos` + cliente `radar_ingest.py`** — Sprint 86.5 spec
6. **Sprint EMBRION-NEEDS-002** — embrión consume catastro

### P2 (completan cobertura del catálogo)
7. **5 fuentes faltantes** (Replicate, FAL, Together, HF Hub, BenchLM)
8. **Macroárea LLM Coding** — Sprint 86.5 spec
9. **Macroárea Razonamiento Estructurado en enum** (verificar)
10. **Refinement biblias agentes** (CATASTRO-A v2 deuda)

### P3 (calidad y validación)
11. **Validación adversarial 3 sabios sobre 44 productos Tier 1** (diferido DSC-G-007.2)
12. **Confidentiality tier consumo por embrión** (verificar)

---

## 5. Mi propuesta CATASTRO-C anterior cubría sólo

- ✅ P0.1, P0.2, P0.3 (Sprint 89 = wire-up + base + resolver)
- ✅ P1.4 (activar radar)

**Dejaba fuera:**
- ❌ P1.5 (tabla `catastro_repos` + cliente radar_ingest con LLM parser)
- ❌ P1.6 (Sprint EMBRION-NEEDS-002)
- ❌ P2.7-10 (5 fuentes + 2 macroáreas + biblias)
- ❌ P3.11-12 (validación sabios + tier consumo)

---

**FIN AUDIT** — emitido por Hilo Catastro a Cowork/Alfredo. Sin firma de cierre. Insumo para decidir el alcance real del próximo sprint.
