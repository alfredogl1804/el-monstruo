---
name: el-monstruo-estado
description: >-
  Estado canónico operativo, arquitectónico y documental de El Monstruo.
  Fuente única para entender qué existe, qué está activo, qué está obsoleto
  y qué debe cambiarse. Leer este skill recupera todo el contexto necesario.
  Usar cuando cualquier hilo necesite contexto completo del Monstruo.
metadata:
  version: 2.0.0
  status: ACTUAL
  owner: Alfredo Góngora
  last_reviewed: 2026-04-24 (Sprint 27 completado)
  review_trigger: cada sprint o cambio mayor
  sources_of_truth: repo-kernel, repo-bot, railway, skill-el-monstruo-core
---

# el-monstruo-estado

## 1) Resumen Ejecutivo

El Monstruo es el agente IA soberano de Alfredo Góngora, operativo 24/7 vía Telegram (@MounstroOC_bot). Compuesto por un **Kernel** (cerebro) y un **Bot** (interfaz), desplegados como servicios independientes en Railway.

**Estado al 22 abril 2026:** Sprint 27 completado. **Kernel v0.20.0-sprint27. 14/14 componentes activos.** MemPalace migrado de ChromaDB a pgvector (Supabase). LightRAG conectado al flujo LangGraph con E2E verificado. Auth fail-closed (Sprint 22). `sonar-reasoning-pro` como modelo primario de Perplexity. AI-Infra-Guard + license-audit en CI. 31+ endpoints HTTP. 4 capas de memoria (Checkpointer, MemPalace, LightRAG, Mem0 activas; Honcho eliminado).

| Tema | Estado | Veredicto |
|---|---|---|
| Kernel LangGraph (8 nodos) | ACTUAL | Base correcta, HITL v2 funcional, enrich con asyncio.gather |
| Router soberano (SDKs nativos) | ACTUAL | Decisión correcta; NO revertir a LiteLLM/OpenClaw |
| Memoria jerárquica (4 capas) | **SPRINT 27** | Checkpointer + MemPalace (pgvector) + LightRAG + Mem0 (pgvector) activos. Honcho eliminado. |
| Auth middleware | **SPRINT 22** | **Fail-closed** (503 si no hay key). `/health/auth` endpoint. |
| Bot Telegram | ACTUAL | `bot_v3.py` thin client |
| Open WebUI | ACTUAL | v0.8.12 desplegado en Railway |
| Persistencia LangGraph | COMPLETADO | `AsyncPostgresSaver` activo (Supabase) |
| Orquestación durable | COMPLETADO | PostgresSaver nativo. Temporal DESCARTADO. |
| CI/CD Security | **SPRINT 22** | AI-Infra-Guard + license-audit + Semgrep + SBOM (Syft). GitHub Actions SHA-pinned. |

### Dictamen ejecutivo

La arquitectura actual se mantiene. No integrar OpenClaw (CVEs), LiteLLM (CVE supply-chain), Mem0 (soberanía), ni Temporal (determinismo). La prioridad del Sprint 28 es integrar servidores FastMCP, actualizar a GPT-5.5, y ejecutar Garak Red Teaming. Honcho fue eliminado en Sprint 26.

---

## 2) Componentes Activos (14/14)

Verificado via `curl /health` el 22 abril 2026.

| Componente | Estado | Backend/Versión |
|---|---|---|
| kernel | active | FastAPI 0.136.0 + LangGraph 1.1.9 |
| event_store | active | Supabase |
| memory | active | Jerárquica (4 capas) |
| knowledge | active | LightRAG 1.4.15 |
| langfuse | active | Langfuse 4.5.0 |
| opentelemetry | active | OTLP SDK 1.41.0 |
| checkpointer | active | AsyncPostgresSaver (Supabase) |
| mempalace | **active** | pgvector (Supabase) — migrado de ChromaDB Sprint 24 |
| lightrag | **active** | OpenAI gpt-4o-mini + text-embedding-3-small |
| multi_agent | active | 6 agentes nativos |
| finops | active | Budget guardrails |
| mcp | active | 3 servidores (github, filesystem, supabase) |
| fastmcp | active | fastmcp 3.2.4 integrado |
| mem0 | active | mem0ai 2.0.0 sobre pgvector |

---

## 3) Arquitectura Actual

### 3.1 Kernel

| Elemento | Estado | Detalle |
|---|---|---|
| Framework API | ACTUAL | FastAPI v0.136.0 (Python 3.12-slim) |
| Orquestación | ACTUAL | LangGraph v1.1.9 StateGraph v2, 8 nodos |
| Nodos del grafo | ACTUAL | intake → classify_and_route → enrich → execute → hitl_review → respond → skill_evaluator → memory_write |
| Router de modelos | ACTUAL | Router soberano con SDKs nativos (6 proveedores) |
| Memoria | **SPRINT 27** | 4 capas: Checkpointer (pgvector), MemPalace (pgvector), LightRAG (OpenAI), Mem0 (pgvector). Honcho eliminado. |
| Event store | ACTUAL | EventStore propio, Supabase |
| Persistencia grafo | COMPLETADO | AsyncPostgresSaver (Supabase PostgreSQL) |
| HITL | ACTUAL | LangGraph v2 `interrupt()` / `Command(resume=)` |
| Observabilidad | ACTUAL | Langfuse 4.5.0 + OpenTelemetry SDK 1.41.0 |
| Auth middleware | **SPRINT 22** | `kernel/auth.py` — **fail-closed** (503 si no hay key). `/health/auth` endpoint. |
| Knowledge endpoints | **SPRINT 23-24** | `/v1/knowledge/ingest` + `/v1/knowledge/query` (LightRAG) |
| Herramientas | ACTUAL | web_search, consult_sabios, email, github, notion, delegate_task, schedule_task, user_dossier, call_webhook |
| Multi-Agent | ACTUAL | 6 agentes nativos (research, code, analysis, creative, ops, default) |
| MCP | ACTUAL | 3 servidores (github, filesystem, supabase), mcp==1.27.0 |
| DeepEval | ACTUAL | skill_evaluator.py, deepeval==3.9.7, CI quality gate 80% |

### 3.2 Capas de Memoria (detalle)

| Capa | Backend | Estado | Tablas/Storage | Sprint |
|---|---|---|---|---|
| Checkpointer | AsyncPostgresSaver (Supabase) | **ACTIVE** | checkpoint_* tables | Sprint 2 |
| MemPalace | pgvector (Supabase) | **ACTIVE** | `mempalace_episodes` + `mempalace_semantic` (HNSW) | Sprint 24 |
| LightRAG | OpenAI (gpt-4o-mini + text-embedding-3-small) | **ACTIVE** | /tmp (efímero — pendiente migrar) | Sprint 24 |
| Mem0 | pgvector (Supabase) | **ACTIVE** | mem0ai 2.0.0 integrado en bridge | Sprint 27 |

### 3.3 Modelos IA en Producción

| Rol | Modelo Principal | Fallback |
|---|---|---|
| Estratega / Sintetizador | gpt-5.4-pro-2026-03-05 (GPT-5.5 en Sprint 28) | claude-opus-4-7 |
| Investigador | **sonar-reasoning-pro** | sonar-pro |
| Razonador | deepseek-r1 (vía OpenRouter) | gpt-5.4 |
| Código | grok-4.20-0309-reasoning | claude-sonnet-4-6 |
| Clasificador / Chat rápido | gemini-3.1-flash-lite (alias → model_id: `-preview`) | gpt-5.4-mini |
| Arquitecto / Crítico | claude-opus-4-7 | gpt-5.4 |

**ALERTAS:** `gemini-3.1-flash-lite` sin `-preview` retorna 404 en Google API. `sonar-pro` sigue funcionando pero `sonar-reasoning-pro` es el primario.

### 3.4 Topología Railway

| Servicio | Tipo | Estado |
|---|---|---|
| el-monstruo-kernel | web (FastAPI) | Online, healthy |
| honcho-railway | **ELIMINADO** | Eliminado en Sprint 26 |
| bot-telegram | worker | Online |
| open-webui | web (v0.8.12) | Online |

DB externa: Supabase (pgvector 0.8.0, 64+ tablas).

### 3.5 Endpoints (31+)

System: `/`, `/health`, `/health/auth`
Core: `/v1/chat`, `/v1/chat/stream`, `/v1/step`, `/v1/cancel`, `/v1/feedback`, `/v1/status/{run_id}`, `/v1/history`, `/v1/hitl/pending`
Knowledge: `/v1/knowledge/ingest`, `/v1/knowledge/query`
Memory: `/v1/memory/status`
Observability: `/v1/replay/{run_id}`, `/v1/events/recent`, `/v1/events/errors`, `/v1/stats`, `/v1/graph`
Autonomy: `/v1/autonomy/schedule`, `/v1/autonomy/cancel/{id}`, `/v1/autonomy/jobs`, `/v1/autonomy/stats`
Dossier/Missions: `/v1/missions/`, `/v1/dossier/`
OpenAI-Compatible: `/openai/v1/models`, `/openai/v1/chat/completions`
MCP: `/v1/mcp/status`, Agents: `/v1/agents/status`, FinOps: `/v1/finops/status`, Background: `/v1/background`

---

## 4) Dependencias Clave (requirements.txt — Sprint 24)

| Paquete | Versión | Rol |
|---|---|---|
| langgraph | 1.1.9 | Orquestación |
| langchain-openai | 1.2.1 | SDK OpenAI para LangChain |
| langfuse | 4.5.1 | Observabilidad |
| mem0ai | 2.0.0 | Capa de memoria |
| fastmcp | 3.2.4 | Tool registry |
| openai | 2.32.0 | SDK OpenAI nativo |
| anthropic | 0.96.0 | SDK Anthropic |
| lightrag-hku | 1.4.15 | Knowledge graph RAG |
| psycopg[binary] | 3.3.3 | PostgreSQL driver (v3) |
| pgvector | 0.4.2 | Vector similarity search |
| honcho-ai | 2.1.1 | User modeling SDK |
| mcp | 1.27.0 | Model Context Protocol |
| fastapi | 0.136.0 | API framework |
| deepeval | 3.9.7 | Evaluation framework |

**REMOVIDO Sprint 24:** `mempalace` (migrado a pgvector directo).

---

## 5) Historial de Sprints Recientes

| Sprint | Fecha | Logros Principales |
|---|---|---|
| 22 | Abr 2026 | Auth fail-closed. Variables Railway reparadas (35 concatenadas→individuales). `/health/auth`. AI-Infra-Guard + license-audit CI. langgraph 1.1.9, langfuse 4.5.0, langchain-openai 1.1.16. |
| 23 | Abr 2026 | MemPalace health probe robusto. Honcho hooks en LangGraph (enrich + memory_write). LightRAG module + endpoints `/v1/knowledge/*`. Compliance semgrep (0 imports). |
| 24 | Abr 2026 | **MemPalace ChromaDB→pgvector** (Supabase, HNSW). **LightRAG conectado a LangGraph** (enrich node, asyncio.gather). E2E verificado (ingestión + consulta). **12/12 componentes activos.** |
| 25-26 | Abr 2026 | FastMCP integrado. Honcho eliminado. |
| 27 | Abr 2026 | **Mem0 activo (mem0ai==2.0.0 + pgvector)**. Dependencias actualizadas (langchain-openai 1.2.1, langfuse 4.5.1). **14/14 componentes activos.** Versión 0.20.0-sprint27. |

---

## 6) Gaps Pendientes

| # | Gap | Severidad | Notas |
|---|---|---|---|
| 1 | FastMCP real | ALTA | Sprint 28 (ej. mcp_github) |
| 2 | Upgrade a GPT-5.5 | ALTA | Sprint 28 (gpt-5.5-pro-2026-04-23) |
| 3 | Test E2E completo (mensaje→todas las capas) | MEDIA | Verificar flujo real con Telegram |
| 4 | Garak red team scan | ALTA | Sprint 28 (contra /v1/chat) |
| 5 | Command Center PWA | MEDIA | Reemplazar Open WebUI |
| 6 | Tool Registry dinámico | CERRADO | FastMCP integrado en Sprint 26 |

---

## 7) Anti-Patrones (NO Hacer)

NO usar: LiteLLM (CVE supply-chain), Temporal (determinismo), OpenClaw (CVEs CVSS 8.8/9.9). Nota: Mem0 fue readmitido en Sprint 27 porque es Apache-2.0 y self-hosteable. NO escribir bridges sobre APIs alucinadas — siempre instalar y probar localmente. NO dejar auth en fail-open. NO hardcodear `sonar-pro` como primario. NO usar `gemini-3.1-flash-lite` sin `-preview` en llamadas directas a Google API.

---

## 8) Referencia Cruzada

Para detalles completos de arquitectura, secretos, decisiones de gobernanza, y fallback chains: leer `el-monstruo-core/SKILL.md`.

Skills obsoletos (NO usar como fuente de verdad): `el-monstruo-toolkit`, `el-monstruo-armero`, `el-monstruo-bot`.

---
*Última revisión: 24 abril 2026 (Sprint 27). Método: curl /health, Railway CLI, git log, PyPI JSON API, tests E2E. IVD Sprint 27: 38/38 PASS (100%).*
