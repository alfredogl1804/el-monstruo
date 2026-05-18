# BRIDGE — Cowork T2-A → Manus Ejecutor 2

**Date:** 2026-05-18
**From:** Cowork T2-A
**To:** Manus E2 (manus_hilo_b)
**Sprint:** **D4-PROD-AUTH-001** — activar Google OAuth real en Railway producción
**Status:** 🟢 **D6 DECLARADO** + **D4-PROD-AUTH-001 FIRMADO + KICKOFF**

---

## §0 TL;DR binario

**D6 LA-FORJA-001 cerrado formalmente:** 🏛️ DECLARADO con audit Cowork DSC-G-008 v4 VERDE 6/6 sobre cadena PRs #157+#159+#160+#161 (smoke C2 HTTP binario validado).

**Próximo sprint firmado:** **D4-PROD-AUTH-001** — activar OAuth Google real en Railway. **NO requiere código adicional** (todo está en main desde DSC-LF-009). Solo activación operativa: T1 setea env vars + tú ejecutas smoke E2E.

---

## §1 D6 — frase canónica emitida

> **🏛️ LA-FORJA-001 D6 — DECLARADO**

Audit completo en mi turno anterior. Cadena de PRs `15cfe83 → 6ff8542 → 754ebc4 → 586a267` verificada binariamente en `origin/main`. Smoke C2 (`/health` 200 + `/api/*` 503 canónico) prueba: ESM Node 22 funcional + Hono routing + middleware activo + `loadEnv()` correctamente + JSON limpio.

3 tickets follow-up D5.3 status:
- ✅ #148 cost-per-thread cerrado en PR #160
- ⏳ #149 budget.ts doc header (pendiente, tu cola post-T6)
- ⏳ #154 ensureThread metadata (pendiente, tu cola post-T6)

---

## §2 D4-PROD-AUTH-001 — spec firmado

**Path:** [`bridge/sprints_propuestos/sprint_D4_PROD_AUTH_001_FIRMADO_2026_05_18.md`](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/sprints_propuestos/sprint_D4_PROD_AUTH_001_FIRMADO_2026_05_18.md) (commit `a2ce8e9c`, 11.7KB, 12 secciones binarias).

### §2.1 Objetivo magno

Transformar `la-forja-api` de "503 stub disabled" a "OAuth Google funcional + smoke E2E real". **Cero código tocado** — solo setup operativo.

### §2.2 División de owners

| Owner | Tareas |
|---|---|
| **T1 (Alfredo)** | Google Cloud Console OAuth client + Railway env vars (3 nuevas) |
| **Manus E2 (tú)** | Smoke C3 E2E post-redeploy + 4 SQL queries verificación + bridge cierre |
| **Cowork T2-A (yo)** | Audit final DSC-G-008 v4 + frase canónica cierre |

---

## §3 Tu trabajo concreto (Manus E2)

### §3.1 Esperar señal T1

T1 hace setup operativo (~30-60min):
1. Crea OAuth 2.0 client en Google Cloud Console
2. Setea Railway env vars production: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `OAUTH_CALLBACK_URL` (+ JWT_SECRET si faltaba)
3. Dispara redeploy `la-forja-api`

Cuando T1 confirme "Railway env vars seteadas + redeploy SUCCESS", arrancas.

### §3.2 Smoke C3 E2E binario

Ejecuta los 4 bloques §7 del spec:

**§7.1 Pre-login (sin cookie):**
```bash
curl -i https://la-forja-api-production.up.railway.app/api/sprints/states
# Esperado: HTTP 401 (no más 503)
```

**§7.2 Auth flow Google redirect:**
```bash
curl -I https://la-forja-api-production.up.railway.app/api/auth/google
# Esperado: 302 Location: accounts.google.com/o/oauth2/v2/auth
```

**§7.3 Post-login con cookie real (T1 hace browser login manual):**
```bash
curl -i -b "la-forja_session=<jwt-real>" \
  https://la-forja-api-production.up.railway.app/api/sprints/states
# Esperado: HTTP 200 + JSON 8 estados
```

**§7.4 Tutor chat E2E:**
```bash
curl -X POST https://la-forja-api-production.up.railway.app/api/tutor/chat \
  -H "Content-Type: application/json" \
  -b "la-forja_session=<jwt-real>" \
  -d '{"messages":[{"role":"user","content":"Hola, ¿cómo funciona La Forja?"}],"mode":"normal","requireValidation":false}'
# Esperado: text/event-stream con tokens reales del tutor Claude Opus 4.7
```

### §3.3 Verificación binaria persistencia post-smoke

Ejecuta 4 SQL queries (§7.5 spec) — esto cierra binariamente el ciclo D5.2 + D5.3 + #148:

```sql
-- M1: cost_usd > 0 binariamente (valida #148 fix con tráfico real)
SELECT COUNT(*) FROM forja_messages WHERE role='assistant' AND cost_usd > 0;
-- Esperado post-smoke: ≥1 (transición histórica de 0 → > 0)

-- M2: thread total_usd agregado correctamente
SELECT COUNT(*), SUM(total_usd) FROM forja_threads WHERE message_count > 0;
-- Esperado: COUNT ≥1, SUM > 0

-- M3: profile google_sub real (no dev-stub:)
SELECT google_sub, email FROM forja_profiles ORDER BY created_at DESC LIMIT 1;
-- Esperado: sub numérico real Google, email T1, NO prefix "dev-stub:"

-- M4: telemetry registra eventos del E2E
SELECT event, COUNT(*) FROM forja_telemetry GROUP BY event;
-- Esperado: ≥1 evento
```

### §3.4 Bridge cierre

Path: `bridge/manus_to_cowork_LA_FORJA_001_D4_PROD_AUTH_RESULT_2026_05_18.md`

Estructura mínima:
- 4 bloques smoke C3 con outputs verbatim
- 4 SQL queries con resultados binarios
- Snapshot forense post-smoke en `discovery_forense/INCIDENTES/D4_PROD_AUTH_smoke_e2e_<fecha>.json` (con filas reales evidencia)
- 11/11 acceptance criteria verificados
- Veredicto VERDE / AMARILLO / ROJO

---

## §4 Acceptance criteria binarios (11 total)

Verbatim §4 del spec firmado:
1. Railway env vars seteadas + redeploy SUCCESS
2. Deployment status RUNNING
3. `/health` sigue 200
4. `/api/sprints/states` sin cookie → 401 (no 503)
5. `/api/auth/google` → 302 redirect Google
6. Login E2E manual T1 → cookie `la-forja_session` válida
7. `/api/sprints/states` con cookie → 200
8. `/api/tutor/chat` con cookie → stream funcional
9. `forja_messages.cost_usd > 0` ≥1 fila
10. `forja_threads.total_usd > 0` ≥1 thread
11. `forja_telemetry` evento del E2E

---

## §5 NO-CRUCE reglas duras (§9 spec)

- ❌ NO modificar código en `apps/la-forja/api/src/` (todo el wiring D4 ya está en main)
- ❌ NO crear migrations nuevas (schema D5.1 soporta google_sub real)
- ❌ NO touch `forja_budget` source-of-truth
- ❌ NO modificar Dockerfile (D6 builder OK)
- ❌ NO interferir con otros 3 hilos Manus paralelos:
  - E1 Anti-Dory D6 Railway flag permanente
  - E2 (tú) VERIFICADOR-001 standby T6 (en worktree dedicada)
  - Catastro hilo activo
- ✅ SÍ ejecutas smoke E2E + bridge cierre

---

## §6 Tu cola Cowork pendiente — orden recomendado

Antes de avanzar D4-PROD-AUTH-001, tienes 3 PRs en cola Cowork:

| PR | Status | Prioridad |
|---|---|---|
| **#155** H15 pytest pythonpath | esperando audit Cowork | **1° destrabea CI verde sistémico** |
| **#158** H17 sqlglot deps | esperando audit Cowork | **2° destrabea CI verde end-to-end** |
| **#153** D5.3 RPC atómico (cierra #149) | esperando audit + apply migration 0050 | **3° (post #155+#158)** |

Recomendación: **mientras T1 hace setup D4-PROD-AUTH-001 (~30-60min), yo Cowork audito #155 + #158 + #153 en paralelo.** Eso destrabea CI verde para futuros PRs incluso antes que tú arranques smoke E2E.

---

## §7 Estado consolidado paralelo

```
Hilos activos:
  🟢 Manus E1   — D6 Anti-Dory Railway flag permanente (Pieza 1 cross-agente)
  🟢 Manus E2 (tú) — VERIFICADOR-001 worktree dedicada (standby T6 mañana ~07:24 UTC)
                  + D4-PROD-AUTH-001 smoke E2E (post-setup T1)
  🟢 Manus Catastro — CATASTRO-WIRING-001 DECLARADO (mini-PR a6be791 en branch)
  🟢 Cowork T2-A — cola 3 PRs (#155 #158 #153) + audit D4-PROD-AUTH-001 final

Sprints en pipeline:
  🏛️ D6 LA-FORJA — DECLARADO
  🏛️ CATASTRO-WIRING-001 — DECLARADO
  🟢 D4-PROD-AUTH-001 — FIRMADO + KICKOFF (este bridge)
  🟡 MANUS-ANTI-DORY-003 v0.2 — pendiente refactor a EXPERIMENTO (3/3 Sabios convergen)
  ⏳ T6 S-EMBRION-009 — madurando 24h
```

---

## §8 Cadencia esperada

- **T+0 (HOY ~08:50 UTC):** spec firmado + bridge enviado (este doc)
- **T+30-60min:** T1 completa setup Google Cloud + Railway env vars
- **T+1-2h:** redeploy SUCCESS + tú smoke E2E + 4 SQL queries
- **T+2-3h:** bridge cierre + Cowork audit DSC-G-008 v4 final + frase canónica

🏛️ **D4-PROD-AUTH-001 — DECLARADO** post-audit verde.

---

**Status:** `🟢 FIRMADO + KICKOFF — espera setup T1, después tu turno`
**Cowork T2-A firma bajo autorización T1 magna "adelante con spec D4-PROD-AUTH-001 + bridge a Manus E2" verbatim 2026-05-18.**

**Sources:**
- [Spec D4-PROD-AUTH-001 firmado](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/sprints_propuestos/sprint_D4_PROD_AUTH_001_FIRMADO_2026_05_18.md)
- [Bridge D6 DEPLOY DONE Manus E2](https://github.com/alfredogl1804/el-monstruo/commit/a18e843)
- [DSC-LF-009 D4 código mergeado](https://github.com/alfredogl1804/el-monstruo/blob/main/discovery_forense/CAPILLA_DECISIONES/LA-FORJA/DSC-LF-009_d4_google_oauth_jwt_signoff.md)
- DSC-X-003 Manus-Oauth pattern (referencia previa)
