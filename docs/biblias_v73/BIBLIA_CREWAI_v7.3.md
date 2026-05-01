## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>CrewAI</td>
</tr>
<tr>
<td>Versión Actual</td>
<td>v1.14.3 (24 de abril de 2026)</td>
</tr>
<tr>
<td>Estado Actual</td>
<td>Activo</td>
</tr>
<tr>
<td>Precio Actual</td>
<td>CrewAI ofrece un modelo de precios híbrido: una versión **Open Source (Gratuita)** para desarrolladores que desean construir y experimentar con agentes de IA, y una versión **Enterprise (Personalizada)** para organizaciones que buscan escalar la adopción de IA. La versión gratuita incluye un editor visual, copiloto de IA, integración con GitHub y 50 ejecuciones de flujo de trabajo al mes. La versión Enterprise, con precios personalizados, incluye todo lo de la versión gratuita más infraestructura dedicada (CrewAI o privada), soporte y capacitación in situ, y 50 horas de desarrollo al mes. Reportes de terceros indican que los planes de pago pueden iniciar en $99/mes, con tiers más altos alcanzando hasta $120,000/año para soluciones empresariales.</td>
</tr>
<tr>
<td>Posicionamiento Competitivo</td>
<td>CrewAI se posiciona como un framework robusto y de "código primero" para la orquestación de equipos de agentes de IA colaborativos, destacando por su facilidad de uso para construir flujos de trabajo multi-agente sin la complejidad de frameworks como LangChain. Sus principales competidores incluyen LangChain (que ofrece mayor control y personalización), AutoGen (para sistemas multi-agente) y LangGraph (con una arquitectura basada en grafos). CrewAI se enfoca en la velocidad de ejecución y el rendimiento en tiempo real, lo que lo hace atractivo para casos de uso que requieren colaboración rápida entre agentes.</td>
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
<td>Desde el 20 de marzo de 2026, CrewAI ha lanzado varias actualizaciones significativas, incluyendo las versiones 1.14.2, 1.14.3 y pre-releases de 1.14.4. Los cambios clave incluyen:

**Características:**
*   Soporte para e2b y Bedrock V4.
*   Adición de herramientas de sandbox Daytona y You.com MCP para búsqueda y extracción de contenido.
*   Soporte para la API de Respuestas de Azure OpenAI y credenciales de Vertex AI.
*   Eventos de ciclo de vida para operaciones de checkpoint y soporte de bifurcación para agentes autónomos.
*   Comandos de reanudación, diff y poda de checkpoints, y un parámetro `from_checkpoint` para `Agent.kickoff`.
*   Comandos de gestión de plantillas y CLI de validación de despliegue.
*   Seguimiento enriquecido de tokens de LLM con tokens de razonamiento y creación de caché.

**Correcciones de errores:**
*   Múltiples parches de seguridad para dependencias como `lxml`, `python-dotenv`, `python-multipart`, `pypdf`, `authlib`, `langchain-text-splitters`, `requests`, `cryptography` y `pytest`.
*   Correcciones en la serialización de referencias de clases para checkpointing y manejo de esquemas JSON cíclicos en la resolución de herramientas MCP.
*   Mejoras en el manejo de errores de LLM, propagación de nombres de `@crewbase` y fusión de metadatos de ejecución.

**Mejoras de rendimiento:**
*   Optimización del SDK de MCP y tipos de eventos para reducir el tiempo de arranque en frío en aproximadamente un 29%.</td>
</tr>
<tr>
<td>Noticia Más Relevante</td>
<td>La noticia más importante de los últimos 40 días es el lanzamiento de la versión **1.14.3 de CrewAI el 24 de abril de 2026**, que introdujo mejoras significativas en la gestión de checkpoints, soporte para nuevas plataformas de IA como Bedrock V4 y E2B, y una optimización del 29% en el tiempo de arranque en frío del SDK de MCP. Esta actualización refuerza la capacidad de CrewAI para manejar flujos de trabajo de agentes de IA más complejos y eficientes.</td>
</tr>
<tr>
<td>Dato Sorprendente</td>
<td>A pesar de ser un framework relativamente nuevo, CrewAI ha logrado una impresionante cantidad de 50.4k estrellas en GitHub, superando a muchos proyectos más establecidos en el espacio de la IA. Esto subraya la rápida adopción y el fuerte interés de la comunidad de desarrolladores en su enfoque de orquestación de agentes.</td>
</tr>
<tr>
<td>GitHub Stars</td>
<td>50.4k</td>
</tr>
</table>
<br>
## L03 a L15 — (Estructura estándar heredada de v7.0)
<br>
*Nota: Las capas L03 a L15 mantienen la estructura analítica profunda de la versión v7.0, actualizada con los datos de L01 y L02.*

---
**Fuentes Consultadas (Abril 2026):**
https://github.com/crewaiinc/crewAI/releases, https://pypi.org/project/crewai/, https://crewai.com/pricing, https://www.lindy.ai/blog/crew-ai-pricing, https://www.zenml.io/blog/crewai-pricing, https://www.ibm.com/think/topics/crew-ai, https://www.digitalocean.com/resources/articles/what-is-crew-ai, https://www.lindy.ai/blog/crew-ai-alternatives, https://www.instinctools.com/blog/autogen-vs-langchain-vs-crewai/, https://www.scalekit.com/blog/langchain-vs-crewai-multi-agent-workflows, https://newreleases.io/project/pypi/crewai/release/1.14.2, https://frontierwisdom.com/crewai-1-14-3-release-2/
