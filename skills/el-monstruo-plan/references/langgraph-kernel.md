# LangGraph Kernel — Diseño del Grafo (Actualizado 14 abril 2026)

> Verificado contra código real en `kernel/engine.py` (627 líneas) y `kernel/nodes.py` (987 líneas).

## Grafo Real: 7 Nodos

```
intake → classify_and_route → enrich → execute → hitl_review → respond → memory_write
```

Nota: `classify` y `route` fueron fusionados en un solo nodo `classify_and_route` (OPT-1).

## Nodos del Grafo

### 1. `intake`
Recibe mensaje via HTTP POST /v1/chat. Normaliza formato. Adjunta metadata (user_id, timestamp, channel, thread_id).

### 2. `classify_and_route`
Determina el modo operativo: `chat`, `deep_think`, `execute`, `background`. Usa clasificador con gemini-3.1-flash-lite. Selecciona modelo según rol y modo consultando fallback chains en `config/model_catalog.py`.

### 3. `enrich`
Consulta memoria soberana (ConversationMemory) para contexto relevante. Construye prompt enriquecido con User Dossier + system prompts + memoria episódica.

### 4. `execute`
Llama al modelo seleccionado via router soberano (`router/engine.py` + `router/llm_client.py`). SDKs nativos de OpenAI, Anthropic, Google, xAI, Perplexity, OpenRouter. NO LiteLLM.

### 5. `hitl_review`
Nodo de gobernanza. Evalúa la respuesta contra Policy Engine (7 reglas) + Composite Risk Scoring. Si `requires_approval = true` → ejecuta `interrupt()` (LangGraph v2). El grafo se pausa y espera feedback humano via POST /v1/feedback.

### 6. `respond`
Formatea respuesta para el canal de origen. Incluye metadata: model_used, latency_ms, cost_usd, policy_class, governance decision.

### 7. `memory_write`
Guarda la interacción en memoria soberana. Actualiza EventStore (audit trail).

## Checkpointing — GAP PENDIENTE

**Estado actual:** `MemorySaver` (en memoria, volátil).

**Problema:** Si Railway reinicia durante un HITL pendiente, el checkpoint se pierde. El usuario presiona Aprobar pero el grafo ya no existe.

**Fix requerido (Sprint 2, prioridad ALTA):**

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

checkpointer = AsyncPostgresSaver.from_conn_string(SUPABASE_DB_URL)
graph = builder.compile(checkpointer=checkpointer)
```

## Human-in-the-Loop — Implementación v2

**NO usar** el patrón v1 (`interrupt_before=["execute"]`). La implementación real usa LangGraph v2:

```python
# Dentro del nodo hitl_review:
from langgraph.types import interrupt, Command

if requires_approval:
    feedback = interrupt({"proposed_response": response, "risk_score": score})
    # El grafo se pausa aquí hasta que llega POST /v1/feedback
    # Luego resume con Command(resume={"decision": "approve"})
```

Ventaja: permite lógica condicional DENTRO del nodo antes de decidir si interrumpir.

## Streaming

El kernel tiene método `stream()` que emite SSE events. Endpoint: POST /v1/chat/stream.

## Observabilidad

Bridge pattern: `observability/langfuse_bridge.py` registra trazas en Langfuse como copia. La fuente de verdad es `memory/event_store.py` (EventStore soberano). NO se usan callbacks nativos de LangGraph para Langfuse.

## Memoria — Implementación Soberana

**NO se usa Mem0.** La memoria es 100% propia:

- `memory/conversation.py` (24KB) — ConversationMemory con event sourcing, semantic search via OpenAI embeddings, keyword search, hybrid search, episodes, replay.
- `memory/knowledge_graph.py` (17KB) — Entidades, relaciones, traversal temporal, weighted relations.
- `memory/event_store.py` (8.5KB) — Append-only event log soberano.
- `memory/checkpoint_store.py` (14.8KB) — LangGraph checkpoints.
- `memory/supabase_client.py` (6.6KB) — Conexión directa a Supabase.

Contrato: `contracts/memory_interface.py` — *"Ningún framework externo (Mem0, Cognee, etc.) es source of truth."*
