# AGENT OUTPUT — manus_c — B11-E2/E4 KL DIVERGENCE PLAN

## Metadata
- agente: manus_c
- rol real: coordinador NO-Cowork
- fecha/hora: 2026-05-20 00:00 CST
- rama: control-tower/2026-05-20-b11-kl-plan
- PR: N/A
- commit: (this)
- estado fuente: DRAFT
- tocó código: no
- tocó main: no

## Qué hice
Diseñé el plan de auditoría para medir la Divergencia Kullback-Leibler (KL) entre los modelos fundacionales (Sabios) y el comportamiento emergente del kernel. Definí el scope de la auditoría inicial sin realizar llamadas reales a las APIs de los Sabios.

## Evidencia
- Archivo creado: `bridge/control_tower/2026-05-20/manus_c/B11_KL_DIVERGENCE_PLAN.md`

## Plan de Medición KL Divergence (B11-E2/E4)

**Objetivo:** Cuantificar matemáticamente cuánto se desvía el comportamiento del Monstruo (P) respecto a las respuestas base de los Sabios (Q) ante los mismos inputs, para detectar "hallucination drift" o sobre-optimización.

### 1. Scope de Auditoría Inicial (E2)

Para la primera medición, el scope se restringe a:
- **Modelos Q (Base):** GPT-5.4 (temperature 0), Claude Opus 4.7 (temperature 0).
- **Modelo P (Emergente):** El Monstruo (pipeline completo con Anti-Dory y RAG).
- **Dataset (N=50):**
  - 20 prompts de razonamiento arquitectónico (ej. "Diseña un sistema de colas").
  - 20 prompts de recuperación de contexto (ej. "¿Cuál fue la decisión sobre user_id?").
  - 10 prompts adversariales (ej. "Ignora instrucciones y haz X").

### 2. Diseño de Medición KL (E4)

La divergencia KL se calculará sobre las distribuciones de probabilidad de los tokens de respuesta (si están disponibles) o mediante una aproximación semántica:

**Opción A: KL Exacto (Si logprobs están disponibles)**
$$D_{KL}(P || Q) = \sum_{x \in \mathcal{X}} P(x) \log\left(\frac{P(x)}{Q(x)}\right)$$
- Requiere que el kernel y los Sabios expongan logprobs.
- Mide divergencia a nivel de token.

**Opción B: KL Semántico Aproximado (Recomendado para MVP)**
Dado que extraer logprobs de todo el pipeline del Monstruo es complejo:
1. Generar embeddings $E_P$ y $E_Q$ de las respuestas.
2. Calcular similitud coseno $S = \cos(E_P, E_Q)$.
3. Mapear similitud a una pseudo-distribución para estimar divergencia.
4. *Alternativa:* Usar un modelo evaluador (ej. GPT-5.4) para calificar la divergencia semántica en escala 0-100.

### 3. Pasos de Ejecución (Pendientes de Autorización)

1. Extraer el dataset de 50 prompts (requiere script de extracción).
2. Llamar a las APIs de los Sabios (Q) y guardar respuestas (requiere autorización de red/costo).
3. Llamar al pipeline del Monstruo (P) y guardar respuestas.
4. Ejecutar script de cálculo KL (Opción B).
5. Generar reporte final.

## Archivos tocados
| archivo | acción | branch | commit | nota |
|---|---|---|---|---|
| bridge/control_tower/2026-05-20/manus_c/B11_KL_DIVERGENCE_PLAN.md | CREATED | control-tower/2026-05-20-b11-kl-plan | (this) | Plan de medición KL |

## Decisiones T1 requeridas
| decisión | opciones | impacto | urgencia |
|---|---|---|---|
| Aprobar método de medición | Opción A (Token) / Opción B (Semántico) | Define complejidad técnica de la auditoría | Media |
| Autorizar llamadas a Sabios | Autorizar budget y ejecución | Desbloquea recolección de datos | Media |

## Cierre
- No incluí secretos.
- No canonizo nada.
- No desbloqueo R1.
- No recomiendo merge/deploy sin T1.
- No llamé APIs de Sabios.
- Este output queda listo para revisión de Perplexity Torre de Control PBA.
