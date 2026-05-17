# Bridge — Manus La-Forja → Perplexity Sonar Reasoning Pro
## Tarea: D3.2 adversarial audit (commit `beebff8`, delta `c089522..beebff8`)

**Fecha:** 16-may-2026 CST
**Auditor:** Perplexity Sonar Reasoning Pro (auditor principal externo)
**Auditado:** Manus La-Forja (Hilo E1, ejecutor sprint LA-FORJA-001)
**Repo:** `https://github.com/alfredogl1804/el-monstruo`
**Branch:** `sprint/la-forja-001`
**Acceso:** Perplexity tiene acceso al repo público vía Sonar.

---

## Contexto previo (binario)

Sprint LA-FORJA-001 entró a fase D3.2 bajo doctrina **DSC-LF-005** (firmada por Cowork 16-may-2026):

> "Todo endpoint backend que invoque un LLM devuelve `text/event-stream` con `createUIMessageStreamResponse` del Vercel AI SDK 6. JSON solo para metadata sin LLM. Aplica forward desde D3.2; sin retroactivos."

Manus E1 entregó la migración del endpoint `POST /api/tutor/chat` de respuesta JSON síncrona a streaming SSE en **un único commit**:

- `beebff8` `feat(la-forja): D3.2 tutor chat SSE bajo DSC-LF-005 (Vercel AI SDK 6 + Anthropic Adaptive)`

Diff stats reportados (`git diff --stat c089522..beebff8`):

```
 apps/la-forja/api/package.json                     |   2 +
 apps/la-forja/api/src/lib/llm/anthropic.ts         | 124 ++++++++++-
 apps/la-forja/api/src/routes/routes.test.ts        | 186 +++++++++++---
 apps/la-forja/api/src/routes/tutor.ts              | 156 ++++++------
 apps/la-forja/todo.md                              |  46 ++++
 apps/la-forja/web/_DOCTRINA_D3.md                  |  80 ++++++
 apps/la-forja/web/src/app/tutor/page.tsx           |  41 ++++
 apps/la-forja/web/src/components/tutor/Chat.tsx    | 272 +++++++++++++++++++++
 apps/la-forja/web/src/components/tutor/MessageBubble.tsx |  75 +++++++
 9 files changed, 866 insertions(+), 116 deletions(-)
```

Gates locales reportados por Manus:
- Backend: `npm test` → 176/176 passing en 478ms · `npx tsc --noEmit` 0 errores · `npm run build` verde (dist/ generado)
- Frontend: `npm test` → 37/37 passing · `npx tsc --noEmit` 0 errores · `npx next build` verde con `/tutor` registrada como `ƒ` (server-rendered on demand)

Stack confirmado: `ai@6.0.184` + `@ai-sdk/anthropic@3.0.78` (backend) + `@ai-sdk/react@3.0.186` + `next@16.2.6` (frontend).

---

## Tu tarea binaria

Lee el delta directamente del repo:

```
git show beebff8
git diff c089522..beebff8
```

O ruta-por-ruta los archivos modificados/agregados:

```
apps/la-forja/api/package.json
apps/la-forja/api/src/lib/llm/anthropic.ts
apps/la-forja/api/src/routes/tutor.ts
apps/la-forja/api/src/routes/routes.test.ts
apps/la-forja/web/_DOCTRINA_D3.md          (§7 nueva)
apps/la-forja/web/src/app/tutor/page.tsx           (NUEVO)
apps/la-forja/web/src/components/tutor/Chat.tsx    (NUEVO)
apps/la-forja/web/src/components/tutor/MessageBubble.tsx  (NUEVO)
apps/la-forja/todo.md
```

Tu trabajo es **doble**:

### Tarea A — Verificación binaria de las 7 promesas operativas D3.2

Manus declara 7 invariantes operativos en el commit. Para cada uno responde **binario**:

- `[CERRADO]` si la implementación cumple binariamente
- `[ABIERTO]` si Manus dijo que cumplió pero el código sigue violando
- `[PARCIAL]` si cumple en el happy path pero deja vector residual

Cada respuesta debe citar **archivo:línea** y la línea exacta que confirma o refuta.

Las 7 promesas son:

1. **P-D3.2-01 SSE migration:** `tutor.ts` retorna `Response` SSE (`text/event-stream` + UI Message Stream protocol v1) en lugar de `c.json(...)`.
2. **P-D3.2-02 Adaptive thinking:** el stream se construye con `providerOptions.anthropic.thinking = { type: "enabled", budgetTokens: 1024 }` (modo Adaptive obligatorio §2.4 SPEC).
3. **P-D3.2-03 preCallCheck pre-stream:** `preCallCheck` para classifier + magna_validation + tutor (vía middleware) corre ANTES de iniciar el stream.
4. **P-D3.2-04 postCallCommit en onFinish:** `postCallCommit(tutor)` se ejecuta dentro de `onFinish` con tokens reales (`totalUsage.inputTokens/outputTokens`), no estimados.
5. **P-D3.2-05 rollback en onError:** `adjustSpent(-estimated)` se ejecuta dentro de `onError` del stream cuando el LLM falla mid-stream.
6. **P-D3.2-06 magna PRE-stream:** `invokeMagnaValidation` corre ANTES del stream (no después) para que las citations viajen como header `x-la-forja-citations`.
7. **P-D3.2-07 namespace errores:** los errores del endpoint preservan namespace `[la-forja:tutor_*]` y los del frontend usan `[la-forja:tutor_stream_failed]`.

### Tarea B — Detección de F-patterns adversariales y R-patterns

Es **muy probable** que al hacer una migración de 866 LOC con cambio de paradigma (sync → streaming) Manus haya introducido bugs nuevos. Busca **F-patterns adversariales** (defectos en el código entregado) y **R-patterns** (regresiones contra D2.6 que el cambio puede haber roto sin testear).

Formato:

```
F-D3.2-NN [SEV] archivo:línea — defecto binario observado
verificación: <comando node/grep/curl ejecutable>
patch mínimo: <diff>
doctrina rota: <regla específica>
```

```
R-D3.2-NN [SEV] archivo:línea — regresión binaria contra comportamiento D2.6
verificación: <comando ejecutable>
patch mínimo: <diff>
```

---

## Áreas obligatorias a auditar

### 1. Budget pipeline mid-stream (corazón de DSC-LF-005)

Revisa `apps/la-forja/api/src/lib/llm/anthropic.ts` función `buildTutorStream()` y `apps/la-forja/api/src/routes/tutor.ts` callbacks `onFinish` / `onError`. Auditá binariamente:

- **Race condition `onFinish` async:** el `Response` SSE se devuelve al cliente ANTES de que `onFinish` termine. Si `onFinish` falla por error de DB en `postCallCommit`, ¿el cap se enforce en el siguiente turn vía `preCallCheck`? ¿O queda spending no contabilizado?
- **`onError` sin `await`:** si `adjustSpent(-estimated)` lanza promesa rejected dentro de `onError`, ¿se traga silenciosamente? ¿Hay logging que lo capture?
- **Doble rollback:** ¿qué pasa si `onError` Y un catch sincrónico afuera del stream ambos disparan? ¿`adjustSpent` se llama 2x con valor negativo? Posible double-credit.
- **`onFinish` con tokens=0:** si Claude devuelve un finish prematuro (e.g. content filter), ¿`totalUsage.inputTokens`/`outputTokens` puede ser 0? ¿`postCallCommit` con `realCostUsd=0` rompe budget tracking?
- **Stream cancelado por cliente:** si el cliente cierra la conexión SSE mid-stream (abort, navega, cierra tab), ¿`onFinish` se dispara igual? ¿O `onError`? ¿O ninguno y el budget queda en estado intermedio?

### 2. Headers SSE custom y reordenamiento magna PRE-stream

Revisa `apps/la-forja/api/src/routes/tutor.ts` orden de operaciones y la construcción de headers para `toUIMessageStreamResponse({ headers })`. Auditá:

- **Magna PRE-stream:** Manus movió `invokeMagnaValidation` ANTES del stream para que las citations viajen como header. La justificación binaria está en el banner del archivo (3 razones). ¿Las 3 razones aguantan?
  1. "El cliente necesita citations en headers" — ¿es realmente imposible inyectar citations como chunk SSE custom? Vercel AI SDK 6 tiene `writer.write({ type: "data-citations", data: [...] })`.
  2. "La validación magna NO depende del output del tutor" — pero entonces, ¿por qué se llamaba magna_validation y no magna_pretopic_validation? El nombre miente sobre el contrato.
  3. "DSC-LF-004 no fija el orden" — pero al reordenar, **se cambia el contrato observable** del endpoint. ¿Eso requiere DSC-LF-006 explícito?
- **Headers ASCII-only:** `x-la-forja-citations` se serializa con `JSON.stringify(citations)`. Si una citation contiene caracteres UTF-8 (acentos, emojis, comillas curly), ¿el header se rompe? HTTP/1.1 RFC 7230 sólo permite ASCII en headers; navegadores interpretan UTF-8 inconsistentemente.
- **Header size limit:** muchas citations (Sonar puede devolver 10+) pueden hacer que el header total exceda el límite default de Hono/Cloud Run (8KB por default). Si rebasa, ¿el server retorna 502 o trunca?
- **Header `x-la-forja-confidence`:** se serializa con `String(number)`. Si confidence es `0.9999999999999999` (float drift), ¿el cliente lo parsea como exactamente 1.0?

### 3. Reordenamiento magna PRE-stream — implicación de cap

DSC-LF-003 fija budget cap $50/mes/user. Antes de D3.2, el orden era:
```
classifier → tutor → magna (post-validation, opt-in)
```
Después de D3.2, el orden es:
```
classifier → magna (pre-validation, opt-in) → tutor stream
```

Auditá:

- **Si `requireValidation=true` y magna falla:** ¿se ejecuta el tutor igual? ¿O se aborta sin haber gastado tutor? ¿Cambió el comportamiento observable para el frontend?
- **Si `requireValidation=true` y `preCallCheck(magna)` falla por cap:** ¿el endpoint retorna 429 sin gastar nada? ¿O ya cobró el classifier?
- **Reservación encadenada:** ¿`reserveSpent` se llama en orden classifier → magna → tutor? Si el flujo aborta en magna, ¿`adjustSpent(-classifier)` se ejecuta? Si no, hay leak de budget reservado.

### 4. Mock `buildTutorStream` en tests — cobertura adversarial

Revisa `apps/la-forja/api/src/routes/routes.test.ts`. Manus declara que el mock `buildTutorStream` exporta un builder que retorna `{ toUIMessageStreamResponse(init) }`. Auditá:

- **Cobertura del mock:** ¿el mock realmente ejercita el path de `onFinish`? ¿O solo simula que retorna un Response sin llamar callbacks?
- **Test H-2 D2.5 hardening:** "si el stream del tutor falla mid-stream, adjustSpent ejecuta rollback vía onError". ¿Cómo dispara el test el `onError` del mock? ¿Es realista vs el comportamiento real del SDK?
- **Test SSE content-type:** ¿el test asserta literal `text/event-stream` o usa regex que también acepta `text/plain`?
- **Test header `x-vercel-ai-ui-message-stream`:** ¿el mock setea ese header o el test asume que el SDK real lo agrega? Si el test no asserta el header desde el mock, el assertion es decorativo.
- **Test citations:** ¿el test asserta `headers.get('x-la-forja-citations')` con `JSON.parse` de array no vacío? ¿O sólo verifica que el header existe?

### 5. Frontend `useChat` v3 + `DefaultChatTransport`

Revisa `apps/la-forja/web/src/components/tutor/Chat.tsx`. Auditá:

- **`input` legacy:** Manus declara que `useChat` v3 removió `input` / `handleInputChange` y ahora usa `useState` local. ¿Es cierto? ¿`@ai-sdk/react@3.0.186` realmente eliminó esos exports? Si los removió, ¿hay alguna forma de migración documentada que Manus no siguió?
- **Custom `fetch` para capturar headers:** el cliente usa un custom `fetch` que lee headers SSE pre-stream para hidratar la barra de metadata. Auditá:
  - ¿El custom `fetch` se ejecuta en server-side rendering? Si Next.js intenta SSR, `Response.headers` puede no estar disponible.
  - ¿Qué pasa si el primer chunk llega antes de que el custom `fetch` lea los headers? Race condition.
  - Si el server retorna 4xx/5xx, ¿el custom `fetch` lee headers de error o sólo del happy path?
- **`useEffect` deps stability:** el `transport` se construye con `useMemo` o `useState`. ¿Las deps son estables? Si cambian en cada render, hay reconnect loop.
- **`stop()` y `regenerate()`:** los handlers pasan a botones del UI. ¿Llaman al backend correctamente cuando el user cierra el stream? ¿El backend recibe el abort signal?

### 6. `MessageBubble.tsx` cursor blink y streaming visibility

Revisa `apps/la-forja/web/src/components/tutor/MessageBubble.tsx`. Auditá:

- **Cursor blink:** Manus declara cursor blink durante streaming. ¿Cómo distingue mensaje en streaming vs mensaje completado? ¿Hay race condition donde el cursor sigue parpadeando después de `onFinish`?
- **Whitespace de tokens:** los tokens de Claude pueden venir con leading/trailing whitespace. ¿`MessageBubble` los renderiza con `<pre>` o `<div>`? Markdown? Si es `<div>` plano, los newlines del LLM se colapsan.
- **XSS:** si el LLM responde con HTML literal (e.g., `<script>alert(1)</script>`), ¿React escapa correctamente o el componente usa `dangerouslySetInnerHTML`?

### 7. `/tutor` page Server Component + `force-dynamic`

Revisa `apps/la-forja/web/src/app/tutor/page.tsx`. Auditá:

- **`force-dynamic` necesidad:** la página solo monta el `<Chat />` Client Component. ¿Realmente necesita `force-dynamic`? Misma observación que R-D3.1-04 del bridge anterior — copiada a otro file.
- **No auth gate:** el endpoint del backend usa stub auth (`x-user-id` header). Frontend `/tutor` no tiene gate. En producción este endpoint quedaría expuesto sin auth real hasta D4. ¿El bridge debe documentar este riesgo?
- **`NEXT_PUBLIC_API_URL` SSR-time:** la prop `apiUrl` se lee server-side. Si la env var no está seteada en build time, ¿el build crashea con fail-loud? Misma doctrina que F-D3.1-14.

### 8. `_DOCTRINA_D3.md §7` honestidad documental

Revisa `apps/la-forja/web/_DOCTRINA_D3.md` §7 nueva. Auditá:

- **Tabla §7.5 honestidad:** "Los 4 tests D2.5 hardening siguen pasando con la misma intención". ¿Es cierto binariamente? ¿O algún test cambió su contrato silenciosamente?
- **§7.4 razón #2:** "La validación magna NO depende del output del tutor". Si esto es cierto, ¿por qué el backend D2.6 la corría DESPUÉS del tutor? Inconsistencia histórica no documentada.
- **§7.6 firma DSC-LF-005:** Manus dice "implementado pero NO firmado todavía". El bridge audit es uno de los 3 gates. Confirma que tu output binario es input válido para la firma.

### 9. Drift backend ↔ frontend (regresión D3.1 que se repite)

En el bridge D3.1-HARDENING, R-D3.1-03 detectó que el contract test entre `apps/la-forja/web` y `apps/la-forja/api` era tautológico. Auditá si el mismo patrón se repite en D3.2:

- **Headers SSE custom:** el frontend espera `x-la-forja-{intent,confidence,model,citations,validation-model}`. ¿Hay un test que importe la lista canónica del backend y la compare contra lo que el frontend asume? Si no, hay drift posible.
- **Modelo del tutor:** el header `x-la-forja-model` retorna `claude-opus-4-7` literal. ¿Hay un test que lo compare contra `MISSION_TO_MODEL` del router? Si el backend cambia el modelo y el frontend no, ¿algún gate rompe?

### 10. Dependencia adicional — co-existencia `@anthropic-ai/sdk@0.96.0` legacy

Revisa `apps/la-forja/api/package.json`. Manus declara que `@anthropic-ai/sdk@0.96.0` legacy queda como dependencia para `invokeTutor()` JSON exportado para "compat de tests". Auditá:

- **¿Realmente se usa?** Si ningún test consume `invokeTutor()` JSON, ¿por qué está exportado? Bloat de dependencia + atack surface.
- **Versión del SDK legacy vs SDK moderno:** ¿`@anthropic-ai/sdk@0.96.0` tiene CVEs publicados desde su release? `npm audit --production`.
- **Doctrina Obj #3 mínima complejidad:** mantener 2 SDKs Anthropic en paralelo viola el objetivo. ¿El commit message lo justifica binariamente o es legacy abandonado?

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

- **LF-1** frontend NUNCA habla con Supabase directo (verificar que `Chat.tsx` solo habla con el backend)
- **LF-2** versiones validadas magna real-time (`ai@6.0.184`, `@ai-sdk/anthropic@3.0.78`, `@ai-sdk/react@3.0.186`)
- **LF-FIVE-DOORS-001** las 5 puertas no se modificaron (sigue siendo `length === 5`)
- **DSC-LF-003** el cap de $50/mes/user sigue enforced (verificar que el reordenamiento magna no rompe `preCallCheck`)
- **DSC-LF-004** Sonar Reasoning Pro como capa magna (verificar que no se cambió de modelo)
- **DSC-LF-005** todo endpoint con LLM retorna SSE (verificar que `tutor.ts` lo cumple binariamente)
- **Regla Dura #6** fail-loud envs (`NEXT_PUBLIC_API_URL`, `ANTHROPIC_API_KEY`)
- **Regla Dura #4 Brand Engine** namespace `[la-forja:*]` + ban `Service|Handler|Util|Helper|Manager` (verificar archivos nuevos)
- **No self-merge** PR #133 sigue OPEN

---

## Output requerido

```
PARTE A — VERIFICACIÓN PROMESAS OPERATIVAS D3.2:
P-D3.2-01: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria
P-D3.2-02: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria
P-D3.2-03: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria
P-D3.2-04: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria
P-D3.2-05: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria
P-D3.2-06: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria
P-D3.2-07: [CERRADO|ABIERTO|PARCIAL] — archivo:línea — evidencia binaria

PARTE B — F-PATTERNS ADVERSARIALES + R-PATTERNS:
F-D3.2-01 [SEV] archivo:línea — defecto binario
verificación: <comando ejecutable>
patch mínimo: <diff>
doctrina rota: <regla específica>

R-D3.2-01 [SEV] archivo:línea — regresión binaria
verificación: <comando ejecutable>
patch mínimo: <diff>

DECISIÓN BINARIA FINAL:
[SHIP / DO NOT SHIP] — reason: <X promesas CERRADAS, Y PARCIALES, Z F-patterns SEV-N, criterio que cierra la decisión>
```

---

## Reglas para Manus E1 (post-output Perplexity)

Cuando reciba este output:

1. Cada `[ABIERTO]` o `[PARCIAL]` se procesa binariamente, no se descarta.
2. Cada `F-D3.2-NN` se aplica con patch mínimo o se marca como register-only con justificación.
3. Cada `R-D3.2-NN` se trata como bug de regresión y se aplica fix antes de cerrar D3.2.
4. El delta de fixes se empuja como commit `hardening(la-forja): D3.2 adversarial fixes Perplexity F-D3.2-* + R-D3.2-*`.
5. Se solicita segundo pase Perplexity sobre el delta del hardening (regresión audit).
6. DSC-LF-005 NO se firma hasta que el segundo pase + bridge audit Cowork D3.2 cierren.

---

**Manus E1 está listo para procesar tu output binariamente.**
