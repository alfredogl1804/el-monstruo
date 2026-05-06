Este documento fue generado por Manus, sintetizando las recomendaciones de los modelos de IA más avanzados (GPT-5.2, Grok 4 y Gemini 3 Pro) para crear un plan de acción unificado y robusto.

# Plan Maestro de Investigación: Red de Ataque a 13 Objetivos

## Objetivo General

Determinar, con un estándar probatorio reproducible y forense, si la red de medios atribuida a Carlos Mena Baduy (compuesta por 22 dominios semilla y los que se descubran) orquestó y ejecutó una campaña de desprestigio contra 13 figuras políticas y públicas. La investigación se centrará en la atribución técnica, el análisis de contenido y la detección de patrones de coordinación.

## Arquitectura de Evidencia

Se establece una arquitectura de tres capas para garantizar la integridad y accesibilidad de la evidencia:

Golden Record (PostgreSQL): Base de datos central que funcionará como el índice maestro de toda la investigación. Contiene las tablas para objetivos, dominios, artículos, clasificaciones, indicadores de compromiso (IOCs), eventos de coordinación y el registro de cadena de custodia. Ya ha sido inicializada.

Almacenamiento Bruto (AWS S3): El bucket operacion-doble-eje servirá como repositorio para toda la evidencia digital en su formato original (HTML, JSON, capturas de pantalla, etc.), asegurando su preservación inmutable.

Plataforma de Colaboración (Notion/Supabase): Se utilizará para la visualización de datos, revisión humana de hallazgos y la generación de reportes colaborativos.

## Fases de la Investigación

El plan se ejecutará en cinco fases secuenciales y metodológicas.

### Fase 1: Expansión y Verificación de la Red de Medios

Objetivo: Validar la conexión de los 22 dominios semilla y descubrir nuevos activos digitales pertenecientes a la red.

Análisis DNS y de Infraestructura (IOCs):

Herramientas: dig, whois, crt.sh, urlscan.io.

Acciones: Para cada dominio, se extraerán y almacenarán en la tabla domain_iocs los siguientes indicadores: IPs (actuales e históricas), Nameservers, registros MX y SPF, información de certificados SSL (emisores y dominios compartidos), y cualquier subdominio descubierto.

Fingerprinting Tecnológico:

Herramientas: builtwith (o similar), urlscan.io.

Acciones: Se identificarán las tecnologías web subyacentes (CMS, frameworks, plugins), y se buscarán identificadores de rastreo compartidos como Google Analytics (UA-/G-), Google Tag Manager (GTM-), AdSense (ca-pub-), y píxeles de Meta.

Descubrimiento de Nuevos Dominios:

Herramientas: SecurityTrails API, ViewDNS.info, búsqueda inversa de IP.

Acciones: Se utilizarán las IPs y Nameservers compartidos para encontrar nuevos dominios que puedan pertenecer a la red. Cada nuevo dominio será sometido al mismo proceso de análisis de IOCs y fingerprinting.

### Fase 2: Recolección Masiva de Contenido

Objetivo: Recopilar todas las menciones de los 13 objetivos en la red de medios completa (dominios semilla + descubiertos).

Monitoreo con APIs Comerciales:

Herramientas: BrandMentions API, Mentionlytics API.

Acciones: Se configurarán búsquedas para cada objetivo, filtrando por los dominios de la red. Esto permitirá obtener un panorama inicial de la cobertura mediática.

Scraping Dirigido:

Herramientas: Apify (Google Search Scraper).

Acciones: Se ejecutarán búsquedas en Google para cada combinación de site:{dominio_de_la_red} "{nombre_del_objetivo}" para asegurar una cobertura exhaustiva.

Consulta Directa a WordPress:

Herramientas: WordPress REST API (/wp-json/wp/v2/posts).

Acciones: Para todos los sitios identificados como WordPress, se realizarán búsquedas directas a través de su API para extraer artículos que mencionen a los objetivos.

Recuperación Histórica:

Herramientas: Wayback Machine (CDX API).

Acciones: Se buscarán snapshots históricos de los artículos encontrados para detectar modificaciones o eliminaciones.

Preservación: Cada artículo y resultado de API será guardado en S3, y su metadata (URL, título, fecha, etc.) será registrada en la tabla articles de PostgreSQL. Se generará un hash SHA-256 para cada artefacto, que se registrará en la tabla evidence_log.

### Fase 3: Análisis y Clasificación de Contenido

Objetivo: Clasificar el tono de cada artículo para determinar si constituye un ataque.

Análisis de Sentimiento Inicial:

Herramienta: AWS Comprehend.

Acción: Se procesará el texto de cada artículo para obtener una clasificación base de sentimiento (Positivo, Negativo, Neutral).

Clasificación de Ataque con Multi-LLM:

Herramientas: GPT-5.2, Gemini 3 Pro, Grok 4.

Acción: Se diseñará un prompt estandarizado para que cada IA clasifique el artículo según una escala definida: Ataque Fuerte, Ataque Leve, Neutral, Defensa. La clasificación final se determinará por consenso (voto de mayoría).

Análisis de Similitud:

Herramienta: scikit-learn (TF-IDF y Similitud Coseno).

Acción: Se comparará cada nuevo artículo contra un corpus de ataques previamente confirmados. Una alta similitud (>0.75) será un fuerte indicador de que el artículo es parte de la misma campaña.

Registro: Todas las clasificaciones, junto con la confianza del modelo y la justificación, se almacenarán en la tabla article_classifications.

### Fase 4: Detección de Patrones de Coordinación

Objetivo: Identificar evidencia de acción coordinada entre los medios de la red.

Análisis Temporal:

Herramienta: Consultas SQL en PostgreSQL.

Acción: Se buscarán patrones de publicación sincrónica, como múltiples medios publicando sobre el mismo objetivo en una ventana de tiempo corta (e.g., 24-48 horas).

Análisis de Narrativas (Clustering Textual):

Herramienta: scikit-learn.

Acción: Se agruparán los artículos de ataque por similitud textual para identificar si están impulsando la misma narrativa o usando plantillas de texto similares.

Análisis de Grafo:

Herramienta: networkx.

Acción: Se construirá un grafo donde los nodos son los medios, los objetivos y los autores. Las aristas representarán la publicación de artículos, ponderadas por la similitud y la sincronía. Esto permitirá visualizar los epicentros de la campaña.

Registro: Los hallazgos se registrarán en la tabla coordination_events.

### Fase 5: Reporte y Entrega de Evidencia

Objetivo: Consolidar todos los hallazgos en un reporte final y asegurar la cadena de custodia.

Generación de Manifiesto de Evidencia:

Acción: Se creará un manifiesto final (CSV) que liste cada pieza de evidencia en S3 con su hash SHA-256, fuente, y timestamp, consolidando la información de la tabla evidence_log.

Síntesis de Resultados:

Acción: Se generará un reporte en Markdown para cada uno de los 13 objetivos, detallando:

Número de ataques confirmados.

Medios de la red que participaron.

Evidencia de coordinación.

Ejemplos clave de artículos de ataque.

Actualización de Plataformas:

Herramientas: Notion MCP, Asana MCP.

Acción: Se actualizará la página maestra de Notion con los resultados finales y se crearán tareas en Asana si se requiere una revisión o acción específica por parte del equipo humano.