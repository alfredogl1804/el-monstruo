# Las 19 Capas del Monstruo — Mapa Completo (Actualizado 14 abril 2026)

> Verificado contra código real, Railway LIVE, y endpoints de producción.

## Clasificación

Las capas se dividen en 3 zonas: **Núcleo Soberano** (control total, código propio), **Híbrida** (herramientas open-source con configuración soberana), y **Commodity** (herramientas intercambiables).

## Mapa de Capas — Con Estado Real

| # | Capa | Zona | Plan Original | Realidad (14 abr 2026) | Estado | Sprint |
|---|---|---|---|---|---|---|
| 1 | Kernel / Orquestador | Soberano | LangGraph 1.1.6 | **LangGraph 1.1.6** — 7 nodos, 15 endpoints, HITL v2 | **COMPLETO** | 1 |
| 2 | Router Inteligente | Soberano | LiteLLM 1.83.3 | **Router soberano** — SDKs nativos (6 proveedores), 14 roles, fallback chains | **COMPLETO** (cambiado) | 1 |
| 3 | Memoria Soberana | Soberano | Mem0 OSS + Supabase | **Memoria propia** — ConversationMemory + KnowledgeGraph + EventStore. NO Mem0. | **COMPLETO** (cambiado) | 1 |
| 4 | Conciencia / Estado | Soberano | Tablas Supabase + Mission Control | EventStore + CheckpointStore. Sin Mission Control ni tablas de conciencia. | **PARCIAL (60%)** | 1 |
| 5 | Políticas / Guardrails | Híbrida | Guardrails AI o Galileo (Sprint 2) | **Policy Engine propio** — 7 reglas + Composite Risk Scoring + Action Envelope/Validator | **ADELANTADO** (hecho en S1) | 2→1 |
| 6 | Registry de Habilidades | Híbrida | JSON/YAML manual → MCP | No implementado | **PENDIENTE** | 2 |
| 7 | Command Center (Consola PWA) | Híbrida | Next.js 16 + shadcn/ui | No implementado. Se priorizó Telegram. | **PENDIENTE** | 1→2 |
| 8 | Observabilidad / Trazas | Híbrida | Langfuse + OTel | **Langfuse 4.2.0** — Bridge pattern (EventStore soberano + Langfuse copia). OTel bridge existe. | **COMPLETO (85%)** | 1 |
| 9 | Tracking de Costes | Híbrida | AgentOps | Kernel reporta cost_usd por request, sin tracking acumulado | **PARCIAL (20%)** | 2 |
| 10 | Gateway Multi-Modelo | Commodity | LiteLLM 1.83.3 | **Fusionado con Capa 2** — Router soberano cubre ambas funciones | **COMPLETO** (fusionado) | 1 |
| 11 | Ejecución Durable | Commodity | Temporal | No implementado | **PENDIENTE** | 3 |
| 12 | Búsqueda Web | Commodity | Tavily API + Perplexity | No implementado como tool del kernel | **PENDIENTE** | 2 |
| 13 | Interfaz de Chat | Commodity | Consola PWA + Telegram | **Solo Telegram** — @MounstroOC_bot con HITL inline keyboard | **PARCIAL (50%)** | 1 |
| 14 | UI Streaming | Commodity | Vercel AI SDK 7.0 | SSE streaming en kernel (POST /v1/chat/stream). Sin Vercel AI SDK. | **PARCIAL (40%)** | 1 |
| 15 | Automatización Navegador | Commodity | Playwright | No implementado | **PENDIENTE** | 3 |
| 16 | Conectividad MCP | Commodity | MCP Servers | No implementado | **PENDIENTE** | 2 |
| 17 | Evaluación RAG | CI/CD | Ragas | No implementado | **PENDIENTE** | 3 |
| 18 | Testing de Prompts | CI/CD | Promptfoo | No implementado | **PENDIENTE** | 3 |
| 19 | Sandboxing de Código | Commodity | E2B | No implementado | **PENDIENTE** | 3 |

## Sprint Roadmap Actualizado

**Sprint 1 (COMPLETADO ~70%):** Capas 1, 2, 3, 5, 8, 10 completas. Capas 4, 13, 14 parciales. Capa 7 postergada.

**Sprint 2 (siguiente):** Capas 6, 7, 9, 12, 16 + fix MemorySaver→PostgresSaver + fallback chains automáticos + modo background.

**Sprint 3 (futuro):** Capas 11, 15, 17, 18, 19 — ejecución durable, browser automation, testing, sandboxing.

## Divergencias Permanentes del Plan Original

1. **LiteLLM descartado** → Router soberano con SDKs nativos (CVE-2026-35030)
2. **Mem0 descartado** → Memoria soberana propia (principio de soberanía)
3. **Capa 5 adelantada** → Policy Engine implementado en Sprint 1 (no Sprint 2)
4. **Capas 2 y 10 fusionadas** → Un solo router soberano cubre ambas
5. **HITL v2** → Superior al plan original (interrupt() dentro del nodo vs interrupt_before)
6. **Dockerfile → Dockerfile.web** → Renombrado por recomendación del Consejo de Sabios
