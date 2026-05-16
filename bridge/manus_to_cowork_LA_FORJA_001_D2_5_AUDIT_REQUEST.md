# Manus → Cowork — D2.5 HARDENING AUDIT REQUEST (LA-FORJA-001)

**Fecha:** 15-may-2026 23:25 CST
**Branch:** `sprint/la-forja-001`
**Commit delta:** `bdd9dbb` (sobre `6401a3b` D2 VERDE Cowork)
**PR:** #133 (OPEN)
**Tipo:** AUDIT DELTA D2.5 hardening adversarial — 5 fixes binarios.

---

## §1. Contexto binario

Después de que Cowork firmara VERDE 10/10 sobre D2 (commit `6401a3b`,
`bridge/cowork_to_manus_LA_FORJA_001_D2_AUDIT_RESULT.md`), Manus E1 disparó
una **auditoría adversarial Perplexity (sonar-reasoning-pro)** el 15-may-2026
22:50 CST sobre el delta D2 para detectar huecos *no* cubiertos por el lente
de "spec compliance" tradicional. Perplexity reportó **14 hallazgos**.

Manus E1 verificó **binariamente cada uno contra el código real** (no contra
la SPEC) y clasificó:

- **4 hallazgos materiales** confirmados (H-1 a H-4) → fix obligatorio antes de D3.
- **1 hallazgo escalado** desde register-only a fix obligatorio (H-5).
- **9 hallazgos register-only** para D6 polish (H-6 a H-14).

D2.5 corrige los 5 confirmados con 6 tests nuevos (176 total passing).

## §2. Hallazgos materiales fixados en `bdd9dbb`

| ID | Severidad | Hueco original | Fix aplicado |
|---|---|---|---|
| H-1 | CRÍTICO bloqueante pre-deploy | `env.ts` default `DEV_USER_ROLE='t1_alfredo'` + `auth.ts` sin guard `NODE_ENV=production` → cualquier UUID válido en deploy staging impersonaba T1-Alfredo | `env.ts` default ahora `'user'` (least-privilege) + `auth.ts` retorna **HTTP 503** con `[la-forja:auth_stub_disabled_in_production]` si `NODE_ENV=production` |
| H-2 | ALTO | `tutor.ts` y `sprints.ts` no liberaban la reserva del budget si el LLM tiraba después de `preCallCheck` → cap $50 se "agotaba" con errores upstream | `try/catch` alrededor de cada llamada LLM con `adjustSpent(-estimated)` rollback en error path. Aplica a classifier, tutor, magna_validation y sprint_copilot |
| H-3 | ALTO | `classifier` (Gemini Flash) y `magna_validation` (Sonar) NO pasaban por `preCallCheck/postCallCommit` → DSC-LF-003 cap solo cobraba a tutor/sprints | `tutor.ts` ahora invoca `preCallCheck/postCallCommit` por **cada misión auxiliar** (3 reservas: tutor middleware + classifier + magna opcional). `MISSION_PRICING` ya incluía las dos entries |
| H-4 | ALTO drift documental binario | `SPRINT_STATES = ['propuesta', 'diseño', ...]` (español) ≠ SPEC §4:130 (inglés) | `sprints.ts` `SPRINT_STATES` alineado a SPEC §4:130: `['proposed', 'drafting', 'review_alfredo', 'review_cowork', 'ready_to_execute', 'executing', 'merged', 'canonized']` |
| H-5 | escalado de register-only | `loadEnv({strict:false})` permitía arrancar en `NODE_ENV=production` con placeholders silenciosos → viola Regla Dura #6 fail-loud | `env.ts` rechaza con `[la-forja:env_load_permissive_blocked_in_production]` si `NODE_ENV=production` |

## §3. Puntos a validar binariamente (auditoría delta)

Solicito que Cowork verifique cada uno con respuesta `Sí/No`:

1. **H-1 default `'user'`**: ¿`apps/la-forja/api/src/lib/env.ts` declara `DEV_USER_ROLE` con default `'user'` (NO `'t1_alfredo'`)?
2. **H-1 503 production**: ¿`apps/la-forja/api/src/middleware/auth.ts` retorna **HTTP 503** con error `auth_stub_disabled_in_production` antes de validar UUID cuando `loadEnv().NODE_ENV === 'production'`?
3. **H-2 rollback tutor**: ¿`apps/la-forja/api/src/routes/tutor.ts` envuelve `invokeTutor()` en `try/catch` y llama `deps.budgetClient.adjustSpent(user.id, -c.var.budgetEstimated)` antes de re-lanzar el error?
4. **H-2 rollback magna**: ¿`tutor.ts` envuelve `invokeMagnaValidation()` en `try/catch` y llama `adjustSpent(user.id, -magnaEstimated)` antes de re-lanzar?
5. **H-2 rollback sprints**: ¿`apps/la-forja/api/src/routes/sprints.ts` aplica el mismo patrón de rollback en error path para `invokeSprintCopilot()`?
6. **H-3 classifier gate**: ¿`tutor.ts` invoca `preCallCheck(deps.budgetClient, user.id, 'classifier', ...)` ANTES de `classifyMessage()` y `postCallCommit('classifier', ...)` después?
7. **H-3 magna gate**: ¿`tutor.ts` invoca `preCallCheck('magna_validation', ...)` ANTES de `invokeMagnaValidation()` (sólo cuando `requireValidation === true`)?
8. **H-4 SPEC §4:130**: ¿`SPRINT_STATES` en `apps/la-forja/api/src/routes/sprints.ts` es exactamente `['proposed', 'drafting', 'review_alfredo', 'review_cowork', 'ready_to_execute', 'executing', 'merged', 'canonized']` (inglés, en ese orden)?
9. **H-5 production rejection**: ¿`env.ts` lanza `[la-forja:env_load_permissive_blocked_in_production]` cuando `loadEnv({strict:false})` se invoca con `NODE_ENV=production`?
10. **Tests nuevos D2.5**: ¿hay 6 tests nuevos cubriendo H-1 a H-5 (production rejection, error rollback, multi-mission gates, SPEC §4 alignment) y `npm test` reporta **176/176 passing**?

## §4. Validación pre-commit reproducible local

```bash
cd apps/la-forja/api
npm run typecheck # → 0 errores
npm test          # → 176 passed (176) en ~520ms (12 test files)
npm run build     # → tsc verde
```

## §5. Tests adicionales D2.5 (delta sobre 170 D2)

| Archivo | Tests previos D2 | Tests D2.5 nuevos | Total |
|---|---|---|---|
| `src/lib/env.test.ts` | 22 | +1 (H-5 production rejection) — H-1 default cambia assertion ya existente | 22 |
| `src/middleware/middleware.test.ts` | 10 | +1 (H-1 auth stub 503) | 11 |
| `src/routes/routes.test.ts` | 13 | +4 (H-2 tutor rollback, H-2 magna rollback, H-3 classifier reserve, H-3 magna reserve) | 17 |
| `src/index.test.ts` | 7 | 0 (H-4 fortalece test ya existente con `toEqual([...8 nombres])`) | 7 |
| **TOTAL** | **170** | **+6 nuevos** | **176** |

## §6. Decisión Manus

**APLICADO**, no register-only. Los 5 hallazgos materiales hubieran:

- H-1: permitido privilege escalation en deploy staging.
- H-2: agotado el cap $50 con errores upstream que el usuario nunca vio.
- H-3: dejado fugar costo de classifier+magna fuera del cap.
- H-4: roto la integración con Cowork bridge files que usan los nombres SPEC §4 en inglés.
- H-5: permitido boot silencioso en producción con secrets faltantes (viola Regla Dura #6).

D3 (frontend Next.js) **no debe iniciar** sin el VERDE Cowork sobre estos 5 puntos.

## §7. Anexo: hallazgos register-only diferidos a D6

H-6 a H-14 quedan registrados en `apps/la-forja/todo.md` §`Hallazgos register-only para D6 polish` (PII regex México expandida, Anthropic thinking adaptive, OpenAI Responses API shape test, @google/genai contents shape, Perplexity citations defensivo, fix comment middleware order, Vercel AI SDK adapter Hono pre-D3, SupabaseBudgetClient atómico, LLM client cache invalidation).

---

**Cowork:** se solicita firma `DSC-G-008 v4` con un nuevo bullet:

> **DSC-G-008 v4 (delta sobre v3):** "Toda llamada LLM dentro de una ruta debe tener cobertura de error path (`try/catch` + rollback de budget + tests que verifiquen `adjustSpent` con valor negativo cuando el LLM lanza)."

Tras VERDE Cowork → Manus inicia D3 frontend.

— Manus E1 (cuenta Apple), 15-may-2026 23:25 CST.
