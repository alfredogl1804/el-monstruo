# Sprint 87.1 — Guía Operativa

**Cierre:** 2026-05-05 · **Hilo:** Manus Memento · **Estado:** ✅ VERDE PRODUCTIVO

## Qué cierra Sprint 87.1

Cierra **2 de las 5 deudas** del Sprint 87 NUEVO:

1. ✅ **Steps LLM reales** — los 5 steps (ESTRATEGIA/FINANZAS/CREATIVO/VENTAS/TECNICO) ya NO devuelven `result: "v1.0 stub structured"`. Ahora invocan LLM real con structured outputs Pydantic.
2. ✅ **Embriones Técnico + Ventas reales** — `kernel/embriones/tecnico/` y `kernel/embriones/ventas/` con LLM-as-parser + fallback heurístico determinístico.

**Quedan abiertas para Sprint 87.2:**
- 🔴 Deploy real (hoy es mock)
- 🔴 Critic visual (sigue stub conservador score=60)
- 🔴 Traffic real (sigue stub `vigia_status=v1_stub_pending`)

## Arquitectura

### `kernel/e2e/steps/llm_step.py` (NUEVO, 380 LOC)

Runner genérico para steps LLM con **LLM-as-parser** (semilla 39):

```python
from kernel.e2e.steps.llm_step import (
    StepConceptOutput, StepICPOutput, StepNamingOutput,
    StepBrandingOutput, StepCopyOutput,
    StepEstrategiaOutput, StepFinanzasOutput,
    run_llm_step,
)

result = await run_llm_step(
    cat=catastro_client,
    step_name="ESTRATEGIA",
    schema=StepEstrategiaOutput,
    system_prompt="...",
    user_prompt="...",
    context={"frase_input": "...", "nombre_proyecto": "..."},
)
# → {modelo_elegido, output_payload, source, model_used, latency_ms, content}
```

**7 schemas Pydantic** con `extra='forbid'` para garantizar estructura estricta.

**Capa Memento aplicada:**
- Lookup de `OPENAI_API_KEY` en runtime (no en import time)
- Si la key existe → `client.beta.chat.completions.parse(model=catastro_choice, response_format=schema)`
- Si la key NO existe o falla la llamada → `_heuristic_fallback(schema, context)` produce contenido NO trivial determinístico (`>50` palabras body_copy, IDs no-genéricos)

**Brand DNA en errores:**
- `e2e_step_llm_call_failed` (no "internal server error")
- Logger structlog con campos `step_name`, `model_id`, `error`

### `kernel/embriones/tecnico/` y `kernel/embriones/ventas/` (NUEVOS)

Clases `EmbrionTecnico` y `EmbrionVentas` que producen reportes Pydantic:

- **EmbrionTecnicoReport**: `stack_recomendado`, `arquitectura`, `complejidad_1_5`, `riesgos[]`, `confidence`
- **EmbrionVentasReport**: `icp_refinado`, `propuesta_valor`, `pricing_modelo`, `canales_adquisicion[]`, `ltv_cac_estimado`

Ambos:
- Reciben `frase_input` + `brief` del architect
- Pydantic `extra='forbid'`
- Source = `llm_openai` o `heuristic_fallback`
- Method `analizar()` síncrono (se invoca con `asyncio.to_thread`)

### Pipeline E2E (`kernel/e2e/pipeline.py`)

`_step_llm_generic` ahora orquesta:

```
ESTRATEGIA → run_llm_step(StepEstrategiaOutput)
FINANZAS   → run_llm_step(StepFinanzasOutput)
CREATIVO   → run_llm_step(StepBrandingOutput)
VENTAS     → EmbrionVentas().analizar()
TECNICO    → EmbrionTecnico().analizar()
```

## Cómo correr smoke productivo

```bash
cd ~/el-monstruo
railway run bash scripts/_smoke_sprint871_e2e.sh
```

**Resultado esperado:**
- 12 steps en 4-7s (con OPENAI key) o ~3s (heurístico)
- Steps 4-8 con `source=llm_openai` (o `heuristic_fallback` si no hay key)
- Step 7 con `embrion=embrion_ventas_real`
- Step 8 con `embrion=embrion_tecnico_real`
- Step 10 (CRITIC) sigue stub → score=60 → `awaiting_judgment`
- POST judgment con score 85 → `completed`

## Tests

```bash
source .venv-test/bin/activate
python -m pytest tests/test_sprint871_*.py tests/test_sprint87_e2e.py
# → 44 passed in 85s
```

| Suite | Tests | Status |
|---|---|---|
| Sprint 87.1 B1 (Embrión Técnico) | 9 | ✅ |
| Sprint 87.1 B2 (Embrión Ventas) | 9 | ✅ |
| Sprint 87.1 B3 (Steps LLM reales) | 9 | ✅ |
| Sprint 87 E2E orchestrator | 17 | ✅ |
| **Total** | **44** | **✅** |

## Variables de entorno relevantes

| Variable | Valor en Railway | Uso |
|---|---|---|
| `OPENAI_API_KEY` | ✅ presente | LLM real en steps + embriones |
| `MONSTRUO_API_KEY` | ✅ presente | Auth en endpoints `/v1/e2e/*` |
| `E2E_CRITIC_THRESHOLD` | 80 (default) | Score mínimo para auto-completar |

## Brand DNA Compliance

- ✅ Errores: `e2e_step_llm_call_failed`, `embrion_tecnico_analyze_failed`, `embrion_ventas_analyze_failed`
- ✅ Naming: `EmbrionTecnico`, `EmbrionVentas`, `run_llm_step` (no "service", "handler")
- ✅ Output payloads tienen identidad (no `"TODO"`, no genéricos)
- ✅ Endpoints respetan `/v1/e2e/{action}` (no tocados en este sprint)

## Zonas tocadas

- ✅ `kernel/embriones/tecnico/` (NUEVO)
- ✅ `kernel/embriones/ventas/` (NUEVO)
- ✅ `kernel/e2e/steps/` (NUEVO)
- ✅ `kernel/e2e/pipeline.py` (modificado: `_step_llm_generic`)
- ✅ `tests/test_sprint871_*.py` (3 archivos NUEVOS)

## Zonas NO tocadas

- ❌ `kernel/catastro/*` (Sprint 86.8 corriendo en paralelo con Manus Catastro)
- ❌ `kernel/memento/*`
- ❌ `apps/mobile/*`
- ❌ `kernel/main.py` (sin cambios)

## Commits

| SHA | Descripción |
|---|---|
| `48c5609` | feat(sprint871-b1): Embrión Técnico real |
| `9d5527c` | feat(sprint871-b2): Embrión Ventas real |
| `631b534` | feat(sprint871-b3): Steps LLM reales conectados al Catastro |
| _por crear_ | docs(sprint871-b5): operational guide + bridge report |

## Smoke productivo verificado

`run_id=e2e_1778002670_81cde7` (2026-05-05 17:37 UTC):

| Step | source | embrion | stub_detected |
|---|---|---|---|
| 4 ESTRATEGIA | `llm_openai` | — | False |
| 5 FINANZAS | `llm_openai` | — | False |
| 6 CREATIVO | `llm_openai` | — | False |
| 7 VENTAS | `llm_openai` | `embrion_ventas_real` | **False** |
| 8 TECNICO | `llm_openai` | `embrion_tecnico_real` | **False** |

El "v1.0 stub" desapareció del pipeline. ✅
