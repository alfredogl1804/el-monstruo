# Validación en Tiempo Real — Los Tres Sabios (2 mayo 2026)

## Correcciones a la investigación original

---

## 1. Railway Cold Start — CONFIRMADO pero con matiz

**Estado actual (mayo 2026):**
- Railway tiene "Serverless" (antes llamado "App-Sleeping") como feature OPT-IN
- Si NO activas Serverless, tu servicio es **always-on** por defecto
- El cold start SOLO ocurre si tú activas Serverless explícitamente
- Railway NO duerme servicios automáticamente en planes pagados sin Serverless habilitado

**Corrección a mi investigación:**
> Mi recomendación de "edge cache para mitigar cold start" asumía que Railway duerme los servicios automáticamente. **Esto es FALSO.** Si el kernel y gateway están en Railway sin Serverless activado, son always-on. No hay cold start.

**Pregunta para Alfredo:** ¿Tienes Serverless activado en el kernel y gateway? Si sí, ¿es por ahorro de costos? Porque si lo desactivas, el cold start desaparece completamente.

**Implicación:** Si el kernel es always-on, el Boot Context puede ir directo al kernel sin necesidad de cache intermedio. Simplifica enormemente la arquitectura.

---

## 2. LangGraph Checkpoint TTL — CONFIRMADO: No existe built-in

**Estado actual (mayo 2026):**
- El foro de LangChain (febrero 2026) confirma que NO hay TTL built-in en PostgresSaver
- La gente sigue preguntando cómo hacer cleanup manual
- LangGraph Support (nov 2025) menciona que "TTL defines how long checkpoints are retained" pero esto es solo en LangGraph Cloud (closed source), NO en self-hosted
- Reddit (2025): "Checkpoints are mainly needed for short-term recovery, not long-term memory"

**Corrección:** Mi recomendación de "cron TTL 7 días" sigue siendo correcta. No hay nada nuevo que lo resuelva automáticamente.

---

## 3. Context Management — ACTUALIZACIÓN IMPORTANTE (enero 2026)

**Deep Agents SDK (LangChain, enero 2026) introduce un patrón superior:**

El patrón que yo recomendé (hierarchical memory con summary) es correcto pero PRIMITIVO comparado con lo que LangChain publicó en enero 2026:

### Patrón Deep Agents (3 técnicas en cascada):

1. **Offload large tool results** — Si un resultado > 20k tokens, se mueve a filesystem y se reemplaza con referencia + preview de 10 líneas
2. **Offload large tool inputs** — Cuando contexto > 85% del window, truncar tool calls viejos (el contenido ya está en filesystem)
3. **Summarization** — Cuando ya no hay nada que offloadear:
   - LLM genera summary estructurado (intent, artifacts, next steps)
   - Mensajes originales se guardan en filesystem como record canónico
   - El agente puede re-leer del filesystem si necesita detalles

**Clave:** El filesystem actúa como "memoria extendida" — el agente siempre puede buscar en él.

### Aplicación a El Monstruo:

El kernel YA tiene Supabase como "filesystem" (conversation_memory). El patrón sería:
1. Mantener últimos N mensajes en el state de LangGraph
2. Cuando state > umbral: summarize + guardar originales en Supabase
3. El kernel puede re-leer de Supabase si necesita detalles específicos
4. El nodo `enrich` ya hace algo similar (retrieval de memorias relevantes)

**Esto es EXACTAMENTE lo que el three_layer_memory del kernel ya intenta hacer.** Solo falta el trigger automático basado en tamaño de contexto.

---

## 4. Memory Ownership — ALERTA ESTRATÉGICA (abril 2026)

**Harrison Chase (CEO LangChain, 11 abril 2026) advierte:**

> "If you don't own your harness, you don't own your memory."

Puntos clave para El Monstruo:
- Anthropic lanzó "Claude Managed Agents" — todo detrás de API, lock-in total
- OpenAI Codex genera "encrypted compaction summary" que NO es usable fuera de OpenAI
- La memoria es lo que crea diferenciación y lock-in
- Si usas APIs stateful de proveedores, pierdes portabilidad

**Implicación directa para El Monstruo:**
- El Monstruo DEBE ser el dueño de su propia memoria (ya lo es con Supabase)
- Cuando invoque a Claude/Manus/Kimi como "manos", los resultados deben volver al kernel y guardarse en SU memoria
- NUNCA depender del estado interno de estos proveedores
- El kernel es el harness soberano — los modelos son intercambiables

**Esto valida completamente la arquitectura de El Monstruo:** El kernel como harness propio, con memoria propia, usando modelos como herramientas descartables.

---

## 5. Multi-dispositivo — SIN CAMBIOS

No encontré información nueva que contradiga la recomendación de Supabase como source of truth + local cache. El patrón sigue siendo correcto.

---

## Resumen de Correcciones

| Punto | Investigación original | Corrección validada |
|---|---|---|
| Cold start Railway | "Necesitas edge cache" | Si Serverless está OFF, no hay cold start. Verificar con Alfredo |
| Checkpoint TTL | "No existe built-in" | CONFIRMADO — sigue sin existir en self-hosted |
| Compactación | "Hierarchical memory" | Deep Agents (ene 2026) tiene patrón superior: offload + summarize |
| Multi-device | "Supabase source of truth" | Sin cambios |
| **NUEVO** | — | Memory ownership: El Monstruo como harness soberano es estratégicamente correcto |

---

## Decisión Actualizada para Boot Context

**Si Railway es always-on (Serverless OFF):**
- Boot context va directo al kernel → respuesta en 1-3 segundos
- No necesitamos edge cache ni Cloudflare Workers
- Simplifica enormemente: solo el endpoint `/v1/boot` en el kernel

**Si Railway tiene Serverless ON (por costos):**
- Opción A: Desactivar Serverless (costo ~$5-10/mes más)
- Opción B: Boot context lee de Supabase directo (sin kernel) como fallback

**Pregunta pendiente para Alfredo:** ¿Serverless está ON u OFF en Railway?
