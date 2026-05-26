# Sprint D5-TUTOR-CLASSIFIER-ROBUSTNESS-001 — FIRMADO

**Origen:** hallazgo F2 reportado por Manus E2 en smoke C3 D4-PROD-AUTH-001 (2026-05-18 11:05Z).
**Autorización T1:** verbatim "procede" 2026-05-18 ~11:10Z.
**Firma:** Cowork T2-A autoridad delegada T1 (regla evolucionada del merge §spec técnico reversible).
**Owner ejecución:** Manus E2 (Hilo Ejecutor 2 — la-forja).
**Owner doctrina:** Cowork T2-A.
**Estimación:** 1-2h.
**Bloqueante para:** D5/D7 tutor user flows reales (cualquier `POST /api/tutor/chat`).

---

## §1 Contexto binario

D4-PROD-AUTH-001 cerrado VERDE con 8/11 criterios directos + 3 condicionados a F2. F2 binario:

**Síntoma reproducible determinista:**
```
$ curl -X POST -H "Cookie: la-forja_session=$JWT" \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"Hola..."}], "mode":"normal"}' \
    https://la-forja-api-production.up.railway.app/api/tutor/chat
HTTP/2 500
{"ok":false,"error":"[la-forja:tutor_classifier_failed]","service":"la-forja-api"}
```

**Stack trace prod (verbatim Manus E2):**
```
Error: [la-forja:tutor_classifier_failed]
    at file:///app/dist/routes/tutor.js:103:19
  [cause]: Error: [la-forja:ac12_classify_invalid_json] Gemini Flash returned non-JSON: Here is
      at classifyMessage (file:///app/dist/lib/ac12.js:103:15)
```

**Cadena ejecutada OK pre-fail:** `auth.js:121 → telemetry.js:23 → budget.js:39 → tutor.js:96 → ac12.js:103`. El fail está aislado en el último eslabón.

**Root cause:** `lib/ac12.ts:classifyMessage()` llama Gemini Flash con prompt pidiendo JSON estricto. Modelo responde con preámbulo `"Here is..."` seguido posiblemente de JSON. `JSON.parse()` falla porque la respuesta no empieza con `{` o `[`.

---

## §2 Acceptance Criteria binarios

| # | Criterion | Verificación |
|---|---|---|
| 1 | `POST /api/tutor/chat` con mensaje canónico retorna HTTP 200 SSE stream | `curl -X POST .../api/tutor/chat -d '{"messages":[{"role":"user","content":"Hola..."}], "mode":"normal", "requireValidation":false}' → 200 + chunks SSE` |
| 2 | Test regresión binaria reproduce F2 vía mock + verifica fix | `vitest` test simula respuesta `"Here is\n{...}"` de Gemini y verifica que `classifyMessage()` retorna estructura válida |
| 3 | Test unitario solución #1 (Gemini responseMimeType) | Mock Gemini API con `responseMimeType: "application/json"` + `responseSchema` → respuesta JSON puro garantizado |
| 4 | Test unitario solución #2 (parser tolerante) | Input `"Here is the result:\n{\"intent\":\"greet\"}"` → extrae JSON correcto |
| 5 | Test unitario solución #3 (fallback chain) | Mock Gemini Flash falla 2x → fallback Claude Haiku → respuesta válida |
| 6 | `forja_messages.cost_usd > 0` ≥1 fila post-test | SQL Supabase prod verifica persistencia |
| 7 | `forja_threads.total_usd > 0` ≥1 thread | SQL Supabase prod verifica persistencia |
| 8 | NO regresión en 242/242 vitest baseline | `npm test` verde completo |
| 9 | DSC-G-008 v4 6 gates verde audit Cowork pre-merge | Self-audit Manus E2 + audit Cowork |
| 10 | E2E real T1 con cookie producción | Manus E2 ejecuta `curl` con `$JWT` real post-deploy, retorna SSE stream funcional |

---

## §3 Solución #1 (OBLIGATORIA) — Gemini structured output

Gemini API soporta forzar JSON puro vía `responseMimeType` + `responseSchema`. Aplicar en `lib/ac12.ts`:

```typescript
const response = await gemini.generateContent({
  contents: [...],
  generationConfig: {
    responseMimeType: "application/json",
    responseSchema: {
      type: "object",
      properties: {
        intent: { type: "string", enum: ["greet", "question", "command", "feedback", "other"] },
        topic: { type: "string" },
        confidence: { type: "number" }
      },
      required: ["intent", "topic", "confidence"]
    }
  }
});
```

**Justificación binaria:** root cause fix. Gemini API garantiza JSON puro cuando `responseMimeType: "application/json"` está activo. Esto elimina la categoría del bug completamente.

**Caveat:** verificar Gemini Flash 1.5+ soporta `responseSchema` (validar en docs Google AI Studio 2026-05). Si modelo en uso es legacy sin soporte, escalar a Gemini Flash 2.0 o aplicar Solución #2 como primary.

---

## §4 Solución #2 (DEFENSE-IN-DEPTH) — Parser tolerante

Independiente de #1, el parser debe ser robusto contra prefijos/sufijos de texto. Reemplazar `JSON.parse(response)` por:

```typescript
function extractJsonStrict(raw: string): unknown {
  const match = raw.match(/(\{[\s\S]*\}|\[[\s\S]*\])/);
  if (!match) {
    throw new Error("[la-forja:ac12_classify_invalid_json] no JSON found in response");
  }
  return JSON.parse(match[1]);
}
```

**Justificación binaria:** defense-in-depth contra futuras regresiones del modelo o cambios de prompt. Solución #1 + #2 aplicadas en conjunto = doble barrera.

---

## §5 Solución #3 (MAGNA) — Fallback chain

Si Gemini Flash falla 2 retries consecutivos con `[la-forja:ac12_classify_invalid_json]`, fallback automático a Claude Haiku 4.5 (rápido + barato). Si Claude Haiku también falla, fallback a GPT-4o-mini.

```typescript
const FALLBACK_CHAIN = ["gemini-2.0-flash-exp", "claude-haiku-4-5", "gpt-4o-mini"];

async function classifyWithFallback(messages: Message[]): Promise<Classification> {
  let lastError: Error | null = null;
  for (const model of FALLBACK_CHAIN) {
    try {
      return await classifyMessage(messages, model);
    } catch (err) {
      lastError = err as Error;
      telemetry.log("ac12_fallback_triggered", { model, error: err.message });
      continue;
    }
  }
  throw new Error("[la-forja:tutor_classifier_all_models_failed]", { cause: lastError });
}
```

**Justificación binaria:** alineado DSC-V-001 (8 Sabios canónicos + fallback). Si el classifier falla, el tutor degrada gracefully en lugar de devolver 500.

**Caveat:** fallback chain agrega latencia P99 si el primer modelo falla. Telemetry obligatoria para tracking de `ac12_fallback_triggered` rate.

---

## §6 Test plan binario

**Archivos a modificar:**
- `apps/la-forja/api/src/lib/ac12.ts` (refactor con #1 + #2 + #3)
- `apps/la-forja/api/src/lib/ac12.test.ts` (tests nuevos para 3 soluciones + regresión F2)

**Tests obligatorios:**
1. `test('classifyMessage uses responseMimeType application/json', ...)`
2. `test('extractJsonStrict tolerates "Here is..." prefix', ...)` ← regresión F2
3. `test('classifyWithFallback retries gemini → claude → gpt on parse fail', ...)`
4. `test('NO regression: 242/242 baseline vitest passes', ...)`

**Reproducción binaria F2 pre-fix:**
```typescript
// Pre-fix: este test FALLA porque ac12.ts no tolera prefijo
test('F2 regression: Gemini "Here is..." prefix', async () => {
  const mockGemini = mockGeminiResponse('Here is the classification:\n{"intent":"greet","topic":"saludo","confidence":0.95}');
  const result = await classifyMessage([{role:'user', content:'Hola'}], mockGemini);
  expect(result.intent).toBe('greet');
});
```

---

## §7 OUT OF SCOPE (NO tocar)

- `apps/la-forja/api/src/middleware/auth.ts` (cerrado D4)
- `apps/la-forja/api/src/middleware/budget.ts` (cerrado D5.3)
- `apps/la-forja/api/src/middleware/telemetry.ts` (cerrado D2.5)
- `apps/la-forja/api/src/routes/tutor.ts` líneas 1-95 (pre-classifier flow)
- `apps/la-forja/api/src/routes/tutor.ts` línea 96 (`classifyMessage` invocation) — ese call site queda igual, solo cambia la implementación interna
- Cualquier otro archivo no listado en §6

Si Manus E2 detecta que necesita tocar algo fuera de scope §7, **DEBE parar y proponer addendum** (no expandir scope unilateralmente — anti-F-pattern doctrinal).

---

## §8 Validaciones doctrina

| Regla | Aplicación |
|---|---|
| **DSC-G-008 v4** validar codebase pre-spec | ✅ Stack trace prod binario verificado por Manus E2 + reproducción determinista |
| **DSC-G-013 v0.1 Coherence Gate Nivel A** | ⚠️ N/A — fix puro código TS, no migration, no CHECK constraint |
| **DSC-V-001 8 Sabios canónicos** | ✅ Fallback chain Claude Haiku + GPT-4o-mini alineado |
| **DSC-LF-001 cinco puertas inviolables** | ✅ Puerta #2 validación SSE chunks NO se toca |
| **DSC-LF-005 SSE protocol Vercel AI SDK 6** | ✅ NO se toca el SSE response handling |
| **DSC-G-008 v2 scope mínimo** | ✅ 2 archivos modificados solamente |
| **Regla evolucionada del merge** | ✅ Cowork mergea bajo (a) instrucción T1 directa "procede" + (b) DSC-G-008 v4 audit verde 6/6 self-emitted post-PR |
| **F#23 + S11 (canonizadas hoy)** | ⚠️ Aplica si Manus E2 cambios reactiven tests previamente broken: enumerar binariamente cuáles tests nuevamente operacionales antes de declarar verde |

---

## §9 Frase canónica de cierre esperada

Post-merge + smoke E2E real verde:

> 🏛️ **D5-TUTOR-CLASSIFIER-ROBUSTNESS-001 — DECLARADO**
>
> F2 cerrado binariamente. `POST /api/tutor/chat` retorna SSE stream funcional en producción.
> 3 soluciones #1 + #2 + #3 aplicadas (root cause + defense-in-depth + magna fallback).
> Criterios D4-PROD-AUTH-001 8/9/10 ahora **VERDE DIRECTO** (ya no condicionados a F2).

---

## §10 Próximos pasos operativos

1. **Manus E2** abre branch `fix/d5-tutor-classifier-robustness-f2` desde `main`
2. Implementa #1 + #2 + #3 en `lib/ac12.ts`
3. Tests vitest 4 nuevos + 242/242 baseline verde
4. Auto-audit DSC-G-008 v4 6 gates pre-PR
5. Abre PR contra `main`
6. Cowork T2-A audit content + Coherence Gate ⚠️ N/A → si verde, merge bajo regla evolucionada T1
7. Railway redeploy producción
8. Manus E2 smoke E2E real con cookie `$JWT` activa (Alfredo NO necesita re-loggear, cookie expira 2026-05-25)
9. Bridge cierre + frase canónica § 9

---

**Firmado por Cowork T2-A bajo autorización T1 verbatim "procede" 2026-05-18.**
**Manus E2 puede empezar inmediato.**
