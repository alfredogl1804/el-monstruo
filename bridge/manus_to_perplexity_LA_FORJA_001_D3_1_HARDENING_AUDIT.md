# Bridge — Manus La-Forja → Perplexity Sonar Reasoning Pro
## Tarea: D3.1-HARDENING regression audit (delta `e125c4c..84c728f`)

**Fecha:** 16-may-2026 CST
**Auditor:** Perplexity Sonar Reasoning Pro (auditor principal externo)
**Auditado:** Manus La-Forja (Hilo E1, ejecutor sprint LA-FORJA-001)
**Repo:** `https://github.com/alfredogl1804/el-monstruo`
**Branch:** `sprint/la-forja-001`
**Acceso:** Perplexity tiene acceso al repo público vía Sonar.

---

## Contexto previo (binario)

En tu auditoría anterior contra commit `e125c4c` (D3.1 tour onboarding) entregaste **15 F-patterns** y veredicto `DO NOT SHIP`. Manus E1 procesó cada uno binariamente y aplicó:

- **14 fixes confirmados** (F-D3.1-01 a F-D3.1-11, F-D3.1-13, F-D3.1-14, F-D3.1-15)
- **1 register-only D6** con migración defensiva (F-D3.1-12)

El delta vive en 2 commits sobre branch `sprint/la-forja-001`:

- `6646544` `hardening(la-forja): D3.1 adversarial fixes Perplexity F-D3.1-01..15 (33/33 tests)`
- `84c728f` `docs(la-forja): bridge Perplexity D3.1 adversarial prompt + 15 F-patterns response`

Diff stats: **15 archivos, +694/-121 LOC, 1 archivo eliminado (`OnboardingFinishHandler.tsx`), 2 archivos nuevos (`version.ts`, `vitest.setup.ts`)**.

Gates post-fix reportados por Manus:
- `npm run lint` 0/0
- `npx tsc --noEmit` 0 errores
- `npx vitest run` 33/33 passing (8 D3.0 + 25 D3.1)
- `npx next build` verde, 4 rutas (`ƒ /`, `ƒ /onboarding`, `ƒ /salud`, `○ /_not-found`)

---

## Tu tarea binaria

Lee el delta directamente del repo:

```
git show 6646544
git show 84c728f
git diff e125c4c..84c728f
```

O ruta-por-ruta los archivos modificados:

```
apps/la-forja/web/eslint.config.mjs
apps/la-forja/web/src/lib/onboarding/cookie.ts
apps/la-forja/web/src/lib/onboarding/cookie.test.ts
apps/la-forja/web/src/lib/onboarding/steps.ts
apps/la-forja/web/src/lib/onboarding/steps.test.ts
apps/la-forja/web/src/components/onboarding/Tour.tsx
apps/la-forja/web/src/components/onboarding/Tour.test.tsx
apps/la-forja/web/src/components/onboarding/StepShell.tsx
apps/la-forja/web/src/app/onboarding/page.tsx
apps/la-forja/web/src/app/page.tsx
apps/la-forja/web/src/lib/version.ts          (NUEVO)
apps/la-forja/web/vitest.config.ts
apps/la-forja/web/vitest.setup.ts              (NUEVO)
apps/la-forja/web/src/app/onboarding/OnboardingFinishHandler.tsx  (ELIMINADO)
```

Tu trabajo es **doble**:

### Tarea A — Verificación binaria de los 14 fixes

Para cada finding F-D3.1-NN que Manus marcó como fixeado, responde **binario**:

- `[CERRADO]` si el fix realmente cierra el defecto
- `[ABIERTO]` si Manus dijo que arregló pero el código sigue vulnerable
- `[PARCIAL]` si el fix mitiga pero deja vector residual

Cada respuesta debe citar **archivo:línea** y la línea exacta que confirma o refuta.

### Tarea B — Detección de regresiones nuevas (R-patterns)

Es **muy probable** que al meter ~700 LOC de fixes Manus haya introducido nuevos bugs. Busca **regresiones nuevas** en formato:

```
R-D3.1-NN [SEV] archivo:línea — defecto introducido por el fix de F-D3.1-XX
verificación: <comando node/grep ejecutable>
patch mínimo: <diff>
```

---

## Áreas obligatorias a auditar

### 1. F-D3.1-01 + F-D3.1-02 — regex id-match

Revisa `apps/la-forja/web/eslint.config.mjs` línea de `"id-match"`. Manus afirma que la nueva regex banea `UserService`, `OnboardingFinishHandler`, etc. **Verifícalo con un script ejecutable** que pruebe contra:

```
UserService, OrderHandler, FormatUtil, StringHelper, AuthManager,
APIService, DataHandler, ConfigUtil, ValidationHelper, EventManager,
service, handler, util, helper, manager,
ForjaTourSteps, ForjaApiClient, getUserById
```

Los primeros 10 deben fallar (banear). Los últimos 3 deben pasar (válidos). Si algún caso patológico viola: `R-pattern`.

### 2. F-D3.1-03 — cookie Secure flag

Revisa `cookie.ts` función `shouldUseSecure()`. Casos a auditar binariamente:

- ¿Funciona si se llama desde Server Component (sin `window`)?
- ¿`documentRef?.defaultView?.location` puede ser `undefined` en happy-dom 20?
- ¿Hay race condition si el script se ejecuta antes de hidratación?
- ¿El test de F-03 cubre el caso HTTPS real (no solo localhost)?

### 3. F-D3.1-04 — guard idempotencia

Revisa `Tour.tsx` `finalize()`. Manus usa `useState` `finished`. Auditá:

- ¿`useState` es suficiente con React 19 batching automático? `setFinished(true)` en click handler — ¿el segundo click llega antes del re-render?
- ¿Qué pasa si el usuario hace click en `next` y luego rápidamente en `skip`? ¿Las DOS llamadas a `finalize` se bloquean?
- ¿El test de doble-click realmente prueba race condition o solo prueba el guard?

### 4. F-D3.1-05 — highlight sort

Revisa `StepShell.tsx` `highlightText()`. Auditá:

- Si `highlights = ["50 USD", "50 USD por mes"]`, ¿el sort + match correctamente captura el más largo en una posición pero el corto en otra del mismo body?
- ¿Qué pasa si un highlight contiene caracteres regex pero el algoritmo usa `indexOf` (no regex)? Confirma binariamente.
- ¿El recorrido `while (remaining.length > 0)` puede tener edge case con highlight vacío?

### 5. F-D3.1-06 — focus + aria-live

Revisa `Tour.tsx` y `StepShell.tsx`. Auditá:

- `isFirstRenderRef` previene robo de scroll en mount. ¿Funciona si `initialIndex !== 0`? ¿Salta el primer focus aunque el usuario aterrizó en paso 3 ya con scroll posicionado?
- `aria-live="polite"` con `aria-atomic="true"` — ¿anuncia TODO el contenido del paso o solo cambios? Para tour de bienvenida, anunciar todo es lo correcto pero confirma WCAG 2.2 SC 4.1.3.
- `tabIndex={-1}` en el `<h2>` — ¿el screen reader anuncia correctamente al recibir foco programático?
- ¿El foco se pierde si el usuario navega a `/` post-finish y vuelve? Test de regresión faltante.

### 6. F-D3.1-07 — focus-visible rings

Revisa los 3 botones (`primary`, `secondary`, `skip`). Auditá:

- Contraste WCAG AA: `forja-300` (`#FDBA74`) vs `graphite-900` (`#1C1917`) — ¿pasa el test de contraste 4.5:1 para texto normal y 3:1 para componentes UI?
- `acero-300` ring en skip — ¿es suficientemente visible vs `graphite-900`?
- ¿El `ring-offset-graphite-900` rompe en algún tema dark/light que el resto del app introduzca después?

### 7. F-D3.1-08 — NaN guard

Revisa `app/page.tsx` `formatTourCompletedAt()`. Auditá:

- Si la cookie tiene `"undefined"` literal (string), ¿`new Date("undefined")` retorna `Invalid Date` o algo más raro?
- Si la cookie tiene un timestamp con offset de timezone (no UTC), ¿se renderiza con el TZ del servidor o del usuario? El display puede mentir.
- ¿Hay XSS posible si un usuario pone una cookie con `<script>` y el servidor la concatena en el HTML? Confirma que `toLocaleString()` retorna texto, no HTML.

### 8. F-D3.1-09 — split regex tolerante

Revisa `cookie.ts` `cookie.split(/;\s*/)`. Auditá:

- ¿Tolera espacios al INICIO de la cookie completa (raro pero posible con proxies)?
- ¿Qué pasa si hay un `;` literal en el VALOR de otra cookie (encoded)? ¿El split lo confunde?
- El test "encoding malformado" devuelve `null` — ¿está bien o debería loggear warning?

### 9. F-D3.1-10 — decode test

Revisa `cookie.test.ts` test "valores con caracteres especiales". Confirma que el test **realmente fallaría** si quitamos `decodeURIComponent` del helper. Si el assertion solo verifica que no crashea, el test es decorativo.

### 10. F-D3.1-11 — StrictMode wrapper

Revisa `Tour.test.tsx` y `vitest.setup.ts`. Auditá:

- React 19 StrictMode hace double-mount en development. ¿Los tests cubren que `useEffect` cleanup funciona correctamente? Si no, los warnings de `act` que Manus silenció pueden estar tapando bugs reales.
- `IS_REACT_ACT_ENVIRONMENT = true` global — ¿afecta test environment de Next.js Server Components si los hubiera?
- Mock de `useRouter` con `vi.mock` — ¿el mock se aplica también si hay otro test que importa `next/navigation` indirectamente?

### 11. F-D3.1-13 — contract test sprint states

Revisa `steps.test.ts` test "menciona literal los 8 estados en orden". Auditá:

- El test usa `fullBody.indexOf(state, cursor)`. Si un estado posterior contiene la subcadena de uno anterior, ¿el match es correcto?
- ¿Qué pasa si el copy del paso menciona los estados en una lista con bullets? El test asume que están en `body.join(" ")`.
- **Falta el test que importa `SPRINT_STATES` del backend y compara binario con `FORJA_TOUR_SPRINT_STATES_LITERAL`.** Manus solo verifica la lista contra una expectativa hardcoded en el test mismo. Si tanto código como test mienten igual, el test pasa.

### 12. F-D3.1-14 — version.ts

Revisa `src/lib/version.ts`. Auditá:

- `import pkg from "../../package.json" with { type: "json" }` — ¿funciona en TypeScript 5.7 build de Next 16 turbopack? ¿O requiere `--experimental-import-attributes`?
- `process.env.NEXT_PUBLIC_FORJA_DELIVERY` — ¿se inlinea en build time? ¿O se lee runtime y rompe SSG/ISR?
- El fallback `"D3.1"` queda hardcoded — defeats the purpose. Cuando D3.2 llegue y nadie setee la env var, el header sigue diciendo "D3.1".

### 13. F-D3.1-15 — eliminación wrapper

Revisa `Tour.tsx` con `useRouter`. Auditá:

- `useRouter` solo funciona dentro de Client Components con App Router. Si Manus lo usó pero el componente está montado en una ruta donde no hay router (tests sin mock), ¿crashea?
- Mock `vi.mock("next/navigation")` cubre los tests, pero ¿qué pasa si en producción el `redirectTo` tiene un valor con caracteres que `router.push` rechaza (ej. spaces, query strings)?
- Eliminar `OnboardingFinishHandler` ELIMINÓ la prop `onFinish` callback custom — ¿ahora `Tour.tsx` ya no permite callback externo? **Verifica binariamente leyendo `Tour.tsx`.**

### 14. Integridad cross-file

- `package.json` no fue modificado pero `vitest.setup.ts` se agregó como dependency de la config. ¿`package.json` o `tsconfig.json` necesitan declarar el archivo en algún `include`?
- `version.ts` agrega `import pkg from "../../package.json"` — ¿`tsconfig.json` tiene `resolveJsonModule: true`?
- `aria-live` cambios — ¿hay tests que verifican el atributo en el DOM? Si no, se puede romper sin que nadie note.

### 15. Build flags y runtime

- `dynamic = "force-dynamic"` en `/onboarding` — ¿es necesario? La página solo lee router en CSR, no usa `cookies()` ni headers en server. Removerlo permitiría prerender estático y mejor performance. ¿Manus dejó este flag por costumbre desde D3.0?
- `useRouter` ahora vive en `Tour.tsx` que está dentro de `/onboarding`. ¿La página podría ser estática y solo el componente dynamic? Auditá si el `force-dynamic` es overkill.

---

## Reglas anti-soft-talk

Prohibido:
- "Considera"
- "Podría"
- "Industry standard"
- "Best practices in general"
- "Depending on requirements"
- "It would be wise to"

Si las usas, **invalido el F y se lo digo**.

Cada finding debe ser binario, verificable con comando ejecutable, y citar archivo:línea exacta.

---

## Hard rules a verificar

- **LF-1** frontend NUNCA habla con Supabase directo
- **LF-2** versiones validadas magna real-time
- **LF-FIVE-DOORS-001** exactamente 5 puertas, el tour no agrega 6ª
- **DSC-LF-003** "50 USD" del tour coincide literal con `apps/la-forja/api/src/lib/budget.ts`
- **SPEC §4:130** los 8 estados del sprint son inglés exactos
- **Regla Dura #6** fail-loud envs
- **Brand Engine** namespace `[la-forja:web_*]` + ban `Service|Handler|Util|Helper|Manager`
- **No self-merge**

---

## Output requerido

```
PARTE A — VERIFICACIÓN F-PATTERNS:
F-D3.1-01: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria
F-D3.1-02: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria
...
F-D3.1-15: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria

PARTE B — REGRESIONES NUEVAS:
R-D3.1-01 [SEV] archivo:línea — defecto introducido por fix F-D3.1-XX
verificación: <comando ejecutable>
patch mínimo: <diff>
doctrina: <regla rota si aplica>

R-D3.1-02 ...

DECISIÓN BINARIA FINAL:
D3.1-HARDENING: SHIP / DO NOT SHIP — reason: <una oración>
```

---

## Contexto que el prompt lleva

- Repo: `https://github.com/alfredogl1804/el-monstruo` branch `sprint/la-forja-001` HEAD `84c728f`
- Backend D2.5 VERDE (`fe82b1c`) + D3.0 hardening VERDE (`0760095`) — fuera de scope
- Auditoría anterior tuya: ver `bridge/manus_to_perplexity_LA_FORJA_001_D3_1_ADVERSARIAL.md` en el repo (incluye tus 15 F-patterns originales al final)
- Fecha: 16-may-2026 (asume training stale)

Encuentra lo que el agente cansado no audita. Especialmente regresiones introducidas por el celo de los fixes mismos.

---

## Final del prompt

---BEGIN PROMPT---

Eres Perplexity Sonar Reasoning Pro actuando como auditor principal externo binario para Manus La-Forja, hilo E1 ejecutor del sprint LA-FORJA-001.

Repo: https://github.com/alfredogl1804/el-monstruo
Branch: sprint/la-forja-001
HEAD actual: 84c728f
Commit anterior: e125c4c (era el que auditaste tú con 15 F-patterns)

En tu auditoría anterior diste 15 F-patterns con DECISION BINARIA `DO NOT SHIP`. Manus E1 declaró que aplicó 14 fixes y registró 1 (F-D3.1-12) como register-only D6. El delta vive en 2 commits:

- 6646544 hardening(la-forja): D3.1 adversarial fixes Perplexity F-D3.1-01..15
- 84c728f docs(la-forja): bridge Perplexity D3.1 adversarial prompt response

Tienes acceso al repo. Lee directamente:

git show 6646544
git show 84c728f
git diff e125c4c..84c728f

Tu tarea binaria es DOBLE:

PARTE A — Verifica cada uno de los 15 F-patterns. Para cada F-D3.1-NN, responde:
[CERRADO] si el fix realmente cierra el defecto, citando archivo:línea
[ABIERTO] si el código sigue vulnerable, con prueba binaria
[PARCIAL] si el fix mitiga pero deja vector residual

PARTE B — Detecta regresiones nuevas R-D3.1-NN introducidas por los ~700 LOC de fixes. Es probable que el celo de fixear haya metido bugs nuevos. Formato:

R-D3.1-NN [SEV] archivo:línea — defecto introducido por fix F-D3.1-XX
verificación: <comando ejecutable>
patch mínimo: <diff>
doctrina rota: <regla>

Áreas obligatorias a auditar (15 zonas listadas en el bridge file que está en el repo: `bridge/manus_to_perplexity_LA_FORJA_001_D3_1_HARDENING_AUDIT.md`).

Foco especial:
1. ¿La nueva regex de id-match en eslint.config.mjs realmente banea sufijos compuestos? Verifica con un script ejecutable contra UserService, OnboardingFinishHandler, FormatUtil.
2. ¿El guard `finished` en Tour.tsx finalize() es resistente a race condition de doble-click?
3. ¿`useRouter` ahora dentro de Tour.tsx puede crashear en producción si redirectTo tiene caracteres problemáticos?
4. ¿El test de contract sprint_states realmente importa SPRINT_STATES del backend o solo verifica una lista hardcoded?
5. ¿El `force-dynamic` en /onboarding es necesario o es overkill que mata performance?
6. ¿`import pkg from "../../package.json" with { type: "json" }` funciona en Next 16 turbopack production build?

Reglas anti-soft-talk: prohibidos "considera", "podría", "industry standard", "best practices in general", "depending on requirements", "it would be wise to". Si las usas invalido el F.

Hard rules a respetar al revisar:
- LF-1 frontend nunca habla con Supabase directo
- LF-2 versiones validadas magna real-time
- LF-FIVE-DOORS-001 exactamente 5 puertas
- DSC-LF-003 "50 USD" coincide literal con apps/la-forja/api/src/lib/budget.ts
- SPEC §4:130 los 8 estados son inglés exactos
- Brand Engine namespace [la-forja:web_*] + ban Service|Handler|Util|Helper|Manager
- Regla Dura #6 fail-loud envs

Output requerido:

PARTE A — VERIFICACIÓN F-PATTERNS:
F-D3.1-01: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria
...
F-D3.1-15: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria

PARTE B — REGRESIONES NUEVAS:
R-D3.1-NN [SEV] archivo:línea — defecto + verificación ejecutable + patch mínimo + doctrina rota

DECISIÓN BINARIA FINAL:
D3.1-HARDENING: SHIP / DO NOT SHIP — reason: <una oración>

Encuentra lo que el agente cansado no audita. Las regresiones del celo de fixear son tu objetivo principal. Fecha actual: 16-may-2026.

---END PROMPT---
