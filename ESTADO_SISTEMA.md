# Estado del Sistema: El Monstruo (Abril 2026)

Este documento sirve como índice central y mecanismo de recuperación de contexto para todos los hilos (threads) que trabajan en el proyecto "El Monstruo". **Es obligatorio leer este documento antes de iniciar cualquier modificación arquitectónica.**

## 1. Arquitectura Actual

El Monstruo es un sistema multi-agente basado en FastAPI y LangGraph, diseñado para operar de forma autónoma con memoria persistente y capacidades de ejecución de código.

### Componentes Principales
- **Kernel (`kernel/`)**: El núcleo del sistema. Contiene el motor de LangGraph (`engine.py`), el planificador de tareas (`task_planner.py`), y el loop autónomo del Embrión (`embrion_loop.py`).
- **Memoria (`memory/`)**: Sistema de RAG basado en LightRAG (`lightrag_bridge.py`) que proporciona memoria a largo plazo y recuperación de contexto.
- **Herramientas (`tools/`)**: Capacidades ejecutables (búsqueda web, ejecución de código, GitHub, Telegram, delegación a Manus, consulta a los 6 Sabios, file_ops, web_dev).
- **Sandbox Manager (`tools/sandbox_manager.py`)**: Sprint 48. Gestión de sandboxes E2B persistentes por plan. Un sandbox compartido entre todas las tool calls (`code_exec`, `file_ops`, `web_dev`) durante la ejecución de un plan multi-paso.
- **Router (`router/`)**: Cliente LLM unificado (`llm_client.py`) que maneja las llamadas a OpenAI, Anthropic, Gemini, etc.

## 2. El Embrión IA

El Embrión es un proceso en background que se ejecuta periódicamente (latidos) para reflexionar, aprender y ejecutar tareas de forma autónoma.

### Capacidades Recientes (Sprints 41-48)
- **Task Planner ReAct**: El Embrión puede generar planes complejos y ejecutarlos usando un loop ReAct (Reason → Act → Observe) con herramientas reales.
- **FCS (Functional Consciousness Score)**: El Embrión se mide a sí mismo (0-100) basándose en la calidad de sus decisiones, lecciones aprendidas y disciplina de memoria.
- **Write Policy**: Reglas estrictas para evitar guardar ruido en la memoria permanente.
- **Delegación (manus_bridge)**: Capacidad de delegar tareas complejas a agentes Manus externos.
- **Consulta a Sabios (`consult_sabios`)**: Capacidad de consultar en paralelo a GPT-5.4, Claude, Gemini, Grok, DeepSeek y Perplexity para decisiones estratégicas.
- **Sandbox Persistente (Sprint 48)**: El Task Planner ahora crea UN sandbox E2B al inicio de cada plan y lo comparte entre todos los pasos. Esto permite tareas end-to-end como crear sitios web (scaffold → write files → build → deploy a Vercel).
- **Web Dev (`web_dev`)**: Scaffold de proyectos React+Vite+Tailwind, build con npm, y deploy a Vercel.
- **File Ops (`file_ops`)**: Operaciones de archivo (write, read, edit, list, delete, mkdir) en sandbox E2B.

## 3. Protocolo de Coordinación Multi-Hilo

Actualmente hay múltiples hilos de Manus trabajando en paralelo en este repositorio. Para evitar conflictos de merge y pérdida de código, se debe seguir este protocolo:

1. **Nunca hacer push directo a `main` si hay otro hilo activo.**
2. **Usar branches separados**: Cada hilo debe crear su propio branch (ej. `sprint-manus`, `sprint-streaming`).
3. **Sincronización**: Antes de hacer merge a `main`, el hilo debe verificar con el usuario (Alfredo) el estado de los otros hilos.
4. **Rebase obligatorio**: Siempre hacer `git pull --rebase origin main` antes de intentar un push o merge.

## 4. Estado de los Sprints

| Sprint | Estado | Rama | Descripción |
|--------|--------|------|-------------|
| 41 | ✅ Completado | `main` | Task Planner genera pasos reales (fix `intent_override` + Claude directo) |
| 42 | ✅ Completado | `main` | Loop ReAct con herramientas reales (`tool_use` nativo de Claude) |
| 43 | ✅ Completado | `main` | Fix `tool_calls=0` y reconexión real de Telegram |
| 44 | 🚧 En progreso | `sprint-manus` | FCS, Write Policy, `manus_bridge` y `consult_sabios` en el Task Planner |
| 42b | 🚧 En progreso | `main` | Fix SSE heartbeat interleaving + progress events streaming (Otro hilo) |
| 46 | ✅ Completado | `main` | Task Planner streaming + file_ops en E2B |
| 47 | ✅ Completado | `main` | web_dev: scaffold, build, deploy a Vercel |
| 48 | ✅ Completado | `main` | **Sandbox persistente + TaskPlanner fix** — E2E test 7/7 passing |

## 5. Problemas Conocidos y Pendientes

- **Quota de OpenAI**: La `OPENAI_API_KEY` en Railway (gpt-5.5) tiene la cuota excedida (Error 429). El sistema está usando Claude-opus-4-7 como fallback principal.
- **Presupuesto del Embrión**: El `EMBRION_DAILY_BUDGET` fue incrementado a $30.0 USD para evitar bloqueos por límite de gasto.
- **~~TaskPlanner sin kernel~~ (RESUELTO Sprint 48)**: `engine.py` instanciaba `TaskPlanner()` sin argumentos → TypeError silencioso → fallback al flujo normal. Corregido: `TaskPlanner(kernel=self, db=self._db)`.
- **~~Sandbox efímero~~ (RESUELTO Sprint 48)**: Cada tool call creaba/destruía su propio sandbox E2B → tareas multi-paso no compartían estado. Corregido: `SandboxManager` con sandbox persistente por plan.
- **~~Modelo incorrecto en streaming~~ (RESUELTO Sprint 48 audit)**: `_execute_step_streaming` usaba `model=EXECUTOR_MODEL` (`gpt-5.5` de OpenAI) con `anthropic.AsyncAnthropic` → Anthropic rechazaba/ignoraba el modelo → Claude no hacía tool calls. Corregido: hardcoded `claude-opus-4-7`.
- **~~max_react_loops hardcodeado~~ (RESUELTO Sprint 48 audit)**: Streaming path tenía `max_react_loops = 3` en vez de `MAX_REACT_LOOPS` (5). Corregido.
- **~~System prompt débil~~ (RESUELTO Sprint 48 audit)**: El prompt del executor no obligaba a usar herramientas. Corregido: "DEBES usar las herramientas. NUNCA respondas solo con texto."

---
*Documento generado automáticamente para preservación de contexto multi-hilo.*
