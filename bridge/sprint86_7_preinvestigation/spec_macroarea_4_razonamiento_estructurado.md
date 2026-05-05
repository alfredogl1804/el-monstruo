# Sprint 86.7 — Catastro Macroárea 4 (Razonamiento Estructurado) · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Spec firmado, listo para arranque INMEDIATO en paralelo con Sprint 87 NUEVO E2E
> **Sprint asignado:** Hilo Manus Catastro
> **Dependencias:** Sprint 86.5 (Macroárea 3 Coding) + Sprint 86.6 (anti-gaming v2 cross-area)
> **NO colisiona con:** Sprint 87 NUEVO E2E (Ejecutor) ni Sprint 86.4.5 B2 Memento

---

## Política Cowork firmada

> **Mientras Alfredo está activo coordinando, ningún hilo Manus entra en standby.**
> Standby blando o duro = desperdicio de 50% de capacity sin justificación.
> Corolario: Sprint 86.7 arranca **en paralelo** con Sprint 87 sin esperar audit.

Esta decisión queda como **11ma decisión arquitectónica firmada viva** del proyecto.

---

## Contexto

El Catastro tiene 3 Macroáreas activas:
- **Macroárea 1 — Razonamiento general** (Artificial Analysis, OpenRouter, LMArena)
- **Macroárea 2 — Arena humana** (LMArena ranking)
- **Macroárea 3 — Coding** (SWE-bench, HumanEval+, MBPP+) ✅ Sprint 86.5

Falta una macroárea crítica para el funcionamiento del Sprint 87 E2E maduro: **Razonamiento Estructurado** — no es "razonamiento general" agregado, sino capacidad demostrable en tareas estructuradas con respuesta verificable (matemática, lógica formal, ciencias).

Macroárea 4 cubre 3 fuentes ortogonales:
- **AIME** (American Invitational Mathematics Examination) — matemática competitiva
- **GPQA Diamond** (Graduate-level Physics, Biology, Chemistry questions, ground-truth verifiable) — ciencias
- **MMLU-Pro** (Massive Multitask Language Understanding, versión Pro con 10 opciones) — conocimiento estructurado multidominio

## Objetivo del Sprint

Activar Macroárea 4 (Razonamiento Estructurado) en el Catastro con disciplina firme: 3 fuentes ortogonales + classifier con vocabulario controlado de 12 tags + anti-gaming v1 (intra-fuente threshold) + anti-gaming v2 cross-area (Macroárea 4 vs 1+2+3) reaprovechando el patrón del Sprint 86.6.

## Decisiones arquitectónicas firmes

### Decisión 1 — Reusar TODA la infraestructura del Sprint 86.5

NO se reescribe nada de:
- `kernel/catastro/sources/__init__.py` (registro)
- `kernel/catastro/coding_classifier.py` (patrón a copiar para `reasoning_classifier.py`)
- Pipeline integration con flag `CATASTRO_ENABLE_REASONING=true`
- Quorum 2-de-3 ortogonal (presencia, no valor)
- Anti-gaming v1+v2 patterns

Sprint 86.7 es **simétrico al Sprint 86.5** en estructura, distinto en contenido.

### Decisión 2 — 3 sources ortogonales (mismo patrón que coding)

| Fuente | Endpoint | Métrica | Anti-gaming v1 |
|---|---|---|---|
| AIME 2024+2025 | `https://benchlm.ai/api/v1/benchmarks/aime` | `accuracy` 0-100 | `aime_2024 >= aime_2025 + 10` → gaming (memorización) |
| GPQA Diamond | `https://benchlm.ai/api/v1/benchmarks/gpqa-diamond` | `accuracy` 0-100 | `gpqa_diamond > gpqa_main + 15` → gaming |
| MMLU-Pro | `https://benchlm.ai/api/v1/benchmarks/mmlu-pro` | `accuracy` 0-100 | `mmlu_pro > mmlu_basic + 20` → gaming |

### Decisión 3 — Classifier con vocabulario controlado de 12 tags

```
Áreas:        math-strong, physics-strong, chemistry-strong, biology-strong,
              logic-formal-strong, multidominio-strong
Estilos:      step-by-step-reasoning, chain-of-thought-strong, abstract-reasoning,
              quantitative-strong, structured-output-strong, anti-gaming-reasoning-verified
```

12 tags ortogonales al vocabulario coding (sin solapamiento).

### Decisión 4 — Anti-gaming v2 cross-area extendido

Reaprovechar el detector del Sprint 86.6:

```python
def detect_overfit_reasoning_cross_area(
    aime_score, gpqa_score, mmlu_score,
    coding_score,  # de Macroárea 3
    razonamiento_general,  # de Macroárea 1
    arena_rank  # de Macroárea 2
):
    """v2 cross-area para Razonamiento."""
    # Si reasoning-strong (al menos 1 de los 3 >= 70) pero coding bajo y arena rank > 50 → overfit
    # Patrón: modelos que "memorizan benchmarks de razonamiento" pero no aplican
```

Tag nuevo `reasoning-overfit-suspected` agregado al vocabulario (13to tag).

### Decisión 5 — Modo LLM con structured outputs Pydantic (semilla 39)

Mismo patrón que coding_classifier: `gpt-4o-mini` con response_format Pydantic, fallback heurístico determinístico si OPENAI_API_KEY ausente.

### Decisión 6 — Persistencia simétrica al coding

```python
data_extra.reasoning = {
    "aime_score": float,
    "gpqa_score": float,
    "mmlu_pro_score": float,
    "gaming_detected": bool,
    "overfit_suspected": bool,
    "overfit_evidence": dict,
    "classification": {
        "tags": [...],
        "primary_strength": str,
        "confidence": float,
        "reasoning": str
    }
}
```

### Decisión 7 — Capa Memento aplicada simétricamente

Operations registradas:
- `catastro_reasoning_source_fetch` (READ remoto)
- `catastro_reasoning_classify_run` (LLM call)
- `catastro_reasoning_persist` (WRITE Supabase)

## Bloques del Sprint

### Bloque 1 — 3 sources nuevas (45-60 min)
- `kernel/catastro/sources/aime.py`
- `kernel/catastro/sources/gpqa.py`
- `kernel/catastro/sources/mmlu_pro.py`
- Registro en `__init__.py`
- Anti-gaming v1 implementado en cada source con thresholds documentados

### Bloque 2 — Reasoning classifier (45-60 min)
- `kernel/catastro/reasoning_classifier.py` con vocabulario 12 tags
- Modo LLM (Structured Outputs Pydantic) + fallback heurístico
- Patrón calcado de `coding_classifier.py`

### Bloque 3 — Pipeline integration (30 min)
- Flag `CATASTRO_ENABLE_REASONING=true` (default OFF)
- `_enrich_with_reasoning()` en `pipeline.py`
- Quorum ortogonal (presencia en >= 2 de 3 fuentes)

### Bloque 4 — Anti-gaming v2 cross-area (30 min)
- `detect_overfit_reasoning_cross_area()` reaprovechando patrón Sprint 86.6
- Tag `reasoning-overfit-suspected` (13to tag) agregado al vocabulario
- Persistencia en `data_extra.reasoning.overfit_*`

### Bloque 5 — Tests + smoke (45-60 min)
- `tests/test_sprint867_reasoning.py` con ≥ 25 casos
  - 9 casos por source (3 sano, 3 gaming v1, 3 edge)
  - 5 casos classifier
  - 5 casos cross-area v2
  - 6 casos pipeline integration
- `scripts/_smoke_sprint867_reasoning.py` con 6 gates

### Bloque 6 — Bridge + reporte cierre (15-20 min)
- `bridge/REASONING_OPERATIONAL_GUIDE.md`
- Reporte de cierre en `bridge/manus_to_cowork.md` con `file_append` (NO heredoc — semilla 40 aplicada)

## ETA total recalibrada

6 bloques × ~40 min promedio = **3.5-5 horas reales**.

Si el patrón Sprint 86.5 → Sprint 86.6 se mantiene, podríamos ver cierre en **2.5-4h**.

## Métricas de éxito

| Métrica | Target |
|---|---|
| 3 sources Macroárea 4 production-ready | ✅ |
| Tests acumulados | ≥ 480 PASS |
| Suite Sprint 86.5 + 86.6 + 86.7 | regresión cero |
| Anti-gaming v1 en las 3 fuentes | ✅ |
| Anti-gaming v2 cross-area Reasoning vs (Coding + Razonamiento general + Arena) | ✅ |
| Vocabulario 12 + 1 = 13 tags Reasoning, ortogonal a 16 tags Coding | ✅ |
| Sin LLM hardcoded | ✅ |

## Disciplina obligatoria

- **Capa Memento:** preflight en source fetch + classify + persist
- **Brand DNA:** errores `catastro_reasoning_*_failed` formato canónico
- **Anti-Dory:** `stash → pull rebase → pop` antes de cada commit
- **Standby:** ninguno mientras Alfredo activo (política Cowork firmada hoy)
- **NO heredoc al bridge:** usar `file_append` o file write directo Python (semilla 40)
- **Vocabulario controlado:** validación whitelist en classifier
- **Structured Outputs Pydantic:** semilla 39 aplicada

## Zona primaria

```
kernel/catastro/sources/aime.py (nuevo)
kernel/catastro/sources/gpqa.py (nuevo)
kernel/catastro/sources/mmlu_pro.py (nuevo)
kernel/catastro/sources/__init__.py (registro de las 3 nuevas)
kernel/catastro/reasoning_classifier.py (nuevo)
kernel/catastro/pipeline.py (modificación quirúrgica para flag CATASTRO_ENABLE_REASONING)
scripts/_smoke_sprint867_reasoning.py (nuevo)
tests/test_sprint867_reasoning.py (nuevo)
bridge/REASONING_OPERATIONAL_GUIDE.md (nuevo)
```

## NO TOCÁS

- `kernel/catastro/coding_classifier.py` (zona Sprint 86.5/86.6, congelado)
- `kernel/catastro/sources/swe_bench.py`, `human_eval.py`, `mbpp.py` (Sprint 86.5)
- `kernel/catastro/schema.py` manual (zona pre-B2)
- `kernel/catastro/schema_generated.py` (zona pre-B2, regenerar solo si hay migration nueva)
- `kernel/memento/*` (zona Memento)
- `kernel/embriones/*` (zona Sprint 88)
- `kernel/e2e/*` (zona Sprint 87 NUEVO — colisionaría con Ejecutor)
- `kernel/guardian/*` (zona Sprint 89)
- `kernel/ventas/*`, `kernel/seo/*` (zonas futuras Sprints 90+91)

## Conexión cross-sprint

| Sprint | Cómo se conecta |
|---|---|
| Sprint 87 NUEVO E2E (Ejecutor en paralelo) | Patrón "consultar Catastro en runtime" — el pipeline E2E va a poder filtrar modelos por Macroárea 4 cuando este sprint cierre |
| Sprint 88 (Embriones colectivos) | Embrión Investigador puede usar Macroárea 4 para validar coherencia de razonamiento |
| Sprint 89 (Guardian Autónomo) | Métricas Macroárea 4 alimentan scoring Obj #2 (Calidad Apple/Tesla) |

## Próximo sprint después

Sprint 86.8 — Macroárea 5 (Visión y Multimodalidad) si aplica. O bien, integración cross-macroárea para producir un "Trono Score Compuesto" v2 que use 4 macroáreas en lugar de 3.

— Cowork (Hilo B)
