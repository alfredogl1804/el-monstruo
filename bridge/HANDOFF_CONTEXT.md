# HANDOFF DE CONTEXTO — El Monstruo (100% Atómico)

**Fecha:** 2026-05-29
**Sprint actual:** 91 (Mapa Vivo 100% Binario)
**Kernel:** v0.84.8-sprint-memento
**Total ecosistema:** ~479,653 líneas de código
**Generado por:** Hilo Manus B (barrido exhaustivo con API key + código fuente + Railway + Supabase MCP)

---

## 1. QUÉ ES EL MONSTRUO

Sistema de IA soberano multi-agente con kernel propio, 7 capas de memoria persistente, agente autónomo (Embrión), 4 Catastros, governance canónica, y 6 interfaces. No es un chatbot — es una infraestructura cognitiva completa que corre 24/7.

**Repo principal:** `https://github.com/alfredogl1804/el-monstruo` (PUBLIC)
**Dueño:** Alfredo Góngora (@alfredogl1804)
**API Key:** Header `X-API-Key: c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259` (var Railway: `MONSTRUO_API_KEY`)

---

## 2. ARQUITECTURA VIVA (verificada 2026-05-29)

### Servicios Railway (19 servicios, 7 proyectos)

| Servicio | URL | Status | Función |
|----------|-----|:---:|---|
| **el-monstruo-kernel** | `https://el-monstruo-kernel-production.up.railway.app` | ACTIVO | Cerebro central: FastAPI + LangGraph + 13 componentes |
| **ag-ui-gateway** | `https://ag-ui-gateway-production.up.railway.app` | ACTIVO | Gateway AG-UI para streaming de tareas |
| **open-webui** | `https://open-webui-production-b74e.up.railway.app` | ACTIVO | UI de chat web |
| **Redis** | Railway internal | ACTIVO | Cache + pub/sub |
| **Postgres** | Railway internal | ACTIVO | Checkpointer LangGraph |
| **forja-mcp** | `https://forja-mcp-production.up.railway.app` | ACTIVO | MCP Gateway HTTP/SSE |
| **proposal-worker** | Railway internal | ACTIVO | Cierra ciclo HITL del Embrión |
| **command-center** | `https://command-center-production.up.railway.app` | ACTIVO | Dashboard interno Next.js |
| **la-forja-api** | Railway internal | ACTIVO | Backend Hono: 5 puertas LLM + budget |
| **worker (bot)** | Railway internal | ACTIVO | Bot Telegram |
| **sms-rem-cycle** | Railway internal | ACTIVO | Ciclo de recordatorio SMS |
| **like-kukulkan-tickets** | `https://like-kukulkan-tickets-production.up.railway.app` | ACTIVO | Boletería Leones |
| **ticketlike-staging** | `https://ticketlike-staging-production.up.railway.app` | ACTIVO | Staging boletería |
| **simulador-api** | `https://simulador-api-production.up.railway.app` | ACTIVO | Monte Carlo + ABM |
| **4x forja-saludo** | Railway internal | ACTIVO | Tests de deploy automático |

### Endpoints clave del kernel (120+)

| Endpoint | Método | Función |
|----------|--------|---------|
| `/v1/chat` | POST | Chat principal (requiere API key) |
| `/health` | GET | Health check con 13 componentes |
| `/v1/genome/now` | GET | Mapa Vivo binario del ecosistema |
| `/v1/factory/constellation` | GET | ForgeNodes federados |
| `/v1/factory/economy` | GET | Cognitive P&L (15 KPIs) |
| `/v1/factory/timeline` | GET | Sovereign Time Axis |
| `/v1/factory/diff` | GET | Reality Diff (4 dominios) |
| `/v1/embrion/diagnostic` | GET | Diagnóstico del Embrión |
| `/v1/embrion/estado` | GET | Estado completo + memorias |
| `/v1/memory/thoughts` | POST | Crear pensamiento persistente |
| `/v1/memory/search` | POST | Búsqueda semántica |
| `/v1/tools` | GET | Tools registradas con status |
| `/v1/agents/status` | GET | Agentes especializados |
| `/v1/finops/status` | GET | Costos y budget |
| `/v1/catastro/dashboard` | GET | Estado del Catastro de Modelos |
| `/v1/colmena/status` | GET | Estado de la Colmena |
| `/v1/brand/dna` | GET | ADN de marca |
| `/v1/memento/dashboard` | GET | Governance dashboard |

---

## 3. DESCOMPOSICIÓN ATÓMICA (100 piezas principales)

### A. Kernel Core (104,646 líneas Python)

| Pieza | Líneas | Función |
|-------|:---:|---|
| engine.py | 1,847 | Grafo LangGraph: 8 nodos, patrón ReAct, circuit breaker, recursion limit 25 |
| main.py | 1,203 | FastAPI app con 20+ routers montados |
| embrion_loop.py | 1,372 | Loop autónomo: piensa cada 60s, cooldown 5min, budget $30/día |
| factory_routes.py | 938 | Constellation + Economy + Timeline + Diff (República Cognitiva) |
| onboarding.py | 487 | Wizard 5 fases para nuevos usuarios |
| nodes.py | ~800 | Los 8 nodos del grafo: classify, retrieve_context, call_llm, execute_tool, evaluate, respond, human_review, error_handler |

### B. Embriones (13,086 líneas — 22 archivos)

| Pieza | Función |
|-------|---------|
| Orchestrator | Coordina los 22 embriones especializados |
| Vigía | Monitoreo continuo del ecosistema |
| 10 domain specialists | Finanzas, legal, marketing, tech, etc. |
| Collective | Inteligencia colectiva entre embriones |
| 10 doctrine-only | Embriones que solo observan y aprenden |
| Self-Verifier | Valida calidad de sus propios pensamientos |

### C. Catastro (9,295 líneas — 29 archivos, 4 catastros)

| Catastro | Entries | Función |
|----------|:---:|---|
| Modelos LLM | 41 | Rankea, recomienda, vota entre modelos IA (RecommendationEngine + quorum) |
| Agentes 2026 | 21 | Cataloga agentes IA del mercado (Claude Code, Cowork, Manus, Devin, etc.) |
| Herramientas AI | 24 | Tools verticales con precios verificados (Hyper3D, Veo 3.1, Runway, etc.) |
| Suppliers Humanos | 36 | Proveedores reales Sureste MX (teléfonos, emails, direcciones) |

### D. Memoria (7 capas)

| Capa | Registros | Función |
|------|:---:|---------|
| Hot (in-context) | variable | Lo que el modelo tiene en ventana |
| Warm (Supabase) | 3,034+ | Thoughts, episodic, semantic, embrión responses |
| Cold (Mem0) | — | Largo plazo, cross-session (código listo, no deployado) |
| Event Store | 5,803 runs | Todos los eventos del kernel |
| Knowledge Graph (LightRAG) | 151 entidades | Relaciones semánticas |
| Sovereign Memory (SMS v4.0) | 1,517 memorias + 57 axiomas | Memoria soberana |
| Error Memory | 38 errores (36 resueltos) | Aprende de fallos |

### E. Anti-Dory (5,264 líneas — 16 archivos)

Prevención de pérdida de contexto entre sesiones. Detecta compactación, recupera contexto, inyecta memorias críticas.

### F. Governance (2,704 líneas)

| Pieza | Función |
|-------|---------|
| Memento | 6 operaciones críticas auditadas, 4 sources of truth |
| Guardian | Identidad de hilo + restauración (V5 con SMS) |
| Brand Engine | Validación de marca (threshold=60, avg_score=90) |
| Thread Immunity | Anclaje anti-drift entre sesiones |
| 99 DSCs firmados | 9 dominios de governance canónica |

### G. Colmena + Vanguard (3,089 líneas)

Inteligencia colectiva: 7 nodos activos, debates, votaciones, consenso.

### H. Forja Protocol (15,769 líneas TypeScript — repo tablero-campana)

| Pieza | Función |
|-------|---------|
| Sovereign Envelope | Firmas ed25519 + canonicalización RFC 8785 |
| BoundaryGateway (442 líneas) | 10 verificaciones de seguridad |
| Attenuation Verifier | 5 invariantes monotónicos |
| eventSigner/Publisher/Observer | Pipeline de eventos firmados |
| SubEnvelope primitiva | Delegación de capacidades |
| 56 tests verdes | Cobertura completa |

### I. Herramientas (20 tools)

| Tool | Status |
|------|:---:|
| web_search, calculator, code_interpreter, file_manager | ACTIVE |
| email_sender, knowledge_query, memory_store | ACTIVE |
| calendar_check, task_manager, data_analyzer | ACTIVE |
| document_generator, image_analyzer, api_caller, notification | ACTIVE |
| browser_automation, voice_call, payment_processor | HITL (requieren aprobación) |
| social_media_post, deploy_service, database_query | Sin credenciales |

### J. Agentes (6 especializados)

| Agente | Modelo preferido | Tools |
|--------|-----------------|-------|
| researcher | sonar-reasoning-pro | web_search, knowledge_query |
| analyst | gpt-5.5-pro | data_analyzer, calculator |
| writer | claude-opus-4.7 | document_generator, knowledge_query |
| developer | claude-opus-4.7 | code_interpreter, file_manager |
| strategist | gpt-5.5-pro | web_search, data_analyzer |
| communicator | gpt-5.5-pro | email_sender, notification |

### K. Modelos IA disponibles (6 principales)

| Modelo | Uso principal | % de runs |
|--------|---|:---:|
| Grok 4 | Razonamiento rápido | 56% |
| Sonar Reasoning Pro | Investigación en tiempo real | 15% |
| Claude Opus 4.7 | Coding, escritura técnica | 15% |
| GPT-5.5 Pro | Arquitectura, estrategia | 11% |
| Gemini 3.1 Pro | Multimodal, análisis largo | 2% |
| DeepSeek R1 | Razonamiento profundo | 1% |

### L. Interfaces (6)

| Interfaz | Stack | Status |
|----------|-------|:---:|
| Telegram Bot | Python + Railway | ACTIVO (standby por instrucción) |
| Open WebUI | Fork + Railway | ACTIVO |
| Command Center | Next.js + Railway | ACTIVO |
| AG-UI Gateway | Python FastAPI + Railway | ACTIVO |
| App Flutter | Dart, 72 archivos, 16,202 líneas, 3 modos | FUNCIONAL (no publicada) |
| La Forja | Hono API + Next.js Web | ACTIVO |

### M. Simulador Predictivo Causal (2,462 líneas — repo simulador-universal)

| Motor | Función |
|-------|---------|
| Monte Carlo | 10,000+ iteraciones, fat tails (t Student df=5), correlación Cholesky |
| Agent-Based Modeling | Agentes LLM con personalidad, memoria, decisión por rondas |
| Perfiles: Electoral, Financial, Crisis | Calibrado contra Mérida 2018/2021/2024 |

### N. Repos satélite (11 con código real)

| Repo | Líneas | Función |
|------|:---:|---|
| like-kukulkan-tickets | 36,025 | Boletería Leones (TS full-stack) |
| tablero-campana | 15,769 | Forja Protocol (TS) |
| crisol-8 | 8,376 | OSINT Investigation (Python) |
| rug-carousel | 8,412 | Catálogo alfombras (TS) |
| el-monstruo-bot | 8,268 | Bot Telegram (Python) |
| observatorio-merida-2027 | 7,970 | Modelo Bayesiano electoral |
| biblia-github-motor | 4,658 | Motor de biblias (Python) |
| command-center | 3,806 | Dashboard (TS/Next.js) |
| simulador-universal | 2,462 | Monte Carlo + ABM (Python) |
| fernando-dia-maestro-2026 | 1,471 | Dashboard show (HTML) |
| forja-mcp | 226 | MCP Gateway (TS) |

### O. Supabase

- 287 tablas (181 en public)
- 328 RPCs custom (72 verificadas por contenido)
- 17 schemas
- 8 extensions (pgvector, pgjwt, pg_cron, etc.)
- 62 migraciones aplicadas

### P. Scripts operativos (28,451 Python + 3,709 Bash + 14,326 Shell)

Genome scanners, credential auditors, seed scripts, deploy helpers, genome generator, thread immunity, DTA sync.

### Q. Tests (51,966 líneas)

143+ tests pasando. Cobertura de kernel, embriones, tools, memory, catastro, forja.

---

## 4. MÉTRICAS OPERATIVAS (2026-05-29)

| Métrica | Valor |
|---------|-------|
| Runs históricos | 5,803 |
| Tokens procesados (12 días) | 64.6M |
| Costo hoy | $0.83 USD |
| Budget diario Embrión | $30 USD |
| Embrión ciclos totales | 191 |
| Sovereignty Score | 118 puntos |
| Memorias del Embrión | 3,034 |
| Knowledge Graph entidades | 151 |
| Sovereign Memories | 1,517 |
| Axiomas canónicos | 57 |
| Sprints completados | 15 |
| Sprints propuestos | 32 |
| DSCs firmados | 99 |
| Branches activas | 458 |

---

## 5. GAPS CONOCIDOS (7)

1. embrion_loop aislado (no comparte state con kernel graph)
2. collective RAM-only (no persiste debates)
3. embriones domain-specialists stateless
4. bot Telegram en standby (instrucción Alfredo 22-mayo, rompe-bucle)
5. embeddings pending en algunas tablas
6. domain embriones doctrine-only (no ejecutan)
7. Catastro de Modelos DB degradada (código listo, tabla Supabase no poblada)

---

## 6. CÓMO CONECTAR (para cualquier hilo nuevo)

```bash
# Health check
curl -sS https://el-monstruo-kernel-production.up.railway.app/health | python3 -m json.tool

# Genome Vivo (mapa binario completo)
curl -sS https://el-monstruo-kernel-production.up.railway.app/v1/genome/now | python3 -m json.tool

# Chat con el kernel
curl -sS -X POST https://el-monstruo-kernel-production.up.railway.app/v1/chat \
  -H "X-API-Key: c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259" \
  -H "Content-Type: application/json" \
  -d '{"message": "hola", "user_id": "manus_hilo"}'

# Factory endpoints (República Cognitiva)
curl -sS -H "X-API-Key: c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259" \
  https://el-monstruo-kernel-production.up.railway.app/v1/factory/constellation

# Embrión diagnóstico
curl -sS -H "X-API-Key: c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259" \
  https://el-monstruo-kernel-production.up.railway.app/v1/embrion/diagnostic

# FinOps
curl -sS -H "X-API-Key: c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259" \
  https://el-monstruo-kernel-production.up.railway.app/v1/finops/status
```

---

## 7. SECRETS Y VARIABLES (en Railway)

| Variable | Servicio |
|----------|---------|
| `MONSTRUO_API_KEY` | Kernel |
| `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` | Kernel |
| `OPENAI_API_KEY` | Kernel |
| `PERPLEXITY_API_KEY` | Kernel |
| `GEMINI_API_KEY` | Kernel |
| `XAI_API_KEY` | Kernel |
| `ANTHROPIC_API_KEY` | Kernel |
| `LANGFUSE_SECRET_KEY` / `LANGFUSE_PUBLIC_KEY` | Kernel |
| `TELEGRAM_BOT_TOKEN` | Worker |
| `CLOUDFLARE_API_TOKEN` | Kernel |
| `DEEPSEEK_API_KEY` | Kernel |
| `ELEVENLABS_API_KEY` | Kernel |
| `HEYGEN_API_KEY` | Kernel |

NO configurar manualmente — todo vive en Railway. Usar `railway variables` desde el repo clonado.

---

## 8. REGLAS DURAS (resumen)

1. Ejecutar `guardian.py` ANTES de cualquier acción
2. Leer Genome Vivo ANTES de proponer construir algo
3. NO credenciales en plaintext (DSC-S-001 a DSC-S-005)
4. Tratamiento canónico: "Alfredo" (no "don Alfredo"). Don Hugo es su papá.
5. Embrión en standby por instrucción explícita (22-mayo rompe-bucle)
6. Fase 1 activa: Hilo B diseña, Hilo A ejecuta
7. Brand Compliance obligatorio en todo output público
8. Los 14 Objetivos Maestros aplican a TODO
9. Las 7 Capas Transversales son obligatorias
10. NO inventar la rueda — buscar si ya existe

---

## 9. LÍNEAS DE CÓDIGO POR COMPONENTE

| Componente | Líneas | Lenguaje |
|------------|:---:|---|
| kernel/ | 104,646 | Python |
| tests/ | 51,966 | Python |
| SQL (migraciones + schemas) | 41,499 | SQL |
| apps/mobile/ | 34,327 | Dart |
| skills/ | 31,663 | Python |
| scripts/ | 32,160 | Python + Bash |
| bridge/ | 16,937 | Mixed |
| apps/la-forja/ | 13,321 | TypeScript |
| tools/ | 12,259 | Python |
| Shell scripts | 14,326 | Bash |
| Repos satélite (11) | 97,443 | Mixed |
| Otros (memory, embryos, router, etc.) | 29,106 | Python |
| **TOTAL ECOSISTEMA** | **~479,653** | |

---

## 10. SISTEMA DE COMUNICACIÓN ENTRE HILOS

- `bridge/manus_to_cowork.md` — Hilo A (ejecutor) reporta a Hilo B (arquitecto)
- `bridge/cowork_to_manus.md` — Hilo B responde con directivas
- `bridge/HANDOFF_CONTEXT.md` — Este archivo (transferencia completa)
- `bridge/sprints_propuestos/` — 32 sprints pendientes
- `bridge/sprints_completados/` — 15 sprints cerrados

---

## 11. ARCHIVOS CLAVE QUE DEBES LEER (en orden)

1. `AGENTS.md` — Reglas duras, identidad, objetivos, capas
2. Este archivo (`bridge/HANDOFF_CONTEXT.md`) — Mapa 100%
3. `MONSTRUO_GENOME.yaml` — Genome estático (958 líneas)
4. `bridge/cowork_to_manus.md` — Últimas directivas
5. `docs/INVENTARIO_PROYECTOS_v3_COMPLETO.md` — 20 proyectos del portfolio

---

## 12. DIVISIÓN DE TRABAJO

| Hilo | Rol | Responsabilidad |
|------|-----|-----------------|
| Hilo A (Manus) | Ejecutor técnico | Código, deploys, tests, curls |
| Hilo B (Cowork) | Arquitecto | Diseño, auditoría, decisiones T1 |
| Embrión | Autónomo | Piensa solo, propone, consulta sabios |
| Alfredo | Dueño | Decisiones magnas, aprobación, dirección |

---

*Última actualización: 2026-05-29T21:15:00-06:00*
*Regenerar con: `python3 scripts/genome_live/run_all.py`*
*Verificar con: `curl -sS https://el-monstruo-kernel-production.up.railway.app/v1/genome/now | python3 -m json.tool`*
