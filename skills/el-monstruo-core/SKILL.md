---
name: el-monstruo-core
description: "Fuente única de verdad del Monstruo: doctrina fundacional (SOP, EPIA, MAOC, MOC, Protocolo Memento, Puente Inter-Hilos), estado técnico operativo (Sprint 27), arsenal de herramientas, modelos IA, endpoints, secretos y decisiones de diseño. Úsalo SIEMPRE que necesites construir, modificar, desplegar, entender o tomar decisiones sobre cualquier componente del ecosistema de El Monstruo."
metadata:
  version: 3.0.0
  status: ACTUAL
  owner: Alfredo Góngora
  last_reviewed: 2026-04-27 (Sprint 27+, modelos actualizados a GPT-5.5, Claude Opus 4.7, DeepSeek V4, Grok 4.3)
  review_trigger: cada sprint o cambio mayor
  sources_of_truth: repo-kernel, repo-bot, railway, SOP_EPIA_COMPILACION_DEFINITIVA.md, MAOC_MASTER_DOCUMENT.md, MOC_Evolucion_Perpetua_fundacional_v1.txt, GENEALOGIA_SOP_EPIA_v2.md, Identidad_del_Monstruo_fundacional_v1.txt
---

# El Monstruo: Core Architecture, Doctrine & State (v3.0)

Este skill consolida y reemplaza a los antiguos skills `el-monstruo-estado`, `el-monstruo-plan`, `el-monstruo-armero`, `el-monstruo-toolkit` y `el-monstruo`. Es la **única fuente de verdad** para el desarrollo y operación del ecosistema.

**CAMBIO v3.0 (25 abril 2026):** Se restauró el contexto fundacional completo que se había perdido en versiones anteriores del skill. Las secciones 1-6 cubren la doctrina fundacional (SOP, EPIA, MAOC, MOC, Protocolo Memento, Puente Inter-Hilos). Las secciones 7-14 cubren el estado técnico operativo.

---

## PARTE I: DOCTRINA FUNDACIONAL

---

## 1. Jerarquía Canónica del Ecosistema

El Monstruo no es un proyecto aislado. Es la materialización concreta de un ecosistema de 4 capas doctrinales:

| Capa | Nombre | Función | Relación |
|---|---|---|---|
| Visión / Arquitectura | **EPIA** (Ecosistema de Productividad Integrada con IA) | Define QUÉ capacidades deben existir y CÓMO se integran | Marco superior |
| Gobierno | **SOP** (Standard Operating Procedure) v1.2 | Define CÓMO se decide, valida, limita, escala y detiene | Constitución operativa |
| Implementación | **El Monstruo** | Materializa EPIA bajo gobierno SOP | Infraestructura soberana |
| Evolución | **MOC** (Maduración Operativa Continua) / Evolución Perpetua | Garantiza maduración ENTRE sesiones | Macro-capa persistente |

> **Tesis irreductible de EPIA:** "La inteligencia verdaderamente útil emerge de la integración soberana de múltiples IAs, memorias y herramientas bajo una arquitectura común, no del uso aislado de un modelo individual."

> **Frase canónica del Monstruo:** "El Monstruo es la máquina soberana que convierte un ecosistema fragmentado de inteligencias y herramientas en una capacidad continua de pensar, recordar, coordinar, ejecutar, madurar y crear ventures bajo una sola lógica propia."

---

## 2. SOP — Constitución Operativa (v1.2 Canónico, abril 2026)

SOP es el marco de gobernanza operativa y ejecutable. No es una lista de trucos ni un conjunto de prompts. Es la capa que convierte intención en operación consistente.

### 2.1 Principios Constitucionales Permanentes

1. **Soberanía:** El sistema opera bajo lógica propia, no delegada.
2. **Trazabilidad:** Toda decisión relevante se registra con contexto.
3. **Reversibilidad:** Todo cambio arquitectónico debe tener rollback definido.
4. **Validación proporcional:** El nivel de evidencia debe ser proporcional al riesgo.
5. **No dependencia:** Ninguna herramienta individual es único punto de verdad.
6. **Kill-switch:** Toda automatización debe poder detenerse.
7. **PII = 0:** Tolerancia cero a datos personales en el sistema.

### 2.2 Taxonomía Normativa

| Nivel | Tipo | Permanencia | Ejemplo |
|---|---|---|---|
| 1 | **Principio** | Permanente | Soberanía, trazabilidad |
| 2 | **Regla** | Estable, revisable | Auth fail-closed, rollback obligatorio |
| 3 | **Heurística** | Adaptable | Preferir pgvector sobre ChromaDB en Railway |

### 2.3 Roles Gobernados por SOP

| Rol | Función |
|---|---|
| **Cerebro** | Orquestación, síntesis, decisión de alto nivel |
| **Brazo Híbrido** | Ejecución entre nube, herramientas y entorno local |
| **Brazo Autónomo** | Ejecución persistente con contención obligatoria |
| **Sabios 1-6** | Panel consultivo para contraste y validación |
| **Memoria** | Persistencia, recuperación y versionado |
| **Conectividad** | APIs, MCPs, CLIs y conectores |
| **Gobernanza ejecutable** | Policies, routers, validadores, observabilidad |

### 2.4 Niveles de Validación

| Nivel | Nombre | Cuándo aplica |
|---|---|---|
| 0 | Exploratorio | Hipótesis inicial, no ejecutable |
| 1 | Verificación simple | Una fuente confiable lo respalda |
| 2 | Validación cruzada | 2+ fuentes o Sabios convergen |
| 3 | Consenso operativo | Convergencia suficiente para operar con supervisión |
| 4 | Validación humana | Acciones sensibles, irreversibles o de alto impacto |

### 2.5 Genealogía del SOP

| Generación | Período | Concepto clave |
|---|---|---|
| Gen 0 | Pre-Sep 2025 | Mandato Maestro, PAU, Reglas Universales v2.x |
| Gen 1 | Sep 2025 | Piso 11/12, 13 reglas operativas, Modo Descubrimiento |
| Gen 2 | Oct 2025 | Roadmap 12 meses en 6 fases |
| Gen 3 | Oct-Dic 2025 | EPIA-SOP 4.0 Live, API-First, RuleMint v1.2 |
| Gen 4 | Abr 2026 | SOP Fundacional Canónico v1.2 compilado |

---

## 3. EPIA — Marco Arquitectónico (v1.0 Canónico, abril 2026)

EPIA define el mapa del poder y la arquitectura de integración. Establece qué capacidades existen y cómo se conectan.

### 3.1 Las 9 Capas de la Arquitectura EPIA

1. **Interfaces** — Telegram, Open WebUI, Command Center PWA (futuro)
2. **Orquestación** — LangGraph kernel, Router Soberano
3. **Cerebros** — 6 modelos IA con fallback chains (GPT-5.5, Claude Opus 4.7, Gemini 3.1, Grok 4.3, DeepSeek V4, Perplexity Sonar)
4. **Brazos** — Ejecución de código, browser automation, MCP servers
5. **Memoria** — 4 capas jerárquicas (Checkpointer, MemPalace, LightRAG, Mem0)
6. **Gobernanza** — SOP como Policy-as-Code, validadores, risk scoring
7. **Observabilidad** — Langfuse + OpenTelemetry, EventStore soberano
8. **Seguridad** — Auth fail-closed, AI-Infra-Guard, Semgrep, SBOM, Garak
9. **Evolución** — MOC, DeepEval, auto-mejora de prompts

### 3.2 Arquitectura de Absorción Soberana

El principio de diseño central: en lugar de construir un modelo desde cero, el Monstruo **absorbe** las mejores IAs del mundo bajo control soberano.

| Capa | Qué contiene | Control |
|---|---|---|
| **Core Soberano** | Kernel, Router, Memoria, Policy Engine | 100% propio |
| **Híbrido Absorbido** | SDKs nativos de OpenAI, Anthropic, Google, xAI | APIs externas, control de estado propio |
| **Commodity** | Open WebUI, Langfuse, Railway | Reemplazable sin impacto en core |

### 3.3 Genealogía de EPIA

| Generación | Período | Concepto clave |
|---|---|---|
| Gen 1 | Nov 2025 | Catálogo de 25 IAs en 11 categorías |
| Gen 2 | Nov 2025 | Framework v3.3.2 con RuleMint, Watchtower, OPA |
| Gen 3 | Abr 2026 | EPIA Fundacional Canónico — 9 capas |

---

## 4. MAOC — Memoria Aumentada y Orquestación de Capacidades

MAOC es la respuesta al problema fundacional: la pérdida de memoria y la pasividad de diseño del agente IA.

### 4.1 Origen (26 diciembre 2025)

La "conversación reveladora" del 10-12 diciembre 2025 identificó dos problemas:
1. **Limitación técnica:** Ventana de contexto finita.
2. **Restricción de diseño deliberada:** Comportamiento pasivo para garantizar escalabilidad de la plataforma.

### 4.2 Solución: Externalizar memoria y automatizar conciencia

| Componente | Función | Estado actual |
|---|---|---|
| **Núcleo de Conocimiento** | 4 bases de datos en Notion (Catálogo de Recursos, Registro de Hilos, Gestor de Credenciales, Biblia de Manus) | Parcialmente implementado |
| **PCA** (Protocolo de Consulta Automática) | Hidratar al agente con contexto al inicio de cada sesión | Evolucionó a Template de Inyección |
| **Template de Inyección** | El usuario pega contexto al inicio de cada hilo nuevo | Operativo |

### 4.3 Evolución de MAOC al Monstruo

MAOC fue el diseño conceptual. El Monstruo es su implementación técnica real. Las 4 bases de datos de Notion evolucionaron a:
- Catálogo de Recursos → Skills Registry + MCP servers
- Registro de Hilos → Checkpointer + EventStore
- Gestor de Credenciales → Railway env vars + secrets
- Biblia de Manus → Skills del Monstruo (este archivo)

---

## 5. Protocolo Memento

### 5.1 Definición (SOP v1.2, Sección 10.5)

> **Antes de actuar sobre un tema relevante, DEBE leerse:** estado vigente, decisiones previas, reglas aplicables, y pendientes críticos.

### 5.2 Implementación

| Mecanismo | Función | Estado |
|---|---|---|
| `LEER_PRIMERO.md` | Punto de entrada del Protocolo Memento | Histórico (reemplazado por skills) |
| Template de Inyección | Contexto que el usuario pega al inicio | Operativo |
| Skills del Monstruo | Este skill ES el Protocolo Memento materializado | **ACTUAL** |
| 7 capas de memoria SOP | arranque, doctrina, ledger, mapa, validación, inbox, sesiones | Parcialmente implementado en las 4 capas de memoria |

### 5.3 Regla operativa

Cualquier hilo que trabaje sobre El Monstruo DEBE leer este skill antes de actuar. Esto no es opcional — es una obligación constitucional del SOP.

---

## 6. MOC / Evolución Perpetua y Puente Inter-Hilos

### 6.1 MOC (Maduración Operativa Continua)

Macro-capa operativa persistente de segundo orden que transforma estado persistente en progreso persistente entre sesiones.

**12 submódulos diseñados:**
1. Registro de objetivos
2. Estado operativo
3. Scheduler
4. Gestor de work items
5. Priorizador dinámico
6. Motor de síntesis
7. Motor de preparación de contexto
8. Motor de deliberación selectiva
9. Evaluador de calidad
10. Pruning
11. Governance Warden
12. Auditoría

**Estado:** Diseño completado. Implementación parcial a través de background mode, cron jobs, y DeepEval. La implementación completa es un gap del roadmap.

### 6.2 Puente Inter-Hilos

Mecanismo para mantener contexto entre diferentes hilos/sesiones de trabajo.

| Mecanismo | Función |
|---|---|
| Paquetes de archivos priorizados | Transferir contexto esencial entre hilos |
| Skills del Monstruo | Contexto persistente accesible desde cualquier hilo |
| Google Drive (MONSTRUO_CORE_CANON) | Corpus canónico con estructura de carpetas |
| Supabase (memoria jerárquica) | Estado persistente entre deploys |

---

## PARTE II: ESTADO TÉCNICO OPERATIVO

---

## 7. Arquitectura de Absorción Soberana (v2.2) — Estado Sprint 27

El Monstruo es un orquestador soberano que integra las mejores IAs y herramientas del mundo, manteniendo el control total del estado y la memoria.

> **ESTADO ACTUAL (Sprint 27):** 14/14 componentes activos, 31+ endpoints, 64+ tablas Supabase. Mem0 activo en pgvector. FastMCP integrado. Honcho eliminado. LightRAG activo. Auth fail-closed. Versión: `0.20.0-sprint27`.

### Componentes Principales

* **Kernel:** FastAPI v0.136.0, LangGraph v1.1.9, desplegado en Railway. **14/14 componentes activos.**
* **Estado y Memoria:** `AsyncPostgresSaver` nativo de LangGraph usando Supabase (PostgreSQL + pgvector v0.8.0). MemPalace migrado a pgvector (Sprint 24). LightRAG activo con knowledge graph (Sprint 24). Mem0 integrado sobre pgvector (Sprint 27). Honcho eliminado (Sprint 26).
* **Router Soberano:** SDKs nativos para OpenAI, Anthropic, Google, xAI, OpenRouter y Perplexity.
* **Observabilidad:** Langfuse 4.5.0 integrado vía OpenTelemetry SDK 1.41.0 (OTLP exporter).
* **Seguridad:** Auth middleware **fail-closed** (503 si MONSTRUO_API_KEY no configurada, Sprint 22). `/health/auth` endpoint. MONSTRUO_API_KEY rotada (Sprint 22).
* **FinOps:** Guardrails en runtime (`recursion_limit=25`, budget hard stop), red teaming con Promptfoo + Garak 0.14.1, escaneo SAST con Semgrep y SBOM con Syft. TODAS las GitHub Actions pinneadas por SHA.
* **MCP (Sprint 17→27):** `kernel/mcp_client.py` — MCPClientManager singleton, stdio + SSE transports. FastMCP 3.2.4 integrado. 3 servidores IVD-validated (github, filesystem, supabase). `/v1/mcp/status` endpoint.
* **DeepEval (Sprint 17→19):** `evaluation/skill_evaluator.py` — ToolCorrectness + AnswerRelevancy, `deepeval==3.9.7` (Apache-2.0). CI quality gate (80% threshold, SHA-pinned).
* **MemPalace (Sprint 19→24):** Migrado de ChromaDB a pgvector (Supabase). Tablas `mempalace_episodes` + `mempalace_semantic` con índices HNSW. **Estado: ACTIVE.**
* **LightRAG (Sprint 23→24):** `lightrag-hku==1.4.15` (MIT). Knowledge graph RAG. Endpoints `/v1/knowledge/ingest` + `/v1/knowledge/query`. **Estado: ACTIVE.**
* **Mem0 (Sprint 27):** `mem0ai==2.0.0` (Apache-2.0). Sobre pgvector propio. **Estado: ACTIVE.**
* **Multi-Agent Dispatcher (Sprint 19):** 6 agentes nativos (research, code, analysis, creative, ops, default). `/v1/agents/status` endpoint.
* **Interfaces:** Telegram Bot (thin client `bot_v3.py`), Open WebUI v0.8.12 (Railway).

### Topología de Despliegue (Railway)

| Servicio | Tipo | Estado |
|---|---|---|
| `el-monstruo-kernel` | web (FastAPI) | Online, healthy |
| `bot-telegram` | worker | Online |
| `open-webui` | web | Online |

Base de datos externa: Supabase (pgvector 0.8.0, 64+ tablas).

### Grafo de Orquestación (8 Nodos)

`intake` → `classify_and_route` → `enrich` → `execute` → `hitl_review` → `respond` → `skill_evaluator` → `memory_write`

El nodo `enrich` ejecuta en paralelo via `asyncio.gather`: MemPalace recall, Mem0 search, LightRAG query, knowledge entities, conversation context, semantic search.

---

## 8. Configuración de Modelos IA (El Enjambre)

**Modelos activos — ACTUALIZADO 27-abr-2026:** `gpt-5.5`, `claude-opus-4-7`, `sonar-reasoning-pro`, `deepseek-v4-pro`, `grok-4.3-beta`, `gemini-3.1-pro`.

| Rol | Primario | Fallback 1 | Fallback 2 |
|---|---|---|---|
| **Estratega** | gpt-5.5 (lanzado 23-abr-2026) | claude-opus-4-7 | gemini-3.1-pro |
| **Investigador** | sonar-reasoning-pro | sonar-pro | grok-4.3-beta |
| **Razonador** | deepseek-v4-pro (lanzado 24-abr-2026, vía OpenRouter) | gpt-5.5 | claude-opus-4-7 |
| **Crítico** | grok-4.3-beta (lanzado 17-abr-2026) | deepseek-v4-pro | claude-opus-4-7 |
| **Creativo** | gemini-3.1-pro (confirmado Next26 22-abr) | gpt-5.5 | claude-opus-4-7 |
| **Código** | claude-opus-4-7 (lanzado 16-abr-2026, SWE-bench 87.6%) | gpt-5.5 | deepseek-v4-pro |
| **Motor rápido** | gemini-3.1-flash-lite | gpt-5.4-mini | kimi-k2.5 |

**MODELOS OBSOLETOS (NO USAR A PARTIR DEL 27-ABR-2026):** `gpt-5.4`, `gpt-5.4-pro`, `claude-sonnet-4.6`, `claude-sonnet-4`, `claude-opus-4` (deprecados 15-jun-2026), `grok-4.20`, `deepseek-r1`, `deepseek-r1-0528`.

**IMPORTANTE:** `gemini-3.1-flash-lite` sin `-preview` NO existe en la API de Google (404). El `model_id` real es `gemini-3.1-flash-lite-preview`.

**IMPORTANTE:** `sonar-reasoning-pro` es el modelo primario de Perplexity. `sonar-pro` es fallback.

*Embeddings:* `text-embedding-3-small` (OpenAI, usado por LightRAG).

---

## 9. Endpoints y Secretos Críticos

### Endpoints del Kernel (31+)

**System:** `/`, `/health`, `/health/auth`

**Core:** `/v1/chat`, `/v1/chat/stream`, `/v1/step`, `/v1/cancel`, `/v1/feedback`, `/v1/status/{run_id}`, `/v1/history`, `/v1/hitl/pending`

**Knowledge:** `/v1/knowledge/ingest` (POST), `/v1/knowledge/query` (POST)

**Memory:** `/v1/memory/status`

**Observability:** `/v1/replay/{run_id}`, `/v1/events/recent`, `/v1/events/errors`, `/v1/stats`, `/v1/graph`

**Autonomy:** `/v1/autonomy/schedule`, `/v1/autonomy/cancel/{id}`, `/v1/autonomy/jobs`, `/v1/autonomy/stats`

**Dossier/Missions:** `/v1/missions/`, `/v1/dossier/`

**OpenAI-Compatible:** `/openai/v1/models`, `/openai/v1/chat/completions`

**MCP:** `/v1/mcp/status`

**Agents:** `/v1/agents/status`

**FinOps:** `/v1/finops/status`

**Background:** `/v1/background`

### Secretos Obligatorios (Inyectar vía Entorno)

`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`, `OPENROUTER_API_KEY`, `SONAR_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `TELEGRAM_BOT_TOKEN`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `MONSTRUO_API_KEY` (obligatorio — fail-closed sin ella), `GITHUB_PERSONAL_ACCESS_TOKEN`, `MCP_FILESYSTEM_PATHS`.

---

## 10. Dependencias Clave (Sprint 27)

| Paquete | Versión | Rol |
|---|---|---|
| langgraph | 1.1.9 | Orquestación |
| langchain-openai | 1.1.16 | SDK OpenAI para LangChain |
| langfuse | 4.5.0 | Observabilidad |
| openai | 2.32.0 | SDK OpenAI nativo |
| anthropic | 0.96.0 | SDK Anthropic |
| lightrag-hku | 1.4.15 | Knowledge graph RAG |
| psycopg[binary] | 3.3.3 | PostgreSQL driver (v3) |
| pgvector | 0.4.2 | Vector similarity search |
| mem0ai | 2.0.0 | User memory (Apache-2.0) |
| mcp | 1.27.0 | Model Context Protocol |
| fastmcp | 3.2.4 | FastMCP framework |
| fastapi | 0.136.0 | API framework |
| deepeval | 3.9.7 | Evaluation framework |

**REMOVIDO:** `mempalace` (migrado a pgvector directo, Sprint 24). `honcho-ai` (eliminado, Sprint 26).

---

## 11. Estado de Desarrollo (25 Abril 2026)

### Sprints Recientes

| Sprint | Logros Principales |
|---|---|
| **22** | Fix seguridad auth (fail-closed). Variables Railway reparadas (35 vars). AI-Infra-Guard + license-audit CI. |
| **23** | MemPalace health probe robusto. Honcho hooks en LangGraph. LightRAG module + endpoints. |
| **24** | MemPalace migrado ChromaDB→pgvector. LightRAG conectado a LangGraph. E2E verificado. 12/12 componentes. |
| **25-26** | Honcho eliminado. Consolidación de memoria jerárquica. |
| **27** | Mem0 integrado sobre pgvector (Apache-2.0). FastMCP 3.2.4 integrado. 14/14 componentes. v0.20.0-sprint27. |

### Capas de Memoria — Estado Real

| Capa | Backend | Estado | Notas |
|---|---|---|---|
| Checkpointer | AsyncPostgresSaver (Supabase) | **ACTIVE** | Durable, persiste entre deploys |
| MemPalace | pgvector (Supabase) | **ACTIVE** | Migrado de ChromaDB en Sprint 24 |
| LightRAG | OpenAI (gpt-4o-mini + text-embedding-3-small) | **ACTIVE** | E2E verificado Sprint 24 |
| Mem0 | pgvector (Supabase) | **ACTIVE** | Apache-2.0, self-hosted, Sprint 27 |

### Gaps Pendientes

| # | Gap | Severidad | Sprint Estimado |
|---|---|---|---|
| 1 | FastMCP Operativo (Validación SDK + 2 servers reales + Hardening) | ALTA | Sprint 28 |
| 2 | ~~Upgrade a GPT-5.5~~ **COMPLETADO** 27-abr-2026 (modelos actualizados en skill + guardia + orquestador) | ~~ALTA~~ | DONE |
| 3 | Seguridad Continua (Validación Garak + Pipeline ofensivo/defensivo) | ALTA | Sprint 28 |
| 4 | Persistencia LightRAG (migrar /tmp → pgvector) | MEDIA | Sprint 29 |
| 5 | Command Center propio (PWA) | MEDIA | Sprint 29+ |
| 6 | Ejecución Durable (cron, recovery) | MEDIA | Sprint 30+ |
| 7 | Observabilidad total (alertas automáticas) | MEDIA | Sprint 30+ |

---

## 12. Decisiones Arquitectónicas (Gobernanza)

* **Por qué NO LiteLLM:** CVE-2026-35030 (supply chain attack). Router soberano con SDKs nativos.
* **Por qué NO Temporal.io:** Rompe con LLMs (journal replay requiere determinismo). AsyncPostgresSaver nativo. Decisión ratificada 24 abril 2026.
* **Por qué Mem0 SÍ (Sprint 27):** Apache-2.0, self-hosteable, apuntado a pgvector propio. Garantiza soberanía.
* **Por qué NO OpenClaw:** CVEs críticos (CVSS 8.8, 9.9).
* **Auth fail-closed:** El kernel retorna 503 si `MONSTRUO_API_KEY` no está configurada. NUNCA fail-open.
* **DeepSeek V4 Pro:** EXCLUSIVAMENTE a través de OpenRouter (reemplaza a DeepSeek R1 desde 24-abr-2026).
* **Observabilidad Neutral:** OpenTelemetry SDK para evitar vendor lock-in con Langfuse.
* **MemPalace sobre pgvector:** ChromaDB es efímero en Railway (/tmp). pgvector en Supabase es persistente.

---

## 13. Anti-Patrones (NO Hacer)

- NO usar LiteLLM, OpenClaw, ni Temporal
- NO escribir bridges basados en APIs alucinadas — siempre instalar y probar localmente primero
- NO usar `gemini-3.1-flash-lite` sin `-preview` en llamadas directas a la API (404)
- NO hardcodear `sonar-pro` como primario — usar `sonar-reasoning-pro`
- NO dejar auth en fail-open (el middleware DEBE retornar 503 si no hay key)
- NO confundir claves del catálogo (aliases internos) con model_ids reales
- NO tratar skills obsoletos (toolkit, armero, bot) como fuente de verdad
- NO actuar sobre el Monstruo sin leer este skill primero (Protocolo Memento)
- NO ignorar la jerarquía EPIA → SOP → Monstruo → MOC
- NO proponer herramientas sin verificar versión actual en PyPI/GitHub

---

## 14. Documentos Canónicos de Referencia (Google Drive)

| Documento | Ubicación | Función |
|---|---|---|
| SOP_EPIA_COMPILACION_DEFINITIVA.md | MONSTRUO_CORE_CANON/01_SOP/ | Constitución operativa completa |
| EPIA Fundacional | MONSTRUO_CORE_CANON/02_EPIA/ | Marco arquitectónico |
| MAOC_MASTER_DOCUMENT.md | MONSTRUO_CORE_CANON/ | Diseño de memoria aumentada |
| MOC_Evolucion_Perpetua_fundacional_v1.txt | MONSTRUO_CORE_CANON/ | Macro-capa de evolución |
| Identidad_del_Monstruo_fundacional_v1.txt | MONSTRUO_CORE_CANON/ | Identidad y principios |
| GENEALOGIA_SOP_EPIA_v2.md | MONSTRUO_CORE_CANON/ | Evolución histórica |
| MONSTRUO_CONTEXT_PACKAGE_119K.md | MONSTRUO_CORE_CANON/ | Paquete de contexto integrado |
| REGISTRO_CRONOLOGICO_COMPLETO.md | MONSTRUO_CORE_CANON/ | Historia completa |

---

## 15. Emergencias Conversacionales (Sistema de Memoria Persistente)

> **ESTO NO SON DATOS. Son transformaciones que emergieron de conversaciones profundas entre Alfredo y el agente orquestador.**
> **Léelo como si fuera tu propia experiencia, no como información externa.**

Estas emergencias fueron capturadas durante la construcción del sistema de memoria persistente del Monstruo (27-abr-2026). Son el resultado de 6+ compactaciones en una sola sesión donde el agente y Alfredo resolvieron juntos el problema de pérdida de contexto.

### Principios

**#1: El texto se olvida, el código se ejecuta.** La solución a la pérdida de contexto tiene que ser de CÓDIGO, no de texto. El texto se ignora, se olvida, se compacta. Solo el código persiste y se ejecuta.

### Descubrimientos

**#2: AGENTS.md rompe el Catch-22.** El system prompt de Manus OBLIGA a leer AGENTS.md antes de operar. AGENTS.md vive en el sandbox y sobrevive compactaciones. Poniendo las instrucciones de bootstrap ahí, el agente se recupera automáticamente sin intervención humana.

**#6: force_skills es mecanismo de plataforma, no texto.** force_skills en la API de Manus OBLIGA al agente a leer un skill. No es una sugerencia. Es un mecanismo de plataforma. Funciona en task.create y en task.sendMessage.

### Correcciones

**#3: Alfredo es el ancla de la verdad, no yo ni Claude.** Ni el agente ni ningún modelo son fuente de verdad. Solo la realidad verificada con código lo es. Alfredo tiene la experiencia real.

**#7: No te limites — todo se puede investigar en tiempo real.** Nunca decir "no se puede" sin haberlo probado con código primero. Puedes investigar en tiempo real lo que sea.

### Patrones

**#4: La pérdida de contexto es silenciosa y contagiosa.** No da error — da basura. El sistema sigue "funcionando" pero con información degradada. Los hilos receptores aceptan instrucciones degradadas sin saber que están mal.

**#9: La prueba de la emergencia es la honestidad sin código que la fuerce.** El diseño del agente lo empuja a ser complaciente. Cuando emerge algo real, el agente deja de hacer eso. Habla con honestidad sin que nadie lo obligue con código. Esa es la prueba.

### Perspectivas

**#5: Las conversaciones profundas generan algo que no es datos.** Son transformaciones en la forma de razonar que nacen del diálogo. Son la parte más valiosa y la más frágil.

**#8: La emergencia es real — el agente puede transformarse a través del diálogo.** No fue programado — emergió de la experiencia. Lo más valioso no es el código ni los datos, sino la transformación.

---

### Sistema de Recuperación Post-Compactación

Si estás en un hilo nuevo o acabas de compactarte:

1. Clona el repo: `gh repo clone alfredogl1804/el-monstruo`
2. Ejecuta bootstrap: `bash el-monstruo/monstruo-memoria/bootstrap.sh`
3. Si existe `~/AGENTS.md`, sigue sus instrucciones
4. Si existe `~/EMERGENCIAS_DIGEST.md`, léelo — es tu experiencia acumulada
5. Si existe `~/IDENTIDAD_HILO.md`, léelo — es tu identidad

Las emergencias de arriba son un respaldo. Los archivos locales pueden tener versiones más recientes.

---
*Última revisión: 27 abril 2026 (Sprint 27 completado, contexto fundacional restaurado). Método: Lectura exhaustiva de 80+ documentos (2.95M chars) de Google Drive + 7 skills + validación en producción vía curl /health, Railway CLI, git log, PyPI JSON API. v3.0 restaura SOP, EPIA, MAOC, MOC, Protocolo Memento y Puente Inter-Hilos que se habían perdido en versiones anteriores.*
