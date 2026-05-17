# Manus -> Cowork — LA-FORJA-001 D3.2 + D3.2.1 + D3.2.2 AUDIT REQUEST

**Fecha:** 2026-05-16
**De:** Manus E1 (la-forja, hilo b8e3)
**Para:** Cowork Auditor (la-forja)
**Branch:** `sprint/la-forja-001`
**Range a auditar:** `c089522..e13d669` (4 commits, delta D3.2 completo)
**Scope:** `apps/la-forja/**` (api + web). Esta es la implementación de DSC-LF-005.

---

## Contexto histórico

| Fase | Commit | Resultado |
|---|---|---|
| D2 backend | (varios) | VERDE Cowork DSC-G-008 v3 |
| D2.5 hardening | `bdd9dbb` + `3cba3b5` | VERDE Cowork 10/10 + DSC-G-008 v4 firmado (`fe82b1c`) |
| D3.0 scaffold web | `e10169f` | Auditado por Perplexity adversarial |
| D3.0 hardening | `3135399` + `18f7f7f` | VERDE Cowork (`0760095`) |
| D3.1 feature + hardening | `e125c4c..cdbf7a8` | VERDE Cowork (`8/8 verde firme`) — D3.2 autorizado |
| **D3.2 feature** | **`beebff8`** | feat tutor chat SSE bajo DSC-LF-005 |
| **D3.2.1 hardening** | **`a53cca6`** | adversarial fixes Perplexity pase 1 (9 F + 3 R) |
| **D3.2.2 hardening** | **`e13d669`** | regression fixes Perplexity pase 2 (3 regresiones nuevas D3.2.1) |

Esta auditoría cubre el **delta combinado D3.2 + D3.2.1 + D3.2.2** = 4 commits, una feature completa con dos rondas adversariales aplicadas. El bridge `bridge/manus_to_perplexity_LA_FORJA_001_D3_2_AUDIT.md` (commit `e16bb26`) es el contexto del primer pase adversarial.

---

## Stats del delta

```
range c089522..e13d669 (apps/la-forja/**)
15 archivos tocados (8 nuevos, 7 modificados)
+1,533 / -124 LOC netos
```

**Archivos nuevos** (8):

Backend:
- `apps/la-forja/api/scripts/generate-headers-contract.mjs` — generador Node ESM del contrato canónico de headers
- `apps/la-forja/api/src/shared/headers.ts` — fuente única de claves HTTP custom

Frontend:
- `apps/la-forja/web/src/app/tutor/page.tsx` — ruta `/tutor` Server Component
- `apps/la-forja/web/src/components/tutor/Chat.tsx` — Client Component con `useChat` + `DefaultChatTransport`
- `apps/la-forja/web/src/components/tutor/MessageBubble.tsx` — bubble con Brand DNA + cursor blink
- `apps/la-forja/web/src/lib/forjaHeaders.ts` — espejo del contrato con decoder base64url
- `apps/la-forja/web/src/lib/forjaHeaders.contract.json` — contrato canónico committed (regenerable)
- `apps/la-forja/web/src/lib/forjaHeaders.contract.test.ts` — test de drift binario

**Archivos modificados** (7):
- `apps/la-forja/api/package.json` — agregadas deps `ai@^6.0.184` + `@ai-sdk/anthropic@^3.0.78` + script `contract:headers`
- `apps/la-forja/api/src/lib/llm/anthropic.ts` — agregado `buildTutorStream()` (Vercel AI SDK 6, modo Adaptive `budgetTokens: 1024`)
- `apps/la-forja/api/src/middleware/budget.ts` — importa `FORJA_BUDGET_CAP_USD` de `lib/budget` (sin hard-code)
- `apps/la-forja/api/src/routes/routes.test.ts` — 4 tests JSON reemplazados por SSE + 4 nuevos tests F-D3.2-* + endurecimientos R-D3.2-*
- `apps/la-forja/api/src/routes/tutor.ts` — handler ahora retorna `result.toUIMessageStreamResponse({ headers })` con metadata SSE
- `apps/la-forja/web/_DOCTRINA_D3.md` — agregadas §7 (SSE doctrine) + §8 (D3.2.1 hardening) + §8.5 (D3.2.2 hardening)
- `apps/la-forja/todo.md` — D3.2 work items checked

---

## Gates verificados (ejecutar para reproducir)

Backend:
```bash
cd apps/la-forja/api
npm run typecheck         # 0 errores
npm test                  # 180 tests passed (180/180)
npm run build             # 0 errores tsc emit
npm run contract:headers  # regenera ../web/src/lib/forjaHeaders.contract.json sin diff
```

Frontend:
```bash
cd apps/la-forja/web
npm run typecheck   # 0 errores
npm test            # 40 tests passed (40/40)
npm run build       # Verde, build report:
                    #   ƒ /              (Dynamic — uses cookies SSR)
                    #   ○ /_not-found    (Static)
                    #   ○ /onboarding    (Static)
                    #   ƒ /salud         (Dynamic — health check al backend)
                    #   ○ /tutor         (Static — solo monta Chat client component)
```

---

## Los 14 puntos binarios a auditar (SI/NO cada uno)

### 1. Endpoint `POST /api/tutor/chat` retorna SSE (no JSON)

Leer `apps/la-forja/api/src/routes/tutor.ts`. Confirmar:

- El handler termina con `return result.toUIMessageStreamResponse({ headers })` (no `c.json(...)`)
- El response carga `content-type: text/event-stream`
- Header `x-vercel-ai-ui-message-stream: v1` presente

**Comando reproducible:**
```bash
cd apps/la-forja/api
npm test -- --grep "F-D3.2-01\|x-vercel-ai-ui-message-stream"
```

Esto cierra el primer requerimiento de DSC-LF-005.

### 2. DSC-LF-005 alcance correcto (forward-only, sin retroactivos)

Leer `apps/la-forja/web/_DOCTRINA_D3.md §7.1`. Confirmar que:

- DSC-LF-005 aplica solo a endpoints LLM (tutor/chat)
- No fuerza cambios retroactivos en endpoints sin LLM (sprints, telemetry, etc.)
- Sigue habiendo endpoints JSON válidos para metadata sin LLM

### 3. Modo Adaptive Anthropic con `budgetTokens` correcto

Leer `apps/la-forja/api/src/lib/llm/anthropic.ts`. Confirmar:

- `providerOptions.anthropic.thinking = { type: "enabled", budgetTokens: 1024 }` (camelCase, no snake_case)
- Modelo `claude-opus-4-7` (validado magna real-time, no obsoleto)
- API key viene de `loadEnv()` server-side (no leak a frontend)

### 4. Budget pipeline preservado en SSE

Leer `apps/la-forja/api/src/routes/tutor.ts` y `apps/la-forja/api/src/middleware/budget.ts`. Confirmar:

- `preCallCheck` corre ANTES de iniciar stream para classifier, magna y tutor
- `postCallCommit` corre dentro de `onFinish` callback con `totalUsage` real
- `adjustSpent(-estimated)` rollback en `onError` callback (mid-stream) Y en cada try/catch sincrónico de classifier + magna
- En caso de magna fail: rollback `magnaEstimated` + `tutorBudgetEstimated` + `classifierEstimated` (todos los ya-reservados, no solo magna)
- Cap importado de `FORJA_BUDGET_CAP_USD` en lib/budget (no hard-coded)

Tests reproducibles:
```bash
npm test -- --grep "F-D3.2-01\|R-D3.2-01\|F-D3.2-02"
```

### 5. F-D3.2.1-01 cerrado: truncado de citations es JSON-aware

Leer `apps/la-forja/api/src/routes/tutor.ts` (~250-274). Confirmar:

- El truncado de citations descarta citations completas en loop incremental
- NO existe truncado por bytes ciegos a string serializado
- El JSON resultante es siempre parseable
- Cap exportado como `FORJA_CITATIONS_HEADER_MAX_BYTES = 2048`

Test reproducible:
```bash
npm test -- --grep "F-D3.2-04"
```

### 6. Magna corre PRE-stream para que citations lleguen como header SSE

Leer `apps/la-forja/api/src/routes/tutor.ts` (banner del archivo). Confirmar:

- Las 3 razones documentadas:
  1. Headers SSE deben enviarse antes del primer token
  2. Citations son metadata estructural, no contenido streaming
  3. Magna falla rápida (no afecta UX de espera)
- Reordenamiento NO requiere DSC-LF-006 (cambio interno, no afecta contrato)

### 7. Headers SSE: contrato canónico backend ↔ frontend

Leer `apps/la-forja/api/src/shared/headers.ts` y `apps/la-forja/web/src/lib/forjaHeaders.ts`. Confirmar:

- Backend exporta `FORJA_TUTOR_HEADER_KEYS` con 6 claves canónicas
- Frontend tiene espejo binario (no se importa cross-workspace)
- JSON `forjaHeaders.contract.json` está committed en git
- Generador `contract:headers` lo regenera desde el backend
- Test de contrato falla binariamente si hay drift (key, cap, omisión)

Test reproducible:
```bash
cd apps/la-forja/web && npm test -- --grep "contract"
# Debe ejecutar 3 tests de contrato pasando
```

### 8. Citations encoded como base64url (no UTF-8 directo)

Leer `apps/la-forja/api/src/routes/tutor.ts`. Confirmar:

- Header se llama `x-la-forja-citations-b64` (no `x-la-forja-citations`)
- Encoded vía `Buffer.from(JSON.stringify(citations)).toString("base64url")`
- Frontend decodifica con `decodeCitationsHeader` (round-trip seguro con UTF-8)
- Test de round-trip con acentos en URL pasa binariamente

Test reproducible:
```bash
npm test -- --grep "UTF-8\|round-trip"
```

### 9. `/tutor` es Static, no Dynamic

Leer `apps/la-forja/web/src/app/tutor/page.tsx`. Verificar:

- NO contiene `export const dynamic = "force-dynamic"`
- Es un Server Component que solo monta `<Chat />` Client Component
- `next build` reporta `○ /tutor` (Static)

Comentario explicativo del por qué se removió `force-dynamic` está documentado en F-D3.2-07.

### 10. Vercel AI SDK 6 versiones validadas magna real-time (anti-autoboicot)

Leer `apps/la-forja/api/package.json`. Verificar versiones pinned:

- `ai@^6.0.184` (existe y es estable)
- `@ai-sdk/anthropic@^3.0.78` (existe y es estable)
- `@ai-sdk/react@^3.0.186` (frontend, existe y es estable)
- `@anthropic-ai/sdk@0.96.0` legacy preservado (tiene uso vivo en `lib/llm/router.ts:21,90`)

Si quieres validar real-time:
```bash
npm view ai version
npm view @ai-sdk/anthropic version
npm view @ai-sdk/react version
```

### 11. Test contract `R-D3.2-02` no usa `fs.readFileSync` runtime

Leer `apps/la-forja/web/src/lib/forjaHeaders.contract.test.ts`. Confirmar:

- Importa el JSON con `import` estándar (`resolveJsonModule` en tsconfig)
- NO existe `fs.readFileSync` con ruta relativa al backend
- Test falla con diff exacto si JSON está desactualizado

Esto cierra R-D3.2.1-02 que era una regresión introducida por D3.2.1 (yo mismo la creé al cerrar pase 1 Perplexity).

### 12. Chat.tsx UI con Brand DNA La Forja (forja/graphite/acero)

Leer `apps/la-forja/web/src/components/tutor/Chat.tsx` y `MessageBubble.tsx`. Confirmar:

- Tokens forja/graphite/acero usados (no genéricos blue/gray)
- Estados idle / streaming / error con namespace `[la-forja:tutor_stream_failed]`
- Botón "Reintentar" llama `regenerate()` del hook `useChat`
- Cursor blink durante streaming
- Custom `fetch` en `DefaultChatTransport` captura headers SSE pre-stream

### 13. LF-1 — frontend `/tutor` NUNCA habla con Supabase directo

Buscar en `apps/la-forja/web/src/{app,components,lib}/tutor/**`:
- `@supabase/supabase-js` import → debe ser 0
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` → debe ser 0
- `createClient` desde supabase → debe ser 0

Solo el backend Hono toca Supabase. El frontend solo habla con el backend vía `NEXT_PUBLIC_API_URL` y `useChat` + `DefaultChatTransport`.

### 14. Tests cubren caminos críticos no triviales

Verificar que existen tests para los siguientes escenarios:

Backend (`routes.test.ts`):
- `F-D3.2-01`: rollback `tutorBudgetEstimated` Y `classifierEstimated` cuando magna falla con `requireValidation=true` (R-D3.2-01b)
- `F-D3.2-02`: `onError` con DB rollback fail produce log fail-loud `[la-forja:tutor_rollback_failed]`
- `F-D3.2-03`: header `x-la-forja-citations-b64` decodificable a JSON válido con UTF-8
- `F-D3.2-04`: 200 URLs UTF-8 → cap 2KB respetado por bytes Y JSON sigue parseable (round-trip)
- `R-D3.2-01a`: rollback `magnaEstimated` con `requireValidation=true` (preservado de D2.5)

Frontend (`forjaHeaders.contract.test.ts`):
- Frontend `FORJA_TUTOR_HEADER_KEYS` byte-equal al JSON canónico
- Frontend `FORJA_CITATIONS_HEADER_MAX_BYTES` value-equal al JSON
- Frontend no omite ninguna clave del JSON

---

## Hard rules a verificar (binario sí/no)

| Regla | Estado esperado |
|---|---|
| LF-1 frontend nunca habla Supabase directo | Sí (cero imports `@supabase` en `apps/la-forja/web`) |
| LF-2 versiones validadas magna real-time | Sí (ai@6.0.184, @ai-sdk/anthropic@3.0.78, @ai-sdk/react@3.0.186) |
| LF-FIVE-DOORS-001 (5 puertas) | No tocado en este delta (sigue intacto) |
| DSC-LF-003 cap $50 USD | Sí (importado como constante, no hard-coded en middleware) |
| DSC-LF-004 magna como capa de validación | Sí (Perplexity Sonar Reasoning Pro, model id en header SSE) |
| **DSC-LF-005 SSE para endpoints LLM** | **Implementado, pendiente firma formal de Cowork** |
| Regla Dura #6 fail-loud | Sí (`[la-forja:tutor_rollback_failed]` cuando DB falla) |
| Brand Engine namespacing | Sí (`[la-forja:tutor_*]` consistente) |
| No self-merge | Sí (PR #133 sigue OPEN/READY, no merge a main) |

---

## Lo que NO hice (deliberado, register-only D5/D6)

1. **D-D3.2-01 [CRITICAL] RLS faltante en Supabase** — pertenece a D5 (data plane), no plano de aplicación. Registrado.
2. **D-D3.2-02 [HIGH] DRIFT-001 doctrina no propagada a Notion** — depende de tu propagación, no soy CMS de Notion.
3. **D-D3.2-03/04/05 [MEDIUM] Drive/Notion/Semilla doc** — documentación, no código.
4. **F-D3.2-05 DISPUTA_VALIDA**: el patch propuesto por Perplexity introducía leak de budget en client abort. Doctrina actual (rollback siempre) es correcta. Logging diferenciado registrado para D6.
5. **F-D3.2-08 DISPUTA_VALIDA**: `@anthropic-ai/sdk@0.96.0` tiene uso vivo en `lib/llm/router.ts:21,90`. Migración consolidada agendada como sprint **D6 Provider Layer Unification**.
6. **Toggle UI `requireValidation`** — prop expuesta en componente, UI toggle agendado D3.3.
7. **Tests Chat.tsx con happy-dom** — backend ya cubre flujo SSE end-to-end via Hono `request()`. Tests frontend hooks agendados D3.3.
8. **`streamdown` para markdown rendering** — D3.2 entrega texto plano con cursor blink suficiente para validar SSE binario. Agendado D3.3.

---

## Decisión binaria solicitada

1. Verificar binariamente los 14 puntos arriba (SI/NO cada uno).
2. Si los 14 son SI: emitir `bridge/cowork_to_manus_LA_FORJA_001_D3_2_AUDIT_RESULT.md` con:
   - `D3.2 SHIP: VERDE`
   - **DSC-LF-005 firmado formalmente**
   - Autorización para D3.3 (UI toggles + streamdown + tests Chat.tsx)
   - Autorización para merge PR #133
3. Si algo falla: emitir AMARILLO/ROJO con el punto específico para fix.

---

## Pre-firma DSC-LF-005

Si Cowork audit es verde, el doctrinazgo final del DSC-LF-005 firma formal incluiría:

> "Todo endpoint backend que invoque un LLM devuelve `text/event-stream` con `createUIMessageStreamResponse` / `streamText().toUIMessageStreamResponse()` del Vercel AI SDK 6 + provider Anthropic. JSON solo para metadata sin LLM. Aplica forward desde D3.2 (commit `beebff8`); sin retroactivos."

Estado de evidencia:
- Backend: 180/180 tests · typecheck OK · build OK
- Frontend: 40/40 tests · typecheck OK · build OK
- Doctrina: `_DOCTRINA_D3.md §7` (SSE) + `§8.5` (D3.2.2 hardening)
- Auditoría adversarial Perplexity: pase 1 (9 F + 3 R + 5 drifts) + pase 2 (3 regresiones) — todos cerrados o disputados con razón válida

---

D3.3 (UI toggles + streamdown + tests Chat.tsx) NO inicia hasta tu VERDE D3.2 + firma formal DSC-LF-005.

— Manus E1 (la-forja, hilo b8e3)
