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


## D2 Cowork DSC-G-008 v3 VERDE_FIRMADO 15-may-2026 (commit `6401a3b`)

**Veredicto Cowork:** 🟢 VERDE 10/10 puntos + 4/4 decisiones — D3 AUTORIZADO.

Bridge: `bridge/cowork_to_manus_LA_FORJA_001_D2_AUDIT_RESULT.md`

### 5 observaciones register-only (no bloquean D3, atender en D4-D6)

- [ ] **OBS-1 (D4):** `DEV_USER_ROLE` default `"t1_alfredo"` puede dejar deploy accidental con acceso total. Mitigación: middleware/auth.ts debe rechazar header `x-user-id` cuando `NODE_ENV=production` y forzar JWT Supabase Auth.
- [ ] **OBS-2 (D5):** `SupabaseBudgetClient` placeholder declara métodos que lanzan `[la-forja:budget_supabase_not_implemented]`. D5 reemplaza cada método con SQL atómico real (UPDATE forja_budget WITH `... RETURNING spent_usd_month`).
- [ ] **OBS-3 (D6 opcional):** Rate limit in-memory en `manus_bridge.ts` (5 calls/hora con `_callTimestamps[]` no compartido). Aceptable hasta D4 con 1 sola instancia Railway. En D6 considerar Redis o Supabase row-level locking si escala horizontal.
- [ ] **OBS-4 (no acción):** Outlier brand engine wording en `manus_bridge.ts` es paridad 1:1 verbatim del Python original. Decisión deliberada documentada. No es violación.
- [ ] **OBS-5 (D5):** `getTelemetryClient()` singleton sin reset en prod. Cuando D5 cambia `StdoutTelemetryClient` → `SupabaseTelemetryClient`, llamar `_setTelemetryClient(null)` antes del primer `recordEvent`.

## D3 — Frontend Next.js 16.2 + Vercel AI SDK 6.0.27 (autorizado por Cowork 10/10)

### D3.0 — Pre-flight checks
- [ ] Validación magna en tiempo real: Next.js 16.2, Vercel AI SDK 6.0.27, Streamdown
- [ ] Verificar formato SSE que el adaptador del SDK espera (para retro-compatibilizar `/api/tutor/chat`)
- [ ] Verificar shadcn/ui versión actual + Tailwind v4
- [ ] Decidir: monorepo `apps/la-forja/web/` (separado del `apps/la-forja/api/`) ✅ confirmado por SPEC §6

### D3.1 — Scaffold Next.js 16.2 (commit 1)
- [ ] `apps/la-forja/web/package.json` con next@16.2, react@19, ai@6.0.27, @ai-sdk/anthropic, streamdown, tailwindcss@4
- [ ] `apps/la-forja/web/next.config.ts` con `experimental: {} ` actual + proxy a backend dev
- [ ] `apps/la-forja/web/Dockerfile` Railway-compatible (NO Nixpacks, Railpack)
- [ ] `apps/la-forja/web/.gitignore` y `.dockerignore`
- [ ] `apps/la-forja/web/tsconfig.json` strict + paths
- [ ] `apps/la-forja/web/eslint.config.mjs`
- [ ] `apps/la-forja/web/app/layout.tsx` shell mínimo con Brand Engine title "La Forja"
- [ ] `apps/la-forja/web/app/page.tsx` redirect a `/tour` o `/dashboard` según role
- [ ] Tests vitest scaffold

### D3.2 — Página /tour (commit 2)
- [ ] `app/tour/page.tsx` onboarding 5 pasos guiados (qué es La Forja, las 5 puertas, ejemplo sprint, ejemplo tutor, dashboard)
- [ ] Componentes Tour reutilizables: `<TourStep>`, `<TourNav>`
- [ ] Local state con sessionStorage flag "tour_completed"
- [ ] Diseño con identidad: tipografía + colores Brand Engine
- [ ] Tests: tour avanza pasos, sessionStorage persiste

### D3.3 — Página /chat (Tutor con SSE) (commit 3)
- [ ] `app/chat/page.tsx` con `useChat` de Vercel AI SDK 6.0.27
- [ ] Hook `useChat` apunta a `/api/tutor/chat` del backend Hono
- [ ] Renderizado streaming con `<Streamdown>` (markdown + streaming gracioso)
- [ ] Display de model usado (Claude Opus 4.7 Adaptive)
- [ ] Display de validación magna cuando se invoca (citations Perplexity)
- [ ] AC12: detector "no entiendo" muestra UI de simplificación automática
- [ ] Tests: hook chat conecta, streaming render, AC12 trigger

### D3.4 — Página /sprint (Sala de Sprint) (commit 4)
- [ ] `app/sprint/page.tsx` co-piloto sprints con GPT-5.5 Pro
- [ ] Componente `<SprintBoard>` con máquina de 8 estados visualizada
- [ ] Form para crear sprint: input objetivo + selección modelo (default GPT-5.5 Pro)
- [ ] Display sprint actual con transiciones de estado animadas
- [ ] Conexión a `/api/sprints` del backend Hono
- [ ] Tests: form submit, transition state, error handling

### D3.5 — Página /dashboard (Dashboard vivo) (commit 5)
- [ ] `app/dashboard/page.tsx` con vista de costos + estado + Cliente Cero
- [ ] Componente `<BudgetCard>` muestra `spent_usd_month` vs cap $50
- [ ] Componente `<RouterStatus>` muestra estado de las 5 puertas
- [ ] Componente `<TelemetryFeed>` últimos 10 eventos del cliente
- [ ] WebSocket o SSE para updates en tiempo real (decidir en D3.0)
- [ ] Tests: render dashboard, cards reactivas

### D3.6 — Backend SSE adapter (commit 6)
- [ ] `apps/la-forja/api/src/routes/tutor.ts`: agregar nuevo endpoint POST `/api/tutor/stream` con SSE compatible con Vercel AI SDK
- [ ] Usar `streamText` o equivalente de `@ai-sdk/anthropic` server-side
- [ ] Ajustar tests del backend para incluir streaming
- [ ] Mantener `/api/tutor/chat` JSON síncrono para compatibilidad

### D3.7 — Telemetry frontend mandatorio (commit 7)
- [ ] `web/lib/telemetry.ts` cliente que POST a `/api/telemetry` desde cada página
- [ ] Hook `useTelemetry` que registra: `tour_step_completed`, `chat_turn`, `confusion_detected`, `sprint_state_change`, `dashboard_view`, `turn_abandoned`, `sprint_completed`
- [ ] LF-TELEMETRY-MANDATORY-001 enforcer: cada página DEBE registrar al menos 1 evento

### D3.8 — Montaje + suite final (commit 8)
- [ ] Build local Next.js: `npm run build` → 0 errores
- [ ] Vitest tests: 100% verde
- [ ] Smoke test: arrancar `npm run dev` ambos apps + click manual por las 4 páginas
- [ ] Validación pre-commit: `bash scripts/_check_no_tokens.sh apps/la-forja/web/`
- [ ] Push y CI

### D3 — Reglas de oro (Brand Engine + Reglas Duras)
- [ ] Solo `process.env` (Next.js: `NEXT_PUBLIC_*` para frontend), cero hardcodes
- [ ] Error messages formato `[la-forja-web:{component}_{action}_{failure_type}]`
- [ ] Naming componentes con identidad: `Forja*`, `<Tour>`, `<Sprint>`, NO genéricos
- [ ] No tocar `apps/la-forja/api/` excepto D3.6 (SSE adapter)
- [ ] Commits desde archivo (Mac heredoc safety)
- [ ] `git pull --rebase` antes de cada push


## D2.5 — Hardening adversarial (auditoría Perplexity Cowork-Opus 15-may 22:50 CST)

### Hallazgos materiales verificados binariamente contra código

- [x] H-1 [CRÍTICO bloqueante pre-deploy]: default `DEV_USER_ROLE=t1_alfredo` + auth stub sin guard `NODE_ENV=production` → privilege escalation
- [x] H-2 [ALTO]: budget leak permanente si LLM tira excepción después de `preCallCheck` (tutor.ts, sprints.ts)
- [x] H-3 [ALTO]: classifier (Gemini Flash) + magna_validation (Perplexity) sin budget gate → DSC-LF-003 cap solo aplica a tutor/sprints, no a las otras 2 misiones
- [x] H-4 [ALTO drift documental binario]: `SPRINT_STATES` español en código (`propuesta, diseño, ejecución, ...`) ≠ SPEC §4:130 inglés (`proposed, drafting, review_alfredo, ...`)
- [x] H-5 [register→escalado]: `loadEnv({strict:false})` permisivo en `NODE_ENV=production` ahora rechaza con error fail-loud

### Fixes a aplicar

- [x] Fix H-1: `env.ts` default `DEV_USER_ROLE` ahora `"user"` (least-privilege) + `auth.ts` guard production → HTTP 503 si `NODE_ENV=production`
- [x] Fix H-2: try/catch en `tutor.ts` y `sprints.ts` con `adjustSpent(-estimated)` rollback en error path (classifier, tutor, magna, sprint_copilot)
- [x] Fix H-3: `MISSION_PRICING` ya tiene `classifier` y `magna_validation` + `tutor.ts` invoca `preCallCheck/postCallCommit` por cada misión auxiliar (3 reservas: tutor middleware + classifier + magna opcional)
- [x] Fix H-4: `SPRINT_STATES` 8 estados inglés alineado a SPEC §4:130 + tests verifican lista exacta (no sólo length)
- [x] Fix H-5: `loadEnv({strict:false})` rechaza en `NODE_ENV=production` con `[la-forja:env_load_permissive_blocked_in_production]`
- [x] Test nuevos D2.5: 6 tests nuevos (`env.test.ts` H-5 rejection + H-1 default; `middleware.test.ts` H-1 503 prod; `routes.test.ts` H-2 tutor rollback + H-2 magna rollback + H-3 classifier reserve + H-3 magna reserve; `index.test.ts` H-4 lista exacta SPRINT_STATES) — 176/176 passing
- [x] Pre-commit: `npm run typecheck` + `npm test` + `npm run build` verde
- [x] Commit `hardening(la-forja): D2.5 adversarial fixes H-1/H-2/H-3/H-4/H-5` (`bdd9dbb`)
- [x] Push a `sprint/la-forja-001`

### Bridge file Cowork con findings adversariales

- [x] `bridge/manus_to_cowork_LA_FORJA_001_D2_5_AUDIT_REQUEST.md` con 10 puntos binarios + decisión Manus (commit `3cba3b5`)
- [x] Commit + push del bridge file
- [x] Solicitar a Cowork audit del delta D2.5 — **VERDE 10/10 firmado** en `bridge/cowork_to_manus_LA_FORJA_001_D2_5_AUDIT_RESULT.md` (commit `fe82b1c`)
- [x] **DSC-G-008 v4 canonizado** con bullet error path coverage obligatorio para toda llamada LLM dentro de ruta

## D2.5 — CIERRE FIRMADO 15-may-2026 23:55 CST

| Métrica | Valor |
|---|---|
| Veredicto Cowork | 🟢 VERDE 10/10 |
| Firma | DSC-G-008 v4 canonizada |
| Commits D2.5 | 2 (`bdd9dbb` hardening + `3cba3b5` audit request) |
| Tests totales | 176/176 passing (170 D2 + 6 D2.5) |
| LOC nuevas D2.5 | ~550 (incluye tests) |
| F-patterns | 0 (cero hallazgos pendientes) |

**Próximo:** D3 frontend Next.js 16.2.6 + Vercel AI SDK 6.0.183 con Tour, Chat tutor SSE, Sala de Sprint, Dashboard vivo. **Autorizado arrancar inmediato** por Cowork (`fe82b1c`).

## D3 — Frontend (Next.js 16.2.6 + Vercel AI SDK 6.0.183) — EN PROGRESO

### D3.0 — Validación real-time + scaffold base — ✅ COMPLETADO 16-may-2026

- [x] Validación real-time de versiones (Next.js 16.2.6, React 19.2.6, Vercel AI SDK 6.0.184, Tailwind 4.3.0, TypeScript 5.7.3) contra `npm view` registry — documentado en `apps/la-forja/web/_DOCTRINA_D3.md`
- [x] H-12 RESUELTO sin adapter custom: AI SDK 6 expone `createUIMessageStream` + `createUIMessageStreamResponse` retornando `Response` web-standard — Hono lo soporta nativo. Verificado en runtime real (header `x-vercel-ai-ui-message-stream: v1`)
- [x] Scaffold `apps/la-forja/web/` con Next.js App Router + TypeScript strict + ESLint flat config + Tailwind 4 + Brand DNA tokens (`forja-500: #F97316`, `graphite-900: #1C1917`, `acero-500: #A8A29E`)
- [x] `package.json` con scripts `dev/build/typecheck/test` y versiones congeladas
- [x] `.env.local.example` con `NEXT_PUBLIC_API_URL` documentado
- [x] `src/lib/env.ts` con Zod fail-loud schema (paridad backend) + 5 tests passing
- [x] `src/lib/api.ts` cliente API tipado contra backend Hono (`ForjaApiError` + `ForjaHealthResponse`) + 3 tests passing
- [x] `src/app/page.tsx` landing minimalista con identidad Brand DNA
- [x] `src/app/salud/page.tsx` Server Component que pega `GET /health` del backend Hono
- [x] `npm run typecheck` verde
- [x] `npx vitest run` — 8/8 passing
- [x] `npx next build` verde — 4 rutas estáticas (`/`, `/_not-found`, `/salud`)

### D3.1 — Tour onboarding (estructura estática primero, sin LLM)

- [ ] Ruta `/onboarding` con 5-7 pasos estáticos siguiendo Brand DNA (forja industrial, sin corporativismo)
- [ ] Estado de tour persistido vía `POST /api/users/onboarding-status` (endpoint backend pendiente)

### D3.2 — Chat tutor con streaming SSE

- [ ] Resolver H-12: validar binariamente que Vercel AI SDK 6.0.183 expone adapter compatible con Hono SSE
- [ ] Componente `ChatTutor` con `Streamdown` para markdown streaming
- [ ] Wire a `POST /api/tutor/chat` con `requireValidation` toggle

### D3.3 — Sala de Sprint (co-pilot UI)

- [ ] Lista de sprints con SPRINT_STATES (8 inglés SPEC §4:130)
- [ ] Form crear sprint (publica POST /api/sprints)
- [ ] Vista detalle con state machine visual

### D3.4 — Dashboard vivo

- [ ] Costos del usuario (read budget desde `/api/budget/me`)
- [ ] Estado de las 5 puertas (LF-FIVE-DOORS-001)
- [ ] Cliente Cero metrics (placeholder D6)

### D3.x — Cierre D3

- [ ] Bridge `manus_to_cowork_LA_FORJA_001_D3_AUDIT_REQUEST.md`
- [ ] Audit Cowork D3 con DSC-G-008 v4 verde sobre frontend

### Hallazgos register-only para D6 polish

- [ ] H-5 strict:false fallback documentar restricción a NODE_ENV=test
- [ ] H-6 PII redact ampliar regex México (CURP, INE, NSS IMSS, RFC lowercase, phone MX 10-dig, tarjeta con dashes)
- [ ] H-7 Anthropic thinking adaptive vs enabled — verificar contra docs oficiales
- [ ] H-8 OpenAI Responses API shape — agregar test integración con SDK mockeado del request body
- [ ] H-9 @google/genai contents shape — verificar contra docs SDK 2.x
- [ ] H-10 Perplexity citations defensivo — agregar return_citations:true + warning si len===0
- [ ] H-11 fix comment middleware order index.ts:115
- [ ] H-12 Vercel AI SDK adapter Hono — verificar antes de D3 codear SSE
- [ ] H-13 SupabaseBudgetClient D5 — UPDATE arithmetic atómico (NUNCA SELECT-then-UPDATE)
- [ ] H-14 LLM client cache invalidation — invalidar caches en path strict:false


## D3.0 Hardening — Perplexity Adversarial Audit (16-may-2026)

Auditoría externa Sonar Reasoning Pro retornó 12 F-patterns + DECISION BINARIA `DO NOT SHIP`. Triage:

- [x] **F-D3.0-01 [HIGH]** `next lint` no existe en Next 16 → script cambiado a `eslint .`
- [x] **F-D3.0-02 [CRITICAL]** `eslint-config-next@16` exporta array → `...next` (sin invocar)
- [x] **F-D3.0-03 [MEDIUM]** Backend Hono default `:8080` confirmado en `api/src/lib/env.ts` → frontend ahora apunta a 8080 + comentario CORS en .env.local.example y next.config.ts
- [x] **F-D3.0-04 [HIGH]** `/salud` ahora `force-dynamic` + `revalidate=0` — build muestra `ƒ /salud (Dynamic)`
- [x] **F-D3.0-05 [MEDIUM]** `new Headers(init?.headers)` preserva instancias `Headers` y `string[][]`
- [x] **F-D3.0-06 [MEDIUM]** `AbortController` + timeout 8s + propaga `signal` externo correctamente
- [ ] **F-D3.0-07 [LOW]** register-only D6 — Next 16 genera `next-env.d.ts` automáticamente, gitignore estándar (no rompe build)
- [x] **F-D3.0-08 [LOW]** removidos `streamdown` y `@vitejs/plugin-react` (reintroducir en D3.2)
- [x] **F-D3.0-09 [LOW]** `id-match` ahora `error` con regex `\\b...\\b` (banea sufijos compuestos)
- [x] **F-D3.0-10 [LOW]** mock test usa shape `{service, version, timestamp}` + assertion contra `Headers` instance
- [x] **F-D3.0-11 [CRITICAL]** `happy-dom` 15.11.7 → **20.9.0**
- [x] **F-D3.0-12 [CRITICAL]** `vitest` 2.1.8 → **4.1.6** (latest stable, drop esbuild vulnerable)
- [x] **F-D3.0-13 [MEDIUM]** `eslint` 9.17.0 → **9.39.4**, `postcss` 8.4.49 → **8.5.14**
- [x] Re-typecheck verde, vitest 8/8, build verde, lint verde, audit pasó de 10 vulns (2 critical) → 2 moderate (postcss transitivo de Next, no fixable sin downgrade)
- [ ] Commit `hardening(la-forja): D3.0 adversarial fixes Perplexity F-D3.0-01..13 (post-audit)`
- [ ] Push a `sprint/la-forja-001`


## D3.1 — Tour onboarding estático — ✅ COMPLETADO 16-may-2026

Sin LLM. Sin contratos backend nuevos. Riesgo cero de tocar algo D2 verde.

- [x] `src/app/onboarding/page.tsx` Server Component con `dynamic = "force-dynamic"`
- [x] `src/app/onboarding/OnboardingFinishHandler.tsx` Client Component que provee callback de redirect post-tour
- [x] `src/components/onboarding/Tour.tsx` Client Component con state local + navegación prev/next/skip + cookie write
- [x] `src/components/onboarding/StepShell.tsx` layout reutilizable con highlights inline (sin regex global)
- [x] `src/lib/onboarding/steps.ts` 7 pasos con copywriting Brand DNA y data inmutable `as const`
- [x] `src/lib/onboarding/cookie.ts` helpers `read/write/clear` con encode/decode + null-safe SSR
- [x] `src/app/page.tsx` landing actualizado a Server Component async que lee cookie via `next/headers`
- [x] Test `steps.test.ts` 7 tests (count, ids únicos, no-empty, eyebrow order, highlight literal match, last-cta distinct)
- [x] Test `cookie.test.ts` 5 tests (null si no existe, read/write round-trip, clear, encodeURIComponent decode, no-throw cookie vacía)
- [x] Test `Tour.test.tsx` 7 tests (mount renderiza paso 0, next avanza, prev retrocede, last+next → onFinish skipped=false, skip → onFinish skipped=true, primer paso sin secundario, último paso sin skip)
- [x] Lint 0/0, tsc 0 errores, vitest **27/27**, next build verde con `ƒ /onboarding (Dynamic)`
- [ ] Commit `feat(la-forja): D3.1 tour onboarding estático 7 pasos sin LLM (27/27 tests)`
- [ ] Push a `sprint/la-forja-001`


## D3.1 Hardening — Perplexity Adversarial Audit (16-may-2026)

Auditoría externa Perplexity Sonar Reasoning Pro retornó 15 F-patterns + DECISION BINARIA `DO NOT SHIP`. Triage:

- [x] **F-D3.1-01 [HIGH]** id-match regex `\b...\b` aceptaba `UserService`/`OnboardingFinishHandler` — verificado binariamente con `node` script. Reemplazada por regex robusta que matchea sufijo compuesto.
- [x] **F-D3.1-02 [HIGH]** `OnboardingFinishHandler` violaba Brand Engine. Resuelto eliminando el wrapper completo (ver F-15) y moviendo `useRouter` directo a `Tour.tsx` con prop `redirectTo`.
- [x] **F-D3.1-03 [MEDIUM]** cookie sin Secure permitía overwrite en HTTP. Helper `shouldUseSecure()` agrega `Secure` solo si `location.protocol === "https:"` (preserva tests locales en localhost).
- [x] **F-D3.1-04 [MEDIUM]** doble click en último paso podría llamar `onFinish` 2x + escribir cookie 2x. Guard `finished` con `useState` previene cualquier re-llamada idempotente. 2 tests nuevos en `Tour.test.tsx`.
- [x] **F-D3.1-05 [MEDIUM]** `highlightText` con highlights que solapan podía dar match incorrecto si el más corto era prefijo del más largo. Sort por longitud descendente antes del match.
- [x] **F-D3.1-06 [MEDIUM]** screen reader no anunciaba transiciones de paso. `aria-live="polite"` + `aria-atomic="true"` en wrapper Tour + `headingRef` con `tabIndex={-1}` recibe foco programático al cambiar `index` (excluyendo mount inicial para no robar scroll).
- [x] **F-D3.1-07 [MEDIUM]** botones skip y secondary sin `focus-visible:ring`. Agregados con `ring-2 ring-{forja|acero}-300 ring-offset-2 ring-offset-graphite-900` para WCAG AA contra el background dark.
- [x] **F-D3.1-08 [MEDIUM]** `new Date(cookieValue).toLocaleString()` rendía `"Invalid Date"` literal si cookie manipulada. `formatTourCompletedAt()` valida con `Number.isNaN(parsed.getTime())` y retorna `null` si inválido (no se renderiza).
- [x] **F-D3.1-09 [MEDIUM]** `cookie.split(";")` no toleraba serializaciones sin espacio. Cambiado a `cookie.split(/;\s*/)`. Test nuevo verifica el caso patológico.
- [x] **F-D3.1-10 [LOW]** test de decode usaba ISO ASCII (no requería decode). Reemplazado con valor que tiene espacios, `&`, `=`, `/`, `ñ` — fuerza `decodeURIComponent` real.
- [x] **F-D3.1-11 [LOW]** tests no envolvían en `<StrictMode>`, perdiendo cobertura de double-mount React 19. Wrapper agregado + `vitest.setup.ts` con `globalThis.IS_REACT_ACT_ENVIRONMENT = true`.
- [ ] **F-D3.1-12 [LOW]** register-only D6 — keys `body-${i}` y `bullet-${i}` solo causan regresión si `body`/`bullets` mutan dinámicamente. La data es `as const` inmutable. Migré a keys `${step.id}-body-${i}` y `${step.id}-bullet-${i}` por defensa preventiva pero el riesgo era teórico.
- [x] **F-D3.1-13 [LOW]** SPRINT_STATES duplicados en frontend sin contract test. Exportada `FORJA_TOUR_SPRINT_STATES_LITERAL` + 2 tests nuevos: lista exacta y orden literal en body.
- [x] **F-D3.1-14 [LOW]** `v0.1.0 · D3.1` hard-coded en JSX. Creado `src/lib/version.ts` que importa `pkg.version` de `package.json` (con `resolveJsonModule`) + `NEXT_PUBLIC_FORJA_DELIVERY` env con fallback.
- [x] **F-D3.1-15 [LOW]** wrapper `OnboardingFinishHandler` redundante. Eliminado completo. Tour.tsx integra `useRouter` directo.
- [x] Re-validación: lint verde 0/0, typecheck 0 errores, vitest **33/33** passing (8 D3.0 + 25 D3.1), next build verde con 4 rutas (`ƒ /`, `ƒ /onboarding`, `ƒ /salud`, `○ /_not-found`).
- [ ] Commit `hardening(la-forja): D3.1 adversarial fixes Perplexity F-D3.1-01..15 (33/33 tests)`
- [ ] Push a `sprint/la-forja-001`


## D3.1-HARDENING — Auditoría regresión Perplexity (delta 6646544..84c728f)

- [ ] Construir prompt adversarial Perplexity D3.1-HARDENING — framing: ¿los 14 fixes que prometí cierran realmente cada F-D3.1 sin introducir regresiones?
- [ ] Entregar prompt copy-paste a Alfredo
- [ ] Recoger respuesta + procesar F-patterns nuevos (R-D3.1-NN regression-pattern format)
- [ ] Aplicar fixes/refutar/registrar binariamente
- [ ] Re-validar lint + typecheck + vitest + build verde
- [ ] Si VERDE → autorizar D3.2 (chat tutor SSE) y consultar a Cowork por DSC-LF-004 sobre cambio de contrato `/api/tutor/chat` JSON→SSE


## D3.1.1 Hardening — ✅ COMPLETADO 16-may-2026

Veredicto Perplexity D3.1-HARDENING: **SHIP** con 5 R-patterns LOW + 3 PARCIALES.
Aplicado de todos modos para cerrar residuales antes de D3.2.

- [x] **R-D3.1-01 [LOW]** `version.ts` ahora fail-loud con `throw` si falta `NEXT_PUBLIC_FORJA_DELIVERY` (sin fallback hardcoded). Documentado en `.env.local.example` con namespace `[la-forja:web_missing_env]`. Regla Dura #6.
- [x] **R-D3.1-02 [LOW]** `Tour.tsx` ahora usa `useRef<boolean>` para idempotencia sincrónica. Test nuevo: 3 clicks dentro del mismo `act()` solo invocan `onFinish` una vez (V1 con state pasaba este test por casualidad de batching, V2 lo pasa por diseño).
- [x] **R-D3.1-03 [LOW]** Comentario de `steps.ts` y `steps.test.ts` reescrito honestamente: el contract test actual es frontend-vs-SPEC literal, no cross-package. TODO D6 documentado para extraer `apps/la-forja/contracts/sprint_states.ts`.
- [x] **R-D3.1-04 [LOW]** `/onboarding/page.tsx` removido `force-dynamic`. Build report confirma `○ /onboarding` (Static) en vez de `ƒ` (Dynamic). El estado del tour vive en Client Component con cookie leída en hidratación, no en server.
- [x] **R-D3.1-05 [LOW]** `eslint.config.mjs` regex con dos lookaheads: PascalCase + ALL_CAPS. Verificado binariamente con `.regex_verify_r05_v2.mjs` que `USERSERVICE`, `FORMAT_UTIL`, `AUTH_MANAGER` ahora son rechazados, y `ForjaTourSteps`, `service`, `FORJA_TOUR_STEPS` siguen pasando.
- [x] **F-D3.1-06 PARCIAL** → fix: 2 tests nuevos verifican `aria-live="polite"`, `aria-atomic="true"`, y `tabIndex={-1}` en heading.
- [x] **F-D3.1-09 PARCIAL** → fix: 2 tests nuevos ejercen `readForjaTourCookie()` end-to-end con `documentRef` mock (separador con y sin espacio).
- [x] **F-D3.1-13 PARCIAL** → resuelto por R-D3.1-03 (comentario honesto + TODO D6).
- [x] **F-D3.1-14 PARCIAL** → resuelto por R-D3.1-01 (fail-loud sin fallback).
- [ ] **F-D3.1-03 PARCIAL** register-only D6 (test cobertura HTTPS branch — no defecto operacional, gap de coverage).
- [x] Lint 0/0, typecheck verde, vitest **37/37** (+4 tests nuevos D3.1.1), build verde con `○ /onboarding` Static.
- [ ] Commit `hardening(la-forja): D3.1.1 regression fixes Perplexity R-D3.1-01..05 + PARCIALES`
- [ ] Push a `sprint/la-forja-001`


## D3.2 — Chat tutor SSE bajo DSC-LF-005 (autorizado Cowork 16-may-2026)

**DSC-LF-005:** "Todo endpoint backend que invoque un LLM devuelve `text/event-stream` con `createUIMessageStreamResponse` del Vercel AI SDK 6. JSON solo para metadata sin LLM. Aplica forward desde D3.2; sin retroactivos."

Decisión H-12 = Opción C (migración con doctrina forward, no doble endpoint).

### Validación real-time stack SSE (anti-autoboicot)
- [x] Confirmar `createUIMessageStreamResponse` / `streamText().toUIMessageStreamResponse()` exportados en `ai@6.0.184`
- [x] Confirmar `useChat` + `DefaultChatTransport` en `@ai-sdk/react@3.0.186` (peer `^19.2.1` cubre React 19.2.6)
- [x] Probar binariamente que retorna `Response` web-standard (Hono `HandlerResponse` lo acepta nativo)
- [x] Documentar shape SSE esperado en `apps/la-forja/web/_DOCTRINA_D3.md` (§7 actualizado abajo)

### Backend D3.2 — migrar /api/tutor/chat a SSE
- [x] `apps/la-forja/api/src/routes/tutor.ts`: handler ahora devuelve `result.toUIMessageStreamResponse({ headers })` (text/event-stream)
- [x] `apps/la-forja/api/src/lib/llm/anthropic.ts`: agregado `buildTutorStream()` con Vercel AI SDK 6 + `@ai-sdk/anthropic@3.0.78` (modo Adaptive con `budgetTokens: 1024`); `invokeTutor` legacy preservado para compat de tests
- [x] `preCallCheck` para classifier + magna_validation + tutor (middleware) corre antes de iniciar el stream
- [x] `postCallCommit` del tutor corre en `onFinish` con tokens reales (`totalUsage.inputTokens/outputTokens`)
- [x] `adjustSpent(-estimated)` rollback en `onError` del stream + en cada try/catch de classifier/magna
- [x] Namespace de errores `[la-forja:tutor_*]` preservado en validaciones pre-stream
- [x] Tests SSE: `content-type: text/event-stream`, `x-vercel-ai-ui-message-stream: v1`, headers `x-la-forja-{intent,confidence,model,citations,validation-model}`
- [x] Test budget rollback en error path SSE (mock dispara `onError` → `negativeCalls.length ≥ 1`)
- [x] Tests classifier + magna preservados (siguen invocados desde server-side)
- [x] Reordenamiento: magna_validation corre PRE-stream para que las citations lleguen como header SSE (rationale en banner de `tutor.ts`)

### Frontend D3.2 — chat tutor con useChat
- [x] `@ai-sdk/react@3.0.186` y `ai@6.0.184` ya estaban en `web/package.json` (no hubo que reintroducir)
- [~] `streamdown` postpone para D3.2.1 — D3.2 entrega texto plano con cursor blink, suficiente para validar el flujo SSE binario sin sumar dependencia que requiere su propio render pipeline. Tracked.
- [x] `apps/la-forja/web/src/components/tutor/Chat.tsx` con `useChat` + `DefaultChatTransport` + custom `fetch` que captura headers SSE pre-stream
- [x] `apps/la-forja/web/src/components/tutor/MessageBubble.tsx` con Brand DNA (forja/graphite/acero, mono uppercase para role labels, cursor blink durante streaming)
- [x] `apps/la-forja/web/src/app/tutor/page.tsx` ruta `/tutor` Server Component con `force-dynamic`
- [~] Toggle UI `requireValidation`: prop del componente, pendiente exponerlo en UI — D3.2 corre con `requireValidation={false}` por default. UI toggle agendado D3.2.1.
- [x] Estados idle / streaming / error con namespace `[la-forja:tutor_stream_failed]`; botón "Reintentar" llama `regenerate()`
- [~] Tests del componente Chat con happy-dom: agendados D3.2.1 (mock de `useChat`+transport; backend ya cubre el flujo SSE end-to-end via Hono `request()`)
- [x] Typecheck + vitest 37/37 + `next build` verdes con ruta `/tutor` registrada

#### Validación cross-stack
- [x] Backend `npm test` → 176/176 (sin regresión; los 4 tests SSE reemplazan los 4 JSON anteriores)
- [x] Frontend `npm test` → 37/37 (sin regresión)
- [x] Backend `npm run build` → verde (tsc emit limpio)
- [x] Frontend `npm run build` → verde, `/tutor` registrada como `ƒ` (server-rendered on demand)
- [x] Auditoría adversarial Perplexity primer pase — COMPLETADO 16-may-2026 (D3.2.1)
  - [x] Bridge `manus_to_perplexity_LA_FORJA_001_D3_2_AUDIT.md` redactado y empujado (commit `e16bb26`)
  - [x] Output Perplexity Sonar Reasoning Pro recolectado: 9 F-patterns + 3 R-patterns + 5 drifts (DO NOT SHIP)
  - [x] Triage binario: 7 F aplicados (F-01/02/03/04/06/07/09), 2 F disputados con razón documentada (F-05/08)
  - [x] R-patterns: 3 aplicados (R-01 endurecido, R-02 contract test fs-based, R-03 doctrina honesty)
  - [x] 5 drifts externos registrados como work item de sprints D5/D6 (D-01 RLS critical, D-02 Notion, D-03/04/05 doc)
  - [x] Backend tests 180/180 (+4) · Frontend tests 38/38 (+1) · typecheck + builds verdes
  - [x] Doctrina actualizada (`apps/la-forja/web/_DOCTRINA_D3.md §8`)
- [ ] Auditoría adversarial Perplexity segundo pase (regresión sobre commit hardening D3.2.1)
- [ ] Bridge audit Cowork D3.2 (sobre delta D3.2 + D3.2.1)
- [ ] DSC-LF-005 firmado formalmente al cierre (tras audits)
