## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>Hasura</td>
</tr>
<tr>
<td>Versión Actual</td>
<td>DDN-Release (27 abril 2026) y V3-Engine v2026.02.17 (17 febrero 2026)</td>
</tr>
<tr>
<td>Estado Actual</td>
<td>Activo</td>
</tr>
<tr>
<td>Precio Actual</td>
<td>Hasura DDN ofrece un modelo de precios basado en "modelos activos":
- **DDN Free**: $0, ideal para desarrolladores individuales.
- **DDN Base**: Desde $5/modelo activo/mes, para equipos que construyen un supergrafo crítico para el negocio.
- **DDN Advanced**: Desde $30/modelo activo/mes, para múltiples equipos colaborando en un supergrafo federado.
Un "modelo activo" se define como cualquier modelo o comando en los metadatos al que se accede más de 1000 veces al mes. También se ofrece la opción **Private DDN** para requisitos avanzados de seguridad y cumplimiento, disponible con los planes Base y Advanced, que permite alojar el plano de datos de Hasura en infraestructura dedicada o VPCs dedicadas en Hasura Cloud.</td>
</tr>
<tr>
<td>Posicionamiento Competitivo</td>
<td>Hasura se posiciona como una plataforma líder para la creación instantánea de APIs GraphQL en tiempo real sobre diversas fuentes de datos, destacando su enfoque en la red de entrega de datos (DDN) y la capacidad de federar supergrafos. Sus principales competidores incluyen soluciones como Apollo GraphQL, Directus y Strapi, así como servicios backend-as-a-service como AWS AppSync. Hasura se diferencia por su capacidad de generar APIs GraphQL a partir de bases de datos existentes con control de acceso granular y webhooks, y su reciente evolución hacia la arquitectura DDN con soporte para múltiples conectores de datos. Su modelo de precios basado en "modelos activos" busca escalar de manera predecible desde startups hasta empresas, ofreciendo opciones de despliegue flexibles y seguridad avanzada con Private DDN.</td>
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
<td>Desde el 20 de marzo de 2026, Hasura ha lanzado varias actualizaciones importantes centradas en su Data Delivery Network (DDN) y sus conectores de datos:
- **DDN-Release**: Múltiples lanzamientos semanales (23, 30 de marzo, 6, 13, 20, 27 de abril de 2026) con mejoras continuas.
- **NDC Elasticsearch v1.10.0 (23 de marzo de 2026)**: Actualización a Go v1.26 y corrección de vulnerabilidades.
- **NDC MongoDb v2.0.0 (23 de marzo de 2026)**: Incorporación de soporte para consultas relacionales (proyección, filtrado, ordenación, paginación, joins, agregaciones, funciones de ventana, uniones y streaming). También se añadió un almacén de configuración respaldado por PostgreSQL para la carga de esquemas bajo demanda y la agrupación de documentos para agregación. Se introdujeron cambios **BREAKING** con la actualización a `ndc-spec v0.2` y la eliminación de la agregación de conteo personalizada.
- **NDC MongoDb v2.0.1 (23 de marzo de 2026)**: Correcciones de errores y lanzamiento.
- **NDC SDK Go v2.3.0 (16 de marzo de 2026)**: Deprecación de módulos de entorno y actualización de Go a v1.24.12 y v1.26.
- **NDC NodeJS Lambda v1.20.3 (16 de marzo de 2026)**: Actualización de `ndc-sdk-typescript` a v8.5.0.
- **NDC SDK RS v0.9.0 (9 de marzo de 2026)**: Adición de soporte para consultas relacionales y de streaming en el SDK de Rust, y actualización para soportar `ndc-spec v0.2.10`.
- **NDC SDK TypeScript v8.5.0 (2 de marzo de 2026)**: Se hizo configurable el límite de cuerpo de Fastify.</td>
</tr>
<tr>
<td>Noticia Más Relevante</td>
<td>La noticia más importante es la evolución continua de Hasura hacia su **Data Delivery Network (DDN)**, con múltiples lanzamientos semanales y actualizaciones significativas en sus conectores de datos, especialmente el lanzamiento de **NDC MongoDb v2.0.0** con soporte completo para consultas relacionales y la adopción de `ndc-spec v0.2`. Esto subraya el compromiso de Hasura con la federación de datos y la expansión de sus capacidades de integración.</td>
</tr>
<tr>
<td>Dato Sorprendente</td>
<td>Hasura ha realizado una transición significativa en su modelo de precios, pasando de un enfoque basado en el consumo tradicional a uno innovador centrado en "modelos activos" dentro de su Data Delivery Network (DDN), lo que implica una nueva forma de medir el uso y el valor para los usuarios.</td>
</tr>
<tr>
<td>GitHub Stars</td>
<td>32k</td>
</tr>
</table>
<br>
## L03 a L15 — (Estructura estándar heredada de v7.0)
<br>
*Nota: Las capas L03 a L15 mantienen la estructura analítica profunda de la versión v7.0, actualizada con los datos de L01 y L02.*

---
**Fuentes Consultadas (Abril 2026):**
https://hasura.io/changelog, https://hasura.io/pricing, https://github.com/hasura/graphql-engine
