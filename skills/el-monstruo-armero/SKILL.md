---
name: el-monstruo-armero
description: Arsenal futuro pre-investigado para construir El Monstruo. Contiene TODAS las herramientas, frameworks, APIs y configuraciones que se necesitarán cuando se construya el Monstruo real (Sprint 1+). Cada herramienta fue investigada en tiempo real, benchmarkeada, y tiene configuración lista para inyectar vía secrets. Este skill es el "armero" — prepara las armas ANTES de la batalla. Usar cuando se vaya a construir El Monstruo de verdad.
---

# El Monstruo Armero v1.0 — Arsenal Futuro Pre-Investigado

**Propósito:** Este skill NO es para el bot actual (eso es `el-monstruo-toolkit`). Este skill prepara TODAS las herramientas que El Monstruo necesitará cuando se construya de verdad. Cada herramienta fue investigada en tiempo real (abril 2026), benchmarkeada contra alternativas, y tiene configuración lista para inyectar.

**Cuándo activar:** Cuando se vaya a construir El Monstruo real (Sprint 1 en adelante).

## Decisión Rápida

1. **Voy a construir el kernel** → `references/build_stack/langgraph.yaml`
2. **Voy a conectar los 6 cerebros** → `references/build_stack/litellm.yaml`
3. **Voy a implementar memoria** → `references/build_stack/mem0_memory.yaml`
4. **Necesito observabilidad** → `references/build_stack/langfuse.yaml`
5. **Necesito embeddings** → `references/embeddings/embedding_models.yaml`
6. **Necesito web scraping** → `references/build_stack/firecrawl.yaml`
7. **Necesito la consola web** → `references/build_stack/console_web.yaml`
8. **Herramientas complementarias** → `references/build_stack/complementary_tools.yaml`
9. **Quiero el esqueleto completo** → `templates/sprint1/architecture_skeleton.py`
10. **Necesito las env vars** → `templates/sprint1/env_template.yaml`
11. **Necesito las dependencias** → `templates/sprint1/requirements.txt`
12. **Necesito inyectar secrets** → Sección 4 (Inyección vía api-context-injector)

## 1. Mapa del Arsenal Completo

### Core Stack (Sprint 1 — Obligatorio)

| Herramienta | Versión | Archivo Config | Rol | Costo | Licencia |
|------------|---------|----------------|-----|-------|----------|
| LangGraph | 1.1.6 | `build_stack/langgraph.yaml` | Kernel de orquestación (grafo dirigido con checkpointing) | Gratis | MIT |
| LiteLLM | 1.83.3 (ANCLAR) | `build_stack/litellm.yaml` | Router unificado para 6+ cerebros con fallbacks | Gratis | MIT |
| Mem0 OSS | latest | `build_stack/mem0_memory.yaml` | Memoria persistente con Supabase pgvector | Gratis | Apache-2.0 |
| Langfuse | latest | `build_stack/langfuse.yaml` | Observabilidad: tracing, cost tracking, evaluaciones | Gratis (free tier) | MIT |
| Supabase pgvector | 0.8.2 | `build_stack/mem0_memory.yaml` | Vector store + PostgreSQL + Auth | Ya pagado | — |

### Embeddings (Sprint 1 — Elegir uno)

| Modelo | Archivo Config | Benchmark MTEB | Costo | Mejor Para |
|--------|----------------|---------------|-------|-----------|
| text-embedding-3-small | `embeddings/embedding_models.yaml` | 62.3 | $0.02/1M | Actual, funciona bien |
| Gemini Embedding 002 | `embeddings/embedding_models.yaml` | 68.7 | **Gratis** | #1 cross-lingual, upgrade recomendado |
| Cohere Rerank 4 Pro | `embeddings/embedding_models.yaml` | — | **Gratis** | Post-retrieval reranking, 100+ idiomas |
| Qwen3-VL-2B | `embeddings/embedding_models.yaml` | 66.5 | **Gratis** (OpenRouter) | Cross-modal (texto+imagen) |

### Web Scraping / RAG Pipeline (Sprint 1)

| Herramienta | Archivo Config | Rol | Costo |
|------------|----------------|-----|-------|
| Firecrawl | `build_stack/firecrawl.yaml` | Scraping → Markdown → LLM-ready | 500 credits gratis |
| Crawl4AI | `build_stack/complementary_tools.yaml` | Fallback OSS, async, sin API key | Gratis (Apache-2.0) |

### Consola Web (Sprint 1)

| Herramienta | Archivo Config | Rol | Costo |
|------------|----------------|-----|-------|
| Next.js 16 + shadcn/ui | `build_stack/console_web.yaml` | PWA con streaming | Gratis (Vercel) |
| Vercel AI SDK 7.0 | `build_stack/console_web.yaml` | Streaming + tool calling | Gratis |

### Arsenal Sprint 2+ (Pre-investigado)

| Herramienta | Archivo Config | Rol | Costo |
|------------|----------------|-----|-------|
| Composio | `build_stack/complementary_tools.yaml` | 850+ app integrations (Slack, Salesforce, etc.) | Free tier |
| DuckDB | `build_stack/complementary_tools.yaml` | Analytics local, SQL sobre CSV/JSON/Parquet | Gratis (MIT) |
| Playwright MCP | `build_stack/complementary_tools.yaml` | Browser automation para agentes | Gratis |
| Galileo Agent Control | `build_stack/complementary_tools.yaml` | Governance layer, policy-as-code | Gratis (Apache-2.0) |

## 2. Alertas de Seguridad Críticas

### LiteLLM — Supply Chain Attack (marzo 2026)

**CVE-2026-35030**: Versiones 1.82.7 y 1.82.8 comprometidas por grupo TeamPCP. Roban credenciales de API keys.

**Vulnerabilidades adicionales corregidas en v1.83.0+ (abril 2026):**
- CVE-2026-35029 (High): Privilege escalation via /config/update — requiere API key válida
- GHSA-69x8-hrgq-fjj8 (High): Password hash exposure — requiere API key válida
- LiteLLM lanzó bug bounty program (hasta $3,000 por vulnerabilidades críticas)

**Acciones obligatorias:**
1. ANCLAR `litellm==1.83.3` en requirements.txt
2. Verificar hash post-instalación: `pip hash litellm`
3. Configurar Dependabot en el repo
4. NUNCA usar `>=` para LiteLLM
5. Si usas JWT auth, verificar que estés en v1.83.0+

→ Detalles completos en `build_stack/litellm.yaml`

### Mem0 — Bug #4596

El método `.single()` falla silenciosamente en ciertas queries. Usar `.execute()` o REST directo como workaround.

→ Detalles en `build_stack/mem0_memory.yaml`

## 3. Templates Sprint 1 — Listos para Copiar

### Architecture Skeleton (`templates/sprint1/architecture_skeleton.py`)

Grafo LangGraph completo de 357 líneas con:
- 6 cerebros configurados (GPT-5.4, Claude, Gemini, Grok, DeepSeek, Perplexity)
- Clasificador de intención
- Router con fallbacks automáticos
- Integración Mem0 para memoria persistente
- Callbacks Langfuse para observabilidad
- 4 modos operativos (chat, deep_think, execute, background)

### Requirements (`templates/sprint1/requirements.txt`)

Todas las dependencias con versiones ancladas. LiteLLM forzada a 1.83.3.

### Environment Variables (`templates/sprint1/env_template.yaml`)

18 variables organizadas en 3 categorías:
- **7 obligatorias** (cerebros): OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, XAI_API_KEY, OPENROUTER_API_KEY, SONAR_API_KEY, ELEVENLABS_API_KEY
- **6 Sprint 1 nuevas** (crear): SUPABASE_URL, SUPABASE_SERVICE_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, MEM0_API_KEY, TELEGRAM_BOT_TOKEN
- **5 opcionales**: HEYGEN_API_KEY, DROPBOX_API_KEY, CLOUDFLARE_API_TOKEN, FIRECRAWL_API_KEY, COMPOSIO_API_KEY

## 4. Inyección de Secrets vía api-context-injector

Cuando llegue el momento de construir, los secrets se inyectan así:

```bash
# 1. Detectar scaffold del proyecto
python3.11 /home/ubuntu/skills/api-context-injector/scripts/inject_secrets.py \
    --detect /path/to/monstruo-v2

# 2. Generar manifiesto automático
python3.11 /home/ubuntu/skills/api-context-injector/scripts/inject_secrets.py \
    --generate-manifest /path/to/monstruo-v2

# 3. Dry run (simular sin tocar nada)
python3.11 /home/ubuntu/skills/api-context-injector/scripts/inject_secrets.py \
    --project /path/to/monstruo-v2 --target sandbox --dry-run

# 4. Inyectar de verdad
python3.11 /home/ubuntu/skills/api-context-injector/scripts/inject_secrets.py \
    --project /path/to/monstruo-v2 --target sandbox

# 5. Auditar post-inyección
python3.11 /home/ubuntu/skills/api-context-injector/scripts/inject_secrets.py \
    --audit /path/to/monstruo-v2
```

Para deploy en producción, cambiar `--target`:
- `--target vercel` → Push encrypted a Vercel
- `--target railway` → Configurar en Railway
- `--target cloudflare` → wrangler secret put

## 5. Checklist de Pre-Vuelo (NUEVO)

Antes de arrancar Sprint 1, ejecutar el checklist de pre-vuelo:

```bash
python3.11 /home/ubuntu/skills/el-monstruo-armero/scripts/preflight_check.py \
    --output preflight_report.json
```

Verifica 7 categorías: secrets (18 vars), packages (12 deps), APIs (6 cerebros), Supabase, servicios externos, integridad del armero (13 archivos), y seguridad. Genera reporte JSON con pass/fail/warn.

Opciones: `--fix` (intenta corregir automáticamente), `--target railway` (verificar entorno Railway).

## 6. Flujo de Construcción Recomendado

```
Día 1: Kernel + Router
  → Copiar architecture_skeleton.py
  → Instalar requirements.txt
  → Configurar env vars desde env_template.yaml
  → Inyectar secrets vía api-context-injector
  → Implementar grafo LangGraph (build_stack/langgraph.yaml)
  → Configurar LiteLLM router (build_stack/litellm.yaml)

Día 2: Memoria + Estado
  → Crear tablas en Supabase (SQL en build_stack/mem0_memory.yaml)
  → Configurar Mem0 con pgvector
  → Implementar 4 buckets de memoria

Día 3: Consola + Observabilidad
  → Scaffold Next.js 16 (build_stack/console_web.yaml)
  → Integrar Langfuse (3 líneas — build_stack/langfuse.yaml)
  → Deploy consola en Vercel

Día 4: Integración + Testing
  → Conectar Telegram → Kernel
  → 3 casos de prueba end-to-end
  → Verificar observabilidad en Langfuse dashboard
```

## 7. Cada Archivo YAML Contiene

Todos los archivos en `references/build_stack/` siguen la misma estructura:

1. **Por qué se eligió** — con datos de benchmark y comparación
2. **Configuración exacta** — YAML/Python copy-paste para El Monstruo
3. **Código de integración** — snippets listos
4. **Alternativas evaluadas** — qué se descartó y por qué
5. **Alertas de seguridad** — si aplican
6. **En qué Sprint se necesita** — priorización clara

## 8. Diferencia con Otros Skills del Monstruo

| Skill | Propósito | Cuándo usar |
|-------|-----------|-------------|
| `el-monstruo` | Contexto del corpus (SOP, EPIA, MAOC, gobernanza) | Decisiones operativas |
| `el-monstruo-plan` | Blueprint Sprint 1 (4 días, arquitectura, 19 capas) | Planificación |
| `el-monstruo-bot` | Bot actual en producción (Railway, Telegram) | Modificar/desplegar bot |
| `el-monstruo-toolkit` | Configs del bot actual (cerebros, secrets, MCPs) | Operar bot actual |
| **`el-monstruo-armero`** | **Arsenal FUTURO pre-investigado (herramientas, configs, secrets)** | **Construir El Monstruo real** |

## Reglas Inquebrantables

1. **SIEMPRE** anclar `litellm==1.83.3` (CVE-2026-35030)
2. **SIEMPRE** verificar hash de LiteLLM post-instalación
3. **SIEMPRE** usar Mem0 `.execute()` no `.single()` (bug #4596)
4. **SIEMPRE** crear índice HNSW en pgvector antes de queries
5. **SIEMPRE** inyectar secrets vía api-context-injector, NUNCA hardcodear
6. **NUNCA** exponer SUPABASE_SERVICE_KEY en frontend
7. **NUNCA** usar LiteLLM sin anclar versión exacta
8. **SIEMPRE** consultar `el-monstruo-plan` para el blueprint antes de construir
9. **SIEMPRE** consultar `el-monstruo-toolkit` para el estado actual del bot

## 9. Modelos en Monitoreo

| Modelo | Estado | Impacto Potencial | Acción |
|--------|--------|-------------------|--------|
| Claude Mythos Preview | Private preview (40 empresas) | Posible upgrade de Claude en el Monstruo | Monitorear disponibilidad pública |
| Gemini 3.1 Flash Lite | Preview | Alternativa económica para tareas simples | Evaluar cuando sea GA |

> **Nota (9 abril 2026):** Claude Mythos es el modelo más poderoso de Anthropic pero NO está disponible públicamente. Anthropic lo considera "demasiado poderoso" para lanzamiento general. Solo disponible para consorcio de cybersecurity. Cuando se abra acceso, evaluar como upgrade del sabio Claude.

## Metadata

```yaml
version: "1.1"
last_verified: "2026-04-09"
ttl_days: 30
research_date: "2026-04-09"
research_sources:
  - OpenRouter API (modelos y precios en tiempo real)
  - GitHub (repos oficiales de cada herramienta)
  - Dev.to (benchmark embeddings abril 2026)
  - GuruSup (comparativa frameworks multi-agente 2026)
  - CVE databases (alertas de seguridad)
depends_on:
  - api-context-injector  # Fuente de verdad de APIs y secrets
  - el-monstruo           # Contexto del corpus
  - el-monstruo-plan      # Blueprint Sprint 1
feeds_into:
  - El hilo que construya El Monstruo real
```
