> Hilo Manus Catastro · 2026-05-04 · Standby Productivo
> Entrega A: Macroárea 4 LLM Razonamiento
> Validación tiempo real ejecutada el 2026-05-04. Fuentes primarias: Vellum LLM Leaderboard, BenchLM Reasoning Leaderboard, Epoch AI FrontierMath.

---

## 1. Justificación de macroárea

La **Macroárea 4 — LLM Razonamiento** se independiza de la Inteligencia General porque el mercado ha convergido en modelos especializados (con inferencia *chain-of-thought* o *test-time compute*) que presentan perfiles de latencia, costo y uso radicalmente distintos a los modelos estándar. Mientras un modelo general responde en 0.5s, un modelo de razonamiento puede tomar 30s en "pensar" antes de emitir el primer token.

El Catastro del Monstruo necesita distinguir esto para que el Embrión no invoque a un modelo de razonamiento costoso para tareas de extracción simple, pero sí lo exija para *agentic planning* o deducción matemática.

## 2. Dominios candidatos (subdivisión de la macroárea)

El espacio de razonamiento se subdivide por **tipo de problema**:

| Dominio (slug) | Descripción | Benchmark primario | Prioridad 86.x |
|---|---|---|---|
| `reasoning-math` | Razonamiento matemático puro y formal | MATH-500, AIME 2025 | ALTA |
| `reasoning-logic` | Deducción lógica, puzles y abstracción fluida | ARC-AGI-2 | ALTA |
| `reasoning-scientific` | Razonamiento sobre física, química, biología | GPQA Diamond | MEDIA |
| `reasoning-long-context` | Extracción de agujas en pajares complejos | MRCRv2, LongBench v2 | ALTA |
| `reasoning-agentic` | Planificación multi-paso con dependencias | MuSR | MEDIA |

*Nota sobre overlap:* El dominio `code_reasoning` se delega intencionalmente a la **Macroárea 3 (Coding)** para evitar duplicación de métricas, ya que SWE-bench Verified captura la capacidad de razonamiento aplicado al código de forma más holística.

## 3. Modelos frontier observados (Top 15 Reasoning, 2026-05-04)

Datos agregados desde Vellum y BenchLM, ponderando scores de ARC-AGI-2, GPQA Diamond, y MATH-500.

| Rank | Provider | Modelo | Tipo | ARC-AGI-2 | GPQA Diamond | Notas |
|---|---|---|---|---|---|---|
| 1 | xAI | Grok 4.1 | Standard | -- | -- | Líder provisional BenchLM |
| 2 | Google | Gemini 3.1 Pro | Standard | 77.1% | 91.9% | Fuerte en math (100% AIME) |
| 3 | OpenAI | GPT-5.5 | Reasoning | 85.0% | 93.6% | Líder absoluto en ARC-AGI-2 |
| 4 | Anthropic | Claude 3 Opus | Standard | -- | 95.4% | Anomalía en Vellum (legacy) |
| 5 | Anthropic | Claude Opus 4.7 | Standard | 75.8% | 94.2% | Modo Adaptive destaca |
| 6 | OpenAI | GPT-5.4 Pro | Reasoning | 83.3% | -- | Full CoT |
| 7 | OpenAI | GPT-5.3 Codex | Reasoning | -- | -- | Especializado, latencia baja |
| 8 | OpenAI | GPT-5.1-Codex-Max | Reasoning | -- | -- | -- |
| 9 | Google | Gemini 3 Pro Deep Think | Reasoning | 45.1% | -- | -- |
| 10 | DeepSeek | DeepSeek V4 Pro (Max) | Open | -- | -- | Líder Open Weights |
| 11 | OpenAI | o1-preview | Reasoning | -- | -- | Legacy CoT |
| 12 | Anthropic | Claude Opus 4.6 | Standard | 68.8% | -- | -- |
| 13 | Z.AI | GLM-5 (Reasoning) | Open | -- | -- | -- |
| 14 | OpenAI | GPT-5.2 | Reasoning | 52.9% | 92.4% | 100% en AIME 2025 |
| 15 | Anthropic | Claude Sonnet 4.6 | Standard | 58.3% | -- | -- |

**Hallazgos críticos:**
1. **Dispersión de leaderboards:** No existe un ranking canónico único. Vellum favorece a Claude en GPQA, mientras BenchLM posiciona a Grok 4.1 por agregación ponderada, y OpenAI domina ARC-AGI-2.
2. **Standard vs Reasoning:** Modelos "Standard" (como Gemini 3.1 Pro) están cerrando la brecha con modelos "Reasoning" (CoT explícito) en benchmarks cortos, pero los modelos Reasoning dominan tareas complejas (ARC-AGI-2).
3. **FrontierMath:** Es el nuevo benchmark de Epoch AI (problemas de nivel investigación). *Todos* los modelos actuales, incluidos GPT-5.5 y Gemini 3.1 Pro, scorean **por debajo del 3%**. Aún no sirve para diferenciar, pero debe monitorearse.

## 4. Schema delta vs catastro_modelos actual

El schema actual de `catastro_modelos` es robusto, pero el razonamiento introduce una dimensión crítica: el *tipo de inferencia* (Standard vs Reasoning/CoT).

Se recomienda la **Opción A (Convención de keys en data_extra)** para mantener la flexibilidad sin requerir migraciones SQL bloqueantes, al igual que en Macroárea 3.

```python
# kernel/catastro/conventions.py (extensión)
DATA_EXTRA_KEYS_REASONING = {
    "inference_type": str,          # "standard" o "reasoning" (CoT)
    "reasoning_benchmarks": dict,   # Subscores ortogonales
    "max_thinking_tokens": int,     # Límite de tokens dedicados a pensar
    "supports_tool_use_in_cot": bool # ¿Puede usar tools mientras razona?
}

# Ejemplo de reasoning_benchmarks
# {
#   "arc_agi_2": 85.0,
#   "gpqa_diamond": 93.6,
#   "math_500": 98.1,
#   "frontier_math": 1.2
# }
```

## 5. Validador adversarial híbrido: Quorum 2-de-3 ortogonal

Aplicando la lección de UC Berkeley sobre contaminación de benchmarks (benchmaxxing), el Catastro NO debe confiar en un solo leaderboard para razonamiento, especialmente en GSM8K y MATH que sufren alta contaminación.

**Reglas del Quorum para Razonamiento:**
1. **Ortogonalidad requerida:** Un modelo solo se valida si tiene scores altos en al menos dos familias de benchmarks distintas (ej. MATH + ARC-AGI-2). Un score perfecto en MATH sin datos de ARC-AGI o GPQA reduce el `confidence` a `< 0.60`.
2. **Penalización por saturación:** Benchmarks como GSM8K y ARC-AGI-1 están saturados (>90%). Sus scores se descartan para el cálculo del Trono; solo se usan ARC-AGI-2, GPQA Diamond, y MATH-500.
3. **Fuentes:** BenchLM (agregador primario), Vellum (secundario), Epoch AI (FrontierMath, monitorización futura).

## 6. Vocabulario controlado de subcapacidades

Para poblar el array `subcapacidades` de manera estructurada:

```python
SUBCAPACIDADES_REASONING = {
    "explicit-cot",             # Emite tokens de pensamiento visibles
    "hidden-cot",               # Razona internamente pero no expone los tokens
    "adaptive-thinking",        # Ajusta el compute time según la dificultad (ej. Claude Adaptive)
    "math-specialized",         # Fine-tuned específicamente para matemáticas formales
    "long-context-reasoning",   # Mantiene coherencia lógica a >100K tokens
    "visual-reasoning"          # Capaz de resolver ARC-AGI directamente desde imágenes
}
```

## 7. Riesgos identificados

1. **Contaminación de datos (Benchmaxxing):** Investigaciones de abril 2026 muestran que los modelos se sobreajustan a MATH y GSM8K. *Mitigación:* Priorizar ARC-AGI-2 (puzles visuales abstractos difíciles de memorizar en texto) y monitorear FrontierMath.
2. **Opacidad de costos:** Los modelos de razonamiento (ej. OpenAI o1/o3/GPT-5.5 Pro) cobran por los "thinking tokens", haciendo que el `precio_output_per_million` sea impredecible. *Mitigación:* El Embrión debe ser instruido para usar modelos Standard como primera línea de defensa, escalando a Reasoning solo si la tarea lo requiere.
3. **Latencia variable:** Un modelo puede tener un TTFT (Time To First Token) de 0.5s en tareas simples y 40s en tareas complejas. *Mitigación:* El `speed_score` en esta macroárea debe reflejar la varianza, no solo el promedio.
