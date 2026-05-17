---
id: DSC-LF-003
proyecto: LA-FORJA
tipo: contrato_arquitectonico
titulo: "Cada usuario de La Forja tiene un cap mensual de 50 USD enforced vía FORJA_BUDGET_CAP_USD. postCallCommit liquida la diferencia entre estimated y real con la fórmula spent = current - estimated + real"
estado: firme (canonizado retroactivamente 2026-05-16)
fecha_decision: 2026-04-XX (durante D2 spec)
fecha_firma_T1: 2026-05-16 (firma retroactiva por canonización capilla LA-FORJA)
fecha_firma_T2A: 2026-05-16 (Cowork audits D2 + D2.5 + D3.2 — verificó enforcement binario en 4 misiones)
fuentes:
  - repo:apps/la-forja/api/src/lib/budget.ts:28 (FORJA_BUDGET_CAP_USD = 50.0)
  - repo:apps/la-forja/api/src/lib/budget.ts (postCallCommit + adjustSpent)
  - repo:apps/la-forja/api/src/lib/llm/router.ts (MISSION_PRICING con 4 entries)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_AUDIT_RESULT.md:23 (DSC propuesto)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_D2_AUDIT_RESULT.md:24 (enforced verificado)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_D2_5_AUDIT_RESULT.md:41 (4 misiones cubiertas)
cruza_con: [DSC-LF-001, DSC-LF-002, DSC-LF-004, DSC-LF-005]
---

# Cap presupuestal por usuario por mes en La Forja

## Decisión

**Cap canónico: 50.00 USD por usuario por mes.** El valor vive en una sola constante exportada desde `apps/la-forja/api/src/lib/budget.ts:28`:

```ts
export const FORJA_BUDGET_CAP_USD = 50.0;
```

Tras cada llamada exitosa al LLM, `postCallCommit(userId, mission, real)` liquida la diferencia entre el estimado pre-call y el costo real con la fórmula:

```
spent_usd_month = current_spent - estimated + real
```

donde:
- `current_spent` es la lectura del DB al momento de `preCallCheck`
- `estimated` es el costo proyectado por `MISSION_PRICING[mission].estimateUsd`
- `real` es el costo material derivado de los tokens reales que devolvió el proveedor

`adjustSpent(userId, delta)` ejecuta la mutación atómica con `delta = real - estimated`. Si el LLM falla mid-flight (timeout, abort, error de provider), se invoca `adjustSpent(userId, -estimated)` como rollback negativo: nadie paga por un call que no completó.

## 4 misiones cubiertas (estado D3.2)

| Misión | Modelo | Estimado pre-call | Cobertura |
|---|---|---|---|
| `tutor` | Anthropic Claude Opus 4.7 (SSE Adaptive, budgetTokens 1024) | 0.075 USD | DSC-LF-005 |
| `classifier` | Anthropic Claude Opus 4.7 (JSON corto) | 0.005 USD | D2 |
| `magna_validation` | Perplexity Sonar Reasoning Pro (citations) | 0.040 USD | DSC-LF-004 |
| `sprint_copilot` | Anthropic Claude Opus 4.7 (JSON estructurado) | 0.060 USD | D2 |

**Adición de una quinta misión requiere DSC nuevo + actualizar `MISSION_PRICING` en `lib/llm/router.ts` + tests de cobertura.**

## Por qué 50 USD / mes

Calibrado sobre uso esperado del usuario (Alfredo Góngora Sr.):

- 50 turnos de chat tutor por día × 30 días × 0.075 USD ≈ 112.50 USD bruto
- Con cache hits + uso esporádico real ≈ 35-45 USD reales

50 USD deja margen ~15% sin permitir runaway. El cap es **dimensionado para uso humano sostenible, no para experimentos automatizados** — agentes que disparan llamadas en bucle agotan el cap en horas (comportamiento intencional como tripwire).

## Enforcement binario

- **Constante única:** prohibido hard-codear `50` o `50.0` en otros archivos. Caso F-D3.2-09 (cerrado D3.2.1 commit `a53cca6`): el middleware `budget.ts` tenía `cap: 50.0` literal en vez de importar `FORJA_BUDGET_CAP_USD`. Resolución: import + uso de la constante.
- **Tests cobertura:** `routes.test.ts` en backend cubre los 4 misiones × happy-path (postCallCommit) × error-path (rollback negativo). 180/180 tests passing post-D3.2.2.
- **Multi-mission rollback:** D2.5 hardening agregó test "reserveSpent multi-mission" que verifica que cuando una request acumula 2-3 reservas (e.g. classifier + magna + tutor) y una falla, el rollback revierte TODAS las pendientes (no solo la última).

## Implicaciones

- **Cualquier sprint que altere `FORJA_BUDGET_CAP_USD` debe firmar DSC nuevo o citar este DSC en el commit.** Cambios silenciosos al cap son regresión bloqueante.
- **Sprint D5 (data plane Supabase RLS)** debe habilitar lectura per-userId del campo `spent_usd_month` con policy explícita — `BudgetClient` actualmente usa una mock implementation, la real requiere DSC-LF-NNN nuevo.
- **Sprint D6 (provider layer unification)** propondrá una `MISSION_PRICING_TABLE` versionada con migration history para rastrear cambios de costos del proveedor sin perder trazabilidad presupuestal.

## Estado de validación

**firme.** Cowork audit D2 verificó la fórmula `delta = real - estimated`. Cowork audit D2.5 verificó cobertura 4/4 misiones. Cowork audit D3.2 (commit `2ac7f81`) revalidó como punto P-04 ("budget pipeline preservado") + P-09 ("F-D3.2-09 cap importado, no hardcoded"). Perplexity adversarial pase 1 + pase 2 (commits `a53cca6`, `e13d669`) confirmaron rollback binario en error-path SSE.
