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
- [x] Auditoría adversarial Perplexity segundo pase — COMPLETADO 16-may-2026 (D3.2.2)
  - [x] Output recolectado: 7 F del pase 1 CERRADOS, 1 PARCIAL (F-D3.2-04), 2 DISPUTA_VALIDA (F-05, F-08), 3 R CERRADOS, 4 drifts D5 confirmados
  - [x] 3 regresiones nuevas detectadas: F-D3.2.1-01 (HIGH bloqueante), R-D3.2.1-02 (MEDIUM), R-D3.2.1-03 (LOW)
  - [x] Fix F-D3.2.1-01: truncado por citation completa (loop incremental); JSON resultante siempre parseable
  - [x] Fix R-D3.2.1-02: contract test sin fs runtime; nuevo generador `contract:headers` + JSON canonico committed
  - [x] Fix R-D3.2.1-03: test F-D3.2-04 endurecido con round-trip JSON.parse + URL completas (startsWith/endsWith)
  - [x] Backend tests 180/180 · Frontend tests 40/40 (+2) · typecheck + builds verdes
  - [x] Doctrina actualizada (`apps/la-forja/web/_DOCTRINA_D3.md §8.5`)
- [ ] Auditoría adversarial Perplexity tercer pase (opcional, NO ejecutado — cerrado por veredicto Cowork VERDE 14/14)
- [x] Bridge audit Cowork D3.2 (sobre delta D3.2 + D3.2.1 + D3.2.2) — COMPLETADO 16-may-2026
  - [x] Bridge `manus_to_cowork_LA_FORJA_001_D3_2_AUDIT_REQUEST.md` redactado y empujado (commit `b84ee0d`)
  - [x] Cowork v0.1 emitió veredicto **VERDE 14/14** + 9/9 hard rules en commit `2ac7f81`
  - [x] 2 disputas Perplexity (F-D3.2-05 abort path, F-D3.2-08 SDK legacy) JUSTIFICADAS por Cowork
  - [x] 8/8 items "Lo que NO hice" justificados (D3.3/D5/D6, ninguno deuda oculta)
  - [x] 1 observación doctrinal menor (§7.3 stale en `_DOCTRINA_D3.md` cita `x-la-forja-citations` sin sufijo `-b64`) — doc drift, no code drift, registrado para D6
- [x] DSC-LF-005 firmado formalmente — 16-may-2026 (commit hardening final `e13d669`)
  - [x] Texto canónico: “Todo endpoint backend que invoque un LLM devuelve text/event-stream con createUIMessageStreamResponse / streamText().toUIMessageStreamResponse() del Vercel AI SDK 6 + provider Anthropic. JSON solo para metadata sin LLM. Aplica forward desde D3.2 (commit beebff8); sin retroactivos.”
  - [x] Triple firma: T1 Alfredo + T2-A Cowork (commit `2ac7f81`) + T2-B Perplexity (pase 1 commit `e16bb26` + pase 2 commit Perplexity respondiendo a `a53cca6`)
- [x] Capilla LA-FORJA canonizada — 16-may-2026
  - [x] Carpeta `discovery_forense/CAPILLA_DECISIONES/LA-FORJA/` creada con README local
  - [x] DSC-LF-001 (5 puertas inviolables) firmado retroactivamente — 6/6 contratos OK
  - [x] DSC-LF-002 (preCallCheck + HTTP 429) firmado retroactivamente — 2/2 contratos OK
  - [x] DSC-LF-003 (cap $50 USD/mes + postCallCommit) firmado retroactivamente — 2/2 contratos OK
  - [x] DSC-LF-004 (magna validation Perplexity Sonar) firmado retroactivamente — 2/2 contratos OK
  - [x] DSC-LF-005 (SSE obligatorio Vercel AI SDK 6) firma original 16-may-2026 — 6/6 contratos OK
  - [x] `_dsc_contracts_index.yaml` actualizado con las 5 entradas
  - [x] Validación binaria `tools/dsc_contract_check.py` → `[ok] 5 DSCs todos con contrato ejecutable adjunto`

### Sprint LA-FORJA-001 D3.2 — CERRADO

**Cierre formal 16-may-2026.**

Commits del sprint en `sprint/la-forja-001`:

- `beebff8` — D3.2 inicial: tutor SSE + Vercel AI SDK 6 + budget pipeline preservado
- `e16bb26` — Bridge Perplexity D3.2 audit request
- `a53cca6` — D3.2.1 hardening: 7 F + 3 R Perplexity pase 1
- `e13d669` — D3.2.2 hardening: 3 regresiones Perplexity pase 2 + DSC-LF-005 firma
- `b84ee0d` — Bridge Cowork D3.2 audit request
- `2ac7f81` — Bridge Cowork D3.2 audit result (VERDE 14/14)

**PR #133:** OPEN/READY/MERGEABLE — merge manual T1 cuando decida.

### D3.3 — Sprint autorizado

- [ ] UI toggle `requireValidation` en `Chat.tsx` (magna opt-in visible al usuario)
- [ ] Adoptar `streamdown` para markdown rendering en `MessageBubble.tsx` (cap tokens visualizados + sanitización XSS)
- [ ] Tests `Chat.tsx` con happy-dom + MSW (mock SSE transport + estados idle/streaming/error)
- [ ] DSC-LF-008 propuesto (markdown rendering canónico)

### Items diferidos a sprints posteriores

- [ ] **D5** — RLS Supabase per-userId para `forja_budget_usage` (D-D3.2-01 Perplexity CRITICAL); habilitar `BudgetClient` real (hoy mock)
- [ ] **D6** — Provider layer unification: migrar `invokeTutor` legacy de `@anthropic-ai/sdk@0.96.0` a `@ai-sdk/anthropic` v3 (DSC-LF-006 propuesto)
- [ ] **D6** — Logging diferenciado abort vs error real en `onError` del stream (F-D3.2-05 plan disputado)
- [ ] **D6** — Doc drift: corregir `_DOCTRINA_D3.md §7.3` para reflejar header `x-la-forja-citations-b64` (Cowork observación menor)

## Sprint LA-FORJA-001 D3.3 — Iniciado 16-may-2026

Autorizado por Cowork audit VERDE 14/14 (commit `2ac7f81`).

### Fase 1 — Mapeo + validación versiones canónicas (anti-autoboicot)

- [x] Leer estado actual de `Chat.tsx` y `MessageBubble.tsx` (D3.2 entregó stub sin markdown ni toggle)
- [x] Validar versión canónica de `streamdown` en npm registry (real-time, no entrenamiento) — 2.5.0 vigente
- [x] Validar versión canónica de `happy-dom` en npm registry — 20.9.0 ya instalado
- [x] Validar versión canónica de `msw` en npm registry — 2.14.6 vigente; **decisión binaria: NO instalar MSW**, mockear `@ai-sdk/react` con `vi.mock` (alineado a patrón canónico Tour.test.tsx + más liviano + sin red)
- [x] Confirmar `vitest` actual del workspace soporta enfoque vi.mock — sí (vitest 4.1.6)
- [x] Verificar peer dependencies — streamdown peer react^18||^19 OK con React 19.2.6

### Fase 2 — T1: UI toggle `requireValidation` en Chat.tsx

- [x] Helper `src/lib/tutor/preferences.ts` SSR-safe + fail-soft con clave `la-forja:tutor:require-validation`
- [x] Tests `preferences.test.ts` 6/6 verde (default, round-trip, corrupt, fail-soft read/write, SSR)
- [x] State `requireValidation` internalizado en `Chat.tsx` (no más prop) con hidratación `useEffect` + persistencia
- [x] Componente toggle visual con Brand DNA (forja/graphite/acero, mono uppercase label, role='switch', aria-checked)
- [x] Sub-label dinámico: "Activa — costo adicional, mayor exactitud" / "Inactiva — respuesta rápida"
- [x] Toggle se incluye en `sendMessage()` body (preservado en `transport.body.requireValidation`)
- [x] Disabled durante streaming + pre-hidratación (no permitir cambio mid-flight)
- [x] Telemetría: log `[la-forja:tutor_validation_toggled]` con `{ prev, next }`
- [x] `<Chat />` en `page.tsx` ya no recibe prop (limpio)

### Fase 3 — T2: streamdown en MessageBubble.tsx

- [x] `npm install streamdown@2.5.0` en `apps/la-forja/web/` — 225 paquetes nuevos
- [x] Reemplazar render plano por `<Streamdown>` solo para `role='assistant'`; user mantiene `whitespace-pre-wrap`
- [x] Sanitización XSS habilitada por default (rehype-sanitize + rehype-harden internos)
- [x] Cursor blink durante streaming preservado como sibling fuera del Streamdown
- [x] Wrapper `.forja-markdown` con tokens Brand DNA (mono uppercase headings forja-300, code/pre graphite-700, table acero-700, blockquote forja-600)
- [x] Code blocks con syntax highlighting nativo de streamdown (Shiki interno)
- [x] Tests Chat.tsx cubren render markdown vs plain (assistant tiene `forja-msg-markdown`, user no) + cursor blink

### Fase 4 — T3: tests Chat.tsx (decisión binaria: vi.mock en lugar de MSW)

- [x] happy-dom 20.9.0 ya en deps; vitest config validado (`globals: false` requiere imports explícitos)
- [x] **Decisión binaria documentada**: NO instalar MSW. Usar `vi.mock("@ai-sdk/react")` + `vi.mock("ai")` + `vi.mock("streamdown")` siguiendo patrón canónico Tour.test.tsx. Más liviano, sin service workers, sin red, alineado al codebase.
- [x] Test 1: render inicial — toggle visible aria-checked=false
- [x] Test 2: hidratación localStorage true persistido
- [x] Test 3: click toggle persiste valor binario en localStorage
- [x] Test 4: toggle disabled durante streaming
- [x] Test 5: error mid-stream muestra banda + botón Reintentar invoca `regenerate()`
- [x] Test 6: composer NO envía con input vacío (sendMessage no llamado)
- [x] Test 7: composer envía texto + `sendMessage({ text })` invocado correcto
- [x] Test 8: durante streaming muestra botón Detener + `stop()` invocado
- [x] Test 9: render mensajes assistant + user con sus testids
- [x] Test 10: cursor blink solo en último assistant durante streaming
- [x] Test 11: cursor blink ausente cuando status=ready
- [x] **11/11 nuevos tests verde**, total frontend 57/57

### Fase 5 — DSC-LF-008 (markdown rendering canónico)

- [x] Redactar `discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-008_markdown_rendering_canonico.md`
- [x] Decisión: streamdown@^2.5.0 obligatorio para role='assistant'; user permanece plano; sanitización XSS no opt-out; mock vi.mock en test layer
- [x] Contratos ejecutables: `MessageBubble.tsx` + `Chat.test.tsx` + `globals.css` + `package.json`
- [x] Actualizar `_dsc_contracts_index.yaml` con DSC-LF-008 (status: enforced, 4 contratos)
- [x] Validar `tools/dsc_contract_check.py` → **6/6 LA-FORJA DSCs OK**

### Fase 6 — Validación binaria

- [x] Backend `npm test` → 180/180 verde (sin regresión)
- [x] Backend `npx tsc --noEmit` → 0 errores
- [x] Frontend `npm test` → 57/57 verde (40 base + 6 preferences + 11 Chat)
- [x] Frontend `npx tsc --noEmit` → 0 errores
- [x] Frontend `npm run build` → verde, rutas / · /onboarding · /salud · /tutor preservadas
- [x] `tools/dsc_contract_check.py` → 6/6 LA-FORJA DSCs OK

### Fase 7 — Auditoría externa (decisión)

- [ ] Decidir: lanzar audit Perplexity D3.3 (recomendable) o saltar a Cowork directo
- [ ] Si Perplexity: redactar `bridge/manus_to_perplexity_LA_FORJA_001_D3_3_AUDIT.md`
- [ ] Si Cowork directo: redactar `bridge/manus_to_cowork_LA_FORJA_001_D3_3_AUDIT_REQUEST.md`

### Fase 8 — Cierre

- [ ] Commit hardening (si Perplexity reporta)
- [ ] Audit Cowork D3.3 → veredicto
- [ ] DSC-LF-008 firmado formalmente
- [ ] PR D3.3 abierto y autorizado para merge
- [ ] Sembrar D3.4 backlog

---

## D4 — Google OAuth + JWT middleware (autorizado por Alfredo · 17-may-2026)

**Branch:** `sprint/la-forja-001-d4` (creada desde `main` post-merge `73936df5`)
**Scope ajustado:** SOLO Google OAuth (RAG diferido a D5/sprint hijo D4.5).
**Stack canónico (anti-autoboicot validado real-time):**
- `@hono/oauth-providers@0.8.5` (oficial Hono, peer hono>=3.0.0)
- `jose@6.2.3` (estándar JWT/JWS)
- `hono@4.12.18` (instalado, vigente 4.12.19, mantengo 4.12.18 por estabilidad delta)

**Decisión binaria:** JWT propio firmado con `JWT_SECRET` (ya en env) en lugar de Supabase Auth (cuyas tablas `auth.*` no están provisionadas todavía). El interface `User` se mantiene idéntico al stub D2.5 → cero ripple en routes existentes. Migración a Supabase Auth queda como deuda canónica para D5+ si T1-Alfredo lo decide.

### Endpoints

| Método | Ruta | Propósito | AC |
|---|---|---|---|
| GET | `/api/auth/google` | redirect 302 → Google OAuth consent | AC5 SPEC v3.2 |
| GET | `/api/auth/google/callback` | recibe `code`+`state`, intercambia por tokens, set cookie JWT, redirect frontend | nuevo |
| POST | `/api/auth/logout` | clear cookie, 200 | nuevo |

### Secrets requeridos

- `GOOGLE_OAUTH_CLIENT_ID` — pendiente provisión humana en Google Cloud Console
- `GOOGLE_OAUTH_CLIENT_SECRET` — pendiente provisión humana en Google Cloud Console
- `JWT_SECRET` — ya existe en env
- `OAUTH_REDIRECT_BASE_URL` — nueva, default `http://localhost:8081`, en prod debe ser dominio Railway

**Modo desarrollo:** los secrets `GOOGLE_OAUTH_*` son **opcionales si NODE_ENV !== production**. Si faltan, el endpoint `/api/auth/google` retorna 503 con mensaje claro. En producción son **obligatorios** (zod validation falla loud al boot).

### Cookie de sesión

- Nombre: `la-forja:session`
- HttpOnly: true
- Secure: true (en producción)
- SameSite: Lax (necesario para que el callback OAuth la set sin bloquearse)
- Path: `/`
- Max-Age: 7 días (604800 segundos)
- Payload JWT: `{ sub: googleSubId, email, name, picture, role, iat, exp, iss: "la-forja", aud: "la-forja-api" }`

### Middleware refactor

Mantener `forjaAuthStub()` para tests/dev legacy (sin tocar). Crear nuevo `forjaAuthGoogle()`:

- Lee cookie `la-forja:session`
- Verifica JWT con `jose.jwtVerify(token, secret, { issuer, audience })`
- Si válido → `c.set('user', { id, email, role })` y `await next()`
- Si inválido/ausente → 401

Selector en `index.ts`:
- Si `NODE_ENV === "production"` → `forjaAuthGoogle()` exclusivo
- Si `NODE_ENV === "development"` → `forjaAuthGoogle()` con fallback a `forjaAuthStub()` cuando falta cookie (para tests E2E que aún usan x-user-id)
- Si `NODE_ENV === "test"` → `forjaAuthStub()` exclusivo (preserva 180/180 backend tests sin regresión)

### Plan de ejecución D4

#### D4.0 — Pre-flight + branch

- [x] Crear branch `sprint/la-forja-001-d4` desde `main` (`73936df5`)
- [x] Verificar Railway: confirmar `GOOGLE_OAUTH_CLIENT_ID/SECRET` NO existen (verificado binariamente, 89 vars revisadas)
- [x] Decisión: implementar código completo con mocks, secrets reales pueden agregarse en paralelo o D6
- [ ] Actualizar `todo.md` con plan D4 detallado

#### D4.1 — Env strict + JWT helper

- [ ] Extender `src/lib/env.ts` con `GOOGLE_OAUTH_CLIENT_ID/SECRET/REDIRECT_BASE_URL/JWT_SECRET` (zod refinement: requeridos solo si NODE_ENV=production)
- [ ] `src/lib/jwt.ts` con `signSession(user, secret)` y `verifySession(token, secret)` usando `jose.SignJWT` + `jwtVerify` con HS256
- [ ] Tests: round-trip sign+verify, expiración, issuer/audience mismatch, secret incorrecto

#### D4.2 — Routes auth

- [ ] `src/routes/auth.ts` con 3 endpoints
- [ ] Usar `googleAuth({ client_id, client_secret, scope: ['openid', 'email', 'profile'] })` de `@hono/oauth-providers/google`
- [ ] Callback: extraer `googleUser` desde `c.get('user-google')`, generar JWT, set cookie, redirect a `${FRONTEND_URL}/post-login`
- [ ] Logout: clear cookie via `setCookie(c, 'la-forja:session', '', { maxAge: 0 })`, 200 OK
- [ ] Tests: 302 redirect, 503 sin secrets en dev, callback con code mock, logout limpia cookie

#### D4.3 — Middleware forjaAuthGoogle

- [ ] Refactor `src/middleware/auth.ts` agregando `forjaAuthGoogle()` (no eliminar stub)
- [ ] Selector binario por NODE_ENV en `index.ts`
- [ ] Tests: cookie válida → next, cookie inválida → 401, cookie expirada → 401, fallback stub en dev

#### D4.4 — Wiring index.ts

- [ ] Importar y montar `authRoutes` en `/api/auth`
- [ ] Aplicar selector middleware a rutas protegidas
- [ ] Tests integración: GET /api/auth/google → 302 con Location header válido

#### D4.5 — Validación binaria

- [ ] Backend `npm test` → todos verde (180 base + N nuevos)
- [ ] Backend `npx tsc --noEmit` → 0 errores
- [ ] Backend `npm run lint` → 0 errores
- [ ] Backend `npm run build` → verde
- [ ] Frontend sin cambios pero correr suite igual para garantizar 0 regresión
- [ ] `tools/dsc_contract_check.py` → 6/6 LA-FORJA DSCs OK
- [ ] AC5 SPEC: `curl -fsSL http://localhost:8081/api/auth/google -I` → 302 con Location apuntando a accounts.google.com

#### D4.6 — DSC-LF-009 (Google OAuth canónico)

- [ ] Redactar `discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-009_google_oauth_canonico.md`
- [ ] Documentar: stack `@hono/oauth-providers@0.8.5` + `jose@6.2.3`, JWT propio (no Supabase Auth), cookie HttpOnly+Secure+Lax, selector por NODE_ENV
- [ ] Actualizar `_dsc_contracts_index.yaml` con DSC-LF-009 (4-5 contratos ejecutables)
- [ ] Validar dsc_contract_check.py → 7/7 LA-FORJA OK

#### D4.7 — Bridge + PR

- [ ] Redactar `bridge/manus_to_cowork_LA_FORJA_001_D4_AUDIT_REQUEST.md` con 12 puntos binarios + reproducción de gates
- [ ] Commit + push branch
- [ ] Abrir PR draft hacia `main`
- [ ] Esperar audit Cowork → fix si AMARILLO → merge si VERDE
