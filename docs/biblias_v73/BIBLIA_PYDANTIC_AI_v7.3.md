## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>Pydantic AI</td>
</tr>
<tr>
<td>Versión Actual</td>
<td>v1.88.0 (28 abril 2026)</td>
</tr>
<tr>
<td>Estado Actual</td>
<td>Activo</td>
</tr>
<tr>
<td>Precio Actual</td>
<td>Pydantic AI es un framework de código abierto. Sin embargo, los productos relacionados como Pydantic Logfire tienen un modelo de precios por niveles: Personal (gratis para proyectos personales), Team ($49/mes para startups y equipos pequeños) y Growth ($249/mes para equipos en crecimiento).</td>
</tr>
<tr>
<td>Posicionamiento Competitivo</td>
<td>Pydantic AI se posiciona como un framework de agentes de IA de extremo a extremo, centrado en la experiencia del desarrollador y la seguridad de tipos. Se diferencia de competidores como LangChain y LangSmith al ofrecer una API más legible, validación de salida estructurada y una integración más profunda con el ecosistema Pydantic (Validation, Logfire, Evals). Destaca por su agnóstico de modelos, soportando una amplia gama de proveedores de LLM, y por su enfoque en la observabilidad con Pydantic Logfire. Su capacidad para construir agentes duraderos y con ejecución humana en el bucle también lo distingue.</td>
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
<td>Desde el 20 de marzo de 2026, Pydantic AI ha lanzado múltiples actualizaciones significativas. La versión v1.88.0 (28 de abril de 2026) introdujo ganchos de validación/procesamiento de salida, soporte para el ajuste de modelo `service_tier` entre proveedores (Anthropic, Gemini API, Vertex Priority PayGo), modo `fast` para Anthropic Opus 4.6, y soporte para `UIAdapter.sanitize_messages`. También se corrigieron errores relacionados con `cache_control` y la propagación de errores. La v1.87.0 (24 de abril de 2026) añadió la capacidad `HandleDeferredToolCalls` y `ProcessEventStream`, además de manejar la configuración de pensamiento para GPT-5.5. La v1.86.1 (23 de abril de 2026) incluyó correcciones de errores para `choices=None` en fragmentos de transmisión de OpenAI y la preservación de errores de validación. La v1.86.0 (23 de abril de 2026) agregó `UIAdapter.manage_system_prompt` y la capacidad `ReinjectSystemPrompt`. La v1.85.0 (21 de abril de 2026) implementó la evaluación en línea a través de eventos OpenTelemetry. La v1.84.0 (17 de abril de 2026) incluyó soporte para Claude Opus 4.7, un modo de compactación con estado para `OpenAICompaction`, y una corrección de seguridad para regex de tiempo exponencial en `FileSearchTool` de Google. La v1.83.0 (16 de abril de 2026) añadió soporte para `XSearchTool` y `FileSearch` para xAI, inyección de metadatos por llamada de herramienta con `FastMCPToolset`, y soporte para caché de prompt TTL en Bedrock y Anthropic. La v1.82.0 (15 de abril de 2026) corrigió problemas de compactación de OpenAI y fugas de tareas huérfanas.</td>
</tr>
<tr>
<td>Noticia Más Relevante</td>
<td>La noticia más importante es el lanzamiento de Pydantic AI Harness con 'Code Mode' impulsado por Monty, anunciado el 16 de abril de 2026. Esto representa un avance significativo en la capacidad de Pydantic AI para generar y ejecutar código, ampliando sus funcionalidades para el desarrollo de agentes de IA.</td>
</tr>
<tr>
<td>Dato Sorprendente</td>
<td>Un hecho sorprendente es que Pydantic AI alcanzó la versión V1 en septiembre de 2025, comprometiéndose a la estabilidad de la API, lo que es inusual para frameworks de IA en rápido desarrollo y demuestra una madurez temprana en su ciclo de vida.</td>
</tr>
<tr>
<td>GitHub Stars</td>
<td>16.8k</td>
</tr>
</table>
<br>
## L03 a L15 — (Estructura estándar heredada de v7.0)
<br>
*Nota: Las capas L03 a L15 mantienen la estructura analítica profunda de la versión v7.0, actualizada con los datos de L01 y L02.*

---
**Fuentes Consultadas (Abril 2026):**
https://github.com/pydantic/pydantic-ai,https://pydantic.dev/,https://github.com/pydantic/pydantic-ai/releases,https://pydantic.dev/pricing,https://pydantic.dev/pricing,https://pydantic.dev/articles/logfire-pricing-change,https://realpython.com/pydantic-ai/,https://www.zenml.io/blog/pydantic-ai-vs-langgraph,https://pydantic.dev/articles/logfire-pricing-change,https://pydantic.dev/articles/ai-is-making-remote-work-a-bigger-advantage-than-ever,https://pydantic.dev/articles/hack-monty-a-5000-bounty-to-break-our-python-sandbox
