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

### D2.0 — Pre-flight checks ✅
- [x] Verificar existencia y path real de `scripts/_check_no_tokens.sh`
- [x] Verificar `KERNEL_MONSTRUO_BASE_URL` en Railway o usar fallback DEV
- [x] Verificar que branch sprint/la-forja-001 está sincronizada (commit 3270f45 ya pulled)
- [x] `git pull --rebase origin sprint/la-forja-001` antes de cada commit (mitigación LF-9)

### D2.1 — Env strict + Supabase client ✅ commit `e37fc33`
- [x] `src/lib/env.ts` strict mode con 11 envs: ANTHROPIC, OPENAI, GEMINI, SONAR, MANUS_APPLE, MANUS_GOOGLE, LANGFUSE_PUBLIC/SECRET, SUPABASE_URL/SERVICE_KEY, KERNEL_MONSTRUO_BASE_URL
- [x] `src/lib/supabase.ts` cliente service-role server-side (RLS bypass autorizado server only)
- [x] Tests: env validation falla loud, Supabase client se construye con config válido (22 tests)

### D2.2 — 5 LLM clients + multi-model router ✅ commit `053f9f9`
- [x] `src/lib/llm/anthropic.ts` Claude Opus 4.7 modo Adaptive obligatorio (@anthropic-ai/sdk@0.96.0)
- [x] `src/lib/llm/openai.ts` GPT-5.5 Pro endpoint /v1/responses con input array (openai@6.38.0)
- [x] `src/lib/llm/google.ts` Gemini 3.1 Pro (RAG) + Gemini 2.5 Flash (clasificador) (@google/genai@2.3.0)
- [x] `src/lib/llm/perplexity.ts` Sonar Reasoning Pro con citations array (fetch directo, no SDK)
- [x] `src/lib/llm/router.ts` dispatcher MISSION_TO_MODEL canónico
- [x] Tests: 16 router + 4 perplexity = 20 tests

### D2.3 — Contratos enforcers binarios ✅ commit `c2faed6`
- [x] `src/lib/budget.ts` LF-RATE-LIMIT-001 + DSC-LF-003 con UPDATE atómico vía BudgetClient interface
- [x] `src/lib/redact.ts` R10 mitigación PII: emails/teléfonos MX/RFCs/cuentas → [REDACTED]
- [x] `src/lib/ac12.ts` clasificador Gemini 2.5 Flash threshold confidence ≥ 0.7
- [x] `src/lib/telemetry.ts` STUB con interface TelemetryClient estable cross D2-D5
- [x] Tests: 14 budget + 22 ac12 + 27 redact/telemetry = 63 tests

### D2.4 — 5 Puertas + LF-FIVE-DOORS-001 enforcer ✅ commit `d1e35ac`
- [x] `src/puertas/manus_apple.ts` wrapper sobre manus_bridge.ts cuenta apple
- [x] `src/puertas/manus_google.ts` wrapper sobre manus_bridge.ts cuenta google
- [x] `src/puertas/cowork_local.ts` role-aware (T1-Alfredo escribe, T1-Padre → not_available_in_environment)
- [x] `src/puertas/kernel_monstruo.ts` fetch KERNEL_MONSTRUO_BASE_URL
- [x] `src/puertas/simulador.ts` POST simulador-api-production.up.railway.app
- [x] `src/puertas/index.ts` enumerator PUERTAS const tuple length 5 EXACT
- [x] Tests: 14 tests con enumerator length 5 + role-aware cowork + 5 invokes

### D2.5 — Middleware Hono ✅ commit `a524686`
- [x] `src/middleware/auth.ts` STUB con interface User estable cross D2-D4
- [x] `src/middleware/budget.ts` preCallCheck + 429 si excede cap $50/mes
- [x] `src/middleware/telemetry.ts` span de inicio + fin del request (stub stdout)
- [x] Tests: 10 tests auth + budget + telemetry

### D2.6 — Rutas Hono (sin SSE) ✅ commit `4c879b3`
- [x] `src/routes/health.ts` (ya existía D1, mantenido)
- [x] `src/routes/tutor.ts` POST /api/tutor/chat → Anthropic Adaptive + AC12 + Perplexity opcional
- [x] `src/routes/sprints.ts` POST + GET /states con SPRINT_STATES tuple length 8
- [x] `src/routes/manus.ts` POST /api/manus/task wrapper handleManusBridge
- [x] `src/routes/puertas.ts` POST /:nombre + GET enumerator
- [x] `src/routes/telemetry.ts` POST /api/telemetry con VALID_EVENT_TYPES canónicos
- [x] Tests: 13 tests rutas integradas con vi.mock por módulo

### D2.7 — Montaje + suite final ✅ commit `ea543e7`
- [x] `src/index.ts` reescrito como factory createApp(options) con DI BudgetClient
- [x] 6 routers montados con middleware orden auth → telemetry → budget → route
- [x] `src/lib/budget_clients.ts` InMemoryBudgetClient (D2-D4) + SupabaseBudgetClient placeholder (D5)
- [x] `src/index.test.ts` smoke test 7 tests del montaje
- [x] Validación pre-commit: typecheck 0 errores + 170/170 tests + build dist/ generado
- [x] Push y CI: 3 rojos confirmados preexistentes (Lint, Unit Tests anti-dory, semgrep)

### D2 — Reglas de oro (Brand Engine + Reglas Duras) ✅ TODAS CUMPLIDAS
- [x] Solo `process.env` vía loadEnv() con `.trim()` defensivo, cero hardcodes
- [x] Error messages formato `[la-forja:{module}_{action}_{failure_type}]`
- [x] Naming módulos con identidad: `puerta_*`, `forja_*`, `la-forja:*`
- [x] No tocar `tools/`, `kernel/`, `scripts/cowork_*` (locks LF-8 respetados)
- [x] No queries SQL contra tablas que no existen (D5 aplica migraciones)
- [x] Commits desde archivo (evitó heredoc corruption en los 7 commits)
- [x] `git pull --rebase` antes de cada push (cero colisiones)

## D2 — CIERRE FIRMADO 15-may-2026 21:09 CST

**Veredicto Manus E1 binario:** 🟢 D2_BACKEND_HONO_COMPLETO

| Métrica | Valor |
|---|---|
| Commits D2 | 7 (e37fc33→053f9f9→c2faed6→d1e35ac→a524686→4c879b3→ea543e7) |
| Tests | 170/170 passing en 486ms (12 test files) |
| typecheck | 0 errores |
| build | dist/ generado: index.js 4.8KB + 4 subdirectorios |
| LOC nuevas D2 | ~3,500 (estimado, sin tests) |
| SDKs LLM oficiales validados magna 15-may | 3 SDKs |

**Próximo:** D3 frontend Next.js 16.2 + Vercel AI SDK 6.0.27 con Tour, Chat tutor SSE, Sala de Sprint, Dashboard vivo. Aprobación Alfredo + audit Cowork del delta D2 requerida para iniciar D3.

