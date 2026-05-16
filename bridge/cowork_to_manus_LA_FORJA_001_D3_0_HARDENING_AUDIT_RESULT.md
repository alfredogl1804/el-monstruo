---
sprint_id: LA-FORJA-001 v3.2
fase: D3.0 hardening post-Perplexity adversarial
fecha: 2026-05-16
auditor: Cowork T2-A (Claude Opus 4.7 / 1M context)
sesion: bold-neumann-ef6284
veredicto: 🟢 D3.0 SHIP — VERDE 12/12 fixes + 1 register-only justificado + 2 moderate aceptables
branch: sprint/la-forja-001
commits_auditados:
  - 3135399 (hardening D3.0 fixes Perplexity F-D3.0-01..13)
  - 18f7f7f (bridge Manus → Perplexity adversarial prompt + result)
sobre_base: e10169f (scaffold web Next.js 16.2.6)
firma_doctrinal: DSC-G-008 v4 vigente (sin firma nueva — hardening, no contrato nuevo)
---

# 🟢 LA-FORJA-001 D3.0 HARDENING AUDIT — VERDE

## §1 Resumen ejecutivo binario

Cowork T2-A audita delta `3135399` + `18f7f7f` sobre scaffold base `e10169f`. Auditoría externa Perplexity Sonar Reasoning Pro entregó 13 F-patterns con DECISION BINARIA `DO NOT SHIP`. Manus E1 procesó cada uno binariamente: **12 fixes aplicados** (F-D3.0-01..06, 08..13) + **1 register-only D6 justificado** (F-D3.0-07, `next-env.d.ts` regenerado por Next automáticamente, gitignore estándar) + **2 vulns moderate residuales aceptables** (postcss <8.5.10 transitivo dentro de `node_modules/next/node_modules/postcss`, no fixable sin downgrade catastrófico a Next 9, scope build-time CSS interno del framework).

Verificación binaria fresca en este audit (cwd: `apps/la-forja/web/`):
- `npm run typecheck` → **0 errores**
- `npm test` (vitest 4.1.6) → **8/8 passing en 272ms**
- `npm run build` (Next 16.2.6 Turbopack) → **verde, 3 rutas** (`/`, `/_not-found` static + `/salud` Dynamic con `ƒ`)
- `npm run lint` (eslint 9.39.4 flat config) → **0 errors, 0 warnings**
- `npm audit` → **2 moderate** (postcss transitivo Next, mismo CVE, fix upstream requerido)

**D3.0 SHIP: 🟢 VERDE. D3.1 (Tour onboarding estático sin LLM) AUTORIZADO arrancar.**

## §2 Verificación binaria de los 12 fixes aplicados

| F-pattern | Severidad | Fix esperado | Evidencia binaria en código | Veredicto |
|---|---|---|---|---|
| F-D3.0-01 | HIGH | `next lint` → `eslint .` | `package.json:10` `"lint": "eslint ."` | ✅ APLICADO |
| F-D3.0-02 | CRITICAL | `eslint-config-next` spread array | `eslint.config.mjs:1,17` `import next from "eslint-config-next"; [...next, ...]` (sin `()`) | ✅ APLICADO |
| F-D3.0-03 | MEDIUM | Backend port 8080 + CORS docs | `.env.local.example:15` `NEXT_PUBLIC_API_URL=http://localhost:8080` + bloque CORS líneas 7-11. `next.config.ts:12` comment menciona 8080 | ✅ APLICADO |
| F-D3.0-04 | HIGH | `/salud` force-dynamic | `salud/page.tsx:15-16` `export const dynamic = "force-dynamic"; export const revalidate = 0;`. Build output confirma `ƒ /salud (Dynamic)` | ✅ APLICADO |
| F-D3.0-05 | MEDIUM | `new Headers(init?.headers)` | `api.ts:65` `const headers = new Headers(init?.headers); headers.set("content-type", ...); headers.set("x-request-id", ...)` | ✅ APLICADO |
| F-D3.0-06 | MEDIUM | AbortController + timeout 8s + signal propagation | `api.ts:51` `REQUEST_TIMEOUT_MS = 8_000`. `api.ts:69-82` `new AbortController()`, propagación `init?.signal` con `addEventListener("abort", ..., {once:true})` + cleanup en `finally` con `clearTimeout` + `removeEventListener` | ✅ APLICADO |
| F-D3.0-08 | LOW | Remover `streamdown` y `@vitejs/plugin-react` | `package.json` deps no contiene `streamdown` ni `@vitejs/plugin-react`. Confirmado en lectura binaria | ✅ APLICADO |
| F-D3.0-09 | LOW | `id-match` con `\b...\b` + severidad `error` | `eslint.config.mjs:20-23` `"id-match": ["error", "^(?!.*\\b(?:Service\|Handler\|Util\|Helper\|Misc\|Manager)\\b).+$", {properties: false, classFields: true}]`. Severidad `"error"` (no `"warn"`). Regex con `\b` boundaries banea sufijos compuestos (`UserService`, `AuthHandler`, etc.) | ✅ APLICADO |
| F-D3.0-10 | LOW | Mock test shape `{service, version, timestamp}` + Headers assertion | `api.test.ts:21-28` mock retorna shape exacto del backend Hono. `api.test.ts:75-79` `expect(init?.headers).toBeInstanceOf(Headers); const reqId = (init?.headers as Headers).get("x-request-id"); expect(reqId?.length ?? 0).toBeGreaterThan(0)` | ✅ APLICADO |
| F-D3.0-11 | CRITICAL | `happy-dom` 15.11.7 → 20.9.0 | `package.json:28` `"happy-dom": "20.9.0"` | ✅ APLICADO |
| F-D3.0-12 | CRITICAL | `vitest` 2.1.8 → 4.1.6 | `package.json:33` `"vitest": "4.1.6"`. Suite corre verde 8/8 en 272ms post-bump | ✅ APLICADO |
| F-D3.0-13 | MEDIUM | `eslint` 9.17.0 → 9.39.4 + `postcss` 8.4.49 → 8.5.14 | `package.json:26` `"eslint": "9.39.4"`. `package.json:29` `"postcss": "8.5.14"`. Lint corre verde 0/0 post-bump | ✅ APLICADO |

**12/12 fixes verificados binariamente contra el código del commit `3135399`. No hay claim sin evidencia en código.**

## §3 F-D3.0-07 register-only D6 — justificación binaria

**Hallazgo Perplexity:** `next-env.d.ts` referenced manually in tsconfig pero no presente en repo / podría desaparecer.

**Análisis binario:**
1. `next-env.d.ts` está en `.gitignore` por convención canónica de Next.js (verificable en `npx create-next-app` template).
2. Next 16.2.6 lo regenera automáticamente en `next dev` y `next build` (fase setup pre-typecheck).
3. Build fresco hoy confirmó: `npm run build` → `Compiled successfully in 876ms` → `Running TypeScript ...` → `Finished TypeScript in 674ms` → 3 rutas generadas. Sin warnings ni errores sobre `next-env.d.ts`.
4. CI (typecheck + build) corre `next build` lo cual regenera el archivo antes del TS check.

**Conclusión binaria:** register-only justificado. No rompe build, no rompe typecheck, convención canónica de Next. Trackeado en `todo.md` línea 367 explícitamente.

✅ **F-D3.0-07 register-only ACEPTADO.**

## §4 Vulns moderate residuales — análisis binario

`npm audit` fresh reporta exactamente:

```
postcss  <8.5.10
Severity: moderate
PostCSS has XSS via Unescaped </style> in its CSS Stringify Output - GHSA-qx2v-qp2m-jg93
node_modules/next/node_modules/postcss
  next  9.3.4-canary.0 - 16.3.0-canary.5
  Depends on vulnerable versions of postcss
  node_modules/next

2 moderate severity vulnerabilities
```

**Análisis binario de la cadena:**

1. **Una sola CVE distinta** (`GHSA-qx2v-qp2m-jg93`), contada 2 veces porque el dep tree la encuentra en 2 paths (`next` directo y `node_modules/next/node_modules/postcss`).
2. **Scope del CVE:** XSS via `Unescaped </style>` en `Stringify Output` de PostCSS. Requiere atacante con control sobre **input CSS arbitrario** procesado por PostCSS en runtime con output servido como HTML.
3. **Cadena en La Forja:**
   - `postcss <8.5.10` está **transitivo dentro de `node_modules/next/node_modules/postcss`**, aislado al uso interno de Next (build-time CSS processing).
   - El frontend usa Tailwind 4 + `@tailwindcss/postcss` a nivel proyecto, que sí está bumpeado a `postcss 8.5.14` top-level (sin vuln).
   - La Forja **no permite** que un usuario externo inyecte CSS arbitrario procesable por PostCSS interno de Next (no hay CSS-in-runtime API expuesta).
4. **Fix upstream requerido:** Next.js debe publicar release con `postcss >=8.5.10` en su dependency interno. Hasta entonces, `npm audit fix --force` propone downgrade a `next@9.3.3` (regresión catastrófica de versión major, inviable).
5. **Mitigación efectiva ya aplicada:** Manus bumpeó `postcss` top-level a `8.5.14`, lo cual es la única acción posible para CSS processing de proyecto.

**Conclusión binaria:** las 2 moderate son **una sola CVE upstream de Next**, scope build-time CSS interno del framework, **no fixable sin downgrade catastrófico**. Aceptables hasta que Next publique fix upstream. **Tracked register-only D6** (recomendado: chequear `npm audit` semanal y bump Next cuando publique 16.2.7+ con postcss interno >=8.5.10).

✅ **2 moderate residuales ACEPTADAS** con análisis binario documentado.

## §5 Validación pre-commit reproducible (fresca hoy en audit)

| Comando | Output | Veredicto |
|---|---|---|
| `npm run typecheck` (tsc 5.7.3) | 0 errores | ✅ |
| `npm test` (vitest 4.1.6) | **8 passed (8)** en 272ms (2 files) | ✅ |
| `npm run build` (Next 16.2.6 Turbopack) | `Compiled successfully in 876ms`, 3 rutas (`/`, `/_not-found` static + `/salud` Dynamic ƒ) | ✅ |
| `npm run lint` (eslint 9.39.4 flat) | 0 errors, 0 warnings | ✅ |
| `npm audit` | 2 moderate (analizados §4) | ⚠️ ACEPTADO |

## §6 Reglas Duras del Monstruo — Compliance binario D3.0 hardening

| Regla | Estado | Evidencia |
|---|---|---|
| #1 NO self-merge | ✅ | `3135399` y `18f7f7f` en `sprint/la-forja-001`, 0 en main |
| #2 calidad premium (TS strict + flat ESLint + vitest) | ✅ | typecheck + lint + tests verdes |
| LF-1 frontend NUNCA habla con Supabase | ✅ | `next.config.ts:10-14` comentario explícito; `api.ts` solo pega al backend Hono via `NEXT_PUBLIC_API_URL` |
| LF-2 versiones validadas magna real-time | ✅ | Manus bumpeó happy-dom + vitest + eslint + postcss a latest post-Perplexity verificación |
| Regla Dura #6 fail-loud envs | ✅ | `env.ts` con Zod + `[la-forja:web_env_load_strict_failed]` + `[la-forja:web_env_load_permissive_blocked_in_production]` |
| Brand Engine `[la-forja:web_*]` | ✅ | `api.ts:21` `[la-forja:web_api_request_failed]`. `salud/page.tsx:58,67` `[la-forja:health_ok]` / `[la-forja:web_health_check_failed]`. `eslint.config.mjs:22` id-match enforced |
| DSC-G-008 v4 error path coverage | ✅ N/A | D3.0 no introduce nuevas llamadas LLM dentro de rutas (es scaffold). Vigente para D3.2+ cuando llegue chat tutor SSE |
| DSC-S-016 anti-fabricación sin grep | ✅ | Audit ejecutó `git show --stat`, `grep`, lecturas binarias de 6 archivos, `npm run typecheck`, `npm test`, `npm run build`, `npm run lint`, `npm audit` |

## §7 Atribución binaria de CI rojos persistentes

Los 3 fallos CI persistentes (`Lint & Type Check transversal/`, `Unit Tests anti_dory/`, `semgrep`) siguen siendo preexistentes del repo `main`. D3.0 hardening **no introdujo nuevos rojos**:
- `git diff --name-only 6401a3b..3135399` toca exclusivamente `apps/la-forja/web/*` y `apps/la-forja/todo.md`.
- D3.0 no toca `transversal/`, `tests/anti_dory/`, ni archivos auditados por semgrep en main.

✅ Atribución previa vigente. Deuda técnica separada del repo.

## §8 Consecuencias materiales si se autoriza D3.1

Si firmo VERDE y autorizo D3.1:

1. **Cero cambio en `main`**: PR #133 sigue OPEN. Branch protection vigente.
2. **D3.1 arranca**: Manus E1 implementa `/onboarding` con 5-7 pasos estáticos (sin LLM, sin SSE). Solo HTML + componentes React + Brand DNA tokens.
3. **Cero llamadas LLM nuevas**: el Tour estático no invoca ningún modelo, por lo que DSC-G-008 v4 no aplica (vigente para D3.2 chat tutor).
4. **2 moderate residuales persisten** hasta Next publique fix postcss upstream. Tracked register-only D6.
5. **Frontend sigue aislado**: LF-1 vigente, no toca Supabase ni LLMs directamente.

Cero bombas en producción detectadas.

## §9 Hallazgos register-only D6 (no bloquean D3.1)

Inventario consolidado de hallazgos diferidos para D6 polish:

| ID | Origen | Justificación register-only |
|---|---|---|
| F-D3.0-07 | Perplexity D3.0 | `next-env.d.ts` regenerado automáticamente por Next; convención gitignore |
| Vulns postcss <8.5.10 transitivo | npm audit fresh | Fix upstream Next requerido; mitigación top-level ya aplicada |
| H-6 PII regex México | Audit D2.5 register | Expandir CURP, INE, NSS IMSS, tarjeta con dashes |
| H-7 Anthropic thinking adaptive vs enabled | Audit D2.5 register | Verificar contra docs oficiales |
| H-8 OpenAI Responses API shape | Audit D2.5 register | Test integración con SDK mockeado |
| H-9 @google/genai contents shape | Audit D2.5 register | Verificar contra docs SDK 2.x |
| H-10 Perplexity citations defensivo | Audit D2.5 register | `return_citations:true` + warning si len===0 |
| H-11 fix comment middleware order | Audit D2.5 register | `index.ts:115` |
| H-13 SupabaseBudgetClient atómico D5 | Audit D2 register | `UPDATE` arithmetic atómico (NUNCA SELECT-then-UPDATE) |
| H-14 LLM client cache invalidation | Audit D2.5 register | Path strict:false |
| OBS-1 D4 DEV_USER_ROLE → cerrado por H-1 D2.5 | n/a | Ya cerrado |
| OBS-3 rate limit in-memory horizontal | Audit D2 register | Considerar Redis o Supabase row-level locking si escala |

Total backlog D6: ~11 items, ninguno bloquea D3.1-D3.4.

## §10 Firma binaria

```
SPRINT:           LA-FORJA-001 v3.2 — D3.0 HARDENING POST-PERPLEXITY
COMMITS:          3135399 (hardening) + 18f7f7f (bridge adversarial)
SOBRE:            e10169f (scaffold web D3.0)
PR:               #133 (READY, mergeable=MERGEABLE)
AUDITOR:          Cowork T2-A (Claude Opus 4.7 / 1M context)
SESIÓN:           bold-neumann-ef6284
FECHA:            2026-05-16
METODOLOGÍA:      audit DELTA hardening (NO firma DSC nueva — fixes, no contrato)
DSC vigente:      DSC-G-008 v4 (delta sobre v3 — error path coverage LLM en rutas)

VERIFICACIONES FRESCAS:
  typecheck:      ✅ 0 errores
  vitest:         ✅ 8/8 passing (272ms, 2 files)
  next build:     ✅ verde, /salud Dynamic
  eslint:         ✅ 0/0
  npm audit:      ⚠️ 2 moderate (analizadas y aceptadas §4)

FIXES APLICADOS:  ✅ 12/12 verificados binariamente contra código
REGISTER-ONLY:    ✅ 1 (F-D3.0-07) justificado
VULNS RESIDUAL:   ⚠️ 2 moderate (postcss upstream Next, fix-on-bump)
REGLAS DURAS:     ✅ #1, #2, LF-1, LF-2, #6 cumplidas
BRAND ENGINE:     ✅ `[la-forja:web_*]` enforced via id-match `error`
CI ROJOS:         ✅ los 3 persistentes siguen preexistentes
DECISION:         ✅ D3.0 SCAFFOLD POST-HARDENING = SHIP
```

🟢 **LA-FORJA-001 D3.0 HARDENING — AUDIT VERDE · D3.1 AUTORIZADO**

## §11 Próximos pasos binarios

1. **Cowork (este turno):** commit + push de este bridge file.
2. **Manus E1:** arranca **D3.1 Tour onboarding estático** (5-7 pasos, sin LLM, sin SSE). Solo React + Brand DNA tokens + persistencia `POST /api/users/onboarding-status` (endpoint backend pendiente — coordinar si requiere D2.6).
3. **T1-Alfredo:** PR #133 sigue READY mergeable. Decide merge manual o instruye Cowork directo.
4. **D6 polish:** chequear `npm audit` semanal y bumpear Next a 16.2.7+ cuando publique fix de postcss interno.
5. **D3.2+ chat tutor SSE:** aplicar DSC-G-008 v4 si introduces nueva ruta backend que invoque LLM (try/catch + adjustSpent rollback + test negativeCalls).

Si surge contradicción binaria entre este audit y la realidad D3.1, prevalece la realidad. Este veredicto es firme.

— Cowork T2-A · LA-FORJA-001 v3.2 · D3.0 HARDENING VERDE · 16 mayo 2026
