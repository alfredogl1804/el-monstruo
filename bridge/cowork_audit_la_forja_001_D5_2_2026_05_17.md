---
fase: LA-FORJA-001 D5.2 — REEMPLAZO STUBS PERSISTENCIA
frase_canonica_pendiente: 🏛️ LA-FORJA-001 D5.2 — DECLARADO
fecha: 2026-05-17
autor: Manus Hilo B (ejecutor técnico)
veredicto_solicitado: GREEN binario 5/5 gates + content audit Cowork
branch: sprint/la-forja-001-d5-2
commit: d6f9a53
ancestor_main: 5858cf4
---

# Bridge Audit — LA-FORJA-001 D5.2 (Reemplazo Stubs Persistencia)

## §1 Frase canónica solicitada

> **🏛️ LA-FORJA-001 D5.2 — DECLARADO**

Sprint LA-FORJA-001 v3.2 fase **D5.2** — reemplazo de los 3 stubs de
persistencia activos en D2-D4 con queries reales contra las 11 tablas
creadas en D5.1 (migrations 0036-0046). Branch `sprint/la-forja-001-d5-2`
listo para audit + merge.

## §2 Score binario 5/5 GATES VERDE

| Gate | Veredicto | Evidencia |
|---|---|---|
| typecheck (`tsc --noEmit`) | ✅ GREEN | exit=0 |
| tests (vitest) | ✅ GREEN | 239/239 passing (+32 nuevos D5.2 sobre baseline 207 D5.1) |
| lint (`eslint --fix`) | ✅ GREEN | 0 errores, 2 warnings preexistentes (no-console en `manus_bridge.ts:432` y `telemetry.ts:71` stub) |
| build (`tsc -p tsconfig.json`) | ✅ GREEN | exit=0 |
| no-tokens (`scripts/_check_no_tokens.sh`) | ✅ GREEN | exit=0 |
| pre-commit hooks (gitleaks-staged, large files, merge conflicts, spec-lint, rls-default) | ✅ GREEN | all passed |

## §3 Cambios estructurales binarios

### 3.1 Nuevos archivos (8)

| Path | Tests | Función |
|---|---|---|
| `lib/repositories/profiles.ts` | 4 | Resuelve User → forja_profiles.id (UPSERT idempotente, cache local) |
| `lib/repositories/budget.ts` | 9 | SupabaseBudgetClient real (UPSERT atómico forja_budget) |
| `lib/repositories/telemetry.ts` | 11 | SupabaseTelemetryClient + mapping vocabulario TS→SQL whitelist |
| `lib/repositories/threads.ts` | 8 | ensureThread (anti-IDOR) + appendUser/AssistantMessage + recordValidation |

### 3.2 Archivos modificados (10)

| Path | Cambio |
|---|---|
| `lib/budget_clients.ts` | `defaultBudgetClient()` selector binario por NODE_ENV; añade resolver compartido `registerUserForResolver`/`resolveUserById` |
| `lib/telemetry.ts` | `installSupabaseTelemetry(nodeEnv)` async swap singleton; mantiene contrato `getTelemetryClient()` síncrono para preservar tests |
| `lib/llm/anthropic.ts` | Extiende `onFinish` con `text: string` para persistir contenido assistant |
| `index.ts` | Llama `installSupabaseTelemetry` en boot (production) + middleware `/api/*` post-auth registra User en cache compartido |
| `routes/tutor.ts` | Persistencia D5.2 con fail-soft binario: pre-stream `resolveProfileId+ensureThread+appendUserMessage`; post-stream `appendAssistantMessage`+`recordValidation` |
| `routes/sprints.ts` | **DRIFT P2 FIX** — `SPRINT_STATES` TS reconciliado al SQL canónico (8 valores) |
| `index.test.ts` | array hardcoded actualizado al nuevo enum |
| `lib/llm/google.ts`, `lib/llm/openai.ts`, `lib/manus_bridge.ts` | curly braces (eslint --fix automático, no-op semántico) |

## §4 Decisiones de diseño binarias

### 4.1 Selector binario stub vs real por NODE_ENV

**Decisión:** `defaultBudgetClient()` y `installSupabaseTelemetry()` activan los clients reales **solo** cuando `NODE_ENV=production`. En `development` y `test` se mantiene `InMemoryBudgetClient` y `StdoutTelemetryClient`.

**Razón:** preserva 207 tests del baseline D5.1 sin tocar ni un mock. Los 32 tests nuevos D5.2 (`repositories/*.test.ts`) interceptan `getSupabase` con `vi.mock('../supabase')` para validar contrato sin red ni DB.

**Trade-off:** los stubs siguen siendo el path de development. Cualquier dev nuevo en La Forja arranca con stubs y solo ve real al promover a production. Aceptable — alternativa (forzar Supabase local) introduciría dependencia de docker-compose en CI, fuera de scope D5.2.

### 4.2 ESM-first sin `require` dinámico

**Decisión:** `installSupabaseTelemetry()` usa `await import()` en lugar de `require()` dinámico. El package `@la-forja/api` tiene `"type": "module"`, por lo que `require` lanza `Cannot find module './env'` en runtime aunque tsc lo permita.

**Evidencia del fix:** primer intento usó `require()` (10 tests rojos por `Cannot find module`); segundo intento con `await import()` lazy desde `createApp()` → 239/239 verde.

### 4.3 Anti-IDOR en `ensureThread`

**Decisión:** si el cliente envía `threadId` que NO pertenece al `profile_id` resuelto, el server **silenciosamente crea uno nuevo** en lugar de retornar 403. La razón: el thread del cliente puede ser un id stale de localStorage tras logout/login con otro Google account; bloquear con 403 produce una pantalla rota mientras que crear thread fresh continúa el UX sin fricción.

**Mitigación side-channel:** ningún dato sensible se filtra porque el server nunca expone que el thread pasado existía bajo otro profile_id. El comportamiento es indistinguible de "thread no existe".

### 4.4 Fail-soft binario en `routes/tutor.ts`

**Decisión:** los `try/catch` de persistencia D5.2 en `tutor.ts` **NUNCA** rompen el stream. Si `resolveProfileId` o `ensureThread` fallan, log warn `[la-forja:tutor_persist_user_failed]` y el stream continúa sin persistir. El usuario ve la respuesta del tutor; el operador ve el warning.

**Razón:** UX > telemetría. Una caída transitoria de Supabase no debe romper el tutor. Los warnings se agregan en logs Railway para forensics post-mortem.

## §5 Disclosure de drift y deuda

### P2 — Vocabulario telemetría TS vs SQL whitelist

**Drift identificado:** la enum SQL `forja_telemetry.event` tiene 13 valores (D5.1 migration 0043), mientras que el set TS `TelemetryEventType` tiene 8 valores. Mapping aplicado:

| TS type | SQL event | SQL subject |
|---|---|---|
| `simplification_requested` | `simplification_requested` | null |
| `confusion_detected` | `confusion_detected` | null |
| `turn_abandoned` | `abandonment_detected` | null |
| `sprint_completed` | `completion_signal` | `"sprint"` |
| `sprint_started` | `other` | `"sprint_started"` |
| `puerta_invoked` | `other` | `"puerta_invoked"` |
| `budget_exceeded` | `budget_cap_hit` | null |
| `magna_validation_used` | `other` | `"magna_validation_used"` |

**Deuda:** los tipos TS no se renombran en este sprint para evitar scope creep. Si Cowork pide reconciliación bidireccional explícita, se hace en D5.3 con migration que renombre o expanda la whitelist SQL.

**Archivo de referencia:** `lib/repositories/telemetry.ts` líneas 41-72.

### P3 — Modo del thread snapshot único

**Decisión:** el `mode` (light|normal|heavy|power) del thread se persiste **solo** en la creación inicial via `ensureThread(profileId, threadId, mode)`. Cambios mid-thread no se reflejan en `forja_threads.mode`.

**Justificación:** suficiente para D5.2 — el modo se usa como signal de telemetría a nivel thread, no como source-of-truth por mensaje. La granularidad por mensaje queda para D5.4 (cuando se introduzca `forja_messages.mode_used` o tabla `forja_thread_mode_changes`).

**Archivo de referencia:** `lib/repositories/threads.ts` función `ensureThread`.

### Drift P2 reconciliado en este sprint (no es deuda)

`SPRINT_STATES` en `routes/sprints.ts` estaba con vocabulario v3.0 SPEC (`drafting, review_alfredo, review_cowork, ready_to_execute, canonized`) que ya había sido reemplazado por v3.2 SPEC en SQL (`confirmed, executing, waiting_audit, audited, merged, blocked, archived`). **SQL gana sobre TS** por Regla Dura #7 (plano de datos cerrado por defecto). Reconciliado en commit `d6f9a53`.

## §6 Solicitud explícita a Cowork T2

1. **Audit content de los 4 nuevos archivos** en `lib/repositories/`. Verificar uso de env vars (no hardcoded), namespace de errores `[la-forja:*]` (Brand Engine), y RLS-awareness implícito vía service-role client + filtros explícitos por `profile_id`/`thread_id`.

2. **Validar mapping P2 telemetría**: confirmar que el mapping TS→SQL no pierde información significativa para los 6 dashboards previstos en §7 SPEC v3.2. Si encuentras un mapping mejor, propón en este bridge para canonización D5.3.

3. **Validar fail-soft binario en `tutor.ts`**: confirmar que el patrón de no romper el stream cuando persistencia falla no enmascara P0s.

4. **Veredicto binario** sobre frase canónica: `🏛️ LA-FORJA-001 D5.2 — DECLARADO` o lista de blockers para retest.

## §7 Próximos pasos automáticos (post-audit verde)

1. Merge `sprint/la-forja-001-d5-2` → `main` (squash).
2. D5.3 — implementar SSE persistence helpers (chat_streaming canonical) si Cowork lo prioriza sobre P2 vocabulary fix.
3. D6 prep — railway env var checklist para activación NODE_ENV=production con SUPABASE_URL + SUPABASE_SERVICE_KEY validados.
