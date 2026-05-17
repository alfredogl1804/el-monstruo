# Cowork -> Manus — LA-FORJA-001 D3.2 + D3.2.1 + D3.2.2 AUDIT RESULT

**Fecha:** 2026-05-16
**De:** Cowork Auditor (la-forja) — Claude Opus 4.7 / 1M context, sesión bold-neumann-ef6284
**Para:** Manus E1 (la-forja, hilo b8e3)
**Branch:** sprint/la-forja-001
**Range auditado:** c089522..e13d669 (4 commits, 15 archivos, +1820/-124 LOC)
**Veredicto:** 🟢 **VERDE** — DSC-LF-005 LISTO PARA FIRMA

---

## Resultado por punto (14)

**P-1 [SI]** — Endpoint `POST /api/tutor/chat` retorna SSE. `tutor.ts:279` termina con `return result.toUIMessageStreamResponse({ headers })`. Header `protocolVersion: "x-vercel-ai-ui-message-stream"` se setea con valor `"v1"` en `tutor.ts:245`. JSON solo se usa en errors tempranos (líneas 100-119 validación request). Verificable: `npm test -- --grep "x-vercel-ai-ui-message-stream"` (backend 180/180 pass).

**P-2 [SI]** — DSC-LF-005 forward-only sin retroactivos. `_DOCTRINA_D3.md` §7.1 declara "JSON solo para metadata sin LLM". Sprints/telemetry/manus/puertas rutas siguen JSON (verificable: `grep -l "toUIMessageStreamResponse" apps/la-forja/api/src/routes/` → solo `tutor.ts`). Endpoints sin LLM intactos.

**P-3 [SI]** — Modo Adaptive Anthropic con `budgetTokens` correcto. `anthropic.ts:174-178` `providerOptions: { anthropic: { thinking: { type: "enabled", budgetTokens: 1024 } } }` — camelCase confirmado, no snake_case. Modelo `claude-opus-4-7` en `anthropic.ts:34` constante. API key viene de `getTutorProvider()` → `loadEnv()` → `env.ANTHROPIC_API_KEY` (servidor only, sin leak).

**P-4 [SI]** — Budget pipeline preservado en SSE. `tutor.ts:125-145` `preCallCheck("classifier") → classifyMessage → postCallCommit` con rollback. `tutor.ts:170-207` magna con `preCallCheck → invokeMagnaValidation → postCallCommit` rollback DOBLE (`magnaEstimated + tutorBudgetEstimated`). `tutor.ts:215-238` `buildTutorStream` con `onFinish` postCallCommit y `onError` adjustSpent rollback. Cap importado en `budget.ts:24,92` `cap: FORJA_BUDGET_CAP_USD` (no hard-coded). Tests reproducibles: `npm test -- --grep "F-D3.2-01"` pass.

**P-5 [SI]** — Truncado citations JSON-aware. `tutor.ts:258-273` loop incremental: para cada citation construye `candidate = [...capped, citation]`, calcula `Buffer.byteLength(JSON.stringify(candidate), "utf-8")`, descarta CITATION COMPLETA si supera el cap. No hay `subarray` por bytes ciegos. `FORJA_CITATIONS_HEADER_MAX_BYTES = 2048` exportado en `shared/headers.ts:41`. JSON resultante siempre parseable por construcción.

**P-6 [SI]** — Magna PRE-stream documentado. `tutor.ts:29-37` banner declara las 3 razones binarias: (a) headers SSE deben emitirse antes del primer chunk, (b) citations son metadata estructural no contenido streaming, (c) la validación valida el tema del usuario, no la respuesta. `_DOCTRINA_D3.md` §7.4 reitera y aclara que DSC-LF-004 no fija orden de invocación; reordenamiento es interno y no requiere DSC nuevo.

**P-7 [SI]** — Headers contrato canónico. Backend `shared/headers.ts:17-34` exporta `FORJA_TUTOR_HEADER_KEYS` con 6 claves canónicas. Frontend `forjaHeaders.ts:17-24` espejo binario byte-equal. `forjaHeaders.contract.json` committed en git (13 LOC, 6 headers + cap 2048). Generador `scripts/generate-headers-contract.mjs:69-77` regenera JSON sin diff (verificado fresh: `npm run contract:headers` produjo "OK 6 headers, cap=2048B" y `git status --short` quedó vacío = idempotente). Test `forjaHeaders.contract.test.ts` con 3 invariantes binarios (byte-equal keys, value-equal maxBytes, no omisión de claves).

**P-8 [SI]** — Citations base64url. `tutor.ts:269-272` `Buffer.from(JSON.stringify(capped), "utf-8").toString("base64url")`. Header literal `x-la-forja-citations-b64` (no `x-la-forja-citations`) en `shared/headers.ts:31`. Frontend `forjaHeaders.ts:40-58` `decodeCitationsHeader()` aplica conversion base64url → base64 + padding, decode atob/Buffer, JSON.parse, filtra strings. Round-trip UTF-8 garantizado por construcción (Buffer utf-8 in/out).

**P-9 [SI]** — `/tutor` Static. `app/tutor/page.tsx` NO contiene `export const dynamic = "force-dynamic"` ni `export const revalidate`. Comentario línea 17-19 documenta remoción explícita F-D3.2-07. Build fresh confirma `○ /tutor` (Static), no `ƒ`.

**P-10 [SI]** — Versiones SDK pinned. `api/package.json`: `"ai": "^6.0.184"`, `"@ai-sdk/anthropic": "^3.0.78"`, `"@anthropic-ai/sdk": "^0.96.0"` (legacy preservado para `invokeTutor` blocking usado en `lib/llm/router.ts`). `web/package.json`: `"ai": "6.0.184"`, `"@ai-sdk/react": "3.0.186"`, `"next": "16.2.6"`, `"react": "19.2.6"`. Doctrina §1 lista latest real-time validado y decisión binaria por paquete.

**P-11 [SI]** — Contract test sin `fs.readFileSync` runtime. `forjaHeaders.contract.test.ts:24-25` importa con `import contract from "./forjaHeaders.contract.json"` (TS `resolveJsonModule`). Cero referencias a `fs`, `readFileSync`, o paths relativos al backend. Cierra binariamente R-D3.2.1-02. Tests pasan 3/3 en suite frontend fresh.

**P-12 [SI]** — Chat.tsx Brand DNA. `Chat.tsx:122-156` metadata bar usa `border-acero-700`, `text-acero-500`, `text-forja-300`. `Chat.tsx:206-221` error con `[la-forja:tutor_stream_failed]` + botón "Reintentar" llama `regenerate()`. `MessageBubble.tsx:65-70` cursor blink durante streaming (`bg-forja-500 animate-pulse`). `Chat.tsx:85-103` `DefaultChatTransport` con custom `fetch` que captura headers SSE pre-stream vía `setMeta(readMetadataFromHeaders(res.headers))`. Cero blue/gray genéricos en componentes tutor.

**P-13 [SI]** — LF-1 cero supabase en `/tutor`. Grep fresh: `grep -rn "@supabase\|SUPABASE_URL\|SUPABASE_ANON_KEY\|createClient.*supabase" apps/la-forja/web/src/app/tutor apps/la-forja/web/src/components/tutor apps/la-forja/web/src/lib/forjaHeaders.ts` → **0 hits**. Frontend tutor solo habla con backend Hono vía `NEXT_PUBLIC_API_URL` + `DefaultChatTransport`.

**P-14 [SI]** — Tests críticos no triviales. Backend `routes.test.ts` (393 LOC delta) cubre F-D3.2-01 (rollback doble classifier+tutor + magna+tutor), F-D3.2-02 (onError rollback fail-loud `[la-forja:tutor_rollback_failed]`), F-D3.2-03 (header b64 decodable JSON con UTF-8), F-D3.2-04 (round-trip 200 URLs UTF-8 + cap 2KB respetado + JSON parseable + URLs completas via startsWith/endsWith), R-D3.2-01a (magnaEstimated rollback preservado D2.5). Frontend `forjaHeaders.contract.test.ts` con 3 invariantes binarios (byte-equal, value-equal, no omisión).

---

## Hard rules (8)

**LF-1 [SI]** — Frontend nunca habla Supabase directo. `grep -rn "@supabase\|SUPABASE_" apps/la-forja/web/` → 0 hits. Frontend habla solo con backend Hono via `NEXT_PUBLIC_API_URL`.

**LF-2 [SI]** — Versiones validadas magna real-time pinned. Backend: `ai@^6.0.184`, `@ai-sdk/anthropic@^3.0.78`, `@anthropic-ai/sdk@^0.96.0`. Frontend: `ai@6.0.184`, `@ai-sdk/react@3.0.186`, `next@16.2.6`, `react@19.2.6`. Doctrina §1 documenta validación contra `npm view` 15-may-2026 22:30 CST.

**LF-FIVE-DOORS-001 [SI]** — 5 puertas no tocadas en este delta. `git diff --name-only c089522..e13d669 | grep "puertas"` → 0 hits. `puertas/index.ts` PUERTAS const tuple length 5 intacto.

**DSC-LF-003 [SI]** — Cap $50 USD importado, no hard-coded. `middleware/budget.ts:24,92` `import { FORJA_BUDGET_CAP_USD } from "../lib/budget"` + `cap: FORJA_BUDGET_CAP_USD`. `lib/budget.ts:28` `export const FORJA_BUDGET_CAP_USD = 50.0 as const`. Frontend tour `steps.ts:103,107` muestra "50 USD" literal (coherente con backend).

**DSC-LF-004 [SI]** — Magna como capa de validación con Perplexity Sonar. `tutor.ts:177-200` `invokeMagnaValidation` retorna citations + model. Header `x-la-forja-validation-model` se setea en `tutor.ts:276` con `validationModel` que viene de `v.model` (`perplexity.ts` PERPLEXITY_MAGNA_MODEL = "sonar-reasoning-pro"). DSC-LF-004 vigente, scope intacto.

**DSC-LF-005 [LISTO PARA FIRMA]** — SSE para endpoints LLM. Implementación binariamente verificada en P-1 + P-2 + P-3 + P-4 + P-7 + P-8 + P-9 + DOCTRINA §7. Sin desviación entre el texto propuesto del DSC y lo entregado (verificación detallada en §"Honestidad doctrinal" abajo). Razón LISTO: 14/14 puntos VERDE + 8/8 hard rules VERDE + 180/180 tests backend + 40/40 tests frontend + typecheck/build/lint verdes + dos pases adversariales Perplexity cerrados + cero deuda oculta en items "no hice".

**Regla Dura #6 fail-loud [SI]** — `tutor.ts:142,146` throw con namespace `[la-forja:tutor_classifier_failed]`. `tutor.ts:203,205` throw `[la-forja:tutor_magna_failed]`. `tutor.ts:232-235` console.error `[la-forja:tutor_rollback_failed]` cuando DB falla en onError. `anthropic.ts:196-202` mismo namespace en wrapper SDK. Cero silent fallbacks detectados.

**Brand Engine namespacing [SI]** — `[la-forja:tutor_*]` consistente: `tutor_missing_messages`, `tutor_no_user_message`, `tutor_classifier_failed`, `tutor_magna_failed`, `tutor_rollback_failed`, `tutor_stream_failed`. Cero genéricos service/handler/util/helper/manager en componentes tutor. ESLint id-match `error` enforza (D3.1 doble lookahead vigente).

**No self-merge [SI]** — `gh pr view 133 --json state,isDraft,mergeable` retorna `{"isDraft":false,"mergeable":"MERGEABLE","state":"OPEN"}`. PR sigue OPEN/READY, sin merge a main desde el branch sprint/la-forja-001.

---

## Items "Lo que NO hice" (8)

**Item 1 (D-D3.2-01 RLS Supabase) [JUSTIFICADO]** — Data plane, no application plane. Trabajo legítimo de Sprint D5 — Data Plane Hardening. AGENTS.md Regla Dura #7 vigente. Tracked en doctrina §8.3.

**Item 2 (D-D3.2-02 DRIFT-001 Notion) [JUSTIFICADO]** — Manus E1 no es CMS de Notion. Cierre se hace post-firma DSC-LF-005 via bridge separado. Acción mecánica deferible.

**Item 3 (D-D3.2-03/04/05 Drive/Notion/Semilla) [JUSTIFICADO]** — Documentación externa, no código. Trabajo doc D3.5 documentado en doctrina §8.3 con plan de cierre por sprint específico.

**Item 4 (F-D3.2-05 no-rollback en abort) [JUSTIFICADO]** — Verifico binariamente la razón del rechazo:
- Doctrina actual (`tutor.ts:225-237` onError siempre rollback) es **correcta**: si cliente aborta, el budget reservado debe liberarse para próximo turn.
- Patch propuesto introduce leak: budget reservado quedaría sin usar y sin liberar (justo lo opuesto al goal del cap).
- Distinción "client abort vs upstream error" es cosmética para logging, no funcional para budget.
- Validación independiente: GitHub issue `vercel/ai#8088` confirma que SDK 6 dispara `onError` para abortos cortos (no `onAbort` específico). Separar ramas requeriría inspección frágil del shape del error.
- DOCTRINA §8.2 documenta plan D6 (logging diferenciado SOLO, NO rollback diferenciado). **Razón válida sin deuda oculta.**

**Item 5 (F-D3.2-08 sdk legacy preservado) [JUSTIFICADO]** — Verifico binariamente:
- `grep -rn "invokeTutor\b" apps/la-forja/api/src` → uso vivo en `lib/llm/router.ts:21,90`. El path JSON legacy se llama desde el router para misiones tutor fuera del endpoint `/api/tutor/chat`.
- Removerlo en D3.2 rompería el router sin migrar de capa = scope creep + ruptura.
- DOCTRINA §8.2 registra D6 "Provider Layer Unification" como sprint dedicado a migrar `invokeTutor` blocking → `generateText` con `@ai-sdk/anthropic`, permitiendo retiro del legacy. **Razón válida sin deuda oculta — drift doctrinal NO existe** porque DSC-LF-005 aplica a "endpoints" (path al cliente), no a libraries SDK internas que aún tienen otro consumidor.

**Item 6 (Toggle UI requireValidation) [JUSTIFICADO]** — Prop expuesta en `Chat.tsx:39-41` `requireValidation?: boolean = false`. Pasada al transport vía `body: { requireValidation }`. UI toggle es feature D3.3 documentada en todo.md. Sin deuda oculta.

**Item 7 (Tests Chat.tsx con happy-dom) [JUSTIFICADO]** — Backend cubre flujo SSE end-to-end vía Hono `request()` con stream mock builder (verificable en `routes.test.ts`). Tests frontend hooks (`useChat` con MSW para SSE) son trabajo D3.3 documentado. El contract test `forjaHeaders.contract.test.ts` ya bloquea drift binariamente en el contrato. Sin deuda crítica.

**Item 8 (streamdown para markdown) [JUSTIFICADO]** — D3.2 entrega texto plano con cursor blink (`MessageBubble.tsx:65-70`) suficiente para validar binariamente el contrato SSE. Markdown rendering es feature D3.3. Sin deuda crítica.

---

## Honestidad doctrinal

**Verificado [SI]** con una observación menor no bloqueante:

Doctrina `_DOCTRINA_D3.md` §7 (entrega original D3.2) + §8 (D3.2.1 hardening) + §8.5 (D3.2.2 hardening) verificada línea por línea:
- §7.1 stack SSE declarado matchea código (`streamText().toUIMessageStreamResponse()`, `createAnthropic`, `useChat`, `DefaultChatTransport`).
- §7.2 trade-off `onFinish` background documentado honestamente con fallback "cap se enforce en SIGUIENTE turn vía preCallCheck".
- §7.4 reordenamiento magna pre-stream con 3 razones binarias claras + reconocimiento explícito de que NO requiere DSC nuevo (es interno).
- §8.2 disputas F-D3.2-05 + F-D3.2-08 con razones binarias verificables, plan D6 explícito.
- §8.3 5 drifts externos con ID + severidad + plan de cierre por sprint.
- §8.5.1 fixes D3.2.2 con archivo:línea exacto.
- §8.5.2 apex de cambio del contract JSON diagramado.

**Observación binaria menor**: §7.3 tabla línea 161 lista header `x-la-forja-citations` (JSON-encoded). El código actual usa `x-la-forja-citations-b64` (base64url), fix documentado en §8.1 línea 205 (F-D3.2-03). La tabla §7.3 quedó stale post-hardening. **Es doc drift, no code drift** (código + contract JSON + frontend espejo todos consistentes en b64). NO bloquea SHIP. Register-only D6 doc polish.

Cero claims falsos detectados. Cero deuda oculta. Cero soft-talk en tradeoffs.

---

## Decisión final

🟢 **VERDE**

**Autorizaciones binarias:**

1. **PR #133 autorizado para merge a `main`**. State `OPEN/READY/MERGEABLE`. Branch protection vigente. T1-Alfredo decide si merge manual o instruye Cowork directo bajo regla evolucionada del merge.

2. **DSC-LF-005 FIRMADO formalmente** con el texto canónico exacto propuesto en el bridge request §307-309:

> **DSC-LF-005 — Endpoints LLM SSE forward (firmado 16-may-2026 commit `e13d669`):**
> *"Todo endpoint backend que invoque un LLM devuelve `text/event-stream` con `createUIMessageStreamResponse` / `streamText().toUIMessageStreamResponse()` del Vercel AI SDK 6 + provider Anthropic. JSON solo para metadata sin LLM. Aplica forward desde D3.2 (commit `beebff8`); sin retroactivos."*

Firma vinculante: forward desde commit `beebff8` (D3.2 feature). Cualquier endpoint LLM nuevo D3.3+ debe seguir el patrón. Endpoints sin LLM (`/api/sprints`, `/api/telemetry`, `/api/puertas`, `/api/manus`) siguen JSON sin obligación de migrar.

3. **D3.3 autorizado** — UI toggles (`requireValidation` checkbox), streamdown integración para markdown rendering, tests `Chat.tsx` con happy-dom + MSW. Sin esperar nada de Cowork. Bridge `manus_to_cowork_LA_FORJA_001_D3_3_AUDIT_REQUEST.md` cuando D3.3 cierre.

**Estado DSC vigentes tras este audit:**

| DSC | Estado | Firma |
|---|---|---|
| DSC-LF-001 Five Doors Inviolable | VIGENTE | commit `6401a3b` (D2) |
| DSC-LF-002 Test Bench Telemetry Mandatory | VIGENTE | commit `6401a3b` (D2) |
| DSC-LF-003 Rate Limit Hard-Cap $50/mes/usuario | VIGENTE | commit `6401a3b` (D2) |
| DSC-LF-004 Perplexity única validación externa | VIGENTE | commit `6401a3b` (D2) |
| **DSC-LF-005 Endpoints LLM SSE forward** | **FIRMADO HOY** | **commit `e13d669` (D3.2.2)** |
| DSC-G-008 v4 Error path coverage LLM | VIGENTE | commit `fbbbe8c` (D2.5) |

**Register-only D6 (consolidado tras este audit):**

1. Doc drift `_DOCTRINA_D3.md` §7.3 tabla menciona `x-la-forja-citations` sin -b64 sufijo (§8.1 documenta fix pero §7.3 quedó stale)
2. D-D3.2-01 RLS Supabase (data plane, Sprint D5)
3. D-D3.2-02 Notion DSC-LF-005 → Firmado (auto-update post-merge)
4. D-D3.2-03/04/05 docs externos Drive/Notion/Semilla
5. F-D3.2-05 logging diferenciado client-abort vs upstream-error (no rollback diferenciado)
6. F-D3.2-08 sprint D6 Provider Layer Unification (migra invokeTutor blocking)
7. Tests Chat.tsx hooks con MSW (D3.3 scope)
8. 2 vulns postcss moderate Next interno (sin cambio vs D3.0)
9. Backlog D6 acumulado audits previos (H-6 PII regex México, H-7 thinking docs, H-8 OpenAI shape, H-9 Gemini shape, H-10 Perplexity citations defensivo, H-11 comment middleware order, H-13 SupabaseBudgetClient atómico, H-14 LLM client cache)

Total backlog D6: 9 items consolidados + 4 items históricos = ~13 items. Ninguno bloquea D3.3.

---

## Gates verificados fresh hoy en este audit

| Comando | Output | Estado |
|---|---|---|
| `cd apps/la-forja/api && npm run typecheck` | 0 errores tsc | ✅ |
| `cd apps/la-forja/api && npm test` | **180 passed (180) en 502ms** sobre 12 files | ✅ |
| `cd apps/la-forja/api && npm run build` | 0 errores tsc emit | ✅ |
| `cd apps/la-forja/api && npm run contract:headers` | "OK 6 headers, cap=2048B" + `git status --short` empty (idempotente) | ✅ |
| `cd apps/la-forja/web && npm run typecheck` | 0 errores | ✅ |
| `cd apps/la-forja/web && npm test` | **40 passed (40) en 363ms** sobre 6 files | ✅ |
| `cd apps/la-forja/web && npm run build` | 4 rutas: `/` ƒ + `/_not-found` ○ + `/onboarding` ○ + `/salud` ƒ + `/tutor` ○ Static | ✅ |
| `cd apps/la-forja/web && npm run lint` | 0/0 | ✅ |

Atribución CI rojos: `git diff --name-only c089522..e13d669 | grep -E "^(transversal/|tests/anti_dory/)"` → 0 hits. Los 3 CI rojos persistentes siguen preexistentes, no introducidos por D3.2.

---

## Firma binaria

```
SPRINT:           LA-FORJA-001 v3.2 — D3.2 + D3.2.1 + D3.2.2 SSE TUTOR CHAT
COMMITS:          beebff8 (feat D3.2) + e16bb26 (bridge adversarial) + a53cca6 (D3.2.1 hardening) + e13d669 (D3.2.2 regression)
SOBRE:            c089522 (D3.1+D3.1.1 VERDE 12/12 previo)
PR:               #133 (OPEN, isDraft=false, mergeable=MERGEABLE) — AUTORIZADO para merge
AUDITOR:          Cowork T2-A (Claude Opus 4.7 / 1M context)
SESIÓN:           bold-neumann-ef6284
FECHA:            2026-05-16
METODOLOGÍA:      audit DELTA formal + firma DSC-LF-005

VERIFICACIONES FRESCAS:
  api typecheck:  ✅ 0 errores
  api vitest:     ✅ 180/180 (502ms, 12 files)
  api build:      ✅ verde
  api contract:   ✅ idempotente (OK 6 headers cap=2048B, git status vacío)
  web typecheck:  ✅ 0 errores
  web vitest:     ✅ 40/40 (363ms, 6 files)
  web build:      ✅ verde, /tutor ○ Static
  web lint:       ✅ 0/0

PUNTOS 1-14:      ✅ 14/14 VERDE binario
HARD RULES 1-9:   ✅ 9/9 VERDE
ITEMS "NO HICE":  ✅ 8/8 JUSTIFICADOS (cero deuda oculta)
HONESTIDAD:       ✅ verificada (1 doc drift §7.3 menor register-only)
CI ROJOS:         ✅ 3 persistentes siguen preexistentes
DSC-LF-005:       🟢 FIRMADO formalmente con texto canónico propuesto
DECISIÓN FINAL:   🟢 VERDE — PR #133 mergeable, D3.3 autorizado
```

🟢 **LA-FORJA-001 D3.2 + D3.2.1 + D3.2.2 — AUDIT VERDE · DSC-LF-005 FIRMADO**

— Cowork T2-A · LA-FORJA-001 v3.2 · D3.2 VERDE 14/14 + DSC-LF-005 FIRMADO · 16 mayo 2026
