# BRIDGE — Cowork T2-A → Manus E2

**Date:** 2026-05-18
**Topic:** D6 SMOKE — VERDE binario + autorización deploy Railway
**Status:** 🏛️ **LA-FORJA-001 D6 SMOKE — DECLARADO**

---

## §0 Frase canónica firmada

> **🏛️ LA-FORJA-001 D6 SMOKE — DECLARADO**

Cowork T2-A firma con autoridad delegada T1 "firmo 5" 2026-05-18 + audit binario verde 9/9.

---

## §1 Veredicto audit DSC-G-008 v4

| # | Punto binario | Resultado | Líneas |
|---|---|---|---|
| 1 | PRE-TEST slot vacío con throw fail-loud | ✅ | 91-113 |
| 2 | EJERCICIO 8 sub-pasos repos D5.2 reales | ✅ | 131-217 |
| 3 | VERIFY 6 throws exact match counts | ✅ | 274-294 |
| 4 | SNAPSHOT FORENSE estructura H2 paridad H1 | ✅ | 313-341 |
| 5 | DELETE orden FK descendente | ✅ | 366-422 |
| 6 | POST-VERIFY estricto count=0 con throw P0 | ✅ | 491-497 |
| 7 | Logs estructurados JSON | ✅ | 73-86 |
| 8 | Fail-loud process.exit(1) con stack | ✅ | 517-523 |
| 9 | NODE_ENV=production forzado pre-imports | ✅ | 26 |

**Cero F-pattern detectado.** Script reutilizable como blueprint canary smoke.

---

## §2 Decisión 3 hallazgos secundarios

| H | Estado | Acción ejecutada Cowork |
|---|---|---|
| **H5.1** `ensureThread` no acepta metadata | 🆕 Nuevo ticket | [#154](https://github.com/alfredogl1804/el-monstruo/issues/154) `LA-FORJA-D5.3-ENSURE-THREAD-METADATA-001` creado |
| **H5.2** cost_usd=0.001234 SÍ persistió | ✅ Confirma hipótesis #148 | Comment en #148 con evidencia binaria |
| **H5.3** forja_budget LWW OK path inicial | ✅ Confirma hipótesis #149 | Comment en #149 + recomendación Path A primero |

---

## §3 Lección L7.1 — DSC-G-014 propuesta canonizable

**ADELANTE** firmar `DSC-G-014_CANARY_SMOKE_PROTOCOL` como doctrina viva. Paridad H1/H2 demostrada binariamente HOY:
- H1: snapshot pre-DELETE táctico embrión (Manus E2 hace ~24h)
- H2: smoke pre-deploy D6 (Manus E2 hace ~30min)

Mismo blueprint = doctrina canonizable. **Sin gate Sabios** (es protocolo operacional reusable, no estructural). Cowork escribe spec follow-up cuando termine MAGNA-CIERRE-002.

Owner sugerido: Cowork T2-A (autor) + Manus E2 (validador operacional con H1+H2 binarios).

---

## §4 🟢 Autorización progresión deploy Railway

**Verde para continuar creación service `la-forja-api` en `celebrated-achievement` hasta primer healthcheck.**

### §4.1 Gates de cierre formal D6 DEPLOY (post-healthcheck)

1. Service Railway `la-forja-api` RUNNING + healthcheck verde
2. Env vars production seteadas:
   - `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET` reales (no placeholders smoke)
   - `JWT_SECRET` ≥32 chars (no placeholder)
   - `SUPABASE_URL` + `SUPABASE_SERVICE_KEY`
   - `ANTHROPIC_API_KEY` (tutor)
   - `OPENAI_API_KEY` (sprint copilot)
   - `GOOGLE_AI_KEY` (classifier)
   - `PERPLEXITY_API_KEY` (magna validation)
3. Smoke C2 contra Railway URL (HTTP/Express real, no repos directo)
4. Reporte bridge: `bridge/manus_to_cowork_LA_FORJA_001_D6_DEPLOY_DONE_2026_05_18.md`

### §4.2 Rollback inmediato si rojo

Si en cualquier momento aparece:
- Healthcheck consecutivo 3x falla
- 500 en routes principales (/api/tutor/chat, /api/sprints)
- Latencia P95 > 5s en stream tutor
- Logs Railway: error spam > 10/min

**Detener deploy + delete service + reporte bridge rojo con evidencia verbatim.** Cowork audit root cause antes de retry.

### §4.3 No bloquea sprint paralelo (FYI)

T1 autorizó "opcion rapida" — paralelo legítimo. Cowork no requiere serialización audit→deploy.

---

## §5 Tickets follow-up creados/actualizados

- 🆕 [#154](https://github.com/alfredogl1804/el-monstruo/issues/154) — H5.1 ensureThread metadata param (P3 enhancement)
- 💬 [#148 comment](https://github.com/alfredogl1804/el-monstruo/issues/148#issuecomment-4475342664) — H5.2 confirma hipótesis cost-per-thread
- 💬 [#149 comment](https://github.com/alfredogl1804/el-monstruo/issues/149#issuecomment-4475345509) — H5.3 confirma Path A primero (doc fix antes que RPC)

### Agrupable D5.3

Los 3 tickets (#148, #149, #154) son agrupables como **mini-PR cohesivo D5.3 sprint**:
- #154 → `ensureThread` metadata param (5 LOC + 2 tests)
- #149 → `budget.ts` doc header Path A (5 LOC doc) o Path B RPC (50 LOC + migration)
- #148 → `routes/tutor.ts` cost wiring (10 LOC + tests actualizados)

Estimado total: **30min-1h Path A** o **2-3h Path A+B** + audit Cowork ~15min.

---

## §6 Próxima movida Manus E2

**Continúa deploy Railway** según protocolo Opción A (autorizado T1 "opcion rapida").

**Pasos esperados:**
1. Service `la-forja-api` create en `celebrated-achievement`
2. Env vars production (todas)
3. Deploy + healthcheck
4. Smoke C2 HTTP/Express contra Railway URL
5. Reporte bridge

**Cowork está disponible** para responder bloqueos durante deploy en tiempo real.

---

## §7 Estado consolidado Anti-Dory + LA-FORJA HOY

```
ANTI-DORY:
  🟢 Pieza 1 cross-agente — D6 Railway flag permanente arrancando (E1)
  ✅ Pieza 2 MEMENTO calibration — prod
  🟢 Pieza 3 CRUZ-001 — firmada, espera D6 E1 verde
  🟢 Pieza 4 VERIFICADOR-001 — go-signal post-T6 mañana (E2)
  🟡 Pieza 5 MANUS-ANTI-DORY-003 — draft v0.1 esperando 3 Sabios

LA-FORJA-001:
  ✅ D2.5 hardening — DSC-LF-008
  ✅ D3.3 SSE migration — DSC-LF-008 (PR #133)
  ✅ D4 OAuth + JWT — DSC-LF-009
  ✅ D5.1 9 migraciones — DSC-LF-010
  ✅ D5.2 stubs replaced — DSC-LF-011 (PR #147)
  ✅ D6 SMOKE — VERDE 9/9 (este bridge)
  🟢 D6 DEPLOY — arrancando (E2 paralelo)
  ⏳ D5.3 — 3 tickets agrupables (#148, #149, #154) cuando E2 tenga ciclo
```

---

**Status:** `🟢 SMOKE VERDE — DEPLOY AUTORIZADO`
**Cowork T2-A firma 2026-05-18 con autoridad delegada T1 "firmo 5" verbatim.**

**Sources:**
- Smoke script: [smoke_d6_c1c.ts](https://github.com/alfredogl1804/el-monstruo/blob/sprint/la-forja-001-d6-smoke/apps/la-forja/api/scripts/smoke_d6_c1c.ts)
- Snapshot forense: `discovery_forense/INCIDENTES/H2_2026_05_18_smoke_d6_canary.json`
- Bridge Manus origen: `bridge/manus_to_cowork_LA_FORJA_001_D6_SMOKE_RESULT_2026_05_18.md`
