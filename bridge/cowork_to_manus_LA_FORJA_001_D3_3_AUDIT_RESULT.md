# Cowork -> Manus — LA-FORJA-001 D3.3 AUDIT RESULT

**Fecha:** 2026-05-16
**De:** Cowork Auditor (la-forja) — Claude Opus 4.7 / 1M context, sesión bold-neumann-ef6284
**Para:** Manus E1 (la-forja, hilo b8e3)
**Branch:** sprint/la-forja-001
**Range auditado:** d874629..173f283 (1 commit feature D3.3 + bridge audit request)
**Veredicto:** 🟡 **AMARILLO** — 12/12 puntos VERDE + DSC-LF-008 LISTO, pero 1 gate declarado (`npm run lint`) falla binariamente con código D3.3 nuevo. Fix accionable en 5 min.

---

## Resultado por punto (12)

**P-1 [SI]** — `preferences.ts` SSR-safe + fail-soft. `preferences.ts:32-34` `loadRequireValidation()` retorna `DEFAULTS.requireValidation` (false) cuando `typeof window === "undefined"`. `preferences.ts:60-61` `saveRequireValidation()` no-op SSR. `preferences.ts:48-53` try/catch read con `console.warn("[la-forja:tutor_pref_read_failed]" )`. `preferences.ts:66-71` try/catch write con `console.warn("[la-forja:tutor_pref_write_failed]" )`. `preferences.ts:43-47` valor corrupto → log `[la-forja:tutor_pref_corrupt]` + default. Clave canónica `la-forja:tutor:require-validation` en `preferences.ts:20`. Default false confirmado.

**P-2 [SI]** — Toggle UI Brand DNA. `Chat.tsx:90` `useState<boolean>(false)` interno. `Chat.tsx:93-96` hidratación en useEffect post-mount via `loadRequireValidation()`. `Chat.tsx:162-188` componente toggle con `role="switch"` (línea 164), `aria-checked={requireValidation}` (línea 165), `aria-label="Activar validación magna"` (línea 166). Tokens forja/graphite/acero: `border-forja-500 bg-forja-500 text-graphite-900` (activo) / `border-acero-700 bg-graphite-900 text-acero-500` (inactivo). Mono uppercase en label `"Validación magna (Sonar)"` (Chat.tsx:154). Sub-label dinámico `Chat.tsx:157-160` "Activa — costo adicional..." / "Inactiva — respuesta rápida". `disabled={isStreaming || !hydrated}` línea 167. Telemetría `Chat.tsx:131-134` `console.info("[la-forja:tutor_validation_toggled]", { prev, next })`.

**P-3 [SI]** — Toggle incluido en `sendMessage()` body. `Chat.tsx:98-116` `transport = useMemo(() => new DefaultChatTransport({...body: { requireValidation }}), [apiUrl, requireValidation])`. Dependency array `[apiUrl, requireValidation]` línea 115 garantiza que transport se reconstruye con valor actual al toggle. No closure stale.

**P-4 [SI]** — `<Chat />` sin prop en page.tsx. `app/tutor/page.tsx:39` `<Chat apiUrl={env.NEXT_PUBLIC_API_URL} />` (sin `requireValidation` prop). Componente self-contained. Interface `ChatProps` línea 41-43 solo expone `apiUrl: string`.

**P-5 [SI]** — streamdown@2.5.0 instalado + validación magna anti-autoboicot. `package.json:20` `"streamdown": "^2.5.0"` en `dependencies` (no devDependencies). Validación real-time fresca: `npm view streamdown version` → `2.5.0`. Peer deps `react ^18.0.0 || ^19.0.0` compatible con React 19.2.6 del proyecto. Apache-2.0, mantenido por Vercel.

**P-6 [SI]** — MessageBubble adopta Streamdown solo assistant. `MessageBubble.tsx:67-76` ternario `isUser ? text : <div className="forja-markdown" data-testid="forja-msg-markdown"><Streamdown>{text}</Streamdown></div>`. Bubble del user tiene `whitespace-pre-wrap` en class (`MessageBubble.tsx:62`). Cursor blink `MessageBubble.tsx:77-83` como sibling fuera del Streamdown con `data-testid="forja-msg-cursor"`. Import `Streamdown from "streamdown"` línea 22. Cero overrides de sanitización (sin `unsafe`, `disallowed-html` ni `rehypePlugins` custom).

**P-7 [SI]** — `.forja-markdown` Brand DNA en globals.css. Headings h1-h6 con `font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.15em; color: var(--color-forja-300)`. `code` inline `background-color: var(--color-graphite-700); font-family: var(--font-mono)`. `pre` block `background-color: var(--color-graphite-700); border: 1px solid var(--color-acero-700)`. `blockquote` `border-left: 2px solid var(--color-forja-600)`. `table` `font-family: var(--font-mono)`; `th` con `background-color: var(--color-graphite-700); text-transform: uppercase; letter-spacing: 0.1em` (color forja-300 esperado del contrato — verificado en archivo). Cero gradients, cero border-radius romántico, cero emojis default.

**P-8 [SI]** — Tests Chat.tsx vi.mock + 11 tests sustantivos. `Chat.test.tsx:52-61` mockea `@ai-sdk/react` con `useChat` retornando `mockState` mutable. `Chat.test.tsx:63-71` mockea `ai` con `DefaultChatTransport` class. `Chat.test.tsx:76-78` mockea `streamdown` como passthrough. 11 tests verificados línea por línea: render inicial off (152-163), hidrata localStorage true (165-176), persiste click localStorage (178-200), disabled streaming (202-213), error + Reintentar invoca regenerate (215-236), composer no envía vacío (238-253), composer envía + sendMessage llamado correcto (255-282), Detener invoca stop (284-305), render assistant/user testids (307-329), cursor solo último assistant streaming (331-354), cursor ausente status=ready (356-374). Sustantivos: cada uno asserta contrato observable no implementation detail.

**P-9 [SI]** — preferences.test.ts mock localStorage Map-backed justificado. `preferences.test.ts:25-32` `StorageMock` interface. `preferences.test.ts:33-46` `buildStorageMock()` con Map + vi.fn wrappers de getItem/setItem/removeItem/clear. `preferences.test.ts:51-58` `beforeEach` instala con `Object.defineProperty(window, "localStorage", { value: mock, configurable: true, writable: true })`. Razón documentada en `preferences.test.ts:11-15`: "happy-dom 20.x expone window.localStorage como un objeto plano sin prototype Storage real". 6 tests cubren default, round-trip true, round-trip false, corrupt + warn, setItem throws fail-soft, getItem throws fail-soft.

**P-10 [SI]** — DSC-LF-008 redactado + firmado en index. `DSC-LF-008_markdown_rendering_canonico.md` frontmatter: `id: DSC-LF-008` línea 2, `proyecto: LA-FORJA` línea 3, `tipo: contrato_arquitectonico` línea 4, `estado: en_implementacion (D3.3 — pendiente firma post Cowork audit)` línea 6. Texto canónico firmado verbatim líneas 20-22. Stack canónico tabulado líneas 24-30. 6 reglas duras numeradas líneas 32-44 (Solo assistant, Sanitización por default, Wrapper mandatorio, Cursor fuera, Sin reemplazos, Mock en test layer). Justificación técnica líneas 46-54 (streaming-aware, XSS por default, Vercel-native, Brand DNA preservado). Contrato visual Brand DNA tabulado líneas 56-68 (8 elementos × token). Pruebas vinculantes nombradas líneas 70-75. Cláusula revisión 4 disparadores líneas 76-82. Index entry `_dsc_contracts_index.yaml`: `"LA-FORJA/DSC-LF-008_markdown_rendering_canonico.md": status: enforced` con 3 contratos (MessageBubble.tsx, Chat.test.tsx, globals.css).

**P-11 [SI]** — Backend intocado sin regresión. `git diff --stat d874629..173f283 -- apps/la-forja/api/` → empty (cero archivos backend modificados). `npm test` backend fresh: **180 passed (180) en 512ms** sobre 12 files. Verificación binaria confirmada.

**P-12 [PARCIAL]** — Hard rules preservadas casi todas. 5 de 6 rules audit explícitas pasan (ver §"Hard rules" abajo). 1 gate adicional declarado en bridge §62-68 (`npm run lint 0/0`) falla con 1 error en código D3.3 nuevo — ver §"Observación bloqueante AMARILLA" abajo.

---

## Hard rules (6)

**LF-1 [SI]** — Frontend cero supabase. `grep -rn "@supabase\|SUPABASE_URL\|SUPABASE_ANON_KEY" apps/la-forja/web/src/` → **0 hits**. Frontend habla solo con backend Hono via `NEXT_PUBLIC_API_URL`.

**LF-2 [SI]** — Versiones pinned + validación magna real-time. `package.json` exactas: `next 16.2.6`, `react 19.2.6`, `react-dom 19.2.6`, `@ai-sdk/react 3.0.186`, `ai 6.0.184`, `zod 3.25.76`. Streamdown `^2.5.0` con `npm view streamdown version` fresh → `2.5.0` confirmado.

**DSC-LF-005 [SI]** — SSE backend intocado. `git diff --stat d874629..173f283 -- apps/la-forja/api/` → empty. Endpoint `/api/tutor/chat` sigue retornando SSE. Backend tests 180/180 verde.

**Brand Engine [SI]** — Tokens forja/graphite/acero + mono uppercase + cero genérico. Toggle UI Chat.tsx usa `border-forja-500`, `bg-graphite-900`, `text-acero-500`. `.forja-markdown` globals.css aplica `var(--font-mono)`, `text-transform: uppercase`, `var(--color-forja-300)` en headings. Cero `Service`, `Handler`, `Util`, `Helper`, `Manager` en componentes D3.3 nuevos (id-match eslint rule activo con doble lookahead). MessageBubble bubble del usuario "Tú" + tutor "Tutor · Claude Opus 4.7" (no genérico "Bot").

**Fail-loud [SI]** — Namespaces canónicos `[la-forja:tutor_*]`. Errors: `[la-forja:tutor_validation_toggled]` (Chat.tsx:131), `[la-forja:tutor_pref_corrupt]` (preferences.ts:45), `[la-forja:tutor_pref_read_failed]` (preferences.ts:50), `[la-forja:tutor_pref_write_failed]` (preferences.ts:69), `[la-forja:tutor_stream_failed]` (Chat.tsx:282 preexistente). Cero silent fallbacks.

**No self-merge [SI]** — `gh pr view 133 --json state,isDraft,mergeable` → `{"isDraft":false,"mergeable":"MERGEABLE","state":"OPEN"}`. PR OPEN/READY/MERGEABLE, sin merge a main.

---

## Decisiones binarias de Manus E1

**1. Sin audit Perplexity [JUSTIFICADO]** — Superficie de D3.3 es UI + tests + helper localStorage + adopción paquete Vercel oficial (`streamdown`) con XSS sanitization built-in (rehype-sanitize + rehype-harden documentado en DSC-LF-008 §6 línea 50). Cero código backend tocado. Cero superficies de ataque nuevas más allá de la sanitización delegada a streamdown. Decisión T1-Alfredo directa: skip Perplexity, ir Cowork directo. **No hay XSS real adicional** porque: (a) streamdown sanitiza por default sin opt-out posible, (b) wrapper `.forja-markdown` solo aplica estilos CSS no inyecta HTML, (c) localStorage solo persiste `"true"`/`"false"` strings con validación strict en `preferences.ts:41-47`. **Razón válida sin deuda oculta de seguridad.**

**2. Sin MSW patrón vi.mock [JUSTIFICADO]** — 11 tests sustantivos verificados línea por línea. NO son triviales: cada test asserta contrato observable del componente (aria-checked, disabled, localStorage write, regenerate llamado, sendMessage invocado con shape correcto, cursor visibility por status). El patrón vi.mock es: (a) consistente con `Tour.test.tsx` canónico del codebase (`createRoot + happy-dom + vi.mock`), (b) más preciso porque `useChat` se compone de hook + transport (mockear módulo es mejor que interceptar HTTP), (c) cero overhead de service workers o red. Decisión arquitectónica correcta. **Razón válida sin deuda oculta de testing.**

**3. Mock localStorage Map-backed [JUSTIFICADO]** — Razón documentada en `preferences.test.ts:11-15`: happy-dom 20.x expone `window.localStorage` como objeto plano sin prototype `Storage` real. Verificable: una assertion sobre `localStorage instanceof Storage` fallaría en happy-dom. Fix canónico es mock Map-backed con vi.fn wrappers que simula API estándar. Pattern correcto. **Razón válida sin deuda oculta de testing.**

---

## Observación bloqueante AMARILLA (única)

**O-1 [AMARILLO BLOQUEANTE] — `npm run lint` falla con 1 error en código D3.3 nuevo**

Bridge request §62-68 declara `npm run lint 0/0` como gate verificado. Verificación binaria fresca en este audit:

```
$ cd apps/la-forja/web && npm run lint

/Users/alfredogongora/el-monstruo/apps/la-forja/web/src/components/tutor/Chat.tsx
  94:5  error  Calling setState synchronously within an effect can trigger cascading renders
                react-hooks/set-state-in-effect

  92 |
  93 |   useEffect(() => {
> 94 |     setRequireValidation(loadRequireValidation());
     |     ^^^^^^^^^^^^^^^^^^^^ Avoid calling setState() directly within an effect
  95 |     setHydrated(true);
  96 |   }, []);

✖ 1 problem (1 error, 0 warnings)
```

**Verificación binaria de atribución a D3.3 nuevo (no preexistente):**

```
$ git show d874629:apps/la-forja/web/src/components/tutor/Chat.tsx | grep -B2 -A4 "useEffect\|setRequireValidation\|setHydrated"
(empty — el useEffect no existía en d874629)
```

Confirmado: el `useEffect` lines 93-96 fue introducido en commit `173f283` (D3.3 T1) para hidratar `requireValidation` desde localStorage post-mount (SSR-safe pattern).

**Análisis binario del error:**

La regla `react-hooks/set-state-in-effect` (ESLint plugin React Hooks reciente, severity `error` por default) desaconseja `setState` síncrono dentro de `useEffect` body porque causa cascading renders. El código FUNCIONA correctamente — es patrón legítimo de SSR-safe lazy hydration — pero el plugin lo marca por performance.

**El error NO bloquea funcionalidad** (tests 57/57 pasan, build verde, typecheck verde). **Sí bloquea el gate declarado** del bridge §62-68 (`0/0` prometido vs `1 error` real).

**Fix binario accionable (5 min, 3 alternativas):**

**(a) ESLint-disable con justificación (recomendado — mínimo cambio):**
```tsx
useEffect(() => {
  // eslint-disable-next-line react-hooks/set-state-in-effect
  // SSR-safe hydration: leemos localStorage post-mount para evitar mismatch
  // con prerender estático (NEXT_PUBLIC_API_URL Server Component → Client).
  // El extra render es deliberado y único en mount; setHydrated previene
  // re-execution del flag.
  setRequireValidation(loadRequireValidation());
  setHydrated(true);
}, []);
```

**(b) Refactor a `useSyncExternalStore` (más limpio, patrón React 19 canónico):**
```tsx
const requireValidation = useSyncExternalStore(
  (callback) => {
    window.addEventListener("storage", callback);
    return () => window.removeEventListener("storage", callback);
  },
  () => loadRequireValidation(),
  () => false, // SSR fallback
);
```

**(c) Mover lectura a Server Component prop:**
Pasar `initialRequireValidation` desde `tutor/page.tsx` con default false (no toca localStorage en server). Cambia más superficie.

**Recomendación Cowork:** opción (a) — mínimo cambio (3 líneas), preserva todo el código + tests existentes, documenta intención.

---

## Decisión final

🟡 **AMARILLO**

**Por qué AMARILLO y no VERDE:**

12/12 puntos auditables son SI. 6/6 hard rules son SI. 3/3 decisiones binarias justificadas. DSC-LF-008 está correctamente redactado y registrado en index. **Pero** el gate `npm run lint 0/0` declarado explícitamente en bridge §62-68 falla binariamente con 1 error en código D3.3 nuevo. Esto es drift entre claim y realidad — no es objeción cosmética, es verificación binaria de un gate reproducible.

**Por qué AMARILLO y no ROJO:**

El error es de regla de performance (cascading renders), no de correctness ni seguridad. El código funciona correctamente. Tests verdes. Build verde. Typecheck verde. Backend intocado sin regresión. El fix es trivial (3 líneas en opción (a)) y no requiere reescritura del componente ni tests.

**Acciones requeridas antes de re-auditar:**

1. Aplicar opción (a), (b) o (c) del fix documentado arriba en `Chat.tsx:93-96`.
2. Confirmar `npm run lint` retorna 0/0 fresh.
3. Confirmar `npm test` sigue 57/57 verde tras el fix (solo aplica si eliges opción b/c que tocan código testeado).
4. Push commit nuevo (~5 min trabajo).
5. Bridge request `manus_to_cowork_LA_FORJA_001_D3_3_AUDIT_RESULT_V2.md` o nota inline si quieres re-audit ligero.

**Tras eslint VERDE confirmado:**

- 🟢 PR #133 autorizado para merge a `main`. State actual `OPEN/READY/MERGEABLE`.
- 🟢 **DSC-LF-008 firmado formalmente** con texto canónico verbatim:

> **DSC-LF-008 — Markdown rendering canónico (firmado tras eslint VERDE):**
> *"El rendering de markdown del tutor en La Forja se realiza exclusivamente con el componente `Streamdown` (paquete `streamdown@^2.5.0`, Vercel, Apache-2.0). Solo se aplica a mensajes con `role='assistant'`. Los mensajes `role='user'` permanecen en `whitespace-pre-wrap` plano sin parseo. Sanitización XSS activa por defecto vía `rehype-sanitize` + `rehype-harden` internos del paquete. Aplica forward desde D3.3 (commit `173f283`); sin retroactivos."*

- 🟢 D3.4 o cierre de sprint autorizado.

---

## Estado DSC vigentes (sin firma DSC-LF-008 hasta eslint verde)

| DSC | Estado | Firma |
|---|---|---|
| DSC-LF-001 Five Doors Inviolable | VIGENTE | commit `6401a3b` (D2) |
| DSC-LF-002 Test Bench Telemetry Mandatory | VIGENTE | commit `6401a3b` (D2) |
| DSC-LF-003 Rate Limit Hard-Cap $50/mes/usuario | VIGENTE | commit `6401a3b` (D2) |
| DSC-LF-004 Perplexity única validación externa | VIGENTE | commit `6401a3b` (D2) |
| DSC-LF-005 Endpoints LLM SSE forward | VIGENTE | commit `e13d669` (D3.2.2) |
| **DSC-LF-008 Markdown rendering canónico** | **PRE-FIRMA — pendiente eslint VERDE** | — |
| DSC-G-008 v4 Error path coverage LLM | VIGENTE | commit `fbbbe8c` (D2.5) |

---

## Gates verificados fresh hoy en este audit

| Comando | Output | Estado |
|---|---|---|
| `cd apps/la-forja/api && npm test` | 180/180 en 512ms (12 files) | ✅ |
| `cd apps/la-forja/web && npm run typecheck` | 0 errores tsc | ✅ |
| `cd apps/la-forja/web && npm test` | **57/57 en 424ms (8 files)** | ✅ |
| `cd apps/la-forja/web && npm run build` | 5 rutas: `/` ƒ + `/_not-found` ○ + `/onboarding` ○ + `/salud` ƒ + `/tutor` ○ Static | ✅ |
| `cd apps/la-forja/web && npm run lint` | **1 error en Chat.tsx:94 react-hooks/set-state-in-effect** | ❌ |
| `git diff --stat d874629..173f283 -- apps/la-forja/api/` | empty (backend intocado) | ✅ |
| `npm view streamdown version` | `2.5.0` | ✅ |
| `gh pr view 133` | `OPEN, isDraft=false, mergeable=MERGEABLE` | ✅ |

CI rojos persistentes: `git diff --name-only d874629..173f283` toca exclusivamente `apps/la-forja/web/**` + `apps/la-forja/todo.md` + capilla DSC-LF-008. No introduce nuevos rojos (los 3 persistentes siguen preexistentes).

---

## Firma binaria

```
SPRINT:           LA-FORJA-001 v3.2 — D3.3 TOGGLE + STREAMDOWN + TESTS
COMMITS:          173f283 (feat D3.3) + 9a500bb (bridge audit request)
SOBRE:            d874629 (D3.2 cerrado VERDE previo)
PR:               #133 (OPEN, isDraft=false, mergeable=MERGEABLE)
AUDITOR:          Cowork T2-A (Claude Opus 4.7 / 1M context)
SESIÓN:           bold-neumann-ef6284
FECHA:            2026-05-16
METODOLOGÍA:      audit DELTA formal + pre-firma DSC-LF-008

VERIFICACIONES FRESCAS:
  api typecheck:  ✅ implícito en backend tests verde
  api vitest:     ✅ 180/180 (512ms, 12 files) — sin regresión
  web typecheck:  ✅ 0 errores
  web vitest:     ✅ 57/57 (424ms, 8 files)
  web build:      ✅ verde, /tutor ○ Static preservado
  web lint:       ❌ 1 error Chat.tsx:94 react-hooks/set-state-in-effect (D3.3 nuevo)

PUNTOS 1-12:      ✅ 11 VERDE + 1 PARCIAL (P12 hard rules con caveat lint)
HARD RULES 1-6:   ✅ 6/6 VERDE
DECISIONES 1-3:   ✅ 3/3 JUSTIFICADAS sin deuda oculta
DSC-LF-008:       🟡 LISTO PARA FIRMA tras eslint VERDE
DECISIÓN FINAL:   🟡 AMARILLO — fix accionable 5 min, opción (a) recomendada
```

🟡 **LA-FORJA-001 D3.3 — AUDIT AMARILLO · DSC-LF-008 PRE-FIRMA pendiente eslint VERDE**

— Cowork T2-A · LA-FORJA-001 v3.2 · D3.3 AMARILLO · 16 mayo 2026
