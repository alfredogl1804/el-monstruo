---
name: site-reality-reconstructor
description: Sistema de reconstrucción de entornos reales con evidencia trazable para generar renders arquitectónicos fieles a la realidad actual del sitio. Usa Gemini Maps Grounding, OSM Overpass, Perplexity, análisis visual multimodal, fotos del usuario y navegador para crear un Site Reality Document (SRD) estructurado con restricciones duras, blind spots explícitos y validación obligatoria de renders. Usar cuando se necesite generar renders de un sitio real, reconstruir el entorno actual de una ubicación, o validar que un render es fiel a la realidad.
---

# Site Reality Reconstructor v2.0

Sistema de reconstrucción de realidad con evidencia trazable. Produce un **Site Reality Document (SRD)** y un **Spatial Reality Model (SRM)** que actúan como contrato de verdad para la generación de renders arquitectónicos. Diseñado por el Consejo de 6 Sabios.

## Propósito

Resolver el problema de que los renders generados por IA inventan elementos inexistentes (edificios, paisajismo, infraestructura) porque no tienen información del estado real del lugar. Este skill reconstruye la realidad antes de renderizar.

## Qué hay de nuevo en v2.0

| Módulo nuevo | Función | Fuentes |
|-------------|---------|---------|
| `photo_processor.py` | Procesamiento masivo de fotos del usuario: EXIF, GPS, clasificación por zona, análisis visual | Fotos del usuario + Gemini Vision |
| `social_media_collector.py` | Búsqueda agresiva en redes sociales de fotos y videos del sitio | Perplexity + YouTube + Instagram/TikTok + Google Images |
| `sketchup_analyzer.py` | Extracción de datos de modelos 3D: renders, archivos SKP, planos PDF | Gemini Vision + pdf2image |
| `spatial_model_builder.py` | Mezclador maestro que fusiona TODAS las fuentes en un modelo espacial unificado | GPT-5.4 |

## Principio Fundamental

> El skill no imagina el sitio: **reconstruye una hipótesis espacial verificable** con evidencia, fechas, niveles de confianza y restricciones duras.

## Reglas Inquebrantables

1. **NUNCA** inventar detalle específico en una zona no observada
2. **NUNCA** aprobar un render que viole una regla crítica del SRD
3. **OBLIGATORIO** que cada afirmación tenga evidencia asociada con fecha y fuente
4. **OBLIGATORIO** marcar blind spots explícitamente con nivel de confianza
5. **OBLIGATORIO** ejecutar render_validator antes de entregar cualquier render
6. **PROHIBIDO** prometer porcentajes de fidelidad como SLA comercial
7. **OBLIGATORIO** solicitar fotos del usuario cuando la cobertura es insuficiente

## Jerarquía de Verdad (Resolución de Conflictos)

Cuando hay conflicto entre fuentes, gana la de mayor rango:

| Rango | Fuente | Tipo | Confianza máx |
|:-----:|--------|------|:-------------:|
| 1 | Fotos/videos recientes del usuario | Visual directa | 0.95 |
| 2 | Planos técnicos PDF | Dimensional | 0.92 |
| 3 | Modelo SketchUp | 3D referencia | 0.88 |
| 4 | Renders existentes del proyecto | Intención de diseño | 0.85 |
| 5 | Google Street View | Visual directa | 0.82 |
| 6 | Imagen satelital | Visual aérea | 0.80 |
| 7 | Video de YouTube | Visual indirecta | 0.75 |
| 8 | OSM Overpass (geometría) | Datos estructurados | 0.72 |
| 9 | Gemini Maps Grounding (POIs) | Semántica | 0.70 |
| 10 | Google Images search | Visual no verificada | 0.65 |
| 11 | Instagram/TikTok | Social media | 0.60 |
| 12 | Perplexity / web | Contexto temporal | 0.58 |
| 13 | Inferencia conservadora | Estimación | 0.40 |

**Regla**: Recencia + visibilidad directa + trazabilidad vencen semántica general.

## Ejecución

Todos los comandos se ejecutan desde `/home/ubuntu/skills/site-reality-reconstructor/scripts/`.

```bash
# Pipeline completo v2.0 con TODAS las fuentes
python3.11 run_reconstruction.py \
    --lat 20.9411 --lng -89.5960 \
    --radius 300 \
    --name "Estadio Kukulkan" \
    --location "Mérida, Yucatán" \
    --output-dir /tmp/srd_output/ \
    --user-photos /path/to/user/photos/ \
    --renders-dir /path/to/existing/renders/ \
    --sketchup-renders /path/to/sketchup/screenshots/ \
    --sketchup-files /path/to/skp/files/ \
    --pdf-plans /path/to/pdf/plans/

# Pipeline mínimo (sin fotos del usuario ni SketchUp)
python3.11 run_reconstruction.py \
    --lat 20.9411 --lng -89.5960 \
    --radius 300 \
    --name "Estadio Kukulkan" \
    --output-dir /tmp/srd_output/

# Sin búsqueda en redes sociales
python3.11 run_reconstruction.py \
    --lat 20.9411 --lng -89.5960 \
    --radius 300 \
    --name "Estadio Kukulkan" \
    --output-dir /tmp/srd_output/ \
    --no-social

# Solo recolección (sin fusión ni SRD)
python3.11 run_reconstruction.py \
    --lat 20.9411 --lng -89.5960 \
    --radius 300 \
    --name "Estadio Kukulkan" \
    --output-dir /tmp/srd_output/ \
    --only-collect

# Validar un render contra un SRD existente
python3.11 render_validator.py \
    --srd /tmp/srd_output/site_reality.json \
    --render /path/to/render.png \
    --output /tmp/srd_output/validation_report.json
```

Parámetros v2.0:
- `--location "Ciudad, Estado"` — Para búsquedas en redes sociales
- `--user-photos /dir/` — Directorio con fotos del usuario (EXIF + GPS + Gemini Vision)
- `--max-photos 100` — Máximo de fotos a procesar
- `--renders-dir /dir/` — Renders existentes del proyecto
- `--sketchup-renders /dir/` — Screenshots/renders del modelo SketchUp
- `--sketchup-files /dir/` — Archivos .skp
- `--pdf-plans /dir/` — Planos PDF del proyecto
- `--no-social` — Desactivar búsqueda en redes sociales
- `--skip-spatial-model` — Omitir el spatial model builder
- `--target-date YYYY-MM-DD` — Fecha objetivo de realidad (default: hoy)
- `--views N,S,E,W,aerial` — Vistas objetivo para renders
- `--skip-browser` — Omitir recolección via navegador
- `--skip-grounding` — Omitir Gemini Maps Grounding
- `--confidence-threshold 0.6` — Umbral mínimo de confianza

## Módulos (13 scripts core + 1 orquestador)

### Orquestador
| Script | Función |
|--------|---------|
| `run_reconstruction.py` | Entrypoint v2.0: orquesta el DAG completo de 10 pasos |

### Módulos Core (v1.0)
| Script | Función | API/Fuente |
|--------|---------|------------|
| `site_resolver.py` | Normaliza coordenadas, radio, orientación, vistas | Local + Geocoding |
| `coverage_profiler.py` | Evalúa disponibilidad de fuentes por sitio | OSM + Gemini |
| `osm_collector.py` | Recolecta footprints, vías, uso de suelo, POIs | Overpass API (gratis) |
| `maps_grounding_collector.py` | Recolecta negocios, lugares, contexto semántico | Gemini Maps Grounding |
| `web_researcher.py` | Investiga cambios recientes, noticias, descripciones | Perplexity Sonar |
| `visual_analyzer.py` | Analiza imágenes (satelital, fotos, street view) | Gemini Vision |
| `evidence_fuser.py` | Fusiona evidencia por atributo con reglas de precedencia | GPT-5.4 |
| `srd_builder.py` | Genera site_reality.json + .md + render_constraints.json | GPT-5.4 |
| `render_validator.py` | Valida render contra SRD, emite score y violaciones | Gemini Vision |

### Módulos Nuevos (v2.0)
| Script | Función | API/Fuente |
|--------|---------|------------|
| `photo_processor.py` | Procesamiento masivo de fotos: EXIF, GPS, zona, análisis visual | Pillow + Gemini Vision |
| `social_media_collector.py` | Búsqueda en Instagram, YouTube, TikTok, Google Images | Perplexity + manus-analyze-video |
| `sketchup_analyzer.py` | Análisis de renders SketchUp, metadata SKP, planos PDF | Gemini Vision + pdf2image |
| `spatial_model_builder.py` | Mezclador maestro: construye modelo espacial unificado | GPT-5.4 |

## Flujo del DAG v2.0

```
site_resolver
    ↓
coverage_profiler
    ↓
┌──────────────────────────────────────────────────────────┐
│ RECOLECCIÓN PARALELA (Paso 3)                            │
│ osm_collector ──────────────────────────────────────────┐│
│ maps_grounding_collector ───────────────────────────────┤│
│ web_researcher ─────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────┐
│ FUENTES EXTENDIDAS v2.0 (Pasos 4-6)                     │
│ photo_processor (fotos del usuario) ────────────────────┐│
│ social_media_collector (Instagram/YouTube/TikTok) ──────┤│
│ sketchup_analyzer (modelos 3D, planos PDF) ─────────────┘│
└──────────────────────────────────────────────────────────┘
    ↓
spatial_model_builder (modelo espacial unificado) ← NUEVO v2.0
    ↓
evidence_fuser (fusión por atributo + conflictos)
    ↓
srd_builder (genera SRD + constraints)
    ↓
render_validator (valida renders contra SRD)
```

## Procesamiento de Fotos del Usuario (v2.0)

El módulo `photo_processor.py` acepta un directorio con muchas fotos y:

1. **Extrae EXIF/GPS** de cada foto (latitud, longitud, altitud, heading, timestamp, cámara)
2. **Clasifica por zona** relativa al sitio (interior, perímetro N/S/E/W, exterior)
3. **Calcula orientación** de la cámara (hacia dónde estaba mirando)
4. **Analiza con Gemini Vision** cada foto para extraer elementos visibles
5. **Genera un catálogo espacial** agrupado por zona con cobertura

Salidas:
- `photo_catalog.json` — Catálogo completo con todas las fotos clasificadas
- `photo_analyses.json` — Análisis visual detallado de cada foto

## Búsqueda en Redes Sociales (v2.0)

El módulo `social_media_collector.py` busca agresivamente en:

1. **Google Images** — Fotos recientes del sitio y alrededores
2. **YouTube** — Videos recientes (tours, noticias, recorridos) + análisis con manus-analyze-video
3. **Instagram/TikTok** — Posts geolocalizados, hashtags populares
4. **Renders existentes** — Cataloga renders del proyecto con Gemini Vision

## Análisis de SketchUp (v2.0)

El módulo `sketchup_analyzer.py` extrae información de:

1. **Renders/screenshots** del modelo SketchUp → dimensiones, materiales, escala
2. **Archivos .skp** → metadata (si formato ZIP/2021+)
3. **Planos PDF** → dimensiones exactas, layout, cotas, áreas

## Modelo Espacial Unificado (v2.0)

El módulo `spatial_model_builder.py` es el corazón de v2.0:

1. **Agrega** todas las observaciones de todas las fuentes
2. **Clasifica** por zona espacial (8 cardinales + interior)
3. **Fusiona** con GPT-5.4 respetando la jerarquía de verdad
4. **Produce** un modelo JSON con:
   - Descripción del sitio core
   - Realidad de cada zona cardinal
   - Estructuras adyacentes con confianza
   - Blind spots explícitos
   - Restricciones duras y prohibidas para renders
   - Mapa de confianza por zona

## Salidas del Skill

| Archivo | Formato | Contenido |
|---------|---------|-----------|
| `site_reality.json` | JSON | SRD completo con evidencia trazable |
| `site_reality.md` | Markdown | Versión legible para humanos |
| `render_constraints.json` | JSON | Reglas duras para el generador de renders |
| `coverage_report.json` | JSON | Perfil de cobertura de fuentes |
| `evidence/spatial_model/spatial_model.json` | JSON | Modelo espacial unificado (v2.0) |
| `evidence/spatial_model/spatial_model_summary.md` | Markdown | Resumen del modelo espacial |
| `evidence/user_photos/photo_catalog.json` | JSON | Catálogo de fotos del usuario |
| `evidence/social_media/social_media_raw.json` | JSON | Resultados de redes sociales |
| `evidence/sketchup/sketchup_analysis.json` | JSON | Análisis de modelos 3D |
| `evidence/raw_evidence.json` | JSON | Toda la evidencia cruda |
| `validation_report.json` | JSON | Resultado de validación de render |

## Semáforo de Cobertura

| Color | Significado | Acción |
|-------|-------------|--------|
| Verde | Render realista permitido | Proceder con generación |
| Amarillo | Render con restricciones fuertes | Proceder con blind spots marcados |
| Rojo | Evidencia insuficiente | Solicitar más fotos al usuario antes de renderizar |

## Protocolo de Fotos del Usuario

Cuando la cobertura es insuficiente, solicitar al usuario:

1. 4 fotos cardinales del sitio (N, S, E, W)
2. 4 fotos desde el entorno inmediato mirando hacia el sitio
3. Video 360 opcional del perímetro
4. Fotos de detalles relevantes (señalización, materiales, vegetación)
5. Fotos de los alrededores (calles, terrenos, edificios vecinos)
6. Screenshots del modelo SketchUp si existe

## Validación de Renders

El `render_validator.py` compara cada render contra el SRD y emite:

| Campo | Descripción |
|-------|-------------|
| `reality_fidelity_score` | 0.0-1.0 score general |
| `critical_violations` | Violaciones que invalidan el render |
| `major_violations` | Violaciones significativas |
| `minor_violations` | Detalles menores |
| `pass_fail` | PASS / FAIL |

Reglas críticas (fallo automático si se viola):
- Inventar edificio donde el lote está vacío
- Subir contexto de 1-2 niveles a 5+ niveles
- Añadir paisajismo exuberante inexistente
- Cambiar superficie de tierra/estacionamiento por boulevard premium
- Omitir un elemento marcado como must_include

## Credenciales Requeridas

| Variable | Servicio | Módulo |
|----------|----------|--------|
| GEMINI_API_KEY | Gemini Maps Grounding + Vision | maps_grounding_collector, visual_analyzer, photo_processor, sketchup_analyzer, render_validator |
| SONAR_API_KEY | Perplexity Sonar | web_researcher, social_media_collector |
| OPENAI_API_KEY | GPT-5.4 | evidence_fuser, srd_builder, spatial_model_builder |

## Dependencias

- `google-genai` — SDK de Gemini
- `requests` — HTTP para Overpass y Perplexity
- `pyyaml` — Parsing de configuración
- `Pillow` — Procesamiento de imágenes y EXIF
- `piexif` — Extracción avanzada de EXIF
- `pdf2image` — Conversión de PDF a imágenes para análisis

## Configuración

- `config/skill_config.yaml` — Configuración centralizada
- `references/overpass_queries.md` — Queries Overpass pre-construidas
- `references/render_rules.md` — Reglas de validación de renders
- `templates/srd_template.json` — Template del SRD

## Metadata

```yaml
version: "2.0"
created: "2026-04-11"
updated: "2026-04-11"
designed_by: "Consejo de 6 Sabios (GPT-5.4, Claude, Gemini, Grok, DeepSeek, Perplexity)"
last_verified: "2026-04-11"
ttl_days: 30
next_review: "2026-05-11"
```
