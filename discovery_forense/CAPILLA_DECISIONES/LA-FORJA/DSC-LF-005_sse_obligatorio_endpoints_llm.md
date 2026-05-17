---
id: DSC-LF-005
proyecto: LA-FORJA
tipo: contrato_arquitectonico
titulo: "Todo endpoint backend de La Forja que invoque un LLM devuelve text/event-stream con createUIMessageStreamResponse / streamText().toUIMessageStreamResponse() del Vercel AI SDK 6 + provider Anthropic. JSON solo para metadata sin LLM. Aplica forward desde D3.2 (commit beebff8); sin retroactivos"
estado: firme (firmado formalmente 2026-05-16)
fecha_decision: 2026-05-15 (propuesta T1 H-12 Opción C en chat)
fecha_implementacion: 2026-05-15 (D3.2 commit beebff8) → 2026-05-16 (D3.2.1 commit a53cca6) → 2026-05-16 (D3.2.2 commit e13d669)
fecha_firma_T1: 2026-05-16 (firma binaria post Cowork audit VERDE 14/14)
fecha_firma_T2A: 2026-05-16 (Cowork audit D3.2 commit 2ac7f81 — "DSC-LF-005 LISTO PARA FIRMA → FIRMADO")
fecha_firma_T2B: 2026-05-16 (Perplexity Sonar Reasoning Pro adversarial pase 1 + pase 2 — fixes aplicados en D3.2.1 + D3.2.2)
fuentes:
  - repo:apps/la-forja/api/src/routes/tutor.ts (handler retorna toUIMessageStreamResponse)
  - repo:apps/la-forja/api/src/lib/llm/anthropic.ts (buildTutorStream con Vercel AI SDK 6)
  - repo:apps/la-forja/api/package.json (ai@^6.0.184 + @ai-sdk/anthropic@^3.0.78)
  - repo:apps/la-forja/web/src/components/tutor/Chat.tsx (useChat + DefaultChatTransport)
  - repo:apps/la-forja/web/src/lib/forjaHeaders.ts (headers canónicos compartidos)
  - repo:apps/la-forja/web/src/lib/forjaHeaders.contract.json (snapshot generado)
  - repo:apps/la-forja/web/_DOCTRINA_D3.md §7 + §8 + §8.5 (doctrina D3.2 + D3.2.1 + D3.2.2)
  - repo:bridge/manus_to_perplexity_LA_FORJA_001_D3_2_AUDIT.md (pase 1 input)
  - repo:bridge/manus_to_cowork_LA_FORJA_001_D3_2_AUDIT_REQUEST.md (Cowork audit input)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_D3_2_AUDIT_RESULT.md (commit 2ac7f81 — VERDE 14/14 + FIRMADO)
cruza_con: [DSC-LF-001, DSC-LF-002, DSC-LF-003, DSC-LF-004, DSC-G-005, DSC-G-008]
---

# SSE obligatorio para endpoints LLM en La Forja (DSC-LF-005)

## Decisión canónica (texto firmado verbatim)

> **"Todo endpoint backend de La Forja que invoque un LLM devuelve `text/event-stream` con `createUIMessageStreamResponse` / `streamText().toUIMessageStreamResponse()` del Vercel AI SDK 6 + provider Anthropic. JSON solo para metadata sin LLM. Aplica forward desde D3.2 (commit `beebff8`); sin retroactivos."**

## Stack canónico

| Capa | Versión | Rol |
|---|---|---|
| `ai` | ^6.0.184 | Vercel AI SDK core (`streamText`, `toUIMessageStreamResponse`, `convertToModelMessages`) |
| `@ai-sdk/anthropic` | ^3.0.78 | Provider Anthropic con modo Adaptive (`thinking: { type: "enabled", budgetTokens: 1024 }`) |
| `@ai-sdk/react` | ^3.0.186 | Hook `useChat` + `DefaultChatTransport` en frontend |
| `@anthropic-ai/sdk` | 0.96.0 (legacy) | Preservado para `invokeTutor` JSON path en `lib/llm/router.ts:21,90` (NO se usa en SSE path) |

## Modelo y configuración

- **Modelo:** `claude-opus-4-7` vía provider `anthropic('claude-opus-4-7')`.
- **Modo Adaptive obligatorio:** `providerOptions.anthropic.thinking = { type: "enabled", budgetTokens: 1024 }` (camelCase, no `budget_tokens`).
- **Callbacks budget pipeline:** `onFinish` invoca `postCallCommit(userId, mission, real)` con tokens reales (`totalUsage.inputTokens`, `totalUsage.outputTokens`); `onError` invoca `adjustSpent(userId, -estimated)` con try/catch fail-loud (F-D3.2-02 cerrado).

## Contrato de headers SSE (frontend↔backend)

Headers canónicos definidos en `apps/la-forja/api/src/shared/headers.ts` y espejados en `apps/la-forja/web/src/lib/forjaHeaders.ts` con snapshot regenerable `apps/la-forja/web/src/lib/forjaHeaders.contract.json`:

| Header | Valor | Decode |
|---|---|---|
| `content-type` | `text/event-stream` | — |
| `x-vercel-ai-ui-message-stream` | `v1` | — |
| `x-la-forja-intent` | string clasificación | utf-8 |
| `x-la-forja-confidence` | float 0..1 | parseFloat |
| `x-la-forja-model` | `claude-opus-4-7` | utf-8 |
| `x-la-forja-citations-b64` | base64url(JSON.stringify(string[])) | base64url decode → JSON.parse |
| `x-la-forja-validation-model` | `sonar-reasoning-pro` o vacío | utf-8 |

**Cap del header citations:** `FORJA_CITATIONS_HEADER_MAX_BYTES = 2048` con truncado **por citation completa** (loop incremental). JSON resultante siempre parseable (F-D3.2.1-01 cerrado).

## Magna PRE-stream (no post-stream)

Cuando `requireValidation === true`, magna corre antes de iniciar el stream. Razón binaria: una vez iniciado el SSE, no se pueden agregar headers de respuesta. Citations son metadata pre-stream por contrato HTTP. Documentado en banner de `apps/la-forja/api/src/routes/tutor.ts`.

## Forward-only (sin retroactivos)

DSC-LF-005 aplica desde commit `beebff8` (D3.2 inicial, 2026-05-15) hacia adelante. Endpoints anteriores que devuelven JSON con LLM no son regresión bajo este DSC siempre que (a) sean ortogonales al chat tutor (e.g. classifier interno, sprint_copilot batch), o (b) sean migrados a SSE en sprint posterior.

## Disputas adversariales validadas

- **F-D3.2-05 (no-rollback en AbortError):** **DISPUTA_VALIDA**. El patch propuesto introducía leak de budget en client abort. Doctrina actual (rollback siempre) es correcta. Logging diferenciado abort vs error agendado D6.
- **F-D3.2-08 (remover SDK legacy `@anthropic-ai/sdk@0.96.0`):** **DISPUTA_VALIDA**. El SDK legacy tiene uso vivo en `lib/llm/router.ts:21,90` (`invokeTutor` JSON path para classifier/sprint_copilot batch). DSC-LF-005 aplica a endpoints HTTP con LLM, no a funciones SDK internas. Migración consolidada a `@ai-sdk/anthropic` agendada D6.

## Items "Lo que NO hice" registrados como D5/D6

| Sprint | Item | Razón |
|---|---|---|
| D3.3 | UI toggle `requireValidation` (default false) | Prop expuesta en componente; UI agendada D3.3 |
| D3.3 | Markdown rendering `streamdown` | D3.2 entrega texto plano con cursor blink, suficiente para validar SSE binario |
| D3.3 | Tests Chat.tsx con happy-dom + MSW | Backend cubre flujo SSE end-to-end via Hono `request()` |
| D5 | RLS Supabase universal (D-D3.2-01 critical) | Data plane, no D3.2 scope |
| D5 | Notion Schema-First registry (D-D3.2-02) | Data plane |
| D6 | Provider layer unification (F-D3.2-08) | Migrar `invokeTutor` legacy → Vercel AI SDK 6 |
| D6 | Logging diferenciado abort vs error (F-D3.2-05) | Mejora observabilidad |
| D6 | Doc drift `_DOCTRINA_D3.md §7.3` (citations sin sufijo `-b64`) | Doc, no código — el código y JSON canónico están consistentes |

## Estado de validación

**firme — firmado formalmente 2026-05-16.** Ciclo completo:

1. **D3.2 (commit `beebff8`):** Migración inicial JSON → SSE. Backend 176/176 + Frontend 37/37 + builds verdes.
2. **Perplexity pase 1 (sobre `beebff8`):** 9 F-patterns + 3 R-patterns + 5 drifts → DO NOT SHIP.
3. **D3.2.1 (commit `a53cca6`):** 7 F aplicados + 2 disputas + 3 R aplicados. Backend 180/180 + Frontend 38/38 + builds verdes.
4. **Perplexity pase 2 (sobre `a53cca6`):** 7 F del pase 1 CERRADOS + 1 PARCIAL → 3 regresiones nuevas detectadas → DO NOT SHIP.
5. **D3.2.2 (commit `e13d669`):** 3 regresiones cerradas (F-D3.2.1-01 truncado JSON-aware, R-D3.2.1-02 contract sin fs, R-D3.2.1-03 round-trip JSON.parse). Backend 180/180 + Frontend 40/40 + builds verdes.
6. **Cowork audit D3.2 (commit `2ac7f81`):** VERDE 14/14 puntos binarios + 9/9 hard rules + 8/8 items "Lo que NO hice" justificados → **DSC-LF-005 LISTO PARA FIRMA → FIRMADO**.

## DSCs vigentes acumulados al cierre D3.2

LF-001 (5 puertas inviolables), LF-002 (budget pre-call check), LF-003 (cap $50 USD/mes), LF-004 (magna Perplexity), **LF-005 (SSE LLM forward-only)**, G-008 v4.

## Autorizaciones desbloqueadas

- ✅ **PR #133 autorizado para merge** — OPEN/READY/MERGEABLE. Merge manual T1 cuando decida.
- ✅ **D3.3 autorizado** — UI toggles `requireValidation` + `streamdown` + tests Chat.tsx con happy-dom + MSW.
