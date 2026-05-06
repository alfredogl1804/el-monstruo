# DIAGNÓSTICO: El Monstruo — Qué Sigue Vigente, Qué Quedó Obsoleto, Qué Es Nuevo

**Fecha:** 20 de marzo de 2026
**Autor:** Manus AI
**Propósito:** Análisis honesto de todas las arquitecturas y planes existentes del Monstruo contra el estado real de la tecnología de agentes IA a marzo 2026, como base para construir el Plan v2.0.

---

## 1. INVENTARIO DE DOCUMENTOS ANALIZADOS

Se identificaron y leyeron **12 documentos fundacionales** distribuidos en sandbox, Notion y Google Drive. La siguiente tabla resume cada uno con su fecha, su idea central, y el veredicto de vigencia.

| # | Documento | Fecha | Idea Central | Veredicto |
|---|---|---|---|---|
| 1 | MAOC — Documento Maestro | 26 dic 2025 | Notion como "servidor" de conocimiento, PCA como primer paso | **PARCIALMENTE OBSOLETO** |
| 2 | MAOC INTEGRADO — Hilo 5 Feb | 5 feb 2026 | PostgreSQL+pgvector como hub, n8n como orquestador, Windows-MCP | **PARCIALMENTE OBSOLETO** |
| 3 | Arquitectura MAOC INTEGRADO | 6 feb 2026 | 4 flujos de trabajo, Claude Desktop como brazo local | **PARCIALMENTE VIGENTE** |
| 4 | Plan de Construcción v0.1 | 8 feb 2026 | 4 fases incrementales, 7 capas lógicas, 22 piezas | **ESTRUCTURA VIGENTE, CONTENIDO OBSOLETO** |
| 5 | Plan de Construcción v0.2 | 7 mar 2026 | Pivote pragmático: Orquestador MVP con LangGraph + SQLite | **VIGENTE PERO INCOMPLETO** |
| 6 | SEMILLA v5.1 (GitHub) | ~14 feb 2026 | Bootstrap para hilos nuevos, 5 Sabios, guardrails | **VIGENTE, NECESITA ACTUALIZACIÓN** |
| 7 | SEMILLA v9 / v10 | ~mar 2026 | Versión ejecutable con verificación automática | **VIGENTE** |
| 8 | Skills v1 + Protocolo LAB/PROD | ~16 feb 2026 | 10 skills, gobernador de costo, stop-rules | **VIGENTE** |
| 9 | Guardian de Verdad v1.0 | 7 feb 2026 | Anti-sabotaje de model IDs, truth.yaml, preflight | **VIGENTE** |
| 10 | Constitución EPIA-SOP v4.0 | ~ene 2026 | GO/NO-GO, etiquetas de transparencia, routing por tarea | **PARCIALMENTE OBSOLETO** |
| 11 | Top-20 Núcleo v1 | 16 feb 2026 | Síntesis de 10 páginas P0, tabla de reglas nucleares | **VIGENTE COMO REFERENCIA** |
| 12 | Framework Operativo CRISOL-7 | ~mar 2026 | Framework OSINT con 7 roles y 5 estrategias | **VIGENTE (pero es de CRISOL-7, no del Monstruo)** |

---

## 2. LO QUE SIGUE VIGENTE

### 2.1 Principios Arquitectónicos Fundamentales

Cinco principios del plan original han resistido el paso del tiempo y siguen siendo la base correcta para cualquier actualización:

**"Ensamblar, no construir desde cero."** Este principio, documentado en las Decisiones Tomadas (Página 10 del Top-20 Núcleo), es más relevante que nunca. En marzo de 2026, el ecosistema de frameworks de agentes es tan maduro que construir componentes propios sería un desperdicio. Google ADK 2.0, OpenAI Agents SDK, LangGraph y CrewAI ofrecen piezas listas para producción [1] [2].

**"Construcción incremental de valor."** Cada fase debe entregar algo funcional. El Plan v0.2 ya aplicaba este principio al proponer un MVP pragmático en lugar de esperar las 3 Biblias faltantes. Este enfoque sigue siendo el correcto.

**"Alfredo como cuello de botella humano."** El Top-20 Núcleo identificó esto como riesgo #2. A marzo de 2026, el problema persiste: toda la orquestación sigue siendo manual. La diferencia es que ahora existen herramientas maduras para automatizarlo (A2A, ADK, MCP en producción).

**"Nunca dejar conocimiento dentro de Manus."** La regla de oro de Skills v1 sigue siendo crítica. El sandbox se reinicia, la memoria se pierde. La triple capa de memoria (Notion + Drive + GitHub) es el patrón correcto.

**"Los 5 Sabios como consejo consultivo."** El modelo de consultar GPT-5.4, Claude Opus 4, Gemini 3.1 Pro, Grok 4 y Perplexity Sonar Pro de forma secuencial e iterativa sigue siendo poderoso y diferenciador. Ningún framework comercial ofrece esto out-of-the-box.

### 2.2 Componentes Operativos

| Componente | Estado | Notas |
|---|---|---|
| 5 Sabios (APIs) | Operativo | Todos verificados y funcionales |
| Guardian de Verdad | Operativo | Protege model IDs, necesita extensión |
| Protocolo LAB/PROD | Vigente | Stop-rules y gobernador de costo siguen siendo necesarios |
| SEMILLA v9/v10 | Operativa | Bootstrap funcional para hilos nuevos |
| Triple memoria (Notion/Drive/GitHub) | Operativa | Patrón correcto, ejecución inconsistente |
| 69 Biblias v4.1 | Completadas | Activo de conocimiento masivo |
| Ranking 7D + Top 10 | Actualizado | Corregido hoy (20 mar 2026) |

---

## 3. LO QUE QUEDÓ OBSOLETO

### 3.1 PostgreSQL + pgvector como hub central de memoria

El MAOC INTEGRADO (febrero 2026) proponía PostgreSQL + pgvector como la capa central de memoria compartida entre todas las IAs. Esta decisión fue razonable en su momento, pero el landscape de memoria de agentes ha cambiado radicalmente.

En marzo de 2026, existen **8 frameworks especializados de memoria para agentes** [3]. Mem0 tiene 48K estrellas en GitHub y ofrece vector + graph con cloud y self-hosted. Hindsight es el nuevo líder en el benchmark LongMemEval con retrieval multi-estrategia. Letta ofrece memoria tiered inspirada en sistemas operativos. Zep/Graphiti destaca en conocimiento temporal.

El insight clave es que la memoria de agentes se ha dividido en dos problemas distintos: **personalización** (recordar preferencias de usuarios) y **conocimiento institucional** (aprender de la experiencia operativa). PostgreSQL + pgvector resuelve parcialmente el primero pero no aborda el segundo. Un framework como Mem0 o Hindsight resuelve ambos con mucho menos esfuerzo de implementación.

**Veredicto:** Reemplazar PostgreSQL+pgvector con Mem0 (más maduro, 48K stars) o Hindsight (más preciso, MIT license). Ambos soportan self-hosted.

### 3.2 n8n como orquestador de automatizaciones

El MAOC INTEGRADO proponía n8n corriendo en un VPS como el orquestador de flujos entre componentes. En marzo de 2026, n8n sigue siendo una herramienta válida para automatizaciones simples, pero para orquestación de agentes IA existen opciones muy superiores.

**LangGraph** ha madurado significativamente con checkpointing, conditional routing, y ahora tiene CLI de deployment y integración con NVIDIA NeMo [4]. **Google ADK 2.0** ofrece soporte nativo para MCP + A2A + Memory Bank en un solo framework [5]. **OpenAI Agents SDK** reemplazó Swarm con handoffs como abstracción central para producción [2].

**Veredicto:** n8n puede complementar pero no debe ser el orquestador central. LangGraph o Google ADK 2.0 son las opciones correctas para el corazón del Monstruo.

### 3.3 Windows-MCP + Tailscale/ngrok para conexión a Surface Studio

El plan original dependía de un Custom MCP Server en la Surface Studio de Alfredo, conectado vía Tailscale o ngrok. Esta arquitectura tenía un riesgo identificado: "Si la Surface está apagada, se rompe la cadena."

En marzo de 2026, MCP ha evolucionado hacia **Streamable HTTP como transporte remoto** [6], eliminando la necesidad de túneles. Además, el protocolo **A2A (Agent-to-Agent)** de Google permite que agentes se descubran y comuniquen sin infraestructura custom [7]. La dependencia de una PC local encendida es un anti-patrón en 2026.

**Veredicto:** Eliminar la dependencia de Surface Studio. Usar MCP remoto (Streamable HTTP) + A2A para comunicación entre agentes. Si se necesita ejecución local, usar Claude Desktop con MCP nativo (ya lo soporta sin túneles).

### 3.4 Constitución EPIA-SOP v4.0

El Top-20 Núcleo ya identificó que la Constitución v4.0 vive bajo [HISTORICO] y no queda claro si fue reemplazada por SEMILLA v5.1. Además, menciona modelos no alineados (o1-pro, GPT-5 Thinking, DeepSeek, LLaMA) y tiene una complejidad excesiva de etiquetas.

**Veredicto:** Retirar formalmente. Las reglas útiles (GO/NO-GO, KILL-SWITCH, etiquetas de transparencia) deben migrar a la SEMILLA v2.0 del Monstruo.

### 3.5 Modelo de 4 Sabios → 5 Sabios (model IDs desactualizados)

El Guardian de Verdad v1.0 protege 4 model IDs verificados el 7 de febrero de 2026: `grok-4-0709`, `gemini-3-pro-preview`, `gpt-5.2`, `sonar-deep-research`. Pero la SEMILLA v9 ya lista 6 modelos incluyendo GPT-5.4 y Claude Opus 4.

**Veredicto:** Actualizar el Guardian de Verdad con los model IDs correctos a marzo 2026. Incluir Claude Opus 4 que no estaba en el guardian original.

---

## 4. LO QUE ES NUEVO (no existía cuando se diseñó El Monstruo)

### 4.1 Ecosistema de 6 Protocolos Estandarizados

Google publicó el 18 de marzo de 2026 una guía de 6 protocolos que cubren todo el ciclo de vida de un agente [7]:

| Protocolo | Función | Relevancia para El Monstruo |
|---|---|---|
| MCP | Agente → Herramientas | **ALTA** — Ya lo usamos (7 MCPs activos) |
| A2A | Agente → Agente | **ALTA** — Resuelve comunicación entre Sabios |
| UCP | Comercio universal | MEDIA — Para IA Coach (producto) |
| AP2 | Pagos de agentes | BAJA — Futuro |
| A2UI | UI declarativa | MEDIA — Para dashboards |
| AG-UI | Streaming a frontend | MEDIA — Para interfaces en tiempo real |

### 4.2 Google ADK 2.0 con Memory Bank

Google Agent Development Kit 2.0, lanzado en marzo de 2026, integra en un solo framework: soporte nativo MCP, comunicación A2A con `RemoteA2aAgent`, Memory Bank para persistencia de largo plazo, y deployment a Cloud Run [5]. Es el framework más completo disponible y no existía cuando se diseñó El Monstruo.

### 4.3 Memoria de Agentes como Disciplina Madura

En febrero de 2026, Mem0 era una idea mencionada en el Plan v0.1 como "Biblia pendiente". En marzo de 2026, existen 8 frameworks especializados con benchmarks estandarizados (LongMemEval), cloud hosting, y documentación de producción [3]. La "Biblia de Mem0" que estaba pendiente ya no es necesaria como investigación — es un componente listo para integrar.

### 4.4 "The Multi-Agent Trap"

Un artículo influyente de Towards Data Science (marzo 2026) advierte que la mayoría de equipos **no necesitan** sistemas multi-agente [8]. Solo 3 patrones funcionan en producción. GitHub Blog complementa con "Design for failure first" como principio central [9]. Esto es relevante porque El Monstruo fue diseñado como un sistema multi-agente ambicioso. La pregunta correcta no es "¿cuántos agentes necesito?" sino "¿cómo fallaría definitivamente?"

### 4.5 LangChain Deep Agents SDK

LangChain lanzó Deep Agents SDK como capa sobre LangGraph para tareas de alto nivel con task decomposition built-in [2]. Esto es exactamente lo que el Plan v0.2 intentaba construir manualmente con `orquestador.py`.

---

## 5. TABLA DE DECISIONES: MANTENER / REEMPLAZAR / AGREGAR

| Componente del Plan Original | Decisión | Reemplazo/Acción |
|---|---|---|
| 5 Sabios (GPT-5.4, Claude, Gemini, Grok, Perplexity) | **MANTENER** | Actualizar model IDs en Guardian |
| Manus como brazo ejecutor | **MANTENER** | Es el brazo más capaz disponible |
| Notion como memoria operativa | **MANTENER** | Complementar con Mem0/Hindsight |
| Google Drive como almacenamiento pesado | **MANTENER** | Sin cambios |
| GitHub repo `el-monstruo` | **MANTENER** | Actualizar README y estructura |
| Guardian de Verdad | **MANTENER** | Actualizar model IDs |
| SEMILLA (bootstrap) | **MANTENER** | Crear v2.0 con protocolos nuevos |
| Skills v1 + LAB/PROD | **MANTENER** | Sin cambios significativos |
| PostgreSQL + pgvector | **REEMPLAZAR** | Mem0 o Hindsight |
| n8n como orquestador | **REEMPLAZAR** | LangGraph o Google ADK 2.0 |
| Windows-MCP + Tailscale | **REEMPLAZAR** | MCP remoto + A2A |
| Constitución EPIA-SOP v4.0 | **RETIRAR** | Migrar reglas útiles a SEMILLA v2.0 |
| Biblia de Mem0 (investigación) | **YA NO NECESARIA** | Integrar directamente |
| Biblia de FastMCP (investigación) | **YA NO NECESARIA** | MCP ya es estándar maduro |
| Biblia de LangGraph (existente) | **MANTENER** | Actualizar a LangGraph 2026 |
| — | **AGREGAR** | Protocolo A2A para comunicación entre agentes |
| — | **AGREGAR** | Google ADK 2.0 como alternativa a LangGraph |
| — | **AGREGAR** | Framework de memoria (Mem0/Hindsight) |
| — | **AGREGAR** | AG-UI para streaming a frontend |
| — | **AGREGAR** | Mecanismo anti "Multi-Agent Trap" |

---

## 6. PREGUNTAS ABIERTAS PARA ALFREDO

Antes de armar el Plan v2.0, necesito tu decisión en estos puntos:

1. **Orquestador central: ¿LangGraph o Google ADK 2.0?** LangGraph tiene más madurez y comunidad. ADK 2.0 tiene integración nativa con A2A y Memory Bank. Ambos son open source.

2. **Memoria: ¿Mem0 o Hindsight?** Mem0 tiene 48K stars y es el más popular. Hindsight es más preciso en benchmarks y tiene licencia MIT. Ambos soportan self-hosted.

3. **¿Mantener la Surface Studio en la arquitectura?** Si sí, usar Claude Desktop con MCP nativo. Si no, todo corre en la nube (Manus + APIs).

4. **¿El primer producto sigue siendo IA Coach para Like Terranorte?** Esto define qué protocolos priorizar (UCP/AP2 si hay comercio, AG-UI si hay interfaz).

5. **Las 40+ Biblias actualizadas que mencionaste:** ¿Dónde están? Son insumo clave para decidir qué agentes integrar como "brazos" adicionales.

6. **Presupuesto:** ¿Sigue siendo ~$1,500/mes? Esto afecta si usamos cloud managed o self-hosted para memoria y orquestación.

---

## Referencias

[1]: https://gurusup.com/blog/best-multi-agent-frameworks-2026 "Best Multi-Agent Frameworks in 2026"
[2]: https://www.chatbot.com/blog/ai-agent-frameworks/ "AI Agent Frameworks: 10 Options, One Guide"
[3]: https://vectorize.io/articles/best-ai-agent-memory-systems "Best AI Agent Memory Systems in 2026: 8 Frameworks Compared"
[4]: https://blog.langchain.com/nvidia-enterprise/ "LangChain Enterprise Agentic AI Platform"
[5]: https://google.github.io/adk-docs/2.0/ "ADK 2.0 Overview"
[6]: https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/ "The 2026 MCP Roadmap"
[7]: https://developers.googleblog.com/developers-guide-to-ai-agent-protocols/ "Developer's Guide to AI Agent Protocols"
[8]: https://towardsdatascience.com/the-multi-agent-trap/ "The Multi-Agent Trap"
[9]: https://github.blog/ai-and-ml/generative-ai/multi-agent-workflows-often-fail-heres-how-to-engineer-ones-that-dont/ "Multi-agent workflows often fail"
