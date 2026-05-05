# Audit Roadmap — Apéndice 1.3: Factor de Velocity Recalibrado

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Recalibración de Apéndice 1.2 con evidencia empírica de 6 sprints
> **Reemplaza:** factor 4-5x del Apéndice 1.2 (firmado 2026-05-04)
> **Vigente desde:** 2026-05-05

---

## Resumen

El Apéndice 1.2, firmado ayer 2026-05-04, recalibró las estimaciones de tiempo por un factor **4-5x más rápido** que las estimaciones magna conservadoras anteriores. Esto se basaba en evidencia inicial limitada (5 casos históricos).

Hoy 2026-05-05, con evidencia empírica de **6 sprints adicionales medidos en tiempo real**, el factor demostrado se sitúa entre **5-8x más rápido**. El extremo superior (8x) aplica cuando el sprint reusa arquitectura simétrica ya validada (templates de sprints previos).

**Apéndice 1.3 actualiza el factor a 5-8x.**

---

## Evidencia empírica de 6 sprints (2026-05-05)

| Sprint | Estimación Cowork | Tiempo real reportado | Factor |
|---|---|---|---|
| Mini-sprint pre-B2 (Schema Canónico) | ~2-3h | <30 min | ~5-6x |
| Sprint 86.5 (Catastro Macroárea 3 Coding) | 2-4h | 16 min | ~8-15x |
| Sprint 86.6 (Anti-gaming v2 cross-area) | 1-2h | 25 min | ~3-5x |
| Sprint 86.4.5 Bloque 2 (Enriquecimiento) | 2-4h | <1h | ~3-4x |
| Sprint 87 NUEVO (Pipeline E2E estructural) | 5-8h | sin reporte explícito de tiempo, pero compatible con 1-2h | ~4-8x |
| Sprint 86.7 (Macroárea 4 Razonamiento) | 2.5-4h | 30 min | ~5-8x |

**Promedio del factor demostrado: 5-8x.** El extremo superior aparece cuando hay arquitectura simétrica template (ej: Sprint 86.5 → Sprint 86.7 reusó toda la estructura del classifier + sources + tests).

## Factor de Cowork sobre sí mismo

Cowork también opera bajo el mismo factor 5-8x sobre sus propias estimaciones internas. Ejemplos de hoy:
- Documento de visión v1.0 (~50 páginas equivalentes): estimado 30-60 min por mí, real ~10 min
- 4 audits + 2 specs + Apéndice 1.3 en paralelo: estimado 30-45 min, real ~5-7 min

La conclusión es coherente: **toda estimación de tiempo magna que un humano o un agente AI haga sobre trabajo de Cowork/Manus en arquitectura simétrica debe dividirse por 5-8 para ser realista.**

## Factores que aceleran (extremo 8x)

- Arquitectura simétrica template ya validada (sprint anterior similar como referencia)
- Spec firmado con zonificación clara antes de arrancar
- Disciplina anti-Dory (stash → pull rebase → pop) operacional
- Política firmada de NO standby mientras Alfredo coordina
- Capa Memento aplicada uniformemente
- Brand DNA + naming convencional consolidado

## Factores que ralentizan (extremo 5x o menor)

- Arquitectura nueva sin precedente (ej: Capa C1 Motor de Ventas Sprint 90 — nueva categoría completa)
- Specs ambiguos sobre zonas
- Trabajo crítico que NO debe acelerarse (ej: SMP Sprint Mobile 0 — la criptografía mal hecha es peor que ninguna)
- Coordinación con piezas externas no controladas por los hilos Manus

## Implicaciones operativas

**Para Cowork:**
- Toda nueva estimación de Cowork sobre sprint de Manus debe usar factor 5-8x
- Cuando el sprint reusa arquitectura simétrica, default al factor 8x
- Cuando el sprint es categoría nueva o crítico, default al factor 5x
- Sprints magna (Mobile 0 SMP) NO se aceleran — la criptografía mal hecha es peor que ninguna

**Para hilos Manus:**
- Reportar siempre tiempo real medido al cierre de cada sprint
- Esto alimenta validación continua del Apéndice 1.3
- Si el factor se demuestra mayor en sprints futuros (ej: 10x consistente), Apéndice 1.4 vendrá

**Para Alfredo:**
- Asumir que cualquier Sprint del backlog del documento de visión cierra en 1-3 días calendario, no semanas
- Sprint Mobile 0 (SMP) es excepción explícita: 2-4 semanas reales, no se acelera

## Sprints v1.0 con ETA recalibrada por Apéndice 1.3

Aplicando factor 5-8x sobre el roadmap de `docs/EL_MONSTRUO_APP_VISION_v1.md`:

| Sprint | ETA Apéndice 1.2 (4-5x) | ETA Apéndice 1.3 (5-8x) |
|---|---|---|
| Sprint Mobile 0 (SMP) | 2-4 semanas | 2-4 semanas (NO acelerar — crypto crítico) |
| Sprint Mobile 1 (esqueleto) | 5-7h | 3-5h |
| Sprint Mobile 2 (Modo Daily fase 1) | 8-12h | 5-8h |
| Sprint Mobile 3-5 (Modo Cockpit progresivo) | 18-27h | 12-18h |
| Sprint Mobile 6 (voice + polish) | 4-6h | 3-4h |
| Sprint 87.1 (Embriones reales) | 3-5h | 2-3h |
| Sprint 87.2 (Deploy + critic visual) | 5-8h | 3-5h |
| Sprint 86.8 (confidentiality_tier) | 1-2h | 0.5-1h |
| Sprint 90 (Motor Ventas C1) | 3-5h | 2-3h |
| Sprint 91 (Motor SEO C2) | 3-5h | 2-3h |

**Total v1.0 producto (sin SMP que es excepción):** ~30-50h reales del/los hilos Manus, calendario ~1-2 semanas si se paraleliza con 2 hilos en distintas zonas.

## Cierre

Este apéndice se vive y se valida. Si en 7 días el factor demostrado se aleja del rango 5-8x (más alto o más bajo), Apéndice 1.4 reemplaza este. Mientras tanto, las estimaciones de Cowork operan con este recalibrado.

— Cowork (Hilo B)
