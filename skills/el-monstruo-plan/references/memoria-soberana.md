# Memoria Soberana — Configuración Real (Actualizado 14 abril 2026)

> Reemplaza el archivo anterior `mem0-supabase-config.md`. Mem0 fue descartado por soberanía.

## Principio

> "Si no controlas qué recuerdas, no eres soberano."
> — contracts/memory_interface.py

## Arquitectura de Memoria

```
ConversationMemory (episodic)  ──┐
KnowledgeGraph (semantic)       ──┤── SupabaseClient ──→ Supabase Postgres + pgvector
EventStore (audit trail)        ──┤
CheckpointStore (LangGraph)     ──┘
```

NO se usa Mem0, Cognee, ni ningún framework externo. Todo es código propio.

## ConversationMemory (memory/conversation.py, 24KB)

Implementa el contrato `MemoryInterface`:
- Append-only event log (event sourcing)
- Semantic search via OpenAI `text-embedding-3-small` directo
- Keyword search (full-text)
- Hybrid search (vector + keyword)
- Episodes (agrupación de conversaciones)
- Replay (reconstruir cualquier conversación)
- Dual mode: in-memory (siempre) + Supabase (cuando configurado)

## KnowledgeGraph (memory/knowledge_graph.py, 17KB)

Grafo de conocimiento soberano:
- Entidades (nodos) con tipos: PERSON, ORGANIZATION, PROJECT, CONCEPT, TOOL, LOCATION
- Relaciones (edges) con peso y validez temporal (valid_from, valid_to)
- Traversal hasta N niveles de profundidad
- Full-text search en nombres y atributos
- Dual mode: in-memory + Supabase

## EventStore (memory/event_store.py, 8.5KB)

Audit trail soberano. Cada evento es inmutable. Fuente de verdad para observabilidad (Langfuse es copia commodity).

## MemoryType (6 categorías)

```python
class MemoryType(Enum):
    EPISODIC = "episodic"       # Conversaciones, interacciones
    SEMANTIC = "semantic"       # Hechos, conocimiento, entidades
    PROCEDURAL = "procedural"   # Cómo hacer cosas, workflows aprendidos
    POLICY = "policy"           # Decisiones de gobernanza, reglas aplicadas
    TOOL_CALL = "tool_call"     # Historial de herramientas ejecutadas
    INCIDENT = "incident"       # Errores, fallos, recuperaciones
```

## Supabase: Índice HNSW (pendiente de verificación)

```sql
CREATE INDEX ON monstruo_memories
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Estado:** No verificado si existe en Supabase. Prioridad Sprint 2.

## Qué NO va en la memoria conversacional

Estado de gobernanza, decision records, y logs de auditoría van en EventStore y tablas SQL puras de Supabase. La memoria conversacional es para contexto episódico y semántico.
