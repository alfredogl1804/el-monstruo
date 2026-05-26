# Sprint D6-CREDITS-RESTORE-001 — FIRMADO

**Origen:** cierre D5 (PR #169 mergeado SHA `522eaa8e`) reveló bloqueo operacional 3 amarillos D4 #8/#9/#10 por root causes externas al código (créditos Anthropic + OpenAI + Gemini prefix bug recurrente).

**Autorización:** Cowork T2-A firma bajo autoridad delegada T1 (post-D5 declarado). T1 carga créditos cuando convenga (NO bloqueante para implementación circuit breaker, sí bloqueante para smoke retest).

**Owner ejecución:** Manus E2 (circuit breaker código) + T1 (acción operacional créditos).
**Owner doctrina:** Cowork T2-A.
**Estimación:** 1h Manus E2 + acción T1 paralela (5min carga Anthropic + 10min verificación OpenAI).

---

## §1 Acción T1 operacional (P0 BLOQUEANTE para smoke retest)

### §1.1 Anthropic API — carga créditos

Cuenta Anthropic detectada con saldo cero. T1 debe:

1. Ir a https://console.anthropic.com/settings/billing
2. Cargar mínimo $10 USD (suficiente para ~333 invocaciones Claude Opus 4.7 a $30/Mtok output asumiendo ~1k tokens/llamada)
3. Verificar que la API key activa en Railway env var (`ANTHROPIC_API_KEY`) corresponde a la org con créditos

**Verificación binaria post-carga:**
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-opus-4-7","max_tokens":10,"messages":[{"role":"user","content":"hola"}]}'
# Esperado: HTTP 200 con response JSON. Si HTTP 400 "credit balance too low" → carga falló.
```

### §1.2 OpenAI API — verificación + carga si requerido

GPT-5.5 Pro respondió vacío en smoke D5 (logs verbatim: `no JSON block found in response: ` con raw vacío). Posibles causas a T1 verificar:

1. **Saldo OpenAI:** https://platform.openai.com/account/billing/overview — confirmar saldo > $0
2. **API key válida:** confirmar `OPENAI_API_KEY` en Railway corresponde a cuenta con saldo
3. **Acceso modelo `gpt-5.5-pro`:** algunos modelos requieren tier organization upgrade. Verificar en https://platform.openai.com/account/limits
4. **Si key inválida o sin acceso:** rotar key + actualizar Railway env var

**Verificación binaria post-carga:**
```bash
curl https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.5-pro","input":[{"role":"user","content":"hola"}],"max_output_tokens":10}'
# Esperado: HTTP 200 + response.output_text. Si HTTP 400 → diagnosticar.
```

### §1.3 Gemini Flash 2.5 — no requiere acción T1

Issue upstream modelo (ignora ocasionalmente `responseMimeType`). Solución #2 (`extractJsonStrict`) + Solución #3 (fallback) cubren defensa. NO requiere acción T1.

---

## §2 Acción Manus E2 — Circuit Breaker pre-call

Implementar detección proactiva de "credit balance too low" ANTES de invocar el modelo, en lugar de descubrirlo solo cuando la API responde 400.

### §2.1 Archivos a modificar

- `apps/la-forja/api/src/lib/llm/anthropic.ts` (+ circuit breaker pre-call)
- `apps/la-forja/api/src/lib/llm/openai.ts` (+ circuit breaker pre-call)

### §2.2 Lógica circuit breaker binaria

Cada cliente LLM mantiene un flag `_creditDepletedUntil: number | null`:

```typescript
let _creditDepletedUntil: number | null = null;

export async function invokeTutor(opts: ...) {
  // Circuit breaker: si detectamos credit depleted en últimos 5min, fail fast
  if (_creditDepletedUntil && Date.now() < _creditDepletedUntil) {
    throw new Error(
      `[la-forja:anthropic_credit_depleted] circuit breaker open until ${new Date(_creditDepletedUntil).toISOString()}`
    );
  }

  try {
    const response = await anthropic.messages.create(...);
    return response;
  } catch (err) {
    if (err.message?.includes("credit balance is too low")) {
      _creditDepletedUntil = Date.now() + 5 * 60 * 1000; // 5min cooldown
      console.error("[la-forja:anthropic_credit_depleted] circuit breaker triggered for 5min");
    }
    throw err;
  }
}
```

### §2.3 Beneficios binarios

1. **Reducción latencia P99** durante credit outage: en lugar de esperar 2-3s timeout API, fail fast en <1ms
2. **Reducción rate-limit churn:** evita spamear API con calls que sabemos van a fallar
3. **Observabilidad:** log namespaced `[la-forja:*_credit_depleted]` aparece en telemetry para alerts operacionales

### §2.4 Tests obligatorios

1. `test('circuit breaker opens on credit_balance_too_low response', ...)`
2. `test('circuit breaker fails fast within 5min cooldown window', ...)`
3. `test('circuit breaker auto-resets after 5min', ...)`
4. `test('circuit breaker does NOT trigger on other errors (rate-limit, timeout)', ...)`
5. NO regresión: 253/253 vitest baseline post-D5 verde

---

## §3 Acceptance Criteria binarios

| # | Criterion | Verificación |
|---|---|---|
| 1 | T1 confirma Anthropic créditos cargados | Curl test §1.1 HTTP 200 |
| 2 | T1 confirma OpenAI key + saldo + tier | Curl test §1.2 HTTP 200 |
| 3 | Manus E2 circuit breaker implementado | PR con +2 archivos `llm/anthropic.ts` + `llm/openai.ts` |
| 4 | 4 tests circuit breaker nuevos + 253 baseline | `vitest run` = 257/257 verde |
| 5 | Smoke retest E2E `POST /api/tutor/chat` con cookie JWT existente | HTTP 200 + SSE stream Claude Opus 4.7 funcional |
| 6 | `forja_messages.cost_usd > 0` ≥1 fila assistant post-smoke | SQL Supabase prod |
| 7 | `forja_threads.total_usd > 0` ≥1 thread | SQL Supabase prod |
| 8 | D4 amarillos #8/#9/#10 cierran retroactivamente | Frase canónica final |

---

## §4 OUT OF SCOPE

- Refactor lib/llm/google.ts (Gemini circuit breaker — no aplica, no falla por créditos)
- Cambio de modelos en fallback chain (sigue Opus 4.7 + GPT-5.5 Pro per D5)
- Optimización costo middle-tier (defer a D7 condicional si fallback rate >1%)
- Cualquier archivo fuera de `apps/la-forja/api/src/lib/llm/anthropic.ts` + `openai.ts` + tests

---

## §5 Frase canónica esperada

Post-circuit breaker merge + créditos cargados + smoke retest verde:

> 🏛️ **D6-CREDITS-RESTORE-001 — DECLARADO**
>
> Circuit breaker pre-call implementado en Anthropic + OpenAI. Créditos restaurados. Smoke E2E verde.
> 3 amarillos D4 #8/#9/#10 cierran retroactivamente → 🏛️ **D4-PROD-AUTH-001 100% DECLARADO**.

---

## §6 Próximos pasos operativos

1. **T1 paralelo:** cargar créditos Anthropic + verificar OpenAI (5-15min total)
2. **Manus E2:** abre branch `fix/d6-credits-restore-circuit-breaker` desde `main`
3. Implementa circuit breaker §2 en 2 archivos
4. 4 tests vitest §2.4 + 253 baseline
5. Auto-audit DSC-G-008 v4 pre-PR
6. PR contra main + audit content Cowork
7. Cowork merge bajo regla evolucionada T1 directa "procede" + audit verde
8. Smoke retest §3 #5/#6/#7 con cookie `$JWT` activa (válida hasta 2026-05-25)
9. Bridge cierre + frase canónica § 5

---

**Firmado por Cowork T2-A bajo autoridad delegada T1 post-D5 declarado 2026-05-18.**
**Manus E2 puede arrancar circuit breaker en paralelo a T1 cargando créditos.**
**Smoke retest §3 #5 requiere ambos: circuit breaker mergeado + créditos cargados.**
