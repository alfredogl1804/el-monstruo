# [Hilo Manus Catastro] · Tarea 1 — Lectura obligatoria

**Hilo:** `[Hilo Manus Catastro]`
**Fecha:** 2026-05-04
**Estado:** En progreso

## Documentos leídos y hallazgos clave

### 1. AGENTS.md (raíz del repo) — leído

Estado: **ABSORBIDO**. Las 5 Reglas Duras aplican a todo lo que construya el Sprint 86:

| Regla | Implicación para Sprint 86 (El Catastro) |
|---|---|
| #1: 14 Objetivos aplican a TODO | Todo módulo `kernel/catastro/*` debe pasar el checklist de los 14 Obj. Naming `forja_catastro_*`, errores con identidad, expone datos para Command Center, no inventa rueda (usar Artificial Analysis API antes de scrapear). |
| #2: 7 Capas Transversales obligatorias | El Catastro es infra, pero igual debe servir las 7 capas: motor de ventas (recommend para pricing tools), SEO (modelos para content), publicidad (modelos para creativos), tendencias (radar de modelos = la 4ta capa puro), administración (cost tracking), finanzas (cost_efficiency es columna), resiliencia agéntica (catastro.status anti-fe-ciega). |
| #3: 4 Capas arquitectónicas — orden | Capa 0 (Cimientos) ya está sólida (Magna Classifier + Error Memory + Brand Engine activos). Sprint 86 agrega un cimiento más al stack: el Catastro vive cerca del Brand Engine como meta-validador de elecciones. |
| #4: Brand Engine | El Catastro **debe pasar el bootstrap audit del BrandValidator**. Naming: `forja_catastro_search`, `forja_catastro_recommend`, `forja_catastro_top`, `forja_catastro_status`, `forja_catastro_events`. Errores con formato `catastro_{action}_{failure_type}`. NUNCA `helper`, `service`, `utils`. |
| #5: División de hilos en 3 fases | Estamos en **Fase 1**: Hilo B diseña, Hilo A ejecuta. Pero ahora se diferencian 3 hilos Manus paralelos (Catastro, Credenciales, Producto). Yo soy ejecutor del Sprint 86, no decisor. Cowork dirige. |

### 2. CLAUDE.md (raíz del repo) — leído

Estado: **ABSORBIDO**. Confirmaciones clave:

- El Catastro debe **integrarse al kernel principal** (decisión del addendum), mismo proceso, mismo Supabase, mismo Railway service `el-monstruo-kernel`.
- **Stack vigente al 2026-05-02:** Python/FastAPI + LangGraph (Capa Kernel), Supabase (Postgres + pgvector), Redis. El Catastro hereda este stack.
- **Modelos disponibles ya cableados:** GPT-5.5, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4.20, Kimi K2.5, DeepSeek R1. Esto define los curadores-LLM disponibles para el pipeline diario sin agregar dependencias.
- **Brand DNA:** naranja forja `#F97316` + graphite `#1C1917` + acero `#A8A29E`. El Catastro UI (Sprint 88) debe heredar esta paleta.
- **Reglas críticas del CLAUDE.md:** (1) habla en español, (2) no inventes datos, (3) valida con código, (4) los 14 Objetivos a todo, (5) no pierdas el hilo, (6) consulta los docs.
- **Estado actual al 2026-05:** Kernel `v0.50.0-sprint50` healthy en Railway. **Pero hay datos newer en cierres posteriores:** Sprint 81/81.5/82 → `0.82.0-sprint82`. Sprint 84 productivo. CLAUDE.md está desactualizado, pero AGENTS.md y bridges sí están al día.

### 3. docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md (v2.0, 1-may-2026) — leído

Estado: **ABSORBIDO**. Resumen operativo:

#### Aplicación directa al Sprint 86 — los 14 Objetivos como criterio de éxito

| Obj | Aplicación al Catastro |
|---|---|
| #1 Crear empresas | El Catastro NO es empresa, es infra. Pero **habilita** que el Monstruo cree mejores empresas (eligiendo mejor stack). |
| #2 Apple/Tesla | Cada output de `catastro.recommend()` debe verse como una recomendación de un VC senior, no como un dump de leaderboard. UI Sprint 88 debe ser premium. |
| #3 Mínima complejidad | El usuario (o Cowork) hace UNA llamada y obtiene Top 3 + reasoning. NO 7 dropdowns para configurar pesos. Esto valida la fórmula del Trono fija + re-ranking contextual transparente. |
| #4 No equivocarse 2x | Citation obligatoria es el mecanismo. Si una recomendación falló (ej. modelo deprecated que se coló), el `error_memory` registra la falla y el pipeline diario filtra el modelo. |
| **#5 Magna/Premium** | **EL CATASTRO ES LA MATERIALIZACIÓN DE ESTE OBJETIVO.** Toda data de modelos IA es magna (caduca cada 24h). El Catastro la valida en tiempo real. Sin Catastro, el Obj #5 está parcialmente cubierto solo por web_search. Con Catastro, está blindado. |
| **#6 Vanguardia perpetua** | El pipeline diario del Catastro **es** el escáner de vanguardia para el dominio modelos/tools IA. Embrión-Vigía (futuro) consume `catastro.events()`. |
| #7 No inventar rueda | Antes de scrapear, usar Artificial Analysis API si la exponen. Antes de calcular Elo, usar el de LMArena. Solo derivar lo que no se publica (BrandFit, Sovereignty, Velocity). |
| #8 Inteligencia emergente | Si `catastro.events()` detecta drift entre 3+ fuentes, eso es señal emergente — Embrión-Vigía actúa. |
| #9 Transversalidad | El Catastro es **transversal a las 7 capas**: cualquier capa que necesite un modelo o herramienta IA pasa por aquí. |
| #10 Simulador causal | El histórico (`catastro_historial`) es input para el Simulador: "¿qué pasa si Anthropic sube precios 30%?" — el Simulador re-rankea. |
| #11 Embriones | Cada Embrión especializado consultará al Catastro para elegir su modelo óptimo. Embrión-Creativo → Visión gen. Embrión-Técnico → Coding LLMs. |
| #12 Soberanía | Tracking de `open_weights=true` en el schema. El Catastro mide cuánto del stack es soberano vs vendor-lock-in. **Métrica del Catastro mismo: % de modelos open-weight en Top 3 por dominio.** |
| #13 Del mundo | Cuando se libere El Monstruo, el Catastro es el bien público más útil — todos los emprendedores tienen el mismo acceso a ranking objetivo. |
| **#14 Guardian de los objetivos** | El Catastro **alimenta** al Guardian: el Obj #6 (Vanguardia) se mide con `edad_promedio_stack vs catastro.last_validated_at`. El Obj #12 (Soberanía) se mide con `% de modelos open en Top 3`. |

#### Conclusión Tarea 1 hasta aquí

El Catastro no es "un módulo más". Es la **infraestructura que materializa los Obj #5, #6 y #14** y que **alimenta al Embrión-Vigía y al Guardián**. Sprint 86 es Cimientos de un sistema que sostiene 3 objetivos del Maestro 14.

### 4. Pendientes de leer (siguientes en cola)

- `docs/BRAND_ENGINE_ESTRATEGIA.md` — para verificar naming + paleta + tono que el Catastro debe heredar
- `docs/ROADMAP_EJECUCION_DEFINITIVO.md` — para confirmar que Sprint 86 está en la posición correcta de la 4-Capa
- `docs/DIVISION_RESPONSABILIDADES_HILOS.md` — para refinar mi rol exacto
- `bridge/cowork_to_manus.md` líneas 4190-4672 (SPEC SPRINT 86 + ADDENDUM) — ya extraído mentalmente, falta escribir resumen formal
- Diseño Maestro Drive `1FVgZU9FeC0pGYOGuOePxy3c8DCGcYIdb` — descargar y leer

Continúo con BRAND_ENGINE_ESTRATEGIA y luego bajo el Diseño Maestro de Drive.

— [Hilo Manus Catastro]


---

## 5. Brand Engine Estrategia (docs/BRAND_ENGINE_ESTRATEGIA.md) — leído

Estado: **ABSORBIDO**.

Implicaciones directas para el Sprint 86:

| Componente del Brand Engine | Cómo aplica al Catastro |
|---|---|
| **Brand DNA** ya implementado en `kernel/brand/brand_dna.py` (Sprint 82) | El módulo `kernel/catastro/*` debe importar `from kernel.brand import BRAND_DNA, BrandValidator` y validar nombres antes de instanciar. |
| **Naming convention** "Forja, Guardián, Colmena, Simulador" | El Catastro adopta naming propio: `forja_catastro_search`, `forja_catastro_recommend`, `forja_catastro_top_n`, `forja_catastro_status`, `forja_catastro_events`. La palabra clave es "forja" (módulo principal del Brand Engine). |
| **Errores con identidad** formato `{module}_{action}_{failure_type}` | `catastro_scrape_timeout`, `catastro_validate_quorum_failure`, `catastro_rerank_invalid_weights`, `catastro_mcp_unauthorized`. NUNCA `internal server error`. |
| **Anti-patrones** | El UI del Catastro (Sprint 88) NO se ve como Grafana ni Datadog. Brutalismo industrial: tablero negro graphite con highlights naranja forja. |
| **BrandValidator bootstrap audit** | El Catastro debe pasar el audit hook automáticamente con score >= 60 en avg. Las 5 tools MCP propuestas pasan diseño preliminar. |
| **BrandDNA.app + BrandVox AI** (Fase 3 futura) | El Catastro mismo puede ser un dato fuente para benchmark competitivo cuando el Monstruo se libere. |

## 6. SPEC SPRINT 86 + ADDENDUM (bridge/cowork_to_manus.md líneas 4190-4672) — leído

Estado: **ABSORBIDO**. Resumen del scope obligatorio:

### Alcance del Sprint 86 (vs los 6 sprints internos del Diseño Maestro)

El Sprint 86 NO ejecuta los 6 sprints internos completos. Es solo **Sprint 1-2 del Diseño Maestro** (Cimientos + 4 Curadores prioritarios) más el MCP server básico.

| Tarea Sprint 86 | Mapeo a Diseño Maestro | Estado |
|---|---|---|
| Schema Supabase 3 tablas | Sec 7 (catastro_modelos, catastro_historial, catastro_eventos) | Pendiente |
| Scraper Artificial Analysis (LLMs + Visión) | Sec 5 fuente primaria #1 | Pendiente |
| Scraper LMArena | Sec 5 fuente primaria #2 | Pendiente |
| Scraper HF Open LLM Leaderboard | Sec 5 fuente primaria #3 | Pendiente |
| 4 Curadores: Inteligencia, Visión, Video, Voz/Avatares | Sec 9 (Curador Inteligencia, Visión, Video, Voz) | Pendiente |
| Pipeline diario base (sin todos los pasos) | Sec 6 pasos 1-5 (sin notificación Telegram completa) | Pendiente |
| Trono Score implementado | Sec 4 fórmula `0.40*Q + 0.25*CE + 0.15*S + 0.10*R + 0.10*BF` | Pendiente |
| Detección de eventos (cambio Top 3, deprecation) | Sec 6 paso 6 | Pendiente |
| 5 tools MCP server | Sec 7 (`search`, `get_top`, `recommend`, `compare`, `changes_since`) — el Diseño Maestro tiene 6 tools, addendum optimiza a 5 | Pendiente |
| Seed inicial 80-105 modelos | Sec 10 Sprint 1 menciona "~200 modelos catalogados" — addendum reduce a 80-105 para Sprint 86 (más realista) | Pendiente |
| Tests: 30 unit + 5 integration | (no en Diseño Maestro, requisito del SPEC) | Pendiente |
| Bootstrap audit Brand Engine: avg score >= 60 | Heredado del Sprint 82 | Pendiente |

### Mejoras que el ADDENDUM incorpora del feedback de Cowork (vs Diseño Maestro v1)

1. **Anti-alucinación Quorum 2-de-3** (no estaba en v1) — para validar precios/métricas, requerir cuórum entre 3 fuentes independientes. Refinamiento mío: implementar como `kernel/catastro/quorum_validator.py`.
2. **Trust Score por curador-LLM** (no estaba en v1) — cada curador acumula score histórico de aciertos/fallos. Si Trust Score < 0.7 sus updates van a HITL.
3. **Re-ranking contextual matemático** (v1 era textual: "ponderación dinámica") — addendum exige fórmula explícita con bonificadores por subcapacidad y penalizadores por limitación.
4. **Schema MCP exacto** (v1 listaba 6 tools sin params) — addendum exige params, retorno y ejemplos por cada tool.
5. **5 dominios críticos faltantes** (no estaban en v1):
   - Embeddings (estaba como subcategoría, ahora es dominio propio)
   - Code-execution / sandboxes (E2B, Modal, Daytona, RunComfy)
   - Guardrails / safety (LlamaGuard, NeMo Guardrails, Promptfoo)
   - Edge inference (Cerebras, Groq, SambaNova hardware)
   - Data labeling AI (Scale AI, Surge, Labelbox AI)

## 7. Comprensión del rol del Hilo Manus Catastro

Estado: **CLARO**.

Mi rol en Sprint 86:
- **No diseño**, ejecuto. El diseño es de Cowork (con feedback mío durante implementación).
- **No toco credenciales**, eso lo maneja `[Hilo Manus Credenciales]` (paralelo).
- **No toco Sprint 85**, eso lo maneja `[Hilo Manus Producto]` o el cierre va por Cowork.
- **Mi sandbox de trabajo**: `bridge/sprint86_preinvestigation/` (pre-investigación), `kernel/catastro/` (cuando arranque), `scripts/016_sprint86_catastro.sql` (migración), `tests/test_catastro_*.py` (tests).
- **Reporto cierres** en `bridge/manus_to_cowork.md` con prefijo `[Hilo Manus Catastro] · <subsección>`.
- **Espero directiva explícita de Cowork** antes de tocar producción.

## Conclusión Tarea 1

Tarea 1 **COMPLETADA**. Tengo absorbido:

1. AGENTS.md (5 reglas duras + checklist de Brand Compliance)
2. CLAUDE.md (stack, modelos, arquitectura kernel)
3. 14 Objetivos Maestros v2.0 (con Obj #14 Guardian)
4. Brand Engine Estrategia (DNA, naming, anti-patrones)
5. Diseño Maestro El Catastro v1.0 (las 13 secciones)
6. SPEC SPRINT 86 + ADDENDUM (scope ejecutable, mejoras anti-alucinación)
7. Mi rol como `[Hilo Manus Catastro]` y división de hilos

Avanzo a Tarea 2: Pre-investigación de fuentes de scraping.

— [Hilo Manus Catastro]
