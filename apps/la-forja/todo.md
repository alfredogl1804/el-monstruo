# La Forja — TODO (Sprint LA-FORJA-001)

## Audit Cowork DSC-G-008 v3 — AMARILLO_CON_OBSERVACIONES (15 mayo 2026)

Commit audit: `1bff43d` · Archivo: `bridge/cowork_to_manus_LA_FORJA_001_AUDIT_RESULT.md`

### Bloqueante pre-SQL (reconciliar antes de cualquier CREATE TABLE)

- [x] Producir patch SPEC v3.2 unificando naming entre §0 header y §3 modelo de datos (4 migraciones con concepto distinto)
- [x] Linter `tools/spec_lint.py` verde sobre v3.2
- [x] Commit + push patch v3.2
- [ ] `gh pr ready 133` (después de incluir D1 no-SQL en el PR)

### D1 no-SQL autorizado por T1-Alfredo (paralelo a v3.2)

- [x] Estructura `apps/la-forja/api/` con package.json + tsconfig + ESLint
- [x] Dockerfile (no Nixpacks, Railpack-compatible)
- [x] Port `tools/manus_bridge.py` → `apps/la-forja/api/src/lib/manus_bridge.ts` con paridad funcional
- [x] Tests vitest sobre `manus_bridge.ts` con mocks (sin tocar API real en CI) — 21/21 passing
- [x] Validación tipada de env vars con Zod (`src/lib/env.ts`)
- [x] Hono entry `src/index.ts` con /health endpoint
- [x] Build TypeScript pasa sin errores
- [ ] Commit estructura backend + port
- [ ] Push branch sprint/la-forja-001

### D2 Backend routes (siguiente fase)

- [ ] Multi-model router (Opus 4.7 tutor + GPT-5.5 sprints + Gemini 3.1 RAG)
- [ ] Ruta POST /api/tutor/chat (streaming SSE)
- [ ] Ruta POST /api/sprints (co-piloto de sprints)
- [ ] Ruta POST /api/manus/task (proxy del bridge)
- [ ] Cliente Supabase server-side con service role
- [ ] Cambiar loadEnv() a strict:true

### D3 Frontend (Next.js 16.2 + Vercel AI SDK 6.0.27)

- [ ] Scaffold `apps/la-forja/web/`
- [ ] Tour guiado (página onboarding)
- [ ] Chat tutor (Streamdown + SSE)
- [ ] Sala de Sprint (co-pilot UI)
- [ ] Dashboard vivo (estado + costos + Cliente Cero)

### D4 Auth Google OAuth

- [ ] GOOGLE_OAUTH_CLIENT_ID/SECRET en Railway
- [ ] Middleware OAuth en Hono
- [ ] Callback handler

### D5 RLS migrations (BLOQUEADO hasta PR ready + Cowork confirma)

- [ ] 9 migraciones 0036-0044 con RLS desde nacimiento
- [ ] Mínimo un CREATE POLICY por tabla (Regla Dura #7)

### D6 Deploy + smoke tests

- [ ] Deploy Railway con Dockerfile
- [ ] /health 200 en producción
- [ ] Smoke test E2E desde frontend Vercel

### No bloqueantes (antes de D6)

- [x] H1: Unificar costos Heavy entre archivos a un único número ($65.30) — aplicado en v3.2
- [x] H2: Especificar mecanismo de update `forja_budget.spent_usd_month` en LF-RATE-LIMIT-001 — aplicado en v3.2
- [x] H3: Considerar clasificador Gemini Flash para AC12 detector "no entiendo" — AC12 mejorado en v3.2
- [x] H4: Agregar mitigaciones R9 (Cliente Cero humano) y R10 (PII en Langfuse spans) — R9+R10 añadidos en v3.2
- [x] H5: Recalibrar timeline D1-D6 a 5-7 días reales — ETA actualizado en v3.2
