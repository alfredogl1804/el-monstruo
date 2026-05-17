# LA-FORJA-001 D3 — Doctrina técnica frontend (validada binariamente 15-may-2026)

> Este archivo es la fuente de verdad de versiones y patrones del frontend.
> Se actualiza ANTES de escribir código en `apps/la-forja/web/` (anti-autoboicot).

## §1. Versiones congeladas (binarias contra `npm view` 15-may-2026 22:30 CST)

| Paquete | Versión planeada | Latest real | Decisión |
|---|---|---|---|
| `next` | `16.2.6` | `16.2.6` (latest stable, beta `16.0.0-beta.0` = legacy tag) | ✅ usar `16.2.6` |
| `react` | `19.2.6` | `19.2.6` | ✅ usar `19.2.6` (Next 16.2.6 acepta `^19.0.0`) |
| `react-dom` | `19.2.6` | `19.2.6` | ✅ usar `19.2.6` |
| `ai` (Vercel AI SDK) | `6.0.184` | `6.0.184` | ✅ usar `6.0.184` (SPEC pedía `6.0.183`, justificable subir 1 patch) |
| `@ai-sdk/react` | `3.0.186` | `3.0.186` | ✅ peer `^19.2.1` cubre 19.2.6 |
| `tailwindcss` | `4.3.0` | `4.3.0` | ✅ usar `4.3.0` (estable) |
| `typescript` | `5.7.3` | `6.0.3` (latest) | ⚠️ usar `5.7.3` para coordinar con backend (`apps/la-forja/api` también en 5.7.3) |
| `zod` | `3.25.76` | (`3.x` estable, `4.x` también listado en peers) | ✅ usar `3.25.76` (alineado con backend, AI SDK acepta `^3.25.76 \|\| ^4.1.8`) |
| `streamdown` | `2.5.0` | `2.5.0` | ✅ usar `2.5.0` |

## §2. H-12 RESUELTO binariamente: Vercel AI SDK 6.0.184 con Hono SSE

**Pregunta abierta D2.5 register-only:** ¿Existe adapter Vercel AI SDK ↔ Hono?

**Respuesta binaria:** **NO se necesita adapter.** El AI SDK 6 expone helpers que retornan un `Response` estándar Web Streams API. Hono retorna `Response` nativo. Por lo tanto:

```ts
// En el backend Hono (apps/la-forja/api/src/routes/tutor.ts), en lugar de
// devolver un objeto JSON, devolver el Response del AI SDK directamente:
import { createUIMessageStream, createUIMessageStreamResponse } from "ai";

const stream = createUIMessageStream({
  execute: ({ writer }) => {
    // ...llamar al modelo, escribir deltas
  },
});
return createUIMessageStreamResponse({ stream });
```

**Verificado contra runtime real:**

```
typeof Response constructor: Response
headers: {
  "cache-control": "no-cache",
  "connection": "keep-alive",
  "content-type": "text/event-stream",
  "x-accel-buffering": "no",
  "x-vercel-ai-ui-message-stream": "v1"
}
status: 200
IS_RESPONSE: true
```

Hono pasa el `Response` directo desde un handler con `return c.body(stream, init)` o más simple `return response;` (Hono soporta retorno directo de `Response`).

**Lado cliente Next.js 16.2.6:** usar `useChat` de `@ai-sdk/react@3.0.186` con `transport: new DefaultChatTransport({ api: '/api/tutor/chat' })`. Header `x-vercel-ai-ui-message-stream: v1` permite al cliente reconocer el formato.

## §3. Patrones obligatorios (Brand Engine + Reglas Duras)

- **Naming**: cero `service/handler/util/helper`. Nombres con identidad: `ChatTutor`, `SalaDeSprint`, `Forja` (root layout), `Bocina` (toast), `Bita\u00b4cora` (logs UI).
- **Errores UI**: formato `[la-forja:{module}_{action}_{failure_type}]` mostrado en `<Bocina>` (toast con copy de marca).
- **Tema**: tokens CSS variables en `app/globals.css`:
  - `--forja-orange: #F97316` (acento principal)
  - `--graphite: #1C1917` (background dark default)
  - `--acero: #A8A29E` (text secundario)
- **Brutalismo refinado**: bordes 1px sólidos, no soft shadows; tipografía sans-serif geométrica (Inter Variable), monospace para datos (JetBrains Mono).
- **Fail-loud envs**: `lib/env.ts` con Zod schema strict, mismo patrón que backend `apps/la-forja/api/src/lib/env.ts`.
- **Cero secrets en código**: `NEXT_PUBLIC_API_URL` es la única var pública. Todo lo demás se queda en el backend.
- **RLS-aware**: el frontend NUNCA lee Supabase directo. Toda data va vía Hono backend para que la auth/budget/RLS se aplique.

## §4. Estructura `apps/la-forja/web/`

```
apps/la-forja/web/
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── postcss.config.mjs
├── eslint.config.mjs
├── .env.local.example
├── _DOCTRINA_D3.md          # este archivo
└── src/
    ├── app/
    │   ├── layout.tsx        # <Forja> root con CSS variables Brand DNA
    │   ├── page.tsx          # landing minimalista
    │   ├── globals.css
    │   └── salud/page.tsx    # health check vs backend (GET /health)
    ├── lib/
    │   ├── env.ts            # Zod fail-loud schema
    │   └── api.ts            # cliente tipado contra Hono
    └── components/
        └── Bocina.tsx        # toast de marca (placeholder D3.0)
```

## §5. Paridad con backend `apps/la-forja/api/`

- TypeScript: ambas `5.7.3`
- Zod: ambas `3.25.76`
- ESLint: misma config base (a definir en D3.0)
- Brand Engine error format: idéntico

## §6. NO hacer en D3.0 (separación de fases)

- ❌ Implementar streaming SSE (es D3.2, requiere wire backend tutor.ts)
- ❌ Tour onboarding (D3.1)
- ❌ Auth Google OAuth (D4)
- ❌ Conexión Supabase directa (NUNCA — siempre vía Hono backend)

D3.0 = scaffold + health check page funcional. Nada más.


---

## §7. D3.2 entregado — contrato SSE binario validado (16-may-2026)

### §7.1 Stack SSE elegido (verificado en runtime, no por suposición)

| Pieza | Decisión binaria | Por qué |
|---|---|---|
| Backend stream builder | `streamText({ model: anthropic('claude-opus-4-7'), … }).toUIMessageStreamResponse({ headers })` | Devuelve `Response` Web-standard. Hono `HandlerResponse` lo acepta tal cual; sin adapter. |
| Provider Anthropic | `@ai-sdk/anthropic@3.0.78` con `createAnthropic({ apiKey })` | Permite inyección de `apiKey` desde `loadEnv()` y override del provider en tests sin tocar `process.env`. |
| Modo Adaptive (§2.4 SPEC) | `providerOptions.anthropic.thinking = { type: "enabled", budgetTokens: 1024 }` | Modo Adaptive obligatorio para el tutor del Cliente Cero. Fija `budgetTokens` (camelCase, no `budget_tokens`). |
| Frontend hook | `useChat({ transport })` de `@ai-sdk/react@3.0.186` | `input` / `handleInputChange` legacy fueron removidos en v3; ahora se controla con `useState` local. |
| Frontend transport | `new DefaultChatTransport({ api, fetch, body })` de `ai@6.0.184` | El custom `fetch` permite leer headers SSE pre-stream para hidratar la barra de metadata sin parsear chunks. |
| Protocolo SSE | UI Message Stream v1 (header `x-vercel-ai-ui-message-stream: v1`) | Único protocolo soportado nativamente por `useChat` v3; reemplaza el "data stream" v0/v1 del SDK 4/5. |

### §7.2 Mapping budget pipeline → callbacks del stream

```
Pipeline tutor (D3.2):

  preCallCheck(classifier)  ──▶  classifyMessage()  ──▶  postCallCommit(classifier)
        │                              │
        └─ rollback en catch ◀─────────┘  (adjustSpent(-classifierEstimated))

  preCallCheck(magna_validation)  ──▶  invokeMagnaValidation()  ──▶  postCallCommit(magna)
        │                                       │
        └─ rollback en catch ◀──────────────────┘  (adjustSpent(-magnaEstimated))

  buildTutorStream({
    onFinish: ({inputTokens, outputTokens}) => postCallCommit(tutor, real, real, c.var.budgetEstimated),
    onError:  (err) => adjustSpent(user.id, -c.var.budgetEstimated),
  })

  return result.toUIMessageStreamResponse({ headers })
```

**Trade-off documentado:** el `Response` SSE se devuelve al cliente ANTES de que `onFinish` se complete (corre en background del stream). Es el patrón canónico del Vercel AI SDK 6. Si `onFinish` falla por error de DB en `postCallCommit`, el cap se enforce en el SIGUIENTE turn vía `preCallCheck`. Si `onError` se dispara mid-stream, el rollback se aplica antes de que el cliente termine de leer el body.

### §7.3 Headers SSE custom que el backend emite

El backend agrega los siguientes headers junto a los del UI Message Stream v1:

| Header | Tipo | Significado |
|---|---|---|
| `x-vercel-ai-ui-message-stream` | literal `v1` | Protocolo del SDK; identifica que el body es UI Message Stream. |
| `x-la-forja-intent` | `"confusion_detected" \| "no_confusion"` | Output de AC12 sobre el último mensaje del usuario. |
| `x-la-forja-confidence` | número con 4 decimales | Confidence del clasificador. |
| `x-la-forja-model` | literal `claude-opus-4-7` | Modelo del tutor (registro contra MISSION_TO_MODEL §2.4). |
| `x-la-forja-citations` | JSON-encoded `string[]` | Solo presente si `requireValidation=true`. URLs devueltas por Sonar. |
| `x-la-forja-validation-model` | string | Solo presente si `requireValidation=true`. Modelo magna usado (sonar-reasoning-pro). |

El cliente (`Chat.tsx`) consume estos headers vía custom `fetch` del `DefaultChatTransport` y los renderiza en una barra metadata + footer de citations.

### §7.4 Reordenamiento magna_validation: PRE-stream (decisión binaria)

En D2.6 magna_validation corría DESPUÉS del tutor (validaba el output). En D3.2 se mueve ANTES del stream. Justificación binaria:

1. **El cliente necesita las citations en headers.** Si magna corre después, las citations llegarían en un chunk post-finish, pero el cliente ya está pintando la respuesta completa. Romper el flujo SSE para inyectar citations al final viola el contrato `useChat`.
2. **La validación magna NO depende del output del tutor.** Sonar valida el TEMA del usuario contra fuentes recientes para que el tutor pueda responder citando, no para corregir al tutor a posteriori. El significado semántico no cambia.
3. **DSC-LF-004 (firmado en D2) no fija el orden,** solo fija que magna usa Sonar Reasoning Pro como capa de validación. La reordenación es interna y no requiere DSC nuevo.

Documentado en el banner del archivo `apps/la-forja/api/src/routes/tutor.ts` para auditoría futura.

### §7.5 Tests retirados vs tests agregados

| Test D2.6 retirado | Reemplazo D3.2 |
|---|---|
| `200 con tutor mockeado y AC12 inyectado` (assertaba JSON `body.content`) | `200 SSE: content-type=text/event-stream + headers metadata` |
| `incluye citations cuando requireValidation=true` (JSON `body.citations`) | `200 SSE: incluye x-la-forja-citations + x-la-forja-validation-model` |
| `H-2: si invokeTutor lanza, adjustSpent rollback` (catch sincrónico) | `H-2 (D3.2): si el stream del tutor falla mid-stream, adjustSpent ejecuta rollback vía onError` |

Los 4 tests D2.5 hardening (H-2 magna, H-3 classifier, H-3 magna, H-2 stream) **siguen pasando con la misma intención**: el invariante mínimo es que `adjustSpent` se llame con valor negativo en cada error path, y `reserveSpent` se llame ≥2 (sin magna) o ≥3 (con magna) veces.

### §7.6 Resultado binario

- Backend: 176/176 tests passing en 478ms · `tsc -p tsconfig.json --noEmit` 0 errores · `npm run build` verde
- Frontend: 37/37 tests passing · typecheck verde · `next build` verde con `/tutor` registrada como `ƒ` (server-rendered on demand)
- DSC-LF-005 implementado pero NO firmado todavía: pendiente auditoría adversarial Perplexity (primer pase + regresión) + bridge audit Cowork antes de firmar formalmente.


---

## §8 — D3.2.1 Hardening adversarial (Perplexity primer pase, 16-may-2026)

**Commit base auditado**: `beebff8` (D3.2). **Output Perplexity**: 9 F-patterns + 3 R-patterns + 5 drifts. **Decisión Perplexity**: DO NOT SHIP. **Decisión Manus tras triage binario**: aplicar 7 F-patterns + 3 R-patterns como código (F-01/02/03/04/06/07/09 + R-01/02/03), disputar 2 (F-05/08) con razón documentada, registrar 5 drifts externos como work item para sprints D5/D6.

### §8.1 Fixes aplicados sobre código

| ID | Severidad | Archivo:línea | Fix binario |
|---|---|---|---|
| F-D3.2-01 | HIGH | `api/src/routes/tutor.ts:127-202` | Capturar `tutorBudgetEstimated` antes del classifier; rollbackear AMBAS reservas (mission + tutor) en cada catch (classifier-fail + magna-fail). |
| F-D3.2-02 | HIGH | `api/src/lib/llm/anthropic.ts:188-204` + `api/src/routes/tutor.ts:225-237` | Try/catch alrededor de `onError` callback en wrapper SDK + en callsite de la ruta; log con namespace canónico `[la-forja:tutor_rollback_failed]` (Brand Engine). |
| F-D3.2-03 | MEDIUM | `api/src/routes/tutor.ts:240-262` + `web/src/lib/forjaHeaders.ts:30-52` | Citations viajan ahora como header `x-la-forja-citations-b64` (base64url(JSON)) para soportar UTF-8 sin romper RFC 7230. Frontend decodifica vía `decodeCitationsHeader()`. |
| F-D3.2-04 | MEDIUM | `api/src/routes/tutor.ts:250-262` | Truncate por **bytes UTF-8** (`Buffer.subarray`), no por caracteres, para respetar `FORJA_CITATIONS_HEADER_MAX_BYTES = 2048` de manera estricta. |
| F-D3.2-06 | LOW | `api/src/routes/tutor.ts:142, 201` | Errores arrojados ahora con namespace `[la-forja:tutor_classifier_failed]` y `[la-forja:tutor_magna_failed]` (Brand Engine §7.5 anti-soft-talk). |
| F-D3.2-07 | LOW | `web/src/app/tutor/page.tsx:14-19` | Removido `export const dynamic = "force-dynamic"`. La página ahora se prerendiza (`○ Static`) por Next.js 16; el SSE corre desde el Client Component contra el API externo. |
| F-D3.2-09 | LOW | `api/src/middleware/budget.ts:22-92` | `cap: 50.0` reemplazado por import de `FORJA_BUDGET_CAP_USD` desde `lib/budget` (DSC-LF-003 fuente única). |
| R-D3.2-01 | MEDIUM | `api/src/routes/routes.test.ts:700-765` | Test H-2 magna endurecido: ahora exige `negativeCalls.length >= 2` (magna + tutor) y agrega `R-D3.2-01b` para classifier-fail con misma asserción binaria. |
| R-D3.2-02 | MEDIUM | `api/src/shared/headers.ts` (NUEVO) + `web/src/lib/forjaHeaders.ts` (NUEVO) + `web/src/lib/forjaHeaders.contract.test.ts` (NUEVO) | Contract test que parsea con `fs.readFileSync` el archivo backend y compara byte por byte contra el espejo frontend; rompe si una clave o valor diverge. |
| R-D3.2-03 | LOW | esta sección §8 | La doctrina ahora declara explícitamente disputas + trade-offs vivos; ver §8.2. |

### §8.2 Disputas registradas (no aplicadas)

#### F-D3.2-05 — DISPUTAR

> Perplexity propone: detectar `error instanceof DOMException && error.name === "AbortError"` en el `onError` y retornar **sin** ejecutar `adjustSpent(-tutorBudgetEstimated)`.

**Razón binaria del rechazo**:
1. La doctrina actual rollbackea SIEMPRE en `onError`. Esto es **correcto** porque si el cliente abortó mid-stream, el budget reservado por el middleware no debe quedarse pegado al usuario; debe liberarse para que su siguiente turn lo use.
2. El patch propuesto introduciría **leak**: el budget reservado quedaría sin usar y sin liberar.
3. La distinción "abort cliente vs error real del modelo" es **cosmética para logging**, no funcional para budget.
4. Validación real-time (GitHub issue `vercel/ai#8088`, agosto 2025): el SDK 6 dispara `onError` para abortos cortos, no `onAbort` específico, así que separar las ramas requeriría inspección frágil del shape del error.

**Si se reactiva en D6**: agregar logging diferenciado (no rollback diferenciado) con `[la-forja:tutor_stream_aborted_by_client]` vs `[la-forja:tutor_stream_failed_upstream]` solo para observabilidad.

#### F-D3.2-08 — DISPUTAR

> Perplexity propone: remover `@anthropic-ai/sdk@0.96.0` del `package.json` por ser bloat / dead code.

**Razón binaria del rechazo**:
1. `grep -rn "invokeTutor\b" apps/la-forja/api/src` devuelve **uso vivo** en `lib/llm/router.ts:21,90`. El router invoca el path JSON legacy bloqueante para misiones donde `tutor` se llama fuera del endpoint `/api/tutor/chat`.
2. Removerlo rompería el router sin cambiar de capa.
3. La consolidación SDK (legacy → AI SDK 6 universal) es trabajo de **D6 — Provider Layer Unification**, no D3.2.1.

**Acción registrada para D6**: migrar `invokeTutor` blocking a usar el provider Vercel `@ai-sdk/anthropic` con `generateText` (no `streamText`), así el package legacy puede salir.

### §8.3 Drifts externos registrados (work item para sprints futuros)

| ID | Severidad | Origen | Acción |
|---|---|---|---|
| D-D3.2-01 | CRITICAL | Supabase: tablas `users`, `budget_ledger`, `events_log` sin RLS habilitado | **Sprint D5 — Data Plane Hardening**: aplicar `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` + policies por tenant. Bloquea producción multi-usuario. Doctrina canónica: AGENTS.md Regla Dura #7 (RLS Universal). |
| D-D3.2-02 | HIGH | Notion DB "DSCs Vivos": `DSC-LF-005` aún en estado `Implementado`, no `Firmado` | **Auto-update tras pase 2 Perplexity verde + Cowork audit verde**: bridge `cowork_to_manus_LA_FORJA_001_D3_2_FIRMA.md` cierra el ciclo. |
| D-D3.2-03 | MEDIUM | Drive: `LA_FORJA_PRICING_MATRIX_v3.2.xlsx` cell `B14` muestra `$50.00` cap mensual sin DSC-LF-003 link | Trabajo doc D3.5 — actualizar matriz con foot-link a la celda. |
| D-D3.2-04 | MEDIUM | Notion: la página "La Forja - SPEC v3.2" §4.2 menciona `text/event-stream` pero no cita DSC-LF-005 | Trabajo doc D3.5 — propagar la firma DSC-LF-005 una vez consolidada. |
| D-D3.2-05 | MEDIUM | `discovery_forense/SEMILLA_v7.3.md`: árbol de modelos no incluye `claude-opus-4-7` Adaptive | Trabajo doc D3.5 — agregar entrada con `budgetTokens: 1024` + DSC-LF-005 link. |

### §8.4 Resultado binario tras hardening

| Métrica | Pre-D3.2.1 (commit beebff8) | Post-D3.2.1 |
|---|---|---|
| Backend tests | 176 | **180** (+4: F-03 b64, F-03 UTF-8, F-04 byte-truncate, F-02 fail-loud, R-01b classifier) |
| Frontend tests | 37 | **38** (+1: R-02 contract test fs-based) |
| Backend typecheck | OK | OK |
| Frontend typecheck | OK | OK |
| Backend build | OK | OK |
| Frontend build | OK | OK + `/tutor` ahora `○ Static` |
| F-patterns abiertos | 9 | 0 (7 aplicados, 2 disputados con razón documentada) |
| R-patterns abiertos | 3 | 0 (3 aplicados) |
| Drifts externos | 5 abiertos | 5 registrados con plan de cierre por sprint |

**DSC-LF-005 estado**: implementado + endurecido. Pendiente segundo pase Perplexity (regresión sobre delta D3.2.1) + bridge audit Cowork D3.2 antes de firma formal.
