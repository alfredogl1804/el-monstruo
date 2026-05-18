---
sprint_id: D4-PROD-AUTH-001
version: v1
titulo: LA-FORJA-001 D4 PROD — Activar Google OAuth real en Railway producción
estado: 🟢 FIRMADO — Cowork T2-A bajo autorización T1 magna "adelante con spec D4-PROD-AUTH-001 + bridge a Manus E2" verbatim 2026-05-18
autor_spec: Cowork T2-A
fecha_firma: 2026-05-18
owner_setup: T1 (Alfredo — credenciales Google OAuth + Railway env vars)
owner_validacion: Manus E2 (smoke E2E + verificación binaria persistencia D5.2/D5.3 con tráfico real)
gate_arranque: este spec firmado + credenciales Google OAuth obtenidas
hermanos_doctrinales: DSC-LF-009 (D4 código mergeado), DSC-LF-011 (D5.2 persistencia), DSC-G-008 v4 (audit)
post_dependencia: LA-FORJA-001 D6 DECLARADO (cadena PRs #157+#159+#160+#161 en main)
---

# Sprint D4-PROD-AUTH-001 — Activar Google OAuth real en Railway producción

> **Objetivo magno:** transformar la-forja-api de "service UP con 503 stub disabled" a "service UP con OAuth Google real funcional + smoke E2E completo". **NO requiere código adicional** — todo el wiring D4 ya está en main desde DSC-LF-009. Solo activación operativa.

## §1 Contexto binario post-D6

D6 declarado HOY (Cowork T2-A firma 2026-05-18). Smoke C2 binario confirmó:
- `GET /health` → 200 ✅
- `GET /api/sprints/states` → **503** `[la-forja:auth_stub_disabled_in_production]`
- `GET /api/puertas` → **503** idem

El 503 es **comportamiento correcto** (D2.5 H-1 hardening + `forjaAuthSelector` discrimina NODE_ENV binario). Falta solo **activar OAuth real Google** para que `forjaAuthGoogle` middleware reemplace al stub.

## §2 Objetivo binario

Post-sprint, los endpoints `/api/sprints/states`, `/api/puertas`, `/api/tutor/chat` deben:
- HTTP 401 si no hay cookie `la-forja_session` válida (en vez de 503 stub)
- HTTP 200 con respuesta válida si login Google completado correctamente
- Persistencia D5.2/D5.3 funcionando con tráfico real (filas en `forja_*` tablas, cost_usd > 0)

## §3 Pre-requisitos T1 (Alfredo setup operativo)

### §3.1 Google Cloud Console — OAuth 2.0 Client

T1 debe crear/obtener:
- **Client ID:** formato `*.apps.googleusercontent.com`
- **Client Secret:** formato `GOCSPX-*`
- **Authorized redirect URI:** `https://la-forja-api-production.up.railway.app/api/auth/google/callback` (verificar path exacto en `apps/la-forja/api/src/routes/auth.ts`)
- **Authorized JavaScript origins:** `https://la-forja-api-production.up.railway.app`

Si T1 ya tiene un OAuth client del Monstruo (DSC-X-003 Manus-Oauth pattern), puede reusar o crear uno dedicado LA-FORJA.

### §3.2 JWT_SECRET — verificar/setear

- Requerimiento: ≥32 chars (verificado en `apps/la-forja/api/src/lib/jwt.ts`)
- Si ya está seteado en Railway env vars production → reusar
- Si NO está seteado → generar via `openssl rand -base64 48 | tr -d '/+=' | head -c 64`

### §3.3 Railway env vars production setup

```bash
# Setear en Railway dashboard (service la-forja-api, environment production)
GOOGLE_OAUTH_CLIENT_ID=<real-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<real-client-secret>
JWT_SECRET=<≥32-chars-secret>  # si no estaba
OAUTH_CALLBACK_URL=https://la-forja-api-production.up.railway.app/api/auth/google/callback
```

Verificar nombres exactos contra `apps/la-forja/api/src/lib/env.ts` (EnvSchema superRefine production-required).

## §4 Acceptance criteria binarios

| # | Check | Comando / método |
|---|---|---|
| 1 | Railway env vars seteadas + redeploy | `railway variables --service la-forja-api --environment production` lista las 3 vars |
| 2 | Service redeploy SUCCESS | Deployment status en Railway dashboard |
| 3 | `GET /health` sigue 200 | `curl https://la-forja-api-production.up.railway.app/health` |
| 4 | `GET /api/sprints/states` sin cookie → 401 (no 503) | `curl ...` → debe ser 401 con error namespaced `[la-forja:unauthenticated]` o similar |
| 5 | `GET /api/auth/google` redirect 302 a Google | `curl -I` → location header con `accounts.google.com/o/oauth2/v2/auth` |
| 6 | Login E2E manual: T1 navega a `/api/auth/google`, completa login Google, vuelve con cookie `la-forja_session` | Browser session manual |
| 7 | `GET /api/sprints/states` con cookie → 200 | post-login |
| 8 | `POST /api/tutor/chat` con cookie → stream funcional | E2E real |
| 9 | Filas reales aparecen en `forja_messages` con `cost_usd > 0` | SQL post-smoke: `SELECT COUNT(*) FROM forja_messages WHERE cost_usd > 0` ≥1 |
| 10 | Filas reales en `forja_threads` con `total_usd > 0` | SQL post-smoke |
| 11 | `forja_telemetry` registra eventos del flow E2E | SQL post-smoke |

## §5 Archivos esperados a tocar

**NO TOCAR código** — todo el wiring D4 está en main:
- ❌ `apps/la-forja/api/src/routes/auth.ts`
- ❌ `apps/la-forja/api/src/middleware/auth.ts`
- ❌ `apps/la-forja/api/src/lib/jwt.ts`
- ❌ `apps/la-forja/api/src/lib/env.ts`

**SÍ TOCAR (infra Railway only):**
- ✅ Railway env vars production (T1 manual via dashboard o `railway` CLI)
- ✅ Google Cloud Console OAuth client (T1 manual)

**SÍ ESCRIBIR (reportes Manus E2):**
- ✅ `bridge/manus_to_cowork_LA_FORJA_001_D4_PROD_AUTH_RESULT_2026_05_18.md`
- ✅ `discovery_forense/INCIDENTES/D4_PROD_AUTH_smoke_e2e_<fecha>.json` (snapshot post-smoke E2E con filas reales evidencia)

## §6 Pre-flight checks obligatorios

```bash
# 1. Verificar HEAD main es post-D6 (debe contener PRs #157+#159+#160+#161)
git log origin/main --oneline | head -10
# Esperado: incluye 586a267 (#161 ESM dynamic) + 754ebc4 (#160 cost) + 6ff8542 (#159 ESM v1) + 15cfe83 (#157 smoke)

# 2. Verificar env vars Railway pre-cambio (snapshot pre-fix)
railway variables --service la-forja-api --environment production | grep -E "GOOGLE_OAUTH|JWT_SECRET|OAUTH_CALLBACK"
# Esperado pre-sprint: faltan GOOGLE_OAUTH_* o están placeholder

# 3. Verificar service la-forja-api UP pre-cambio
curl -s https://la-forja-api-production.up.railway.app/health | jq .status
# Esperado: "ok"

# 4. Coherence Gate Nivel A DSC-G-013 v0.1 (no aplica acción magna SQL — skip)
```

## §7 Smoke E2E binario (post-redeploy)

### §7.1 Pre-login (sin cookie)

```bash
curl -i https://la-forja-api-production.up.railway.app/api/sprints/states
# Esperado: HTTP 401 (no 503)
```

### §7.2 Auth flow Google

```bash
curl -I https://la-forja-api-production.up.railway.app/api/auth/google
# Esperado: 302 Location: https://accounts.google.com/o/oauth2/v2/auth?...
```

T1 navega manualmente en browser, completa login Google, recibe cookie.

### §7.3 Post-login con cookie

```bash
curl -i -b "la-forja_session=<jwt-real>" \
  https://la-forja-api-production.up.railway.app/api/sprints/states
# Esperado: HTTP 200 + JSON con 8 estados sprint
```

### §7.4 Tutor chat E2E

```bash
curl -X POST https://la-forja-api-production.up.railway.app/api/tutor/chat \
  -H "Content-Type: application/json" \
  -b "la-forja_session=<jwt-real>" \
  -d '{
    "messages": [{"role": "user", "content": "Hola, ¿cómo funciona La Forja?"}],
    "mode": "normal",
    "requireValidation": false
  }'
# Esperado: text/event-stream con tokens del tutor
```

### §7.5 Verificación binaria persistencia post-smoke

```sql
-- M1: forja_messages.cost_usd > 0 (#148 fix validation)
SELECT COUNT(*) FROM forja_messages WHERE role='assistant' AND cost_usd > 0;
-- Esperado post-smoke: ≥1

-- M2: forja_threads.total_usd agregado
SELECT COUNT(*), SUM(total_usd) FROM forja_threads WHERE message_count > 0;
-- Esperado: COUNT ≥1, SUM > 0

-- M3: forja_profiles tiene el google_sub real (no dev-stub:)
SELECT google_sub, email FROM forja_profiles ORDER BY created_at DESC LIMIT 1;
-- Esperado: google_sub sin prefix "dev-stub:" (sub real numérico Google)

-- M4: forja_telemetry registra eventos
SELECT event, COUNT(*) FROM forja_telemetry GROUP BY event;
-- Esperado: ≥1 evento (puede ser confusion_detected, completion_signal, o other según mensaje)
```

## §8 Limitaciones declaradas (DSC-G-008 v3 §4)

| Id | Limitación | Mitigación |
|---|---|---|
| L_P1 | T1 setup operativo requiere acceso Google Cloud Console + Railway dashboard | T1 ya tiene ambos — gate trivial |
| L_P2 | Callback URL hardcoded a `la-forja-api-production.up.railway.app` | Si el dominio público cambia (custom domain) → re-setear OAuth client + env var |
| L_P3 | Cookie `la-forja_session` HttpOnly+secure+SameSite=Lax → no funciona en localhost dev | Aceptable: dev usa stub mode (NODE_ENV=development) |
| L_P4 | Smoke E2E requiere intervención manual T1 (login browser) | No automatizable sin Playwright + headless Google account — fuera scope |
| L_P5 | Si OAuth client de Google es shared (otros proyectos Monstruo), riesgo de leak credentials cross-project | DSC-X-003 patron Manus-Oauth dice scaffold separado por proyecto — recomendado nuevo client dedicado LA-FORJA |
| L_P6 | Una vez activado, rollback requiere unset env vars + redeploy (no flag toggle instantáneo) | Aceptable: rotura de auth no es runtime regression, es operativa |

## §9 NO-CRUCE reglas duras

- ❌ NO modificar código en `apps/la-forja/api/src/` (todo el wiring está en main desde DSC-LF-009)
- ❌ NO crear migrations nuevas (schema D5.1 ya soporta `google_sub` real en `forja_profiles`)
- ❌ NO touch `forja_budget` source-of-truth canonical
- ❌ NO modificar Dockerfile (D6 builder OK)
- ❌ NO interferir con otros 3 hilos Manus paralelos (E1 Anti-Dory D6, E2 VERIFICADOR-001 standby T6, Catastro hilo activo)
- ✅ SÍ setear Railway env vars production (T1)
- ✅ SÍ configurar Google Cloud Console OAuth client (T1)
- ✅ SÍ Manus E2 ejecuta smoke E2E post-redeploy + reporte bridge

## §10 Cadencia esperada

- **T+0 (HOY):** spec firmado + bridge a Manus E2 + T1 inicia setup Google Cloud
- **T+0.5-1h:** T1 completa setup Google Cloud + Railway env vars + dispara redeploy
- **T+5-10min post-redeploy:** Manus E2 ejecuta smoke C3 E2E + 4 SQL queries verificación
- **T+2h max:** bridge cierre Manus E2 con evidencia binaria + Cowork audit DSC-G-008 v4 + frase canónica

**Total estimado:** 1-3h end-to-end (mayoría tiempo es setup T1 manual).

## §11 Cierre verde — gates DSC-G-008 v4 (audit Cowork final)

Audit Cowork sobre reporte Manus E2:
- G1 Acceptance criteria 11/11 verificados binariamente
- G2 Smoke E2E exitoso con login manual T1 + tutor stream
- G3 Cero secrets en bridge final (logs Railway sanitized)
- G4 SQL verificación post-smoke retorna evidencia esperada
- G5 Scope respetado (cero código tocado)
- G6 No-duplicate (es activación operativa, no re-implementación)

Si verde:
- 🏛️ **D4-PROD-AUTH-001 — DECLARADO**
- Auth Google real funcional en producción
- Persistencia D5.2/D5.3 validada con tráfico E2E real
- #148 cost-per-thread fix validation binaria post-smoke

Si rojo:
- Manus E2 reporta error binario verbatim
- Cowork audit root cause + spec fix follow-up
- Posible rollback Railway env vars

## §12 Trayectoria post-D4-PROD-AUTH

1. **HOY:** spec firmado + setup + smoke E2E + cierre formal
2. **HOY+1d:** observabilidad 24h tráfico real (Langfuse + Railway logs)
3. **HOY+1-3d:** próximo sprint LA-FORJA (D5 follow-ups #149 #154 agrupable, o D5.4/D7 si están en SPEC v3.2)

---

**Status:** `🟢 FIRMADO — T1 ejecuta setup, Manus E2 ejecuta smoke E2E post-redeploy`
**Cowork T2-A firma con autoridad delegada T2 bajo autorización T1 magna verbatim 2026-05-18.**

**Sources:**
- D4 código mergeado: DSC-LF-009 (firmado 2026-05-17)
- D6 declarado: bridge `bridge/cowork_to_manus_LA_FORJA_001_D6_SMOKE_VERDE_DEPLOY_AUTORIZADO_2026_05_18.md`
- Cadena D6 PRs en main: #157 `15cfe83` + #159 `6ff8542` + #160 `754ebc4` (Cowork mergeé) + #161 `586a267`
- HEAD main actual: `de99c63` (Regla Dura #11 4-hilos Manus)
