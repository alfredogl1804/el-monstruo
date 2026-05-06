# Arquitectura de Absorción Soberana del Monstruo v2.0 — Versión Definitiva

## 1. Resumen ejecutivo

**El Monstruo** es una infraestructura de IA soberana para operar trabajo cognitivo, automatización y ejecución de negocio sin depender estratégicamente de un SaaS, un framework o un proveedor de modelos. No busca “tener acceso a herramientas de IA”; busca **poseer el sistema que decide cómo, cuándo y por qué usarlas**.

### Qué problema resuelve

Hoy, la mayoría de stacks agentic caen en uno de dos extremos:

1. **Frankenstein de APIs**: muchas piezas conectadas rápido, poca soberanía, lock-in progresivo, lógica de negocio filtrada en herramientas externas. [SABIO: Claude]
2. **Purismo improductivo**: intentar construir desde cero memoria, durabilidad, observabilidad, gateways y UIs que el mercado ya resolvió mejor. [SABIO: GPT-5.4] [ENJAMBRE: B27, B17, B30]

El Monstruo resuelve esa tensión con una tesis simple:

> **Construir solo el núcleo donde vive la ventaja estratégica; absorber todo lo demás mediante capas anti-corrupción, wrappers soberanos y planes explícitos de reemplazo.**

### Qué es arquitectónicamente

El Monstruo no es una app, ni un chatbot, ni un framework visual. Es un sistema compuesto por:

- un **núcleo soberano** que contiene:
  - kernel/orquestación
  - router inteligente
  - memoria soberana
  - conciencia persistente
  - políticas
  - skills registry
  - módulos de negocio
- una **capa híbrida absorbida** que usa herramientas externas pero bajo control interno
- una **capa commodity** de infraestructura madura que no vale la pena reconstruir

### Tesis arquitectónica definitiva

La ventaja competitiva no está en usar LangGraph, Temporal, LiteLLM, Mem0 o Langfuse. Tampoco en tener acceso a GPT, Claude o Gemini. La ventaja está en un sistema donde:

- **el núcleo decide**
- **las herramientas ejecutan**
- **los datos estratégicos permanecen soberanos**
- **todo componente externo es reemplazable**
- **la memoria y la continuidad no dependen de terceros**
- **la lógica de negocio nunca vive fuera**

### Decisión central

La arquitectura correcta para El Monstruo v2.0 es una de **absorción soberana controlada**:

- **usar** commodities maduros donde no hay diferenciación
- **envolver** servicios y frameworks útiles detrás de interfaces propias
- **adaptar** patrones valiosos sin heredar lock-in conceptual
- **construir** solo el núcleo de decisión, memoria, continuidad, políticas y negocio

### Componentes estratégicos ya resueltos por el mercado

Hay evidencia fuerte de que no debemos reconstruir:

- **durabilidad**: Temporal [DATO: temporalio/temporal, 19.4k★]
- **gateway multi-modelo**: LiteLLM / Portkey [DATO: BerriAI/litellm, 42.2k★] [DATO: Portkey-AI/gateway, 11.2k★]
- **observabilidad**: Langfuse / Helicone [DATO: langfuse/langfuse, 24.4k★] [DATO: Helicone/helicone, 5.4k★]
- **browser automation**: Playwright [DATO: microsoft/playwright, 85.6k★]
- **UI streaming**: Vercel AI SDK [DATO: vercel/ai, 23.3k★]
- **sandboxing**: E2B [DATO: e2b-dev/E2B, 11.6k★]

### Componentes que deben ser soberanos

La evidencia cruzada de Sabios + enjambre converge en que no debemos ceder:

- kernel/orquestador soberano [SABIO: GPT-5.4, Claude, Grok]
- router inteligente [SABIO: Claude, Grok] [ENJAMBRE: B03, B04]
- memoria soberana [SABIO: GPT-5.4, Claude, Grok] [ENJAMBRE: B05, B06, B07, B41]
- conciencia persistente separada de la durabilidad [SABIO: Claude, Grok] [ENJAMBRE: B08, B09]
- skills registry soberano [SABIO: Gemini] [ENJAMBRE: B12, B21]
- políticas y gobernanza [SABIO: Claude, GPT-5.4] [ENJAMBRE: B10, B11]
- módulos de negocio [SABIO: todos] [ENJAMBRE: B13, B14, B33, B34, B35]

### Resultado esperado

Si se implementa correctamente, El Monstruo será un sistema capaz de:

- operar con múltiples modelos sin lock-in
- mantener memoria y continuidad entre sesiones
- ejecutar workflows durables y trazables
- integrar herramientas externas sin ceder el control
- degradar funcionalmente ante fallos de proveedores
- evolucionar sin reescribir el sistema cada vez que cambie el mercado

---

## 2. Mapa de capas definitivo

### Vista general

La arquitectura final se organiza en tres niveles:

- **Núcleo soberano**: donde vive la identidad, la decisión y el aprendizaje
- **Capa híbrida**: donde absorbemos capacidades externas bajo control interno
- **Commodity externo**: infraestructura madura, reemplazable, no diferenciadora

### Tabla de capas

| Capa | Clasificación | Qué es | Por qué existe | Repos / soluciones relevantes | Qué es soberano vs absorbido |
|---|---|---|---|---|---|
| Kernel / Orquestador | Núcleo soberano | Bucle central de control y coordinación | Mantiene intención, flujo y coherencia del sistema | LangGraph [DATO: 28.4k★], CrewAI [48k★], AutoGen [56.7k★] | **Soberano**: lógica de orquestación, planes, estados. **Absorbido**: motor/framework subyacente si se usa |
| Router inteligente | Núcleo soberano | Decide modelo, herramienta, skill y estrategia | Es la inteligencia operativa recurrente | semantic-router [3.6k★], LLMRouter [1.6k★], LiteLLM como transporte [42.2k★] | **Soberano**: política y decisión. **Absorbido**: multiplexado/gateway |
| Memoria soberana | Núcleo soberano | Gestión de memoria episódica, semántica y de trabajo | Sin memoria no hay aprendizaje ni personalización | Mem0 [52k★], Cognee [14.9k★], Letta [21.9k★], Graphiti [24.5k★] | **Soberano**: esquema, consolidación, olvido, acceso. **Absorbido**: backend o motor de apoyo |
| Conciencia persistente | Núcleo soberano | Estado de identidad, objetivos, intención y continuidad | Separa “quién soy / qué estaba haciendo” de “qué workflow corría” | Mission Control [3.8k★], AgentState [55★] | **Soberano**: vector de estado del agente. **Absorbido**: UI o utilidades de seguimiento |
| Políticas y gobernanza | Núcleo soberano / híbrida | Reglas de seguridad, coste, ética, permisos y límites | Evita comportamiento no deseado y controla riesgo | Guardrails AI [6.6k★], OPA [11.5k★], NeMo Guardrails [5.9k★] | **Soberano**: definición de políticas. **Absorbido**: motor de ejecución |
| Skills Registry | Núcleo soberano | Registro de capacidades, skills, prompts, tools y contratos | Desacopla intención del kernel de implementación concreta | awesome-agent-skills [14.2k★], agent-skills [2k★], openapi-to-skills [268★] | **Soberano**: definición/versionado/descubrimiento. **Absorbido**: catálogos o generadores |
| Módulos de negocio | Núcleo soberano | Outreach, research, GTM, análisis, ejecución comercial | Aquí vive el IP real del Monstruo | SalesGPT [2.6k★], GPT Researcher [26.2k★], patrones de Mautic/Twenty | **Soberano**: lógica de negocio. **Absorbido**: ejecutores externos |
| Command Center soberano | Híbrida | Cockpit operativo para humanos | Unifica estado, trazas, memoria, costes y control | Dify [136k★], Langflow [146k★], Flowise [51.5k★], Mission Control [3.8k★] | **Soberano**: backend/API de control. **Absorbido**: UI inicial o andamio |
| Observabilidad | Híbrida | Trazas, métricas, prompts, costes, evaluaciones | Permite operar, depurar y optimizar | Langfuse [24.4k★], Helicone [5.4k★], Phoenix [9.2k★], OpenLLMetry [ENJAMBRE: B17] | **Soberano**: almacén primario y análisis. **Absorbido**: visor/dashboard |
| Durabilidad de tareas | Commodity | Garantiza ejecución fiable de workflows | Resuelve retries, reanudación y consistencia | Temporal [19.4k★], Hatchet [6.8k★], Restate [3.7k★] | **Soberano**: definición del workflow. **Absorbido**: motor durable |
| Gateway multi-modelo | Commodity | Unifica acceso a múltiples LLMs | Evita lock-in de proveedor y simplifica integración | LiteLLM [42.2k★], Portkey [11.2k★], Bifrost [3.5k★] | **Soberano**: interfaz interna. **Absorbido**: gateway |
| Búsqueda web | Commodity / híbrida | Acceso a información pública actualizada | Da grounding externo | Tavily [ENJAMBRE: B31], Exa [B31], Perplexity API, Brave Search API | **Soberano**: cuándo buscar, cómo sintetizar. **Absorbido**: proveedor |
| Conectividad / MCP / OpenAPI | Híbrida | Capa de integración con herramientas y APIs | Permite interoperabilidad sin acoplar el núcleo | MCP servers [83k★], MCP SDK Python [22.5k★], TS SDK [12.1k★], HAPI MCP [ENJAMBRE: B19] | **Soberano**: adaptador genérico. **Absorbido**: protocolo específico |
| UI / chat / frontend | Híbrida / commodity | Interfaz de interacción humana | Hace operable el sistema | Open WebUI [130k★], Chainlit [11.9k★], Streamlit [44.1k★], Vercel AI SDK [23.3k★] | **Soberano**: experiencia final y API. **Absorbido**: framework |
| Browser automation | Commodity | Navegación, scraping, automatización web | Cubre herramientas sin API o tareas web | Playwright [85.6k★], Puppeteer [94k★], browser-use [86.1k★], Stagehand [21.8k★] | **Soberano**: estrategia y validación. **Absorbido**: motor |
| Evaluación / testing | Híbrida | Evalúa prompts, RAG, agentes y regresiones | Evita degradación silenciosa | Promptfoo [19.4k★], DeepEval [14.5k★], Ragas [13.2k★], AgentBench [3.3k★] | **Soberano**: criterios y datasets. **Absorbido**: framework |
| GTM / outreach / CRM | Híbrida / commodity | Email, campañas, CRM, enriquecimiento | Ejecuta negocio real | Mautic [9.4k★], Twenty [43.6k★], Listmonk [19.4k★], fire-enrich [1.1k★], Mira [99★] | **Soberano**: secuencia, scoring, timing. **Absorbido**: plataforma |
| Sandboxing / seguridad de ejecución | Commodity | Aísla código y acciones peligrosas | Reduce blast radius | E2B [11.6k★], gVisor [18k★], nsjail [3.8k★] | **Soberano**: políticas de uso. **Absorbido**: runtime aislado |
| Almacenamiento vectorial / relacional | Commodity | Persistencia de embeddings, estado y datos | Base operativa del sistema | Chroma [ENJAMBRE], pgvector [ENJAMBRE], Qdrant [ENJAMBRE], Postgres | **Soberano**: modelo de datos. **Absorbido**: motor DB |

### Separación crítica: Durabilidad vs Conciencia

Esta es una corrección fundamental aportada por los Sabios. [SABIO: Claude, Grok]

- **Durabilidad** = “que el workflow no muera”
- **Conciencia persistente** = “que el agente recuerde quién es, qué perseguía y qué aprendió”

Temporal puede reanudar una ejecución.  
No puede, por sí solo, reconstruir la identidad operativa del Monstruo.

### Skills Registry: capa faltante ya incorporada

El Skills Registry no es un catálogo decorativo. Es la capa que permite que el kernel pida una **capacidad** (“investigar competidor”, “enriquecer lead”, “buscar en web”) sin conocer la implementación concreta. [SABIO: Gemini] [ENJAMBRE: B12]

Eso lo convierte en una pieza soberana central.

---

## 3. Tabla de absorción maestra

> Nota: “lock-in técnico” = dificultad de reemplazo por API/datos/runtime.  
> “lock-in arquitectónico” = dependencia de patrones mentales, abstracciones y forma de modelar el sistema. [SABIO: Claude]

| Capacidad | Opción principal | Backup | Stars | Licencia | Lock-in técnico | Lock-in arquitectónico | Estrategia de absorción | Fuente |
|---|---|---:|---:|---|---|---|---|---|
| Kernel de agentes | LangGraph | CrewAI | 28.4k | MIT | Medio | Alto | Adaptar detrás de kernel soberano | [DATO] [ENJAMBRE: B01] [SABIO: Claude] |
| Colaboración multiagente | CrewAI | AutoGen | 48k | MIT | Medio | Alto | Envolver y aislar en módulos periféricos | [DATO] [ENJAMBRE: B01] |
| Conversación multiagente | AutoGen | CrewAI | 56.7k | CC-BY-4.0 | Medio | Alto | Tomar patrón, no base del núcleo | [DATO] [ENJAMBRE: B01] |
| Gateway LLM | LiteLLM | Portkey | 42.2k | NOASSERTION | Bajo | Bajo | Usar envuelto por `ModelGateway` | [DATO] [ENJAMBRE: B30] |
| Gateway LLM alterno | Portkey | Bifrost | 11.2k | MIT | Bajo | Bajo | Backup operativo | [DATO] [ENJAMBRE: B30] |
| Router inteligente | Propio sobre gateway | semantic-router | — | Propio | Bajo | Nulo | Construir | [SABIO: GPT-5.4] [ENJAMBRE: B03] |
| Router semántico | semantic-router | LLMRouter | 3.6k | Apache-2.0 | Medio | Medio | Adaptar patrón | [DATO] [ENJAMBRE: B03] |
| Memoria universal | Mem0 | Cognee | 52k | Apache-2.0 | Medio | Alto | Usar self-hosted detrás de `SovereignMemory` | [DATO] [ENJAMBRE: B05, B06, B41] |
| Motor de conocimiento | Cognee | Graphiti | 14.9k | Apache-2.0 | Medio | Medio | Adaptar para memoria semántica avanzada | [DATO] [ENJAMBRE: B05, B07] |
| Memoria jerárquica de agente | Letta | LangMem | 21.9k | Apache-2.0 | Medio | Alto | Tomar patrón | [DATO] [ENJAMBRE: B07] |
| Grafo temporal | Graphiti | GraphRAG | 24.5k | Apache-2.0 | Medio | Medio | Absorber patrón | [DATO] [ENJAMBRE: B06, B07] |
| Conciencia persistente | Mission Control | AgentState | 3.8k | MIT | Medio | Medio | Adaptar, persistiendo estado en DB propia | [DATO] [ENJAMBRE: B09, B08] |
| Durabilidad | Temporal | Hatchet | 19.4k | MIT | Medio | Bajo | Usar tal cual | [DATO] [ENJAMBRE: B27, B37] |
| Durabilidad ligera | Hatchet | Restate | 6.8k | MIT | Medio | Bajo | Backup si Temporal resulta pesado | [DATO] [ENJAMBRE: B27] |
| Observabilidad | Langfuse | Helicone | 24.4k | NOASSERTION | Medio | Bajo | Usar con telemetría dual | [DATO] [ENJAMBRE: B17] |
| Observabilidad alternativa | Helicone | Phoenix | 5.4k | Apache-2.0 | Medio | Bajo | Backup self-hostable | [DATO] [ENJAMBRE: B17] |
| Evaluación de agentes | AgentOps | Phoenix | 5.4k | MIT | Medio | Bajo | Envolver; no fuente primaria | [DATO] [ENJAMBRE: B38] |
| Guardrails de salida | Guardrails AI | NeMo Guardrails | 6.6k | Apache-2.0 | Bajo | Bajo | Usar | [DATO] [ENJAMBRE: B10] |
| Motor de políticas general | OPA | GoRules Zen | 11.5k | Apache-2.0 | Bajo | Medio | Usar para políticas no conversacionales | [DATO] [ENJAMBRE: B10, B11] |
| Rule engine | GoRules Zen | OPA | 1.7k | MIT | Bajo | Medio | Adaptar si se requiere motor determinista rápido | [ENJAMBRE: B11] |
| Skills Registry | Propio | awesome-agent-skills como referencia | — | Propio | Nulo | Nulo | Construir | [SABIO: Gemini] [ENJAMBRE: B12] |
| Catálogo de skills | awesome-agent-skills | vercel-labs/skills | 14.2k | MIT | Bajo | Medio | Tomar patrón | [DATO] [ENJAMBRE: B12] |
| OpenAPI a skills | openapi-to-skills | OpenAPI Generator | 268 | Apache-2.0 | Bajo | Bajo | Usar como herramienta de generación | [DATO] [ENJAMBRE: B21] |
| Command Center inicial | Dify | Langflow | 136k | NOASSERTION | Alto | Alto | Usar como andamio temporal | [DATO] [ENJAMBRE: B16] |
| Builder visual alterno | Langflow | Flowise | 146k | MIT | Medio | Alto | Prototipado, no núcleo | [DATO] [ENJAMBRE: B16] |
| UI local | Open WebUI | Chainlit | 130k | NOASSERTION | Medio | Bajo | Usar como cliente, no como backend | [DATO] [ENJAMBRE: B23] |
| SDK UI streaming | Vercel AI SDK | llm-ui | 23.3k | NOASSERTION | Bajo | Bajo | Usar | [DATO] [ENJAMBRE: B24] |
| Browser automation | Playwright | Puppeteer | 85.6k | Apache-2.0 | Bajo | Bajo | Usar | [DATO] [ENJAMBRE: B36] |
| Browser-use para agentes | browser-use | Stagehand | 86.1k | MIT | Medio | Medio | Adaptar patrón sobre Playwright | [DATO] [ENJAMBRE: B36] |
| Búsqueda web | Tavily | Exa | — | SaaS | Alto | Bajo | Envolver con fallback | [ENJAMBRE: B31] |
| Búsqueda web backup | Exa | Brave Search API | — | SaaS | Alto | Bajo | Segundo proveedor | [ENJAMBRE: B31] |
| MCP servers | MCP oficial | HAPI MCP | 83k | NOASSERTION | Medio | Medio | Adaptar, no acoplar núcleo a MCP | [DATO] [ENJAMBRE: B19, B20] |
| Testing prompts | Promptfoo | DeepEval | 19.4k | MIT | Bajo | Bajo | Integrar en CI/CD | [DATO] [ENJAMBRE: B26] |
| Evaluación RAG | Ragas | DeepEval | 13.2k | Apache-2.0 | Bajo | Bajo | Integrar en CI/CD | [DATO] [ENJAMBRE: B26] |
| CRM | Twenty | Mautic | 43.6k | NOASSERTION | Medio | Medio | Envolver si se usa | [DATO] [ENJAMBRE: B14] |
| Marketing automation | Mautic | Listmonk | 9.4k | NOASSERTION | Medio | Medio | Envolver fuertemente | [DATO] [ENJAMBRE: B13, B14] |
| Enriquecimiento de leads | fire-enrich | Mira | 1.1k | MIT | Medio | Bajo | Adaptar / envolver | [DATO] [ENJAMBRE: B33] |
| Social scheduling | Postiz | Mixpost | 27.9k | AGPL-3.0 | Medio | Bajo | Envolver como ejecutor | [DATO] [ENJAMBRE: B35] |
| Sandboxing | E2B | gVisor | 11.6k | Apache-2.0 | Medio | Bajo | Usar | [DATO] [ENJAMBRE: B48] |
| Kernel minimalista patrón | agent-kernel | MMClaw | 301 | MIT | Bajo | Bajo | Tomar patrón, no usar directo | [DATO] [ENJAMBRE: B02] |
| Auto-mejora | self-improving-agent | learning-agent | 450 | None | Medio | Medio | Tomar patrón | [DATO] [ENJAMBRE: B43] |

---

## 4. Stack recomendado definitivo

## 4.1 Núcleo soberano

### 1) Kernel / Orquestación: **LangGraph**
- **Elección**: LangGraph [DATO: langchain-ai/langgraph, 28.4k★, MIT]
- **Por qué este y no otro**:
  - más bajo nivel y controlable que CrewAI o AutoGen [ENJAMBRE: B01]
  - diseñado para agentes con estado, ciclos y human-in-the-loop
  - licencia MIT
- **Pros**:
  - control granular
  - buen encaje con kernel soberano
  - comunidad fuerte
- **Contras**:
  - lock-in arquitectónico si el grafo se vuelve el modelo mental del sistema [SABIO: Claude]
- **Plan B**:
  - CrewAI para módulos colaborativos
  - o máquina de estados propia sobre Temporal

### 2) Router inteligente: **propio**
- **Elección**: construir router soberano
- **Por qué**:
  - ningún router externo debe decidir estrategia operativa [SABIO: Claude]
  - el valor está en la política de selección, no en el multiplexado [SABIO: GPT-5.4]
- **Base táctica**:
  - semantic-router [3.6k★] o LLMRouter [1.6k★] como inspiración [ENJAMBRE: B03]
- **Plan B**:
  - reglas heurísticas simples en v1

### 3) Memoria soberana: **Mem0 self-hosted + patrón de grafo**
- **Elección**: Mem0 [52k★, Apache-2.0]
- **Por qué este y no otro**:
  - mayor madurez y adopción [ENJAMBRE: B05, B06, B41]
  - opción self-hosted clara
  - arquitectura multi-nivel
- **Pros**:
  - rápido time-to-value
  - buena comunidad
- **Contras**:
  - riesgo de lock-in arquitectónico si se adopta su modelo interno sin abstracción
- **Plan B**:
  - Cognee si se requiere mayor estructuración semántica
  - Letta como patrón de memoria jerárquica

### 4) Conciencia persistente: **módulo propio + Mission Control como referencia**
- **Elección**: construir módulo propio de Agent State Vector, usando Mission Control como apoyo visual/patrón [DATO: 3.8k★]
- **Por qué**:
  - esta capa define identidad e intención
  - no existe una solución madura que deba ser fuente de verdad
- **Plan B**:
  - Postgres + Redis + API propia

### 5) Skills Registry: **propio**
- **Elección**: construir registro soberano
- **Por qué**:
  - es una abstracción central, no un catálogo [SABIO: Gemini]
  - debe versionar capacidades, contratos, prompts y herramientas
- **Plan B**:
  - usar catálogos como awesome-agent-skills solo como inspiración

### 6) Políticas: **Guardrails AI + OPA**
- **Elección**:
  - Guardrails AI para validación LLM
  - OPA para políticas generales
- **Por qué**:
  - Guardrails AI es práctico y maduro [ENJAMBRE: B10]
  - OPA es estándar industrial para políticas deterministas [DATO: 11.5k★]
- **Plan B**:
  - GoRules Zen si se necesita rule engine dedicado

---

## 4.2 Capa híbrida absorbida

### 7) Observabilidad: **Langfuse + almacén soberano**
- **Elección**: Langfuse [24.4k★] con arquitectura dual
- **Por qué**:
  - mejor UX operativa del mercado [ENJAMBRE: B17]
  - pero no debe ser custodio único de datos [SABIO: Claude]
- **Plan B**:
  - Helicone self-hosted

### 8) Command Center inicial: **Dify como andamio**
- **Elección**: Dify [136k★]
- **Por qué**:
  - velocidad de arranque
  - UI usable desde día 1
- **Por qué no como núcleo**:
  - lock-in alto
  - licencia NOASSERTION
  - riesgo de que la arquitectura termine subordinada a su modelo [SABIO: Claude]
- **Plan B**:
  - Langflow si Dify no encaja
  - Command Center propio progresivo

### 9) MCP / conectividad: **adaptador soberano con soporte MCP**
- **Elección**: usar SDKs MCP oficiales, pero detrás de Tool Adapter propio
- **Por qué**:
  - MCP es estándar emergente, no garantía eterna [SABIO: Claude] [ENJAMBRE: B19, B20]
- **Plan B**:
  - OpenAPI adapters propios

### 10) Búsqueda web: **Tavily + Exa**
- **Elección**: Tavily como principal, Exa como backup [ENJAMBRE: B31]
- **Por qué**:
  - mejor equilibrio entre calidad, coste y orientación a agentes
- **Plan B**:
  - Brave Search API
  - browser automation si todo falla

---

## 4.3 Commodity externo

### 11) Durabilidad: **Temporal**
- **Elección**: Temporal [19.4k★, MIT]
- **Por qué este y no otro**:
  - estándar de facto [ENJAMBRE: B27, B37]
  - durable execution real
- **Pros**:
  - robustez industrial
- **Contras**:
  - complejidad operativa
- **Plan B**:
  - Hatchet

### 12) Gateway multi-modelo: **LiteLLM**
- **Elección**: LiteLLM [42.2k★]
- **Por qué**:
  - mayor adopción
  - compatibilidad amplia
- **Contras**:
  - licencia NOASSERTION en datos de Apify; revisar legalmente antes de producción
- **Plan B**:
  - Portkey
  - Bifrost si prima rendimiento

### 13) Browser automation: **Playwright**
- **Elección**: Playwright [85.6k★]
- **Por qué**:
  - madurez, soporte multi-browser, robustez [ENJAMBRE: B36]
- **Plan B**:
  - Puppeteer

### 14) UI local: **Open WebUI**
- **Elección**: Open WebUI [130k★]
- **Por qué**:
  - enorme adopción
  - buen cliente local
- **Contras**:
  - no debe convertirse en backend ni command center real
- **Plan B**:
  - Chainlit

### 15) Sandboxing: **E2B**
- **Elección**: E2B [11.6k★]
- **Por qué**:
  - diseñado para agentes
  - aislamiento fuerte [ENJAMBRE: B48]
- **Plan B**:
  - gVisor

---

## 5. Reglas arquitectónicas definitivas

## Regla 1. Wrapper obligatorio
Toda pieza externa se accede solo a través de una interfaz interna.

**Ejemplo**:  
El kernel nunca llama a LiteLLM directamente. Llama a `ModelGateway.generate()`.

**Motivo**: reemplazo, control, testabilidad.  
[SABIO: GPT-5.4] [SABIO: Claude]

---

## Regla 2. Anti-Corruption Layer obligatoria
El wrapper no solo traduce API; traduce modelo mental.

**Ejemplo**:  
Tavily devuelve resultados web. El ACL los convierte en `EvidenceChunk` con `source`, `confidence`, `timestamp`, `trust_level`.

**Motivo**: evitar que las abstracciones externas contaminen el núcleo.  
[SABIO: Grok] [FUENTE 5]

---

## Regla 3. El router decide, el gateway ejecuta
LiteLLM o Portkey transportan. El router soberano decide.

**Ejemplo**:  
`Router.select(task="draft_outreach", policy="cheap") -> claude-haiku`  
`Gateway.execute(model="claude-haiku", prompt=...)`

**Motivo**: la inteligencia no se delega.  
[SABIO: GPT-5.4] [ENJAMBRE: B30]

---

## Regla 4. Motor de ejecución ciego
Temporal, NeMo, Guardrails o cualquier motor externo reciben instrucciones atómicas, no intención estratégica.

**Ejemplo**:  
Temporal ejecuta `workflow_send_sequence(contact_batch_id)`  
No decide “a quién conviene contactar hoy”.

**Motivo**: la estrategia vive en el núcleo.  
[SABIO: Claude]

---

## Regla 5. Dato no rehén
Ningún SaaS o herramienta externa puede ser la única fuente de verdad de memoria, trazas, políticas o estado.

**Ejemplo**:  
Langfuse recibe trazas, pero también se almacenan en warehouse soberano.

**Motivo**: soberanía real.  
[SABIO: Claude] [ENJAMBRE: B17]

---

## Regla 6. Separación entre durabilidad y conciencia
Workflow state ≠ agent identity.

**Ejemplo**:  
Temporal guarda el progreso de una tarea.  
El Agent State Vector guarda objetivo, subobjetivos, contexto, prioridades y lecciones.

**Motivo**: evitar confundir ejecución con continuidad.  
[SABIO: Claude, Grok]

---

## Regla 7. Skills Registry soberano
El kernel pide capacidades, no herramientas concretas.

**Ejemplo**:  
`invoke_skill("company_research", input)`  
El registry resuelve si usa Tavily, Exa, Playwright o GPT Researcher.

**Motivo**: modularidad y reemplazo.  
[SABIO: Gemini] [ENJAMBRE: B12]

---

## Regla 8. Estrategia de salida obligatoria
Toda integración nace con plan de reemplazo.

**Ejemplo**:  
Si Dify desaparece, el backend soberano sigue operando headless y la UI se reemplaza por frontend propio.

**Motivo**: no acumular deuda invisible.  
[SABIO: Claude]

---

## Regla 9. Presupuesto de soberanía
Cada dependencia externa consume soberanía. Si gastas mucho en una capa, compensa reforzando otra.

**Ejemplo**:  
Usar Dify temporalmente exige ACL fuerte, API soberana y roadmap explícito de salida.

**Motivo**: balance consciente, no improvisado.  
[SABIO: Claude]

---

## Regla 10. Telemetría dual
Toda observabilidad crítica fluye a un visor y a un almacén soberano.

**Ejemplo**:  
OpenTelemetry -> collector propio -> ClickHouse/Postgres + Langfuse

**Motivo**: operar incluso si el visor cae o cambia.  
[SABIO: Claude, Grok]

---

## Regla 11. Degradación elegante
Cada capacidad crítica debe tener modo degradado.

**Ejemplo**:
- sin Tavily -> usar Exa
- sin Exa -> usar Brave
- sin búsqueda -> responder con memoria interna y marcar baja confianza

**Motivo**: resiliencia real.  
[SABIO: Grok] [FUENTE 5]

---

## Regla 12. Modo monasterio
El sistema debe poder operar sin SaaS externos, aunque con funcionalidad reducida.

**Ejemplo**:
- modelos locales o proveedor único temporal
- sin búsqueda web
- sin Dify
- sin Langfuse

**Motivo**: prueba máxima de soberanía.  
[SABIO: Grok]

---

## Regla 13. Memoria en cuarentena
Todo dato externo entra primero a una zona de confianza limitada antes de consolidarse.

**Ejemplo**:  
Resultados de búsqueda o scraping se guardan como `unverified_memory` hasta validación.

**Motivo**: prevenir memory poisoning.  
[SABIO: Grok]

---

## Regla 14. Lógica de negocio solo en el núcleo
Ni Make, ni n8n, ni Dify, ni Mautic definen la estrategia.

**Ejemplo**:  
Mautic envía correos.  
El núcleo decide secuencia, timing, scoring y stop conditions.

**Motivo**: ahí vive el IP.  
[SABIO: todos] [ENJAMBRE: B13, B14]

---

## Regla 15. Patrón sobre framework
Antes de adoptar un framework, extraer el patrón que resuelve.

**Ejemplo**:  
CrewAI aporta patrón de roles.  
No implica que el núcleo deba “ser CrewAI”.

**Motivo**: minimizar lock-in arquitectónico.  
[SABIO: Claude] [ENJAMBRE: B40]

---

## Regla 16. Interfaz estable, implementación reemplazable
El núcleo depende de contratos internos, no de SDKs externos.

**Ejemplo**:
- `WebSearch.search()`
- `Memory.remember()`
- `PolicyEngine.check()`

**Motivo**: evolución sin ruptura.  
[SABIO: GPT-5.4]

---

## Regla 17. Evaluación fuera del camino caliente
Promptfoo, Ragas, DeepEval y similares viven en CI/CD y observabilidad, no en cada request.

**Ejemplo**:  
No correr Ragas en producción por cada consulta.

**Motivo**: coste, latencia y simplicidad.  
[ENJAMBRE: B26]

---

## 6. Anti-patrones y errores

## 6.1 Repos y opciones a evitar o tratar con extrema cautela

| Repo / opción | Problema | Evidencia |
|---|---|---|
| SendPortal | actividad débil / casi abandonado | [ENJAMBRE: B34] |
| Knotie-AI | abandonado | [ENJAMBRE: B13] [DATO: 159★] |
| user-email-enrichment | obsoleto | [ENJAMBRE: B33] |
| LLMTracker | abandonado | [ENJAMBRE: B38] |
| AgentRails | baja madurez, foco estrecho | [ENJAMBRE: B15] |
| repos con licencia NOASSERTION | riesgo legal | [DATO: Dify, Langfuse, LiteLLM, Open WebUI, Vercel AI SDK, etc.] |

## 6.2 Trampas de popularidad

### 1) “Tiene muchas stars, entonces es seguro”
Falso.

- Dify [136k★] puede ser excelente como andamio, pero pésimo como núcleo.
- LangChain [132k★] puede ser útil como ecosistema, pero peligroso como columna vertebral.
- n8n [182k★] es potentísimo, pero no debe alojar lógica central.

### 2) “Es open source, entonces no hay lock-in”
Falso. [SABIO: Claude]

CrewAI, LangGraph o AutoGen pueden atraparte por arquitectura, no por licencia.

### 3) “Si funciona en demo, sirve como base”
Falso.

Muchos proyectos agentic son demos sofisticadas, no infraestructura durable.

---

## 6.3 Anti-patrones arquitectónicos

### A. Frankenstein de APIs
Conectar muchas piezas sin núcleo soberano.

**Síntoma**:  
la lógica de negocio termina repartida entre prompts, nodos visuales, webhooks y configuraciones SaaS.

**Resultado**:  
sistema frágil, caro, inmigrable.  
[SABIO: Claude]

---

### B. Memoria como simple vector DB
Reducir memoria a embeddings + similarity search.

**Síntoma**:  
no hay consolidación, olvido, episodios, semántica ni confianza.

**Resultado**:  
memoria cara, ruidosa e inútil.  
[SABIO: Claude] [ENJAMBRE: B41]

---

### C. Confundir UI con arquitectura
Creer que Dify, Langflow o Open WebUI son el sistema.

**Resultado**:  
el producto queda subordinado a la herramienta.  
[SABIO: GPT-5.4, Claude]

---

### D. Delegar la lógica de negocio a SaaS
Poner secuencias, scoring, decisiones y reglas en Mautic, n8n o plataformas similares.

**Resultado**:  
regalas tu IP.  
[SABIO: todos]

---

### E. Router ingenuo
Construir un router como if/else o confiar en que un LLM siempre decidirá bien.

**Resultado**:  
costes altos, decisiones inconsistentes, vulnerabilidad a envenenamiento.  
[SABIO: Grok] [ENJAMBRE: B03]

---

### F. No diseñar cuarentena de memoria
Permitir que cualquier dato externo entre directo a memoria soberana.

**Resultado**:  
memory poisoning sistémico.  
[SABIO: Grok]

---

### G. Acoplar el núcleo a MCP
Hacer que el kernel “hable MCP” directamente.

**Resultado**:  
el protocolo se vuelve tu arquitectura.  
[SABIO: Claude] [ENJAMBRE: B19]

---

### H. Construir commodities resueltos
Rehacer Temporal, Langfuse, Playwright o un gateway multi-modelo.

**Resultado**:  
desperdicio de tiempo estratégico.  
[SABIO: GPT-5.4] [ENJAMBRE: B17, B27, B30, B36]

---

## 7. Roadmap de implementación

## Fase 1 — Fundación operativa mínima
**Objetivo**: tener un sistema usable, desacoplado y observable.

### Componentes
- Temporal
- LiteLLM
- Open WebUI o Dify
- Postgres
- Langfuse
- Playwright

### Entregables
- `ModelGateway`
- `ToolAdapter`
- `TelemetryCollector`
- primer flujo end-to-end

### Métricas de éxito
- cambiar de modelo sin tocar lógica de negocio
- trazabilidad completa de una ejecución
- workflow durable funcionando

### Go / No-Go
- **GO** si el sistema opera headless y vía UI
- **NO-GO** si la lógica ya depende de Dify o llamadas directas a proveedores

---

## Fase 2 — Núcleo soberano
**Objetivo**: instalar el verdadero cerebro.

### Componentes
- kernel soberano sobre LangGraph
- router inteligente v1
- skills registry v1
- policy engine v1

### Entregables
- API interna estable
- selección de modelo por tarea
- invocación por skill, no por tool

### Métricas de éxito
- 80% de llamadas externas pasan por interfaces soberanas
- router reduce coste medio por tarea
- skills registry desacopla al kernel de implementaciones

### Go / No-Go
- **GO** si el kernel puede operar sin UI visual
- **NO-GO** si el sistema sigue siendo un conjunto de flujos externos

---

## Fase 3 — Memoria y conciencia
**Objetivo**: pasar de scripts durables a agente persistente.

### Componentes
- Mem0 self-hosted detrás de `SovereignMemory`
- Agent State Vector propio
- cuarentena de memoria
- consolidación episódica/semántica

### Entregables
- recuperación de contexto útil entre sesiones
- continuidad de objetivos
- memoria con niveles de confianza

### Métricas de éxito
- mejora medible en continuidad entre sesiones
- reducción de repetición de contexto manual
- cero escrituras directas a memoria desde integraciones externas

### Go / No-Go
- **GO** si el agente puede reanudar una misión con coherencia
- **NO-GO** si la memoria sigue siendo solo RAG vectorial

---

## Fase 4 — Operación soberana avanzada
**Objetivo**: robustez, evaluación y negocio real.

### Componentes
- telemetría dual completa
- Promptfoo / Ragas / DeepEval en CI
- GTM envuelto
- sandboxing con E2B
- degradación elegante

### Entregables
- command center propio inicial
- dashboards de coste/valor
- fallback multi-proveedor
- módulos de negocio operativos

### Métricas de éxito
- sistema sobrevive a caída de un proveedor crítico
- coste por tarea optimizado
- regresiones detectadas antes de producción
- primer módulo de negocio genera valor real

### Go / No-Go
- **GO** si el sistema puede operar con funcionalidad degradada
- **NO-GO** si una sola caída externa paraliza el negocio

---

## 8. Advertencias estratégicas

## 8.1 Memory poisoning
Una sola integración comprometida puede contaminar memoria soberana a largo plazo. [SABIO: Grok]

**Mitigación**:
- cuarentena
- scoring de confianza
- consolidación diferida
- trazabilidad de origen

---

## 8.2 Router envenenado
Un router basado en LLM puede ser sesgado por prompts adversariales o patrones de entrada. [SABIO: Grok]

**Mitigación**:
- reglas deterministas base
- auditoría de decisiones
- detección de anomalías
- modo paranoia

---

## 8.3 Falacia del open source
Open source no elimina lock-in; solo cambia su forma. [SABIO: Claude]

**Mitigación**:
- interfaces propias
- patrones portables
- no internalizar abstracciones externas como verdad del dominio

---

## 8.4 Síndrome Frankenstein
El sistema parece flexible, pero en realidad es una maraña de dependencias.

**Mitigación**:
- kernel soberano
- skills registry
- ACLs
- revisiones arquitectónicas trimestrales

---

## 8.5 UI takeover
La herramienta visual termina dictando el diseño del sistema.

**Mitigación**:
- backend soberano primero
- operación headless obligatoria
- UI como cliente, no como centro

---

## 8.6 Vendor drift silencioso
Cambios de pricing, límites, licencias o roadmap pueden matar una capa crítica.

**Mitigación**:
- backup por capacidad
- estrategia de salida documentada
- presupuesto de soberanía

---

## 9. Conceptos pendientes de validación

## 9.1 Capas concéntricas de soberanía
**Hipótesis**: pensar la arquitectura como anillos mejora decisiones de diseño. [SABIO: GPT-5.4]

**Validar**:
- si mejora comunicación y gobernanza
- si ayuda a clasificar nuevas integraciones

---

## 9.2 Degradación elegante sistemática
**Hipótesis**: diseñar explícitamente modos “completo / degradado / monasterio” mejora resiliencia. [SABIO: Grok]

**Validar**:
- coste de implementación
- valor real para MVP

---

## 9.3 Métricas de integridad arquitectónica
**Hipótesis**: se puede medir cuándo la lógica de negocio se está filtrando fuera del núcleo. [SABIO: Claude]

**Posibles métricas**:
- % de decisiones tomadas fuera del kernel
- nº de llamadas directas a SDKs externos
- nº de workflows críticos alojados en herramientas externas

---

## 9.4 Núcleo minimalista óptimo
**Hipótesis**: existe un tamaño ideal del núcleo soberano antes de caer en sobreingeniería. [SABIO: DeepSeek/Grok]

**Validar**:
- qué debe entrar en v1
- qué puede vivir temporalmente en capa híbrida

---

## 9.5 Grafo de conocimiento como memoria primaria
**Hipótesis**: para ciertos dominios, un grafo puede superar a una memoria vectorial clásica.

**Validar**:
- coste operativo
- complejidad
- mejora real en recuperación y razonamiento

---

## 10. Conclusión y tesis final

La Arquitectura de Absorción Soberana del Monstruo v2.0 no propone construir una fortaleza aislada ni ensamblar un collage de herramientas ajenas; propone un sistema donde **un núcleo soberano de decisión, memoria, continuidad, políticas y negocio absorbe estratégicamente capacidades externas maduras mediante interfaces propias, capas anti-corrupción y planes explícitos de reemplazo**, porque la única ventaja defendible no es acceder a modelos o herramientas, sino **poseer la inteligencia acumulada que decide cómo usarlos sin quedar atrapado por ellos**.

**Frase final**:  
**El Monstruo debe ser un sistema donde un núcleo soberano pequeño pero absoluto piense, recuerde y decida, mientras todo lo demás —modelos, herramientas, UIs y motores— solo ejecuta bajo sus reglas.**