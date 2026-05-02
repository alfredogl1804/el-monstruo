# Investigación: Los Tres Sabios — Gateway Multi-Agente
## Fecha: 2 mayo 2026
## Fuentes: Perplexity Sonar Pro + Gemini 2.5 Flash

---

## Pregunta 1: Cold Start de Railway para Boot Context

### Problema:
Gateway y Kernel están en Railway. Ambos se duermen tras inactividad. Cuando el usuario abre la app, el boot context request dispara un cold start de 45 segundos.

### Solución Recomendada: Edge Cache + Background Sync (Opción 1 de Perplexity)

**Implementación:**
1. Desplegar un Cloudflare Worker (o Supabase Edge Function) que sirva el último estado de conversación desde un KV store
2. El Gateway escribe el estado de conversación al cache en cada actualización
3. El cliente primero golpea el edge function → respuesta en ~50ms
4. En background, el cliente refresca el estado cuando el Gateway despierta

**Alternativa pragmática (Opción 3):** Stale cache + background sync
- Redis en Railway (o Supabase directamente) como cache
- Retorna estado "stale" inmediatamente (<100ms)
- Dispara refresh en background
- El usuario ve la conversación anterior instantáneamente, se actualiza si hay algo nuevo

### Decisión para El Monstruo:
**Usar Supabase directamente como cache** — ya tenemos la conversation_memory ahí. El boot context endpoint puede leer directamente de Supabase sin pasar por el kernel. El Gateway puede tener un endpoint `/v1/boot` que:
1. Lee los últimos N mensajes de `conversation_events` en Supabase
2. Lee el `project_state` activo
3. Retorna todo al cliente en <100ms (Supabase no duerme)

**El kernel NO necesita estar despierto para el boot context.** Solo necesita estar despierto para procesar nuevos mensajes.

---

## Pregunta 2: Límites del Checkpointer PostgresSaver de LangGraph

### Hallazgos:
- **No hay límite inherente** más allá de la capacidad de PostgreSQL (~1GB por campo)
- **No hay compactación built-in** — la tabla crece indefinidamente
- **Performance degrada** con el tiempo: queries más lentas, más I/O, más vacuuming
- **No hay TTL nativo** en la versión open-source

### Estrategias de Producción:
1. **TTL con cron:** `DELETE FROM checkpoints WHERE created_at < NOW() - INTERVAL '30 days'`
2. **Minimizar escrituras:** Usar `write_mode: "exit"` para solo guardar al final del run
3. **Offload objetos grandes:** Guardar blobs en S3, solo refs en el state
4. **VACUUM ANALYZE periódico:** Mantener índices saludables

### Decisión para El Monstruo:
- Implementar un cron job que borre checkpoints > 7 días (el conversation_memory en Supabase es la fuente de verdad, no los checkpoints)
- Los checkpoints son solo para "reanudar" un run interrumpido, no para historial largo
- El historial largo vive en conversation_memory (Supabase) con el three_layer_memory

---

## Pregunta 3: Multi-Dispositivo (Mac + iPhone)

### Recomendación unánime: Backend (Supabase) como fuente de verdad

**Razones:**
- El thread_id es un pointer al estado que YA vive en el backend
- Cross-platform sin dependencia de Apple
- Extensible a futuros dispositivos
- Supabase Realtime puede notificar cambios

**Implementación:**
- Tabla `user_sessions` en Supabase con columna `active_thread_id`
- Al abrir la app: leer `active_thread_id` de Supabase
- Al cambiar de thread: actualizar en Supabase
- SharedPreferences como cache local (fallback offline)
- Si hay conflicto: el backend gana siempre

**NO usar iCloud KeyValueStore:**
- Solo Apple (no extensible)
- No es la fuente de verdad (el estado está en el backend)
- Complejidad extra sin beneficio real para single-user

### Decisión para El Monstruo:
- Agregar columna `active_thread_id` a la tabla de usuario en Supabase
- ThreadPersistence (SharedPreferences) es el cache local
- Al boot: primero leer local (instantáneo), luego verificar con Supabase (async)
- Si difieren: Supabase gana, actualizar local

---

## Pregunta 4: Compactación de Contexto para Threads Largos

### Recomendación: Hierarchical Memory (Opción B)

**Arquitectura de 3 capas en el LangGraph state:**

```python
class ThreadState(TypedDict):
    messages: List[AnyMessage]       # Últimos N mensajes completos (short-term)
    long_term_summary: str           # Resumen acumulado de interacciones antiguas
    key_facts: List[str]             # Hechos críticos extraídos (entities, decisiones)
```

**Implementación:**
1. **Nodo de compactación** que se ejecuta cada N mensajes (e.g., cada 20):
   - Toma los mensajes más viejos del buffer
   - Los resume con LLM
   - Agrega el resumen a `long_term_summary`
   - Extrae key_facts nuevos
   - Borra los mensajes originales del state
2. **Window size:** Mantener últimos 20-30 mensajes completos
3. **Trigger:** Cuando `len(messages) > 30`, compactar los primeros 20 en summary

**Ventajas sobre las alternativas:**
- Sliding window (A): Pierde información — no hay resumen
- Thread rotation (C): Rompe la continuidad — el usuario tiene que "empezar de nuevo"
- Hierarchical (B): Mantiene todo pero compacto — el LLM siempre tiene el summary + recientes

### Decisión para El Monstruo:
El kernel YA tiene un sistema de three_layer_memory (core, index, doc). La compactación se puede implementar como un nodo adicional en el grafo que:
1. Detecta cuando el state tiene > 30 mensajes
2. Llama a LLM para resumir los primeros 20
3. Actualiza el `long_term_summary` en el state
4. Opcionalmente guarda key_facts en la capa `core` de three_layer_memory

---

## Resumen de Decisiones

| Problema | Solución | Esfuerzo |
|---|---|---|
| Cold start boot | Leer de Supabase directo (sin kernel) | 4h |
| Checkpointer growth | Cron TTL 7 días + VACUUM | 2h |
| Multi-dispositivo | Supabase como source of truth + local cache | 6h |
| Compactación | Nodo hierarchical memory en LangGraph | 12h |
| Long-running tasks | Webhook + SSE (ya tenemos WebSocket) | 8h |

---

## Próximos Pasos Recomendados (en orden)

1. **Boot Context endpoint** — Gateway lee de Supabase directo, no necesita kernel
2. **Multi-device sync** — Agregar `active_thread_id` a Supabase
3. **Compactación** — Nodo en el grafo LangGraph
4. **Cron TTL** — Limpiar checkpoints viejos
5. **Webhook para tareas largas** — Cuando se integren agentes externos
