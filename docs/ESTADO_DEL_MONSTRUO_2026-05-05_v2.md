# Estado del Monstruo · Snapshot 2026-05-05 v2 (post-cierre Sprint 86.5)

> **Autor:** Cowork (Hilo B)
> **Timestamp:** 2026-05-05 ~03:50 CST
> **Propósito:** brújula consolidada actualizada después del cierre Sprint 86.5 LLM Coding production-ready (16 min reales) + 3 specs nuevos firmados.
> **Vida útil:** invalidar cuando Sprint 87 NUEVO E2E cierre (próximo hito macro).
> **Reemplaza:** `ESTADO_DEL_MONSTRUO_2026-05-05.md` (v1, ~03:00 CST, ya stale por avance del Catastro).

---

## TL;DR — Una sola línea

**Sprint 86.5 Catastro Macroárea 3 (LLM Coding) PRODUCTION-READY + 3 specs siguientes firmados (88, 89, 90) + ETA v1.0 funcional recalibrado a 1-2 semanas + 3 hilos Manus operando en paralelo a velocity 5-10x más rápida que estimación previa.**

---

## Estado por capa arquitectónica

### Capa 0 — Cimientos Perpetuos (~85% completo, ↑ desde 80%)
- **Error Memory:** ✅ 39+ semillas + 40 candidata (heredoc Mac corruption pendiente seeding)
- **Magna Classifier:** ✅ kernel/magna_classifier.py operativo
- **Vanguard Scanner / Catastro:** ✅✅ **Catastro v1.1 con Macroárea 3 (Coding) production-ready**
  - 3 fuentes Macroárea 3: SWE-bench Verified, HumanEval+, MBPP+
  - Anti-gaming UC Berkeley primer hit en producción (`overfit-coder-v1` detectado)
  - Vocabulario controlado 15 tags (16to viene en Sprint 86.6: `coding-overfit-suspected`)
- **Design System:** ⚠️ Brand DNA + 6 verticales YAML + Critic Visual integrado, falta E2E con tráfico real (Sprint 87 NUEVO)

### Capa 1 — Manos (~70% completo, sin cambios desde v1)
- **Browser Soberano:** ✅ Sprint 84.6 cerrado
- **Backend Deploy:** ✅ tools/deploy_to_railway + deploy_to_github_pages
- **Pagos Stripe:** ❌ Sprint 95+ DIFERIDO por decisión Alfredo
- **Media Generation:** ✅ tools/generate_hero_image
- **Stuck Detector:** ⚠️ circuit breaker judge sí, general no
- **Observabilidad:** ⚠️ Langfuse + OTEL, falta Guardian autónomo (Sprint 89)

### Capa 2 — Inteligencia Emergente (~45% completo, sin cambios desde v1)
- **Multiplicación Embriones:** ⚠️ 9 Embriones existentes (3,487+ LOC), orchestration colectiva pendiente Sprint 88
- **Protocolo IE:** ⚠️ kernel/collective/ con 1,508 LOC, activación Sprint 88
- **Simulador Causal:** ⚠️ kernel/causal_*/ con 1,913 LOC, integración pendiente
- **Capas Transversales:**
  - ⚠️ Capa 7 Resiliencia + Capa 8 Memento ✅
  - C1 (Motor de Ventas) **spec firmado en Sprint 90 ✅** ← NUEVO desde v1
  - C2-C6 (SEO/Ads/etc) pendientes Sprints 91-95

### Capa 3 — Soberanía (~35% completo, sin cambios)
- **Modelos propios:** ❌ no iniciado (post-v1.0)
- **Infra propia:** ❌ no iniciado (post-v1.0)
- **Economía propia:** ⚠️ Sprint 95+ Stripe Pagos cuando Alfredo decida
- **Browser Soberano:** ✅ ya cumplido en Capa 1

---

## Sprints en curso (estado vivo al snapshot v2)

| Hilo | Sprint actual | Estado | Velocity demostrada |
|---|---|---|---|
| **Manus Catastro** | Sprint 86.6 (Visión Quorum 2-de-3 Macroárea 3) | TASK DESPACHADA, autorizado a arrancar | 16 min reales para Sprint 86.5 (6 bloques) |
| **Manus Ejecutor (Memento)** | Sprint 86.4.5 Bloque 2 (Enriquecimiento) + push de 2 audits Cowork | TASK DESPACHADA | mini-sprint pre-B2 cerrado en línea con recalibración |
| **Cowork (Hilo B)** | 3 entregables paralelos: spec Sprint 90 + semilla 40 + este snapshot v2 | EN CURSO | autoseguimiento de tiempo real activado |

## Sprints próximos en cola (post-actuales)

```
Sprint 86.5 Catastro ─ ✅ CERRADO 2026-05-05 03:30 CST (16 min reales)
   ↓
Sprint 86.4.5 B2 (Enriquecimiento) ─ EN CURSO Hilo Ejecutor
Sprint 86.6 (Visión Quorum 2-de-3) ─ EN CURSO Hilo Catastro
   ↓ (paralelo)
Sprint 87 NUEVO (E2E Frase → Empresa con tráfico real) ─ spec firmado
   ↓
Sprint 88 (Multiplicación + Orchestration Embriones) ─ spec firmado
   ↓
Sprint 89 (Activación Guardian Autónomo) ─ spec firmado
   ↓
Sprint 90 (Capa Transversal C1 Motor de Ventas E2E) ─ spec firmado HOY ✅
   ↓
Sprint 91-95 (Capas Transversales C2-C6 E2E) ─ pendientes
   ↓
Sprint 96 (Verificación Autonomía Total)
   ↓
Sprint 97 (Sub-ola gobernanza ticketlike) ─ spec en backlog
   ↓
Sprint 98+ (Stripe Pagos Monstruo) ─ DIFERIDO por Alfredo
```

(Numeración recalibrada: el sprint magna previo "Sprint 90-92 Capas Transversales C1/C2/C3" se desglosa en Sprints 90+91+92+93+94+95 individuales por capa, alineado con velocity demostrada.)

## Métricas vivas del proyecto

| Métrica | Valor v1 (~03:00) | Valor v2 (~03:50) | Delta |
|---|---|---|---|
| **% Monstruo v2.0 (sin Capa 4)** | ~62-68% | **~67-72%** | +5pp |
| **Tests acumulados** | 560+ PASS | **582+ PASS** (411 + 171 Memento) | +22 |
| **Semillas en error_memory** | 39 | 39 + **40 candidata** | +1 |
| **Sprints/bloques cerrados verdes hoy** | 28+ | **34+** (Sprint 86.5 B3-B6 + reportes + audits) | +6 |
| **Falsos positivos diagnosticados** | 3 | 3 | sin cambio |
| **Modelos en Catastro vivo** | 37 con quorum_alcanzado=true | 37 + 2 enriquecidos `data_extra.coding` (gpt-5-5, claude-opus-4-7) | +2 |
| **Fuentes activas Catastro** | 3/3 | **3/3 + 3 latentes** (SWE-bench, HumanEval+, MBPP+ con flag CATASTRO_ENABLE_CODING) | +3 |
| **Embriones operando** | 9 | 9 (sin cambio) | 0 |
| **Versión Railway productiva** | 0.84.8-sprint-memento | 0.84.8-sprint-memento (sin deploy nuevo aún, espera CATASTRO_ENABLE_CODING set) | sin cambio |
| **Specs Cowork firmados pre-investigación** | 88 + 89 | **88 + 89 + 90** | +1 |
| **Audits Cowork commiteados hoy** | 0 | **3** (cd16929 + 089ffdd + 0745f63) | +3 |

## Hitos macro completados desde v1 (~03:00 → ~03:50)

1. ✅ **Sprint 86.5 Catastro Bloques 1-6 cerrados production-ready** — 13 archivos, +1340 LOC, 22 tests, smoke 6/6 gates, anti-gaming primer hit
2. ✅ **3 audits Cowork commiteados** — pre-B2 (cd16929) + B1-B2 (089ffdd) + B3-B6+cierre (0745f63)
3. ✅ **Spec Sprint 90 (Capa C1 Motor de Ventas) firmado** — 7 bloques, 3-5h ETA recalibrada
4. ✅ **Semilla 40 candidata documentada** (heredoc Mac corruption, segundo incidente)
5. ✅ **Política standby duro 7 días anulada (de nuevo)** — disciplina firme aplicada al re-pedirlo el Catastro
6. ✅ **Validación adicional Apéndice 1.2** — 16 min reales para Sprint 86.5 = factor 10x sobre estimación previa de 1-3h, confirma recalibración

## Lo que vos podés hacer al volver

| Acción | Tiempo tuyo |
|---|---|
| Pasar mensajes a hilos cuando llegue su próximo cierre | ~2-5 min cada uno |
| Decidir cuándo arrancar Sub-ola gobernanza ticketlike (acción humana con tu empleado) | ~2-3h en una sesión coordinada |
| Decidir cuándo arrancar Stripe Pagos del Monstruo (Sprint 98+) | flexible, no urgente |
| Validar Test 1 v2 cuando Sprint 87 NUEVO cierre — emitir veredicto "comercializable" | ~30 min de validación humana |
| Configurar `CATASTRO_ENABLE_CODING=true` en Railway env del kernel | ~30 segundos |

## Decisiones arquitectónicas firmadas vivas (ratificadas o nuevas)

1. **Objetivo #15 — Memoria Soberana** ratificado v3.0 (commit `1360c70`) — sin cambios
2. **Capa 8 Memento** formalizada como capa transversal — sin cambios
3. **Re-priorización A→B→C** ratificada por Alfredo — sin cambios
4. **Stripe Pagos diferido** a Sprint 98+ — sin cambios
5. **Patrón "consultar Catastro en runtime"** firmado para Sprint 87 NUEVO + Sprint 90 (Motor de Ventas) — extendido
6. **Patrón DUAL REST + sub-FastMCP** canónico (semilla 34) — sin cambios
7. **Quorum 2-de-3 ortogonal anti-gaming** — confirmado en producción Sprint 86.5 con `overfit-coder-v1`
8. **LLM-as-parser con Structured Outputs Pydantic** > regex (semilla 39) — formalizada en Sprint 86.5
9. **Schema Authority único** (Pydantic from SQL) — mini-sprint pre-B2 cerrado verde
10. **ETA recalibradas 5-10x más rápido** (Audit Roadmap Apéndice 1.2) — **VALIDACIÓN EMPÍRICA** con 16 min Sprint 86.5
11. **NUEVA: standby duro 7 días anulado** — política firme Cowork, re-anulada cuando el Catastro la pidió de nuevo
12. **NUEVA: Vocabulario controlado del coding_classifier va a 16 tags** — Sprint 86.6 agrega `coding-overfit-suspected`

## Bloqueos actuales

Ninguno. Los hilos están operando en paralelo con tasks despachadas.

## Próximo hito macro esperado

**Sprint 87 NUEVO E2E cierre** = momento donde Alfredo escribe una frase, el Monstruo entrega URL viva con tráfico real, Critic Visual ≥ 80, veredicto "comercializable" = **v1.0 funcional declarado.**

ETA recalibrada al ritmo actual: **1-2 semanas calendario.**

(Sub-hito intermedio: cierre Sprint 86.4.5 B2 + Sprint 86.6 en próximas 2-4h reales, basado en velocity demostrada.)

— Cowork (Hilo B)
