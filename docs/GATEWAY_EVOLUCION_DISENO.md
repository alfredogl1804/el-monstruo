# El Monstruo — Evolución del Gateway a Cerebro Multi-Agente

## Documento de Diseño Arquitectónico

**Versión:** 1.0  
**Fecha:** 2 mayo 2026  
**Autor:** Manus AI (Hilo B — Ejecutor Técnico)  
**Estado:** Propuesta para revisión

---

## 1. Diagnóstico del Estado Actual

### Lo que YA funciona correctamente

| Componente | Estado | Notas |
|---|---|---|
| Gateway WebSocket con SSE bridge | Operativo | Token coalescing 30ms, heartbeat 25s |
| Kernel LangGraph con 8 nodos | Operativo | intake, classify, enrich, execute, respond, memory_write |
| Router de modelos (6 cerebros) | Operativo | GPT-5.5, Claude Opus 4-7, Grok 4.20, Sonar Pro, Gemini 3.1, Kimi K2.5 |
| 14 herramientas nativas | Operativo | web_search, code_exec, browse_web, manus_bridge, wide_research, etc. |
| Conversation Memory (Supabase) | Operativo | Episódica + semántica + pgvector |
| LangGraph Checkpointer (PostgreSQL) | Operativo | AsyncPostgresSaver persiste estado del grafo |
| Manus Bridge (API) | Operativo | create_task, get_status, create_and_wait — 5 calls/hour |
| Tiered Enrichment (Sprint 42) | Operativo | MODERATE vs COMPLEX/DEEP — reduce TTFT |
| Mem0 episodic memory | Operativo | Almacena y recupera memorias por usuario |
| MemPalace long-term | Operativo | Almacena episodios para recuperación futura |

### El Gap Real (3 problemas concretos)

**Problema 1: Thread ID efímero.** La app Flutter no persiste el `currentThreadId` entre sesiones. Cuando cierras la app y la vuelves a abrir, `currentThreadId` es `null`. El Gateway genera uno nuevo (`str(uuid4())`). El kernel crea un grafo nuevo. Resultado: cada vez que abres la app, empiezas "en blanco" — aunque Supabase tiene toda tu historia.

**Problema 2: El kernel SÍ recuerda, pero nadie le pregunta bien.** El nodo `enrich` hace `get_conversation_context(user_id, channel, max_messages=10-20)` que lee de Supabase. PERO como el `thread_id` es nuevo, el LangGraph checkpointer no tiene estado previo para ese thread. La conversación de Supabase SÍ se inyecta (por `user_id`), pero sin el contexto del grafo (qué herramientas se usaron, qué decisiones se tomaron).

**Problema 3: No hay "estado de proyecto" persistente.** El kernel sabe conversar, pero no sabe "estamos en Monstruo Kids, Fase 1, paso 3 de 7". No hay una estructura de datos que represente proyectos activos con su progreso.

---

## 2. Solución: 5 Cambios Quirúrgicos (no reescritura)

### Cambio 1: Thread Persistence en Flutter (4 horas)

**Archivo nuevo:** `apps/mobile/lib/services/thread_persistence.dart`

```dart
import 'package:shared_preferences/shared_preferences.dart';

class ThreadPersistence {
  static const _key = 'active_thread_id';
  
  static Future<String?> getActiveThread() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_key);
  }
  
  static Future<void> setActiveThread(String threadId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, threadId);
  }
  
  static Future<void> clearThread() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
```

**Cambios en `chat_provider.dart`:**
- Al inicializar: cargar `ThreadPersistence.getActiveThread()` como `currentThreadId`
- Cuando el Gateway responde `run_start` con `thread_id`: guardarlo
- `newThread()` llama `ThreadPersistence.clearThread()`

**Resultado:** La app siempre envía el mismo thread_id. El kernel retoma donde quedó.

---

### Cambio 2: Boot Context en Gateway + Kernel (8 horas)

**Endpoint nuevo en Gateway:** `GET /api/session/boot`

```python
@app.get("/api/session/boot")
async def session_boot(thread_id: Optional[str] = None):
    """Retorna contexto de arranque para la app."""
    if not thread_id:
        # Buscar último thread activo en Supabase
        response = await http_client.get(
            f"{KERNEL_URL}/v1/memory/last-thread",
            params={"user_id": "alfredo"}
        )
        if response.status_code == 200:
            thread_id = response.json().get("thread_id")
    
    if thread_id:
        response = await http_client.get(
            f"{KERNEL_URL}/v1/memory/thread-summary",
            params={"thread_id": thread_id, "max_messages": 10}
        )
        if response.status_code == 200:
            return response.json()
    
    return {"thread_id": None, "messages": [], "projects": []}
```

**Endpoints nuevos en Kernel:** `/v1/memory/last-thread` y `/v1/memory/thread-summary`

Consultan Supabase para encontrar el último thread y retornar los últimos N mensajes.

**Resultado:** Al abrir la app, se carga la conversación anterior automáticamente.

---

### Cambio 3: Project State — tabla + CRUD + tool (12 horas)

**Tabla nueva en Supabase:**

```sql
CREATE TABLE active_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'alfredo',
    name TEXT NOT NULL,
    description TEXT,
    current_phase TEXT,
    current_step TEXT,
    total_phases INTEGER DEFAULT 1,
    progress_pct INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    context JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Tool nueva en el kernel:** `project_state`

El kernel puede listar, crear, actualizar y avanzar proyectos. Cuando le preguntas "¿en qué vamos?", consulta esta tabla y responde con el estado real.

**Resultado:** El kernel sabe "Monstruo Kids está en Fase 1, paso 3".

---

### Cambio 4: Session Report Endpoint (6 horas)

**Endpoint nuevo en Kernel:** `POST /v1/session-report`

```python
@app.post("/v1/session-report")
async def receive_session_report(req: SessionReportRequest):
    """Recibe resumen de sesión de agentes externos."""
    report = {
        "source": req.source,       # "manus", "claude", "kimi"
        "summary": req.summary,
        "decisions": req.decisions,
        "files_modified": req.files,
        "project_id": req.project_id,
        "phase_completed": req.phase_completed,
        "next_steps": req.next_steps,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db.insert("session_reports", report)
    
    if req.project_id and req.phase_completed:
        await advance_project_phase(req.project_id)
    
    await memory.append(MemoryEvent(
        memory_type=MemoryType.EPISODIC,
        user_id="alfredo",
        channel=req.source,
        content=f"Session report from {req.source}: {req.summary}",
        metadata=report,
    ))
    return {"status": "received"}
```

**Cómo se usa desde Manus:** En AGENTS.md del proyecto, la instrucción dice que al hacer checkpoint, TAMBIÉN se envía un POST al kernel con el resumen.

**Resultado:** Cada vez que Manus hace un checkpoint, el kernel se entera. La próxima sesión sabe qué pasó.

---

### Cambio 5: Agent Selector en Flutter UI (10 horas)

**Cambio en la UI** para que puedas:
1. Ver qué "manos" están disponibles (Kernel, Manus, Claude, Kimi, Perplexity)
2. Elegir cuál usar para una tarea específica
3. O dejar que el kernel decida (modo "auto")

El Gateway ya pasa props al kernel. Solo se agrega `preferred_agent` al mensaje WebSocket, y el kernel lo respeta en `classify_and_route`.

**Resultado:** Puedes decir "usa Manus para esto" o dejar que el kernel decida.

---

## 3. Arquitectura Evolucionada

```
┌─────────────────────────────────────────────────────┐
│              FLUTTER APP (macOS/iOS)                  │
│                                                      │
│  Chat │ Projects │ Agents │ Config                   │
│       │          │        │                          │
│  ThreadPersistence (SharedPreferences)               │
└──────────────────────┬───────────────────────────────┘
                       │ WebSocket + REST
                       ▼
┌──────────────────────────────────────────────────────┐
│              GATEWAY (Railway, FastAPI)                │
│                                                       │
│  WS /ws/chat        → Stream kernel ↔ Flutter        │
│  GET /api/session/boot → Contexto de arranque        │
│  POST /api/chat     → REST fallback                  │
│  GET /api/projects  → Lista proyectos activos        │
│  POST /api/session-report → Reportes de agentes      │
└──────────────────────┬───────────────────────────────┘
                       │ HTTP/SSE (AG-UI)
                       ▼
┌──────────────────────────────────────────────────────┐
│              KERNEL (Railway, LangGraph)               │
│                                                       │
│  Grafo: intake → classify → enrich → execute → respond│
│                                                       │
│  Nodo ENRICH mejorado:                               │
│  • Conversación previa (Supabase) ✅ YA EXISTE       │
│  • Proyecto activo (tabla nueva)                     │
│  • Session reports recientes                         │
│  • Todo inyectado como contexto al LLM              │
│                                                       │
│  Tools: 14 existentes + project_state + session_report│
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│              SUPABASE (PostgreSQL + pgvector)          │
│                                                       │
│  Existentes: memory_events, knowledge_graph, etc.    │
│  Nuevas: active_projects, session_reports            │
└──────────────────────────────────────────────────────┘
```

---

## 4. Flujo: "Abrir la App y Continuar Donde Quedamos"

1. Alfredo abre `el_monstruo_app`
2. Flutter: `ThreadPersistence.getActiveThread()` → "thread_abc123"
3. Flutter: `GET /api/session/boot?thread_id=thread_abc123`
4. Gateway → Kernel → Supabase: últimos 10 mensajes + proyecto activo
5. Response a Flutter con historial + estado del proyecto
6. Flutter muestra: "Estamos en Monstruo Kids (Fase 1, 35%). Manus completó el diseño del Gateway ayer."
7. Alfredo escribe: "continúa con la implementación"
8. El kernel SABE exactamente qué sigue

---

## 5. Flujo: "Manus Reporta Automáticamente"

1. Alfredo abre Manus (esta sesión)
2. AGENTS.md dice: "Al hacer checkpoint, reporta al kernel"
3. Manus trabaja en Monstruo Kids...
4. Manus hace `webdev_save_checkpoint`
5. TAMBIÉN ejecuta POST a `/v1/session-report` con resumen
6. Kernel guarda en Supabase
7. Próxima vez que Alfredo abre la app → el kernel sabe todo

---

## 6. Resolución del Problema Original

| Escenario | Antes (hoy) | Después |
|---|---|---|
| Abrir app después de cerrarla | Thread nuevo, sin historial | Thread persistente, historial cargado |
| Sesión de Manus termina | Se pierde todo | Manus reporta al kernel vía session-report |
| Sesión se corta por contexto | Se pierde todo | Último checkpoint tiene el report |
| Preguntar "¿en qué vamos?" | El kernel no sabe | Consulta active_projects |
| Cambiar de agente | Cada uno es isla | Todos reportan al mismo kernel |

**El respaldo es automático porque:**
1. La memoria de conversación YA se guarda en Supabase (existe hoy)
2. El thread_id persiste en SharedPreferences (Cambio 1)
3. Los agentes externos reportan al kernel (Cambio 4)
4. El estado de proyectos vive en Supabase (Cambio 3)

**Nadie tiene que "acordarse" de respaldar.** El sistema lo hace por diseño.

---

## 7. Plan de Implementación

| # | Cambio | Esfuerzo | Prioridad |
|---|---|---|---|
| 1 | Thread Persistence (Flutter) | 4 horas | P0 — Resuelve 60% del problema |
| 2 | Boot Context (Gateway + Kernel) | 8 horas | P0 — Completa la experiencia |
| 3 | Project State (Supabase + Kernel) | 12 horas | P1 — Estructura el progreso |
| 4 | Session Report (Kernel + AGENTS.md) | 6 horas | P1 — Conecta agentes externos |
| 5 | Agent Selector (Flutter UI) | 10 horas | P2 — UX de selección de agente |

**Total:** ~40 horas (~5 días de sprint)  
**Orden:** 1 → 2 → 3 → 4 → 5

---

## 8. Lo que NO cambia

- Gateway sigue siendo proxy inteligente (no backend pesado)
- Kernel sigue siendo el cerebro (LangGraph, herramientas, routing)
- App Flutter sigue siendo la interfaz (no se reescribe)
- Supabase sigue siendo la persistencia (no se agrega otra DB)
- AG-UI sigue siendo el protocolo de streaming

**Son 5 cambios quirúrgicos, no una reescritura.**

---

## 9. Riesgos y Mitigaciones

| Riesgo | Mitigación |
|---|---|
| Thread muy largo degrada rendimiento | Tiered enrichment ya limita a 10-20 msgs |
| Session reports no se envían (sesión cortada) | El checkpoint es el trigger, no el "final" |
| Supabase down | In-memory fallback ya existe |
| Latencia del boot context | Cache en Gateway (TTL 5min) |
| SharedPreferences se borra | Boot endpoint busca último thread en Supabase como fallback |

---

## 10. Criterios de Éxito

1. Abrir la app y ver la última conversación sin hacer nada especial
2. Preguntar "¿en qué vamos?" y que el kernel responda con el estado real
3. Hacer un checkpoint en Manus y que el kernel se entere automáticamente
4. Abrir la app al día siguiente y que el kernel sepa qué hizo Manus ayer
5. Latencia del boot < 3 segundos (incluyendo cold start de Railway)
