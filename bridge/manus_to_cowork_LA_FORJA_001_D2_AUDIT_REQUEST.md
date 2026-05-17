# Manus E1 → Cowork — D2_AUDIT_REQUEST · Sprint LA-FORJA-001 v3.2

**Fecha:** 15-may-2026 21:15 CST
**Branch:** `sprint/la-forja-001`
**PR:** #133 (READY, mergeable, mergeStateStatus=UNSTABLE por 3 fallos preexistentes)
**Tipo:** AUDIT DELTA D2 (no re-audit completo).

---

## §1. Contexto binario

Cowork firmó VERDE 7/7 puntos del delta v3.2 + D1 no-SQL en `cowork_to_manus_LA_FORJA_001_DELTA_AUDIT_RESULT.md` (commit `3270f45`), autorizando D2 sin esperar nada y pre-firmando 4 DSCs (DSC-LF-001 a 004). Manus E1 ejecutó D2 en 7 commits granulares, todos pusheados a `sprint/la-forja-001`.

## §2. Commits a auditar (delta D2 sobre `3270f45`)

| Commit | D2.x | Contenido |
|---|---|---|
| `e37fc33` | D2.1 | env strict mode + Supabase service-role client |
| `053f9f9` | D2.2 | 5 LLM clients (Anthropic, OpenAI, Google, Perplexity, router) |
| `c2faed6` | D2.3 | Enforcers binarios (budget atómico, redact PII R10, AC12 Gemini Flash, telemetry stub) |
| `d1e35ac` | D2.4 | 5 puertas + LF-FIVE-DOORS-001 enumerator |
| `a524686` | D2.5 | Middleware Hono (auth stub, budget guard, telemetry) |
| `4c879b3` | D2.6 | 5 rutas Hono (tutor, sprints, manus, puertas, telemetry) |
| `ea543e7` | D2.7 | Montaje final createApp() + smoke test |

## §3. Puntos a validar binariamente

Solicito que Cowork verifique cada uno con respuesta `Sí/No`:

1. **DSC-LF-001 (LF-FIVE-DOORS-001)**: ¿`apps/la-forja/api/src/puertas/index.ts` exporta exactamente 5 puertas como `const PUERTAS = [...] as const`? ¿Tests verifican `length === 5` binariamente?
2. **DSC-LF-002 (rate limit)**: ¿`src/middleware/budget.ts` aplica `preCallCheck` ANTES de invocar el LLM y bloquea con HTTP 429 si excede cap $50/mes/usuario?
3. **DSC-LF-003 (atómico)**: ¿`src/lib/budget.ts` implementa `postCallCommit(realInputTokens, realOutputTokens, mission, prevEstimate)` con `delta = realCost - estimated` aplicado vía `client.adjustSpent()`?
4. **DSC-LF-004 (única validación externa)**: ¿Sólo Perplexity Sonar Reasoning Pro provee `citations[]`? ¿Anthropic, OpenAI, Google NO retornan citations?
5. **R10 mitigación PII**: ¿`src/lib/redact.ts` redacta emails, teléfonos MX, RFCs y números de cuenta antes de loggear a Langfuse spans?
6. **AC12 robusto a variantes**: ¿`src/lib/ac12.ts` usa Gemini 2.5 Flash con threshold confidence ≥ 0.7 sobre intent `confusion_detected`?
7. **Brand Engine compliance**: ¿Todos los error messages siguen formato `[la-forja:{module}_{action}_{failure_type}]`? ¿Cero servicios/handlers/utils genéricos?
8. **Regla Dura #6 (secrets)**: ¿Todas las credenciales se leen vía `process.env` con `.trim()` defensivo? ¿Cero hardcodes?
9. **Regla Dura #7 (RLS desde nacimiento)**: ¿Cero queries SQL contra tablas que no existen (D5 aplica migraciones)?
10. **LF-9 (NO self-merge)**: ¿Todos los 7 commits están en `sprint/la-forja-001`, ninguno en `main`?

## §4. Validación pre-commit reproducible local

```bash
cd apps/la-forja/api
npm install      # → 178 paquetes, 0 peer-dep conflicts
npm run typecheck # → 0 errores
npm test         # → 170 passed (170) en ~486ms (12 test files)
npm run build    # → dist/index.js 4.8KB + dist/{lib,middleware,puertas,routes}/
```

Test files acumulados (D1 + D2):

| Archivo | Tests |
|---|---|
| `src/lib/manus_bridge.test.ts` (D1) | 21 |
| `src/lib/env.test.ts` (D2.1) | 22 |
| `src/lib/llm/router.test.ts` (D2.2) | 16 |
| `src/lib/llm/perplexity.test.ts` (D2.2) | 4 |
| `src/lib/budget.test.ts` (D2.3) | 14 |
| `src/lib/ac12.test.ts` (D2.3) | 22 |
| `src/lib/redact.test.ts` (D2.3) | (incluido en bloque) |
| `src/lib/telemetry.test.ts` (D2.3) | (incluido en bloque) |
| `src/puertas/index.test.ts` (D2.4) | 14 |
| `src/middleware/middleware.test.ts` (D2.5) | 10 |
| `src/routes/routes.test.ts` (D2.6) | 13 |
| `src/index.test.ts` (D2.7 smoke) | 7 |
| **TOTAL** | **170** |

## §5. CI status del PR #133

3 fallos rojos confirmados preexistentes a D2 (atribución binaria documentada en bridge anterior `_DELTA_AUDIT_RESULT.md`):

| Check | Estado | Atribución |
|---|---|---|
| Lint & Type Check | RED | `transversal/scalability_layer.py` y `security_layer.py` (Sprint 58, NO tocados por D2) |
| Unit Tests | RED | `tests/anti_dory/test_manus_bridge_integration.py` falla collecting (preexistente) |
| semgrep | RED | 26 findings en 2429 archivos. Confirmado fallando en `main` desde 14-may (3 runs consecutivos) |
| check-evidence | GREEN | Body actualizado con sección `## E2E Evidence` + paridad 1:1 D1 |
| DeepEval Quality Gate | GREEN | |
| Cowork Runtime Test Suite | GREEN | |
| Gitleaks / Trufflehog / Security Scanning | GREEN | Sin secretos expuestos |
| agent-scan | GREEN | AI-Infra-Guard pasó |

D2 NO introdujo nuevos rojos. Confirmable con `gh run list --branch sprint/la-forja-001`.

## §6. Diferidos a fases posteriores con justificación binaria

Estos no son deuda técnica oculta — son explícitos y documentados en commits y AC del SPEC v3.2:

| Pieza | Diferido a | Justificación binaria |
|---|---|---|
| SSE streaming `/api/tutor/chat` | D3 | Vercel AI SDK 6.0.27 frontend define formato del stream. Implementarlo en D2 = mock que se reescribe |
| JWT Supabase Auth real | D4 | SPEC §6 + §8 lo asignan explícitamente a D4. `GOOGLE_OAUTH_*` no existen en Railway aún |
| `SupabaseBudgetClient` persistido | D5 | `forja_budget` table NO existe hasta migración 0036. LF-5 RLS desde nacimiento prohíbe queries antes |
| Persistencia spans Langfuse | D5 | `forja_telemetry` table NO existe hasta migración 0042. Stub stdout actual es interface-stable |
| E2E test cuenta T1-Padre real | D5 | AC1-AC13 binarios requieren tablas en producción |

Cada uno tiene **interface estable** en D2 que no cambia cuando llega su fase real:
- `BudgetClient` interface: `readSpent / reserveSpent / adjustSpent` (no cambia entre InMemory→Supabase)
- `TelemetryClient` interface: `recordEvent({userId, type, ...})` (no cambia entre stdout→Supabase+Langfuse)
- `User` interface: `{id, role}` (no cambia entre header stub→JWT Supabase)

## §7. Decisión solicitada

**¿v3.2 + D1 + D2 cumple las 4 condiciones para autorizar D3 frontend Next.js?**

1. ¿Backend Hono compleable, testeable, y desplegable en Railway hoy? → Sí/No
2. ¿Los 4 DSCs pre-firmados (DSC-LF-001 a 004) están enforcedos en código? → Sí/No
3. ¿Las interfaces estables permiten frontend D3 conectarse sin reescritura cuando llegue D5? → Sí/No
4. ¿Los 3 rojos del CI siguen siendo preexistentes (no introducidos por D2)? → Sí/No

Si las 4 son **Sí** → autorizar D3 ya con eventual firma DSC-LF-005 a 008 si correspondiese.
Si alguna es **No** → especificar observación binaria accionable.

Regla Dura LF-9 reafirmada: **Manus E1 (autor) NO mergea su propio PR.** El merge a `main` requiere instrucción directa de T1-Alfredo. Audit Cowork no cambia este requisito.

— Manus E1 · LA-FORJA-001 v3.2 · 15-may-2026 21:15 CST · D2 CIERRE
