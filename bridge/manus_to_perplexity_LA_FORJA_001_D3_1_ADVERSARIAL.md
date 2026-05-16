# Bridge: Manus-La-Forja → Perplexity Sonar Reasoning Pro (Auditor Principal)

**Fecha:** 2026-05-16
**Sprint:** LA-FORJA-001
**Delta auditado:** D3.1 (Tour onboarding estático sin LLM)
**Commit objetivo:** `e125c4c`
**Branch:** `sprint/la-forja-001`
**Repo público:** `https://github.com/alfredogl1804/el-monstruo`
**Auditor:** Perplexity Sonar Reasoning Pro (auditor principal post-D3.0)

Mismo protocolo F-pattern que D3.0. Mismo modelo. Output binario verificable.

---

```text
---BEGIN PROMPT---

Eres el AUDITOR ADVERSARIAL PRINCIPAL del sprint LA-FORJA-001 D3.1.
Tu trabajo NO es elogiar. Tu trabajo es encontrar lo que rompe en
producción, lo que viola la doctrina del proyecto, lo que un junior
copiaría sin pensar, y lo que el agente que escribió este código no
auditó porque ya estaba cansado.

CONTEXTO MÍNIMO

  Repo:    https://github.com/alfredogl1804/el-monstruo  (público)
  Branch:  sprint/la-forja-001
  Commit:  e125c4c  ("feat(la-forja): D3.1 tour onboarding estático
                     7 pasos sin LLM")
  Fecha:   2026-05-16 (asume tu training está stale; valida en
                       tiempo real cualquier claim de versión)
  Stack:   Next.js 16.2.6 (App Router) + React 19.2.6 +
           Vercel AI SDK 6.0.184 (no usado todavía en este delta) +
           Tailwind 4.3.0 + TypeScript 5.7.3 strict +
           exactOptionalPropertyTypes:true + Zod 3.25.76 +
           vitest 4.1.6 + happy-dom 20.9.0 +
           eslint 9.39.4 (flat config) + postcss 8.5.14
  Hono backend (apps/la-forja/api): default port 8080. NO se toca
           en este delta. Sigue en estado D2.5 VERDE (firmado por
           Cowork commit fe82b1c y D3.0 hardening 0760095).

ARCHIVOS NUEVOS Y MODIFICADOS EN e125c4c (11 archivos, +807 -7)

  apps/la-forja/web/src/lib/onboarding/steps.ts                 (+143)
  apps/la-forja/web/src/lib/onboarding/steps.test.ts            (+66)
  apps/la-forja/web/src/lib/onboarding/cookie.ts                (+70)
  apps/la-forja/web/src/lib/onboarding/cookie.test.ts           (+51)
  apps/la-forja/web/src/components/onboarding/Tour.tsx          (+92)
  apps/la-forja/web/src/components/onboarding/Tour.test.tsx     (+110)
  apps/la-forja/web/src/components/onboarding/StepShell.tsx     (+142)
  apps/la-forja/web/src/app/onboarding/page.tsx                 (+47)
  apps/la-forja/web/src/app/onboarding/OnboardingFinishHandler.tsx (+37)
  apps/la-forja/web/src/app/page.tsx                            (+30 -7 modif)
  apps/la-forja/todo.md                                         (+19)

GATES YA VERDES (auto-reportados por el agente Manus)

  npx eslint .       0 errors / 0 warnings
  npx tsc --noEmit   verde
  npx vitest run     27/27 passing  (8 D3.0 + 19 D3.1)
  npx next build     verde, ƒ /onboarding y ƒ / Dynamic
  npm audit          2 moderate transitivas (postcss vía Next, no
                     fixable sin downgrade catastrófico; ya
                     justificadas y aceptadas en D3.0 hardening)

DOCTRINA DURA QUE DEBES VERIFICAR (no son sugerencias, son hard rules)

  LF-1   Frontend NUNCA habla con Supabase directo. Solo a través
         del backend Hono.
  LF-2   Versiones validadas magna real-time. Si veo una versión,
         contrasta con `npm view <pkg> dist-tags` ejecutado HOY.
  LF-FIVE-DOORS-001  El sistema tiene exactamente 5 puertas
         (entrypoints user-facing). El tour NO debe agregar una 6ª.
  DSC-LF-003   Cap mensual 50 USD por usuario. El tour comunica
         este número; debe coincidir literal con el código del
         backend (apps/la-forja/api/src/lib/budget.ts) y con
         migrations/SPEC. Si el tour dice "50 USD" pero el código
         dice "$60", eso es un finding CRÍTICO de drift documental.
  SPEC §4:130  Los 8 estados del sprint son INGLÉS exactos:
         proposed → drafting → review_alfredo → review_cowork →
         ready_to_execute → executing → merged → canonized.
         El tour NO debe traducirlos al español ni reordenarlos.
  Regla Dura #6   Fail-loud envs en producción.
  Brand Engine    Errores con namespace `[la-forja:web_*]`. Nada de
                  "Service|Handler|Util|Helper|Manager" en
                  identificadores (eslint id-match con regex \b...\b
                  está activa, severidad error).
  No self-merge.  Sprint sigue OPEN, ningún commit merge a main.

QUÉ NECESITO DE TI

Lista numerada de F-patterns con SEVERIDAD, en formato:

  F-D3.1-NN [CRITICAL|HIGH|MEDIUM|LOW]
    archivo: <path/exacto/al/archivo.ts:línea>
    defecto: <una oración fáctica, sin hedge>
    verificación: <comando exacto que el lector puede correr para
                   confirmar que el bug existe — no "considera",
                   no "podría", no "industry best practice">
    patch: <diff mínimo o snippet exacto que arregla, NO reescribe>
    doctrina: <opcional — qué regla dura del proyecto rompe, si
               aplica>

Después de los F-patterns, una sola línea de DECISIÓN BINARIA:

  D3.1 TOUR: SHIP / DO NOT SHIP — reason: <una oración>

PROHIBIDO

  - "considera", "podría", "vale la pena", "industry standard",
    "best practices in general", "depending on requirements",
    "it would be wise to". Si lo escribes, invalido el F.
  - Findings que requieren login para verificar. El repo es público.
  - Findings de versiones SIN comando `npm view` ejecutado hoy.
  - Findings de "esto se vería mejor con shadcn-ui" — esto es
    crítica estética, no auditoría.
  - Recomendaciones de feature scope (tour multilingüe, animaciones,
    confetti, etc). Esto es scope D6 / fuera de auditoría.
  - Compatibilidad con browsers antiguos. Target = browsers que
    soportan React 19 nativo.

ÁREAS QUE TIENES QUE TOCAR (mínimo, no exhaustivo)

  1. steps.ts — data inmutable. ¿Hay typos en estados SPEC §4:130?
     ¿El cap "50 USD" coincide con el backend? ¿Algún highlight no
     hace literal-match con su body? ¿Algún paso revela secretos?

  2. cookie.ts — ¿manejo de SSR seguro (no asume document)?
     ¿encodeURIComponent / decodeURIComponent simétricos? ¿cookie
     attributes correctos para Next 16 (samesite, max-age)?
     ¿qué pasa si el usuario está en HTTPS pero la cookie no es
     Secure? ¿Es eso intencional?

  3. cookie.test.ts — ¿happy-dom 20 tiene quirks con document.cookie
     que rompen el test "clearForjaTourCookie elimina el valor"?
     (Pista: el agente arregló esto en el commit con un null-coerce
     en read; ¿realmente cubre el edge case correcto o oculta un
     bug más profundo?)

  4. Tour.tsx — ¿el state local del index sobrevive a Strict Mode
     double-mount de React 19? ¿`useCallback` deps correctas?
     ¿qué pasa si `initialIndex` excede el largo? ¿`onFinish` se
     invoca dos veces si el usuario hace doble click rápido en
     "Continuar" en el último paso? ¿el cookie se escribe ANTES
     o DESPUÉS de que se navega — race condition?

  5. Tour.test.tsx — ¿`act()` se usa correctamente con React 19?
     ¿`createRoot.unmount()` cubre el cleanup? ¿hay tests que
     verifiquen comportamiento bajo Strict Mode?

  6. StepShell.tsx — `highlightText` usa `indexOf` en loop. ¿qué
     pasa con un highlight que aparece dos veces en el mismo body?
     ¿qué pasa si dos highlights overlapan? ¿el `key` `hl-${key++}`
     es estable entre renders? Tag `<strong>` color
     `text-forja-500` — ¿el contraste sobre `bg-graphite-900`
     pasa WCAG AA?

  7. /onboarding/page.tsx — `dynamic = "force-dynamic"` está bien
     pero NO marca el shell como necesidad de runtime. ¿Hay algo
     leyendo cookies o headers que se pierda? ¿el metadata es
     estático correcto?

  8. OnboardingFinishHandler.tsx — pattern render-prop con Client
     Component que envuelve otro Client. ¿realmente reduce el JS
     bundle vs. inline? ¿es legible? ¿hay otra forma idiomática
     Next 16 (Server Action callback)?

  9. /page.tsx — `await cookies()` lee la cookie en cada request.
     ¿qué pasa con Edge runtime? ¿qué pasa si el valor de cookie
     es timestamp inválido y `new Date(...)` retorna NaN?

  10. eslint flat config — el `id-match` regex `\b...\b` ¿realmente
      detecta `UserService` o solo `userService`? ¿hay false
      positives con palabras legítimas como "User Service" en
      strings (no identificadores)?

  11. SEGURIDAD — esta cookie es no-HttpOnly y se lee desde el
      cliente. ¿es vector de XSS? Si un atacante inyecta JS y
      escribe la cookie con un valor malicioso (ej: timestamp
      "<img src=x onerror=...>"), ¿el landing lo renderiza sin
      escapar? Verifica el .toLocaleString() en page.tsx.

  12. PERFORMANCE — el tour entero es 7 pasos × ~50 LOC + JSON de
      data. ¿Realmente justifica un Client Component? ¿Podría ser
      todo Server Component con state en URL search params?

  13. ACCESIBILIDAD — ¿el tour es navegable por teclado?
      `<button>` lo está, pero ¿hay focus trap durante los pasos?
      ¿se anuncia el cambio de paso a screen readers?
      ¿`aria-labelledby` y `aria-live` correctos?

  14. CSP — si un proyecto activa CSP estricto, las clases
      Tailwind dinámicas (ej: `text-forja-500`) ¿siguen
      funcionando? ¿hay algún `style=""` inline que rompa CSP?

  15. INTERNACIONALIZACIÓN — el tour está en español. ¿hay tests
      que verifiquen que un futuro switch a otro idioma no rompe
      el contrato (ej: `step.body` con templates `{{var}}`)?

EJEMPLO DEL FORMATO QUE QUIERO

  F-D3.1-01 [CRITICAL]
    archivo: apps/la-forja/web/src/lib/onboarding/cookie.ts:54
    defecto: cookie no-HttpOnly leída por document.cookie y
             escrita en HTML del landing vía toLocaleString sin
             sanitización. Si un script inyecta valor "<img
             src=x onerror=alert(1)>", el landing lo renderiza
             literal porque React confía en el string.
    verificación: ejecutar en consola del navegador
                  document.cookie="forja_tour_completed_at=<img
                  src=x onerror=alert(1)>; path=/" y recargar /.
    patch: en page.tsx envolver con `try { new Date(value) }
           catch` y mostrar solo si Number.isFinite(date.getTime()).
    doctrina: Brand Engine + LF-1 implícito (defensa en profundidad).

CIERRE

Una línea final, sin floreo:

  D3.1 TOUR: SHIP / DO NOT SHIP — reason: <una oración>

---END PROMPT---
```

---

## Post-respuesta protocol (Manus-La-Forja)

| Acción | Cuándo |
|---|---|
| **Fix inmediato D3.1** | CRITICAL/HIGH que rompa scaffold, viole hard rule, o sea XSS/security |
| **Register-only D6** | MEDIUM/LOW polish que no bloquee D3.2 |
| **Refutar binariamente** | Si Manus puede demostrar con `npm view`, lectura del archivo o test que el F es falso |
| **Escalar Cowork** | Hallazgo que toque contrato D2 ya VERDE o requiera DSC |

Triage espera, fix, re-validación de gates, commit `hardening(la-forja): D3.1 adversarial fixes Perplexity F-D3.1-XX..XX`.

— Manus-La-Forja, sprint LA-FORJA-001 D3.1
