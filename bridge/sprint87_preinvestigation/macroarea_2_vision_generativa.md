# Pre-investigación Sprint 87 — Macroárea 2: Visión Generativa

> Hilo Manus Catastro · 2026-05-04 22:00 CST · Standby Productivo Sprint 86  
> Validación tiempo real ejecutada el 2026-05-04. Fuente primaria: Artificial Analysis Image Arena (visitada en navegador).

---

## 1. Justificación de macroárea

La **Macroárea 2 — Visión Generativa** se incorpora al Catastro porque la Roadmap del Catastro (definida en Bloque 1, ver `kernel/catastro/schema.py` enum `Macroarea.VISION_GENERATIVA`) la marca como el siguiente dominio a poblar tras Inteligencia. La industria 2026 confirma su madurez: 127 modelos públicos rankeados por Elo, 72 con datos de API operativos, y un mercado dividido entre **3 hyperscalers** (OpenAI, Google, xAI) y **2 specialists open-weight** (Black Forest Labs, BytePlus).

La separación con Macroárea 1 (Inteligencia) es clara: los modelos de visión generativa **producen píxeles**, no tokens; sus métricas de calidad son **perceptuales** (Elo de blind preference voting humano), no logits sobre benchmarks textuales; sus economías de inferencia se miden por **imagen generada**, no por millón de tokens.

## 2. Dominios candidatos (subdivisión de la macroárea)

El Image Arena de Artificial Analysis ya divide nativamente el espacio en **2 sub-leaderboards** independientes, lo cual confirma la siguiente subdivisión canónica para el schema del Catastro:

| Dominio (slug) | Descripción | Tarea representativa |
|---|---|---|
| `text-to-image` | Generación de imagen desde prompt textual | "Genera un ave fénix volando sobre Mérida" |
| `image-editing` | Edición de imagen existente con instrucción textual | "Reemplaza el cielo por uno tormentoso" |
| `image-to-video` | Animación de imagen estática a clip corto | "Anima esta foto con movimiento de cámara dolly-in" |
| `text-to-video` | Generación de clip desde prompt textual | "Tigre corriendo por la jungla, 5 segundos, 720p" |

Los dos primeros son **prioridad Sprint 87**. Los dos últimos quedan diferidos a Sprint 88 (la lógica del Trono Score y la persistencia atómica son agnósticas de modalidad, el dominio se agrega vía registro en `catastro_modelos` sin migración).

## 3. Modelos frontier observados (Top-15 Elo, abril 2026)

Datos capturados en vivo desde [artificialanalysis.ai/text-to-image](https://artificialanalysis.ai/text-to-image) el 2026-05-04 21:59 CST. Esta es **fuente primaria**, no entrenamiento del LLM.

| Rank | Modelo | Elo | Provider | Notas |
|---|---|---|---|---|
| 1 | GPT Image 2 (high) | **1338** | OpenAI | Lanzado abril 2026, primer modelo con reasoning built-in |
| 2 | GPT Image 1.5 (high) | 1272 | OpenAI | Predecesor, sigue competitivo |
| 3 | Nano Banana 2 (Gemini 3.1 Flash Image) | 1261 | Google | Hereda velocidad de Flash |
| 4 | Nano Banana Pro (Gemini 3 Pro Image) | 1218 | Google | Multi-imagen reference, 4K nativo |
| 5 | Seedream 4.0 | 1202 | BytePlus | Bytedance, fuerte en estética asiática |
| 6 | FLUX.2 [max] | 1201 | Black Forest Labs | Open-weights flagship |
| 7 | MAI-Image-2 | 1196 | Microsoft | Confirmar provider |
| 8 | Peanut (Open Weights, Coming Soon) | 1192 | -- | Desconocido todavía, watch closely |
| 9 | FLUX.2 [pro] | 1188 | Black Forest Labs | API hosted |
| 10 | FLUX.2 [flex] | 1183 | Black Forest Labs | Tier intermedio |
| 11 | grok-imagine-image | 1182 | xAI | Integrado a Grok |
| 12 | ImagineArt 2.0 | 1181 | -- | Verificar provider |
| 13 | Imagen 4 Ultra | 1174 | Google | Tercer producto Google de imagen |
| 14 | Seedream 4.5 | 1169 | BytePlus | Iteración menor |
| 15 | FLUX.2 [dev] Turbo | 1164 | Black Forest Labs | Open-weight, más rápido |

**Observación crítica:** la diferencia entre #1 (1338) y #15 (1164) es 174 Elo, equivalente a una probabilidad de victoria de ~73% del top sobre el #15 — gap significativo pero no aplastante. Esto significa que el Trono Score con z-scores intra-dominio (Bloque 4) producirá un ranking más útil que el Elo crudo, porque normalizará por el dominio específico.

## 4. Métricas observadas en producción

### 4.1. Métricas que Artificial Analysis publica (4 ejes)

| Métrica | Tipo | Mapping al schema actual |
|---|---|---|
| **Image Arena Elo** | Quality (preferencia humana) | → `quality_score` (escalar 0-100 vía normalización) |
| **API Generation Time** | Speed (segundos por imagen) | → `speed_score` (más rápido = mejor, invertido a 0-100) |
| **API Price** | Cost (USD por 1k imágenes) | → `cost_efficiency` (más barato = mejor, invertido a 0-100) |
| **Provider** | Categórico | → `proveedor` (campo string ya existente) |

### 4.2. Rangos observados (Top-15)

- **Generation time:** 0.4s (FLUX.1 schnell, Prodia) → 35.7s (GPT Image 1.5 high). Spread 89×.
- **Price:** $2/1k (FLUX.1 schnell) → $134/1k (Nano Banana Pro). Spread 67×.
- **Elo:** 1164 → 1338 dentro del Top-15 (spread modesto, pero la cola larga llega a ~800 en el Top-127).

### 4.3. Métricas adicionales que NO publica AA pero SÍ usan papers académicos

| Métrica | Para qué | ¿Vale la pena para Catastro? |
|---|---|---|
| **FID (Fréchet Inception Distance)** | Distancia estadística entre imágenes generadas y reales | Útil para benchmark interno reproducible, pero requiere dataset propio |
| **CLIP Score** | Alineación texto-imagen | Útil para `prompt_fidelity` como subcapacidad |
| **HPSv2** | Human Preference Score v2 | Aproximación automática del Elo, sin necesidad de votos humanos |
| **AestheticPredictor v2.5** | Score estético modelado sobre LAION | Subcapacidad opcional |
| **Text rendering accuracy** | Habilidad para renderizar texto legible | Subcapacidad clave: GPT Image 2 ~95%, Nano Banana ~90%, Midjourney ~30% |
| **Multilingual prompt support** | Idiomas más allá de inglés | Subcapacidad: GPT Image 2 soporta JP/KR/ZH/HI/BN nativos |

## 5. Schema delta requerido (mínimo invasivo)

El schema actual de `catastro_modelos` (Bloque 1) **ya soporta** modelos de visión generativa sin migración. Los únicos cambios recomendados:

### 5.1. Agregar enum `Dominio` (no breaking)

```python
# kernel/catastro/schema.py
class Dominio(str, Enum):
    # Macroárea 1 (existentes)
    LLM_FRONTIER = "llm_frontier"
    LLM_OPEN_SOURCE = "llm_open_source"
    CODING_LLMS = "coding_llms"
    SMALL_EDGE = "small_edge"
    # Macroárea 2 (nuevos Sprint 87)
    TEXT_TO_IMAGE = "text-to-image"
    IMAGE_EDITING = "image-editing"
```

### 5.2. Agregar al campo `subcapacidades` (lista existente, JSONB)

```python
# Vocabulario controlado para subcapacidades de visión:
SUBCAPACIDADES_VISION = [
    "text_rendering",        # Renderiza texto legible en la imagen
    "multilingual_prompts",  # Acepta prompts en >1 idioma
    "photoreal_humans",      # Humanos fotorrealistas
    "prompt_fidelity_high",  # >0.85 CLIP score
    "fast_generation",       # <5s por imagen
    "high_resolution",       # >=4K nativo
    "multi_reference",       # Acepta >=2 imágenes de referencia
    "style_consistency",     # Mantiene estilo entre múltiples generaciones
]
```

### 5.3. Reusar `data_extra` (JSONB) para métricas crudas opcionales

```python
# Ejemplo de payload de un modelo de visión:
{
  "id": "gpt-image-2-high",
  "macroarea": "vision_generativa",
  "dominios": ["text-to-image", "image-editing"],
  "quality_score": 91.5,        # Elo 1338 normalizado
  "cost_efficiency": 12.3,      # $134/1k → muy bajo
  "speed_score": 22.0,          # 30s+ → bajo
  "reliability_score": 95.0,    # API uptime histórico
  "brand_fit": 0.85,
  "subcapacidades": ["text_rendering", "multilingual_prompts", "photoreal_humans"],
  "data_extra": {
    "elo_image_arena": 1338,
    "generation_time_seconds": 30.3,
    "price_per_1k_usd": 133,
    "max_resolution": "4K"
  }
}
```

**Conclusión:** Sprint 87 NO requiere cambios al pipeline, persistence, trono o MCP. Solo agrega valores enum y siembra modelos. Esto valida la decisión arquitectónica del Sprint 86 de hacer el schema agnóstico de modalidad.

## 6. Validador adversarial específico

Para Macroárea 1 (Inteligencia) usamos quorum 2-de-3 sobre **respuestas textuales** de 6 sabios LLM. Para Macroárea 2 esa estrategia NO aplica porque las "respuestas" son imágenes y los curadores no tienen ojos. Propongo un **quorum hybrido** para visión generativa:

| Curador | Tipo | Función |
|---|---|---|
| **Artificial Analysis Arena** | Datos públicos | Aporta Elo crudo (fuente principal de Quality) |
| **Perplexity grounded search** | LLM con búsqueda | Recopila claims de proveedores y verifica fechas de release |
| **GPT-5.5 + Claude Opus 4.7** | LLMs sin imagen | Validan **metadata textual** (precio, velocidad, capacidades, licencia) — NO juzgan calidad visual |
| **Gemini 3.1 Pro (multimodal)** | LLM multimodal | Único curador que SÍ puede hacer prompt fidelity scoring sobre N imágenes generadas con prompts canónicos |

**Quorum 2-de-3 modificado:** AA + Perplexity + (GPT-5.5 OR Claude) deben coincidir en metadata. Calidad visual viene únicamente del Elo de AA (no se simula con LLMs ciegos).

## 7. Fuentes y APIs accionables

| Fuente | URL | Cómo se ingiere |
|---|---|---|
| Artificial Analysis Image Arena | `artificialanalysis.ai/api/v2/data/image/...` (verificar paywall) | Si la API REST de AA expone image: usar `requests.get` con header `x-api-key`. Si no: scraping HTML del leaderboard (extraído via BeautifulSoup) |
| Black Forest Labs API | `api.bfl.ml/v1/...` | Para modelos FLUX, lista de modelos disponibles + pricing |
| OpenAI Images API | `api.openai.com/v1/images` | Pricing y modelos disponibles, NO Elo |
| Replicate | `api.replicate.com/v1/models` | Lista cross-provider (FLUX, SD, etc.) con pricing unificado |

**Anti-patrón:** NO confiar en webpages de noticias o blogs de comparación. Siempre fuente primaria del proveedor o Arena oficial.

## 8. Estimación de esfuerzo Sprint 87

Asumiendo el patrón del Sprint 86 (7 bloques, ~2h cada uno con 60+ tests):

| Bloque | Trabajo | ETA |
|---|---|---|
| 87-B1 | Schema delta (enum Dominio, subcapacidades visión) + tests | 0.5h |
| 87-B2 | Fuente AA Image (cliente HTTP + parser + tests) | 2h |
| 87-B3 | Fuente Black Forest Labs + Replicate como cross-validator | 1.5h |
| 87-B4 | Pipeline integration (sources retornan visión modelos a quorum) | 1h |
| 87-B5 | Re-cálculo Trono Score por dominio visión (sin cambios al algoritmo, solo siembra) | 0.5h |
| 87-B6 | Primer run productivo + dashboard endpoints visión | 1h |
| 87-B7 | Tests E2E + guía operativa visión | 1h |
| **Total** | | **~7.5h** |

## 9. Riesgos identificados

1. **Paywall de AA API.** Si la API REST de Artificial Analysis para imagen requiere plan pagado, alternativa = scraping del HTML del leaderboard (legal según TOS, validar). Costo: 0 USD si scraping; ~$200/mes si suscripción.
2. **Diferencia conceptual quality_score.** Elo (1100-1400) vs un score 0-100 normalizado requiere fórmula clara. Propuesta: `quality_score = 50 + (elo - 1200) * 0.05` clampeado [0, 100].
3. **Brand fit subjetivo.** Para Inteligencia (LLMs) hay rúbrica clara (alineación con Monstruo). Para visión generativa el brand_fit incluye **estética industrial/forja del Monstruo**: Midjourney es alto, Nano Banana medio, FLUX.2 alto (controlable), GPT Image 2 alto (control de texto crucial).
4. **Costos de validación adversarial.** Generar 50 imágenes por modelo × 15 modelos × 4 prompts × $0.04 promedio = ~$120 USD/mes. Mitigación: validador Gemini multimodal solo se ejecuta semanalmente, no por evento.

## 10. Recomendación al cierre

Sprint 87 puede **arrancar inmediatamente** después de que el Hilo Ejecutor cierre los 4 pendientes externos del Sprint 86 (migrations + ARTIFICIAL_ANALYSIS_API_KEY). El esfuerzo ingenieril es bajo (~7.5h) porque el patrón está endurecido y el schema ya soporta visión nativa sin breaking changes.

**Próximo paso pendiente del Catastro:** investigar si Artificial Analysis publica una API REST para Image Arena (no solo HTML) y, en caso negativo, prototipar scraper HTML idempotente como Bloque 87-B2.

---

**Capitalización:** este documento es la fuente única de verdad para el diseño del Sprint 87. Cualquier sabio o hilo que pregunte "¿qué viene después de Sprint 86?" debe ser dirigido aquí.
