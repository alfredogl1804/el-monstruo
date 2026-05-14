# La Forja — Cliente Cero del Monstruo

**App web tutor IA adaptativo + co-piloto de sprints + test bench del Monstruo.**

## Estado actual

`scaffolding-pre-audit` (B híbrida).

El SPEC LA-FORJA-001 v3.1 está firmado por T1-Alfredo el 15 mayo 2026 y pendiente de audit DSC-G-008 v3 por Cowork. Esta carpeta contiene únicamente la estructura mínima reversible: README, AGENTS.md, y subcarpetas vacías. **No existe código de negocio, migraciones SQL, ni dependencies instaladas hasta que Cowork firme.**

## Misiones

| ID | Misión |
|---|---|
| A | Tutor IA adaptativo (técnico/no técnico on-demand) |
| B | Co-piloto de sprints (diseñar, ejecutar, auditar con Manus + Cowork + Kernel) |
| C | Cliente Cero — papá T1-Padre como primer humano que usa el Monstruo para construir un proyecto distinto al Monstruo mismo |

## Arquitectura

5 puertas binarias para alcanzar el ecosistema: `manus_apple`, `manus_google`, `cowork_local`, `kernel_monstruo`, `simulador`. Capa transversal de validación tiempo real con Perplexity Sonar Reasoning Pro.

Stack verificado magna 15 mayo 2026: Next.js 16.2 + Vercel AI SDK 6.0.27 + Hono 4.12.18 + Node 22 + Railway con Dockerfile + Vercel + Supabase del Monstruo.

Modelos IA: Opus 4.7 (tutor), GPT-5.5 Pro (sprints), Gemini 3.1 Pro (RAG), Gemini 2.5 Flash (clasificador), Sonar Reasoning Pro (validación).

## Costos proyectados

| Escenario | USD/mes |
|---|---|
| Light (2 hrs/día) | $16.32 |
| Normal (4 hrs/día) | $32.65 |
| Heavy (8 hrs/día) | $60.30 |

Cap recomendado por usuario: **$50/mes**. Por encima requiere aprobación T1-Alfredo.

## Estructura

```
apps/la-forja/
  api/            ← Backend Hono (Railway, Dockerfile)
  web/            ← Frontend Next.js 16.2 (Vercel)
  migrations/     ← Migraciones 0036-0044 con RLS desde nacimiento
  README.md       ← Este archivo
  AGENTS.md       ← Doctrina específica que extiende Monstruo
```

## Pointers

- SPEC firmable: `bridge/sprints_propuestos/sprint_LA_FORJA_001_v3_1.md`
- Auditoría magna: `bridge/discovery_la_forja_001/auditoria_magna.md`
- Auditoría binaria producción: `bridge/discovery_la_forja_001/auditoria_real.md`
- Cierres pre-scaffolding: `bridge/discovery_la_forja_001/cierres.md`
- Bridge audit-request: `bridge/manus_to_cowork_LA_FORJA_001_AUDIT_REQUEST.md`

## Plan D1-D6

Ver SPEC §6.

## Reglas Duras del Monstruo aplicables

Las 8 Reglas Duras se aplican a este proyecto sin excepción. Ver `apps/la-forja/AGENTS.md` para extensiones específicas.
