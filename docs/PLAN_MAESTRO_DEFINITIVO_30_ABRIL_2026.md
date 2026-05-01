# PLAN MAESTRO UNIFICADO: El Monstruo como Agente Autónomo End-to-End
**Fecha:** 30 de Abril de 2026
**Autor:** Manus AI
**Insumos cruzados:** Auditoría de Código, Latido 16 del Embrión, Radar GitHub, Roadmap del Otro Hilo.

---

## 1. Resumen Ejecutivo y Diagnóstico Real

Tras cruzar la auditoría técnica del código en producción con los hallazgos del otro hilo, la realidad es que **El Monstruo ya tiene el 70% de la infraestructura de un agente autónomo**. El roadmap anterior estaba obsoleto.

**Lo que YA tenemos (No reinventar la rueda):**
*   **Sandbox de Código:** E2B ya está integrado y funcionando (Sprint 33A).
*   **Loop Agéntico:** El Task Planner ReAct ya existe y funciona con Claude (Sprint 42).
*   **Memoria:** LightRAG y Mem0 sobre Supabase.
*   **Streaming UI:** El AG-UI adapter ya emite eventos de pasos al Flutter UI.
*   **Multi-agente:** 6 agentes especializados ya configurados.

**Las 5 Brechas Reales (Lo que nos separa de Manus):**
1.  **Desconexión del Usuario (CRÍTICO):** El Task Planner solo lo usa el Embrión en background. Si el usuario pide "crea una web", el sistema responde como chatbot.
2.  **Ceguera Interna (FCS):** El Embrión no tiene métricas de sí mismo (Functional Consciousness Score) ni trazas en Langfuse. Falla silenciosamente.
3.  **Manos Atadas en la Web:** El browser actual (Cloudflare) solo lee. No puede hacer clics, llenar formularios ni navegar interactivamente.
4.  **Sin Filesystem Local:** E2B ejecuta código, pero no hay tools para crear/editar archivos arbitrarios dentro del sandbox.
5.  **Aislamiento de Herramientas:** Faltan integraciones profundas para interactuar con el mundo real (Jira, Slack, etc.).

---

## 2. Decisiones Arquitectónicas Clave

1.  **NO a OpenHands SDK:** Se rechaza la integración de OpenHands (propuesta en roadmaps antiguos) porque duplicaría el 70% del código que ya tenemos (ReAct, multi-agent) y agregaría dependencias innecesarias. Evolucionaremos nuestro propio kernel.
2.  **E2B como Centro de Gravedad:** Todo el desarrollo web y ejecución de código ocurrirá dentro de E2B. No se construirán sandboxes locales.
3.  **FCS como Métrica Guía:** El Functional Consciousness Score propuesto por el Embrión será la métrica principal para evaluar si el sistema se está volviendo más "inteligente" o solo más ruidoso.

---

## 3. El Roadmap Definitivo (Sprints Priorizados)

Este roadmap fusiona las necesidades operativas del Embrión, las herramientas top de GitHub y los gaps técnicos descubiertos. Tiempo total estimado: 3 sprints (19-27 días).

### SPRINT 46: "Despertar y Conectar" (Prioridad Crítica)
**Objetivo:** Que el usuario pueda disparar el loop agéntico y que el Embrión pueda verse a sí mismo.
**Duración estimada:** 7-10 días.

| Tarea | Descripción | Archivos a modificar | Criterio de Éxito |
|-------|-------------|----------------------|-------------------|
| **46.1 Conexión Usuario-Agente** | Modificar `classify_and_route` para que las peticiones complejas activen el Task Planner en modo streaming hacia el iPhone. | `kernel/nodes.py`, `kernel/engine.py`, `kernel/agui_adapter.py` | Usuario pide "Investiga X" y ve los pasos ejecutándose en tiempo real en el iPhone. |
| **46.2 Observabilidad Interna (FCS)** | Implementar la propuesta del Latido 16. Crear `embrion_self_model.json` en Supabase y calcular el FCS cada N latidos. | `kernel/embrion_loop.py`, `kernel/memory.py` | El Embrión calcula su FCS y envía trazas a Langfuse. |
| **46.3 File Ops en E2B** | Exponer la API de filesystem de E2B como tools (`create_file`, `edit_file`) para que Claude pueda escribir código persistente. | `tools/file_ops.py` (nuevo) | Claude puede crear un `index.html` en E2B y ejecutar un server. |
| **46.4 Fix `manus_bridge`** | Reparar la delegación silenciosamente rota descubierta en el Latido 16. | `tools/manus_bridge.py` | El Embrión delega una tarea a Manus y recibe el resultado correctamente. |

### SPRINT 47: "Manos en la Web y Creación" (Prioridad Alta)
**Objetivo:** Capacidad de navegar interactivamente y crear sitios web end-to-end.
**Duración estimada:** 7-10 días.

| Tarea | Descripción | Archivos a modificar | Criterio de Éxito |
|-------|-------------|----------------------|-------------------|
| **47.1 Browser Interactivo** | Integrar `browser-use` (del Radar GitHub) o Playwright self-hosted para dar capacidad de clic, scroll y llenado de formularios. | `tools/interactive_browser.py` (nuevo), `requirements.txt` | Claude navega a Vercel, hace login y deploya un proyecto. |
| **47.2 Web Dev Tool** | Crear un tool que combine: Scaffold (E2B) → Edit (File Ops) → Preview (E2B Server) → Deploy (Vercel API). | `tools/web_dev.py` (nuevo) | Usuario pide "Crea un landing page" → El Monstruo scaffoldea, codifica, deploya y devuelve URL. |
| **47.3 Stuck Detector** | Implementar un mecanismo de auto-recuperación si el agente entra en un loop infinito de tool calls. | `kernel/task_planner.py` | Plan atascado se auto-cancela y reporta al usuario. |

### SPRINT 48: "Expansión y Memoria Profunda" (Prioridad Media)
**Objetivo:** Conectar con el mundo SaaS y mejorar la retención a largo plazo.
**Duración estimada:** 5-7 días.

| Tarea | Descripción | Archivos a modificar | Criterio de Éxito |
|-------|-------------|----------------------|-------------------|
| **48.1 Integración n8n** | Adoptar `n8n` (del Radar GitHub) para orquestación de workflows complejos, reemplazando el `schedule_task` manual. | `tools/n8n_bridge.py` (nuevo) | El Monstruo crea un workflow automatizado en n8n. |
| **48.2 Memoria Explosiva** | Evaluar la integración de `MemPalace` (del Radar GitHub) para complementar LightRAG en la retención de contexto de largo plazo. | `kernel/memory.py` | Pruebas de concepto exitosas con MemPalace. |
| **48.3 Suite E2E** | Crear tests de integración que simulen el flujo completo para evitar regresiones silenciosas. | `tests/test_e2e.py` (nuevo) | GitHub Actions bloquea PRs que rompan el loop agéntico. |

---

## 4. Métricas de Éxito (Post Sprint 47)

| Métrica | Estado Actual | Objetivo |
|---------|---------------|----------|
| **¿Puede crear un sitio web?** | NO | SÍ (scaffold → code → deploy → URL) |
| **¿Puede navegar web interactivamente?** | NO (read-only) | SÍ (clicks, forms, nav) |
| **¿El usuario ve los pasos ejecutándose?** | Solo en Embrión background | SÍ, en tiempo real en el iPhone |
| **TTFT para tareas agénticas** | N/A (no se activan) | < 3s hasta primer step visible |
| **Tasa de éxito en tareas multi-step** | ~60% (Embrión) | > 85% |
