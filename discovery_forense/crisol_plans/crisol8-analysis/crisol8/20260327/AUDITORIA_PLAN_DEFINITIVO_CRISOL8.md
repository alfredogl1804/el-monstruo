# AUDITORÍA CRUZADA: PLAN DEFINITIVO GPT-5.4 vs PROPUESTAS DE LOS 6 SABIOS

**Auditor:** Manus (Ejecutor del proyecto)
**Fecha:** 2026-03-27 00:15 CST
**Propósito:** Detectar omisiones, descartados y propuestas valiosas que GPT-5.4 no integró en el Plan Definitivo Real v3.0

---

## METODOLOGÍA DE AUDITORÍA

Leí las 4,380 líneas (148,012 chars) de los 6 Sabios y las 1,690 líneas (37,685 chars) del Plan Definitivo. Comparé propuesta por propuesta. Clasifiqué cada hallazgo como:

- **INTEGRADO**: GPT-5.4 lo adoptó correctamente
- **PARCIALMENTE INTEGRADO**: Lo mencionó pero sin la profundidad o especificidad del Sabio original
- **OMITIDO**: No aparece en el Plan Definitivo y debería estar
- **DESCARTADO JUSTIFICADAMENTE**: No aparece pero la omisión tiene sentido
- **OMISIÓN CRÍTICA**: Falta algo que yo como ejecutor necesito y que ningún Sabio ni GPT-5.4 abordó

---

## 1. GROK 4.20 (LATERAL) — 8,542 chars

### INTEGRADO
| Propuesta | Dónde aparece en Plan Definitivo |
|-----------|----------------------------------|
| Nodo raíz = Guillermo Cortés, no dominios | Sección 1.1 - Principio rector |
| BrandMentions como fuente de verdad inicial | Fase 1.1 - Discovery web |
| Tabla `guillermo_mentions` con embedding | Tabla 6 `content_items` (sin embedding) |
| Tabla `narrative_interactions` | Tabla 11 `interactions` |
| Tabla `coordination_clusters` | Tabla 18 `coordination_clusters` |

### PARCIALMENTE INTEGRADO
| Propuesta de Grok | Lo que falta en el Plan |
|-------------------|------------------------|
| **"Menciones sin nombre propio" (el silencio nombrado)**: buscar referencias indirectas ("el periodista que destapó lo de los contratos") | GPT-5.4 menciona "variantes" y "OCR" pero NO incluye búsqueda de referencias indirectas sin nombre. Esto es una técnica de recall que podría capturar 15-30% más de menciones relevantes |
| **Cadenas de custodia narrativa**: no solo quién comparte, sino quién comparte el share del share (2da y 3ra generación) | GPT-5.4 tiene 4 tipos de amplificación pero NO modela generaciones de cascada explícitamente |

### OMITIDO — DEBERÍA ESTAR
| Propuesta de Grok | Impacto de la omisión |
|-------------------|----------------------|
| **Anti-menciones**: cuentas que DEJAN de seguir o interactuar en momentos específicos. La coordinación también se ve en la abstención sincronizada | **ALTO** — Nadie más propuso esto. Es una señal débil pero de altísimo valor forense. Detectar quién se calla cuando debería hablar es tan revelador como detectar quién habla |
| **Cuentas "viuda negra"**: perfiles que solo aparecen para atacar/defender y luego se duermen meses | **ALTO** — GPT-5.4 menciona "patrón operativo" genéricamente pero no define este patrón específico que es extremadamente revelador |
| **"Linguistic DNA + Embedding Entropy"**: clusterizar embeddings de comentarios con HDBSCAN y medir "author entropy" por cluster. Baja entropía de autores en cluster semántico coherente = operador | **ALTO** — GPT-5.4 menciona embeddings y cosine similarity pero NO propone HDBSCAN ni el concepto de "author entropy" que es matemáticamente más riguroso |
| **"Temporal Ghost Protocol"**: serie temporal por usuario SOLO en contenido de GC, buscar usuarios con actividad global baja pero picos idénticos en ventana de 15 min cross-platform | **ALTO** — Más sofisticado que el burst detection genérico de GPT-5.4 porque filtra por actividad basal del usuario |
| **"Narrative Vaccination Signature"**: detectar cuando alguien publica PREVENTIVAMENTE contenido que desactiva narrativas futuras sobre GC (días antes de que salga una nota) | **MEDIO** — Señal muy específica pero de altísimo valor si se detecta. Sugiere conocimiento previo |
| **"Cross-platform Avatar DNA"**: no solo pHash de avatar, sino análisis de filtro, ratio, tipografía en bio. Cuentas con avatars generados con mismos prompts = oro | **MEDIO** — GPT-5.4 tiene avatar_hash pero no el análisis de estilo visual |
| **"Model Collapse Detection inverso"**: entrenar modelo en estilo de escritura de comentarios tóxicos/alabadores, medir perplexity de nuevos comentarios. Baja perplexity = mismo operador | **MEDIO** — Técnica avanzada de estilometría que complementa TF-IDF/cosine |
| **Señal de consistencia ortográfica**: cuentas que usan consistentemente la misma forma de escribir "Guillermo" (con/sin tilde, "Guille", "G.C.") en un mismo cluster. Los humanos son inconsistentes, los operadores no | **ALTO** — Señal simple, barata de implementar, y nadie más la propuso |
| **Quote Chain Reconstruction en Twitter**: reconstruir árboles completos de quote tweets usando `quoted_tweet_id` | **MEDIO** — GPT-5.4 menciona quote tweets pero no la reconstrucción de árboles |

---

## 2. GEMINI 3.1 PRO (MULTIMODAL) — 9,219 chars

### INTEGRADO
| Propuesta | Dónde aparece |
|-----------|---------------|
| OCR masivo con easyocr | Subfase 2.3 |
| Whisper para transcripción de video/audio | Subfase 2.3 |
| pHash para detección de imágenes reutilizadas | Tabla 12 `media_assets`, Señal 5 |
| Detección de avatares GAN/IA | Subfase 5.2 |
| Gemini Vision para análisis semántico de imágenes | Subfase 2.3 |

### PARCIALMENTE INTEGRADO
| Propuesta de Gemini | Lo que falta |
|--------------------|-------------|
| **Pipeline de 3 pasos (Triage → OCR rápido → Análisis profundo)**: solo enviar a Gemini Vision lo que pasa el triage | GPT-5.4 menciona OCR y Gemini pero NO define el embudo de 3 pasos que ahorra 70-80% de costos de API |
| **Tabla `gc_multimodal_assets`** con campos `is_screenshot`, `gemini_narrative`, `visual_sentiment` | GPT-5.4 tiene `media_assets` y `media_extractions` pero NO tiene `is_screenshot` ni `visual_sentiment` como campos explícitos |

### OMITIDO — DEBERÍA ESTAR
| Propuesta de Gemini | Impacto |
|--------------------|---------|
| **Detección "Zero-Text"**: campañas que usan la cara de GC en memes SIN escribir su nombre en el post. BrandMentions y scrapers de texto NO los ven | **CRÍTICO** — Gemini estima que el 70% de las campañas de difamación modernas no mencionan textualmente a la víctima. Sin pipeline visual, perdemos la mayoría del contenido visual hostil |
| **Capturas de pantalla como vectores de infección**: operadores suben capturas de notas falsas o tuits para evitar backlinks rastreables. El OCR de la captura debe correlacionarse con la nota original | **ALTO** — GPT-5.4 no tiene flujo explícito de "captura → OCR → correlación con nota original → identificar paciente cero vs vectores" |
| **Template Matching de memes**: usar embeddings visuales para detectar si el FONDO de un meme es el mismo en múltiples cuentas aunque el texto superpuesto cambie | **ALTO** — pHash detecta imágenes similares pero NO detecta templates con texto diferente |
| **Huellas dactilares acústicas**: videos de TikTok/Reels donde se habla de GC con títulos genéricos ("Miren lo que pasó en la ciudad"). Solo Whisper los detecta | **MEDIO** — GPT-5.4 menciona Whisper pero no enfatiza que muchos videos relevantes tienen títulos genéricos y solo el audio revela la mención |
| **Detección de evolución técnica de atacantes**: desde cuentas sin foto (2017) → avatares robados (2019) → StyleGAN (2021) → deepfakes/Midjourney (2023-2024). Análisis temporal de sofisticación | **MEDIO** — Perspectiva temporal de la evolución de tácticas que nadie más propuso |
| **Grafo interactivo Plotly de distribución visual**: nodos de perfiles unidos por la misma imagen/meme compartido al mismo tiempo | **MEDIO** — GPT-5.4 menciona grafos Plotly genéricamente pero no este grafo específico de distribución visual |

---

## 3. CLAUDE OPUS 4.6 (CRÍTICO) — 48,234 chars

### INTEGRADO
| Propuesta | Dónde aparece |
|-----------|---------------|
| Autocrítica de Ronda 1 | Sección 1 del Plan |
| Metodología Persona-Céntrica Forense (PCF) | Todo el Plan |
| Ficha de Identidad Digital antes de cualquier búsqueda | Subfase 0.1 |
| Filtros de desambiguación de homónimos | Subfase 1.3 |
| Taxonomía de contenido relevante | Subfase 0.1 |
| 5 pruebas de coordinación con código Python | Fase 4 |
| Hipótesis alternativas obligatorias | Fase 5.1 |
| Resultado nulo como resultado válido | Sección 1.5 |
| Schema SQL agnóstico de plataforma | Sección 3 |
| Tabla `narrativas` | Tabla 14 `narratives` |
| Tabla `evidencia_forense` | Tabla 21 `evidence_items` |
| Tabla `clusters_coordinacion` con `hipotesis_alternativas` | Tabla 18 + Tabla 20 |

### PARCIALMENTE INTEGRADO
| Propuesta de Claude | Lo que falta |
|--------------------|-------------|
| **Código Python ejecutable completo** para detección de ráfaga anómala, similitud textual, co-ocurrencia cross-platform | GPT-5.4 describe los scripts pero NO incluye código ejecutable. Claude entregó funciones Python completas con scipy, sklearn, numpy |
| **Definición operativa de "coordinación" vs "no coordinación"** con ejemplos concretos | GPT-5.4 define scoring pero NO tiene la sección explícita de "esto SÍ es coordinación / esto NO es coordinación" que Claude escribió |
| **Tabla `mencion_narrativa` (M:N)** para vincular menciones con múltiples narrativas | GPT-5.4 tiene `content_narratives` pero es 1:N, no M:N. Una mención puede pertenecer a múltiples narrativas simultáneamente |

### OMITIDO — DEBERÍA ESTAR
| Propuesta de Claude | Impacto |
|--------------------|---------|
| **Control Crítico 0.1**: La ficha DEBE ser completada y validada por el dueño ANTES de ejecutar cualquier búsqueda. Un error aquí contamina todo | **CRÍTICO** — GPT-5.4 tiene el Gate A pero NO enfatiza que el DUEÑO debe validar la ficha, no solo el sistema |
| **Control Crítico 0.2**: El dueño debe proporcionar una LÍNEA DE TIEMPO de eventos clave de GC en los últimos 7 años. Sin esto, no podemos distinguir picos orgánicos de coordinados | **CRÍTICO** — GPT-5.4 tiene tabla `events` pero NO exige que el dueño proporcione la línea de tiempo ANTES de empezar. Es un input humano indispensable |
| **Riesgo R1 — Homónimos**: "Guillermo Cortés" es nombre común. Sin filtros de contexto se recoge ruido masivo. Claude propone `FILTROS_DESAMBIGUACION` con `contexto_obligatorio`, `exclusion_explicita` y `confianza_minima` | **ALTO** — GPT-5.4 menciona desambiguación pero no tiene el dict de filtros concreto |
| **Riesgo R2 — Volumen inmanejable**: 7 años × todas las plataformas puede generar millones de registros. Claude propone priorización agresiva: primero web+Twitter, luego FB, luego IG/YT/TikTok | **ALTO** — GPT-5.4 no define orden de prioridad por plataforma. Intentar todas simultáneamente puede agotar presupuesto de Apify en semana 1 |
| **Riesgo R3 — Limitaciones técnicas por plataforma**: Facebook limita scraping público, Instagram requiere login para comentarios, TikTok cambia API frecuentemente | **ALTO** — GPT-5.4 no documenta limitaciones conocidas por plataforma |
| **Riesgo R4 — Filtración de la investigación**: si se filtra, los actores borran evidencia. Claude propone usar alias interno "TARGET_ALPHA" en código y no nombrar a GC en nombres de archivos | **MEDIO** — GPT-5.4 tiene pseudonimización para modelos gratis pero NO para nombres de archivos/scripts |
| **Riesgo R5 — Que no haya coordinación**: el proyecto DEBE estar preparado para resultado nulo | **INTEGRADO** — GPT-5.4 sí lo incluye |
| **Control Crítico 3.2a**: Un pico temporal SOLO no es suficiente. Si GC aparece en noticias de las 8pm, habrá pico orgánico a las 8:05pm. El pico debe evaluarse contra el CONTEXTO del evento | **ALTO** — GPT-5.4 tiene contextualización en Subfase 4.3 pero no con esta claridad de ejemplo |
| **Control Crítico 3.2b**: Textos cortos ("qué asco", "bravo") tienen alta similitud natural. Solo contar pares donde AMBOS textos tienen > 50 caracteres | **ALTO** — Filtro práctico que evita miles de falsos positivos. GPT-5.4 no lo tiene |
| **Métrica de éxito explícita**: "¿podemos demostrar, con evidencia que resiste escrutinio, que existe (o no existe) coordinación narrativa alrededor de GC?" | **MEDIO** — GPT-5.4 tiene criterios de éxito por subfase pero no una métrica de éxito global del proyecto |

---

## 4. DEEPSEEK R1 (INGENIERO) — 43,206 chars

### INTEGRADO
| Propuesta | Dónde aparece |
|-----------|---------------|
| Arquitectura de 4 capas simplificada | Pipeline Sección 4 |
| Schema SQL persona-céntrico | Sección 3 (schema híbrido) |
| Tabla `persons` central | Tabla 1 `subjects` |
| Tabla `platforms` | Tabla 3 `platforms` |
| Tabla `profiles` | Tabla 7 `profiles` |
| Tabla `content` | Tabla 6 `content_items` |
| Tabla `comments` | Tabla 11 `interactions` |
| Tabla `shares` | Tabla 11 `interactions` (tipo share) |
| Tabla `coordination_patterns` | Tabla 17 `coordination_signals` |
| Tabla `cross_platform_matches` | Tabla 9 `actor_profile_links` |

### PARCIALMENTE INTEGRADO
| Propuesta de DeepSeek | Lo que falta |
|----------------------|-------------|
| **Script ETL completo `PersonCentricETL`** con clase Python, async, logging, manejo de errores, simulación de datos | GPT-5.4 describe 9 scripts pero NO entrega código ejecutable. DeepSeek entregó una clase completa de ~300 líneas |
| **Script `CoordinationDetector`** con detección temporal, textual, redes y cross-platform | GPT-5.4 describe `detect_coordination.py` pero sin código. DeepSeek entregó la clase completa con NetworkX, sklearn, Plotly |
| **Config ETL como dict Python** con todas las plataformas, herramientas y parámetros | GPT-5.4 no tiene un archivo de configuración centralizado |

### OMITIDO — DEBERÍA ESTAR
| Propuesta de DeepSeek | Impacto |
|----------------------|---------|
| **Datos de simulación para pruebas**: funciones `_simulate_brandmentions_data()` y `_simulate_comments_data()` para probar el pipeline sin datos reales | **ALTO** — Sin datos de prueba, no podemos validar el pipeline antes de gastar dinero en Apify. GPT-5.4 no menciona testing |
| **Queries SQL con CTEs completas**: `comment_activity`, `temporal_clusters`, `profile_pairs`, `multi_platform_users` — queries ejecutables, no pseudocódigo | **ALTO** — GPT-5.4 tiene queries conceptuales pero no CTEs ejecutables |
| **Manejo de errores async con try/except/finally y cleanup** | **MEDIO** — Código de producción necesita esto. GPT-5.4 no lo aborda |
| **Tabla `coordination_patterns` con `content_ids TEXT[]` y `profile_ids TEXT[]`** como arrays | **MEDIO** — GPT-5.4 usa relaciones normalizadas (cluster_members) que es más correcto pero más lento para queries de detección |

---

## 5. GPT-5.4 (ORQUESTADOR) — Ronda 2 vs Plan Definitivo

GPT-5.4 escribió 36,922 chars en Ronda 2 y luego 37,685 chars como Arquitecto Final. Comparo si se descartó algo de su propia Ronda 2:

### OMITIDO DE SU PROPIA RONDA 2
| Propuesta de GPT-5.4 Ronda 2 | Presente en Plan Definitivo |
|-------------------------------|----------------------------|
| **Diccionario de búsqueda maestro** con tabla `subject_search_terms` y categorías (exactos, variantes, co-ocurrencias, hashtags, OCR/typo candidates, exclusiones) | **PARCIAL** — Subfase 0.1 menciona aliases pero no la tabla `subject_search_terms` ni las categorías detalladas |
| **Queries web por rango temporal anual**: `"Guillermo Cortés" after:2019-01-01 before:2020-01-01` repetido por cada año | **OMITIDO** — Estrategia práctica de segmentación temporal que evita duplicados y mejora cobertura |
| **Config JSON de Apify website-content-scraper** con parámetros exactos | **OMITIDO** — GPT-5.4 menciona Apify pero no incluye configs ejecutables |
| **Nota sobre Facebook shares**: no siempre exhaustivos por limitaciones de visibilidad pública. Modelar "amplificación inferida" | **PARCIAL** — Tipo D de amplificación existe pero no la nota sobre limitaciones de FB |
| **Recolección por año (7 ventanas anuales + incremental)** en vez de una sola corrida | **OMITIDO** — Estrategia operativa importante que GPT-5.4 Ronda 2 propuso pero el Plan Definitivo no incluye explícitamente |
| **TikTok audio reutilizado**: si varios perfiles usan mismo audio + mismo framing + misma ventana temporal = coordinación | **PARCIAL** — Mencionado en señal 5 pero sin la especificidad de TikTok audio_id |

---

## 6. PERPLEXITY SONAR — 1,889 chars

Declinó participar por segunda vez. Su ausencia deja un hueco en:
- Verificación de fuentes abiertas
- Contexto noticioso para cada pico de menciones
- Validación de eventos detonantes reales

**Impacto**: GPT-5.4 asigna a Perplexity Sonar roles en Subfases 0.1, 1.1, 4.3 y 5.1. Si Perplexity sigue declinando, necesitamos un plan B (Grok o búsquedas web manuales).

---

## 7. OMISIONES CRÍTICAS QUE NINGÚN SABIO NI GPT-5.4 ABORDARON

Estas son cosas que yo como ejecutor necesito y que nadie propuso:

### 7.1 — Migración del schema existente
**Problema**: Ya existen 9 tablas en el schema `crisol8` de Supabase (`articles`, `bot_analysis`, `comments`, `entity_connections`, `persons`, `portal_clusters`, `portals`, `social_media_posts`, `timeline_events`) + 8 tablas Golden Record en `public`. El Plan Definitivo propone 23 tablas nuevas como si fuera greenfield.

**Lo que falta**: Estrategia de migración/coexistencia:
- ¿Se borran las 9 tablas existentes?
- ¿Se renombran?
- ¿Se migran datos?
- ¿Se crea un schema nuevo `crisol8_v2`?
- ¿Cómo coexisten con Golden Record?

### 7.2 — Acceso a Supabase
**Problema**: La cuenta de GitHub `alfredogl1804` NO ve los proyectos de Supabase (que están bajo `alfredogl1.gongora@gmail.com`). El Plan dice "obtener service_role key" como si fuera trivial.

**Lo que falta**: Procedimiento de acceso a Supabase con la cuenta correcta.

### 7.3 — Presupuesto de Apify por plataforma
**Problema**: Apify Starter es $39/mes. El Plan propone scraping simultáneo de 6 plataformas × 7 años. Sin priorización, se agota el presupuesto en día 1.

**Lo que falta**: Orden de prioridad de plataformas con estimación de créditos Apify por cada una. Claude lo mencionó como Riesgo R2 pero GPT-5.4 no lo integró.

### 7.4 — Token de Mentionlytics
**Problema**: En sesiones anteriores, el token de Mentionlytics devolvió error. No está validado.

**Lo que falta**: Validación del token de Mentionlytics antes de contar con él como fuente.

### 7.5 — Embeddings: qué modelo y dónde
**Problema**: GPT-5.4 menciona "embeddings" 12+ veces pero nunca especifica qué modelo, qué dimensión, dónde se almacenan (Supabase pgvector? S3? memoria?), ni el costo.

**Lo que falta**: Decisión de modelo de embeddings (OpenAI ada-002? Sentence-transformers local? OpenRouter gratis?) y estrategia de almacenamiento.

### 7.6 — Límites de rate de APIs
**Problema**: BrandMentions, Apify, OpenRouter, Instagram MCP — todos tienen rate limits. El Plan no los documenta.

**Lo que falta**: Tabla de rate limits por API y estrategia de throttling.

### 7.7 — Qué hacer con los 77,909 menciones existentes de BrandMentions
**Problema**: Ya tenemos 24 proyectos con 77,909 menciones en BrandMentions. El Plan dice "crear proyecto dedicado" pero no dice qué hacer con los datos existentes.

**Lo que falta**: Estrategia de explotación de datos existentes vs nueva recolección.

### 7.8 — Instagram MCP: 4 tools disponibles
**Problema**: Tenemos Instagram MCP con tools de publicación y métricas, pero NO de scraping. Los tools son: publish, get_account_info, get_posts, get_post_insights. Ninguno sirve para buscar menciones de GC en Instagram.

**Lo que falta**: Clarificación de que Instagram MCP es para NUESTRA cuenta, no para investigación. Para investigar Instagram necesitamos Apify exclusivamente.

---

## RESUMEN CUANTITATIVO

| Categoría | Grok | Gemini | Claude | DeepSeek | GPT-5.4 auto | Sistémicas |
|-----------|------|--------|--------|----------|--------------|------------|
| Integrado | 5 | 5 | 12 | 10 | - | - |
| Parcialmente integrado | 2 | 2 | 3 | 3 | 4 | - |
| Omitido (debería estar) | 9 | 6 | 8 | 4 | 2 | 8 |
| **Total omisiones** | **9** | **6** | **8** | **4** | **2** | **8** |

**Total de omisiones detectadas: 37**

De estas 37, clasifico como **críticas para ejecución inmediata**: 12

---

## TOP 12 OMISIONES CRÍTICAS (ordenadas por impacto en ejecución)

| # | Omisión | Sabio origen | Impacto |
|---|---------|-------------|---------|
| 1 | Migración del schema existente (9 tablas → 23 tablas) | Ninguno | Bloquea Paso 2 |
| 2 | Acceso a Supabase con cuenta correcta | Ninguno | Bloquea Paso 2 |
| 3 | Validación del dueño de la Ficha de Identidad + línea de tiempo de eventos | Claude | Bloquea Paso 1 |
| 4 | Detección "Zero-Text" (70% de ataques son visuales sin texto) | Gemini | Pierde mayoría de contenido visual hostil |
| 5 | Presupuesto Apify por plataforma y orden de prioridad | Claude + Ninguno | Agota presupuesto en semana 1 |
| 6 | Anti-menciones (abstención sincronizada) | Grok | Pierde señal forense única |
| 7 | Cuentas "viuda negra" (aparecen solo para atacar/defender) | Grok | Pierde patrón operativo clave |
| 8 | Embedding Entropy + HDBSCAN para detección de operador | Grok | Detección inferior a la posible |
| 9 | Datos de simulación para testing del pipeline | DeepSeek | No se puede validar antes de gastar dinero |
| 10 | Filtro de texto corto (>50 chars) para similitud textual | Claude | Miles de falsos positivos |
| 11 | Pipeline visual de 3 pasos (Triage → OCR → Análisis profundo) | Gemini | 70-80% más caro sin el embudo |
| 12 | Instagram MCP es para nuestra cuenta, no para investigación | Ninguno | Expectativa falsa sobre capacidad |

---

## RECOMENDACIÓN FINAL

El Plan Definitivo de GPT-5.4 es **sólido en arquitectura y estrategia** (90% correcto). Pero tiene **brechas de ejecución** que yo como ejecutor necesito resolver antes de empezar:

1. **Integrar las 12 omisiones críticas** como addendum al Plan
2. **Adoptar el código ejecutable de Claude y DeepSeek** en vez de los pseudocódigos de GPT-5.4
3. **Adoptar las técnicas de Grok** (anti-menciones, viuda negra, embedding entropy, consistencia ortográfica) como señales adicionales en Fase 4
4. **Adoptar el pipeline visual de Gemini** como embudo de 3 pasos en Fase 2
5. **Resolver los 8 problemas sistémicos** (schema existente, acceso Supabase, presupuesto Apify, Mentionlytics, embeddings, rate limits, datos existentes BM, Instagram MCP) antes de ejecutar Paso 1

**Propuesta**: Enviar esta auditoría a GPT-5.4 para que produzca un **Addendum v3.1** que integre las 37 omisiones sin modificar la estructura del Plan Definitivo.
