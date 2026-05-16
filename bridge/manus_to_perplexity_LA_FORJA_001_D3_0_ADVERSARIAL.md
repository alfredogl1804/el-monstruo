# PROMPT ADVERSARIAL — Perplexity Sonar Pro Reasoning

**Sprint:** LA-FORJA-001 D3.0
**Commit auditable:** `e10169f` en `https://github.com/alfredogl1804/el-monstruo` branch `sprint/la-forja-001`
**Fecha:** 16-may-2026
**Hilo emisor:** Manus E1 (ejecutor frontend La Forja)

---

## INSTRUCCIONES DE COPIA

Pegar el bloque entre `---BEGIN PROMPT---` y `---END PROMPT---` literal en Perplexity con modelo **Sonar Reasoning Pro**.

Tras la respuesta, esperar la lista de F-patterns numerados (F-D3.0-XX) y traerla de vuelta a este hilo Manus para procesarla en bloque.

---

---BEGIN PROMPT---

# Adversarial audit — La Forja D3.0 frontend scaffold

You are an adversarial code reviewer with a single objective: **find every concrete defect** in the scaffold described below. Today is **16-may-2026**.

Treat training data as suspect. **Verify all version numbers, peer dependencies, and API surface claims against real npm registry and GitHub release data current to today** before you make any claim. Flag any check you cannot complete in real time.

Output rules — non-negotiable:

1. Output a numbered list of findings using the exact format `F-D3.0-01`, `F-D3.0-02`, …
2. Each finding must include:
   - **Severity:** `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `INFO`
   - **File / line / construct** affected (verbatim from the snippets below)
   - **Concrete defect** — one sentence, no hedging, no "consider"
   - **Verification step** — exact command, npm view query, or registry URL someone else can run to confirm or refute the finding
   - **Minimal patch** — exact diff or replacement snippet, not prose
3. Do **not** include praise, summaries, or "looks good overall" framing. The deliverable is a defect list.
4. If you find nothing in a category, write `NO FINDINGS — verified via <command/url>`.
5. **Forbidden phrases:** "best practices in general", "you may want to", "depending on your needs", "industry standard". Be specific to this codebase.
6. End with a section titled **DECISION BINARIA** — single line:
   `D3.0 SCAFFOLD: SHIP / DO NOT SHIP — reason: <one sentence>`

## Project context (read once, do not paraphrase)

`La Forja` is the frontend of an internal product. Backend is **Hono 4.12.18** in `apps/la-forja/api` (already audited green at D2.5, commit `fe82b1c`). This audit is only for the frontend scaffold `apps/la-forja/web/` introduced at commit `e10169f`.

Hard rules the codebase must respect:

- **LF-1:** the frontend NEVER talks to Supabase or any database directly. All data flows through the Hono backend.
- **LF-2 (anti-stale-versions):** every dependency version must be validated in real time against npm registry on the day of the commit.
- **Hard Rule #6 fail-loud:** environment variables must be validated with Zod and reject loudly in `NODE_ENV=production` if missing or invalid.
- **Brand Engine:** error codes use `[la-forja:web_*]` namespace. Generic naming like `Service`, `Handler`, `Util`, `Helper`, `Manager` is banned by ESLint.
- **No self-merge:** the work lives on a feature branch and a human merges PRs.

## Stack frozen at commit e10169f

| Package | Version | Source claim |
|---|---|---|
| next | 16.2.6 | claimed `npm view next dist-tags.latest` on 15-may-2026 |
| react | 19.2.6 | claimed latest stable |
| react-dom | 19.2.6 | matches react |
| ai (Vercel AI SDK) | 6.0.184 | claimed +1 patch over SPEC 6.0.183 |
| @ai-sdk/react | 3.0.186 | claimed peer covers React 19.2 |
| tailwindcss | 4.3.0 | claimed latest |
| @tailwindcss/postcss | 4.3.0 | matches tailwind |
| typescript | 5.7.3 | parity with backend |
| zod | 3.25.76 | parity with backend |
| vitest | 2.1.8 | dev |
| happy-dom | latest dev | dev only |
| eslint-config-next | 16.2.6 | matches next |

**Verify each version** is still installable today and that peer-dependency ranges actually accept the listed React/Next versions. Flag any drift with `npm view <pkg>@<version> peerDependencies --json` output cited.

## H-12 design decision (verify or refute)

Manus claims that `ai@6.0.184` exposes `createUIMessageStream` and `createUIMessageStreamResponse` returning a web-standard `Response`, and that this lets a Hono route stream SSE without any custom adapter. The runtime probe Manus reports:

```
content-type: text/event-stream
x-vercel-ai-ui-message-stream: v1
IS_RESPONSE: true
```

**Adversarial task:** confirm or refute that those exports exist in `ai@6.0.184` exactly as named, that the response is consumable by `useChat` from `@ai-sdk/react@3.0.186` without polyfills, and that returning that `Response` object from a Hono handler does not strip headers or break the stream. If any of those three assertions is false, flag it.

## Files in scope (verbatim — audit each)

### apps/la-forja/web/package.json (40 lines)

```json
{
  "name": "@la-forja/web",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "start": "next start",
    "typecheck": "tsc --noEmit",
    "lint": "next lint",
    "test": "vitest run"
  },
  "dependencies": {
    "next": "16.2.6",
    "react": "19.2.6",
    "react-dom": "19.2.6",
    "ai": "6.0.184",
    "@ai-sdk/react": "3.0.186",
    "zod": "3.25.76",
    "streamdown": "latest"
  },
  "devDependencies": {
    "typescript": "5.7.3",
    "@types/node": "22.10.5",
    "@types/react": "19.2.0",
    "@types/react-dom": "19.2.0",
    "tailwindcss": "4.3.0",
    "@tailwindcss/postcss": "4.3.0",
    "postcss": "8.5.10",
    "eslint": "9.18.0",
    "eslint-config-next": "16.2.6",
    "vitest": "2.1.8",
    "happy-dom": "latest"
  }
}
```

Adversarial questions:
- Is `"latest"` acceptable for `streamdown` and `happy-dom` under LF-2? **Refute or accept with cited commit policy.**
- Are all `@types/*` versions compatible with the React 19.2 / Node 22 runtime?
- Does `eslint-config-next@16.2.6` exist and pull a flat-config-compatible setup?

### apps/la-forja/web/next.config.ts (16 lines)

```ts
import type { NextConfig } from "next";

/**
 * La Forja — Next.js 16.2.6 config.
 * Sprint LA-FORJA-001 D3.0.
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  typedRoutes: true,
  // El frontend NUNCA habla con Supabase directo (LF-1 + RLS-aware).
  // Toda data viaja vía el backend Hono en `apps/la-forja/api`.
  // En dev local, NEXT_PUBLIC_API_URL apunta a http://localhost:3000.
  // En producción, apunta a https://la-forja-api.up.railway.app.
};

export default nextConfig;
```

Adversarial questions:
- Is `typedRoutes` at the top level the correct location in Next 16.2.6, or has it moved again?
- Does this config opt out of any Next 16 default that should be explicit (e.g. caching defaults, server actions, image optimization)?

### apps/la-forja/web/tsconfig.json (47 lines, strict)

Manus claims `strict: true`, `noUncheckedIndexedAccess: true`, target ES2022, paths `@/* -> src/*`, includes `next-env.d.ts`, `.next/dev/types/**/*.ts`, and excludes `node_modules`.

Adversarial questions:
- Is `noUncheckedIndexedAccess` compatible with the Next 16.2.6 generated types?
- Does Next 16 still need `next-env.d.ts` referenced manually, or is it auto-included?

### apps/la-forja/web/eslint.config.mjs (24 lines, flat config)

Includes `next/core-web-vitals`, `next/typescript`, plus a custom `id-match` rule banning identifiers `Service|Handler|Util|Helper|Manager` (Brand Engine).

Adversarial questions:
- Does `next` ship flat-config presets in 16.2.6, or does this need the legacy `.eslintrc` shim?
- Is `id-match` reachable from the flat config without an extra plugin import?

### apps/la-forja/web/src/lib/env.ts (64 lines)

Loads env with Zod. `loadForjaWebEnv({ strict: true })` rejects with code `[la-forja:web_env_load_strict_failed]` if `NEXT_PUBLIC_API_URL` is missing or not a valid URL. `loadForjaWebEnv({ strict: false })` rejects with `[la-forja:web_env_load_permissive_blocked_in_production]` when `NODE_ENV=production`.

Adversarial questions:
- Does this module accidentally bundle `process.env` access into the client (Next 16 inlines `NEXT_PUBLIC_*` at build time — anything else leaks)?
- Are the error codes consistent enough to be greppable for postmortem?

### apps/la-forja/web/src/lib/api.ts (83 lines)

Exports `ForjaApiError`, `ForjaHealthResponse`, `buildForjaApi({ apiUrl? })`. Uses `fetch` with header `x-request-id` (random UUID per request). On non-2xx throws `ForjaApiError` with code `[la-forja:web_api_request_failed]` and message including status + path.

Adversarial questions:
- Is `crypto.randomUUID()` (or whatever Manus used) safe in both Server Components and the Edge runtime that Next 16 may pick?
- Does the client implicitly trust the backend's `content-type`? What happens on `text/html` 502 from a CDN?
- Any timeout / abort signal? If absent, that is a finding.

### apps/la-forja/web/src/app/salud/page.tsx (71 lines)

Server Component that calls `buildForjaApi().health()` at request time and renders status. Reads `NEXT_PUBLIC_API_URL` server-side.

Adversarial questions:
- Will this page accidentally be statically prerendered at build time and show stale or dead data?
- Server Component fetching `localhost:3000` from the Next server during build — does this break in CI?

### apps/la-forja/web/src/lib/api.test.ts + env.test.ts (3 + 5 = 8 tests, all passing)

Tests stub `globalThis.fetch` and `process.env`. Adversarial questions:
- Are `vi.stubGlobal` and `vi.unstubAllGlobals` actually balanced per test? Any leak between tests?
- Do these tests actually exercise the `[la-forja:web_env_load_permissive_blocked_in_production]` path or only the regex match on the message?

### apps/la-forja/web/src/app/globals.css

Tailwind 4 with `@theme` block declaring `forja-{50..900}`, `graphite-{50..900}`, `acero-{300,500,700}`. `color-scheme: dark` at root.

Adversarial questions:
- Does Tailwind 4.3 support `@theme` exactly as written, or has the syntax shifted?
- Does the `@tailwindcss/postcss` plugin chain need any extra import in `postcss.config.mjs`?

### apps/la-forja/web/.env.local.example

Single var documented: `NEXT_PUBLIC_API_URL=http://localhost:3000`.

Adversarial questions:
- Should this file include a comment about CORS being required when frontend and backend run on different origins?
- Any other env required by Next 16 (telemetry, build-id, etc.) that Manus forgot?

## Out of scope

- The backend Hono routes, schemas, or DB layer. Already audited green at D2.5.
- The `_DOCTRINA_D3.md` design doc.
- Future phases D3.1..D3.4 (Tour, Chat tutor SSE, Sprint room, Dashboard).

## Final reminder

Verify every version claim with a real `npm view` query dated today. Cite the query verbatim in the verification step of any finding that depends on a version. Do not invent CVE IDs, peer-dep ranges, or release dates.

Begin output now with `F-D3.0-01`. End with `DECISION BINARIA: ...`.

---END PROMPT---

---

## Post-respuesta — qué hacer con los F-patterns de Perplexity

1. Pegar la respuesta completa en este hilo Manus.
2. Manus E1 procesa cada `F-D3.0-XX` con esta tabla binaria:

| Acción | Cuándo |
|---|---|
| **Fix inmediato D3.0** | severidad `CRITICAL` o `HIGH` que rompa el scaffold o viole LF-1/LF-2/Regla Dura #6 |
| **Register-only D6** | severidad `MEDIUM`/`LOW` que sea polish o no bloquee D3.1 |
| **Refutar** | severidad cualquiera donde Manus pueda demostrar binariamente que el hallazgo es falso (con `npm view`, runtime probe, o lectura del archivo real) |
| **Escalar a Cowork** | hallazgo que toque un contrato D2 ya VERDE (ej. cambiar shape de `/health` o `/api/tutor/chat`) |

3. Al cierre, commit `hardening(la-forja): D3.0 adversarial fixes Perplexity Fx/Fy/Fz` análogo al patrón D2.5.
