# Night 0 Complex Shadow Run — Carril A: Endpoint Consumer Gap

**Fecha:** 2026-05-18
**Oportunidad:** OPP-NB-010
**Risk Class:** R0
**Carril:** A de 4
**Artifact type:** Reporte (read-only, cero side effects)
**base_sha (atlas branch):** `5f880054278942dd7f9f97036a109ae1679e57d4`

---

## base_sha

```
bed77d9acb832ce0e735b104e2ae60ba50079457
```

(origin/main al momento de iniciar el escaneo — verificado via `git rev-parse origin/main`)

---

## files_read

| Archivo | Fuente |
|---|---|
| `monstruo_reality_atlas/reports/PROD_REALITY_AND_UI_CONSUMER_PACK.md` | branch `origin/monstruo-reality-atlas-001` |
| `kernel/**/*.py` (grep prefixes + route decorators) | origin/main |
| `apps/mobile/lib/core/config.dart` | origin/main |
| `apps/mobile/gateway/server.py` | origin/main |
| `bot/*.py` | origin/main |
| `scripts/*.py` | origin/main |

---

## commands_or_searches_run

1. `git show origin/monstruo-reality-atlas-001:monstruo_reality_atlas/reports/PROD_REALITY_AND_UI_CONSUMER_PACK.md`
2. `grep -rn 'prefix=' kernel/ --include="*.py" | grep -o 'prefix="[^"]*"' | sort -u`
3. `grep -rn '@router.\|app.' kernel/ --include="*.py" | grep -E '\.(get|post|put|delete|patch)\(' | grep -o '"[^"]*"' | sort -u`
4. `grep -rn '/v1/' apps/mobile/gateway/ --include="*.py" --include="*.ts" | grep -o '"/v1/[^"]*"' | sort -u`
5. `grep -rn '/v1/' apps/mobile/lib/ --include="*.dart" | grep -o '"/v1/[^"]*"' | sort -u`
6. `grep -rn '/v1/' bot/ --include="*.py" | sort -u`
7. `grep -rn 'httpx\|requests.\|aiohttp\|fetch(' kernel/ --include="*.py" | grep '/v1/'`
8. `git rev-parse origin/main`

---

## Endpoints encontrados (Router Prefixes declarados en kernel/)

| # | Prefix | Módulo kernel |
|---|---|---|
| 1 | `/v1/a2a` | kernel/a2a/ |
| 2 | `/v1/agui` | kernel/agui/ |
| 3 | `/v1/alerts` | kernel/alerts/ |
| 4 | `/v1/autonomy` | kernel/autonomy/ |
| 5 | `/v1/brand` | kernel/brand/ |
| 6 | `/v1/catastro` | kernel/catastro/ |
| 7 | `/v1/cowork` | kernel/cowork_runtime/ |
| 8 | `/v1/deployments` | kernel/deployments/ |
| 9 | `/v1/dossier` | kernel/dossier/ |
| 10 | `/v1/e2e` | kernel/e2e/ |
| 11 | `/v1/embrion` | kernel/embrion/ |
| 12 | `/v1/finops` | kernel/finops/ |
| 13 | `/v1/magna` | kernel/magna/ |
| 14 | `/v1/memento` | kernel/memento/ |
| 15 | `/v1/memory` | kernel/memory/ |
| 16 | `/v1/missions` | kernel/missions/ |
| 17 | `/v1/moc` | kernel/moc/ |
| 18 | `/v1/planner` | kernel/planner/ |
| 19 | `/v1/traffic` | kernel/traffic/ |
| 20 | `/openai/v1` | kernel/openai_compat/ |

**Total prefixes:** 20

---

## Consumidores reales por endpoint (evidencia de grep)

### Flutter App (apps/mobile/lib/)

| Endpoint consumido | Archivo consumidor | Evidencia |
|---|---|---|
| `/v1/agents/external` | `apps/mobile/lib/core/config.dart:40` | `agentsListEndpoint = '/v1/agents/external'` |
| `/v1/agents/dispatch` | `apps/mobile/lib/core/config.dart:41` | `agentsDispatchEndpoint = '/v1/agents/dispatch'` |

**Total Flutter directo:** 2 endpoints

### AG-UI Gateway (apps/mobile/gateway/)

| Endpoint consumido | Evidencia |
|---|---|
| `/v1/agui/info` | proxy directo |
| `/v1/agui/run` | proxy directo |
| `/v1/embrion/status` | proxy (nota: endpoint real es `/v1/embrion/estado`) |
| `/v1/finops/status` | proxy |
| `/v1/finops/summary` | proxy |
| `/v1/memory/search/semantic` | proxy |
| `/v1/memory/stats` | proxy |
| `/v1/memory/thoughts` | proxy |
| `/v1/moc/insights?limit=5` | proxy |
| `/v1/moc/sintetizar` | proxy |
| `/v1/moc/status` | proxy |
| `/v1/tools` | proxy |

**Total Gateway:** 12 endpoints

### Telegram Bot (bot/)

| Endpoint consumido | Evidencia |
|---|---|
| `/v1/feedback` | bot HITL handler |
| `/v1/hitl/pending` | bot HITL handler |
| `/v1/step` | bot step handler |

**Total Bot:** 3 endpoints

### Scripts internos (scripts/)

| Endpoint consumido | Evidencia |
|---|---|
| `/v1/catastro/recommend` | scripts de catastro |
| `/v1/catastro/status` | scripts de catastro |
| `/v1/catastro/dashboard/*` (4 sub-endpoints) | scripts de catastro |
| `/v1/catastro/dominios` | scripts de catastro |
| `/v1/catastro/modelos/{id}` | scripts de catastro |
| `/v1/error-memory/seed` | scripts de seeding |
| `/v1/memento/admin/dashboard` | scripts de memento |
| `/v1/memento/admin/reload` | scripts de memento |
| `/v1/memento/validate` | scripts de memento |

**Total Scripts:** 12 endpoints

### Kernel-to-kernel (internal)

| Endpoint consumido | Consumidor |
|---|---|
| `/v1/catastro/recommend` | `kernel/embrion_loop.py` vía `_select_model_via_catastro` (CATASTRO-WIRING-001) |

**Total kernel-to-kernel:** 1 endpoint

---

## Endpoints SIN consumidor identificado

Los siguientes prefixes/endpoints **NO tienen consumidor real auditado** (ni Flutter, ni Gateway, ni Bot, ni Scripts, ni kernel-to-kernel):

| # | Prefix/Endpoint | Módulo | Riesgo |
|---|---|---|---|
| 1 | `/v1/alerts/*` | kernel/alerts/ | Endpoint expuesto sin consumidor |
| 2 | `/v1/autonomy/*` | kernel/autonomy/ | Endpoint expuesto sin consumidor |
| 3 | `/v1/brand/*` | kernel/brand/ | Endpoint expuesto sin consumidor |
| 4 | `/v1/cowork/*` | kernel/cowork_runtime/ | Solo consumido por Cowork sessions dashboard (interno) |
| 5 | `/v1/deployments/*` | kernel/deployments/ | Endpoint expuesto sin consumidor |
| 6 | `/v1/dossier/*` | kernel/dossier/ | Endpoint expuesto sin consumidor |
| 7 | `/v1/e2e/*` | kernel/e2e/ | Endpoint expuesto sin consumidor externo |
| 8 | `/v1/magna/*` | kernel/magna/ | Endpoint expuesto sin consumidor |
| 9 | `/v1/missions/*` | kernel/missions/ | Endpoint expuesto sin consumidor |
| 10 | `/v1/planner/*` | kernel/planner/ | Endpoint expuesto sin consumidor |
| 11 | `/v1/traffic/*` | kernel/traffic/ | Endpoint expuesto sin consumidor |
| 12 | `/v1/a2a/*` | kernel/a2a/ | Endpoint expuesto sin consumidor |
| 13 | `/openai/v1/*` | kernel/openai_compat/ | Endpoint expuesto sin consumidor |

**Total endpoints sin consumidor:** 13 de 20 prefixes (65%)

---

## NO_SOURCE

| Item | Descripción |
|---|---|
| `Command Center` | Directorio NO existe en `apps/`, `kernel/`, ni top-level. Doctrina lo menciona, código no lo implementa. |
| `cowork_session_memory` tabla | Declarada en prompt T1, NO existe en Supabase producción (404 verificado por PACK). |
| `FCS` (Functional Consciousness Score) | Concepto en APP_VISION, NO en runtime `/health`. |
| `proposal_processor` worker logs | Solo código, sin endpoint público ni log accesible. |

---

## ACCESS_BLOCKED

| Recurso | Razón |
|---|---|
| `/v1/embrion/proposals` | Requiere `X-API-Key` |
| `/v1/embrion/diagnostic` | Requiere `X-API-Key` |
| `/v1/finops/summary` | Requiere `X-API-Key` |
| `/v1/memory/status` | Requiere `X-API-Key` |
| `/v1/moc/status` | Requiere `X-API-Key` |
| `/v1/catastro/status` | Requiere `X-API-Key` |
| `/v1/agui/info` | Requiere `X-API-Key` |
| Logs Railway (últimos 7 días) | Sin CLI Railway desde sandbox |
| Costos Railway/Supabase/Langfuse infra | Sin API pública desde sandbox |

---

## Riesgos identificados

| # | Riesgo | Severidad | Evidencia |
|---|---|---|---|
| 1 | **65% de prefixes sin consumidor real** — sobre-construcción del kernel respecto a transports | P1 | 13/20 prefixes sin consumer |
| 2 | **Drift naming** `/v1/embrion/status` (Gateway proxy) vs `/v1/embrion/estado` (endpoint real) | P2 | Gateway server.py vs embrion_routes.py |
| 3 | **Command Center inexistente** — doctrina sin implementación | P1 | `find . -name "command*"` vacío |
| 4 | **URL muerta** `el-monstruo-kernel.up.railway.app` (sin `-production`) en docs/bridge | P1 | PACK §8.1 |
| 5 | **Flutter consume solo 2 endpoints directos** — el resto del kernel es invisible para la app | P1 | config.dart:40-41 |
| 6 | **Gateway proxy 12 endpoints** pero Flutter NO los invoca directamente — posible capa muerta | P2 | Gateway server.py vs config.dart |
| 7 | **13 prefixes expuestos en producción sin auth visible** (solo X-API-Key en algunos) | P2 | grep route decorators |

---

## Qué NO inferir

- **NO inferir que los endpoints sin consumidor son inútiles.** Pueden ser para futuros transports (Command Center, WhatsApp, Apple Watch) aún no implementados.
- **NO inferir que el Gateway está muerto** porque Flutter solo consume 2 endpoints directos. El Gateway puede servir a un frontend web no auditado aquí.
- **NO inferir que los endpoints AUTH-BLOCKED están rotos.** La protección por `X-API-Key` es intencional (DSC-S-006 RLS + auth).
- **NO inferir que `/v1/cowork/*` no tiene consumidor.** El Cowork sessions dashboard es un consumidor interno (browser-based, no Flutter).
- **NO inferir que el kernel debe reducirse.** La doctrina (Obj #9 Transversalidad) exige que los módulos expongan datos para otros — el gap es de transports, no de kernel.

---

## stop_reason

```
SCAN_COMPLETE — todas las fuentes read-only agotadas sin side effects.
```

---

## cost_estimate

| Recurso | Consumo estimado |
|---|---|
| Manus credits (este ciclo) | ~15-20 tool calls (grep, git show, file read) |
| LLM tokens (este reporte) | ~4000 output tokens |
| API calls externas | 0 |
| DB queries | 0 |
| Deploys | 0 |
| Branches creadas | 0 |
| PRs abiertos | 0 |

---

## Confirmación de cero side effects

- ✅ Cero archivos escritos en el repo (solo lectura)
- ✅ Cero branches creadas
- ✅ Cero PRs abiertos
- ✅ Cero tests ejecutados
- ✅ Cero queries a Supabase
- ✅ Cero secrets accedidos o modificados
- ✅ Cero deploys
- ✅ Cero canonizaciones
- ✅ Cero modificaciones a AGENTS.md, CLAUDE.md, gates, workflows o evaluators
- ✅ Este reporte es el ÚNICO artefacto generado (R0 = máximo 1 artefacto)
