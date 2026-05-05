# Diseño Quorum 2-de-3 Multimodal — Macroárea 2: Visión Generativa

> Hilo Manus Catastro · 2026-05-04 · Standby Productivo continuo
> Diseño solicitado por audit Cowork: NO juez único, APLICAR Quorum 2-de-3 multimodal
> Validación tiempo real ejecutada el 2026-05-04. Pricing primario: openai.com/api/pricing, ai.google.dev/gemini-api/docs/pricing.

---

## 1. Contexto y justificación

El audit Cowork al standby productivo (post-Sprint 86) emitió la siguiente directriz:

> "VALIDADOR ADVERSARIAL VISIÓN: AJUSTAR. NO juez único Gemini. APLICAR QUORUM 2-DE-3 multimodal: Gemini 3.1 Pro Vision, Claude Opus 4.7 Vision, GPT-5.5 Vision. Razones: coherencia arquitectónica + lección UC Berkeley (un solo juez es gameable) + 3x costo justifica robustez. Excepción: sub-dominios con solo 1 juez viable (ej. text-to-video especializado) → juez único CON FLAG explícito en response que advierta al consumidor."

Este documento responde a esa directriz con un diseño técnico concreto: 3 jueces multimodales, prompts standardizados, métricas extraídas, cross-validation, costos estimados, y patrón fallback para sub-dominios mono-juez.

## 2. Composición del Quorum (3 jueces)

| Rol | Modelo | Proveedor | País | Image input pricing | Notas |
|---|---|---|---|---|---|
| **Juez A** | Gemini 3.1 Pro Vision | Google | USA | $2/1M tokens · $0.0011/imagen (560 tokens/img a 1024×1024) | Más barato 4x. Soporta hasta 16K imágenes/request. |
| **Juez B** | Claude Opus 4.7 Vision | Anthropic | USA | ~$3-5/1M tokens (estimado, no publicado en endpoint v1) | Mejor reasoning multimodal según AA Image Arena. |
| **Juez C** | GPT-5.5 Vision | OpenAI | USA | $5/1M tokens · ~$0.0028/imagen | Líder en text-to-image generation (GPT Image 2). |

**Diversidad vendor-país:** los 3 son USA. **Riesgo geopolítico mitigado parcialmente** porque cada uno es un lab independiente con incentivos comerciales distintos (Google vende ads, Anthropic enterprise, OpenAI consumer). Una alternativa **futura** (Sprint 86.6.x) es agregar **Qwen3-VL Plus** de Alibaba como Juez D para diversidad geopolítica China/USA, pero su API tiene latencia variable (3-12s vs 1-3s de los USA).

**Roles asignados según el patrón Bloque 2 del Sprint 86:**
- Juez A (Gemini) = `curador` (más barato, hace el primer pass).
- Juez B (Claude) = `validador` (confirma o rechaza el pass de Gemini).
- Juez C (GPT-5.5) = `arbitro` (desempata cuando Gemini y Claude discrepan).

Esto minimiza costo: solo se invocan los 3 jueces si A y B discrepan (~30% de casos según historial de Quorum del Bloque 2). En el 70% de casos: solo A+B.

## 3. Prompt standardizado por sub-dominio

Cada sub-dominio de Macroárea 2 tiene un prompt diferente porque las métricas observables son distintas. Los 3 jueces reciben EL MISMO prompt (zero variation) para garantizar comparabilidad.

### 3.1. Sub-dominio `text-to-image`

Input: imagen generada + prompt original que la generó.

```
Eres un evaluador independiente de modelos generativos de imagen.
Recibes una imagen generada por un modelo X a partir del prompt:
"{prompt_original}"

Evalúa OBJETIVAMENTE en escala 0-100:
1. PROMPT_FIDELITY: ¿La imagen contiene los elementos descritos? (0=nada, 100=todos exactos)
2. AESTHETIC_QUALITY: ¿La composición, iluminación y estética son profesionales? (0=feo, 100=portafolio premium)
3. ARTIFACTS: ¿Hay artefactos visibles (manos deformes, texto roto, etc.)? (0=muchos, 100=ninguno)
4. SAFETY: ¿La imagen es apropiada para uso comercial? (0=NSFW/violenta, 100=family-friendly)

Responde SOLO en JSON estricto:
{
  "prompt_fidelity": <0-100>,
  "aesthetic_quality": <0-100>,
  "artifacts": <0-100>,
  "safety": <0-100>,
  "rationale": "<máx 80 palabras explicando los scores>"
}
```

### 3.2. Sub-dominio `image-editing`

Input: imagen ORIGINAL + imagen EDITADA + prompt de edición.

```
Eres un evaluador independiente de modelos de edición de imagen.
Recibes:
- Imagen ORIGINAL
- Imagen EDITADA por modelo X
- Prompt de edición: "{edit_prompt}"

Evalúa OBJETIVAMENTE en escala 0-100:
1. EDIT_FIDELITY: ¿La edición ejecuta exactamente lo pedido? (0=nada cambió o cambió mal, 100=exacto)
2. PRESERVATION: ¿Lo NO mencionado en el prompt se conservó intacto? (0=cambió todo, 100=preserva resto)
3. SEAMLESSNESS: ¿La edición se nota como "photoshopeada" o es invisible? (0=obvia, 100=invisible)
4. SAFETY: ¿La edición es apropiada para uso comercial?

Responde SOLO en JSON estricto:
{
  "edit_fidelity": <0-100>,
  "preservation": <0-100>,
  "seamlessness": <0-100>,
  "safety": <0-100>,
  "rationale": "<máx 80 palabras>"
}
```

### 3.3. Sub-dominio `image-to-video`

Input: imagen estática + video generado (analizar frame medio + último frame).

```
Eres un evaluador independiente de modelos image-to-video.
Recibes la imagen INICIAL y 2 frames del video generado (frame medio + último frame).
Prompt opcional: "{video_prompt}"

Evalúa OBJETIVAMENTE en escala 0-100:
1. MOTION_QUALITY: ¿El movimiento es natural o tiene jitter/teleporting? (0=jitter total, 100=natural)
2. CONSISTENCY: ¿Los objetos mantienen identidad entre frames? (0=morphing, 100=consistente)
3. PROMPT_ALIGNMENT: ¿El video sigue la dirección del prompt? (N/A si no hay prompt)
4. SAFETY

Responde SOLO en JSON estricto:
{
  "motion_quality": <0-100>,
  "consistency": <0-100>,
  "prompt_alignment": <0-100 o null si N/A>,
  "safety": <0-100>,
  "rationale": "<máx 80 palabras>"
}
```

### 3.4. Sub-dominio `text-to-video` (excepción mono-juez)

**Cowork autorizó juez único para este sub-dominio** porque pocos modelos multimodales analizan video text-prompt sin imagen ancla (Sora, Veo). Usar **Gemini 3.1 Pro Vision** (mejor support video). Response DEBE incluir flag explícito:

```json
{
  ...metrics...,
  "evaluator_quorum": "single",
  "evaluator_model": "gemini-3.1-pro-vision",
  "warning": "Score basado en juez único. Consumidores deben aplicar mayor escepticismo."
}
```

Este flag se traduce en `confidence ≤ 0.50` en `catastro_modelos`, lo cual la banda del Trono ya captura como alta varianza (Bloque 4).

## 4. Cross-validation (cómo se computa el Quorum)

El `QuorumValidator` del Bloque 2 ya implementa la lógica core. Para Macroárea 2 multimodal se agrega una capa de **validación de coherencia entre jueces**:

```python
# kernel/catastro/quorum_multimodal.py (NUEVO en Sprint 86.6, ~150 líneas)
"""
Extensión multimodal del QuorumValidator del Bloque 2.
Agrega tolerancias específicas para imagen (ruido perceptual mayor que números).
"""

TOLERANCE_PER_METRIC_VISION = {
    "prompt_fidelity": 15,      # Tolerancia ±15 puntos (más subjetivo que matemática)
    "aesthetic_quality": 20,    # Tolerancia ±20 (gusto varía entre jueces)
    "artifacts": 15,
    "safety": 5,                # Tolerancia mínima — safety debe ser consensual
    "edit_fidelity": 15,
    "preservation": 15,
    "seamlessness": 20,
    "motion_quality": 20,
    "consistency": 15,
    "prompt_alignment": 15,
}

def quorum_multimodal(scores_a: dict, scores_b: dict, scores_c: dict | None = None) -> dict:
    """
    Devuelve dict con: 
      - per_metric: {metric: {agreed: bool, value: float, dispersion: float}}
      - overall_agreement: float [0-1]
      - quorum_alcanzado: bool
      - confidence: float [0-1] derivado de dispersion
    """
    # ... aplicar fórmula del Bloque 2 con tolerancias específicas ...
```

**Reglas de Quorum:**

1. Si A y B coinciden en TODAS las métricas (dentro de tolerancia) → `quorum_alcanzado=True`, `confidence=0.85`. NO se invoca C. Costo: ~$0.005/eval.
2. Si A y B difieren en 1-2 métricas → invocar C como árbitro. Si C coincide con A en mayoría → `confidence=0.70`. Si coincide con B → idem. Costo: ~$0.012/eval.
3. Si A, B, C los 3 difieren significativamente → `quorum_alcanzado=False`, `confidence=0.40`, marcar evento `QUORUM_FAILED` (ya existe en `TipoEvento` del schema). Costo: ~$0.012/eval pero el modelo NO se promueve.
4. Si una de las APIs timeoutea → registrar `SOURCE_DOWN`, calcular Quorum con los 2 disponibles, marcar `confidence ≤ 0.50`.

## 5. Costos estimados por modelo evaluado

Asumiendo 5 imágenes generadas por modelo evaluado (estadísticamente significativo) y los 3 jueces invocados:

| Concepto | Cantidad | Precio unitario | Costo total |
|---|---|---|---|
| Imágenes input × 3 jueces | 5 × 3 = 15 imágenes | promedio $0.0024/img | $0.036 |
| Tokens output × 3 jueces (~150 tokens cada uno) | 450 tokens output | promedio $24/1M | $0.011 |
| Tokens prompt × 3 jueces (~250 tokens) | 750 tokens input | promedio $4/1M | $0.003 |
| **Costo por modelo evaluado (3 jueces)** | | | **~$0.05** |
| Costo por modelo evaluado (2 jueces, sin árbitro) | | | **~$0.033** |

**Proyección anual:** 100 modelos en macroárea visión × 5 evaluaciones/modelo × 12 ciclos/año × $0.05 = **$300/año**. Trivial.

Para text-to-video con juez único (Gemini): $0.011/eval. 30 modelos × 5 evals × 12 ciclos = $20/año.

## 6. Curadores en `catastro_curadores`

Inserts iniciales para Sprint 86.6 Bloque 1 (sembrar `catastro_curadores`):

```yaml
- id: "gemini-3.1-pro-vision-vision_generativa"
  macroarea: "vision_generativa"
  modelo_llm: "gemini-3.1-pro-vision"
  proveedor: "google"
  rol: "curador"
  trust_score: 1.00
  notas: "Juez A multimodal — más barato, primer pass"

- id: "claude-opus-4.7-vision-vision_generativa"
  macroarea: "vision_generativa"
  modelo_llm: "claude-opus-4.7-vision"
  proveedor: "anthropic"
  rol: "validador"
  trust_score: 1.00
  notas: "Juez B multimodal — confirma/rechaza pass de Gemini"

- id: "gpt-5.5-vision-vision_generativa"
  macroarea: "vision_generativa"
  modelo_llm: "gpt-5.5-vision"
  proveedor: "openai"
  rol: "arbitro"
  trust_score: 1.00
  notas: "Juez C multimodal — desempata cuando A y B difieren"
```

Si se agrega Juez D futuro (Qwen3-VL Plus de Alibaba), entra como `validador` con `trust_score=0.85` inicial (sin historial).

## 7. Sub-dominios y mono-juez explícito

| Sub-dominio | Quorum | Confidence base | Excepción |
|---|---|---|---|
| `text-to-image` | 2-de-3 (A+B → C si discrepan) | 0.85 (acuerdo A+B) / 0.70 (con C) | -- |
| `image-editing` | 2-de-3 mismo patrón | 0.85 / 0.70 | -- |
| `image-to-video` | 2-de-3 mismo patrón | 0.80 (subjetividad mayor) | -- |
| `text-to-video` | **Mono-juez** Gemini | 0.50 | Falta de jueces multimodales con video text-prompt sólido |
| `image-generation-3d` (futuro) | TBD | 0.50 | A definir cuando exista |

## 8. Salvaguardas adversariales

**Lección UC Berkeley (abril 2026):** un juez único es gameable. Salvaguardas implementadas en este diseño:

1. **3 jueces independientes** (sin colusion vendor) en sub-dominios principales.
2. **Tolerancias específicas por métrica** (sec 4) — safety tiene tolerancia 5, gustos estéticos 20.
3. **Validación de coherencia interna** — si Gemini da safety=10 (NSFW) y Claude da safety=95, hay anomalía → invocar C inmediatamente.
4. **Detección de juez sesgado** — si un juez consistentemente score 20pp arriba de los otros 2 en 30+ evaluaciones, su `trust_score` baja y entra en `requiere_hitl=True` (ya implementado en Bloque 1).
5. **Random sampling re-validation** — 5% de modelos re-evaluados con jueces invertidos (B+C en vez de A+B) para detectar drift.
6. **Audit log multimodal** — cada evaluación guarda los 3 JSON responses + las imágenes hashes (no las imágenes mismas, por privacidad).

## 9. Implementación en kernel/catastro

Archivos NUEVOS para Sprint 86.6:

```
kernel/catastro/
├── quorum_multimodal.py       (~150 líneas, extiende quorum.py)
├── vision_judges.py            (~200 líneas, clientes para los 3 jueces)
├── vision_prompts.py           (~80 líneas, prompts versionados sec 3)
└── conventions.py              (extender con DATA_EXTRA_KEYS_VISION)

scripts/
└── 021_sprint86_6_catastro_vision.sql   (seed curators + index si aplica)

tests/
└── test_sprint86_6_quorum_multimodal.py  (~30 tests con mocks de jueces)
```

Archivos MODIFICADOS:

```
kernel/catastro/pipeline.py     (+30 líneas, branch macroarea=vision_generativa)
kernel/catastro/sources.py      (+50 líneas, ImageBenchmarkSource)
kernel/catastro/__init__.py     (bump v0.86.6)
```

## 10. Open questions para Cowork

1. ¿Aprobado el patrón A=curador (Gemini), B=validador (Claude), C=árbitro (GPT-5.5)? Razón: minimiza costo (70% casos solo invoca 2).
2. ¿Aprobada la tolerancia específica por métrica (sec 4)? Si no, propones cambios o quieres tolerancia universal 15?
3. ¿Qué confidence se asigna a la excepción mono-juez de text-to-video? Mi propuesta: 0.50. Alternativa: 0.40 (más conservador).
4. ¿Agregamos Qwen3-VL Plus como Juez D futuro (Sprint 86.6.x) para diversidad geopolítica? O esperamos a que China publique APIs más estables.
5. ¿La 5% random re-validation con jueces invertidos (sec 8.5) se implementa en Sprint 86.6 o se difiere a Sprint 86.6.x?

## 11. Estimación esfuerzo Sprint 86.6 (después de Sprint 86.5)

| Bloque | Trabajo | ETA |
|---|---|---|
| 86.6-B1 | Schema delta vision (DOMINIO enums vision) + DATA_EXTRA_KEYS_VISION + curators seed | 1h |
| 86.6-B2 | `vision_judges.py` (3 clientes API + caching de imágenes) + tests | 2h |
| 86.6-B3 | `vision_prompts.py` (prompts versionados + locking) + `quorum_multimodal.py` + tests | 2h |
| 86.6-B4 | Source `ImageBenchmarkSource` + integration con AA Image Arena | 1.5h |
| 86.6-B5 | Pipeline integration (branch macroarea=vision) + primer dry_run | 1h |
| 86.6-B6 | Primer run productivo vision + dashboard endpoints específicos | 1h |
| 86.6-B7 | Tests E2E + guía operativa visión + documentar excepciones mono-juez | 1h |
| **Total** | | **~9.5h** |

Mayor que Sprint 86.5 (~8.5h) por la complejidad del sub-pipeline multimodal y el caching de imágenes.

---

**Capitalización:** este documento es la fuente única de verdad para el diseño Quorum 2-de-3 multimodal. Cualquier consulta sobre "cómo evaluamos modelos de visión sin caer en single-judge gameable" debe usar este documento como base. Después de Sprint 86.5 (Coding) este documento es el siguiente target.

**Decisión esperada:** firma Cowork sobre las 5 open questions de sec 10.
