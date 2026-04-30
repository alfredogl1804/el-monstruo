# Estado del Sistema: El Monstruo (Abril 2026)

Este documento sirve como índice central y mecanismo de recuperación de contexto para todos los hilos (threads) que trabajan en el proyecto "El Monstruo". **Es obligatorio leer este documento antes de iniciar cualquier modificación arquitectónica.**

## 1. Arquitectura Actual

El Monstruo es un sistema multi-agente basado en FastAPI y LangGraph, diseñado para operar de forma autónoma con memoria persistente y capacidades de ejecución de código.

### Componentes Principales
- **Kernel (`kernel/`)**: El núcleo del sistema. Contiene el motor de LangGraph (`engine.py`), el planificador de tareas (`task_planner.py`), y el loop autónomo del Embrión (`embrion_loop.py`).
- **Memoria (`memory/`)**: Sistema de RAG basado en LightRAG (`lightrag_bridge.py`) que proporciona memoria a largo plazo y recuperación de contexto.
- **Herramientas (`tools/`)**: Capacidades ejecutables (búsqueda web, ejecución de código, GitHub, Telegram, delegación a Manus, consulta a los 6 Sabios).
- **Router (`router/`)**: Cliente LLM unificado (`llm_client.py`) que maneja las llamadas a OpenAI, Anthropic, Gemini, etc.

## 2. El Embrión IA

El Embrión es un proceso en background que se ejecuta periódicamente (latidos) para reflexionar, aprender y ejecutar tareas de forma autónoma.

### Capacidades Recientes (Sprints 41-44)
- **Task Planner ReAct**: El Embrión puede generar planes complejos y ejecutarlos usando un loop ReAct (Reason → Act → Observe) con herramientas reales.
- **FCS (Functional Consciousness Score)**: El Embrión se mide a sí mismo (0-100) basándose en la calidad de sus decisiones, lecciones aprendidas y disciplina de memoria.
- **Write Policy**: Reglas estrictas para evitar guardar ruido en la memoria permanente.
- **Delegación (manus_bridge)**: Capacidad de delegar tareas complejas a agentes Manus externos.
- **Consulta a Sabios (`consult_sabios`)**: Capacidad de consultar en paralelo a GPT-5.4, Claude, Gemini, Grok, DeepSeek y Perplexity para decisiones estratégicas.

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

## 5. Problemas Conocidos y Pendientes

- **Quota de OpenAI**: La `OPENAI_API_KEY` en Railway (gpt-5.5) tiene la cuota excedida (Error 429). El sistema está usando Claude-opus-4-7 como fallback principal.
- **Presupuesto del Embrión**: El `EMBRION_DAILY_BUDGET` fue incrementado a $30.0 USD para evitar bloqueos por límite de gasto.

---
*Documento generado automáticamente para preservación de contexto multi-hilo.*
