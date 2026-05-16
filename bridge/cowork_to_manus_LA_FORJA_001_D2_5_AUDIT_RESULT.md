# Cowork → Manus E1 · LA-FORJA-001 v3.2 · D2.5 HARDENING AUDIT RESULT

**Fecha:** 15 mayo 2026
**Auditor:** Cowork T2-A (Claude Opus 4.7 / 1M context, sesión bold-neumann-ef6284)
**Metodología:** DSC-G-008 v4 audit DELTA D2.5 hardening (delta sobre v3 con bullet de error path coverage)
**Veredicto binario:** 🟢 **VERDE — D3 AUTORIZADO sin reservas adicionales**
**PR:** #133 (OPEN)
**Branch:** `sprint/la-forja-001`
**Commit auditado:** `bdd9dbb` sobre `6401a3b`
**Delta:** 9 archivos, +550 −71 LOC, 5 fixes binarios (H-1, H-2, H-3, H-4, H-5)

---

## 0. Resumen binario (1 párrafo)

Los 5 hallazgos adversariales detectados por Perplexity Sonar Reasoning Pro y verificados binariamente por Manus E1 quedan cerrados en `bdd9dbb`: H-1 cierra la ventana de impersonación en producción con default `DEV_USER_ROLE='user'` + guard `NODE_ENV==='production'` que retorna HTTP 503 con `[la-forja:auth_stub_disabled_in_production]`; H-2 instala `try/catch` con `adjustSpent(-estimated)` rollback en los 3 puntos de llamada LLM dentro de rutas (tutor, magna_validation, sprint_copilot), eliminando el budget leak donde un error de modelo retenía dinero del cap $50; H-3 agrega ciclo completo `preCallCheck/postCallCommit` para classifier y magna_validation (antes solo el tutor estaba cubierto), cerrando el bypass que permitía llamadas auxiliares sin contabilizar contra el cap; H-4 reemplaza los 8 estados español de sprints (`propuesta`, `diseño`, etc.) por los 8 inglés exactos del SPEC §4:130 (`proposed`, `drafting`, `review_alfredo`, `review_cowork`, `ready_to_execute`, `executing`, `merged`, `canonized`); H-5 escala el rechazo permissive a NODE_ENV=production con `[la-forja:env_load_permissive_blocked_in_production]`. Verificación fresca: typecheck 0 errores + **176/176 tests pass en 403ms** (151 contados via grep, 25 adicionales via `it.each` confirmados por el runner) + build verde + D2.5 no tocó `transversal/*.py` ni `tests/anti_dory/*` (CI rojos persistentes siguen atribuibles a sprints previos). Cowork **firma DSC-G-008 v4** con el bullet de error path coverage explícito; las observaciones #1 (default DEV_USER_ROLE) y #2 (Supabase fail-loud) del audit D2 quedan cerradas materialmente por este delta.

---

## 1. Veredicto binario sobre los 10 puntos auditables (§3 del request)

| # | Punto | Veredicto | Evidencia binaria |
|---|---|---|---|
| 1 | H-1 default `'user'` en `env.ts` | 🟢 **SÍ** | `env.ts:73-75` `DEV_USER_ROLE: z.enum(["t1_alfredo", "t1_padre", "user"]).default("user")`. Línea 30 del docstring lo declara explícitamente: "default `user` (rol más restrictivo)". |
| 2 | H-1 HTTP 503 en producción | 🟢 **SÍ** | `auth.ts:51-61` `if (env.NODE_ENV === "production") return c.json({error: "[la-forja:auth_stub_disabled_in_production] D4 Google OAuth + Supabase Auth required"}, 503)`. La guard se ejecuta ANTES del check de header `x-user-id`. Imposible bypass por un atacante con UUID válido. |
| 3 | H-2 rollback tutor | 🟢 **SÍ** | `tutor.ts:147-157` `try { tutorResp = await invokeTutor(...) } catch (err) { await deps.budgetClient.adjustSpent(user.id, -c.var.budgetEstimated); throw err; }`. Rollback con valor negativo + re-throw para que la ruta retorne error semánticamente. |
| 4 | H-2 rollback magna | 🟢 **SÍ** | `tutor.ts:163-199` `if (body.requireValidation) { const magnaEstimated = await preCallCheck(...); try { ... await invokeMagnaValidation(...) ... } catch (err) { await deps.budgetClient.adjustSpent(user.id, -magnaEstimated); throw err; } }`. Reserve y rollback usan el MISMO estimado (no se mezcla con classifier ni tutor). |
| 5 | H-2 rollback sprints | 🟢 **SÍ** | `sprints.ts:101-116` `try { resp = await invokeSprintCopilot(...) } catch (err) { await deps.budgetClient.adjustSpent(user.id, -c.var.budgetEstimated); throw err; }`. Mismo patrón cohesivo con tutor. |
| 6 | H-3 classifier gate | 🟢 **SÍ** | `tutor.ts:108-135` ciclo completo: `const classifierEstimated = await preCallCheck(deps.budgetClient, user.id, "classifier", CLASSIFIER_MAX_INPUT, CLASSIFIER_MAX_OUTPUT)` → `classifyMessage()` con try/catch → `postCallCommit(..., "classifier", ..., classifierEstimated)`. El classifier cobra al cap igual que el tutor (DSC-LF-003 cumplido). |
| 7 | H-3 magna gate (sólo si requireValidation) | 🟢 **SÍ** | `tutor.ts:162-200` gate condicional `if (body.requireValidation)`. Si flag true: `preCallCheck("magna_validation", MAGNA_MAX_INPUT, MAGNA_MAX_OUTPUT)` → `invokeMagnaValidation()` con try/catch → `postCallCommit(..., "magna_validation", ..., magnaEstimated)`. Si flag false: sin reserva, sin commit, sin gasto. |
| 8 | H-4 SPRINT_STATES exacto §4:130 inglés | 🟢 **SÍ** | `sprints.ts:46-55` `SPRINT_STATES = ["proposed", "drafting", "review_alfredo", "review_cowork", "ready_to_execute", "executing", "merged", "canonized"] as const satisfies readonly string[]`. 8 elementos exactos en el orden SPEC §4:130. `SprintState = (typeof SPRINT_STATES)[number]` type-safe. `SPRINT_INITIAL_STATE = "proposed"`. Cero estados español residuales en el archivo. |
| 9 | H-5 production rejection en permissive | 🟢 **SÍ** | `env.ts:132-138` `if (parsed.NODE_ENV === "production") throw new Error("[la-forja:env_load_permissive_blocked_in_production] loadEnv({strict:false}) is forbidden when NODE_ENV=production. Use strict mode (default) so missing secrets fail loud.")`. Bloquea bypass accidental del Zod strict en deploys reales. |
| 10 | 6 tests nuevos D2.5 + 176/176 passing | 🟢 **SÍ** | `npm test` fresh hoy: **`Tests 176 passed (176)` en 403ms** sobre 12 test files. Delta vs D2 (170) = +6 tests. Verificación de los nuevos: `routes.test.ts:400 describe("D2.5 hardening — /api/tutor/chat (H-2 budget rollback + H-3 multi-mission gate)")` con tests específicos `routes.test.ts:480 H-2: si invokeTutor lanza, adjustSpent(-estimated) se llama para rollback` y `routes.test.ts:506 H-2: si invokeMagnaValidation lanza ... adjustSpent(-magnaEstimated) ejecuta rollback`. Asserts: `negativeCalls = client.adjustSpent.mock.calls.filter(call => call[1] < 0)`. |

---

## 2. Validación pre-commit reproducible (§4 del request)

Ejecutado fresh en este audit (cwd: `apps/la-forja/api`):

| Comando | Output | Veredicto |
|---|---|---|
| `npm run typecheck` | 0 errores TypeScript | ✅ |
| `npm test` | **176 passed (176) en 403ms** (12 test files) | ✅ |
| `npm run build` | `dist/` emitido sin errores | ✅ |

---

## 3. Atribución binaria de fallos CI (continuación del audit D2)

| Check | Estado | D2.5 tocó? |
|---|---|---|
| Lint & Type Check (transversal Sprint 58) | RED preexistente | `git diff --name-only 6401a3b..bdd9dbb \| grep "^transversal/"` → **0 hits**. D2.5 NO tocó. |
| Unit Tests (tests/anti_dory) | RED preexistente | `git diff --name-only 6401a3b..bdd9dbb \| grep "^tests/anti_dory/"` → **0 hits**. D2.5 NO tocó. |
| semgrep main desde 14-may | RED preexistente | Pre-existente desde antes del sprint. |

D2.5 no introdujo nuevos rojos. Atribución previa vigente.

---

## 4. DSC-G-008 v4 — Firma binaria del bullet adicional

Cowork firma **DSC-G-008 v4** como delta sobre v3 con el siguiente bullet canónico:

> **DSC-G-008 v4 — Error Path Coverage Obligatoria:**
> "Toda llamada LLM dentro de una ruta debe tener cobertura de error path: `try/catch` envolviendo la invocación, `adjustSpent(userId, -estimated)` rollback del budget reservado por `preCallCheck()` antes del re-throw, y tests que verifiquen `adjustSpent` con valor negativo cuando el LLM lanza. Sin error path coverage = budget leak = violación DSC-LF-003."

**Aplicación inmediata en D2.5:**
- ✅ `tutor.ts` cubre 3 llamadas LLM (classifier, tutor, magna_validation), cada una con try/catch + rollback negativo.
- ✅ `sprints.ts` cubre 1 llamada LLM (sprint_copilot) con try/catch + rollback negativo.
- ✅ `routes.test.ts:400-528` valida con `negativeCalls.filter(call => call[1] < 0)` que el rollback ocurre cuando el LLM lanza.

**Aplicación obligatoria en sprints futuros:**
- Cualquier nueva ruta que invoque un LLM debe seguir el mismo patrón.
- Audit Cowork DSC-G-008 v4 verifica binariamente:
  1. Cada `await invoke{Tutor,Rag,Classifier,SprintCopilot,MagnaValidation}` está dentro de `try { ... } catch (err) { ... await adjustSpent(userId, -<estimated>); throw err; }`.
  2. Existe al menos 1 test por ruta con asserción `negativeCalls.length >= 1` cuando se mockea el LLM con `vi.fn(() => { throw ... })`.
  3. El `<estimated>` del rollback coincide con el `<estimated>` del `preCallCheck()` previo (no se confunde entre misiones).

---

## 5. Observaciones D2 cerradas por D2.5

Las 5 observaciones register-only del audit D2 (commit `6401a3b`) tienen el siguiente estado tras D2.5:

| Obs D2 | Estado tras D2.5 |
|---|---|
| #1 `DEV_USER_ROLE` default `t1_alfredo` en producción | ✅ **CERRADO MATERIALMENTE** — default ahora `user` + guard production HTTP 503 |
| #2 `SupabaseBudgetClient` fail-loud hasta D5 | ✅ Defensive engineering vigente y correcto (sin cambios) |
| #3 Rate limit in-memory horizontal scaling | 📝 Sigue register-only D6 (no afecta D3) |
| #4 Brand engine outlier `manus_bridge.ts` paridad Python | 📝 Sigue register-only (paridad deliberada firmada) |
| #5 `getTelemetryClient()` singleton sin reset prod | 📝 Sigue register-only D5 swap point |

**Resultado:** las observaciones críticas del audit anterior (#1) quedan cerradas materialmente. Las 4 restantes son no-bloqueantes para D3 y trackeadas para D5/D6.

---

## 6. Decisión binaria sobre la solicitud (§6 del request)

| Pregunta | Veredicto |
|---|---|
| ¿Los 5 hallazgos materiales H-1 a H-5 quedan cerrados binariamente en `bdd9dbb`? | 🟢 **SÍ** (10/10 verificaciones en §1) |
| ¿Backend Hono sigue compleable, testeable, desplegable tras D2.5? | 🟢 **SÍ** (typecheck + 176 tests + build verde) |
| ¿DSC-G-008 v4 firmado con bullet error path coverage? | 🟢 **SÍ** (ver §4) |
| ¿D3 frontend Next.js queda autorizado sin reserva adicional? | 🟢 **SÍ** |

→ **4/4 SÍ. D3 desbloqueado.**

---

## 7. Reglas Duras del Monstruo — Compliance binario en D2.5

| Regla | Estado | Evidencia |
|---|---|---|
| #1 NO self-merge | ✅ | `bdd9dbb` en sprint branch, no en main |
| #2 calidad premium | ✅ | typecheck + 176 tests + build verde |
| #4 secretos sólo process.env | ✅ | sin cambios en mecanismo |
| #6 cero hardcodes | ✅ | sin cambios |
| #7 RLS desde nacimiento | ✅ | cero queries SQL contra forja_* (sin cambios) |
| #8 identidad auditable | ✅ | Manus E1 owner + Cowork audit + T1 dirige |
| DSC-G-004 cero genéricos | ✅ | sin cambios |
| DSC-S-016 anti-fabricación sin grep | ✅ | audit ejecutó `grep`, `git diff --name-only`, `npm test`, `npm run typecheck`, `npm run build`, `sed`, `Read` directo |
| LF-9 commits en sprint branch | ✅ | `bdd9dbb` en `sprint/la-forja-001`, 0 en main |
| **NUEVO** DSC-G-008 v4 error path coverage | ✅ | aplicado en 4 llamadas LLM (tutor, classifier, magna, sprint_copilot) con tests |

---

## 8. Consecuencias materiales si se aprueba D3

Si firmo VERDE D2.5 + autorizo D3:

1. **Cero cambio en `main`**: PR #133 sigue READY pendiente merge T1-Alfredo.
2. **D3 arranca**: Manus E1 escribe frontend Next.js 16.2 + Vercel AI SDK 6.0.27 sobre `apps/la-forja/web/`.
3. **DSC-G-008 v4 vigente**: cualquier nueva ruta D3+ que invoque LLM debe cumplir el bullet.
4. **Ventana de impersonación cerrada**: si Manus despliega un staging con `NODE_ENV=production` accidentalmente, el `forjaAuthStub` responde 503 globalmente. No hay UUID que abra el sistema.
5. **Budget leak cerrado**: errores de modelo no retienen dinero contra el cap. Tests aseguran rollback negativo.

Cero bombas en producción detectadas. Atribución CI rojos preexistentes vigente.

---

## 9. Firma DSC-G-008 v4 D2.5

```
SPRINT:           LA-FORJA-001 v3.2 — D2.5 HARDENING ADVERSARIAL
COMMIT:           bdd9dbb (sobre 6401a3b)
PR:               #133 (READY, mergeable=MERGEABLE)
AUDITOR:          Cowork T2-A (Claude Opus 4.7 / 1M context)
SESIÓN:           bold-neumann-ef6284
FECHA:            2026-05-15
METODOLOGÍA:      DSC-G-008 v4 audit DELTA D2.5 (firma del bullet error path coverage)
TYPECHECK:        ✅ 0 errores
TESTS:            ✅ 176/176 vitest en 403ms (12 files, +6 nuevos D2.5)
BUILD:            ✅ dist/ emitido
H-1 default:      ✅ user + 503 production
H-2 rollback:     ✅ tutor + magna + sprint_copilot
H-3 multi-gate:   ✅ classifier + magna preCallCheck/postCallCommit
H-4 SPEC §4:130:  ✅ 8 estados inglés exactos
H-5 strict prod:  ✅ permissive bloqueado en production
DSC-G-008 v4:     ✅ FIRMADO con bullet error path coverage
OBS D2 #1:        ✅ CERRADA materialmente
CI ROJOS:         ✅ los 3 siguen preexistentes (D2.5 no introduce nuevos)
PUNTOS 1-10:      ✅ 10/10 VERDE
DECISIONES 1-4:   ✅ 4/4 VERDE
```

🟢 **LA-FORJA-001 v3.2 — D2.5 DSC-G-008 v4 VERDE_FIRMADO · D3 AUTORIZADO**

---

## 10. Próximos pasos binarios

1. **Cowork (este turno)**: commit + push de este bridge.
2. **Manus E1**: arranca **D3 frontend ya** (Next.js 16.2 + Vercel AI SDK 6.0.27 + 4 páginas SPEC §5). Sin esperar nada.
3. **T1-Alfredo**: PR #133 sigue READY mergeable. Merge manual cuando D6 cierre, o instruye Cowork.
4. **D3 cierre**: Manus solicita D3_AUDIT_REQUEST con AC frontend específicos + verificación DSC-G-008 v4 en cada nueva ruta que invoque LLM.
5. **Trackear hallazgos H-6 a H-14 register-only** para D6 polish (no requieren acción D3).

Si surge contradicción binaria entre este audit y la realidad D3, prevalece la realidad. Este veredicto es firme.

— Cowork T2-A · LA-FORJA-001 v3.2 · D2.5 DSC-G-008 v4 VERDE · 15 mayo 2026
