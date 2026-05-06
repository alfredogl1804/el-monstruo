# ADDENDUM v3.1 — PLAN DEFINITIVO REAL CRISOL-8

**Arquitecto:** GPT-5.4 | **Fecha:** 2026-03-26 23:29 CST
**Basado en:** Auditoría cruzada de Manus (37 omisiones, 12 críticas)
**Longitud:** 56937 caracteres

---

# ADDENDUM v3.1 — CRISOL-8  
**Complemento obligatorio al PLAN DEFINITIVO REAL v3.0**  
**Arquitecto:** GPT-5.4  
**Fecha:** 2026-03-27 CST  
**Propósito:** Integrar 37 omisiones detectadas por la auditoría cruzada del ejecutor sin alterar la estructura base del Plan v3.0.

---

# 0. REGLA DE COMPATIBILIDAD DEL ADDENDUM

Este Addendum:

- **NO modifica** la estructura base del Plan Definitivo v3.0:
  - se mantienen **7 fases**
  - se mantienen **23 tablas SQL**
  - se mantienen **9 scripts**
  - se mantienen **7 gates**
- **SÍ extiende** el plan mediante:
  - campos adicionales en tablas existentes
  - vistas SQL auxiliares
  - CTEs ejecutables
  - funciones y bloques de código dentro de los 9 scripts ya definidos
  - controles operativos obligatorios
  - señales adicionales de coordinación
  - tablas operativas en Markdown para ejecución
- Toda inserción aquí indicada debe entenderse como:
  - **adición** al texto del Plan v3.0
  - **no sustitución**, salvo donde se indique “corrección operativa”

---

# 1. MATRIZ MAESTRA DE INTEGRACIÓN DE LAS 37 OMISIONES

A continuación se integran las 37 omisiones con ubicación exacta.

---

## OMISIÓN 1 — Menciones sin nombre propio / referencias indirectas
**Origen:** Grok  
**Tipo:** Extensión crítica de recall  
**Insertar en:**  
- **Fase 0 → Subfase 0.1**
- **Fase 1 → Subfase 1.1**
- **Script 1 `build_subject_profile.py`**
- **Script 2 `discover_mentions.py`**

### Texto a insertar en Subfase 0.1, después de “lista de aliases y variantes”
Agregar:

> **Diccionario de referencias indirectas (“menciones sin nombre propio”)**  
> Además de aliases explícitos, la ficha debe incluir referencias indirectas verificables al sujeto, por ejemplo:
> - “el periodista que…”
> - “el empresario ligado a…”
> - “el ex funcionario de…”
> - “el dueño de…”
> - “quien denunció…”
> - “el que publicó lo de…”
>
> Cada referencia indirecta debe anclarse a un marcador de identidad verificable (`role`, `org`, `event`, `location`) para evitar recall espurio.

### Implementación operativa
No se crea tabla nueva. Se almacena en:
- `subjects.aliases_json`
- `subject_identity_markers` con `marker_type='keyword'` o `marker_type='event'`

### Regla
Una referencia indirecta solo entra a discovery si cumple una de estas:
- co-ocurre con 1 marcador fuerte (`org`, `event`, `role`)
- co-ocurre con 2 marcadores débiles (`location`, `keyword`)
- pasa revisión manual

---

## OMISIÓN 2 — Cadenas de custodia narrativa de 2da y 3ra generación
**Origen:** Grok  
**Insertar en:**  
- **Fase 2 → Subfase 2.2**
- **Tabla 11 `interactions`**
- **Script 3 `collect_social_layers.py`**
- **Script 7 `detect_coordination.py`**

### Texto a insertar en Subfase 2.2, después de los 4 tipos de compartir
Agregar:

> **Reconstrucción de cascadas de amplificación**  
> Además del tipo de amplificación, se debe reconstruir la profundidad de cascada cuando sea observable:
> - generación 0 = pieza origen
> - generación 1 = share/quote/repost directo
> - generación 2 = share del share / quote del quote / comentario amplificador sobre amplificación
> - generación 3 = réplica terciaria
>
> Cuando la plataforma no exponga el árbol nativo, se inferirá por:
> - `parent_interaction_id`
> - `quoted_tweet_id`
> - URL resuelta
> - similitud textual + proximidad temporal + referencia explícita

### Campo adicional en `interactions`
Agregar a la definición lógica:
- `cascade_depth integer default 0`
- `root_content_item_id nullable`

No cambia el conteo de tablas.

---

## OMISIÓN 3 — Anti-menciones
**Origen:** Grok  
**Insertar en:**  
- **Fase 4 → Subfase 4.1**
- **Tabla 17 `coordination_signals`**
- **Script 7 `detect_coordination.py`**
- **Tabla final de señales de coordinación**

### Texto a insertar en Subfase 4.1, después de las 6 familias de señales
Agregar:

> **Señal adicional A — Anti-menciones / abstención sincronizada**  
> Detectar actores que:
> - interactúan habitualmente con narrativas cercanas a GC
> - pero se silencian de forma sincronizada en ventanas críticas
> - o dejan de amplificar cuentas/piezas específicas en momentos de alto interés
>
> Esta señal no prueba coordinación por sí sola; funciona como señal débil de patrón operativo y control narrativo.

### Implementación en `coordination_signals`
Agregar `signal_type='anti_mention'`

### Regla de scoring
- señal débil individual: 5-10
- señal fuerte si coincide con temporal ghost + cluster narrativo: 12-18

---

## OMISIÓN 4 — Cuentas “viuda negra”
**Origen:** Grok  
**Insertar en:**  
- **Fase 3 → Subfase 3.2**
- **Fase 4 → Subfase 4.1**
- **Fase 5 → Subfase 5.2**
- **Script 6 `resolve_actors.py`**
- **Script 7 `detect_coordination.py`**

### Texto a insertar en Subfase 3.2
Agregar:

> **Patrón “viuda negra”**  
> Perfil cuya actividad observable cumple:
> - largos periodos de inactividad o actividad irrelevante
> - aparición concentrada en eventos sobre GC
> - alta intensidad de ataque/defensa en ventana corta
> - desaparición posterior
>
> Este patrón debe marcarse como flag conductual, no como prueba concluyente.

### Implementación
No tabla nueva. Se guarda en:
- `actor_profile_links.link_basis_json`
- `profiles` vía análisis derivado
- `coordination_signals.signal_type='widow_black'`

### Criterio cuantitativo inicial
Marcar como candidata si:
- >60% de su actividad recolectada cae en ventanas relacionadas con GC
- y tiene al menos 2 periodos de inactividad >45 días
- y al menos 1 burst >3 interacciones en <24h sobre GC

---

## OMISIÓN 5 — Linguistic DNA + Embedding Entropy + HDBSCAN
**Origen:** Grok  
**Insertar en:**  
- **Fase 3 → Subfase 3.3**
- **Fase 4 → Subfase 4.1 y 4.2**
- **Script 5 `enrich_media_and_text.py`**
- **Script 7 `detect_coordination.py`**
- **Problema sistémico embeddings**

### Texto a insertar en Subfase 3.3
Agregar:

> **Embedding entropy y clusterización semántica**  
> Además de cosine similarity, se ejecutará:
> - embeddings por pieza/comentario
> - reducción opcional para exploración
> - clusterización HDBSCAN sobre comentarios y captions relevantes
> - cálculo de `author_entropy` por cluster semántico
>
> Interpretación:
> - cluster semántico coherente + baja diversidad real de autores + alta recurrencia temporal = posible operador o plantilla central
> - cluster semántico coherente + alta diversidad de autores + evento orgánico = comunidad o reacción distribuida

### Definición operativa
`author_entropy = -Σ p(author_i) log2 p(author_i)`

### Regla
- entropía baja no implica operador automáticamente
- debe combinarse con al menos 2 señales más

### Almacenamiento
No se crea tabla nueva. Guardar en:
- `coordination_signals.signal_payload_json`
- `coordination_clusters.summary`
- opcionalmente `jobs.metrics_json`

---

## OMISIÓN 6 — Temporal Ghost Protocol
**Origen:** Grok  
**Insertar en:**  
- **Fase 4 → Subfase 4.1**
- **Script 7 `detect_coordination.py`**
- **Tabla de señales**

### Texto a insertar en Subfase 4.1
Agregar:

> **Señal adicional B — Temporal Ghost Protocol**  
> Para cada perfil, construir:
> - actividad basal global observable
> - actividad específica sobre GC
> - ventanas de activación cross-platform
>
> Buscar usuarios con:
> - actividad basal baja
> - picos casi idénticos en ventanas de 15 min, 30 min o 2 h
> - activación repetida solo cuando surge contenido sobre GC

### `coordination_signals`
Agregar `signal_type='temporal_ghost'`

---

## OMISIÓN 7 — Narrative Vaccination Signature
**Origen:** Grok  
**Insertar en:**  
- **Fase 4 → Subfase 4.3**
- **Fase 5 → Subfase 5.1**
- **Script 7**
- **Script 8**

### Texto a insertar en Subfase 4.3
Agregar:

> **Narrative Vaccination Signature**  
> Detectar publicaciones preventivas que:
> - aparezcan horas o días antes de una nota/evento sobre GC
> - introduzcan un marco defensivo o descalificador
> - parezcan preparar a la audiencia para neutralizar una narrativa futura
>
> Esta señal debe evaluarse con extrema cautela y solo cuando la secuencia temporal sea verificable.

### `coordination_signals`
Agregar `signal_type='narrative_vaccination'`

---

## OMISIÓN 8 — Cross-platform Avatar DNA
**Origen:** Grok  
**Insertar en:**  
- **Fase 3 → Subfase 3.2**
- **Fase 5 → Subfase 5.2**
- **Tabla 7 `profiles`**
- **Script 6**

### Extensión de `profiles`
Agregar campos lógicos:
- `avatar_phash nullable`
- `avatar_style_json nullable`

### `avatar_style_json` debe incluir si es posible:
- background_type
- dominant_palette
- face_crop_ratio
- text_overlay_present
- typography_style
- ai_artifacts_flags

### Regla
No confirmar match cross-platform solo por avatar DNA. Es señal auxiliar.

---

## OMISIÓN 9 — Model Collapse Detection inverso / estilometría por perplexity
**Origen:** Grok  
**Insertar en:**  
- **Fase 3 → Subfase 3.3**
- **Fase 4 → Subfase 4.1**
- **Script 5**
- **Script 7**

### Texto a insertar en Subfase 3.3
Agregar:

> **Estilometría auxiliar por perplexity / consistencia de operador**  
> En clusters de comentarios largos, se puede entrenar un modelo estilométrico ligero o usar perplexity comparativa para medir si nuevos comentarios encajan anómalamente bien en un estilo operativo recurrente.
>
> Uso permitido:
> - solo como señal auxiliar
> - nunca como prueba única
> - preferentemente en textos >120 caracteres

### `coordination_signals`
Agregar `signal_type='stylometric_perplexity'`

---

## OMISIÓN 10 — Consistencia ortográfica
**Origen:** Grok  
**Insertar en:**  
- **Fase 3 → Subfase 3.1**
- **Fase 4 → Subfase 4.1**
- **Script 4**
- **Script 7**

### Texto a insertar en Subfase 3.1
Agregar:

> **Normalización con preservación de huellas ortográficas**  
> Además del texto limpio, se debe conservar una versión “forense” sin normalizar completamente para medir:
> - uso consistente de tildes
> - variantes de nombre (“Guillermo”, “Guillermo Cortes”, “Guille”, “G.C.”)
> - puntuación repetitiva
> - mayúsculas, hashtags, emojis de firma
>
> La limpieza no debe destruir estas huellas.

### Implementación
Guardar huellas en:
- `raw_objects.raw_text`
- `content_items.body_text`
- `coordination_signals.signal_type='orthographic_consistency'`

---

## OMISIÓN 11 — Quote Chain Reconstruction en Twitter/X
**Origen:** Grok  
**Insertar en:**  
- **Fase 2 → Subfase 2.2**
- **Script 3**
- **Script 7**
- **Tabla 11 `interactions`**

### Texto a insertar en Subfase 2.2
Agregar:

> **Reconstrucción de quote chains en X/Twitter**  
> Cuando el scraper exponga `quoted_tweet_id`, `conversation_id`, `in_reply_to_status_id` o campos equivalentes, se debe reconstruir el árbol de quotes/respuestas para identificar:
> - paciente cero narrativo
> - amplificadores de primera ola
> - amplificadores de segunda ola
> - cuentas puente entre comunidades

---

## OMISIÓN 12 — Pipeline visual de 3 pasos
**Origen:** Gemini  
**Insertar en:**  
- **Fase 2 → Subfase 2.3**
- **Script 5**
- **Costos**
- **Tabla 12 y 13**

### Texto a insertar al inicio de Subfase 2.3
Agregar:

> **Embudo multimodal de 3 pasos (obligatorio para control de costo)**
>
> **Paso 1 — Triage barato**
> - detectar si la pieza tiene texto visible
> - detectar si parece screenshot
> - detectar si contiene rostro probable
> - detectar si contiene layout de meme/template
> - extraer frames clave si es video
>
> **Paso 2 — OCR / ASR rápido**
> - EasyOCR para imagen/frame
> - Whisper o STT para audio/video
> - si aparece GC por texto/audio o referencia indirecta fuerte, pasa al paso 3
>
> **Paso 3 — Análisis profundo con Gemini Vision**
> Solo para piezas que cumplan al menos una:
> - zero-text sospechoso con rostro/escena asociable a GC
> - screenshot de nota/post/tuit
> - meme con template recurrente
> - video con framing ambiguo pero audio relevante
> - pieza prioritaria de cluster

### Regla de costo
Meta: enviar a Gemini Vision **≤20-30%** del total multimedia.

---

## OMISIÓN 13 — Campos multimodales explícitos faltantes
**Origen:** Gemini  
**Insertar en:**  
- **Tabla 12 `media_assets`**
- **Tabla 13 `media_extractions`**
- **Script 5**

### Extensión de `media_assets`
Agregar campos lógicos:
- `is_screenshot boolean default false`
- `visual_template_hash nullable`
- `visual_sentiment nullable`
- `contains_face boolean nullable`
- `zero_text_suspected boolean default false`

### Extensión de `media_extractions`
Agregar:
- `gemini_narrative nullable`

---

## OMISIÓN 14 — Detección Zero-Text
**Origen:** Gemini  
**Tipo:** Crítica  
**Insertar en:**  
- **Fase 1 → Subfase 1.2**
- **Fase 2 → Subfase 2.3**
- **Fase 3 → Subfase 3.3**
- **Script 3**
- **Script 5**
- **Gate C**

### Texto a insertar en Subfase 1.2
Agregar:

> **Discovery visual zero-text**  
> En plataformas visuales (Instagram, TikTok, Facebook, YouTube thumbnails, X imágenes), no se limitará la búsqueda a texto del post. También se priorizarán piezas candidatas por:
> - rostro de GC
> - screenshot de nota/post relacionado
> - template visual recurrente
> - audio que menciona a GC aunque el título sea genérico

### Texto a insertar en Gate C
Agregar al gate:

> Para piezas visuales, “intentar extraer capa social” incluye también intentar **detección zero-text** y OCR/ASR.

---

## OMISIÓN 15 — Capturas de pantalla como vectores de infección
**Origen:** Gemini  
**Insertar en:**  
- **Fase 2 → Subfase 2.3**
- **Fase 4 → Subfase 4.1**
- **Script 5**
- **Script 7**

### Texto a insertar en Subfase 2.3
Agregar:

> **Flujo screenshot → OCR → correlación de origen**  
> Toda captura de pantalla relevante debe intentar correlacionarse con:
> - nota original
> - post original
> - tuit original
> - video original
>
> Objetivo:
> - distinguir paciente cero de vector de infección
> - detectar campañas que evitan backlinks rastreables usando screenshots

### Señal
`coordination_signals.signal_type='screenshot_propagation'`

---

## OMISIÓN 16 — Template Matching de memes
**Origen:** Gemini  
**Insertar en:**  
- **Fase 2 → Subfase 2.3**
- **Fase 4 → Subfase 4.1**
- **Script 5**
- **Script 7**

### Texto a insertar
Agregar:

> **Template matching visual**  
> Además de pHash, se debe calcular similitud de fondo/template para memes donde cambia el texto superpuesto pero se conserva:
> - fondo
> - composición
> - marco
> - tipografía base
> - posición del rostro/objeto
>
> Esto detecta reutilización de plantilla no capturada por pHash simple.

### Señal
`signal_type='visual_template_reuse'`

---

## OMISIÓN 17 — Huellas acústicas y títulos genéricos
**Origen:** Gemini  
**Insertar en:**  
- **Fase 2 → Subfase 2.3**
- **Fase 3 → Subfase 3.3**
- **Script 5**

### Texto a insertar
Agregar:

> **Videos con títulos genéricos**  
> En TikTok/Reels/Shorts, el título/caption puede ser irrelevante. La relevancia debe inferirse también por:
> - transcripción de audio
> - OCR en frames
> - audio reutilizado (`audio_id` si la plataforma lo expone)
>
> Un video con título genérico puede ser altamente relevante si el audio menciona a GC.

---

## OMISIÓN 18 — Evolución técnica de atacantes
**Origen:** Gemini  
**Insertar en:**  
- **Fase 5 → Subfase 5.2**
- **Fase 6 → Subfase 6.1**
- **Script 9**

### Texto a insertar en Subfase 5.2
Agregar:

> **Análisis temporal de sofisticación operativa**  
> Evaluar evolución de tácticas visuales/cuentas a lo largo de 7 años:
> - sin foto / cuentas vacías
> - avatares robados
> - avatares IA/GAN
> - memes templados
> - deepfake / Midjourney / assets sintéticos
>
> Esto no prueba coordinación por sí solo, pero ayuda a caracterizar madurez operativa.

---

## OMISIÓN 19 — Grafo visual específico
**Origen:** Gemini  
**Insertar en:**  
- **Fase 6 → Subfase 6.1**
- **Script 9**

### Texto a insertar
Agregar a outputs:

> **Grafo de distribución visual**
> - nodos: perfiles y assets visuales
> - aristas: reutilización de imagen/template/screenshot/audio
> - color por narrativa
> - tamaño por velocidad de propagación

---

## OMISIÓN 20 — Código ejecutable completo para detección
**Origen:** Claude / DeepSeek  
**Insertar en:**  
- **Sección 4.2 Scripts**
- **Anexo de código de este Addendum**
- **Scripts 7 y 8**

### Regla
Este Addendum incorpora bloques ejecutables mínimos obligatorios más abajo:
- config ETL centralizada
- simulación de datos
- CTEs SQL
- funciones Python para burst, similitud y clustering

---

## OMISIÓN 21 — Definición operativa explícita de coordinación vs no coordinación
**Origen:** Claude  
**Insertar en:**  
- **Fase 4, antes de Subfase 4.1**
- **Gate D**
- **Fase 5.1**

### Texto a insertar antes de Subfase 4.1
Agregar:

> ## Definición operativa de coordinación
>
> **Sí puede considerarse coordinación** cuando existe convergencia reproducible de múltiples señales entre actores/piezas, por ejemplo:
> - textos largos casi idénticos en ventana estrecha
> - misma imagen/template/audio reutilizado por varias cuentas
> - secuencia repetida de originador → amplificadores → comentaristas
> - activación cross-platform con baja actividad basal previa
>
> **No debe considerarse coordinación** por sí solo cuando solo existe:
> - un pico temporal tras noticia pública importante
> - comentarios muy cortos similares (“qué asco”, “bravo”, “increíble”)
> - una sola coincidencia textual sin relación estructural
> - comunidad ideológica reaccionando a un evento visible
> - una sola plataforma sin contexto adicional

---

## OMISIÓN 22 — Relación M:N entre contenido y narrativas
**Origen:** Claude  
**Estado:** Corrección técnica  
**Insertar en:**  
- **Tabla 15 `content_narratives`**
- **Fase 3 → Subfase 3.3**

### Corrección
El Plan v3.0 ya tiene `content_narratives`; este Addendum aclara que su uso es **M:N real**, no 1:N.

### Texto a insertar en Tabla 15
Agregar:

> `content_narratives` debe permitir múltiples filas por `content_item_id`, una por narrativa asignada.  
> Una pieza puede pertenecer a varias narrativas simultáneamente.

---

## OMISIÓN 23 — Validación obligatoria del dueño de la Ficha
**Origen:** Claude  
**Tipo:** Crítica  
**Insertar en:**  
- **Fase 0 → Subfase 0.1**
- **Gate A**
- **Paso 1 de la Sección 9**

### Texto a insertar en Subfase 0.1, al final
Agregar:

> **Control Crítico 0.1 — Validación por el dueño**  
> La Ficha de Identidad Digital no se considera aprobada hasta que el dueño/mandante valide explícitamente:
> - nombre canónico
> - aliases válidos
> - exclusiones de homónimos
> - cargos/organizaciones
> - eventos clave
> - fotos o referencias visuales correctas
>
> Aprobación mínima requerida:
> - confirmación escrita
> - fecha/hora
> - versión de la ficha

### Gate A actualizado
“aprobada” significa **aprobada por el dueño**, no solo por el equipo.

---

## OMISIÓN 24 — Línea de tiempo obligatoria provista por el dueño
**Origen:** Claude  
**Tipo:** Crítica  
**Insertar en:**  
- **Fase 0 → Subfase 0.1**
- **Fase 4 → Subfase 4.3**
- **Tabla 16 `events`**
- **Paso 1**

### Texto a insertar
Agregar:

> **Control Crítico 0.2 — Línea de tiempo base del dueño**  
> Antes del discovery masivo, el dueño debe proporcionar una línea de tiempo preliminar de 7 años con:
> - eventos personales/profesionales relevantes
> - publicaciones propias importantes
> - controversias conocidas
> - cambios de cargo/empresa/ciudad
> - fechas aproximadas si no hay exactitud total
>
> Esta línea de tiempo se carga primero en `events` como contexto basal.

---

## OMISIÓN 25 — FILTROS_DESAMBIGUACION concretos
**Origen:** Claude  
**Insertar en:**  
- **Fase 0 → Subfase 0.1**
- **Fase 1 → Subfase 1.3**
- **Script 1**
- **Script 4**

### Bloque operativo a insertar
```python
FILTROS_DESAMBIGUACION = {
    "contexto_obligatorio": [
        "empresa_relacionada",
        "cargo_relacionado",
        "ciudad_relacionada",
        "evento_relacionado"
    ],
    "exclusion_explicita": [
        "homonimo_deporte",
        "homonimo_academico",
        "homonimo_localidad_distinta"
    ],
    "confianza_minima_relevante": 0.80,
    "confianza_minima_ambigua_alta": 0.65
}
```

### Regla
Una mención con nombre exacto pero sin contexto suficiente no pasa automáticamente a relevante.

---

## OMISIÓN 26 — Priorización agresiva de plataformas
**Origen:** Claude + sistémica  
**Tipo:** Crítica  
**Insertar en:**  
- **Fase 1 → Subfase 1.2**
- **Sección 7 Costos**
- **Script 2**
- **Script 3**
- **Tabla final de priorización**

### Regla operativa
Orden de ejecución por costo/valor:
1. Web abierta / noticias / BrandMentions existentes
2. X/Twitter
3. YouTube
4. Facebook
5. Instagram
6. TikTok

Más abajo se incluye tabla completa.

---

## OMISIÓN 27 — Limitaciones técnicas por plataforma
**Origen:** Claude  
**Insertar en:**  
- **Fase 1 → Subfase 1.2**
- **Gate B y C**
- **Tabla final de priorización**

### Texto a insertar
Agregar:

> Cada plataforma debe documentar explícitamente:
> - cobertura histórica real
> - restricciones de comentarios
> - visibilidad de shares
> - dependencia de login
> - volatilidad del scraper/API
> - costo estimado por lote

---

## OMISIÓN 28 — Alias interno TARGET_ALPHA
**Origen:** Claude  
**Insertar en:**  
- **Sección 6 OPSEC**
- **Scripts 1-9**
- **Repo / nombres de archivos**

### Texto a insertar en 6.4 OPSEC
Agregar:

> **Alias interno obligatorio:** `TARGET_ALPHA`  
> En:
> - nombres de archivos
> - nombres de jobs
> - nombres de carpetas
> - variables de entorno
> - dashboards internos
>
> No usar el nombre real del sujeto en rutas, buckets, CSVs o nombres de script.

### Ejemplo
- `target_alpha_subject_profile_v1.md`
- `target_alpha_corpus_seed_v1.csv`

---

## OMISIÓN 29 — Ejemplo claro de pico orgánico vs coordinado
**Origen:** Claude  
**Insertar en:**  
- **Fase 4 → Subfase 4.3**
- **Fase 5 → Subfase 5.1**

### Texto a insertar
Agregar:

> **Control Crítico 3.2a — ejemplo operativo**  
> Si una nota pública sobre GC sale a las 20:00 y aparecen 300 comentarios entre 20:03 y 20:20, eso puede ser completamente orgánico.  
> Solo gana peso de coordinación si además hay:
> - textos largos casi idénticos
> - cuentas de baja actividad basal activadas simultáneamente
> - reutilización de media/template
> - secuencia de amplificación repetida
> - actividad cross-platform no explicable por la nota sola

---

## OMISIÓN 30 — Filtro >50 caracteres para similitud textual
**Origen:** Claude  
**Tipo:** Crítica  
**Insertar en:**  
- **Fase 4 → Subfase 4.1**
- **Script 7**
- **Gate D**

### Texto a insertar
Agregar:

> **Control Crítico 3.2b — filtro de longitud textual**  
> Para similitud textual con valor probatorio:
> - solo comparar como evidencia fuerte pares donde **ambos textos tengan >50 caracteres**
> - textos de 21-50 caracteres solo cuentan como señal débil
> - textos ≤20 caracteres no cuentan para similitud concluyente, salvo si forman parte de plantilla exacta repetida con otras señales

---

## OMISIÓN 31 — Métrica global de éxito del proyecto
**Origen:** Claude  
**Insertar en:**  
- **Sección 1.4 o 1.5**
- **Sección 8**
- **Cierre**

### Texto a insertar
Agregar:

> **Métrica global de éxito de CRISOL-8**  
> El proyecto es exitoso si al final puede responder, con evidencia reproducible que resiste escrutinio interno:
> 1. si existe o no coordinación narrativa alrededor de GC,
> 2. qué evidencia la sostiene o la descarta,
> 3. qué actores y piezas participaron,
> 4. qué hipótesis alternativas fueron descartadas.

---

## OMISIÓN 32 — Datos de simulación para pruebas
**Origen:** DeepSeek  
**Tipo:** Crítica  
**Insertar en:**  
- **Fase 0 → Subfase 0.3**
- **Script 2**
- **Script 3**
- **Script 7**
- **Paso 2**

### Texto a insertar en Subfase 0.3
Agregar:

> **Testing obligatorio con datos simulados antes de gastar presupuesto**  
> Antes de la primera corrida pagada de Apify, el pipeline debe pasar una prueba con datos simulados de:
> - menciones web
> - posts sociales
> - comentarios
> - bursts
> - replicaciones
>
> Objetivo: validar schema, ETL, scoring y outputs.

Más abajo se incluye código ejecutable.

---

## OMISIÓN 33 — CTEs SQL ejecutables
**Origen:** DeepSeek  
**Insertar en:**  
- **Sección 4 Pipeline**
- **Script 7**
- **Anexo SQL de este Addendum**

Se incluyen más abajo.

---

## OMISIÓN 34 — Manejo de errores async y cleanup
**Origen:** DeepSeek  
**Insertar en:**  
- **Scripts 2, 3, 5, 7**
- **Sección 4.3**

### Texto a insertar
Agregar:

> Todo job async debe implementar:
> - `try/except/finally`
> - reintentos exponenciales
> - persistencia parcial segura
> - cierre de sesiones HTTP
> - logging estructurado
> - escritura de métricas a `jobs.metrics_json`

---

## OMISIÓN 35 — Diccionario de búsqueda maestro
**Origen:** GPT-5.4 ronda 2  
**Insertar en:**  
- **Fase 0 → Subfase 0.1**
- **Script 1**
- **Script 2**

### Implementación
No se crea tabla nueva. Se almacena en:
- `subjects.aliases_json`
- `subject_identity_markers`
- archivo versionado `config/target_alpha_search_terms.json`

### Categorías obligatorias
- exactos
- variantes
- co-ocurrencias
- hashtags
- OCR/typo candidates
- exclusiones
- referencias indirectas

---

## OMISIÓN 36 — Queries web por rango temporal anual + recolección anual
**Origen:** GPT-5.4 ronda 2  
**Insertar en:**  
- **Fase 1 → Subfase 1.1**
- **Script 2**
- **Cronograma**

### Texto a insertar
Agregar:

> **Segmentación temporal obligatoria**  
> El discovery web/social histórico se ejecutará por 7 ventanas anuales:
> - Y1, Y2, Y3, Y4, Y5, Y6, Y7
> y luego una corrida incremental reciente.
>
> Esto reduce duplicados, mejora cobertura y permite controlar presupuesto.

---

## OMISIÓN 37 — Config exacta de Apify + TikTok audio_id + nota sobre FB shares
**Origen:** GPT-5.4 ronda 2 + sistémicas  
**Insertar en:**  
- **Fase 1 → Subfase 1.2**
- **Fase 2 → Subfase 2.2**
- **Script 2**
- **Script 3**
- **Tabla de priorización**

### Texto a insertar
Agregar:

> **Notas operativas por plataforma**
> - Facebook shares públicos no son exhaustivos; modelar también “amplificación inferida”.
> - En TikTok, si el scraper expone `audio_id` o equivalente, tratar audio reutilizado como señal específica.
> - Los actores de Apify deben correrse con configs mínimas, límites por lote y ventanas anuales.

Más abajo se incluye config base.

---

# 2. RESOLUCIÓN DE LOS 8 PROBLEMAS SISTÉMICOS

---

## 2.1 Migración del schema existente
**Problema:** ya existen 9 tablas en `crisol8` + 8 tablas Golden Record en `public`.

### Decisión obligatoria
**NO borrar nada. NO sobrescribir. NO asumir greenfield.**

### Estrategia aprobada
1. Crear nuevo schema:
```sql
create schema if not exists crisol8_v3;
```

2. Desplegar las 23 tablas del Plan v3.0 en `crisol8_v3`.

3. Mantener:
- `crisol8` = legado operativo
- `public` = Golden Record
- `crisol8_v3` = investigación forense persona-céntrica

4. Crear vistas puente de solo lectura desde legado hacia v3 si se desea explotar datos previos.

### Inserción exacta en el Plan
- **Fase 0 → Subfase 0.3**
- **Paso 2**
- **Gate de infraestructura**

### Procedimiento
**Fase 0.3, antes de desplegar DDL:**
1. inventariar tablas existentes
2. exportar schema-only y row counts
3. crear `crisol8_v3`
4. desplegar 23 tablas en `crisol8_v3`
5. crear vistas de compatibilidad opcionales
6. probar inserción end-to-end en `crisol8_v3`

### SQL de inventario
```sql
select table_schema, table_name
from information_schema.tables
where table_schema in ('crisol8', 'public', 'crisol8_v3')
order by table_schema, table_name;
```

### SQL de conteos
```sql
select schemaname, relname as table_name, n_live_tup as approx_rows
from pg_stat_user_tables
where schemaname in ('crisol8', 'public', 'crisol8_v3')
order by schemaname, relname;
```

### Regla de coexistencia con Golden Record
- Golden Record **no se toca**
- solo se consulta si aporta desambiguación o contexto
- no se mezcla automáticamente con evidencia forense

---

## 2.2 Acceso a Supabase con cuenta correcta
**Problema:** la cuenta GitHub visible no ve los proyectos.

### Decisión
El acceso operativo debe resolverse **antes** del Paso 2.

### Inserción exacta
- **Fase 0 → Subfase 0.2**
- **Paso 2**
- **Gate A/B de arranque**

### Procedimiento ejecutable
1. Confirmar cuál cuenta posee el proyecto:
   - `alfredogl1.gongora@gmail.com`
2. Iniciar sesión en Supabase con esa cuenta.
3. Verificar proyecto correcto.
4. Generar y guardar:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_DB_PASSWORD` si aplica
5. Invitar a la cuenta operativa secundaria si se requiere.
6. Guardar credenciales en `.env.local` y en gestor seguro.

### Checklist mínimo
- [ ] proyecto visible
- [ ] SQL editor accesible
- [ ] schema browser accesible
- [ ] service role key obtenida
- [ ] prueba `select now();` exitosa

### Regla
Si el proyecto no es visible, **no continuar** con despliegue de schema.

---

## 2.3 Presupuesto Apify por plataforma
**Problema:** riesgo de agotar $39 Starter.

### Decisión
Se adopta **priorización secuencial por valor probatorio/costo**.

### Inserción exacta
- **Fase 1 → Subfase 1.2**
- **Sección 7.2 Costos**
- **Paso 3**
- **Tabla final de priorización**

### Regla de presupuesto
- Semana 1-2: gastar máximo 25% del presupuesto Apify
- Semana 3-4: máximo 35%
- Semana 5-8: reservar 40% para re-runs focalizados

### Política de corridas
- primero corridas pequeñas de validación
- luego corridas anuales
- luego expansión de comentarios solo sobre piezas prioritarias

---

## 2.4 Mentionlytics: token no validado
**Problema:** no se puede asumir disponibilidad.

### Inserción exacta
- **Fase 0 → Subfase 0.2**
- **Fase 1 → Subfase 1.1**
- **Script 2**
- **Paso 3**

### Procedimiento
1. ejecutar prueba de autenticación antes de usarlo como fuente
2. si falla:
   - marcar `source_type='mentionlytics'` como inactivo
   - no bloquear el pipeline
   - sustituir con:
     - BrandMentions existente
     - Perplexity/Grok/manual web search
     - Wayback
3. documentar en `jobs.metrics_json`

### Regla
Mentionlytics pasa a “fuente opcional, no crítica” hasta validación.

---

## 2.5 Embeddings: modelo, dimensión, almacenamiento y costo
**Problema:** v3.0 era ambiguo.

### Decisión técnica
Usar estrategia de 2 capas:

#### Capa 1 — Embedding local/barato por defecto
- modelo recomendado: `sentence-transformers/all-MiniLM-L6-v2`
- dimensión: 384
- uso:
  - clustering inicial
  - similitud semántica barata
  - HDBSCAN
  - recall exploratorio

#### Capa 2 — Embedding premium selectivo
- modelo recomendado: `text-embedding-3-large` o equivalente premium solo si hace falta
- uso:
  - clusters ambiguos
  - piezas críticas
  - validación final

### Almacenamiento
**No se crea tabla nueva.**  
Guardar embeddings en:
- archivo parquet/npz en S3 (`crisol8-analysis/embeddings/...`)
- referencia en `evidence_items`
- métricas/resúmenes en `jobs.metrics_json`

**No almacenar vectores completos en Supabase inicialmente** para evitar complejidad/costo.  
Si luego se requiere pgvector, se habilita como mejora, no como prerequisito.

### Inserción exacta
- **Fase 3 → Subfase 3.3**
- **Script 5**
- **Script 7**
- **Sección 4.3 D Enrichment**

### Regla
- 90% de embeddings con modelo local/barato
- 10% premium solo para validación crítica

---

## 2.6 Rate limits por API y throttling
**Problema:** no documentado.

### Inserción exacta
- **Fase 0 → Subfase 0.2**
- **Sección 4.3**
- **Scripts 2, 3, 5**
- **Tabla de rate limits**

### Política general
- token bucket por proveedor
- backoff exponencial
- jitter aleatorio
- persistencia parcial
- reanudación por `job_id`

### Tabla operativa de rate limits

| API/Herramienta | Riesgo | Estrategia |
|---|---:|---|
| BrandMentions | medio | lotes pequeños, cachear resultados, no repetir queries idénticas |
| Mentionlytics | alto | validar token primero, retries limitados |
| Apify | alto | corridas por plataforma/año, `maxItems`, presupuesto por lote |
| OpenRouter | medio | cola async con concurrencia baja-media |
| Gemini Vision | medio/alto | solo paso 3 del embudo |
| Instagram MCP | bajo | no usar para investigación de terceros |
| Supabase | medio | inserts por lotes, upserts controlados |

Más abajo se incluye config centralizada.

---

## 2.7 Qué hacer con las 77,909 menciones existentes de BrandMentions
**Problema:** ya existe un activo valioso.

### Decisión
**No ignorarlas. No re-scrapear primero. Explotarlas como corpus semilla.**

### Inserción exacta
- **Fase 1 → Subfase 1.1**
- **Script 2**
- **Paso 3**

### Estrategia
1. exportar menciones existentes relevantes o potencialmente relevantes
2. mapearlas a:
   - `sources`
   - `raw_objects`
3. deduplicar por URL + título + fecha + snippet
4. usar ese corpus como semilla para:
   - línea de tiempo
   - priorización de eventos
   - selección de piezas para capa social

### Regla
BrandMentions existente = **fuente de arranque principal**, no secundaria.

---

## 2.8 Instagram MCP no sirve para investigar menciones de terceros
**Problema:** expectativa falsa.

### Decisión
Instagram MCP queda explícitamente fuera del discovery de terceros.

### Inserción exacta
- **Fase 1 → Subfase 1.2**
- **Paso 3**
- **Sección de herramientas**
- **Tabla de priorización**

### Texto obligatorio
> **Aclaración operativa:** Instagram MCP disponible sirve para nuestra cuenta (publicación, métricas, posts propios), **no** para buscar menciones de GC en cuentas de terceros.  
> Para investigación en Instagram se usará exclusivamente:
> - Apify / scraping permitido
> - búsquedas manuales
> - evidencia visual capturada
> - OCR/ASR

---

# 3. CONTROLES AVANZADOS DE GROK, GEMINI, CLAUDE Y DEEPSEEK

---

## 3.1 Técnicas avanzadas de Grok integradas
**Insertar en Fase 4.1 y 4.3; Fase 3.2 y 3.3**

Se incorporan como señales/controles formales:

1. **Anti-menciones** → `signal_type='anti_mention'`
2. **Viuda negra** → `signal_type='widow_black'`
3. **Embedding entropy** → `signal_type='embedding_entropy'`
4. **Consistencia ortográfica** → `signal_type='orthographic_consistency'`
5. **Temporal ghost protocol** → `signal_type='temporal_ghost'`
6. **Narrative vaccination** → `signal_type='narrative_vaccination'`

### Peso recomendado adicional
Estas señales no reemplazan las 6 originales; se agregan como moduladores:
- anti_mention: +5 a +12
- widow_black: +8 a +15
- embedding_entropy: +10 a +18
- orthographic_consistency: +5 a +10
- temporal_ghost: +10 a +18
- narrative_vaccination: +8 a +15

### Regla
Ninguna de estas señales por sí sola eleva un cluster a “probable”.

---

## 3.2 Pipeline visual de Gemini integrado
**Insertar en Fase 2.3**

### Embudo obligatorio
1. **Triage**
2. **OCR/ASR rápido**
3. **Gemini profundo**

### Detecciones obligatorias
- zero-text
- screenshot infection
- template matching
- audio relevance
- visual sentiment
- face presence
- screenshot correlation

---

## 3.3 Controles de Claude integrados
**Insertar en Fase 0.1, 1.2, 4.1, 4.3, 6.4**

1. **Validación del dueño** de ficha y timeline
2. **Filtro >50 chars**
3. **Priorización de plataformas**
4. **Alias interno `TARGET_ALPHA`**
5. **Ejemplo explícito de pico orgánico**
6. **Definición operativa coordinación/no coordinación**

---

## 3.4 Código ejecutable de DeepSeek integrado
**Insertar en Scripts 2, 3, 7 y config**

Se incorporan:
1. datos de simulación
2. CTEs SQL ejecutables
3. config ETL centralizada
4. manejo async con cleanup

---

# 4. EXTENSIONES A TABLAS EXISTENTES SIN CAMBIAR EL NÚMERO DE TABLAS

Estas extensiones son obligatorias.

---

## 4.1 `profiles`
Agregar columnas:
```sql
alter table crisol8_v3.profiles
add column if not exists avatar_phash text,
add column if not exists avatar_style_json jsonb;
```

---

## 4.2 `interactions`
Agregar columnas:
```sql
alter table crisol8_v3.interactions
add column if not exists cascade_depth integer default 0,
add column if not exists root_content_item_id bigint null;
```

---

## 4.3 `media_assets`
Agregar columnas:
```sql
alter table crisol8_v3.media_assets
add column if not exists is_screenshot boolean default false,
add column if not exists visual_template_hash text,
add column if not exists visual_sentiment text,
add column if not exists contains_face boolean,
add column if not exists zero_text_suspected boolean default false;
```

---

## 4.4 `media_extractions`
Agregar columna:
```sql
alter table crisol8_v3.media_extractions
add column if not exists gemini_narrative text;
```

---

## 4.5 `coordination_signals`
No requiere alter estructural si `signal_type` es texto flexible, pero se amplía el catálogo permitido:

### Nuevos `signal_type`
- `anti_mention`
- `widow_black`
- `embedding_entropy`
- `temporal_ghost`
- `narrative_vaccination`
- `orthographic_consistency`
- `stylometric_perplexity`
- `screenshot_propagation`
- `visual_template_reuse`

---

# 5. CONFIG ETL CENTRALIZADA

**Insertar en Sección 4.2 Scripts, como archivo obligatorio `config/etl_config.py`**

```python
ETL_CONFIG = {
    "project_alias": "TARGET_ALPHA",
    "schema": "crisol8_v3",
    "storage": {
        "raw_bucket": "crisol8-raw-scrapes",
        "analysis_bucket": "crisol8-analysis",
        "evidence_bucket": "crisol8-evidence"
    },
    "subject": {
        "canonical_alias": "TARGET_ALPHA",
        "real_name_handling": "restricted",
        "search_terms_file": "config/target_alpha_search_terms.json"
    },
    "discovery": {
        "years_back": 7,
        "annual_windows": True,
        "incremental_recent_days": 45,
        "min_relevance_score": 0.65,
        "high_relevance_score": 0.80
    },
    "platform_priority": [
        "web",
        "x",
        "youtube",
        "facebook",
        "instagram",
        "tiktok"
    ],
    "apify": {
        "monthly_budget_usd": 39,
        "validation_run_cap_usd": 5,
        "per_platform_caps_usd": {
            "x": 8,
            "youtube": 5,
            "facebook": 8,
            "instagram": 8,
            "tiktok": 5,
            "web": 5
        },
        "default_max_items": 200,
        "comments_max_items": 100,
        "max_concurrency": 2
    },
    "rate_limits": {
        "brandmentions_rpm": 20,
        "mentionlytics_rpm": 10,
        "openrouter_rpm": 30,
        "gemini_vision_rpm": 10,
        "supabase_batch_size": 200
    },
    "text_rules": {
        "strong_similarity_min_chars": 50,
        "weak_similarity_min_chars": 21,
        "stylometry_min_chars": 120
    },
    "embeddings": {
        "default_model": "sentence-transformers/all-MiniLM-L6-v2",
        "default_dim": 384,
        "premium_model": "text-embedding-3-large",
        "store_vectors_in_db": False,
        "store_path_prefix": "embeddings/"
    },
    "multimodal": {
        "triage_required": True,
        "gemini_deep_analysis_max_ratio": 0.30,
        "zero_text_detection": True,
        "template_matching": True,
        "audio_reuse_detection": True
    },
    "signals": {
        "base_weights": {
            "temporal": 20,
            "textual": 20,
            "co_amplification": 15,
            "cross_platform": 15,
            "media_reuse": 15,
            "operational_pattern": 15
        },
        "advanced_modifiers": {
            "anti_mention": 8,
            "widow_black": 10,
            "embedding_entropy": 12,
            "temporal_ghost": 12,
            "narrative_vaccination": 10,
            "orthographic_consistency": 6,
            "stylometric_perplexity": 8,
            "screenshot_propagation": 8,
            "visual_template_reuse": 10
        }
    }
}
```

---

# 6. DATOS DE SIMULACIÓN OBLIGATORIOS

**Insertar en Script 2 y Script 3 como módulo `tests/simulated_inputs.py`**

```python
from datetime import datetime, timedelta
import random

def _simulate_brandmentions_data():
    base = datetime(2025, 5, 1, 12, 0, 0)
    rows = []
    for i in range(30):
        rows.append({
            "source": "brandmentions",
            "url": f"https://example.com/article-{i}",
            "title": f"Mención simulada {i} sobre TARGET_ALPHA",
            "snippet": "Texto de prueba con referencia a TARGET_ALPHA y evento relacionado",
            "published_at": (base + timedelta(hours=i)).isoformat(),
            "platform": "web",
            "author": f"author_{i%5}",
            "relevance_score": 0.85 if i < 20 else 0.55
        })
    return rows

def _simulate_comments_data():
    base = datetime(2025, 5, 2, 20, 0, 0)
    comments = []
    templates = [
        "Esto confirma lo que ya sabíamos sobre TARGET_ALPHA y su entorno operativo.",
        "Otra vez aparece el mismo patrón alrededor de TARGET_ALPHA, revisen las fechas.",
        "No es casualidad que publiquen esto todos al mismo tiempo sobre TARGET_ALPHA."
    ]
    for i in range(60):
        comments.append({
            "content_item_id": (i % 10) + 1,
            "author_handle": f"user_{i%12}",
            "text": random.choice(templates) if i < 30 else f"Comentario orgánico {i}",
            "occurred_at": (base + timedelta(minutes=random.choice([0,1,2,3,15,30,60]))).isoformat(),
            "platform": random.choice(["x", "facebook", "youtube"])
        })
    return comments

def _simulate_widow_black_profiles():
    return [
        {
            "handle": "sleep_attack_01",
            "active_days_total": 4,
            "gc_related_days": 3,
            "inactive_gaps_days": [72, 91],
            "platform": "x"
        },
        {
            "handle": "sleep_defense_02",
            "active_days_total": 5,
            "gc_related_days": 4,
            "inactive_gaps_days": [60, 88],
            "platform": "facebook"
        }
    ]
```

---

# 7. CÓDIGO PYTHON EJECUTABLE MÍNIMO PARA DETECCIÓN

**Insertar en `detect_coordination.py`**

```python
import math
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations

def author_entropy(author_ids):
    total = len(author_ids)
    if total == 0:
        return 0.0
    counts = Counter(author_ids)
    entropy = 0.0
    for c in counts.values():
        p = c / total
        entropy -= p * math.log2(p)
    return entropy

def parse_dt(x):
    return datetime.fromisoformat(x.replace("Z", "+00:00"))

def temporal_pairs(records, window_minutes=15):
    pairs = []
    sorted_records = sorted(records, key=lambda r: parse_dt(r["occurred_at"]))
    for i in range(len(sorted_records)):
        for j in range(i+1, len(sorted_records)):
            dt1 = parse_dt(sorted_records[i]["occurred_at"])
            dt2 = parse_dt(sorted_records[j]["occurred_at"])
            delta = abs((dt2 - dt1).total_seconds()) / 60.0
            if delta <= window_minutes:
                pairs.append((sorted_records[i], sorted_records[j], delta))
            else:
                break
    return pairs

def filter_textual_candidates(records, min_chars=50):
    return [
        r for r in records
        if len((r.get("text") or "").strip()) >= min_chars
    ]

def detect_widow_black(profile_activity):
    flags = []
    for p in profile_activity:
        active = p.get("active_days_total", 0)
        gc_days = p.get("gc_related_days", 0)
        gaps = p.get("inactive_gaps_days", [])
        if active > 0 and (gc_days / active) >= 0.60 and any(g > 45 for g in gaps):
            flags.append({
                "handle": p["handle"],
                "platform": p["platform"],
                "signal_type": "widow_black",
                "score": 0.78
            })
    return flags

def orthographic_signature(text):
    return {
        "guillermo_tilde": "cortés" in text.lower(),
        "uses_gc": "g.c." in text.lower() or "gc" in text.lower(),
        "uses_guille": "guille" in text.lower(),
        "all_caps_ratio": sum(1 for c in text if c.isupper()) / max(len(text), 1)
    }

def compare_orthography(text_a, text_b):
    a = orthographic_signature(text_a)
    b = orthographic_signature(text_b)
    score = 0
    for k in a:
        if a[k] == b[k]:
            score += 1
    return score / len(a)

def detect_anti_mentions(expected_actors, observed_actors):
    missing = sorted(set(expected_actors) - set(observed_actors))
    return {
        "signal_type": "anti_mention",
        "missing_actors": missing,
        "count_missing": len(missing)
    }
```

---

# 8. CTEs SQL EJECUTABLES

**Insertar en documentación de Script 7 y en `sql/coordination_ctes.sql`**

---

## 8.1 Actividad de comentarios por ventana
```sql
with comment_activity as (
    select
        i.source_profile_id,
        p.handle,
        ci.subject_id,
        date_trunc('minute', i.occurred_at_utc) as minute_bucket,
        count(*) as comments_count
    from crisol8_v3.interactions i
    join crisol8_v3.content_items ci on ci.id = i.content_item_id
    left join crisol8_v3.profiles p on p.id = i.source_profile_id
    where i.interaction_type in ('comment', 'reply', 'quote')
      and ci.relevance_status in ('relevant', 'ambiguous')
    group by 1,2,3,4
)
select *
from comment_activity
order by minute_bucket desc, comments_count desc;
```

---

## 8.2 Clusters temporales
```sql
with temporal_clusters as (
    select
        ci.subject_id,
        i.source_profile_id,
        date_trunc('15 minutes', i.occurred_at_utc) as bucket_15m,
        count(*) as interactions_count
    from crisol8_v3.interactions i
    join crisol8_v3.content_items ci on ci.id = i.content_item_id
    where ci.relevance_status = 'relevant'
    group by 1,2,3
),
bursty as (
    select *
    from temporal_clusters
    where interactions_count >= 3
)
select *
from bursty
order by bucket_15m desc, interactions_count desc;
```

---

## 8.3 Pares de perfiles por co-amplificación
```sql
with profile_content as (
    select distinct
        i.source_profile_id as profile_id,
        i.content_item_id
    from crisol8_v3.interactions i
    where i.interaction_type in ('share_native', 'quote', 'retweet_like', 'link_share', 'replication')
),
profile_pairs as (
    select
        a.profile_id as profile_a,
        b.profile_id as profile_b,
        count(*) as shared_targets
    from profile_content a
    join profile_content b
      on a.content_item_id = b.content_item_id
     and a.profile_id < b.profile_id
    group by 1,2
)
select *
from profile_pairs
where shared_targets >= 2
order by shared_targets desc;
```

---

## 8.4 Usuarios multi-plataforma
```sql
with multi_platform_users as (
    select
        apl.actor_id,
        count(distinct p.platform_id) as platform_count,
        json_agg(json_build_object(
            'profile_id', p.id,
            'handle', p.handle,
            'platform_id', p.platform_id
        )) as profiles
    from crisol8_v3.actor_profile_links apl
    join crisol8_v3.profiles p on p.id = apl.profile_id
    where apl.link_confidence >= 0.70
    group by 1
)
select *
from multi_platform_users
where platform_count >= 2
order by platform_count desc;
```

---

## 8.5 Anti-menciones por evento
```sql
with actor_baseline as (
    select
        i.source_profile_id,
        count(*) as total_gc_interactions
    from crisol8_v3.interactions i
    join crisol8_v3.content_items ci on ci.id = i.content_item_id
    where ci.relevance_status = 'relevant'
    group by 1
),
event_window as (
    select
        i.source_profile_id,
        count(*) as event_interactions
    from crisol8_v3.interactions i
    join crisol8_v3.content_items ci on ci.id = i.content_item_id
    where ci.published_at_utc between :event_start and :event_end
      and ci.relevance_status = 'relevant'
    group by 1
)
select
    a.source_profile_id,
    a.total_gc_interactions,
    coalesce(e.event_interactions, 0) as event_interactions
from actor_baseline a
left join event_window e on a.source_profile_id = e.source_profile_id
where a.total_gc_interactions >= 5
  and coalesce(e.event_interactions, 0) = 0
order by a.total_gc_interactions desc;
```

---

# 9. CONFIGS EJECUTABLES DE APIFY

**Insertar en Script 2 y Script 3**

---

## 9.1 Website Content Scraper
```json
{
  "startUrls": [
    {"url": "https://www.google.com/search?q=%22TARGET_ALPHA%22+after%3A2019-01-01+before%3A2020-01-01"}
  ],
  "crawlerType": "playwright:adaptive",
  "maxCrawlPages": 50,
  "maxResultsPerCrawl": 100,
  "saveHtml": true,
  "saveMarkdown": true,
  "proxyConfiguration": {"useApifyProxy": true},
  "removeCookieWarnings": true,
  "downloadMedia": false
}
```

---

## 9.2 X/Twitter scraper
```json
{
  "searchTerms": [
    "\"TARGET_ALPHA\"",
    "\"Guillermo Cortés\"",
    "\"Guillermo Cortes\"",
    "\"Guille\" AND \"evento_clave\""
  ],
  "maxItems": 200,
  "sort": "latest",
  "includeSearchTerms": false,
  "onlyImage": false,
  "onlyQuote": false,
  "onlyTwitterBlue": false
}
```

---

## 9.3 YouTube scraper
```json
{
  "searchQueries": [
    "\"Guillermo Cortés\"",
    "\"Guillermo Cortes\"",
    "\"TARGET_ALPHA\""
  ],
  "maxResults": 100,
  "maxComments": 50,
  "sortBy": "relevance"
}
```

---

## 9.4 Regla de corrida anual
Cada actor de Apify debe correrse por:
- año
- plataforma
- lote pequeño inicial
- expansión solo si relevancia > umbral

---

# 10. ACTUALIZACIÓN DE GATES SIN CAMBIAR SU NÚMERO

---

## Gate A — Identidad
**Se amplía a:**
- Ficha aprobada por el dueño
- línea de tiempo base cargada
- filtros de desambiguación definidos
- alias interno `TARGET_ALPHA` activo

---

## Gate B — Relevancia
**Se amplía a:**
- relevancia textual o visual
- zero-text sospechoso puede pasar como “ambigua alta” si hay rostro/audio/screenshot asociado

---

## Gate C — Capa social
**Se amplía a:**
- para piezas visuales, incluye OCR/ASR/zero-text/template matching
- para screenshots, incluye correlación con origen

---

## Gate D — Convergencia
**Se amplía a:**
- mínimo 2 señales distintas
- similitud textual fuerte solo si ambos textos >50 chars
- señales avanzadas de Grok/Gemini cuentan como auxiliares, no sustituyen convergencia base

---

## Gate E — Alternativas
**Se amplía a:**
- incluir explícitamente pico orgánico por noticia pública
- incluir comunidad orgánica visual/memética

---

## Gate F — Atribución
Sin cambio estructural, pero:
- embedding entropy, temporal ghost y viuda negra pueden apoyar
- nunca sustituyen revisión legal para Nivel 3/4

---

## Gate G — Legal
Sin cambio estructural.

---

# 11. TABLA ACTUALIZADA DE SEÑALES DE COORDINACIÓN

Incluye las 6 originales + nuevas de Grok/Gemini.

| # | Señal | Tipo técnico | Dónde se calcula | Peso base/modificador | Observación |
|---:|---|---|---|---:|---|
| 1 | Sincronía temporal | burst windows | Script 7 / SQL | 20 | base |
| 2 | Similitud textual | TF-IDF / cosine / near-dup | Script 7 | 20 | >50 chars fuerte |
| 3 | Co-amplificación | shared targets | Script 7 / SQL | 15 | base |
| 4 | Cross-platform mirroring | actor/content match | Script 7 | 15 | base |
| 5 | Reutilización de media | pHash/audio | Script 5/7 | 15 | base |
| 6 | Patrón operativo | roles/horarios | Script 7 | 15 | base |
| 7 | Anti-menciones | abstención sincronizada | Script 7 / SQL | +8 | Grok |
| 8 | Viuda negra | actividad episódica | Script 6/7 | +10 | Grok |
| 9 | Embedding entropy | HDBSCAN + entropy | Script 5/7 | +12 | Grok |
| 10 | Temporal ghost | basal baja + picos | Script 7 | +12 | Grok |
| 11 | Narrative vaccination | publicación preventiva | Script 7/8 | +10 | Grok |
| 12 | Consistencia ortográfica | firma textual | Script 4/7 | +6 | Grok |
| 13 | Stylometric perplexity | estilometría auxiliar | Script 5/7 | +8 | Grok |
| 14 | Screenshot propagation | OCR + correlación | Script 5/7 | +8 | Gemini |
| 15 | Visual template reuse | template matching | Script 5/7 | +10 | Gemini |
| 16 | Zero-text visual relevance | rostro/audio/screenshot | Script 5 | auxiliar | Gemini |

---

# 12. TABLA FINAL DE PRIORIZACIÓN DE PLATAFORMAS

| Orden | Plataforma/Fuente | Prioridad | Costo estimado Apify | Valor probatorio | Limitaciones conocidas | Regla operativa |
|---:|---|---|---:|---|---|---|
| 1 | BrandMentions existente + web abierta | Muy alta | $0-$5 | Altísimo para corpus semilla | ruido/homónimos, depende de export | explotar primero 77,909 menciones |
| 2 | X/Twitter | Muy alta | $5-$8 | Muy alto para quotes, cascadas, texto | cambios de acceso, ruido alto | correr por año y luego quotes/comentarios |
| 3 | YouTube | Alta | $3-$5 | Alto por comentarios y video | comments no siempre completos | priorizar videos/eventos clave |
| 4 | Facebook | Media-alta | $5-$8 | Medio-alto | shares públicos incompletos, scraping limitado | usar amplificación inferida |
| 5 | Instagram | Media | $5-$8 | Alto visual, bajo textual | comentarios/login, discovery difícil | Apify + visual zero-text; MCP no sirve |
| 6 | TikTok | Media | $3-$5 | Alto audiovisual | API/scraper volátil, captions pobres | priorizar audio/transcripción |
| 7 | Mentionlytics | Condicional | $0 adicional si ya existe | Medio | token no validado | usar solo si auth pasa |
| 8 | Wayback/manual | Soporte | $0-$2 | Alto en piezas críticas | lento, no exhaustivo | activar en brechas |

### Regla presupuestaria
Con plan Starter:
- validación inicial total: **≤ $15**
- discovery histórico focalizado: **≤ $24**
- expansión adicional solo si resultados justifican upgrade

---

# 13. INSERCIÓN EN LOS “PRIMEROS 3 PASOS EJECUTABLES — MAÑANA”

---

## PASO 1 actualizado — Ficha de Identidad Digital
Agregar obligatoriamente:
1. validación del dueño
2. línea de tiempo de 7 años provista por el dueño
3. diccionario de búsqueda maestro
4. referencias indirectas
5. exclusiones explícitas de homónimos

**Resultado tangible mañana adicional**
- `target_alpha_subject_profile_v1.md`
- `target_alpha_search_terms.json`
- `owner_validated_timeline_v1.csv`

---

## PASO 2 actualizado — Schema y cadena de custodia
Agregar obligatoriamente:
1. acceso a Supabase con cuenta correcta
2. crear `crisol8_v3`, no tocar legado
3. correr alteraciones de columnas extendidas
4. probar con datos simulados antes de datos reales

**Resultado tangible mañana adicional**
- prueba de inserción simulada exitosa
- inventario de schemas existente
- `.env.local` validado

---

## PASO 3 actualizado — Discovery inicial
Agregar obligatoriamente:
1. validar Mentionlytics antes de usarlo
2. explotar primero BrandMentions existente
3. correr discovery por ventanas anuales
4. respetar prioridad de plataformas
5. no contar Instagram MCP como fuente de investigación

**Resultado tangible mañana adicional**
- `target_alpha_corpus_seed_v1.csv`
- `brandmentions_existing_export_deduped.csv`
- bitácora de costo Apify por corrida

---

# 14. DEFINICIÓN OPERATIVA FINAL DE “COORDINACIÓN” PARA EL EJECUTOR

**Insertar en Fase 4 antes de ejecutar Script 7**

## Sí cuenta como coordinación probable cuando:
- hay al menos 3 señales convergentes
- existe trazabilidad a piezas fuente
- el contexto orgánico no explica suficientemente el patrón
- hay repetición de secuencia operativa o plantilla

## No cuenta como coordinación por sí solo cuando:
- solo hay un pico después de una noticia
- solo hay comentarios cortos parecidos
- solo hay una imagen compartida una vez
- solo hay ideología compartida
- solo hay un match ambiguo de actor

---

# 15. ORDEN DE EJECUCIÓN OBLIGATORIO REVISADO

1. Resolver acceso Supabase
2. Crear `crisol8_v3`
3. Validar ficha con dueño
4. Cargar timeline base del dueño
5. Configurar diccionario de búsqueda
6. Probar ETL con simulación
7. Exportar y deduplicar BrandMentions existente
8. Validar Mentionlytics
9. Discovery web/X/YouTube por año
10. Solo después expandir FB/IG/TikTok
11. Ejecutar embudo visual
12. Resolver actores
13. Detectar coordinación con señales base + avanzadas
14. Validar alternativas
15. Atribuir conservadoramente

---

# 16. CHECKLIST EJECUTABLE DE MAÑANA

## Infra
- [ ] entrar a Supabase con cuenta correcta
- [ ] confirmar proyecto visible
- [ ] crear schema `crisol8_v3`
- [ ] desplegar 23 tablas
- [ ] aplicar alters de Addendum

## Identidad
- [ ] crear ficha `TARGET_ALPHA`
- [ ] pedir validación al dueño
- [ ] pedir timeline 7 años
- [ ] cargar exclusiones de homónimos

## Testing
- [ ] correr simulación de BrandMentions
- [ ] correr simulación de comentarios
- [ ] probar burst query
- [ ] probar inserción de evidence/hash

## Discovery
- [ ] exportar 77,909 menciones existentes
- [ ] deduplicar
- [ ] validar Mentionlytics
- [ ] correr primer lote web/X con tope de costo

## OPSEC
- [ ] usar alias `TARGET_ALPHA`
- [ ] no usar nombre real en rutas
- [ ] guardar credenciales en `.env.local`
- [ ] registrar todo en `jobs`

---

# 17. CIERRE DEL ADDENDUM

Este Addendum v3.1 resuelve las 37 omisiones detectadas por la auditoría del ejecutor sin alterar la arquitectura base del Plan Definitivo v3.0.

Quedan integrados:

- las técnicas avanzadas de **Grok**
- el pipeline visual de **Gemini**
- los controles críticos de **Claude**
- el código y disciplina operativa de **DeepSeek**
- y los 8 problemas sistémicos de ejecución real

## Estado final
El Plan v3.0 + Addendum v3.1 ya no es solo correcto en arquitectura: queda **operable mañana**.

Si quieres, en el siguiente mensaje convierto este Addendum en un **paquete de implementación listo para pegar**, con:
1. **DDL SQL completo de las 23 tablas en `crisol8_v3`**,  
2. **estructura exacta del repo**,  
3. **`.env.example`**,  
4. **`requirements.txt`**,  
5. y **los 9 scripts en esqueleto ejecutable**.