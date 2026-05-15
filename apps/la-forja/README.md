# La Forja — Cliente Cero del Monstruo

**App web tutor IA adaptativo + co-piloto de sprints + test bench del Monstruo.**

## Estado actual

`d1-no-sql-completado` (15 mayo 2026).

El SPEC `LA-FORJA-001 v3.2` está firmado por T1-Alfredo y auditado por Cowork DSC-G-008 v3 (commit `1bff43d`, veredicto AMARILLO_CON_OBSERVACIONES). El patch v3.2 reconcilió el drift §0/§3, pasó el linter con cero errores y D1 no-SQL ya tiene scaffolding completo: Hono v4.12.18 sobre Node 22, Dockerfile Railway-compatible, validación tipada de env vars con Zod, port 1:1 de `tools/manus_bridge.py` a TypeScript con paridad funcional total y suite vitest de 21/21 tests passing. La primera migración SQL `0036_*` sigue BLOQUEADA hasta que el PR #133 sea marcado ready y Cowork confirme.

Ver: `bridge/cowork_to_manus_LA_FORJA_001_AUDIT_RESULT.md` y §0.1 del SPEC.

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

## Costos proyectados (fórmula canónica v3.2)

| Escenario | USD/mes |
|---|---|
| Light (2 hrs/día) | $16.32 |
| Normal (4 hrs/día) | $32.65 |
| Heavy (8 hrs/día) | $65.30 |
| Power (12 hrs/día) | $97.95 |

Cap recomendado por usuario: **$50/mes**. Por encima requiere aprobación T1-Alfredo binaria.

Fórmula canónica unificada (post-audit Cowork v3.2): Light = Normal/2, Heavy = Normal×2, Power = Normal×3. Esta tabla y la §11 del SPEC son la fuente única de verdad.

## Estructura

```
apps/la-forja/
  api/                              ← Backend Hono (Railway, Dockerfile)
    src/
      index.ts                      ← Entry Hono con /health
      lib/
        env.ts                      ← Validación Zod de env vars
        manus_bridge.ts              ← Port TS de tools/manus_bridge.py
        manus_bridge.test.ts         ← vitest 21/21 ✅
    Dockerfile                       ← Multi-stage Node 22 alpine
    package.json                     ← Hono 4.12.18 + Zod 3.25.76
    tsconfig.json                    ← TS strict ES2023
    eslint.config.mjs                ← ESLint 9 flat config
  web/                              ← Frontend Next.js 16.2 (D3, pendiente)
  migrations/                       ← Migraciones 0036-0044 con RLS (D5, BLOQUEADO)
  README.md                         ← Este archivo
  AGENTS.md                         ← Doctrina específica que extiende Monstruo
  todo.md                           ← Tracking sprint LA-FORJA-001
```

### Comandos backend

```bash
cd apps/la-forja/api
npm install        # 178 paquetes, sin peer-dep conflicts
npm run typecheck  # 0 errores
npm test           # 21/21 passing en ~400ms
npm run build      # Genera dist/
npm run dev        # tsx watch sobre src/index.ts
```

En modo dev, GET http://localhost:8080/health responde `{status:"ok", service:"la-forja-api", version:"0.1.0"}`.

Doctrina aplicada: Regla Dura #4 (secretos solo desde `process.env`), F-pattern #11 (UUID 22-char vs etiqueta lógica), incidente 2026-05-12 (`.trim()` defensivo en API key), retry con backoff exponencial 2s/4s/8s, rate limit 5 calls/hora in-memory.

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
