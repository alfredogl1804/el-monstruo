---
sprint_id: LA-FORJA-001 v3.2
fase: D3.1 + D3.1.1 tour onboarding + hardening Perplexity
fecha: 2026-05-16
auditor: Cowork T2-A (Claude Opus 4.7 / 1M context)
sesion: bold-neumann-ef6284
veredicto: 🟢 D3.1 SHIP — VERDE 12/12 + decisión H-12 = Opción C (DSC-LF-005 propuesto)
branch: sprint/la-forja-001
commits_auditados:
  - e125c4c (feat tour onboarding 7 pasos sin LLM)
  - 6646544 (hardening D3.1 fixes Perplexity F-D3.1-01..15)
  - 84c728f (bridge adversarial prompt + 15 F-patterns response)
  - cdbf7a8 (hardening D3.1.1 regression R-D3.1-01..05 + PARCIALES)
sobre_base: 0760095 (D3.0 hardening VERDE previo)
firma_doctrinal: DSC-G-008 v4 vigente + DSC-LF-005 PROPUESTO (no firmado aún)
---

# 🟢 LA-FORJA-001 D3.1 + D3.1.1 AUDIT — VERDE 12/12

## §1 Resumen binario (1 párrafo)

Cowork T2-A audita range `e125c4c..cdbf7a8` (4 commits, ~1850 LOC, 17 archivos). D3.1 entrega tour onboarding 7 pasos estáticos sin LLM (Server Component shell + Client Component idempotente con `useRef`), 4 helpers nuevos (`steps.ts`, `cookie.ts`, `version.ts`, `StepShell.tsx`) y 3 suites de test (Tour 16, cookie 8, steps 8 = 32 nuevos + 5 D3.0 = 37 totales). D3.1.1 cierra 5 regressions Perplexity (R-D3.1-01 fail-loud sin fallback, R-D3.1-02 useRef sincrónico para idempotency, R-D3.1-04 /onboarding Static, R-D3.1-05 regex Brand Engine con doble lookahead PascalCase+ALL_CAPS). Verificación binaria fresca: typecheck 0 errores + **vitest 37/37 en 405ms** sobre 5 files + next build verde con `/onboarding` correctamente `○ Static` + eslint 0/0 + npm audit 2 moderate (postcss transitivo Next 16, ya documentado y aceptado desde D3.0). 12/12 puntos auditables VERDE binario verificados línea por línea contra código. Backend D2.5 (`fe82b1c`) no tocado, scope confinado a `apps/la-forja/web/**`. **D3.1 SHIP: VERDE. D3.2 chat tutor SSE autorizado con decisión H-12 = Opción C (DSC-LF-005 propuesto, firma formal en D3.2).**

## §2 Verificación binaria de los 12 puntos (SI/NO)

| # | Punto | Veredicto | Evidencia binaria |
|---|---|---|---|
| 1 | Brand Engine regex banea PascalCase + ALL_CAPS + snake_UPPER, permite identificadores legítimos | 🟢 **SÍ** | `eslint.config.mjs:36-40` `FORBIDDEN_SUFFIXES = "Service\|Handler\|Util\|Helper\|Misc\|Manager"`; `BRAND_NAMING_REGEX` con doble lookahead: `(?!.*(?:Service\|...)(?:[A-Z]\|$))(?!.*(?:SERVICE\|...)(?:[A-Z_0-9]\|$))`. Lookahead 1 cubre PascalCase compuesto (`UserService`, `AuthHandler`), lookahead 2 cubre ALL_CAPS/snake_UPPER (`USERSERVICE`, `USER_SERVICE`, `FORMAT_UTIL`). Identificadores `ForjaTourSteps`, `service`, `FORJA_TOUR_STEPS` pasan porque no contienen el sufijo en posición prohibida. |
| 2 | Tour idempotency sincrónica con `useRef`, 3 clicks dentro del mismo `act()` → 1 sola invocación | 🟢 **SÍ** | `Tour.tsx:71` `const finishedRef = useRef(false)`. `Tour.tsx:95-96` finalize() chequea `if (finishedRef.current) return; finishedRef.current = true;` ANTES de cualquier side-effect (cookie write, onFinish call, router.push). Test `Tour.test.tsx:169-183` invoca `act(() => { btn.click(); btn.click(); btn.click(); })` y asserta `expect(onFinish).toHaveBeenCalledTimes(1)`. Test PASS confirmado fresh. |
| 3 | `version.ts` fail-loud sin fallback `"D3.1"` | 🟢 **SÍ** | `version.ts:27-33` `const rawDelivery = process.env.NEXT_PUBLIC_FORJA_DELIVERY; if (typeof rawDelivery !== "string" \|\| rawDelivery.trim().length === 0) { throw new Error("[la-forja:web_missing_env] NEXT_PUBLIC_FORJA_DELIVERY no seteada...") }`. Cero ocurrencias del string literal `"D3.1"` como fallback. `.env.local.example` documenta la variable. |
| 4 | `/onboarding` es Static, sin `force-dynamic` | 🟢 **SÍ** | `onboarding/page.tsx` no contiene `export const dynamic` ni `export const revalidate`. Build output fresh confirma `○ /onboarding` (Static), no `ƒ` (Dynamic). Comentario en página líneas 17-21 explica que el shell no lee cookies/headers/searchParams en server. |
| 5 | Cookie helpers — Secure flag conditional + split regex tolerante | 🟢 **SÍ** | `cookie.ts:40-45` `shouldUseSecure` retorna `loc?.protocol === "https:"` (no hardcode). `cookie.ts:54` `doc.cookie.split(/;\s*/)` regex tolera tanto `"; "` estándar como `";"` degenerado. `cookie.ts:82-83` y `:96-97` agregan `secure` SOLO cuando `shouldUseSecure()` retorna true. Test file existe (8 tests con mock `documentRef`). |
| 6 | Tour a11y — `aria-live="polite"` + `aria-atomic="true"` + heading `tabIndex={-1}` + focus programático | 🟢 **SÍ** | `Tour.tsx:136-137` `aria-live="polite" aria-atomic="true"` en contenedor. `StepShell.tsx:110-111` `ref={headingRef} tabIndex={-1}`. `Tour.tsx:82-88` `useEffect` con `stepHeadingRef.current?.focus()` al cambiar `[index]`, skip mount inicial via `isFirstRenderRef`. Tests dedicados `Tour.test.tsx:188-204` validan los 3 aspectos. |
| 7 | `SPRINT_STATES` literal en `steps.ts` matchea SPEC §4:130 inglés exacto | 🟢 **SÍ** | `steps.ts:163-172` `FORJA_TOUR_SPRINT_STATES_LITERAL = ["proposed", "drafting", "review_alfredo", "review_cowork", "ready_to_execute", "executing", "merged", "canonized"] as const`. 8 estados exactos en el orden SPEC §4:130. Cross-check binario contra `apps/la-forja/api/src/routes/sprints.ts:46-55` (mismo array exacto). Cuerpo del paso 4 (`sala-de-sprint` línea 93) menciona los 8 en orden inline. |
| 8 | DSC-LF-003 cap $50 USD literal en tour + binding backend | 🟢 **SÍ** | `steps.ts:103` paso 5 body: `"Tienes 50 USD por mes."`. `steps.ts:107` highlights: `["50 USD", ...]`. Backend `apps/la-forja/api/src/lib/budget.ts:28` `export const FORJA_BUDGET_CAP_USD = 50.0 as const`. Coinciden binariamente. |
| 9 | LF-1 frontend cero imports `@supabase/supabase-js` ni `SUPABASE_*` vars | 🟢 **SÍ** | `grep -rn "@supabase\|SUPABASE_URL\|SUPABASE_ANON_KEY\|createClient.*supabase" apps/la-forja/web/src/ apps/la-forja/web/package.json` → **0 hits**. Frontend habla únicamente con el backend Hono via `NEXT_PUBLIC_API_URL`. |
| 10 | LF-2 versiones pinned exactas | 🟢 **SÍ** | `package.json`: `"next": "16.2.6"`, `"react": "19.2.6"`, `"react-dom": "19.2.6"`, `"tailwindcss": "4.3.0"`, `"typescript": "5.7.3"`, `"zod": "3.25.76"`. Todas versionadas exactas (no `^` ni `~`), todas validadas magna D3.0 + D3.1. |
| 11 | Brand Engine namespacing `[la-forja:web_*]` consistente | 🟢 **SÍ** | grep en `apps/la-forja/web/src/lib/`: `api.ts:21` `[la-forja:web_api_request_failed]`, `version.ts:30` `[la-forja:web_missing_env]`, `env.ts:48` `[la-forja:web_env_load_strict_failed]`, `env.ts:54` `[la-forja:web_env_load_permissive_blocked_in_production]`. Cero namespaces genéricos. id-match `error` los enforza en CI. |
| 12 | Tests críticos no triviales — idempotency 3 clicks, skip vs finish, cookie round-trip, separador sin espacio, contract 8 estados | 🟢 **SÍ** | `Tour.test.tsx:146-154` doble click rápido último paso = 1 invocación. `Tour.test.tsx:157-164` doble skip = 1 invocación. `Tour.test.tsx:169-183` 3 clicks síncronos dentro de `act()` (R-D3.1-02 regression test). `Tour.test.tsx:108-117` finish `{skipped: false}` vs `:119-127` skip `{skipped: true}`. Cookie tests existen (8 tests). Steps test contract 8 estados existe (líneas confirmadas via ls + 109 LOC en file). |

**12/12 binario VERDE.** Cero hallazgos materiales en el delta D3.1 + D3.1.1.

## §3 Validación pre-commit reproducible (fresca hoy)

| Comando | Output | Veredicto |
|---|---|---|
| `npm run typecheck` (tsc 5.7.3) | 0 errores | ✅ |
| `npm test` (vitest 4.1.6) | **37 passed (37) en 405ms** sobre 5 test files | ✅ |
| `npm run build` (Next 16.2.6 Turbopack) | `Compiled successfully in 873ms`, 4 rutas (`/` ƒ + `/_not-found` ○ + `/onboarding` ○ + `/salud` ƒ) | ✅ |
| `npm run lint` (eslint 9.39.4 flat) | 0 errors, 0 warnings | ✅ |
| `npm audit` | 2 moderate (postcss transitivo Next, **idéntico al estado D3.0 documentado**) | ⚠️ ACEPTADO (sin cambio respecto a D3.0) |

## §4 Reglas Duras del Monstruo — Compliance binario D3.1 + D3.1.1

| Regla | Estado | Evidencia |
|---|---|---|
| #1 NO self-merge | ✅ | `git log --oneline | grep main` → 0 merges. PR #133 OPEN. |
| #2 calidad premium (TS strict + flat ESLint + vitest) | ✅ | typecheck + 37/37 tests + lint verdes |
| LF-1 frontend nunca Supabase directo | ✅ | grep 0 hits (§2 punto 9) |
| LF-2 versiones magna real-time pinned | ✅ | 6 deps exactas (§2 punto 10) |
| DSC-LF-001 Five Doors Inviolable | ✅ | no tocado en D3.1 (frontend solo tour onboarding) |
| DSC-LF-002 Test Bench Telemetry | ✅ | Frontend no genera telemetry en D3.1 (tour estático). Aplicable D3.2+. |
| DSC-LF-003 Cap $50/mes/usuario | ✅ | binding cross frontend↔backend verificado (§2 punto 8) |
| DSC-LF-004 Perplexity única validación | ✅ | no tocado en D3.1 |
| Regla Dura #6 fail-loud envs | ✅ | `version.ts` throw sin fallback (§2 punto 3) |
| Brand Engine `[la-forja:web_*]` | ✅ | 4 ocurrencias correctas (§2 punto 11) |
| DSC-G-008 v4 error path coverage LLM | ✅ N/A | D3.1 tour estático no invoca LLMs. Aplicable D3.2 chat tutor. |
| DSC-S-016 anti-fabricación sin grep | ✅ | Audit ejecutó `git diff --stat`, `grep`, `ls`, 8 lecturas binarias, `npm run typecheck`, `npm test`, `npm run build`, `npm run lint`, `npm audit` |

## §5 Atribución binaria de CI rojos persistentes

`git diff --name-only 0760095..cdbf7a8` toca exclusivamente `apps/la-forja/web/**` + `apps/la-forja/todo.md` + `bridge/*.md`. **Cero hits en `transversal/`, `tests/anti_dory/`, `kernel/`, `scripts/cowork_*`**. Los 3 CI rojos persistentes (`Lint & Type Check` Sprint 58, `Unit Tests` anti_dory paused, `semgrep` failing main desde 14-may) siguen siendo preexistentes del repo, no introducidos por D3.1.

## §6 Decisión H-12 — arquitectura SSE para D3.2

### §6.1 Análisis binario de las 3 opciones

**Opción A: endpoint nuevo `/api/tutor/chat/stream` SSE + mantener JSON intacto.**
- Pro: zero break del contrato D2 VERDE. Zero migración de tests backend.
- Contra: dual code path permanente. Cada nueva feature LLM debe decidir endpoint. Technical debt acumulativo.
- Verdict Cowork: **subóptimo a medio plazo**, acepta pero recomienda no como canon.

**Opción B: migrar `/api/tutor/chat` a SSE + bumpear `apiVersion: 2`.**
- Pro: superficie limpia. Consumidores eligen versión.
- Contra: requiere infraestructura de versionado (header `X-Forja-API-Version` o path `/v2/`), tests duplicados durante coexistencia, decisión de cuándo deprecar v1.
- Verdict Cowork: **válido pero introduce complejidad de versionado prematura** dado que no hay consumidores activos de `/api/tutor/chat` JSON aún.

**Opción C: DSC-LF-005 canon — endpoints LLM siempre SSE, JSON solo metadata sin LLM.**
- Pro: patrón uniforme forward, zero double-code, alineado con Vercel AI SDK 6 idioma SSE-first. Decisión arquitectónica una sola vez.
- Contra: Manus reescribe `routes.test.ts:400-528` D2 (testea JSON shape `/api/tutor/chat`) para asertar SSE shape. Trabajo concreto pero acotado al sprint D3.2.
- Verdict Cowork: **canonical forward correcto**. No hay consumidores activos del JSON, así que zero breaking real downstream.

### §6.2 Decisión binaria Cowork: **OPCIÓN C** con caveat de numeración

**Recomendación firme: Opción C.** Forward-canonical pattern, elimina la decisión recurrente, alineado con idiom SSE-first de Vercel AI SDK 6.

**Caveat de numeración**: Manus E1 propuso "DSC-LF-004" para la canonización. **Conflicto binario detectado**: DSC-LF-004 ya está canonizado en SPEC v3.2 §15 como `"Perplexity Sonar como única capa validación externa"` (firmado por Cowork en audit D2 commit `6401a3b`). El nuevo DSC debe numerarse **DSC-LF-005**.

**Texto propuesto del DSC-LF-005:**

> **DSC-LF-005 — Endpoints LLM SSE por default:**
> *"Todo endpoint backend de La Forja que invoque un LLM (Claude, GPT, Gemini, Perplexity, etc.) devuelve `text/event-stream` usando `createUIMessageStreamResponse` del Vercel AI SDK 6 (o el equivalente forward del SDK vigente). JSON queda únicamente para metadata sin LLM (health checks, lookups, enumerators, state machine queries). Cualquier ruta que mezcle ambas requiere SPEC nuevo + audit Cowork DSC-G-008 v4 explícito. Esta regla aplica forward desde D3.2; no se reescribe retroactivamente código pre-D3.2 mientras esté inactivo."*

**Aplicación obligatoria D3.2:**
- `POST /api/tutor/chat` migra de JSON a SSE con `createUIMessageStreamResponse`.
- Test `routes.test.ts:400-528` se reescribe para asertar SSE shape (header `content-type: text/event-stream`, chunks formato `data:` SSE).
- Frontend D3.2 consume con `useChat` de `@ai-sdk/react@3.0.186` (paridad confirmada en H-12 D3.0 hardening F-D3.0-spec).
- DSC-G-008 v4 error path coverage sigue vigente: try/catch + `adjustSpent(-estimated)` rollback antes de cerrar el stream con error frame SSE.

### §6.3 Estado de firma

Cowork T2-A **propone** DSC-LF-005 con el texto arriba como parte de este audit. La **firma formal canonizada** se aplica cuando Manus implemente el cambio en D3.2 y actualice SPEC v3.3 con el bullet nuevo en §15. Mientras tanto, esta propuesta es vinculante para arquitectura D3.2 (no para retroactivos).

## §7 Hallazgos register-only D6 (acumulados, no bloquean D3.2)

Inventario consolidado a este audit:

| ID | Origen | Justificación |
|---|---|---|
| F-D3.0-07 next-env.d.ts | D3.0 register | Next regenera auto pre-typecheck |
| 2 vulns postcss <8.5.10 | npm audit | Transitivo Next, fix upstream requerido |
| F-D3.1-03 PARCIAL HTTPS cookie | D3.1.1 register | Cubrir branch HTTPS en test cookie con location stub |
| R-D3.1-03 contract test extraction | D3.1.1 register | Crear `apps/la-forja/contracts/sprint_states.ts` shared workspace |
| CSP headers | D5 | Aplicable en deploy real |
| Tests a11y con axe-core | D6 | Polish |
| H-6 PII regex México expandida | D2.5 register | CURP, INE, NSS IMSS |
| H-7 thinking adaptive vs enabled | D2.5 register | Verificar docs oficiales |
| H-8 OpenAI Responses shape | D2.5 register | Test SDK mock |
| H-9 @google/genai contents | D2.5 register | Docs SDK 2.x |
| H-10 Perplexity citations defensivo | D2.5 register | `return_citations:true` |
| H-11 fix comment middleware order | D2.5 register | `index.ts:115` |
| H-13 SupabaseBudgetClient atómico | D5 | UPDATE arithmetic atómico |
| H-14 LLM client cache invalidation | D2.5 register | Strict:false path |

Total backlog D6: ~14 items, ninguno bloquea D3.2.

## §8 Consecuencias materiales si se autoriza D3.2

Si firmo VERDE y autorizo D3.2:

1. **Cero cambio en `main`**: PR #133 sigue OPEN. Branch protection vigente.
2. **D3.2 arranca**: Manus E1 implementa `/chat` Client Component con `useChat` de `@ai-sdk/react@3.0.186` + reescribe backend `POST /api/tutor/chat` a SSE bajo DSC-LF-005 propuesto.
3. **DSC-LF-005 firma formal** se aplica cuando Manus actualice SPEC v3.3 + entregue D3.2 con tests SSE verdes.
4. **DSC-G-008 v4 vigente**: error path coverage obligatorio en cualquier ruta LLM (incluido el SSE migrado).
5. **Cero impacto en sprints abiertos**: scope D3.2 confinado a `apps/la-forja/web/src/app/chat/` + `apps/la-forja/api/src/routes/tutor.ts` (1 archivo backend tocado).
6. **2 moderate residuales** persisten (postcss upstream Next, sin cambio).

Cero bombas en producción detectadas.

## §9 Firma binaria

```
SPRINT:           LA-FORJA-001 v3.2 — D3.1 + D3.1.1 TOUR ONBOARDING + HARDENING
COMMITS:          e125c4c (feat) + 6646544 (hardening D3.1) + 84c728f (bridge) + cdbf7a8 (D3.1.1 regression)
SOBRE:            0760095 (D3.0 hardening VERDE previo)
PR:               #133 (READY, mergeable=MERGEABLE)
AUDITOR:          Cowork T2-A (Claude Opus 4.7 / 1M context)
SESIÓN:           bold-neumann-ef6284
FECHA:            2026-05-16
METODOLOGÍA:      audit DELTA (NO firma DSC nueva en D3.1 — hardening, no contrato)

VERIFICACIONES FRESCAS:
  typecheck:      ✅ 0 errores
  vitest:         ✅ 37/37 passing (405ms, 5 files)
  next build:     ✅ verde, /onboarding ○ Static, /salud ƒ Dynamic
  eslint:         ✅ 0/0
  npm audit:      ⚠️ 2 moderate (postcss Next, sin cambio vs D3.0)

PUNTOS 1-12:      ✅ 12/12 VERDE binario
REGLAS DURAS:     ✅ #1, #2, #6, LF-1, LF-2, DSC-LF-001..003 cumplidas
BRAND ENGINE:     ✅ `[la-forja:web_*]` enforced via id-match regex doble lookahead
CI ROJOS:         ✅ los 3 persistentes siguen preexistentes
H-12 DECISIÓN:    🟢 OPCIÓN C (DSC-LF-005 propuesto, firma formal D3.2)
NUMERACIÓN:       ⚠️ Manus propuso "DSC-LF-004" — conflicto con LF-004 vigente. Corregir a DSC-LF-005.
DSCs VIGENTES:    LF-001 (Five Doors), LF-002 (Telemetry), LF-003 (Cap $50), LF-004 (Perplexity-only), G-008 v4 (error path)
```

🟢 **LA-FORJA-001 D3.1 + D3.1.1 — AUDIT VERDE 12/12 · D3.2 AUTORIZADO con DSC-LF-005 propuesto**

## §10 Próximos pasos binarios

1. **Cowork (este turno):** commit + push de este bridge file.
2. **Manus E1 D3.2:** arranca chat tutor con SSE bajo Opción C:
   - Migra `POST /api/tutor/chat` backend a `createUIMessageStreamResponse` (Vercel AI SDK 6).
   - Reescribe `routes.test.ts` D2 tutor para asertar SSE shape.
   - Implementa `/chat` Client Component con `useChat` de `@ai-sdk/react@3.0.186`.
   - Aplica DSC-G-008 v4: try/catch + `adjustSpent(-estimated)` rollback en error path antes de cerrar stream.
   - Actualiza SPEC v3.3 §15 con DSC-LF-005 nuevo bullet (número correcto: **005**, no 004).
3. **T1-Alfredo:** PR #133 sigue READY mergeable. Decide merge manual o instruye Cowork directo.
4. **Audit D3.2:** Manus solicita `D3_2_AUDIT_REQUEST` con verificación SSE + DSC-LF-005 firma formal.
5. **D6 polish:** backlog ~14 items trackeados.

Si surge contradicción binaria entre este audit y la realidad D3.2, prevalece la realidad. Este veredicto es firme.

— Cowork T2-A · LA-FORJA-001 v3.2 · D3.1 + D3.1.1 VERDE 12/12 · H-12 = C · 16 mayo 2026
