---
name: el-monstruo-plan
description: "Blueprint de implementación del Monstruo — el asistente IA soberano de Alfredo. Use when building, modifying, or debugging any component of El Monstruo's technical stack, when making architecture decisions, when selecting or configuring tools (LangGraph, Supabase, Langfuse), or when planning sprints. Contains verified component versions, security alerts, fallback chains, build plan calibrated to WAP mode, and orchestration evaluation (Temporal DESCARTADO, PostgresSaver GANADOR). ACTUALIZADO 29 abril 2026 (Sprint 33 en producción)."
---

# El Monstruo — Plan de Implementación (Actualizado 29 abril 2026)

Blueprint verificado contra código real en producción, Railway LIVE, y endpoints testeados. Cada componente fue cruzado contra repos reales, no contra planes previos.

> **ESTADO ACTUAL (Sprint 33):** 16/16 componentes activos, versión `0.26.0-sprint33`. Embrión activo con 435+ ciclos. Manus M2M Bridge (tools/manus_bridge.py) en main. Self-Evaluation Loop y Memory Consolidation completados en Sprint 34.

> **REGLA ANTI-DESVÍO:** Este skill refleja lo que REALMENTE está construido y desplegado. NO lo que se planeó originalmente. Si hay divergencia entre este skill y el código real, el código real gana.

## Arquitectura Real: 6 Módulos + 4 Modos

**Flujo real en producción:** Telegram → Bot (thin client) → Kernel HTTP API → Router Soberano → Modelo IA → Memoria Soberana (4 capas) → Respuesta

### Decisiones Arquitectónicas Tomadas (NO revertir)

| Decisión | Plan Original | Realidad | Razón |
|---|---|---|---|
| Router | LiteLLM 1.83.3 | **Router soberano con SDKs nativos** | CVE-2026-35030 (supply-chain attack). LiteLLM descartado permanentemente. |
| Memoria | Honcho | **Memoria jerárquica propia** (4 capas: Checkpointer + MemPalace + LightRAG + Mem0) | Honcho eliminado. Mem0 readmitido en Sprint 27 (es Apache-2.0 y self-hosteable). |
| MemPalace backend | ChromaDB local | **pgvector (Supabase)** | ChromaDB efímero en Railway (/tmp). pgvector persistente. Sprint 24. |
| LightRAG | No planeado | **lightrag-hku 1.4.15** (knowledge graph RAG) | Conectado a LangGraph enrich node. Sprint 24. |
| HITL | `interrupt_before=["execute"]` (v1) | **`interrupt()` dentro del nodo** (LangGraph v2) | Superior: lógica condicional dentro del nodo. |
| Checkpointing | PostgresSaver desde día 1 | **AsyncPostgresSaver** (Supabase) | COMPLETADO Sprint 2. |
| Durable Execution | Temporal (evaluado) | **LangGraph PostgresSaver** (nativo) | Temporal DESCARTADO: rompe con LLM calls (requiere determinismo). |
| Auth | Fail-open (dev mode) | **Fail-closed** (503 si no hay key) | Sprint 22. NUNCA volver a fail-open. |
| Consola PWA | Next.js 16 + Vercel | **Open WebUI v0.8.12** | Railway. Conectada via adaptador OpenAI. |
| M2M Bridge | No planeado | **tools/manus_bridge.py v2.1** | Embrión puede delegar tareas a Manus via API. Sprint 30. |

## Stack Técnico REAL (verificado 29 abril 2026)

| Módulo | Herramienta | Versión | Notas |
|---|---|---|---|
| Kernel | LangGraph | 1.1.9 | 8 nodos, HITL v2, 31+ endpoints HTTP |
| Router | **Router soberano** (SDKs nativos) | N/A | OpenAI, Anthropic, Google, xAI, Perplexity, OpenRouter. NO LiteLLM. |
| Memoria | **Implementación jerárquica** | N/A | Checkpointer + MemPalace (pgvector) + LightRAG + Mem0 (pgvector). Honcho eliminado. |
| Estado | Supabase Postgres | pgvector 0.8.0 | 64+ tablas. MemPalace usa pgvector directo. |
| Observabilidad | Langfuse | 4.5.0 | Bridge pattern: EventStore soberano + Langfuse como copia commodity. |
| Gobernanza | **Policy Engine propio** | N/A | 7 reglas, Composite Risk Scoring, Action Envelope + Validator. |
| Interfaz | Telegram (@MounstroOC_bot) | python-telegram-bot 22.7 | Bot thin client con HITL inline keyboard. |
| Deploy | Railway | **4 servicios** | kernel (web) + bot (worker) + open-webui (web) + embrion (loop). |
| CI/CD | GitHub Actions | SHA-pinned | AI-Infra-Guard, license-audit, Semgrep, SBOM (Syft), DeepEval. |
| Embrión | Loop autónomo Python | Sprint 33 | 435+ ciclos, 15 latidos, 128 memorias, activo 24/7. |
| M2M Bridge | tools/manus_bridge.py | v2.1 | Dual account (Google/Apple), retry, polling. En main desde Sprint 30. |

### Modelos disponibles en producción (verificado /health 29 abril 2026)

- `gpt-5.5`
- `claude-opus-4-7`
- `gemini-3.1-pro-preview`
- `sonar-reasoning-pro`

### Alerta Permanente: NO usar LiteLLM ni Temporal

**LiteLLM:** CVE-2026-35030 (bypass OIDC). Router soberano elimina dependencia de supply-chain.

**Mem0:** *Excepción resuelta.* En Sprint 27 se comprobó que `mem0ai` es Apache-2.0 y se puede apuntar a pgvector propio, garantizando soberanía. Fue integrado exitosamente.

**Temporal:** Frameworks de durable execution basados en journal replay requieren determinismo. LLMs son no-determinísticos. LangGraph PostgresSaver usa checkpoint caching.

## Fallback Chains REALES (14 roles, config/model_catalog.py)

| Rol | Primario | Fallback 1 | Fallback 2 | Fallback 3 |
|---|---|---|---|---|
| Estratega | gpt-5.5 | claude-opus-4-7 | gemini-3.1-pro | - |
| Investigador | **sonar-reasoning-pro** | sonar-pro | grok-4.20 | gpt-5.5 |
| Razonador | deepseek-r1-0528 | gpt-5.5 | claude-opus-4-7 | - |
| Sintetizador | gpt-5.5 | claude-opus-4-7 | gemini-3.1-pro | - |
| Crítico | grok-4.20 | deepseek-r1-0528 | claude-opus-4-7 | - |
| Creativo | gemini-3.1-pro | gpt-5.5 | claude-opus-4-7 | - |
| Código | claude-sonnet-4-6 | gpt-5.5 | deepseek-r1-0528 | - |
| Análisis | gpt-5.5 | claude-opus-4-7 | sonar-reasoning-pro | - |
| Motor barato | gemini-3.1-flash-lite-preview | gpt-5.5-mini | kimi-k2.5 | - |
| Clasificador | gemini-3.1-flash-lite-preview | gpt-5.5-mini | - | - |
| Planificador | gpt-5.5 | claude-opus-4-7 | - | - |
| Ejecutor | claude-sonnet-4-6 | gpt-5.5 | - | - |
| Arquitecto | claude-opus-4-7 | gpt-5.5 | - | - |
| Chat rápido | gemini-3.1-flash-lite-preview | gpt-5.5-mini | - | - |

**NOTA:** `gemini-3.1-flash-lite` es un alias interno. El `model_id` real es `gemini-3.1-flash-lite-preview`. Sin `-preview` retorna 404 en Google API.

## 4 Modos Operativos — Estado Real

| Modo | Estado | Pipeline Real |
|---|---|---|
| `chat` | **FUNCIONA** | classify → gemini-flash-lite → respuesta directa (sin HITL) |
| `deep_think` | **PARCIAL (60%)** | IntentType existe, enrich consulta memoria, falta diferenciación de modelo fuerte |
| `execute` | **FUNCIONA** | classify → claude-sonnet-4-6 → HITL (interrupt) → aprobación → respuesta |
| `background` | **10%** | IntentType existe en enum, sin pipeline de jobs async |

## Grafo LangGraph REAL (8 nodos)

```
intake → classify_and_route → enrich → execute → hitl_review → respond → skill_evaluator → memory_write
```

El nodo `enrich` ejecuta en paralelo via `asyncio.gather`: MemPalace recall, Mem0 search, LightRAG query, knowledge entities, conversation context, semantic search.

## Gaps Cerrados (Sprints 2-34)

| # | Gap | Estado | Sprint |
|---|---|---|---|
| 1 | MemorySaver → PostgresSaver | **CERRADO** | Sprint 2 |
| 2 | Fallback chains automáticos | **CERRADO** | Sprint 7 |
| 3 | Modo background (async queue) | **CERRADO** | Sprint 5+8 |
| 4 | Consola PWA | **CERRADO** | Sprint 2 (Open WebUI) |
| 5 | Tablas de conciencia | **CERRADO** | Sprint 9 (user_dossier + active_missions) |
| 6 | Auth fail-closed | **CERRADO** | Sprint 22 |
| 7 | Variables Railway corruptas | **CERRADO** | Sprint 22 (35 vars reparadas) |
| 8 | MemPalace activo (persistente) | **CERRADO** | Sprint 24 (pgvector) |
| 9 | LightRAG activo (knowledge graph) | **CERRADO** | Sprint 24 |
| 10 | CI Security (AIG + license-audit) | **CERRADO** | Sprint 22 |
| 11 | FastMCP integrado | **CERRADO** | Sprint 27 |
| 12 | Mem0 integrado (pgvector soberano) | **CERRADO** | Sprint 27 |
| 13 | Embrión — loop autónomo | **CERRADO** | Sprint 30 |
| 14 | Manus M2M Bridge (tools/manus_bridge.py) | **CERRADO** | Sprint 30 |
| 15 | Self-Evaluation Loop | **CERRADO** | Sprint 34 |
| 16 | Memory Consolidation (episodic → semantic) | **CERRADO** | Sprint 34 |
| 17 | Manus Bridge async + tool_dispatch | **CERRADO** | Sprint 34 |

## Gaps Restantes

| # | Gap | Severidad | Sprint Estimado |
|---|---|---|---|
| 1 | Modo `deep_think` completo (60% → 100%) | ALTA | Sprint 35 |
| 2 | Modo `background` completo (10% → 100%) | ALTA | Sprint 35 |
| 3 | Benchmark soberano para modelos (gates de promoción) | ALTA | Sprint 35 |
| 4 | Seguridad Continua (Validación Garak + Pipeline ofensivo/defensivo) | ALTA | Sprint 35 |
| 5 | Persistencia LightRAG (migrar /tmp → pgvector) | MEDIA | Sprint 36 |
| 6 | Command Center propio (PWA) | MEDIA | Sprint 36+ |
| 7 | Observabilidad total (alertas automáticas) | MEDIA | Sprint 36+ |
| 8 | Emergencias → Embrión (inyección de contexto operativo) | MEDIA | Pendiente decisión Alfredo |

## Evaluación de Orquestación Durable (15 abril 2026)

| Plataforma | Licencia | Veredicto | Razón |
|---|---|---|---|
| **LangGraph PostgresSaver** | MIT/Apache | **GANADOR** | Nativo, 0 infra extra, checkpoint caching |
| **Hatchet** | MIT | **Plan B futuro** | Solo PostgreSQL, diseñado para AI agents |
| Temporal | MIT | **DESCARTADO PERMANENTE** | Rompe con LLM calls (journal replay). ADR formal pendiente Sprint 35. |
| Restate | BSL 1.1 | **DESCARTADO** | Licencia no open source |
| Windmill | AGPL | **DESCARTADO** | 3 CVEs graves abril 2026 |

---
*Última revisión: 29 abril 2026 (Sprint 33 en producción, Sprint 34 mergeado). Método: curl /health, git log, API GitHub. Embrión: 435 ciclos activos.*
