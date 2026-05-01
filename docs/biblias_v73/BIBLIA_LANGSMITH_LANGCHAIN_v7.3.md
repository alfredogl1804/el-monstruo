## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>LangSmith (LangChain)</td>
</tr>
<tr>
<td>Versión Actual</td>
<td>v0.7.36 (para langsmith/schemas/SkillContext/files) [1], v0.5.25 (para langsmith/utils/uuid/src/version) [1], langsmith-0.15.0-rc.2 (Helm chart) [1]. No hay una única versión monolítica para toda la plataforma, sino versiones para componentes específicos y SDKs. El CLI de LangSmith fue actualizado hace 1 día. [1]</td>
</tr>
<tr>
<td>Estado Actual</td>
<td>Activo</td>
</tr>
<tr>
<td>Precio Actual</td>
<td>LangSmith ofrece un modelo de precios por niveles:

*   **Developer:** $0 / asiento por mes, luego pago por uso. Incluye hasta 5k trazas base / mes, trazado, evals online y offline, Prompt Hub, Playground, Canvas, colas de anotación, monitoreo y alertas, 1 agente Fleet, hasta 50 ejecuciones Fleet / mes, soporte comunitario, 1 asiento.
*   **Plus:** $39 / asiento por mes, luego pago por uso. Incluye todo lo del plan Developer, más hasta 10k trazas base / mes, 1 despliegue de agente de desarrollo gratuito, soporte por correo electrónico, agentes Fleet ilimitados, hasta 500 ejecuciones Fleet / mes, asientos ilimitados, hasta 3 workspaces.
*   **Enterprise:** Precios personalizados. Incluye todo lo del plan Plus, más opciones de alojamiento híbrido y autohospedado, SSO y RBAC personalizados, acceso al equipo de ingeniería, SLA de soporte, capacitaciones de equipo y guía arquitectónica, asientos y workspaces personalizados, paquetes Fleet personalizados.

**Costos adicionales:**
*   **Volumen de trazas (Observabilidad y Evaluación):**
    *   Trazas base: $2.50 por 1k trazas (retención de 14 días).
    *   Trazas extendidas: $5.00 por 1k trazas (retención de 400 días).
*   **Ejecuciones de despliegue (Deployment):** $0.005 / ejecución de despliegue (para despliegues adicionales más allá del gratuito en el plan Plus).
*   **Costo de tiempo de actividad (Deployment):** $0.0007 / minuto por despliegue de desarrollo; $0.0036 / minuto por despliegue de producción.
*   **Ejecuciones Fleet:** $0.05 / ejecución Fleet (para ejecuciones adicionales más allá de las incluidas en el plan Plus).

Los costos del modelo LLM y las herramientas de terceros se facturan por separado por el proveedor correspondiente. [2]</td>
</tr>
<tr>
<td>Posicionamiento Competitivo</td>
<td>LangSmith se posiciona como una plataforma integral para el desarrollo, depuración y despliegue de agentes de IA y aplicaciones LLM, con un fuerte énfasis en la observabilidad y evaluación. Sus principales competidores incluyen Confident AI, Arize AI, Langfuse, Helicone, Braintrust, Vellum, Galileo, Fiddler AI, HoneyHive y OpenLLMetry. A diferencia de algunos competidores que se centran más en el MLOps tradicional (como MLflow), LangSmith está específicamente diseñado para el comportamiento no determinista de los LLM y los agentes. Su integración nativa con el ecosistema LangChain (LangChain, LangGraph, Deep Agents) le otorga una ventaja significativa para los usuarios de este framework, ofreciendo una experiencia unificada desde el desarrollo hasta la producción. La plataforma se diferencia por su capacidad para manejar el ciclo de vida completo del agente, desde el trazado y la depuración hasta la evaluación y el despliegue, con características como el Prompt Hub, Playground y Canvas para la mejora de prompts, y las colas de anotación para la retroalimentación humana. La oferta de planes Enterprise con opciones de alojamiento híbrido y autohospedado también lo distingue en el mercado.</td>
</tr>
</table>
<br>
## L02 — NOVEDADES Y CAMBIOS RECIENTES (ABRIL 2026)
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Cambios Clave desde Marzo 2026</td>
<td>Desde el 20 de marzo de 2026, LangSmith y el ecosistema LangChain han experimentado varias actualizaciones significativas, centrándose en la mejora de agentes, observabilidad, evaluación y despliegue:

*   **Mejoras en Agentes y Deep Agents:** Lanzamiento de nuevas características para Deep Agents, incluyendo la capacidad de "Tuning Deep Agents to Work Well with Different Models" (29 de abril) y "The runtime behind production deep agents" (20 de abril). También se ha trabajado en "Running Subagents in the Background" (16 de abril).
*   **Observabilidad y Evaluación:** Introducción de "Reusable Evaluators and Evaluator Templates in LangSmith" (16 de abril) y mejoras en el "Human judgment in the agent improvement loop" (9 de abril). Se ha enfatizado que "The Agent Improvement Loop Starts with a Trace" (31 de marzo).
*   **Despliegue:** Se ha destacado la capacidad de "Deep Agents Deploy: an open alternative to Claude Managed Agents" (9 de abril).
*   **Integraciones y Cumplimiento:** Se ha abordado cómo "LangSmith and LangChain OSS Help You Meet EU AI Act Requirements" (27 de abril).
*   **Casos de Uso y Éxito:** Publicación de estudios de caso como "How Madrigal Built a Flexible and Scalable Multi-Agent Research and Intelligence Platform for Pharma with LangChain and LangSmith" (29 de abril) y "How Credit Genie used Insights Agent to improve their AI financial assistant" (20 de abril).
*   **Newsletter de Abril 2026:** Resumen de las actualizaciones del mes, incluyendo "new Agent Builder features, production monitoring insights, Deep Agents v0.4" (27 de abril). [1]</td>
</tr>
<tr>
<td>Noticia Más Relevante</td>
<td>La noticia más relevante de los últimos 40 días es el continuo enfoque de LangChain en la mejora y el despliegue de agentes de IA, con el lanzamiento de nuevas características para Deep Agents y la publicación de estudios de caso que demuestran la aplicación exitosa de LangSmith en entornos de producción, como el de Madrigal Pharmaceuticals. Además, la atención a la compatibilidad con las regulaciones como la Ley de IA de la UE subraya su compromiso con la adopción en el mundo real. [1]</td>
</tr>
<tr>
<td>Dato Sorprendente</td>
<td>A pesar de ser una plataforma integral para el desarrollo de agentes de IA, LangSmith no utiliza los datos de sus usuarios para entrenar modelos, garantizando la privacidad de las trazas, prompts y outputs. [2]</td>
</tr>
<tr>
<td>GitHub Stars</td>
<td>N/A (propietario). El repositorio principal de LangChain, `langchain-ai/langchain`, tiene más de 121k estrellas en GitHub. [1]</td>
</tr>
</table>
<br>
## L03 a L15 — (Estructura estándar heredada de v7.0)
<br>
*Nota: Las capas L03 a L15 mantienen la estructura analítica profunda de la versión v7.0, actualizada con los datos de L01 y L02.*

---
**Fuentes Consultadas (Abril 2026):**
https://docs.langchain.com/langsmith/home, https://www.langchain.com/pricing, https://github.com/langchain-ai/langsmith-cli, https://reference.langchain.com/python/langsmith/schemas/SkillContext/files, https://reference.langchain.com/javascript/langsmith/utils/uuid/src/version, https://github.com/langchain-ai/helm/releases, https://www.langchain.com/blog, https://www.confident-ai.com/knowledge-base/compare/top-langsmith-alternatives-and-competitors-compared, https://sumble.com/tech/langsmith, https://www.metacto.com/blogs/top-langsmith-competitors-alternatives-for-llm-observability-in-2024, https://www.helicone.ai/blog/best-langsmith-alternatives, https://www.braintrust.dev/articles/langsmith-alternatives-2026, https://www.leanware.co/insights/langsmith-vs-mlflow, https://www.linkedin.com/posts/jainn-sparsh_langchain-currently-has-121k-stars-on-github-activity-7399756417936613376--ty_
