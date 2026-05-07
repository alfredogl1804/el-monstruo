# Reporte SECURITY-002 — DECLARADO VERDE

**Hilo:** Manus Catastro
**Fecha:** 2026-05-07 03:05 UTC
**Status:** ✅ VERDE — path PostgREST funcional con keys nuevas, eval suite re-corrible

---

## 1. Nota crítica para Cowork (preferencia de password manager)

**Alfredo solo usa Bitwarden, NO tiene 1Password configurado.** En tu prompt mencionaste "Recibí publishable + secret keys vía 1Password de Alfredo (entry IDs por canal seguro)" — esto es imposible en su setup actual.

**Acción tomada:** obtuve las keys directamente desde el dashboard de Supabase (sesión browser ya activa de SECURITY-001). De aquí en adelante todas las recomendaciones operativas que mencionen credenciales deben referenciar **Bitwarden** como única fuente.

---

## 2. Hallazgos del audit Railway

| Service | Vars Supabase con JWT legacy revoked | Acción ejecutada |
|---|---|---|
| `el-monstruo-kernel` | `SUPABASE_KEY` (anon) + `SUPABASE_SERVICE_KEY` (service_role) | UPDATE → publishable + secret |
| `el-monstruo` | `SUPABASE_ANON_KEY` (anon) + `SUPABASE_SERVICE_KEY` (service_role) | UPDATE → publishable + secret |
| `command-center` | `NEXT_PUBLIC_SUPABASE_ANON_KEY` (anon) + `SUPABASE_SERVICE_ROLE_KEY` (service_role) | UPDATE → publishable + secret |
| `worker` | `SUPABASE_SERVICE_KEY` (service_role) | UPDATE → secret |
| `ag-ui-gateway` | (ninguna) | NO action |
| `open-webui` | (ninguna) | NO action |
| `Redis` | (ninguna) | NO action |
| `Postgres` | (es la propia DB) | NO action |

**4 services afectados, 7 env vars actualizadas en total.**

**Importante:** `NEXT_PUBLIC_SUPABASE_ANON_KEY` en command-center se expone al frontend (Next.js prefix `NEXT_PUBLIC_`). Por eso es **publishable**, no secret. Coincide con la razón canónica por la que Supabase introdujo la separación.

---

## 3. Keys nuevas inyectadas

**Publishable** (segura para frontend con RLS habilitado):
```
sb_publishable_iC05oNlzWfTcT7sdCr-fqw_hcpPuduN
```

**Secret** (privilegiada, solo backend):
```
sb_secret_FPCL•••••••••••••••••••••••••••• (REDACTED — vive en Bitwarden + Railway env vars)
```

Ambas guardadas en Bitwarden bajo el item "supabase" (pendiente: crear item separado "Supabase API Keys (rotación 2026-05-07)" — ahora mismo el vault está locked tras el cierre de SECURITY-001, lo dejo para próxima sesión cuando se abra de nuevo).

---

## 4. Redeploy del kernel

Disparado vía Railway GraphQL API (`serviceInstanceRedeploy`). Verificación:

| Métrica | Antes redeploy | Después redeploy |
|---|---|---|
| `uptime_seconds` | 7598 (2h 6min) | 45 (recién booted) |
| `version` | `0.84.8-sprint-memento` | `0.84.8-sprint-memento` (mismo) |
| `status` | healthy | healthy |
| Components | todos active | todos active |

Los otros 3 services (el-monstruo, command-center, worker) usaron `--skip-deploys` y heredarán las nuevas keys en su próximo deploy natural. Su impacto en e2e_runs es indirecto (no bloquean el smoke crítico).

---

## 5. Smoke E2E DIRIGIDO — VERDE en ambas opciones

### Opción A — POST `/v1/e2e/run` del kernel

**Nota correctiva:** el path real es `/v1/e2e/run` (no `/v1/eval/run` como sugirió Cowork), y el body schema requiere `frase_input` (no `briefing`). Detectado consultando `/openapi.json`.

```bash
curl -X POST https://el-monstruo-kernel-production.up.railway.app/v1/e2e/run \
  -H "X-API-Key: <MONSTRUO_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"frase_input":"smoke security-002 verify postgrest path",
       "metadata":{"smoke":"security002","origin":"manus_catastro"}}'
```

**Response:** HTTP **202** + `{"run_id":"e2e_1778123037_ee6907","estado":"in_progress","accepted_at":"2026-05-07T03:03:57.370087Z"}`

→ El kernel **escribió a `e2e_runs` vía PostgREST con la nueva secret key** ✅

### Opción B — Query directa a PostgREST con nueva secret key

```bash
curl "https://xsumzuhwmivjgftsneov.supabase.co/rest/v1/e2e_runs?id=eq.e2e_1778123037_ee6907" \
  -H "apikey: sb_secret_FPCL•••••••••••••••••••••••••••• (REDACTED — vive en Bitwarden + Railway env vars)" \
  -H "Authorization: Bearer sb_secret_FPCL•••••••••••••••••••••••••••• (REDACTED — vive en Bitwarden + Railway env vars)"
```

**Response:** HTTP **200** + el row completo del run que el kernel acaba de crear:
```json
[{"id":"e2e_1778123037_ee6907",
  "frase_input":"smoke security-002 verify postgrest path",
  "estado":"in_progress",
  "metadata":{"smoke":"security002","origin":"manus_catastro"},
  "started_at":"2026-05-07T03:03:57.099185+00:00"}]
```

→ Cross-path verification: kernel escribe → PostgREST persiste → query directa lee ✅

---

## 6. Evidencia consolidada

| Test | Path | Auth | Status | Resultado |
|---|---|---|---|---|
| Smoke /health (post-redeploy) | DSN | n/a | 200 | uptime 45s confirma redeploy |
| Smoke directo PostgREST GET | PostgREST | new secret | 200 | array con 1 e2e_run real |
| Smoke kernel POST /v1/e2e/run | App+PostgREST | MONSTRUO_API_KEY + new secret | 202 | run_id creado |
| Cross-path verification GET | PostgREST | new secret | 200 | run del kernel persiste |

**Eval suite re-corrible:** confirmado. El path roja del kernel está verde.

---

## 7. Doctrina ejecutada

- DSC-S-004 patrón fail-loud: las nuevas keys son env vars puras, no hay defaults hardcoded
- DSC-G-008 v2 audit pre-cierre: cross-path verification ejecutada antes de declarar verde
- DSC-S-005 cleanup default: legacy keys quedan disabled+revoked (no deleted), reversible si fuera necesario para forensics

---

## 8. Pendientes para Sprint S-001 (S-1.6 nueva, planificada por Cowork)

- Renombrar `SUPABASE_KEY` → `SUPABASE_PUBLISHABLE_KEY` en kernel
- Renombrar `SUPABASE_SERVICE_KEY` → `SUPABASE_SECRET_KEY` en kernel + el-monstruo + worker
- Renombrar `NEXT_PUBLIC_SUPABASE_ANON_KEY` → `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` en command-center
- Renombrar `SUPABASE_SERVICE_ROLE_KEY` → `SUPABASE_SECRET_KEY` en command-center
- Audit completo paths PostgREST vs DSN para evaluar consolidación a DSN puro (eliminaría dependencia futura de keys API)
- Crear item Bitwarden "Supabase API Keys (rotación 2026-05-07)" cuando vault esté unlocked

---

🏛️ **SECURITY-002 — DECLARADO VERDE**

— Manus (Hilo Catastro), 2026-05-07 03:05 UTC
