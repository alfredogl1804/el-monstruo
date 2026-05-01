# BACKLOG TÉCNICO: EL MONSTRUO VS. MANUS AI
**Fecha:** 30 de Abril de 2026
**Objetivo:** Brechas técnicas identificadas al cruzar la Biblia de Implementación de Manus v2 con el código actual del Monstruo.

---

## 1. Módulo M04: Manejo de Contexto y Memoria

**Lo que hace Manus:**
- Escribe archivos `.progress.md` y `.json` en el sandbox para persistir estado de tareas largas.
- NO comprime el contexto; cuando se llena, despliega sub-agentes con contexto fresco (Wide Research).
- Tiene una Knowledge Base inyectada como "eventos de Conocimiento".

**Lo que hace El Monstruo:**
- Usa LightRAG y Mem0 en Supabase para memoria a largo plazo.
- El Task Planner ReAct mantiene todo el historial en el contexto del LLM.
- **GAP CRÍTICO:** El Monstruo no tiene un mecanismo para vaciar el contexto en tareas muy largas sin perder el hilo. No escribe archivos de estado en el sandbox.

**Acción para el Backlog:**
- [ ] Implementar `StateWriterTool` para que el Task Planner guarde su progreso en archivos locales.
- [ ] Modificar el router para que, al alcanzar el 80% del límite de tokens, resuma el historial y pase solo el resumen + el archivo de estado al siguiente ciclo.

---

## 2. Módulo M09: Orquestación Multi-Agente (Wide Research)

**Lo que hace Manus:**
- Despliega hasta 250 sub-agentes en paralelo para tareas de investigación masiva.
- Cada sub-agente tiene un contexto fresco y no se comunica con los demás.
- El orquestador sintetiza los resultados.

**Lo que hace El Monstruo:**
- Tiene `consult_sabios` para consultar a 6 modelos en paralelo para decisiones estratégicas.
- Tiene `map` tool para procesamiento paralelo de datos estructurados.
- **GAP CRÍTICO:** No tiene un mecanismo para desplegar sub-agentes autónomos (con acceso a tools) en paralelo para investigación abierta.

**Acción para el Backlog:**
- [ ] Crear `WideResearchTool` que instancie múltiples `TaskPlanner` independientes en hilos separados, asigne una subtarea a cada uno, y luego consolide los resultados.

---

## 3. Módulo M05: Browser y Web

**Lo que hace Manus:**
- Navegación interactiva completa: clics, formularios, login, manejo de estado de sesión.

**Lo que hace El Monstruo:**
- Usa Cloudflare Browser Run (read-only) para extraer markdown y screenshots.
- **GAP CRÍTICO:** No puede interactuar con páginas web dinámicas ni hacer login.

**Acción para el Backlog:**
- [ ] Integrar `browser-use` (identificado en el Radar de GitHub) como tool principal de navegación interactiva.

---

## 4. Módulo M07: Agent Skills y Connectors

**Lo que hace Manus:**
- Sistema de Skills y 15+ conectores nativos (Slack, GitHub, Notion, etc.).

**Lo que hace El Monstruo:**
- Tiene integración con GitHub y Google Workspace via CLI.
- Soporta MCP (Model Context Protocol).
- **GAP CRÍTICO:** Faltan conectores para herramientas de comunicación y gestión de proyectos.

**Acción para el Backlog:**
- [ ] Integrar Composio o n8n (identificados en el Radar) para expandir masivamente las integraciones sin escribir código personalizado.
