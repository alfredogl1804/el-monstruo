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
