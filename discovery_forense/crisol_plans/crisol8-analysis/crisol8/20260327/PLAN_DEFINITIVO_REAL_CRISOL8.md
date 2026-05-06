# PLAN DEFINITIVO REAL — CRISOL-8

**Arquitecto:** GPT-5.4 | **Fecha:** 2026-03-26 23:06 CST
**Basado en:** 2 rondas de consulta con 6 Sabios (148,012 chars) + 59+ herramientas
**Longitud:** 37,685 caracteres

---

# CRISOL-8 — PLAN DEFINITIVO REAL
## Arquitecto Final: GPT-5.4

---

# 1. ESTRATEGIA MAESTRA

## 1.1 Principio rector
CRISOL-8 no es un sistema de monitoreo de marca, ni un observatorio de 17 dominios, ni una colección de scrapers. Es una **investigación forense persona-céntrica**.

La unidad de verdad no es “el dominio”, “la red”, “la nota” o “la narrativa”.  
La unidad de verdad es:

> **Guillermo Cortés → qué se publicó sobre él → quién lo comentó/compartió/replicó → cómo se coordinó → quién podría operar esa coordinación, si la evidencia converge.**

Todo lo que no responda directamente a esa cadena se considera desvío.

---

## 1.2 Secuencia lógica óptima
La investigación correcta no empieza detectando coordinación. Empieza creando el universo verificable de exposición pública de Guillermo Cortés en 7 años.

### Orden estratégico correcto:
1. **Definir con precisión a Guillermo Cortés digitalmente**
   - desambiguar homónimos
   - aliases, variantes, contexto, cargos, fotos, eventos
2. **Construir el corpus maestro de menciones públicas**
   - notas, posts, videos, reels, tweets, captions, comentarios, shares detectables
3. **Expandir cada pieza a su capa social**
   - comentarios
   - compartidas
   - replicaciones de contenido
   - perfiles involucrados
4. **Resolver identidades y actores**
   - mismo perfil en varias plataformas
   - cuentas recurrentes
   - actores que aparecen alrededor de múltiples eventos
5. **Detectar patrones de coordinación**
   - temporal
   - textual
   - estructural
   - cross-platform
   - media reutilizada
   - patrón operativo
6. **Someter cada cluster a controles**
   - hipótesis alternativas
   - falsos positivos
   - evento real detonante
   - autenticidad de cuentas
7. **Solo al final** formular hipótesis de operador
   - nunca al principio
   - nunca por intuición
   - solo por convergencia de evidencia

---

## 1.3 Puntos de apalancamiento reales
Los mayores multiplicadores del proyecto no son “más scraping”, sino estos seis:

### A. Ficha de Identidad Digital de Guillermo Cortés
Si esto está mal, todo lo demás se contamina con homónimos, ruido y sesgo.

### B. Corpus maestro unificado de 7 años
Sin corpus exhaustivo no hay forensia; solo hay ejemplos sueltos.

### C. Extracción de capa social por pieza
El valor no está solo en la publicación, sino en:
- quién comenta
- quién comparte
- quién replica
- quién aparece siempre

### D. Resolución de actores
La coordinación no la hacen URLs; la hacen perfiles, cuentas, comunidades y operadores.

### E. Detección por convergencia, no por señal única
Una sola coincidencia temporal o textual no prueba nada.  
La fuerza probatoria surge cuando varias señales convergen.

### F. Gates anti-desvío
El proyecto se perderá si se permite:
- abrir líneas paralelas prematuras
- investigar actores sin conexión probada con GC
- convertir intuiciones en conclusiones
- expandir a “todo internet” sin priorización

---

## 1.4 Tesis operativa del plan
La mejor forma de investigar coordinación contra una persona es construir un **grafo forense de propagación narrativa centrado en la persona**, donde cada nodo y relación tenga trazabilidad.

Ese grafo debe permitir responder cuatro preguntas finales:

1. **Qué se publicó sobre Guillermo Cortés y cuándo**
2. **Quién lo amplificó, comentó, replicó o empujó**
3. **Qué patrones de coordinación existen con evidencia**
4. **Qué hipótesis de operador sobreviven a controles y alternativas**

---

## 1.5 Filosofía de ejecución
Este plan privilegia:
- **exhaustividad inicial controlada**
- **normalización fuerte**
- **evidencia reproducible**
- **atribución conservadora**
- **privacidad y OPSEC**
- **resultado nulo como resultado válido**

No se optimiza para velocidad; se optimiza para **resistir escrutinio interno serio**.

---

# 2. PLAN DEFINITIVO

## Resumen de fases
- **Fase 0. Arranque forense y blindaje**
- **Fase 1. Construcción del corpus maestro de Guillermo Cortés**
- **Fase 2. Expansión social y recolección de interacciones**
- **Fase 3. Normalización, enriquecimiento y resolución de actores**
- **Fase 4. Detección de coordinación**
- **Fase 5. Validación forense, hipótesis alternativas y atribución**
- **Fase 6. Productos finales y cierre**

Duración recomendada: **8 semanas**
- Semanas 1-2: Fase 0-1
- Semanas 3-4: Fase 2
- Semanas 5-6: Fase 3-4
- Semanas 7-8: Fase 5-6

---

## FASE 0. ARRANQUE FORENSE Y BLINDAJE

### Objetivo
Preparar entorno, criterios, esquema, cadena de custodia y definición exacta del sujeto.

---

### Subfase 0.1 — Ficha de Identidad Digital de Guillermo Cortés
**Herramientas**
- GPT-5.4
- Claude Opus 4.6
- Perplexity Sonar
- Notion MCP
- Wayback
- búsquedas manuales estructuradas

**Inputs**
- nombre completo
- variantes conocidas
- cargos, empresas, fotos, ciudades, fechas relevantes
- URLs oficiales o semioficiales conocidas

**Outputs**
- `subject_master_profile.md`
- lista de aliases y variantes
- lista de exclusiones de homónimos
- taxonomía inicial de contenido
- línea de tiempo de eventos clave

**Criterio de éxito**
- existe una ficha única con:
  - nombre canónico
  - variantes
  - atributos de desambiguación
  - eventos verificables
  - señales de exclusión

**Gate**
- No se inicia scraping masivo hasta tener aprobada la ficha.

---

### Subfase 0.2 — Preparación de infraestructura y cadena de custodia
**Herramientas**
- GitHub privado
- Supabase
- AWS S3
- Python
- SHA-256 hashing
- Notion MCP

**Inputs**
- credenciales
- buckets
- repo
- service_role key de Supabase

**Outputs**
- estructura de carpetas
- buckets activos:
  - `crisol8-raw-scrapes`
  - `crisol8-analysis`
  - `crisol8-evidence`
- tabla `audit_log`
- rutina de hash por evidencia
- convención de nombres

**Criterio de éxito**
- todo archivo entrante genera:
  - hash SHA-256
  - timestamp UTC
  - origen
  - job_id
  - ruta de almacenamiento

**Gate**
- No se ingesta nada sin hash y metadatos mínimos.

---

### Subfase 0.3 — Esquema SQL definitivo
**Herramientas**
- DeepSeek R1
- GPT-5.4
- Supabase SQL editor

**Inputs**
- requerimientos del plan
- propuestas previas de schema

**Outputs**
- schema desplegado
- índices creados
- constraints
- vistas base

**Criterio de éxito**
- inserción de prueba end-to-end exitosa desde raw hasta evidencia

**Gate**
- No correr ETL masivo sin prueba de inserción y consulta.

---

## FASE 1. CONSTRUCCIÓN DEL CORPUS MAESTRO DE GUILLERMO CORTÉS

### Objetivo
Crear el universo más amplio posible de publicaciones públicas sobre GC en los últimos 7 años.

---

### Subfase 1.1 — Descubrimiento web y noticias
**Herramientas**
- BrandMentions
- Mentionlytics
- Perplexity Sonar
- Apify website-content-scraper
- Wayback
- búsquedas avanzadas Google/Bing manuales
- SecurityTrails/crt.sh/whois solo si aparecen dominios relevantes

**Inputs**
- queries canónicas y variantes
- ventana temporal de 7 años
- idiomas y regiones relevantes

**Outputs**
- lista maestra de URLs
- artículos/notas/posts web
- metadatos:
  - título
  - fecha
  - autor
  - dominio
  - snippet
  - plataforma_origen

**Criterio de éxito**
- cobertura inicial de web abierta y medios suficiente para construir línea de tiempo de menciones

**Gate**
- revisión de muestra de 100 resultados:
  - precisión de relevancia >= 85%
  - homónimos controlados

---

### Subfase 1.2 — Descubrimiento por plataforma social
**Herramientas**
- Apify twitter-scraper
- youtube-scraper
- instagram-scraper
- tiktok-scraper
- facebook-scraper
- Perplexity Sonar
- búsquedas manuales por plataforma

**Inputs**
- queries por plataforma
- aliases
- combinaciones con eventos clave

**Outputs**
- tabla de contenido social candidato
- posts/videos/tweets/reels que mencionan a GC
- URLs canónicas y IDs de plataforma

**Criterio de éxito**
- corpus social inicial por plataforma con cobertura temporal y de eventos

**Gate**
- cada plataforma debe entregar al menos:
  - volumen
  - calidad
  - limitaciones documentadas
- si una plataforma no ofrece historia suficiente, se documenta la brecha.

---

### Subfase 1.3 — Desambiguación y depuración del corpus maestro
**Herramientas**
- GPT-5.4
- Claude Opus
- modelos baratos OpenRouter para clasificación
- reglas determinísticas

**Inputs**
- corpus bruto de menciones
- ficha de identidad digital

**Outputs**
- `mentions_master`
  - relevantes
  - ambiguas
  - excluidas
- razones de exclusión
- score de confianza de relevancia

**Criterio de éxito**
- cada mención clasificada:
  - relevante
  - dudosa
  - irrelevante

**Gate**
- solo pasan a Fase 2 las menciones:
  - relevantes
  - dudosas con score alto y revisión manual

---

## FASE 2. EXPANSIÓN SOCIAL Y RECOLECCIÓN DE INTERACCIONES

### Objetivo
Por cada publicación relevante, extraer su capa social: comentarios, compartidas, replicaciones y perfiles involucrados.

---

### Subfase 2.1 — Extracción de comentarios
**Herramientas**
- website-comments-scraper
- facebook-comments-scraper
- instagram-comment-scraper
- youtube-scraper
- twitter-scraper
- tiktok-scraper
- Python ETL

**Inputs**
- URLs/IDs de contenido relevante

**Outputs**
- comentarios normalizados
- autor, fecha, texto, parent_id, engagement visible

**Criterio de éxito**
- al menos 80% de las piezas prioritarias con comentarios extraídos donde la plataforma lo permita

**Gate**
- si extracción < 60% en una plataforma, documentar limitación y activar plan alterno:
  - captura manual priorizada
  - snapshots
  - Wayback si aplica

---

### Subfase 2.2 — Extracción de compartidas y amplificación
**Herramientas**
- Apify por plataforma
- resolución de URLs
- expand_urls script
- búsquedas por texto y hash de contenido

**Inputs**
- piezas originales
- links acortados
- texto/caption

**Outputs**
- 4 tipos de compartir:
  1. share nativo
  2. link amplification
  3. content replication
  4. narrative amplification

**Criterio de éxito**
- cada pieza relevante queda etiquetada con su tipo de amplificación detectable

**Gate**
- si no hay share nativo visible, se buscan replicaciones y mirrors antes de cerrar la pieza como “sin amplificación”.

---

### Subfase 2.3 — Captura multimedia asociada
**Herramientas**
- easyocr
- Gemini Vision
- Whisper / manus-speech-to-text
- PIL imagehash
- manus-analyze-video
- Replicate ai-image-detector

**Inputs**
- imágenes, memes, videos, reels, shorts, capturas

**Outputs**
- OCR de texto en imagen
- transcripción de audio/video
- pHash de imágenes
- fingerprint de audio cuando aplique
- señal de probable IA en avatar/contenido

**Criterio de éxito**
- toda pieza multimedia relevante se vuelve texto consultable y evidencia indexable

**Gate**
- ninguna pieza multimedia crítica queda sin OCR/transcripción.

---

## FASE 3. NORMALIZACIÓN, ENRIQUECIMIENTO Y RESOLUCIÓN DE ACTORES

### Objetivo
Transformar contenido disperso en entidades forenses comparables.

---

### Subfase 3.1 — Normalización universal
**Herramientas**
- Python ETL
- Supabase
- OpenRouter barato/gratis para limpieza asistida
- expresiones regulares
- UTC normalization

**Inputs**
- raw scrapes
- comentarios
- multimedia procesada

**Outputs**
- contenido normalizado:
  - timestamps UTC
  - texto limpio
  - idioma
  - plataforma
  - canonical_url
  - author_handle
  - content_type

**Criterio de éxito**
- todos los registros comparables entre plataformas

**Gate**
- no se ejecuta detección con timestamps locales inconsistentes o URLs no canonicalizadas.

---

### Subfase 3.2 — Resolución de actores
**Herramientas**
- resolve_actors.py
- NetworkX
- GPT-5.4
- Kimi K2.5
- Grok
- Hunter/HIBP solo si aparece justificación OSINT y legal

**Inputs**
- perfiles, handles, bios, nombres, links, imágenes, patrones de escritura

**Outputs**
- actor graph provisional
- posibles equivalencias cross-platform
- score de confianza por match
- flags de autenticidad/sospecha

**Criterio de éxito**
- lista priorizada de actores recurrentes con identidad resuelta o pseudorresuelta

**Gate**
- un match cross-platform no se considera confirmado sin al menos 2 señales consistentes.

---

### Subfase 3.3 — Enriquecimiento semántico y narrativo
**Herramientas**
- OpenRouter 70/25/5
- embeddings
- GPT-5.4
- Claude Opus
- qwen3-coder/free o similares para clasificación barata

**Inputs**
- texto normalizado
- OCR/transcripciones
- metadata de eventos

**Outputs**
- narrativa principal/secundaria
- tono
- blanco de ataque/defensa
- claims extraíbles
- entidades mencionadas
- embeddings

**Criterio de éxito**
- cada pieza relevante etiquetada narrativamente y vectorizada

**Gate**
- revisión de precisión sobre muestra humana >= 80%.

---

## FASE 4. DETECCIÓN DE COORDINACIÓN

### Objetivo
Identificar clusters de cuentas/piezas con señales convergentes de coordinación.

---

### Subfase 4.1 — Señales base
Se implementan las 6 familias de señales:

1. **Sincronía temporal**
2. **Similitud textual**
3. **Co-amplificación**
4. **Cross-platform mirroring**
5. **Reutilización de media**
6. **Patrón operativo**

**Herramientas**
- detect_coordination.py
- TF-IDF + cosine
- embeddings similarity
- NetworkX
- imagehash pHash
- audio fingerprint
- SQL burst queries

**Inputs**
- contenido normalizado
- actores resueltos
- multimedia enriquecida

**Outputs**
- tabla de señales por par y por cluster
- bursts
- clusters preliminares

**Criterio de éxito**
- clusters detectados con trazabilidad a evidencia fuente

**Gate**
- ningún cluster pasa a “analizable” si no tiene al menos 2 señales distintas.

---

### Subfase 4.2 — Scoring compuesto
**Modelo recomendado 0-100**
- sincronía temporal: 20
- similitud textual: 20
- co-amplificación: 15
- cross-platform mirroring: 15
- reutilización de media: 15
- patrón operativo: 15

**Clasificación**
- 0-24: ruido/no concluyente
- 25-49: coincidencia débil
- 50-69: coordinación posible
- 70-84: coordinación probable
- 85-100: coordinación fuerte

**Convergencia tipo Claude**
- 4/5 o equivalente robusto: confirmada internamente
- 3/5: probable
- 2/5: posible
- 1/5: insuficiente

**Outputs**
- score por par de perfiles
- score por cluster
- score por narrativa
- score por evento

**Gate**
- no se formula hipótesis de operador debajo de “probable”.

---

### Subfase 4.3 — Contextualización por evento real
**Herramientas**
- Perplexity Sonar
- web search citada
- línea de tiempo de eventos

**Inputs**
- picos de actividad
- bursts
- fechas

**Outputs**
- explicación contextual:
  - evento orgánico
  - detonante mediático
  - publicación original
  - hecho externo

**Criterio de éxito**
- cada burst importante tiene contexto causal evaluado

**Gate**
- si un pico se explica razonablemente por evento orgánico, baja su peso como evidencia de coordinación.

---

## FASE 5. VALIDACIÓN FORENSE, HIPÓTESIS ALTERNATIVAS Y ATRIBUCIÓN

### Objetivo
Separar coordinación real de activismo orgánico, moda narrativa, reacción legítima o simple coincidencia.

---

### Subfase 5.1 — Hipótesis alternativas obligatorias
Para cada cluster:
1. reacción orgánica a evento real
2. comunidad ideológica no coordinada
3. replicación por tendencia o meme
4. automatización de plataforma/no operador humano central
5. coincidencia temporal por cobertura noticiosa

**Herramientas**
- Claude Opus
- GPT-5.4
- Perplexity
- revisión manual

**Outputs**
- matriz de descarte de alternativas

**Criterio de éxito**
- cada cluster tiene análisis comparativo y justificación

**Gate**
- sin matriz de alternativas, ningún cluster puede subir de “posible”.

---

### Subfase 5.2 — Autenticidad y comportamiento de cuentas
**Herramientas**
- Kimi K2.5
- GPT-5.4
- reglas de autenticidad
- NetworkX
- análisis de creación/actividad/bio/avatar

**Inputs**
- perfiles recurrentes

**Outputs**
- score de autenticidad
- flags:
  - posible sockpuppet
  - bot-like
  - cuenta reciclada
  - cuenta orgánica

**Criterio de éxito**
- actores principales evaluados individualmente

**Gate**
- no etiquetar “bot” sin evidencia conductual suficiente.

---

### Subfase 5.3 — Hipótesis de operador
**Niveles**
- Nivel 0: sin atribución
- Nivel 1: operador funcional desconocido
- Nivel 2: célula/comunidad probable
- Nivel 3: entidad/operador probable
- Nivel 4: atribución robusta interna

**Herramientas**
- GPT-5.4
- Claude Opus
- OSINT permitido
- revisión legal interna

**Inputs**
- clusters validados
- actores
- evidencias convergentes

**Outputs**
- dossier de hipótesis de operador
- evidencia a favor
- evidencia en contra
- grado de confianza

**Criterio de éxito**
- atribución conservadora y defendible

**Gate**
- Nivel 3 o 4 requiere revisión legal previa.

---

## FASE 6. PRODUCTOS FINALES Y CIERRE

### Objetivo
Convertir hallazgos en entregables internos accionables, trazables y auditables.

---

### Subfase 6.1 — Construcción de productos analíticos
**Herramientas**
- NetworkX + Plotly
- Matplotlib/Seaborn
- manus-render-diagram
- manus-md-to-pdf
- Notion MCP

**Outputs**
- timeline maestro
- grafo sujeto-céntrico
- grafo de amplificación
- grafo de coordinación
- grafo de identidad cross-platform
- ranking de actores recurrentes
- ranking de clusters
- mapa narrativo
- dossier de evidencia

---

### Subfase 6.2 — Cierre, archivo y reproducibilidad
**Herramientas**
- S3
- GitHub privado
- Supabase exports
- SHA-256 manifest

**Outputs**
- paquete reproducible
- manifest de evidencia
- snapshot de base
- bitácora final

**Criterio de éxito**
- otro analista interno puede reconstruir el caso desde cero.

**Gate**
- cierre solo cuando:
  - hashes verificados
  - tablas congeladas
  - reportes versionados
  - limitaciones documentadas

---

# 3. ARQUITECTURA DE DATOS

## 3.1 Decisión
No conviene adoptar intacta ninguna de las tres propuestas.  
La mejor opción es un **schema híbrido persona-céntrico, agnóstico de plataforma y orientado a evidencia**, tomando:
- la riqueza relacional de GPT-5.4
- la disciplina forense de Claude
- la claridad operativa de DeepSeek

## 3.2 Principios del schema
- sujeto central explícito
- timestamps UTC en todo
- raw y normalized separados
- evidencia trazable a archivo fuente
- actores y perfiles separados
- contenido e interacciones separados
- clusters y señales separados
- auditabilidad total

---

## 3.3 Schema SQL definitivo

### 1. `subjects`
Sujeto investigado.
- id
- canonical_name
- aliases_json
- description
- created_at
- updated_at

### 2. `subject_identity_markers`
Desambiguación.
- id
- subject_id
- marker_type (`photo`, `org`, `location`, `role`, `event`, `keyword`, `exclude_keyword`)
- marker_value
- confidence
- source
- created_at

### 3. `platforms`
- id
- name
- platform_type
- base_url

### 4. `sources`
Origen de recolección.
- id
- source_type (`brandmentions`, `mentionlytics`, `apify`, `manual`, `wayback`, `perplexity`)
- source_ref
- config_json
- created_at

### 5. `raw_objects`
Registro bruto de todo lo recolectado.
- id
- source_id
- platform_id
- object_type (`post`, `article`, `comment`, `profile`, `video`, `image`, `share`, `snapshot`)
- raw_payload_json
- raw_text
- raw_url
- fetched_at
- sha256
- s3_path
- job_id

### 6. `content_items`
Contenido normalizado.
- id
- subject_id
- platform_id
- raw_object_id
- content_type (`article`, `post`, `tweet`, `video`, `reel`, `story_ref`, `commentary`, `image_post`)
- canonical_url
- platform_content_id
- title
- body_text
- published_at_utc
- author_profile_id nullable
- language
- relevance_status (`relevant`, `ambiguous`, `excluded`)
- relevance_score
- event_context_id nullable
- created_at

### 7. `profiles`
Perfiles por plataforma.
- id
- platform_id
- handle
- display_name
- profile_url
- bio
- avatar_url
- external_links_json
- created_at
- updated_at

### 8. `actors`
Entidad lógica de actor.
- id
- actor_label
- actor_type (`individual`, `media`, `collective`, `anonymous_cluster`, `unknown`)
- notes
- created_at

### 9. `actor_profile_links`
Vincula actor con perfiles.
- id
- actor_id
- profile_id
- link_confidence
- link_basis_json
- is_primary
- created_at

### 10. `subject_mentions`
Mención específica del sujeto dentro de una pieza.
- id
- subject_id
- content_item_id
- mention_text
- mention_variant
- mention_start
- mention_end
- sentiment
- attack_defend_neutral
- confidence
- created_at

### 11. `interactions`
Interacciones sobre contenido.
- id
- content_item_id
- interaction_type (`comment`, `reply`, `share_native`, `quote`, `retweet_like`, `link_share`, `replication`, `mention`, `duet`, `stitch`)
- source_profile_id
- target_profile_id nullable
- parent_interaction_id nullable
- interaction_text
- interaction_url
- occurred_at_utc
- engagement_json
- raw_object_id
- created_at

### 12. `media_assets`
Archivos multimedia asociados.
- id
- content_item_id
- media_type (`image`, `video`, `audio`, `screenshot`)
- media_url
- s3_path
- sha256
- phash
- audio_fingerprint
- ai_generated_score nullable
- created_at

### 13. `media_extractions`
Resultados OCR/transcripción.
- id
- media_asset_id
- extraction_type (`ocr`, `transcript`, `vision_summary`, `frame_ocr`)
- extracted_text
- language
- model_used
- confidence
- created_at

### 14. `narratives`
Taxonomía narrativa.
- id
- narrative_label
- narrative_description
- created_at

### 15. `content_narratives`
- id
- content_item_id
- narrative_id
- assignment_confidence
- model_used
- rationale_short
- created_at

### 16. `events`
Eventos reales/contextuales.
- id
- event_label
- event_date_start
- event_date_end
- event_description
- source_url
- created_at

### 17. `coordination_signals`
Señales por par o cluster.
- id
- subject_id
- signal_type (`temporal`, `textual`, `co_amplification`, `cross_platform`, `media_reuse`, `operational_pattern`)
- actor_a_id nullable
- actor_b_id nullable
- content_item_a_id nullable
- content_item_b_id nullable
- cluster_temp_id nullable
- signal_score
- signal_payload_json
- detected_at

### 18. `coordination_clusters`
Clusters consolidados.
- id
- subject_id
- cluster_label
- narrative_id nullable
- cluster_score
- coordination_level (`insufficient`, `possible`, `probable`, `strong`)
- first_seen_at
- last_seen_at
- summary
- created_at

### 19. `cluster_members`
- id
- cluster_id
- actor_id nullable
- profile_id nullable
- content_item_id nullable
- role_in_cluster
- membership_confidence
- created_at

### 20. `operator_hypotheses`
- id
- cluster_id
- hypothesis_level (`0`,`1`,`2`,`3`,`4`)
- hypothesis_label
- supporting_evidence_json
- contradicting_evidence_json
- alternative_explanations_json
- confidence
- legal_review_status
- created_at

### 21. `evidence_items`
Cadena de custodia.
- id
- related_table
- related_id
- evidence_type (`url`, `screenshot`, `raw_json`, `html`, `image`, `video`, `csv`, `report`)
- sha256
- s3_path
- captured_at
- captured_by
- provenance_json
- admissibility_notes

### 22. `audit_log`
- id
- action_type
- actor_system
- target_table
- target_id
- action_payload_json
- created_at

### 23. `jobs`
ETL/jobs corridos.
- id
- job_type
- job_status
- started_at
- finished_at
- config_json
- metrics_json
- logs_path

---

## 3.4 Índices clave
- `content_items(subject_id, published_at_utc)`
- `content_items(platform_id, platform_content_id)`
- `profiles(platform_id, handle)`
- `interactions(content_item_id, occurred_at_utc)`
- `coordination_signals(subject_id, signal_type, detected_at)`
- `coordination_clusters(subject_id, cluster_score)`
- `actor_profile_links(actor_id, profile_id)`

---

# 4. PIPELINE DE PROCESAMIENTO

## 4.1 ETL maestro
Pipeline de 6 etapas:

1. **Discovery**
2. **Raw ingest**
3. **Normalize**
4. **Enrichment**
5. **Detection**
6. **Outputs**

---

## 4.2 Scripts definitivos a construir

### Script 1 — `build_subject_profile.py`
Crea ficha de identidad digital.
- inputs: aliases, markers, exclusions
- outputs: `subjects`, `subject_identity_markers`

### Script 2 — `discover_mentions.py`
Integra BrandMentions, Mentionlytics, Perplexity y búsquedas.
- outputs: URLs candidatas, posts candidatos, `raw_objects`

### Script 3 — `collect_social_layers.py`
Expande contenido a comentarios, shares, replicaciones.
- usa Apify por plataforma
- outputs: `raw_objects`, `interactions`, `profiles`

### Script 4 — `normalize_content.py`
Limpia, canonicaliza, UTC, deduplica.
- outputs: `content_items`, `subject_mentions`

### Script 5 — `enrich_media_and_text.py`
OCR, Whisper, pHash, embeddings, narrativa.
- outputs: `media_assets`, `media_extractions`, `content_narratives`

### Script 6 — `resolve_actors.py`
Une perfiles en actores.
- outputs: `actors`, `actor_profile_links`

### Script 7 — `detect_coordination.py`
Calcula señales y clusters.
- outputs: `coordination_signals`, `coordination_clusters`, `cluster_members`

### Script 8 — `validate_clusters.py`
Aplica hipótesis alternativas y scoring final.
- outputs: `operator_hypotheses`

### Script 9 — `generate_outputs.py`
Produce timelines, grafos, reportes PDF/CSV.
- outputs: reportes y evidencia

---

## 4.3 Flujo ETL detallado

### Etapa A — Discovery
**Fuentes prioritarias**
1. BrandMentions
2. Apify búsquedas por plataforma
3. Perplexity Sonar
4. Mentionlytics
5. Wayback/manual

**Regla**
Todo hallazgo entra primero como `raw_object`.

---

### Etapa B — Raw ingest
- guardar payload original
- guardar HTML/JSON/screenshot si aplica
- calcular SHA-256
- subir a S3 raw
- registrar job_id y source_id

---

### Etapa C — Normalize
- deduplicación por canonical_url + platform_content_id + similitud
- timezone a UTC
- limpieza de texto
- detección de idioma
- clasificación de relevancia respecto a GC
- extracción de mención específica

---

### Etapa D — Enrichment
#### Texto
- embeddings
- narrativa
- tono
- entidades

#### Imagen
- OCR
- pHash
- detección IA si tiene sentido

#### Video/audio
- transcript
- OCR por frames
- audio fingerprint

---

### Etapa E — Actor resolution
- mismo handle en distintas plataformas
- mismo nombre + bio + links
- misma foto/avatar aproximada
- mismo patrón de enlaces externos
- misma narrativa + timing + comunidad

---

### Etapa F — Detection
Aplicar señales:

#### 1. Sincronía temporal
- ventanas:
  - 5 min
  - 30 min
  - 2 h
  - 24 h
- detectar bursts por narrativa y actor

#### 2. Similitud textual
- exact match
- near-duplicate
- template reuse
- embeddings cosine

#### 3. Co-amplificación
- mismos actores amplificando mismas piezas repetidamente
- secuencias recurrentes

#### 4. Cross-platform mirroring
- mismo mensaje en X, FB, IG, TikTok, YouTube
- misma secuencia narrativa en distintas plataformas

#### 5. Reutilización de media
- misma imagen/meme/video/audio
- variantes leves detectadas por pHash/fingerprint

#### 6. Patrón operativo
- horarios consistentes
- roles repetidos:
  - originador
  - amplificador
  - comentarista
  - replicador
- cuentas que aparecen solo en eventos sobre GC

---

## 4.4 Integración OpenRouter — regla 70/25/5

### 70% gratis
Usos:
- limpieza textual barata
- clasificación preliminar
- etiquetado simple
- resúmenes de lotes
- dedupe asistido

Modelos:
- qwen3-coder:free
- qwen3-next-80b:free
- gpt-oss-120b:free
- nemotron-3-super-120b:free
- step-3.5-flash:free

### 25% baratos
Usos:
- clasificación narrativa
- resolución de actores ambigua
- análisis de clusters medianos
- extracción estructurada

Modelos:
- qwen3.5-flash
- gemini-2.5-flash-lite
- grok-4.1-fast

### 5% premium
Usos:
- revisión crítica
- síntesis final
- atribución conservadora
- comparación de hipótesis
- redacción de productos finales

Modelos:
- GPT-5.4
- Claude Opus 4.6
- Gemini 3.1 Pro

### Regla de privacidad
- En modelos gratis: **pseudonimizar**
  - GC = `SUBJ-001`
  - actores = `ACT-###`
  - URLs sensibles truncadas o hasheadas
  - texto con minimización cuando sea posible

---

## 4.5 Detección: scoring y convergencia

### Señales y pesos
- temporal: 20
- textual: 20
- co-amplificación: 15
- cross-platform: 15
- media reuse: 15
- patrón operativo: 15

### Ajustes negativos
- evento orgánico fuerte: -15
- volumen pequeño: -10
- datos incompletos: -10
- una sola plataforma: -5
- alta ambigüedad de actor: -10

### Regla de convergencia
- **Confirmada internamente**: score >= 85 y al menos 4 señales
- **Probable**: score 70-84 y al menos 3 señales
- **Posible**: score 50-69 y al menos 2 señales
- **Insuficiente**: resto

---

# 5. MECANISMO ANTI-DESVÍO

## 5.1 Regla madre
Toda tarea debe responder por escrito:

> “¿Cómo acerca esto a entender qué se publicó sobre Guillermo Cortés, quién lo amplificó y si hubo coordinación?”

Si no responde claramente, no se ejecuta.

---

## 5.2 Gates obligatorios

### Gate A — Identidad
No se recolecta masivamente sin Ficha de Identidad Digital aprobada.

### Gate B — Relevancia
No se analiza coordinación sobre piezas no clasificadas como relevantes o ambiguas altas.

### Gate C — Capa social
No se atribuye coordinación sobre una pieza si no se intentó extraer su capa social.

### Gate D — Convergencia
No se eleva cluster sin mínimo 2 señales.

### Gate E — Alternativas
No se llama coordinación probable/fuerte sin hipótesis alternativas evaluadas.

### Gate F — Atribución
No se formula hipótesis de operador por debajo de “probable”.

### Gate G — Legal
No sale ningún entregable externo sin abogado.

---

## 5.3 Checkpoints semanales
Cada semana se responde:

1. ¿Cuánto del corpus de GC ya está cubierto?
2. ¿Qué porcentaje es ruido/homónimo?
3. ¿Qué plataformas están subrepresentadas?
4. ¿Cuáles son los actores recurrentes reales?
5. ¿Qué clusters tienen evidencia convergente?
6. ¿Qué hallazgos dependen de datos incompletos?
7. ¿Estamos investigando algo que ya no está anclado a GC?

---

## 5.4 Criterios de “parar si…”
- el 70%+ del corpus resulta homónimo o ruido y la ficha debe rehacerse
- una plataforma crítica no permite extracción y no hay plan alterno viable
- un cluster importante depende de evidencia no verificable
- la atribución se sostiene solo por intuición
- aparece riesgo legal no resuelto
- el equipo empieza a investigar actores sin conexión documentada a GC

---

## 5.5 Lista explícita de desvíos prohibidos
- abrir “17 dominios” como frentes autónomos
- perfilar actores por curiosidad sin conexión a una mención o cluster de GC
- investigar ideologías generales en vez de interacción concreta
- convertir narrativas generales en prueba de coordinación
- usar una sola plataforma como universo total
- usar una sola señal como prueba concluyente

---

# 6. CONTROLES Y OPSEC

## 6.1 Controles contra falsos positivos
Obligatorios por cluster:

1. **Sesgo de confirmación**
   - buscar evidencia en contra
2. **n pequeño**
   - no inferir redes por 2-3 cuentas aisladas
3. **correlación temporal espuria**
   - verificar evento detonante real
4. **bots que no son bots**
   - distinguir automatización parcial de coordinación central
5. **activismo/comunidad vs operación**
   - una comunidad alineada no equivale a operador coordinador

---

## 6.2 Hipótesis alternativas obligatorias
Ya definidas en Fase 5.1; deben documentarse siempre.

---

## 6.3 Protocolo de evidencia
Por cada evidencia:
- captura del objeto original si es posible
- URL
- timestamp UTC de captura
- fuente
- hash SHA-256
- ubicación S3
- relación con tabla/registro
- notas de contexto
- versión si hubo actualización

### Evidencia mínima por cluster
- 3 piezas fuente
- 2 o más interacciones
- 1 visualización de red o timeline
- 1 tabla de señales
- 1 matriz de alternativas

---

## 6.4 OPSEC operativo
1. Todo en repositorio privado
2. Buckets privados con acceso restringido
3. No usar cuentas personales en scraping
4. No interactuar con sujetos
5. No crear cuentas falsas
6. Pseudonimizar al usar modelos gratis
7. Logs de acceso y jobs
8. Segmentación de credenciales
9. No compartir capturas por canales inseguros
10. Congelar evidencia crítica en S3 + hash manifest

---

## 6.5 Legal y ética
- solo observación pasiva de información pública
- no doxxing
- no intrusión
- no evasión de controles de acceso
- no publicar
- resultado nulo válido
- revisión legal antes de cualquier salida externa
- minimización de datos personales no relevantes

---

# 7. CRONOGRAMA Y COSTOS

## 7.1 Cronograma de 8 semanas

### Semana 1
- Fase 0 completa
- Ficha de identidad digital
- infraestructura
- schema
- queries maestras
- prueba ETL

### Semana 2
- discovery web y social
- corpus maestro inicial
- depuración y desambiguación

### Semana 3
- extracción de comentarios
- extracción de shares/replicaciones
- captura multimedia

### Semana 4
- completar capa social
- OCR/transcripción
- normalización total

### Semana 5
- resolución de actores
- embeddings y narrativas
- primeros grafos descriptivos

### Semana 6
- detección de coordinación
- clusters preliminares
- contextualización por eventos

### Semana 7
- hipótesis alternativas
- autenticidad de cuentas
- hipótesis de operador

### Semana 8
- reportes finales
- dossiers
- evidencia
- cierre reproducible

---

## 7.2 Costos estimados

### Infra ya disponible
- Supabase: ya disponible
- S3: costo variable bajo/moderado
- GitHub: ya disponible
- Apify Starter: **$39/mes**
- BrandMentions: ya disponible
- Mentionlytics: ya disponible si token se corrige

### Estimación operativa 8 semanas
- Apify: $39-$78
- S3 almacenamiento/egress: $10-$40
- OpenRouter barato: $20-$80
- Premium puntual: $30-$120
- herramientas auxiliares/Replicate: $10-$30

### Total estimado realista
**$109-$348 USD**  
Si se intensifica multimodal/video: **hasta $450 USD**

Esto coincide con la estimación de Claude, pero con margen más realista para multimedia.

---

# 8. PRODUCTOS FINALES

## 8.1 Entregables principales

### 1. Corpus Maestro de Guillermo Cortés
- todas las menciones relevantes de 7 años
- por plataforma
- con metadata y relevancia

### 2. Timeline Maestro
- publicaciones sobre GC
- picos
- eventos detonantes
- fases narrativas

### 3. Grafo Sujeto-Céntrico
- GC al centro
- contenido, perfiles, actores, narrativas alrededor

### 4. Grafo de Amplificación
- quién amplifica a quién
- secuencias recurrentes
- hubs

### 5. Grafo de Coordinación
- clusters
- fuerza de relación
- señales por arista

### 6. Grafo de Identidad Cross-Platform
- perfiles vinculados a un mismo actor

### 7. Ranking de Actores Recurrentes
- frecuencia
- plataformas
- narrativas
- score de recurrencia

### 8. Ranking de Clusters de Coordinación
- score
- nivel
- narrativa
- periodo
- evidencia

### 9. Dossiers de Cluster
Cada dossier incluye:
- resumen ejecutivo
- piezas fuente
- actores
- señales
- timeline
- alternativas
- evaluación final

### 10. Dossier de Hipótesis de Operador
Solo si la evidencia lo permite.

### 11. Paquete de Evidencia
- manifest SHA-256
- rutas S3
- snapshots
- CSVs
- JSONs
- PDFs

---

## 8.2 Formatos
- PDF ejecutivo interno
- CSV exportable
- JSON estructurado
- dashboards Plotly locales/internos
- Markdown versionado en GitHub privado
- Notion bitácora operativa

---

## 8.3 Distribución
- solo interna
- Gmail/Outlook solo para distribución controlada
- nunca pública
- si hay resumen audiovisual, HeyGen/ElevenLabs solo para uso interno

---

# 9. PRIMEROS 3 PASOS EJECUTABLES — MAÑANA

## PASO 1 — Crear la Ficha de Identidad Digital de Guillermo Cortés
**Duración:** 4-6 horas  
**Responsable lógico:** GPT-5.4 + Claude + Perplexity  
**Acciones**
1. abrir documento `subject_master_profile.md`
2. registrar:
   - nombre canónico
   - aliases
   - cargos/empresas/roles
   - ciudades/fechas
   - fotos conocidas
   - keywords asociadas
   - exclude_keywords para homónimos
3. construir línea de tiempo inicial de eventos clave
4. aprobar versión 1.0

**Resultado tangible mañana**
- un documento maestro aprobado que define quién es GC y quién no es GC

---

## PASO 2 — Desplegar schema y cadena de custodia
**Duración:** 3-5 horas  
**Responsable lógico:** DeepSeek R1 + ejecución técnica local  
**Acciones**
1. obtener `service_role key` de Supabase
2. crear las 23 tablas
3. crear `audit_log`, `jobs`, `evidence_items`
4. configurar buckets S3 y convención de nombres
5. escribir función `sha256_file()` y rutina de ingest mínima
6. ejecutar inserción de prueba con 1 URL, 1 screenshot, 1 raw json

**Resultado tangible mañana**
- base lista para recibir datos reales con trazabilidad

---

## PASO 3 — Correr discovery inicial de 7 años
**Duración:** 1 día  
**Responsable lógico:** Python + BrandMentions + Perplexity + Apify  
**Acciones**
1. lanzar queries maestras en BrandMentions
2. corregir endpoint/token de BrandMentions y Mentionlytics si falla
3. correr búsquedas por plataforma con Apify:
   - X/Twitter
   - YouTube
   - Instagram
   - Facebook
   - TikTok
4. guardar todo como `raw_objects`
5. producir primer CSV:
   - `gc_corpus_seed_v1.csv`
   - columnas: fecha, plataforma, url, título/snippet, relevancia preliminar

**Resultado tangible mañana**
- primer corpus semilla real, no teórico

---

## CIERRE ARQUITECTÓNICO

La decisión más importante de este plan es esta:

> **CRISOL-8 no va a perseguir “dominios” ni “temas” ni “enemigos” en abstracto. Va a reconstruir, con disciplina forense, el ecosistema completo de publicación, reacción y amplificación alrededor de Guillermo Cortés durante 7 años.**

Si ese corpus está bien construido, la coordinación emerge.  
Si el corpus está mal planteado, todo el proyecto se vuelve ruido.

Este plan está diseñado para correr, no para admirarse.  
El orden correcto es:

**definir sujeto → recolectar universo → expandir capa social → resolver actores → detectar coordinación → validar alternativas → atribuir conservadoramente → entregar evidencia.**

Si quieres, en el siguiente mensaje puedo convertir este plan en un **documento operativo de implementación**, con:
- SQL DDL de las 23 tablas,
- estructura exacta del repo,
- nombres de scripts,
- variables de entorno,
- y checklist diario de ejecución para las 8 semanas.