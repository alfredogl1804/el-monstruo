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
