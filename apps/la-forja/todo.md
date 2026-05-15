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

## Solicitud T1-Alfredo · 15 mayo 2026 21:55 CST

- [x] Redactar prompt para Cowork solicitando audit del delta v3.2 + D1 sobre PR #133 → `bridge/manus_to_cowork_LA_FORJA_001_DELTA_AUDIT_REQUEST.md`

## D2 — Backend Hono (scope ajustado, autorizado por Alfredo 15-may 22:30 CST tras VERDE Cowork)

### Scope ajustado (binariamente justificado en chat T1-Alfredo ↔ Manus E1)

**Diferidos a fases posteriores con justificación binaria:**
- `telemetry`/`anti_dory` persistentes → D5 (dependencia: tablas SQL `forja_telemetry`/`forja_threads` no existen hasta D5; LF-5 RLS desde nacimiento). En D2: stub con interface estable.
- SSE streaming en `tutor.ts` → D3 (dependencia: formato SSE definido por adaptador Vercel AI SDK 6.0.27 frontend; Obj #4 no equivocarse 2x). En D2: response síncrono JSON.
- Auth real Google OAuth → D4 (doctrina explícita SPEC §6 + §8; secrets `GOOGLE_OAUTH_*` no existen en Railway). En D2: stub `x-user-id` header con interface User estable.

### D2.0 — Pre-flight checks
- [ ] Verificar existencia y path real de `scripts/_check_no_tokens.sh`
- [ ] Verificar `KERNEL_MONSTRUO_BASE_URL` en Railway o usar fallback DEV
- [ ] Verificar que branch sprint/la-forja-001 está sincronizada (commit 3270f45 ya pulled)
- [ ] `git pull --rebase origin sprint/la-forja-001` antes de cada commit (mitigación LF-9)

### D2.1 — Env strict + Supabase client (commit 1)
- [ ] `src/lib/env.ts` strict mode con 11 envs: ANTHROPIC, OPENAI, GEMINI, SONAR, MANUS_APPLE, MANUS_GOOGLE, LANGFUSE_PUBLIC/SECRET, SUPABASE_URL/SERVICE_KEY, KERNEL_MONSTRUO_BASE_URL
- [ ] `src/lib/supabase.ts` cliente service-role server-side (RLS bypass autorizado server only)
- [ ] Tests: env validation falla loud, Supabase client se construye con config válido

### D2.2 — 5 LLM clients + multi-model router (commit 2)
- [ ] `src/lib/llm/anthropic.ts` Claude Opus 4.7 modo Adaptive obligatorio
- [ ] `src/lib/llm/openai.ts` GPT-5.5 Pro endpoint /v1/responses con input array (NO temperature)
- [ ] `src/lib/llm/google.ts` Gemini 3.1 Pro (RAG) + Gemini 2.5 Flash (clasificador)
- [ ] `src/lib/llm/perplexity.ts` Sonar Reasoning Pro con citations array (DSC-LF-004 única capa validación externa)
- [ ] `src/lib/llm/router.ts` dispatcher: tutor→Anthropic, sprints→OpenAI, RAG→Gemini Pro, AC12→Gemini Flash, validación→Perplexity
- [ ] Tests: cada misión rutea al modelo correcto, fallback chain

### D2.3 — Contratos enforcers binarios (commit 3)
- [ ] `src/lib/budget.ts` LF-RATE-LIMIT-001 + DSC-LF-003: estimateCost(maxIn, maxOut, model) pre-call + commitCost(realIn, realOut, model) post-call con UPDATE atómico
- [ ] `src/lib/redact.ts` R10 mitigación PII: emails/teléfonos MX/RFCs/cuentas → [REDACTED]
- [ ] `src/lib/ac12.ts` clasificador Gemini 2.5 Flash threshold confidence ≥ 0.7
- [ ] `src/lib/telemetry.ts` STUB: interface estable que loggea a stdout (en D5 cambia impl a INSERT INTO forja_telemetry, interface no cambia)
- [ ] Tests: budget atomicidad, redact 4 regex con casos edge, AC12 las 10 frases sinónimas SPEC §7, telemetry stub callable

### D2.4 — 5 Puertas + LF-FIVE-DOORS-001 enforcer (commit 4)
- [ ] `src/puertas/manus_apple.ts` wrapper sobre manus_bridge.ts cuenta apple
- [ ] `src/puertas/manus_google.ts` wrapper sobre manus_bridge.ts cuenta google
- [ ] `src/puertas/cowork_local.ts` escribe .monstruo/COWORK_CONTEXT_INJECTION.md (T1-Alfredo only; T1-Padre → not_available_in_environment)
- [ ] `src/puertas/kernel_monstruo.ts` fetch KERNEL_MONSTRUO_BASE_URL
- [ ] `src/puertas/simulador.ts` POST simulador-api-production.up.railway.app
- [ ] `src/puertas/index.ts` enumerator: PUERTAS const tuple length 5 exact
- [ ] Tests: enumerator length 5, cowork_local diferenciado por role, todas las puertas exportan invoke()

### D2.5 — Middleware Hono (commit 5)
- [ ] `src/middleware/auth.ts` STUB: lee header x-user-id, lookup mock con role from env DEV_USER_ROLE (en D4 cambia a JWT Supabase, interface User no cambia)
- [ ] `src/middleware/budget.ts` aplica estimateCost + bloquea HTTP 429 si excede $50/mes/usuario + log telemetry
- [ ] `src/middleware/telemetry.ts` inicia span Langfuse y lo cierra al fin del request (stub stdout en D2)
- [ ] Tests: auth stub valida UUID, budget bloquea con 429 al exceder cap

### D2.6 — Rutas Hono (commit 6, sin SSE)
- [ ] `src/routes/health.ts` mantener (ya existe)
- [ ] `src/routes/tutor.ts` POST /api/tutor/chat respuesta JSON síncrona (NO SSE, eso es D3) → Anthropic Adaptive + AC12 + Perplexity validación condicional
- [ ] `src/routes/sprints.ts` POST/GET/PATCH transitions máquina 8 estados §4 → OpenAI GPT-5.5 Pro + Supabase persist
- [ ] `src/routes/manus.ts` POST/GET dispatcher handleManusBridge (puerto del existente D1)
- [ ] `src/routes/puertas.ts` POST /api/puertas/:nombre + GET /api/puertas
- [ ] `src/routes/telemetry.ts` POST /api/telemetry (eventos cliente: confusion, simplificación, abandono, completitud)
- [ ] Tests: integration con mocks LLM, dispatcher correcto, error mapping tipado

### D2.7 — Montaje + suite final (commit 7)
- [ ] `src/index.ts` montar 6 routers (health, tutor, sprints, manus, puertas, telemetry) con middleware orden: auth → budget → telemetry → route
- [ ] Validación pre-commit completa: npm run typecheck (0 errores) + npm test (100% verde) + npm run build (dist/) + scripts/_check_no_tokens.sh (PASS)
- [ ] Push y verificar CI: confirmar que los 3 rojos siguen siendo los preexistentes (Lint Type, Unit Tests, semgrep)

### D2 — Reglas de oro (Brand Engine + Reglas Duras)
- [ ] Solo `process.env` con `.trim()` defensivo, cero hardcodes (Regla Dura #6 + DSC-S-004 + incidente 2026-05-12)
- [ ] Error messages formato `{module}_{action}_{failure_type}` con identidad (Regla Dura #4 Brand Engine)
- [ ] Naming módulos con identidad: `puerta_*`, `motor_*`, `forja_*` (NUNCA service/handler/utils)
- [ ] No tocar `tools/`, `kernel/`, `scripts/cowork_*` (lock VERIFICADOR-001 LF-8)
- [ ] No queries SQL contra tablas que no existen (LF-5 RLS desde nacimiento; D5 aplica migraciones)
- [ ] Commits desde archivo (evitar Mac heredoc corruption confirmado en D1)
- [ ] `git pull --rebase` antes de cada push (mitigación LF-9 colisión con Cowork)
