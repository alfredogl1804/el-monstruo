---
id: DSC-LF-002
proyecto: LA-FORJA
tipo: contrato_arquitectonico
titulo: "Toda invocación a LLM en La Forja DEBE pasar por preCallCheck antes del next() del middleware. Si excede el cap del usuario, responde HTTP 429 ForjaBudgetExceededError sin tocar el LLM"
estado: firme (canonizado retroactivamente 2026-05-16)
fecha_decision: 2026-04-XX (durante D2 spec)
fecha_firma_T1: 2026-05-16 (firma retroactiva por canonización capilla LA-FORJA)
fecha_firma_T2A: 2026-05-16 (Cowork audit D2 — verificó enforcement binario)
fuentes:
  - repo:apps/la-forja/api/src/middleware/budget.ts (preCallCheck antes de next())
  - repo:apps/la-forja/api/src/lib/budget.ts:28 (FORJA_BUDGET_CAP_USD = 50.0)
  - repo:apps/la-forja/api/src/lib/errors.ts (ForjaBudgetExceededError)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_AUDIT_RESULT.md:23 (DSC propuesto)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_D2_AUDIT_RESULT.md:24 (enforced verificado)
cruza_con: [DSC-LF-001, DSC-LF-003, DSC-LF-005, DSC-G-008]
---

# Budget pre-call check obligatorio en La Forja

## Decisión

Antes de invocar cualquier LLM en La Forja, el middleware `budget.ts` DEBE ejecutar `preCallCheck(userId, mission)` como gate inviolable. Si el usuario excede su cap mensual, la request es rechazada con HTTP 429 `ForjaBudgetExceededError` y **el LLM nunca es invocado** (cero costo en API externa, cero token consumido).

El cap canónico es la constante `FORJA_BUDGET_CAP_USD` exportada desde `lib/budget.ts:28` — **prohibido hard-codear el valor en otros archivos** (regresión documentada como F-D3.2-09 cerrada en D3.2.1).

## Enforcement binario

```ts
// apps/la-forja/api/src/middleware/budget.ts (esquemático)
import { FORJA_BUDGET_CAP_USD, preCallCheck } from "../lib/budget";
import { ForjaBudgetExceededError } from "../lib/errors";

export const budgetMiddleware = async (c, next) => {
  const userId = c.get("userId");
  const mission = c.get("mission");
  const estimated = await preCallCheck(userId, mission, { cap: FORJA_BUDGET_CAP_USD });
  if (estimated.exceeded) {
    throw new ForjaBudgetExceededError({ userId, mission, cap: FORJA_BUDGET_CAP_USD });
  }
  c.set("budgetEstimated", estimated.amount);
  await next();
};
```

- **Compile-time:** `c.set("budgetEstimated", ...)` antes de `next()` produce `c.var.budgetEstimated` tipado en handlers downstream.
- **Runtime:** `errorHandler` mapea `ForjaBudgetExceededError → HTTP 429 + body { error: "[la-forja:budget_exceeded]", cap, current }`.
- **Tests:** `routes.test.ts` cubre con mock `BudgetClient` que `preCallCheck` se llama ANTES de cada handler, y que el 429 se emite cuando `currentSpentUsd >= cap`.

## Por qué

La Forja es la herramienta personal de Alfredo Góngora Sr. — una sola cuenta con uso exploratorio. Sin cap pre-call, una llamada en bucle accidental (e.g. tutor regenerando infinito) podría drenar cientos de USD en minutos. El cap pre-call hace que el peor caso sea un 429 inmediato, no una factura sorpresa.

Detonante histórico: durante D2 spec se evaluó "post-call cap" (chequear después del LLM y rollback si excede). Cowork bloqueó esa propuesta porque "rollback negativo" no devuelve el costo al proveedor — solo limita el siguiente call. Pre-call es la única decisión binaria sin riesgo financiero.

## Implicaciones

- **Toda nueva ruta de La Forja que invoque LLM DEBE registrar el middleware `budget.ts`.** Sin él, el `errorHandler` no puede hacer rollback automático.
- **Todo cambio del cap requiere editar `FORJA_BUDGET_CAP_USD` en `lib/budget.ts`.** Hard-codear `50` o `50.0` en otros archivos es regresión bloqueante (caso F-D3.2-09 cerrado en D3.2.1 commit `a53cca6`).
- **El campo `c.var.budgetEstimated` queda como contrato implícito entre middleware y handlers** — handlers de tutor lo consumen para hacer rollback en `onError` del stream SSE (DSC-LF-005).

## Estado de validación

**firme.** Enforced binariamente desde D2 commit base. Cowork audit D2 verificó preCallCheck antes de next() con 14 tests passing. Cowork audit D2.5 revalidó cobertura de las 4 misiones (tutor + classifier + magna_validation + sprint_copilot). Cowork audit D3.2 (commit `2ac7f81`) revalidó como punto P-04 + P-05 + P-09 ("budget pipeline preservado en SSE", "F-D3.2-09 cap importado no hardcoded").
