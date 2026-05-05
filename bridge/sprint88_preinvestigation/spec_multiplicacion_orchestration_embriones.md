# Sprint 88 — Multiplicación + Orchestration de Embriones · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05 ~02:00 CST
> **Estado:** Spec firmado, listo para arranque post-Sprint 87 NUEVO
> **Sprint asignado:** Hilo Manus Ejecutor
> **Dependencias:** Sprint 87 NUEVO E2E cerrado verde (los 9 Embriones invocados secuencialmente en pipeline)
> **Cierra:** Objetivo #11 (Multiplicación de Embriones) al 70%+, Objetivo #8 (Inteligencia Emergente Colectiva) al 70%+

---

## Contexto

Sprint 87 NUEVO entrega Pipeline lineal con los 9 Embriones invocados **secuencialmente**: cada Embrión recibe input del anterior, no hay debate, no hay paralelización. Eso cumple Objetivo #1 al 95% pero deja Obj #8 + #11 en ~30%.

Sprint 88 transforma la invocación lineal en **orchestration colectiva con emergencia verificable**. Los 9 Embriones empiezan a hablarse entre sí, debaten decisiones magna, generan conclusiones que ningún Embrión individual hubiera producido.

## Objetivo del Sprint

Activar protocolo de inteligencia emergente entre los 9 Embriones existentes con métricas observables de emergencia (conclusiones nuevas, drift detection, consenso adversarial). Demostrar que el output del colectivo > suma de outputs individuales.

## Decisiones arquitectónicas firmes

### Decisión 1 — Reuso del módulo `kernel/collective/` existente

`kernel/collective/` ya tiene 1,508 LOC implementados:
- `protocol.py` (705 LOC) — protocolo de IE
- `knowledge_propagator.py` (458 LOC)
- `emergence_detector.py` (289 LOC)

**Sprint 88 NO reescribe esto. Lo activa, integra con Embriones, y agrega métricas observables.** Si descubre que algún componente está incompleto, completa en Sprint 88. Si está sano, solo conecta cables.

### Decisión 2 — 3 modos de orchestration

| Modo | Cuándo se activa | Embriones que participan |
|---|---|---|
| `lineal` (actual Sprint 87) | Pipeline E2E estándar | 9 secuencial |
| `debate` (NUEVO) | Decisiones magna (stack tech, pricing, brief válido?) | 3-5 Embriones relevantes en paralelo |
| `quorum` (NUEVO) | Validación adversarial de output (Critic Visual + Critic Estratégico + Critic Financiero) | 3 Embriones críticos votan |

Modo elegido por `kernel/e2e/orchestrator.py` según el step del pipeline.

### Decisión 3 — Detector de emergencia con criterios objetivos

Una conclusión cuenta como "emergente" si cumple **al menos 3 de 4 criterios**:
1. **Novedad:** ningún Embrión individual la generó en la primera ronda
2. **Convergencia:** ≥ 2 Embriones la suscriben tras debate
3. **Verificabilidad:** la conclusión es testeable (no es opinión)
4. **Aplicabilidad:** modifica el resultado del pipeline (no es trivia)

Métrica de éxito Obj #8: **≥ 3 emergence events confirmados/semana** en runs E2E.

### Decisión 4 — Schema Supabase nuevo

Migration `022_sprint88_emergence_schema.sql`:

```sql
CREATE TABLE collective_debates (
    id TEXT PRIMARY KEY,                  -- 'debate_<timestamp>_<hash>'
    e2e_run_id TEXT REFERENCES e2e_runs(id),
    step_number INT NOT NULL,
    modo TEXT NOT NULL CHECK (modo IN ('debate','quorum')),
    embriones_participantes TEXT[] NOT NULL,
    pregunta TEXT NOT NULL,
    respuestas_individuales JSONB NOT NULL,    -- ronda 1
    respuestas_post_debate JSONB,              -- ronda 2 si aplica
    conclusion_final TEXT,
    is_emergent BOOLEAN DEFAULT FALSE,
    emergence_criteria_met TEXT[],             -- subset de los 4
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE emergence_events (
    id BIGSERIAL PRIMARY KEY,
    debate_id TEXT REFERENCES collective_debates(id),
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    novedad BOOLEAN, convergencia BOOLEAN,
    verificabilidad BOOLEAN, aplicabilidad BOOLEAN,
    impacto_pipeline TEXT,                     -- qué cambió en el output
    confidence NUMERIC(3,2)
);
```

### Decisión 5 — Capa Memento aplicada por hilo Manus DENTRO del colectivo

Los Embriones operan con LLMs externos (Claude, GPT, Gemini). Cada llamada a LLM **debe pasar por `tools/memento_preflight.py`** con operation=`embrion_llm_call`. Razón: prevenir que un Embrión use modelo deprecated que el Catastro ya marcó como problemático.

## Bloques del Sprint

### Bloque 1 — Auditoría de `kernel/collective/` (15-30 min)

- Verificar qué 1,508 LOC realmente funcionan vs son stub
- Identificar gaps de integración con Embriones
- Reportar hallazgos en bridge

### Bloque 2 — Schema + endpoints (30-45 min)

- Migration 022 (2 tablas nuevas)
- `kernel/collective/routes.py` con `POST /v1/collective/debate` + `GET /v1/collective/emergence_events`

### Bloque 3 — Modos `debate` y `quorum` integrados al orchestrator E2E (45-60 min)

- `kernel/e2e/orchestrator.py` modificado para invocar modo según step
- Modo `debate`: paralelización con `asyncio.gather` de 3-5 Embriones
- Modo `quorum`: validación 2-de-3 con cap trust delta

### Bloque 4 — Detector de emergencia (30-45 min)

- `kernel/collective/emergence_detector.py` activado/completado
- Lógica de 4 criterios (novedad, convergencia, verificabilidad, aplicabilidad)
- Persistencia en `emergence_events`

### Bloque 5 — Capa Memento integrada (15-20 min)

- Cada llamada de Embrión a LLM pasa por `preflight_check(operation='embrion_llm_call')`
- Tests con mock de preflight

### Bloque 6 — Tests + smoke E2E (30-45 min)

- Test del modo debate con 3 Embriones simulados
- Test del modo quorum con consenso/disenso
- Test del detector con casos sintéticos (1 emergente, 1 no-emergente)
- Smoke contra producción real con 1 frase E2E que dispare al menos 1 debate

### Bloque 7 — Métricas + dashboard (15-30 min)

- Endpoint `GET /v1/collective/dashboard/summary` con métricas:
  - Total debates últimos 7 días
  - Emergence events count
  - Embriones más activos
  - Conclusiones emergentes destacadas

## ETA total recalibrada

7 bloques × ~30 min promedio = **3-5 horas reales** al ritmo demostrado del Hilo Ejecutor.

(ETA magna previa: 1 semana. Recalibración 5-10x más rápido aplicada.)

## Métricas de éxito

| Métrica | Target |
|---|---|
| Test 1 v2 con tráfico real dispara ≥ 1 debate emergente | ✅ |
| Tests acumulados | ≥ 350 PASS |
| Suite Sprint 86 + 87 + 88 | regresión cero |
| Latencia por debate | < 30s P95 |
| Emergence rate | ≥ 1 event por 5 runs E2E |

## Disciplina obligatoria

- Capa Memento aplicada en cada call de Embrión a LLM externo
- `tests/fixtures/` con casos sintéticos de debates emergentes vs no-emergentes
- Brand DNA aplicado en dashboard HTML (forja + graphite + acero)
- Anti-Dory: lectura fresh de catálogo de modelos del Catastro antes de cada debate

## Zona primaria

```
kernel/collective/* (existente, completar/activar)
kernel/collective/routes.py (nuevo)
kernel/e2e/orchestrator.py (modificación quirúrgica)
scripts/022_sprint88_emergence_schema.sql (nuevo)
scripts/run_migration_022.py (nuevo)
scripts/_smoke_collective_emergence.py (nuevo)
tests/test_sprint88_*.py (nuevos)
bridge/COLLECTIVE_OPERATIONAL_GUIDE.md (nuevo)
```

## NO TOCÁS

- `kernel/embriones/*` (los 9 Embriones existentes — solo se invocan, no se modifican)
- `kernel/catastro/*` (zona del Catastro)
- `kernel/memento/*` (cerrado Sprint Memento)
- `kernel/e2e/pipeline.py` salvo donde el orchestrator lo invoca

## Próximo sprint después

Sprint 89 — Activación Guardian Autónomo. Spec en `bridge/sprint89_preinvestigation/spec_guardian_autonomo.md`.

— Cowork (Hilo B)
