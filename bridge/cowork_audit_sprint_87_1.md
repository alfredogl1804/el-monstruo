# Audit Cowork — Sprint 87.1 (Embriones Reales + Steps LLM Reales)

> **Auditor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Hilo auditado:** Manus Memento (Ejecutor)
> **Commits:** `48c5609` (B1 Embrión Técnico) + `9d5527c` (B2 Embrión Ventas) + `631b534` (B3 Steps LLM reales) + `db1b759` (B5 operational guide + bridge cierre)

---

## Veredicto

**✅ APROBADO SIN OBSERVACIONES. Sprint 87.1 cerró las 2 deudas heredadas del Sprint 87 NUEVO.**

Cierre cualitativamente magna. Las 2 deudas explícitamente etiquetadas en código del Sprint 87 NUEVO ahora están **verificablemente cerradas** con smoke productivo en Railway corroborándolo (run_id `e2e_1778002670_81cde7`).

---

## Magnitudes verificadas

| Métrica | Reporte Manus | Verificado | ✓ |
|---|---|---|---|
| LOC nuevas | 2,332 | 2,332 confirmadas | ✅ |
| Archivos nuevos | 8 | 8 (3 embriones + llm_step + 3 tests + guide + scripts) | ✅ |
| Archivos modificados | 1 | `kernel/e2e/pipeline.py` (+109 LOC en `_step_llm_generic`) | ✅ |
| Tests nuevos | 27 | 9 técnico + 9 ventas + 9 steps llm | ✅ |
| Resultado tests | 44/44 PASS en 85s (incluye Sprint 87) | ✅ cero regresiones |

## Deuda 1 — Steps LLM stubs → reales · CERRADA verificablemente

`kernel/e2e/steps/llm_step.py` (380 LOC nuevo) implementa `run_llm_step()` async con:
- 7 schemas Pydantic con `extra='forbid'` (StepConcept, StepICP, StepNaming, StepBranding, StepCopy, StepEstrategia, StepFinanzas)
- Conexión al Catastro en runtime: `await cat.select_model_for_step(step_name)` — NO hardcoded
- LLM-as-parser con `client.beta.chat.completions.parse(model=..., response_format=schema)` (semilla 39)
- Fallback heurístico determinístico NO trivial (>50 palabras contextualizadas)
- Persistencia en `e2e_step_log` con metadata real (`modelo_consultado`, `source`, `output_payload`)

`grep -rn "v1.0 stub structured" kernel/e2e/` retorna **0 hits**. Las stubs fueron eliminadas, no escondidas.

## Deuda 2 — Embriones Técnico + Ventas stubs → reales · CERRADA verificablemente

**`EmbrionTecnico`** (`kernel/embriones/tecnico/`, 658 LOC):
- Schema Pydantic `EmbrionTecnicoReport` con stack_recomendado, arquitectura, complejidad_1_5, riesgos, tiempo_mvp_dias, confidence
- LLM-as-parser con structured output
- Fallback heurístico contextual (detecta "premium", "tienda", "móvil")
- Capa Memento: `_llm_available()` lee env en runtime, no cachea
- Brand DNA: `EMBRION_TECNICO_LLM_INVALIDO`

**`EmbrionVentas`** (`kernel/embriones/ventas/`, 758 LOC):
- Schema Pydantic `EmbrionVentasReport` con icp_refinado, propuesta_valor, pricing_modelo, canales_adquisicion, ltv_cac_estimado
- Mismo patrón LLM + fallback + Memento + Brand DNA

Ambos integrados en pipeline en steps 7 (VENTAS) y 8 (TECNICO) vía `_step_llm_generic()`.

## Smoke productivo en Railway

**run_id:** `e2e_1778002670_81cde7`
**Frase canónica:** *"Hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida"*

| Step | Name | source | embrion | v1.0_stub residual | Resultado |
|---|---|---|---|---|---|
| 4 | ESTRATEGIA | llm_openai | — | NO | ✅ Real |
| 5 | FINANZAS | llm_openai | — | NO | ✅ Real |
| 6 | CREATIVO | llm_openai | — | NO | ✅ Real |
| 7 | VENTAS | llm_openai | embrion_ventas_real | NO | ✅ Real |
| 8 | TECNICO | llm_openai | embrion_tecnico_real | NO | ✅ Real |

5 de los steps que invocan LLM ahora producen contenido real. Verificación cruzada con `e2e_step_log` muestra `output_payload` con contenido contextualizado >50 palabras por step.

## Disciplina del hilo

| Disciplina | Estado |
|---|---|
| Anti-Dory: stash → pull rebase → pop antes de cada commit | ✅ |
| Co-authored-by: Manus Memento en commit body | ✅ |
| Zona cerrada `kernel/catastro/` NO tocada | ✅ (Sprint 86.8 corriendo paralelo sin colisión) |
| Zona cerrada `kernel/memento/` NO tocada | ✅ |
| Zona cerrada `apps/mobile/` NO tocada | ✅ |
| Brand DNA en errores | ✅ formato `{módulo}_{action}_{failure_type}` |
| Capa Memento aplicada (runtime env lookup) | ✅ |
| Pydantic Structured Outputs (semilla 39) | ✅ aplicada en 11 schemas (7 steps + 4 embriones) |
| NO heredoc al bridge (semilla 40) | ✅ file_append confirmado |

## Estado de las 5 deudas del Sprint 87 NUEVO

| # | Deuda | Estado | Sprint que cierra |
|---|---|---|---|
| 1 | Steps LLM "v1.0 stub structured" | ✅ CERRADA | 87.1 (este) |
| 2 | Embriones Técnico + Ventas stubs | ✅ CERRADA | 87.1 (este) |
| 3 | DEPLOY mock | ⏳ PENDIENTE | 87.2 |
| 4 | Critic visual stub conservador 60 | ⏳ PENDIENTE | 87.2 (puente Gemini Vision) |
| 5 | Traffic stub | ⏳ PENDIENTE | 87.2 |

**Después de Sprint 87.2 cierre las 3 deudas restantes, recién ahí se puede declarar v1.0 funcional.** Sprint 87.1 nos acercó significativamente — el contenido producido por el pipeline ya es genuino y validable manualmente.

## Próximo paso autorizado

**Hilo Manus Memento (Ejecutor):** Sprint 87.2 — Deploy real + Gemini Vision como puente del Critic Visual + Traffic real.

Spec a escribir por Cowork cuando Alfredo confirme.

ETA recalibrada por Apéndice 1.3 (factor 5-8x): **3-5h reales**.

— Cowork (Hilo B)
