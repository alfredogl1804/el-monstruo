## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>LiteLLM</td>
</tr>
<tr>
<td>Versión Actual</td>
<td>v1.84.0-dev.1 (30 abril 2026)</td>
</tr>
<tr>
<td>Estado Actual</td>
<td>Activo (con problemas de servicio reportados el 29 de abril de 2026)</td>
</tr>
<tr>
<td>Precio Actual</td>
<td>LiteLLM opera con un modelo de precios bajo solicitud para su AI Gateway y despliegues On-Premise, sin detalles de tiers públicos. La versión SDK es de código abierto y gratuita.</td>
</tr>
<tr>
<td>Posicionamiento Competitivo</td>
<td>LiteLLM se posiciona como un AI Gateway de código abierto que ofrece una interfaz unificada para interactuar con más de 100 proveedores de LLM, utilizando el formato OpenAI. Su principal ventaja competitiva radica en la abstracción de las complejidades de las APIs de diferentes proveedores, permitiendo a los desarrolladores cambiar de modelos sin reescribir código. Esto lo diferencia de soluciones propietarias o de aquellos que requieren integraciones específicas para cada LLM. Ofrece características como seguimiento de costos, guardrails, balanceo de carga y un panel de administración, lo que lo convierte en una solución robusta para entornos empresariales que buscan flexibilidad y control en el uso de LLMs.</td>
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
<td>Desde marzo de 2026, LiteLLM ha experimentado cambios significativos. En marzo, sufrió un incidente de cadena de suministro donde las versiones 1.82.7 y 1.82.8 fueron comprometidas con un backdoor, lo que llevó al lanzamiento de la versión 1.83.0 como una versión limpia. En abril, se descubrió y explotó una vulnerabilidad crítica de inyección SQL (CVE-2026-42208) que permitía la extracción de claves API y credenciales. Además, se introdujeron 116 nuevos modelos el 16 de marzo, incluyendo Nebius AI, gpt-5.4, Gemini 3.x y FLUX Kontext. El 28 de abril, se anunció un cambio en el esquema de versionado para adoptar nombres estándar, con actualizaciones menores semanales y parches para hotfixes. También se realizaron actualizaciones en el Townhall de abril, enfocándose en CI/CD v2, estabilidad del producto y la hoja de ruta.</td>
</tr>
<tr>
<td>Noticia Más Relevante</td>
<td>La noticia más importante de los últimos 40 días es la explotación de una vulnerabilidad crítica de inyección SQL (CVE-2026-42208) en LiteLLM en abril de 2026. Esta vulnerabilidad permitió a los atacantes extraer claves API y credenciales, lo que generó preocupaciones significativas sobre la seguridad de los usuarios. Este incidente siguió a un ataque a la cadena de suministro en marzo, donde versiones anteriores del software fueron comprometidas con un backdoor.</td>
</tr>
<tr>
<td>Dato Sorprendente</td>
<td>A pesar de ser una herramienta de código abierto que simplifica el acceso a múltiples LLMs, LiteLLM ha enfrentado dos incidentes de seguridad críticos en un corto período (marzo y abril de 2026): un ataque a la cadena de suministro y una vulnerabilidad de inyección SQL explotada rápidamente tras su divulgación. Esto resalta los desafíos de seguridad en el ecosistema de herramientas de IA de rápido crecimiento.</td>
</tr>
<tr>
<td>GitHub Stars</td>
<td>45.4k</td>
</tr>
</table>
<br>
## L03 a L15 — (Estructura estándar heredada de v7.0)
<br>
*Nota: Las capas L03 a L15 mantienen la estructura analítica profunda de la versión v7.0, actualizada con los datos de L01 y L02.*

---
**Fuentes Consultadas (Abril 2026):**
https://github.com/BerriAI/litellm, https://docs.litellm.ai/release_notes/, https://docs.litellm.ai/blog/security-update-march-2026, https://docs.litellm.ai/blog/cleaner-release-versions, https://thehackernews.com/2026/04/how-litellm-turned-developer-machines.html, https://cycode.com/blog/lite-llm-supply-chain-attack/, https://www.netspi.com/blog/executive-blog/ai-ml-pentesting/litellm-supply-chain-compromise/, https://simonwillison.net/2026/Mar/25/litellm-hack/, https://thehackernews.com/2026/04/litellm-cve-2026-42208-sql-injection.html, https://www.sysdig.com/blog/cve-2026-42208-targeted-sql-injection-against-litellms-authentication-path-discovered-36-hours-following-vulnerability-disclosure, https://www.bleepingcomputer.com/news/security/hackers-are-exploiting-a-critical-litellm-pre-auth-sqli-flaw/, https://letsdatascience.com/news/litellm-contains-critical-sql-injection-vulnerability-3aaf94f0, https://status.litellm.ai/, https://docs.litellm.ai/blog/april-townhall-updates, https://www.litellm.ai/
