---
name: api-context-injector
description: Registro centralizado, router inteligente e inyector de contexto para todas las IAs, APIs, MCPs, herramientas nativas y skills disponibles. Incluye arsenal expandido — cada conector-puerta cataloga sus sub-servicios específicos. Inyección automatizada de secrets a proyectos con detección de scaffold y validación de seguridad. Skill Intelligence Layer para scouting y evaluación de skills externas con metodología TRUST+FIT. Contrato compartido (ecosystem-state) con skill-factory. Usar cuando se necesite decidir qué IA/API usar, verificar credenciales, obtener metadata de conexión, inyectar contexto de capacidades a cualquier tarea, configurar secrets en un proyecto, buscar skills externas, o evaluar si instalar/fork/componer/construir.
---

# api-context-injector v4.0 — Skill OS Kernel

Sistema nervioso central del ecosistema de Alfredo. Fuente de verdad operativa para decidir qué herramienta usar, cómo conectarse, qué hacer si falla, cómo inyectar secrets, y cuándo descubrir/instalar/componer skills externas.

## DECISIÓN RÁPIDA (Leer Primero)

1. **Tarea en 1 dominio** → `routing/capability_registry.yaml`
2. **Tarea en 2+ dominios** → `routing/pipeline_templates.yaml`
3. **Tarea desconocida** → `routing/use_case_index.yaml`
4. **Necesitas conectarte** → `docs/connection_patterns.md`
5. **Algo falla** → `docs/fallback_policy.md`
6. **Inyectar secrets** → `scripts/inject_secrets.py`
7. **Buscar skill externa** → `scripts/skill_scout.py --search "keyword"`
8. **Evaluar skill externa** → `scripts/skill_scout.py --evaluate-url "URL"`
9. **Antes de construir skill** → `routing/ecosystem_state.yaml` (sección skill_decision)
10. **Evaluar install vs build** → `routing/trust_fit_evaluator.yaml`
11. **Herramientas que faltan** → `arsenals/tier1_expansion.yaml`

## Reglas Inquebrantables

1. **NUNCA** imprimir API keys, tokens, o credenciales en texto plano
2. **NUNCA** inyectar secrets en scaffolds frontend-only (`web-static`)
3. **NUNCA** usar prefijos `VITE_`, `NEXT_PUBLIC_`, `REACT_APP_` para secrets reales
4. **NUNCA** instalar skill externa que falle hard gates de TRUST+FIT
5. **OBLIGATORIO** consultar `routing/capability_registry.yaml` antes de elegir herramienta
6. **OBLIGATORIO** verificar scaffold antes de inyectar secrets (`--detect`)
7. **OBLIGATORIO** verificar env var con `scan_env.py` antes de conexión
8. **OBLIGATORIO** consultar arsenal (`arsenals/*.yaml`) para tareas de conectores-puerta
9. **OBLIGATORIO** usar pipeline template para tareas multi-dominio (2+ capabilities)
10. **OBLIGATORIO** consultar `ecosystem_state.yaml` antes de construir nueva skill
11. **OBLIGATORIO** benchmark-before-build: verificar si ya existe interna o externamente
12. **PROHIBIDO** usar SDK OpenAI para Perplexity — solo `requests`
13. **PROHIBIDO** usar `max_tokens` con GPT-5.4 — solo `max_completion_tokens`

## Anti-Errores Críticos

| Error Común | Corrección |
|-------------|-----------|
| `max_tokens` con GPT-5.4 | Usar `max_completion_tokens` |
| SDK OpenAI para Perplexity | Usar `requests` directo |
| Claude `4-20250514` | Es `anthropic/claude-sonnet-4-6` vía OpenRouter (Opus tiene timeouts) |
| Grok `grok-4-latest` | Es `grok-4.20-0309-reasoning` |
| DeepSeek directo | Va por OpenRouter: `base_url=openrouter.ai/api/v1` |
| Secret en `web-static` | BLOQUEADO — crear proxy backend |
| `VITE_API_KEY=sk-...` | NUNCA — expone al cliente |
| Construir skill sin benchmark | PROHIBIDO — verificar ecosystem_state primero |

## Skill Intelligence Layer (NUEVO v4.0)

### Buscar Skills Externas

```bash
# Buscar por capacidad
python3.11 scripts/skill_scout.py --search "web scraping"

# Buscar y evaluar con TRUST+FIT
python3.11 scripts/skill_scout.py --search "video generation" --evaluate

# Evaluar un repo específico
python3.11 scripts/skill_scout.py --evaluate-url "https://github.com/user/skill-repo"

# Ver fuentes disponibles
python3.11 scripts/skill_scout.py --list-sources

# Skills trending
python3.11 scripts/skill_scout.py --trending
```

### Metodología TRUST+FIT

Antes de instalar cualquier skill externa:

1. **Hard Gates** (falla 1 = RECHAZAR): No hardcoded secrets, no curl|bash, no exfiltración, licencia compatible, compatible Manus, no acceso a pagos sin aprobación, data residency OK
2. **Scorecard** (0-100): Security(20) + Provenance(10) + License(10) + Manus compat(10) + Functional fit(15) + Maintainability(10) + Performance(10) + Compliance(10) + ROI(5)
3. **Decisión**: install (>75) / fork_and_harden (>55) / use_as_reference (>40) / reject (<40)

→ Detalle completo: `routing/trust_fit_evaluator.yaml`

### Decisión: Install / Fork / Compose / Build

Antes de construir CUALQUIER skill nueva, seguir este flujo:

1. Verificar skills internas → `references/skills-registry.yaml`
2. Verificar capabilities existentes → `routing/capability_registry.yaml`
3. Scout externo → `scripts/skill_scout.py --search`
4. Si hay candidato externo → evaluar con TRUST+FIT
5. Decidir:
   - **Install**: commodity, fuente confiable, compatible, bajo riesgo
   - **Fork & harden**: buena base, necesita adaptación
   - **Compose**: >60% existe en piezas internas
   - **Build**: alta diferenciación, datos sensibles, incompatibilidad legal

→ Framework completo: `routing/ecosystem_state.yaml` sección `skill_decision`

## Flujo de Inyección de Secrets

```bash
# Detectar scaffold
python3.11 scripts/inject_secrets.py --detect /path/to/project

# Auditar secrets
python3.11 scripts/inject_secrets.py --audit /path/to/project

# Auto-generar manifiesto
python3.11 scripts/inject_secrets.py --generate-manifest /path/to/project

# Inyectar (4 targets: sandbox, vercel, cloudflare, supabase)
python3.11 scripts/inject_secrets.py --project /path --target sandbox
python3.11 scripts/inject_secrets.py --project /path --target vercel --dry-run
```

→ Política de seguridad: `routing/security_policy.yaml`

## Contrato Compartido con skill-factory (NUEVO v4.0)

El archivo `routing/ecosystem_state.yaml` es el contrato estructurado entre api-context-injector y skill-factory. Contiene:

1. **Capability Summary** — qué puede hacer el ecosistema y qué NO
2. **Cost & Reliability Matrix** — costos, latencia, disponibilidad por tier
3. **Secrets & Deployment Matrix** — qué secret requiere cada servicio, targets permitidos
4. **Policy & Compliance Matrix** — GDPR, EU AI Act, data residency, licensing
5. **External Skill Index** — fuentes verificadas y no verificadas de skills
6. **Execution Telemetry** — hooks para métricas reales
7. **Skill Decision Framework** — flujo benchmark-before-build

**skill-factory DEBE consultar este archivo antes de crear cualquier skill.**

## Inventario Resumido

| Categoría | Cantidad | Referencia |
|-----------|----------|-----------|
| IAs LLM (6 Sabios + extras) | 7 | `references/llm-registry.yaml` |
| APIs Media/Generación | 8 | `references/media-apis.yaml` |
| APIs Infraestructura/Cloud | 9 | `references/infra-apis.yaml` |
| APIs Datos/Monitoreo/Scraping | 7 | `references/data-apis.yaml` |
| APIs Pagos | 1 | `references/payment-apis.yaml` |
| Conectores Manus (MCPs+APIs+Nativos) | 27 | `references/mcp-registry.yaml` |
| Herramientas Nativas Sandbox | 10 | `references/native-tools.yaml` |
| Skills Existentes | 12 | `references/skills-registry.yaml` |
| Capacidades atómicas ruteadas | 52 | `routing/capability_registry.yaml` |
| Pipelines multi-dominio | 15 | `routing/pipeline_templates.yaml` |
| Rutas de decisión | 59 | `routing/decision_router.yaml` |
| Herramientas Tier-1 planificadas | 5 | `arsenals/tier1_expansion.yaml` |

**Total: 82 recursos directos + 52 capabilities + 15 pipelines + 59 rutas + 5 Tier-1 planificadas + acceso a ~31,700+ herramientas via 8 conectores-puerta.**

## Los 6 Sabios (Semilla v7.3)

| Sabio | model_id | Env Var | Contexto |
|-------|----------|---------|----------|
| GPT-5.4 | gpt-5.4 | OPENAI_API_KEY | 1.05M |
| Claude Sonnet 4.6 | anthropic/claude-sonnet-4-6 | OPENROUTER_API_KEY | 1M |
| Gemini 3.1 Pro | gemini-3.1-pro-preview | GEMINI_API_KEY | 1M |
| Grok 4.20 | grok-4.20-0309-reasoning | XAI_API_KEY | 2M |
| DeepSeek R1 | deepseek-r1 | OPENROUTER_API_KEY | 128K |
| Perplexity Sonar | sonar-reasoning-pro | SONAR_API_KEY | 128K |

→ Patrones de conexión: `docs/connection_patterns.md`

## Conectores de Manus (27 activos)

### MCPs (11 — via `manus-mcp-cli`)
notion, supabase, gmail, google-calendar, asana, zapier, vercel, paypal-for-business, revenuecat, instagram, outlook-mail

### APIs con Env Var (10 — via SDK/requests)
OpenAI, Anthropic, Gemini, Perplexity, ElevenLabs, Grok, OpenRouter, Dropbox, Cloudflare, HeyGen

### Integraciones Nativas (3 — CLI/browser)
Mi navegador, Google Drive (`gws`), GitHub (`gh`)

→ Detalle completo: `references/mcp-registry.yaml`

## Arsenales Expandidos (8 activos + 5 planificados)

| Conector | Ecosistema | Arsenal |
|----------|-----------|---------|
| OpenRouter | 500+ modelos IA | `arsenals/openrouter.yaml` |
| Apify | 23,000+ actors | `arsenals/apify.yaml` |
| Cloudflare | 15+ productos cloud | `arsenals/cloudflare.yaml` |
| AWS | 200+ servicios | `arsenals/aws.yaml` |
| Zapier | 8,000+ apps | `arsenals/zapier.yaml` |
| GitHub | Repos + CI/CD | `arsenals/github.yaml` |
| Google Workspace | Drive+Docs+Sheets | `arsenals/google_workspace.yaml` |
| Supabase | PostgreSQL+Vector+Auth | `arsenals/supabase.yaml` |
| **Tier-1 Planificados** | **5 herramientas** | `arsenals/tier1_expansion.yaml` |

→ **Solo leer el arsenal relevante para la tarea actual, no todos.**

## Credenciales (Solo Referencias)

### Env Vars del Sandbox (siempre disponibles)
OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, XAI_API_KEY, SONAR_API_KEY, OPENROUTER_API_KEY, HEYGEN_API_KEY, ELEVENLABS_API_KEY, CLOUDFLARE_API_TOKEN, DROPBOX_API_KEY

### Credenciales en Notion DB (requieren consulta)
DB: `54b9d97704bc408d8453c1524fbfec9b` | Data Source: `collection://d94369d5-5dc3-437e-b483-fa86a5e98b74`

Servicios solo en Notion: Together AI, Replicate, Novita AI, Atlas Cloud, Meshy AI, Fashn AI, RunPod, AWS, Keepa, Best Buy, SecurityTrails, HIBP, BrandMentions, Mentionlytics, Apify, Stripe, Vercel.

```bash
# Obtener credencial de Notion:
manus-mcp-cli tool call notion-search --server notion --input '{"query": "NOMBRE_SERVICIO", "data_source_url": "collection://d94369d5-5dc3-437e-b483-fa86a5e98b74", "page_size": 5}'
```

## Cadenas de Fallback

→ Detalle completo: `docs/fallback_policy.md`

| Si falla... | Usar... | Si también falla... |
|-------------|---------|---------------------|
| GPT-5.4 | Claude Opus 4.6 | Grok 4.20 |
| Claude | GPT-5.4 | Gemini |
| Perplexity | Grok (web access) | GPT-5.4 |
| HeyGen | Atlas Cloud | — |
| ElevenLabs | AWS Polly | OpenAI TTS |
| Cloudflare | AWS equivalente | Vercel |
| Apify actor | Apify/web-scraper genérico | Browser nativo |

**ALTO TOTAL si < 3 sabios disponibles.**

## Scripts

| Script | Función |
|--------|---------|
| `scan_env.py` | Verifica env vars disponibles |
| `sync_notion.py` | Sincroniza desde Notion DB |
| `health_check.py` | Ping a todas las APIs |
| `inject_context.py` | Genera contexto para tarea |
| `inject_secrets.py` | Inyección automatizada de secrets |
| `validate_registry.py` | Valida integridad de registros |
| `skill_scout.py` | **NUEVO v4.0** — Skill Intelligence Layer |

## Estructura de Archivos

```
api-context-injector/
├── SKILL.md                          # Orquestador (este archivo)
├── README.md                         # Documentación pública
├── docs/
│   ├── connection_patterns.md        # Patrones de conexión copy-paste
│   └── fallback_policy.md            # Cadenas de fallback + políticas
├── references/                       # Registros planos por dominio
│   ├── llm-registry.yaml
│   ├── media-apis.yaml
│   ├── infra-apis.yaml
│   ├── data-apis.yaml
│   ├── payment-apis.yaml
│   ├── mcp-registry.yaml
│   ├── native-tools.yaml
│   └── skills-registry.yaml
├── arsenals/                         # Sub-servicios por conector-puerta
│   ├── openrouter.yaml
│   ├── apify.yaml
│   ├── cloudflare.yaml
│   ├── aws.yaml
│   ├── zapier.yaml
│   ├── github.yaml
│   ├── google_workspace.yaml
│   ├── supabase.yaml
│   └── tier1_expansion.yaml          # NUEVO v4.0 — Herramientas planificadas
├── routing/
│   ├── capability_registry.yaml      # 52 capacidades atómicas
│   ├── pipeline_templates.yaml       # 15 pipelines multi-dominio
│   ├── decision_router.yaml          # 59 rutas de decisión
│   ├── use_case_index.yaml           # Índice invertido
│   ├── security_policy.yaml          # Política de seguridad
│   ├── ecosystem_state.yaml          # NUEVO v4.0 — Contrato compartido
│   └── trust_fit_evaluator.yaml      # NUEVO v4.0 — Evaluador TRUST+FIT
├── scripts/
│   ├── scan_env.py
│   ├── sync_notion.py
│   ├── health_check.py
│   ├── inject_context.py
│   ├── inject_secrets.py
│   ├── validate_registry.py
│   └── skill_scout.py               # NUEVO v4.0 — Skill Intelligence Layer
├── templates/
│   ├── api_connection.py
│   └── project_manifest.yaml
└── data/                             # NUEVO v4.0 — Datos operativos
    └── skill_evaluations.jsonl       # Historial de evaluaciones TRUST+FIT
```

## Metadata

```yaml
version: "4.0"
last_verified: "2026-04-09"
ttl_days: 30
audit_score: "Diseñado por Consejo de 6 Sabios (2026-04-09)"
next_review: "2026-05-09"
changelog:
  - "4.0: Skill OS Kernel — Skill Intelligence Layer (scout + TRUST+FIT), Ecosystem State (contrato compartido), Tier-1 expansion arsenal, benchmark-before-build policy"
  - "3.1: Flujo automatizado de inyección de secrets"
  - "3.0: Capability routing, pipeline templates, modular docs"
  - "2.0: Arsenal expandido (8 conectores-puerta)"
  - "1.0: Inventario plano inicial"
```
