# Sprint SPR-FACTORY-UI-001 — Factory Mode UI en `tablero-campana`

**Estado:** WAITING_REVIEW (Cowork audit + firma Alfredo pendientes)
**Fecha de propuesta:** 2026-05-28
**Paradigm:** frontend
**Capa:** C1 + C2
**Origen:** `bridge/FORJA_OMEGA_VISUAL_PROMPT_v2_2026_05_28.md` (PR #235 SHA `de91b96`)
**Validado por (Track 1, 2026-05-28):** GPT-5 (8/10), Claude Opus 4.5 (8/10), Gemini 2.5 Pro (7/10), Perplexity Sonar Pro (8.5/10) — los 4 veredicto APRUEBA_CON_CAMBIOS

**Objetivo:** Construir la 6ª lente "Fábrica" del `tablero-campana` con 4 paneles HUD que consuman los endpoints `/v1/factory/*` del kernel via BFF tRPC autenticado, respetando Brand DNA Forja y estándar a11y WCAG AA.

## Tareas

1. Inventariar componentes existentes en `client/src/components/ui/` para reuso.
2. Implementar `server/routers/factory.ts` con 4 procedimientos protectedProcedure + zod schemas.
3. Implementar 4 paneles HUD (`Constellation`, `Economy`, `Timeline`, `Diff`) con estados loading/error/empty.
4. Agregar 6ª lente "Fábrica" al `LayerSwitcher` con cámara orbital + click bidireccional.
5. Implementar 4 hooks centralizados con visibility-aware polling.
6. Tests obligatorios: proxy + UI + a11y (axe-core 0 violations) + security (no leak API key).
7. Validación pre-merge: typecheck + vitest + build + screenshots móvil + audit Cowork.

## Objetivos maestros tocados

- **OM-1** Soberanía de UI/visualización del Monstruo
- **OM-3** Reuso jerárquico de capas existentes (cero duplicación de backend)
- **OM-7** Brand DNA Forja como diferenciador defendible
- **OM-9** Observabilidad ejecutable (BFF + zod + visibility-aware polling)

## Alcance

Construir la 6ª lente "Fábrica" + 4 paneles HUD + proxy tRPC server-side BFF que consumen los 4 endpoints aggregator del kernel (`/v1/factory/{constellation,economy,timeline,diff}`) ya LIVE.

**Spec autoritativa:** `bridge/FORJA_OMEGA_VISUAL_PROMPT_v2_2026_05_28.md` (a complementar con v2.1 post-síntesis sabios).

## Ejecutor sugerido

Manus A (cuenta `manus_a`) en sesión limpia, frontend puro, después de que Cowork apruebe spec v2.1.

## Pre-requisitos

1. Alfredo firma OK al prompt v2.1 (que integra los cambios obligatorios de los 4 sabios).
2. Cowork audita pre-arranque (DSC-G-008 v2).
3. PR del prompt v2.1 mergeado (sucesor de PR #235).

## Estimación

~1 200–1 800 LOC TSX, 1-2 días de Manus A.

## Criterios de cierre

- Los 4 paneles HUD renderizan con datos reales del kernel.
- Tests proxy + UI + a11y + security pasan en CI.
- Bundle delta < 80 KB gzip.
- Audit Cowork verde sobre Brand DNA + a11y.
- Screenshots móvil iOS Safari + iPad landscape adjuntos en PR.

## Cierre

Cuando se mergee, mover a `bridge/sprints_completados/` con sufijo `_completed_at_YYYY_MM_DD.md`. Crear `bridge/missions/SPR-FACTORY-UI-001/` con la estructura T1-007 C: `0_intent.md, 1_orders/, 2_assemblies/, 3_executions/, 4_evidence/, 5_court/, 6_outcomes.md`.
