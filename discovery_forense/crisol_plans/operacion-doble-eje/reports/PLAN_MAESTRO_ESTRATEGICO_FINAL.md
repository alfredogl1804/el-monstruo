# Plan Maestro Estratégico: Operación "Doble Eje"

**Fecha:** 23 de Febrero de 2026
**Autor:** Manus AI (con el consejo de los 5 Sabios)

---

## 1. Introducción y Marco Rector

Este documento presenta el plan estratégico definitivo para la investigación de la campaña de ataques mediáticos coordinados contra funcionarios de la CONADE y sus vínculos con ataques históricos a otros funcionarios públicos. El plan, denominado **Operación "Doble Eje"**, ha sido consolidado tras una consulta exhaustiva con el consejo de inteligencias artificiales avanzadas (los "5 Sabios") y está diseñado para maximizar la eficacia de todas las herramientas disponibles, garantizando un proceso riguroso y la generación de evidencia defendible.

El objetivo central es desmantelar y evidenciar la operación de dos ejes de ataque que, aunque aparentemente operan de forma independiente, podrían tener intersecciones en infraestructura, métodos o financiamiento. La investigación se guiará por la validación de dos hipótesis principales:

*   **Hipótesis 1 (Eje Mena/Meza):** Se postula la existencia de una campaña editorial y mediática sostenida, orquestada por Carlos Mena Baduy y Alejandro Meza Corrales. Esta campaña se caracterizaría por patrones de autoría, lenguaje específico, "paquetes" de publicación en medios satélite como *PorEsto!*, y una posible amplificación pagada para maximizar su alcance.

*   **Hipótesis 2 (Eje Vadillo/Rosado Pat):** Se investigará un patrón de filtraciones de información interna de la CONADE, presuntamente por parte de José Miguel Rosado Pat, que son posteriormente colocadas como notas, columnas o "trascendidos" en medios locales bajo la posible protección o dirección de Sergio Vadillo. El patrón de publicación estaría ligado a eventos administrativos clave dentro de la CONADE.

La condición fundamental de este plan es **no presuponer una coordinación** entre ambos ejes. El objetivo es, precisamente, comparar las "firmas" operativas de cada uno para detectar y probar intersecciones reales, ya sea en medios utilizados, narrativas, ventanas temporales de actividad, infraestructura digital o fuentes de financiamiento.

---

## 2. Fases de la Operación "Doble Eje"

El plan se estructura en cuatro capas operativas que se ejecutan en paralelo y convergen en la creación de un expediente maestro de inteligencia. Cada capa tiene un objetivo claro y utiliza un conjunto específico de herramientas y técnicas.

### Capa A: Construcción del Universo de Contenido

**Objetivo:** Recopilar, consolidar y normalizar más del 95% de los artículos de noticias, publicaciones en redes sociales y cualquier otro contenido relevante relacionado con los ataques, tanto a nivel histórico (backfill) como en tiempo real (monitoreo).

| Tarea | Herramientas | Descripción de la Acción |
| :--- | :--- | :--- |
| **Backfill Histórico Masivo** | Apify (Google Search Scraper), Wayback Machine, NewsPlease, Newspaper3k | Se ejecutarán docenas de búsquedas avanzadas en Google para recopilar URLs de los últimos 7 años, utilizando combinaciones de nombres, variantes ortográficas, medios y narrativas clave ("corrupción", "desvío", "aviador"). Se utilizará la Wayback Machine para recuperar contenido eliminado y crawlers especializados para extraer texto limpio de las URLs encontradas. |
| **Monitoreo Futuro** | Mentionlytics API v2 | Se reconfigurarán los trackers para usar lógica booleana avanzada, creando rastreadores específicos no solo para personas, sino también para las narrativas de ataque, permitiendo detectar la campaña incluso si cambia de objetivo. Se eliminará el tracker irrelevante "Hivecom". |

**Entregable:** Un repositorio centralizado en Amazon S3 conteniendo el corpus completo de la investigación (archivos HTML, PDF, texto plano) con metadatos enriquecidos (fecha, autor, medio, URL, etc.).

### Capa B: Normalización y Creación del "Golden Record"

**Objetivo:** Transformar el caótico conjunto de datos crudos en un dataset de inteligencia estructurado, deduplicado y defendible, que sirva como la única fuente de verdad para el análisis.

| Tarea | Herramientas | Descripción de la Acción |
| :--- | :--- | :--- |
| **Diseño del Esquema de Datos** | AWS DynamoDB | Se implementará un esquema de base de datos NoSQL con cuatro tablas interconectadas: **items** (contenido individual), **sources** (medios y cuentas), **claims** (acusaciones normalizadas) y **events** (hitos del mundo real para correlación). Este modelo supera la propuesta inicial al permitir un análisis más profundo de las narrativas y sus orígenes. |
| **Deduplicación y Detección de Sindicación** | AWS Bedrock, Python (Pandas) | Se generarán hashes y embeddings vectoriales para cada pieza de contenido. Esto permitirá agrupar copias exactas y paráfrasis, identificando quién publicó una historia primero (el **origen**) y quiénes la replicaron después (los **amplificadores**). |

**Entregable:** Una base de datos estructurada y limpia en DynamoDB que servirá como el núcleo para todas las consultas y análisis posteriores.

### Capa C: Atribución y Mapeo de Firmas

**Objetivo:** Separar las campañas por eje operativo (H1 vs. H2), atribuir la autoría de contenido anónimo y detectar puntos de cruce reales entre ambos ejes.

| Tarea | Herramientas | Descripción de la Acción |
| :--- | :--- | :--- |
| **Lingüística Forense** | Claude Opus 4.6, Python | Se construirá un "perfil estilométrico" de los textos firmados por Carlos Mena Baduy y se comparará con el estilo de las notas anónimas o "trascendidos", analizando n-gramas, puntuación, longitud de frase y muletillas para asignar una probabilidad de autoría. |
| **Análisis de Firma Operativa** | Grok 4, Python (Matplotlib) | Se analizarán las series temporales de publicación para detectar ráfagas, cadencia, y correlaciones con eventos externos. Se medirá la velocidad de replicación y la concentración de ataques por medio para cada eje. |
| **Análisis de Infraestructura** | Gemini 3.1 Pro, Manus (Wide Research), Spiderfoot | Se irá más allá del WHOIS/IP para buscar identificadores compartidos en el código fuente de los sitios web (Google Analytics, AdSense, Meta Pixel), lo que constituye una evidencia más fuerte de operación coordinada. |
| **Análisis de Financiamiento** | Apify (Facebook Ads Library Scraper) | Se investigará qué páginas están pagando para promocionar los ataques en redes sociales, cuánto gastan y a qué audiencias se dirigen, buscando el rastro del dinero que financia la difamación. |

**Entregable:** Un grafo de atribución y un informe detallado sobre las "firmas" de cada eje, destacando cualquier solapamiento probado.

### Capa D: Síntesis y Producto Final de Inteligencia

**Objetivo:** Consolidar todos los hallazgos en un producto de inteligencia accionable que resista el escrutinio legal y mediático, y que pueda ser utilizado para la toma de decisiones estratégicas.

| Tarea | Herramientas | Descripción de la Acción |
| :--- | :--- | :--- |
| **Visualización de Datos** | AWS QuickSight, Gephi | Se crearán dashboards interactivos para visualizar las líneas de tiempo, los clusters narrativos y las redes de sindicación. Se usará Gephi para generar un mapa de red final que muestre las conexiones probadas entre actores, medios y financiamiento. |
| **Generación de Expedientes** | GPT-5.2, Manus | Se redactarán dosieres de inteligencia separados para cada eje de operación, detallando su modus operandi, actores clave, y la evidencia primaria recopilada. Finalmente, se producirá un informe ejecutivo que resuma los hallazgos y presente una narrativa probatoria clara. |

**Entregable:** Un dashboard interactivo, un grafo de red visual y un expediente de inteligencia completo con anexos metodológicos y de evidencia.

---

## 3. Checklist de Ejecución: Estado Actual y Pasos Siguientes

A continuación se presenta el estado de la investigación y las tareas pendientes priorizadas.

### Tareas Completadas

- [x] **Configuración Inicial:** Se ha solucionado el acceso a la API v2 de Mentionlytics, se han creado 7 trackers iniciales y se han auditado las configuraciones de AWS y los 5 Sabios.
- [x] **Recolección Preliminar:** Se ha ejecutado una primera ronda de búsqueda en Google, obteniendo 196 URLs relevantes.
- [x] **Análisis de Sabios:** Se ha consultado a los 5 Sabios y se han consolidado sus recomendaciones en este plan maestro.

### Tareas Pendientes (Priorizadas)

**Semana 1: Cimientos y Recolección Masiva**
- [ ] **Fase 0: Correcciones Urgentes**
  - [ ] Eliminar el tracker "Hivecom" de Mentionlytics.
  - [ ] Reconfigurar todos los trackers de Mentionlytics con la arquitectura de 19 keywords y lógica booleana avanzada propuesta por Claude y refinada por GPT-5.2.
- [ ] **Fase 1: Backfill Histórico**
  - [ ] Ejecutar el sprint de recolección masiva con Apify y Wayback Machine para construir el universo de contenido (meta: 1,500-3,000 artefactos).
  - [ ] Implementar el pipeline de ingesta en AWS (S3, Lambda) para procesar y normalizar el contenido a medida que se recopila.

**Semanas 2-4: Análisis Profundo y Síntesis**
- [ ] **Fase 2: Procesamiento y Enriquecimiento**
  - [ ] Ejecutar el clustering de historias y la detección de sindicación.
  - [ ] Extraer y normalizar las "claims" o acusaciones principales.
  - [ ] Iniciar la investigación de financiamiento con el scraper de la Facebook Ads Library.
- [ ] **Fase 3 y 4: Atribución y Entrega**
  - [ ] Realizar el análisis de estilometría y de firma de infraestructura.
  - [ ] Construir el modelo de atribución de ejes y el grafo de red final.
  - [ ] Generar los dashboards y el expediente final de inteligencia.

---

Este plan representa un enfoque integral y metódico para cumplir con los objetivos de la investigación. Se solicita su revisión y aprobación para proceder con la ejecución de la Fase 0.
