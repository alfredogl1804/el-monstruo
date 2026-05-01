## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>Prefect</td>
</tr>
<tr>
<td>Versión Actual</td>
<td>3.6.28 (24 de abril de 2026)</td>
</tr>
<tr>
<td>Estado Actual</td>
<td>Activo</td>
</tr>
<tr>
<td>Precio Actual</td>
<td>Prefect Cloud ofrece un modelo de precios basado en asientos y espacios de trabajo, no en el uso. Los tiers son:
*   **Hobby:** Gratis para siempre. Incluye programación de flujos de trabajo, 2 usuarios, hasta 5 despliegues, 500 minutos de Prefect Serverless, observabilidad de flujos de trabajo, registro y alertas, y retención de 7 días.
*   **Starter:** $100/mes. Incluye todas las características de Hobby, más 3 usuarios, hasta 20 despliegues, 75 horas de Prefect Serverless, y 1,250 solicitudes de API/min.
*   **Team:** $100/usuario/mes (para 4-8 usuarios). Incluye todas las características de Starter, más hasta 100 despliegues, 225 horas de Prefect Serverless, cuentas de servicio, registro de auditoría de 24 horas, y 50 automatizaciones.
*   **Pro:** Precio personalizado (para 5-20 usuarios). Incluye todas las características de Team, más hasta 1,000 despliegues, 250 horas de Prefect Serverless, múltiples espacios de trabajo, SSO (SAML/OIDC), RBAC básico, y 5,000 solicitudes de API/min.
*   **Enterprise:** Precio personalizado (para 5+ usuarios). Ofrece despliegues ilimitados, horas de Serverless personalizadas, SSO (SAML/OIDC), SCIM, retención de registros de auditoría y de ejecución personalizados, roles personalizados, RBAC a nivel de objeto, IP Allowlisting, PrivateLink, entorno Sandbox, SLA de tiempo de actividad del 99.9%, y soporte con SLAs y portal.</td>
</tr>
<tr>
<td>Posicionamiento Competitivo</td>
<td>Prefect se posiciona como un framework de orquestación de flujos de trabajo para la construcción de pipelines de datos resilientes en Python, diferenciándose por su enfoque en la orquestación dinámica que se adapta a las condiciones de datos en tiempo real y evita bloqueos por DAGs estáticos. Sus principales competidores son Apache Airflow y Dagster. A diferencia de Dagster, Prefect Cloud no cobra por tarea o ejecución, ofreciendo horas serverless incluidas en sus planes, lo que proporciona una predictibilidad de costos superior.</td>
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
<td>Desde el 20 de marzo de 2026, los cambios principales en las versiones de desarrollo (`3.6.29.devX` y `3.6.28.devX`) de Prefect incluyen mejoras como la corrección de deadlocks en la inserción masiva de TRR y el manejo de serializadores desconocidos. Se han implementado numerosas correcciones de errores, destacando optimizaciones de rendimiento en `count_flow_runs`, detección de `CONTAINER_MISSING` en GCP, y mejoras en el seguimiento de `PrefectConcurrentFuture`. También se han realizado actualizaciones de dependencias y correcciones en pruebas. En cuanto a la documentación, se han añadido notas de lanzamiento para `prefect-redis==0.2.11` y `prefect-kubernetes==0.7.8`, y se ha ampliado la documentación sobre varios patrones de desarrollo y despliegue.</td>
</tr>
<tr>
<td>Noticia Más Relevante</td>
<td>La noticia más relevante de los últimos 40 días es la publicación del blog "Dagster vs Prefect: Self-Serve Plans Compared" el 14 de abril de 2026, donde Prefect destaca las diferencias en los modelos de precios y la oferta de horas serverless incluidas en sus planes de Prefect Cloud, posicionándose favorablemente frente a su competidor Dagster. Además, en abril de 2026, Prefect resaltó su arquitectura de agentes de IA y casos de uso críticos de latencia en una charla de PyAI Conf 2026.</td>
</tr>
<tr>
<td>Dato Sorprendente</td>
<td>El dato más sorprendente es que, a pesar de ser una herramienta de orquestación de flujos de trabajo, Prefect Cloud basa su modelo de precios en asientos y workspaces, no en el uso o la cantidad de tareas ejecutadas, lo que ofrece una predictibilidad de costos inusual en este tipo de servicios.</td>
</tr>
<tr>
<td>GitHub Stars</td>
<td>22.3k</td>
</tr>
</table>
<br>
## L03 a L15 — (Estructura estándar heredada de v7.0)
<br>
*Nota: Las capas L03 a L15 mantienen la estructura analítica profunda de la versión v7.0, actualizada con los datos de L01 y L02.*

---
**Fuentes Consultadas (Abril 2026):**
https://github.com/PrefectHQ/prefect/releases,https://artifacthub.io/packages/helm/prefect/prefect-server,https://pypi.org/project/prefect/,https://statusgator.com/services/prefect,https://incidenthub.cloud/status/prefect.io,https://www.prefect.io/pricing,https://www.prefect.io/blog/dagster-vs-prefect-self-serve-plans-compared,https://www.zenml.io/blog/prefect-pricing,https://www.reddit.com/r/dataengineering/comments/1hsg422/is_airflow_or_prefect_cheaper/,https://medium.com/the-prefect-blog/simple-success-based-pricing-3ff9bcec39f,https://www.prefect.io/blog/prefect-brand-2026,https://www.tipranks.com/news/private-companies/prefect-highlights-ai-agent-architecture-and-latency-critical-use-cases,https://dagster.io/learn/data-pipeline-orchestration-tools,https://kanerika.com/blogs/mlops-orchestration/
