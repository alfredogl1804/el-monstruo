# Plan Maestro Estratégico v2: Operación "Doble Eje"

**Fecha:** 23 de Febrero de 2026
**Autor:** Manus AI (con el consejo de los 5 Sabios)
**Versión:** 2.0 — Corregida tras observaciones del cliente

---

## 1. Introducción y Marco Rector

Este documento presenta el plan estratégico definitivo para la investigación de la campaña de ataques mediáticos coordinados contra funcionarios de la CONADE y sus vínculos con ataques históricos a otros funcionarios públicos. El plan, denominado **Operación "Doble Eje"**, ha sido consolidado tras una consulta exhaustiva con el consejo de inteligencias artificiales avanzadas (los "5 Sabios") y corregido con dos observaciones clave del cliente.

La investigación se guiará por la validación de dos hipótesis principales, sin presuponer coordinación entre ellas:

**Hipótesis 1 (Eje Mena/Meza):** Campaña editorial y mediática sostenida, orquestada por Carlos Mena Baduy y Alejandro Meza Corrales, con patrones de autoría, lenguaje específico, "paquetes" de publicación en medios satélite, y posible amplificación pagada. La hipótesis incluye un componente financiero-legal: los ataques mediáticos podrían ser la contraprestación de Mena a Meza por acceso institucional o financiero a través del Infonavit.

**Hipótesis 2 (Eje Vadillo/Rosado Pat):** Patrón de filtraciones de información interna de la CONADE por parte de José Miguel Rosado Pat, colocadas como notas o "trascendidos" en medios locales bajo la protección de Sergio Vadillo. El patrón de publicación estaría ligado a eventos administrativos clave dentro de la CONADE.

---

## 2. Arquitectura del Plan: 4 Capas + 1 Vertical

El plan se estructura en cuatro capas operativas horizontales que convergen en un expediente maestro, más un **vertical de inteligencia legal-financiera** que atraviesa todas las capas. Este vertical, identificado como el elemento de mayor potencial probatorio por GPT-5.2 y Claude Opus 4.6, integra el dossier legal de Carlos Mena Baduy descubierto durante la investigación.

---

### Capa A: Construcción del Universo de Contenido

**Objetivo:** Recopilar y consolidar más del 95% de los artículos, publicaciones y contenido relevante relacionado con los ataques, tanto a nivel histórico como en tiempo real.

| Tarea | Herramientas | Descripción |
| :--- | :--- | :--- |
| **A.1 Corrección de Mentionlytics** | Mentionlytics API v2 | Eliminar tracker "Hivecom". Reconfigurar "Guillermo Cortez CONADE" como `"Guillermo Cortés" OR "Guillermo Cortez"` (sin CONADE). Crear arquitectura de 19 keywords en 4 bloques: personas atacadas (8), actores de la red (5), medios (4), narrativas (2). Agregar keywords del dossier legal: "Factor Finvex", "FINRED", "690942", "1363/2017", "641/2020". |
| **A.2 Backfill Histórico Focalizado** | Apify (Google Search Scraper), Wayback Machine | Priorizar el rango temporal **marzo 2019 – agosto 2020** (período de la secuencia operativa Mena-Meza) antes del backfill generalista. Ejecutar 28 búsquedas avanzadas para Castro, CONADE, actores y medios. Recuperar notas eliminadas con Wayback Machine. |
| **A.3 Crawling de Medios de la Red** | Apify (Website Content Crawler) | Crawlear los 5 medios principales de la red (El Principal, Grillo de Yucatán, Grillo Porteño, El Chismógrafo, Formal Prisión) para extraer su archivo histórico completo. |
| **A.4 Wide Research: Infraestructura Digital** | Manus (Wide Research) | Investigación paralela amplia sobre los dominios de la red: correlaciones en direcciones IP, registros WHOIS históricos, servidores DNS, y huellas digitales compartidas (Google Analytics, AdSense, Meta Pixel, plantillas CMS). |
| **A.5 Wide Research: Dossier Legal** | Manus (Wide Research) | Investigación paralela sobre registros públicos: CompraNet (contratos Finvex-Infonavit), SIPOT/PNT (transparencia), CNBV/SIPRES (regulación SOFOMs), CONDUSEF (quejas), Poder Judicial Federal (expedientes), DOF (nombramientos de Meza). |
| **A.6 Monitoreo Futuro** | Mentionlytics (continuo) | Trackers activos 24/7 con alertas para nuevas menciones. Perfiles sociales de actores y medios vinculados. |

---

### Capa B: Normalización y Creación del "Golden Record"

**Objetivo:** Transformar los datos crudos en un dataset de inteligencia estructurado, deduplicado y defendible.

| Tarea | Herramientas | Descripción |
| :--- | :--- | :--- |
| **B.1 Esquema de Datos** | AWS DynamoDB | Implementar 5 tablas interconectadas: **items** (contenido individual con sentimiento, toxicidad, target, eje), **sources** (medios y cuentas con fingerprints digitales), **claims** (acusaciones normalizadas por tipo y target), **events** (hitos del mundo real para correlación), **entities** (personas, empresas, casos judiciales con relaciones). |
| **B.2 Ingesta del Dossier Legal** | AWS S3 + DynamoDB | Crear Golden Record de Mena/Meza/Factor Finvex/FINRED + casos judiciales (1363/2017, 641/2020, sentencia 03/2019, denuncias de fraude). Cada documento con hash SHA-256 y cadena de custodia. |
| **B.3 Procesamiento Paralelo** | Manus (Enjambre, hasta 2,000 subtareas) | Ejecutar Enjambre con las 196+ URLs recopiladas. Cada agente paralelo extrae de una URL: fecha de publicación, titular, autor/byline, entidades mencionadas (personas, instituciones), tono/sentimiento, y genera un hash de deduplicación. |
| **B.4 Deduplicación y Sindicación** | AWS Bedrock (embeddings), Python | Generar embeddings vectoriales para agrupar copias exactas y paráfrasis. Registrar quién publicó primero (origen) vs. quién replicó después (amplificadores). |
| **B.5 Análisis de Sentimiento** | AWS Comprehend | Procesar todos los textos con `DetectSentiment` y `DetectEntities` en español (`LanguageCode: 'es'`). Almacenar scores y entidades en DynamoDB. |

---

### Capa C: Atribución y Mapeo de Firmas

**Objetivo:** Separar las campañas por eje operativo, atribuir autoría de contenido anónimo, detectar puntos de cruce reales entre ejes, y establecer nexos financiero-legales.

| Tarea | Herramientas | Descripción |
| :--- | :--- | :--- |
| **C.1 Lingüística Forense** | Claude Opus 4.6, Python | Construir perfil estilométrico de textos firmados por Mena Baduy vs. textos anónimos/trascendidos. Analizar n-gramas, puntuación, longitud de frase, muletillas, adjetivación. Clasificador de probabilidad de autoría. |
| **C.2 Firma Operativa** | Grok 4, Python (Matplotlib) | Analizar series temporales de publicación: ráfagas, cadencia, correlación con eventos. Cross-correlation con lag entre filtraciones internas y publicaciones. Velocidad de replicación entre medios. |
| **C.3 Infraestructura Digital** | Gemini 3.1 Pro, Spiderfoot, theHarvester | Extraer IDs compartidos del código fuente de los sitios (Google Analytics, Tag Manager, AdSense, ads.txt, Meta Pixel). Mapear propiedad/operación probable. Instalar y ejecutar Spiderfoot para emails/dominios. |
| **C.4 Atribución Financiera y Legal (VERTICAL PRIORITARIO)** | Wide Research, Enjambre, Sabios | **Sub-módulo nuevo.** Integra el dossier legal de Mena Baduy. Tres líneas de investigación prioritarias (ver Sección 3). |
| **C.5 Amplificación Pagada** | Apify (Facebook Ads Library Scraper) | Scraping de la biblioteca de anuncios de Meta para los medios de la red. Identificar quién pauta contenido contra los targets, cuánto gasta, fechas y segmentación. |
| **C.6 Cruce CONADE vs. Castro** | Python (Pandas), Enjambre | Matriz de coincidencia cruzando autores/medios de ataques a Castro (2018-2023) con autores/medios de ataques a CONADE (2024-2026). Visualización de red que muestre el reciclaje de medios y actores. |

---

### Capa D: Síntesis y Producto Final de Inteligencia

**Objetivo:** Consolidar hallazgos en un producto de inteligencia accionable y defendible.

| Tarea | Herramientas | Descripción |
| :--- | :--- | :--- |
| **D.1 Timeline Probatorio** | Python (Matplotlib), AWS QuickSight | Timeline dual: eventos legales de Mena en un eje, ataques mediáticos en otro. Visualizar correlaciones temporales. |
| **D.2 Grafo de Red** | Gephi, Python (NetworkX) | Mapa visual con nodos (actores, medios, empresas, casos) y aristas (republicación, similitud, IDs compartidos, pauta, co-ocurrencia). Exportar en formato CSV de nodos y aristas. |
| **D.3 Dashboards** | AWS QuickSight | Dashboards interactivos: top dominios, clusters narrativos, red de sindicación, picos de actividad. |
| **D.4 Expediente Final** | GPT-5.2, Manus | Dosieres separados por eje + informe ejecutivo con narrativa probatoria, anexos metodológicos y cadena de custodia de evidencia. |
| **D.5 Monitoreo Automatizado** | Manus (Playbook), AWS Lambda | Playbook "Auditoría de Nota Nueva": cada 6 horas verifica Mentionlytics API, descarga nuevas menciones, ejecuta Comprehend, busca replicación en otros medios del clúster, y genera alerta si detecta ataque coordinado. |

---

## 3. Vertical Prioritario: Dossier Legal-Financiero de Mena Baduy (C.4)

GPT-5.2 y Claude Opus 4.6 coinciden en que este vertical tiene **mayor prioridad que el backfill generalista de scraping**, porque ofrece un nexo causal documentado (semanas) vs. correlación estadística (meses). El monitoreo en tiempo real no se detiene, pero el backfill se re-enfoca.

### 3.1 Las 3 Líneas de Investigación Prioritarias

**Línea 1 (Prioridad Crítica): Factor Finvex ↔ Infonavit ↔ Meza Corrales**

Factor Finvex (SOFOM de Mena, código CNBV 690942) está registrada en el catálogo de instituciones financieras vinculadas al Infonavit. Meza Corrales fue nombrado Gerente de Cumplimiento Legal del Infonavit en abril de 2019. Si se prueba una relación operativa (contratos, cesiones de crédito, supervisión), se establece el canal financiero de toda la operación. La pregunta central es: ¿los ataques mediáticos son la contraprestación de Mena a Meza por acceso institucional?

| Tarea | Herramienta |
| :--- | :--- |
| Buscar contratos Finvex-Infonavit en CompraNet, SIPOT, PNT | Wide Research |
| Descargar catálogo completo CNBV de SOFOMs vinculadas a Infonavit | Enjambre |
| Buscar cesiones de crédito en DOF, Gacetas, bases de transparencia | Wide Research + Sabios |
| Mapear rol exacto de Meza: organigramas históricos, DOF, LinkedIn | Apify + Wide Research |
| Analizar si Cumplimiento Legal supervisa SOFOMs | Sabios (Sonar con prompt académico) |
| Cruzar accionistas de Finvex con red de actores conocidos | DynamoDB + Wide Research |

**Línea 2 (Prioridad Crítica): Cronología Marzo 2019 → Agosto 2020**

La secuencia temporal no es coincidencia: sentencia contra Finvex (marzo 2019) → Meza en Infonavit (abril 2019) → primer ataque contra Cortés (julio 2019) → Mena se ampara (agosto 2020). Claude Opus propone que la sentencia de marzo 2019 fue el evento catalizador que activó la relación operativa Mena-Meza.

| Tarea | Herramienta |
| :--- | :--- |
| Obtener sentencia completa de marzo 2019 | Wide Research + Enjambre |
| Focalizar backfill de Apify SOLO en marzo 2019 – agosto 2020 | Apify (Google Search Scraper) |
| Crear timeline dual: eventos legales vs. ataques mediáticos | AWS Lambda + DynamoDB |
| Verificar quién nombró a Meza en Infonavit | Wide Research (DOF, boletines) |

**Línea 3 (Prioridad Alta): Amparo Penal 641/2020**

El amparo ante un juez de adolescentes es una anomalía procesal grave que indica posible forum shopping o corrupción. Además, ampararse en 3 distritos contra órdenes que aún no existen demuestra conciencia de culpabilidad.

| Tarea | Herramienta |
| :--- | :--- |
| Identificar juez, abogado firmante y resolución del amparo | Wide Research |
| Verificar si las órdenes de aprehensión se materializaron | Wide Research (Poder Judicial) |
| Cruzar abogado del amparo con otros asuntos de Mena/Finvex | Enjambre |
| Documentar la anomalía procesal para el expediente | Claude Opus (análisis legal) |

### 3.2 Líneas Secundarias del Dossier

| Línea | Prioridad | Herramienta Principal |
| :--- | :--- | :--- |
| Juicio Mercantil 1363/2017: Identificar a Ángel Sánchez Bernal | Alta | Wide Research |
| FINRED vs. NAFIN (2005): ¿Castro estaba en NAFIN? | Alta | Wide Research + Sabios |
| Denuncias de fraude: Consolidar y buscar patrones | Media | Wide Research + Enjambre |
| Calificación 0 CONDUSEF: Documentar | Media | Apify + Sabios |

---

## 4. Roles Asignados

### Inteligencias Artificiales (Los 5 Sabios)

| Sabio | Rol | Tareas Principales |
| :--- | :--- | :--- |
| **GPT-5.2** | Orquestador | Diseño probatorio, QA de hallazgos, redacción del expediente final, control de sesgos |
| **Claude Opus 4.6** | Lingüista Forense + Analista Legal | Estilometría, normalización de claims, análisis de anomalías procesales del dossier Mena |
| **Grok 4** | Radar Táctico | Series temporales, detección de ráfagas, correlaciones con eventos, scoring de coordinación |
| **Gemini 3.1 Pro** | Estructurador + Infraestructura | Modelo de datos, grafo de red, fingerprinting técnico (IDs, ads.txt, trackers) |
| **Sonar Deep Research** | Cronista + Regulatorio | Líneas de tiempo, marco regulatorio de SOFOMs, investigación con prompts académicos |

### Herramientas Nativas de Manus

| Herramienta | Uso Específico |
| :--- | :--- |
| **Wide Research** | Investigación paralela de: (1) infraestructura digital de medios, (2) registros públicos del dossier legal, (3) organigramas y nombramientos históricos |
| **Enjambre (Map)** | Procesamiento paralelo de: (1) 196+ URLs para extracción de datos, (2) catálogos CNBV/SOFOMs, (3) cruce de abogados/despachos entre casos de Mena |
| **Playbook** | Automatización de: "Auditoría de Nota Nueva" cada 6 horas (Mentionlytics → S3 → Comprehend → alerta) |

### Herramientas Open Source de GitHub

| App | Uso | Instalación |
| :--- | :--- | :--- |
| Spiderfoot | OSINT de dominios/emails de medios de la red | `pip install spiderfoot` |
| theHarvester | Emails y subdominios de sitios sospechosos | `pip install theHarvester` |
| Gephi | Visualización de red (nodos y aristas) | Exportar CSV desde Manus, importar en Gephi |
| NewsPlease | Parser de noticias RSS/URLs en español | `pip install news-please` |
| Newspaper3k | Crawler de artículos completos | `pip install newspaper3k` |

---

## 5. Cronograma de Ejecución

### Semana 1: Cimientos + Dossier Legal (Prioridad Máxima)

| Día | Tarea | Herramienta |
| :--- | :--- | :--- |
| 1 | Eliminar Hivecom, reconfigurar Mentionlytics (19 keywords) | Mentionlytics API |
| 1 | Crear estructura S3 + tablas DynamoDB | AWS |
| 1-2 | Ingestar dossier legal en Golden Record (B.2) | AWS S3 + DynamoDB |
| 2-3 | Wide Research: Finvex-Infonavit + Cronología + Amparo | Manus Wide Research |
| 3-5 | Backfill focalizado: marzo 2019 – agosto 2020 | Apify Google Search |
| 5-7 | Enjambre: procesar URLs + catálogos CNBV | Manus Enjambre |

### Semana 2: Recolección Masiva + Análisis Inicial

| Día | Tarea | Herramienta |
| :--- | :--- | :--- |
| 8-10 | Backfill histórico completo (7 años) | Apify + Wayback |
| 8-10 | Crawling de los 5 medios de la red | Apify Website Crawler |
| 10-12 | Comprehend: sentimiento + entidades en español | AWS Comprehend |
| 12-14 | Clustering y detección de sindicación | AWS Bedrock + Python |

### Semana 3: Atribución y Cruce

| Día | Tarea | Herramienta |
| :--- | :--- | :--- |
| 15-17 | Estilometría de Mena Baduy | Claude Opus |
| 15-17 | Series temporales y firma operativa | Grok 4 |
| 17-19 | Infraestructura digital (IDs compartidos) | Gemini + Spiderfoot |
| 19-21 | Facebook Ads Library | Apify |
| 19-21 | Cruce CONADE vs. Castro | Python + Enjambre |

### Semana 4: Producto Final

| Día | Tarea | Herramienta |
| :--- | :--- | :--- |
| 22-24 | Timeline probatorio + grafo de red | Python + Gephi |
| 24-26 | Dashboards interactivos | AWS QuickSight |
| 26-28 | Expediente final + dosieres por eje | GPT-5.2 + Manus |
| 28+ | Monitoreo automatizado continuo | Playbook + Lambda |

---

## 6. Checklist de Estado Actual

### Completado

| Tarea | Estado |
| :--- | :--- |
| Mentionlytics API v2 solucionada | Funcional |
| 7 trackers de competidores creados | Indexando (24-48h) |
| Apify Google Search: 196 URLs encontradas | Primera ronda completa |
| OSINT de infraestructura: DNS, WHOIS, código fuente de 9 medios | Completo |
| 5 clusters de medios identificados | Completo |
| Jhony Alamilla Castro identificado como operador de los Grillos | Confirmado |
| AWS configurado y auditado (12 servicios activos) | Listo |
| 5 Sabios actualizados y consultados | 5/5 respondieron |
| Dossier legal de Mena Baduy recopilado | 7 hallazgos documentados |
| Consulta focalizada sobre integración del dossier | GPT-5.2 + Claude respondieron |

### Pendiente (Priorizado)

| Prioridad | Tarea |
| :--- | :--- |
| **P0 (hoy)** | Eliminar tracker Hivecom |
| **P0 (hoy)** | Reconfigurar keywords de Mentionlytics |
| **P0 (72h)** | Ingestar dossier legal en Golden Record |
| **P0 (72h)** | Wide Research: Finvex-Infonavit + Cronología + Amparo |
| **P1 (semana 1)** | Backfill focalizado marzo 2019 – agosto 2020 |
| **P1 (semana 1)** | Enjambre: procesar 196+ URLs |
| **P1 (semana 1)** | Crear estructura S3 + DynamoDB |
| **P2 (semana 2)** | Backfill histórico completo |
| **P2 (semana 2)** | Crawling de medios de la red |
| **P2 (semana 2)** | AWS Comprehend: sentimiento + entidades |
| **P3 (semana 3)** | Estilometría, firma operativa, infraestructura |
| **P3 (semana 3)** | Facebook Ads Library |
| **P3 (semana 3)** | Cruce CONADE vs. Castro |
| **P4 (semana 4)** | Producto final: timeline, grafo, dashboards, expediente |

---

## 7. Métricas de Éxito por Fase

| Fase | Métrica | Meta |
| :--- | :--- | :--- |
| Semana 1 | URLs/artefactos en Golden Record | >500 |
| Semana 1 | Líneas legales del dossier con avance | 3 de 3 prioritarias |
| Semana 2 | Artículos históricos respaldados | >1,500 |
| Semana 2 | Datos procesados por Comprehend | >80% del corpus |
| Semana 3 | Patrones de coordinación identificados | >20 |
| Semana 3 | Solapamientos CONADE-Castro probados | >5 medios/actores comunes |
| Semana 4 | Expediente final entregado | Completo con anexos |
| Continuo | Falsos positivos en monitoreo | <10% |

---

*Este plan ha sido validado por los 5 Sabios y corregido con las observaciones del cliente. Se solicita aprobación para iniciar la ejecución de la Fase P0.*
