# Sprint 87.1 — Embriones Reales + Steps LLM Reales · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Spec firmado, listo para arranque inmediato post-audit Sprint 87 NUEVO
> **Sprint asignado:** Hilo Manus Memento (Ejecutor)
> **Dependencias:** Sprint 87 NUEVO cerrado (commits `2e0b2a5` + `005ddf7`)
> **Cierra:** 2 de las 5 deudas etiquetadas en Sprint 87 NUEVO; avanza hacia v1.0 funcional declarable

---

## Contexto

Sprint 87 NUEVO cerró **v1.0 estructural** del pipeline E2E. Las 5 deudas etiquetadas en código son la diferencia entre estructural y funcional. Sprint 87.1 cierra **2 de las 5**, las que producen contenido real:

1. **Steps LLM stubs → reales:** los 5 steps que invocan LLM hoy registran qué modelo eligieron del Catastro pero NO llaman al modelo real ni reciben contenido. Sprint 87.1 los conecta de verdad.
2. **Embriones Técnico + Ventas stubs → reales:** los 2 Embriones que faltan implementar para que el pipeline tenga análisis estratégico completo.

Las otras 3 deudas (deploy real, critic visual real, traffic real) caen en Sprint 87.2.

## Objetivo del Sprint

Cuando Sprint 87.1 cierre, una frase de Alfredo va a producir contenido REAL en cada step (concept, ICP, naming, branding, copy con LLM real respondiendo según el Catastro), pasando por todos los Embriones reales (incluyendo Técnico y Ventas). El output sigue siendo mock deploy con stub critic — pero el contenido producido es genuino y validable manualmente.

## Decisiones arquitectónicas firmes

### Decisión 1 — Steps LLM conectados al Catastro en runtime, sin hardcodeo

Cada step que necesita LLM:
1. Llama a `catastro_service.choose_model(task=step_name, sensitivity=...)` en runtime
2. Recibe el modelo elegido + endpoint + credentials
3. Hace el call real al LLM con prompt estructurado
4. Parsea respuesta con Pydantic Structured Outputs (semilla 39)
5. Persiste resultado en `e2e_step_log`

NO se hardcodea modelo en código. Si el Catastro está down, fallback a modelo default registrado.

### Decisión 2 — Embrión Técnico real

Responsabilidad: análisis técnico del concepto recibido del intake.
- Stack tech recomendado (frontend, backend, hosting, deploy)
- Complejidad estimada (1-5)
- Riesgos técnicos detectados
- Output: `EmbrionTecnicoReport` Pydantic

Modo Memento: lee `OPENAI_API_KEY` (o equivalente del Catastro) en runtime, fallback heurístico determinístico si no hay key.

### Decisión 3 — Embrión Ventas real

Responsabilidad: análisis de viabilidad comercial.
- ICP refinado del intake
- Propuesta de valor sintetizada
- Pricing tentativo
- Canales de adquisición sugeridos
- Output: `EmbrionVentasReport` Pydantic

### Decisión 4 — Steps que se conectan al Catastro

| Step | Tarea | Tier de sensibilidad |
|---|---|---|
| concept_generation | Genera concepto inicial | cloud_anonymized_ok |
| icp_definition | Define ICP | cloud_anonymized_ok |
| naming | Genera 5 nombres candidatos | cloud_only OK (no hay datos personales) |
| branding | Tono, colores, voice | cloud_only OK |
| copy_generation | Hero, body, CTAs | cloud_only OK |

Los 5 steps reciben contexto del intake + outputs de steps previos.

### Decisión 5 — Capa Memento aplicada

Preflight obligatorio en cada call a LLM externo:
- Operation: `e2e_step_llm_call`
- Validación: prompt no contiene PII no anonimizada
- Validación: modelo elegido tiene `confidentiality_tier` apropiado (cuando Sprint 86.8 se cierre, este check se vuelve más estricto)

### Decisión 6 — Tests + smoke productivo

Tests unitarios:
- Cada step LLM con mock del Catastro + mock LLM call
- Embrión Técnico + Ventas con casos sintéticos (3 cada uno)
- Pipeline E2E con LLMs reales activados (con OPENAI_API_KEY válida)

Smoke productivo:
- Misma frase canónica de Sprint 87 (*"Hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida"*)
- Verificar que cada step produce contenido NO trivial (longitud > 50 palabras, no es "lorem ipsum", no es respuesta vacía)
- Verificar que Embriones Técnico + Ventas devuelven JSON válido con schema esperado

## Bloques del Sprint

### Bloque 1 — Embrión Técnico real (45-60 min)
- `kernel/embriones/tecnico/embrion_tecnico.py`
- `EmbrionTecnicoReport` Pydantic schema
- Tests con 3 casos sintéticos
- Capa Memento integrada

### Bloque 2 — Embrión Ventas real (45-60 min)
- `kernel/embriones/ventas/embrion_ventas.py`
- `EmbrionVentasReport` Pydantic schema
- Tests con 3 casos sintéticos
- Capa Memento integrada

### Bloque 3 — Steps LLM conectados (60-90 min)
- 5 steps modificados (concept, ICP, naming, branding, copy)
- Conexión real al Catastro en runtime
- Pydantic Structured Outputs (semilla 39 reaplicada)
- Persistencia en `e2e_step_log` con metadata real (modelo elegido, tokens consumidos, latencia)

### Bloque 4 — Smoke productivo + tests E2E (30-45 min)
- Tests E2E con LLMs reales (gated por env var `E2E_REAL_LLM_TESTS=true`)
- Smoke productivo con frase canónica
- Verificación de contenido NO trivial

### Bloque 5 — Bridge + reporte cierre (15-20 min)
- `bridge/SPRINT_87_1_OPERATIONAL_GUIDE.md`
- Reporte cierre en `bridge/manus_to_cowork.md` con file_append (NO heredoc)
- Quitar etiquetas de stubs en código (las 2 deudas cerradas dejan de ser stubs)

## ETA total recalibrada

5 bloques × ~50 min promedio = **3-5 horas reales** según Apéndice 1.3 (factor 5-8x demostrado).

## Métricas de éxito

| Métrica | Target |
|---|---|
| 5 steps LLM produciendo contenido real (>50 palabras, no trivial) | ✅ |
| Embrión Técnico + Ventas devolviendo JSON Pydantic válido | ✅ |
| Tests acumulados | ≥ 200 PASS |
| Suite completa | regresión cero |
| Smoke productivo con frase canónica produce empresa con contenido genuino | ✅ |
| Catastro elige modelo en runtime (NO hardcoded) | ✅ |

## Disciplina obligatoria

- Capa Memento en cada call a LLM externo
- Brand DNA en errores: `e2e_step_llm_*_failed`, `embrion_tecnico_*_failed`, `embrion_ventas_*_failed`
- Anti-Dory: stash → pull rebase → pop antes de cada commit
- NO heredoc al bridge (semilla 40 aplicada)
- LLM-as-parser con Pydantic Structured Outputs (semilla 39)

## Zona primaria

```
kernel/embriones/tecnico/embrion_tecnico.py (NUEVO)
kernel/embriones/ventas/embrion_ventas.py (NUEVO)
kernel/e2e/steps/concept_generation.py (modificación)
kernel/e2e/steps/icp_definition.py (modificación)
kernel/e2e/steps/naming.py (modificación)
kernel/e2e/steps/branding.py (modificación)
kernel/e2e/steps/copy_generation.py (modificación)
scripts/_smoke_sprint871_real_content.py (NUEVO)
tests/test_sprint871_*.py (NUEVOS)
bridge/SPRINT_87_1_OPERATIONAL_GUIDE.md (NUEVO)
```

## NO TOCÁS

- `kernel/catastro/*` (zona Catastro — Sprint 86.8 corriendo en paralelo)
- `kernel/memento/*` (zona cerrada)
- `kernel/embriones/critico_visual/*`, `kernel/embriones/product_architect/*`, `kernel/embriones/creativo/*`, `kernel/embriones/estratega/*`, `kernel/embriones/financiero/*`, `kernel/embriones/investigador/*`, `kernel/embriones/vigia/*` (Embriones existentes — solo se invocan)
- `kernel/e2e/orchestrator.py` salvo donde el orchestrator invoca los steps (modificación quirúrgica)
- `apps/mobile/*` (zona Mobile — sprints futuros)

## Próximo sprint después

Sprint 87.2 — Deploy real + Gemini Vision como puente del Critic Visual + Traffic real.

— Cowork (Hilo B)
