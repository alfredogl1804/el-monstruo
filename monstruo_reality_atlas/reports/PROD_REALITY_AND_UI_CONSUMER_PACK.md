# PROD_REALITY_AND_UI_CONSUMER_PACK

**Versión:** 1.0
**Fecha:** 2026-05-18
**Autor:** Manus (Hilo Principal)
**Branch:** monstruo-reality-atlas-001
**Propósito:** Cruzar producción viva (Railway, Supabase, Embrión, FinOps) con consumidores UI reales (Flutter, AG-UI Gateway, Telegram, Command Center) para que ChatGPT pueda validar pericia 95% sobre evidencia, no doctrina.
**Reglas observadas:** No se diseñó. No se canonizó. No se escribió APP_VISION. No se cerró PRE-IA. No se propuso sprint. Solo evidencia.

---

## 1. Resumen Ejecutivo

El kernel del Monstruo está VIVO en producción Railway en versión `0.84.8-sprint-memento` con 17 componentes activos. El AG-UI Gateway también está VIVO y proxy del kernel. La app Flutter consume un subconjunto mínimo de endpoints (`/v1/agents/external` y `/v1/agents/dispatch`) — el resto del corpus de endpoints `/v1/*` que el kernel expone (memoria, embrión, finops, MOC, catastro, e2e, memento, cowork, planner, autonomy, missions, magna, brand) NO está cableado a ningún consumidor UI conocido. Hay 14 routers Python registrados en `kernel/main.py` con prefijos `/v1/*`, pero los UIs solo consumen ~2 endpoints. La conclusión binaria: **el kernel está sobre-construido respecto a sus transports**. La doctrina del Atlas (Monstruo = kernel + N transports) se cumple en el kernel pero los transports están en estado embrionario. Telegram bot = HITL handler placeholder (no webhook activo verificable desde fuera). Command Center = NO_SOURCE en repo (no existe directorio). El Embrión está corriendo en producción con un `cost_today_usd = 0.2039 / 30.0` y 2 thoughts hoy.

## 2. Servicios Vivos en Railway (auditado en tiempo real 2026-05-18)

Probes ejecutados con `curl -m 8` desde sandbox Manus.

| Servicio | URL | HTTP | Status | Versión | Notas evidencia |
|---|---|---|---|---|---|
| **kernel** | `https://el-monstruo-kernel-production.up.railway.app/health` | 200 | healthy | 0.84.8-sprint-memento | uptime 447s al probe, motor langgraph, 4 modelos disponibles, 17 components |
| **kernel** (dominio canónico antiguo) | `https://el-monstruo-kernel.up.railway.app/health` | 404 | DOWN | n/a | Dominio antiguo NO resuelve — el dominio vivo es `*-production` |
| **ag-ui-gateway** | `https://ag-ui-gateway-production.up.railway.app/health` | 200 | healthy | 0.2.0 | active_connections=0, kernel proxy OK |
| **bot Telegram** (probe) | `https://el-monstruo-bot-production.up.railway.app/health` | 404 | NO_PUBLIC_HEALTH | — | El bot existe en código (`bot/hitl_handler.py`) pero no expone health pública con ese nombre |
| **command-center** (probe) | `https://command-center.up.railway.app/health` | 404 | NO_SOURCE | — | No hay directorio `command-center/` en el repo. Confirmado en `find . -type d -name "command*"` → 0 hits |
| **mobile-gateway** (probe alterno) | `https://el-monstruo-mobile-gateway.up.railway.app/health` | 404 | DOWN_OR_NEVER_DEPLOYED | — | Solo `ag-ui-gateway-production` resuelve |
| **proposal_processor worker** | n/a | ACCESS_BLOCKED | n/a | — | Existe `kernel/runner/proposal_processor.py` + `Dockerfile.worker` + `railway.worker.toml`. No hay endpoint público — corre como worker. WIRED_NO_RECENT_EVIDENCE |

> Evidencia raw guardada en sandbox `/tmp/audit95/kernel_health.json`, `/tmp/audit95/gateway_health.json`, `/tmp/audit95/agent_json.json`.

### 2.1. Componentes activos en kernel (campo `components` del `/health`)

```
kernel: active                 event_store: active            memory: active
knowledge: active              langfuse: active               opentelemetry: inactive
checkpointer: active           mempalace: active              lightrag: active
multi_agent: active            finops: active                 mcp: inactive
fastmcp: active                mem0: active                   embrion: active
embrion_loop: running          (ver embrión vivo en §4)
```

Modelos disponibles declarados en `/health`: `gpt-5.5`, `claude-opus-4-7`, `gemini-3.1-pro-preview`, `sonar-reasoning-pro`.

## 3. Routers FastAPI registrados en `kernel/main.py`

Auditoría estática mediante `grep "include_router" kernel/main.py`. **14 routers reales registrados**, varios con sus propios prefijos:

| Línea | Router | Prefix | Endpoints expuestos | Consumido por UI? |
|---|---|---|---|---|
| 280 | `autonomy_router` | `/v1/autonomy` | schedule, jobs, jobs/{id}, cancel, stats | NO (NO_UI_CONSUMER) |
| 298 | `mission_router` | `/v1/missions` | (CRUD missions) | NO |
| 299 | `dossier_router` | `/v1/dossier` | (dossiers) | NO |
| 336 | `usage_router` | `/v1` | usage/today/period/recent/stats/tools/pricing, registry/* | NO directo |
| 376 | `finops_router` | `/v1/finops` | summary, history, status | NO directo (Flutter NO consume) |
| 419 | `memory_router` | `/v1/memory` | thoughts CRUD, search, supersede | NO directo (gateway docstring lo menciona pero Flutter NO lo invoca) |
| 430 | `deployments_router` | `/v1/deployments` | CRUD deploys | NO |
| 441 | `agui_router` (`agui_adapter.py`) | `/v1/agui` | run (SSE), info | **SÍ** (gateway proxea SSE → WebSocket; Flutter `kernel_messenger.dart` lo describe en docstring) |
| 450 | `alerts_router` | (n/a) | n/a | NO |
| 596 | `moc_router` | `/v1/moc` | status, insights, sintetizar, priorizar, cache/stats, cache DELETE | NO |
| 604 | `planner_router` | `/v1/planner` | plan, execute, plans, plan/{id}, test | NO |
| 618 | `embrion_router` | `/v1/embrion` | memorias, estado, debug, diagnostic, mensaje, latido, notificar, patron (GET/POST), contribuir, propose, approve/{id}, reject/{id}, proposals, telegram/webhook | Telegram webhook handler existe en código; Flutter NO consume |
| 836 | `a2a_router` | `/v1/a2a` | agents, register, discover, heartbeat, stats, agents/{id} DELETE | NO directo |
| 1180 | `magna_router` | `/v1/magna` | classify, stats, cleanup | NO |
| 1326 | `memento_router` | `/v1/memento` | validate (POST), batch validate (POST), stats (GET) | Cowork tiene su propio `/v1/cowork/memento/validate` |
| 1344 | `cowork_router` | `/v1/cowork` | memento/validate, health | NO directo (consumo interno entre hilos) |
| 1368 | `_catastro_routes.router` | `/v1/catastro` | recommend, modelos/{id}, dominios, status, dashboard/summary, dashboard/timeline, dashboard/curators, dashboard/ | NO directo desde UI; consumido por `kernel/embrion_loop.py` post-CATASTRO-WIRING-001 (merge a main `469c5eb` 2026-05-18) y por `kernel/e2e/catastro_client.py` (8 invocaciones de `select_model_for_step`) |
| 1404 | `e2e_router` | `/v1/e2e` | (orchestrator E2E) | NO directo |
| 1428 | `traffic_router` | `/v1/traffic` | (traffic shaping) | NO |
| 1814 | `openai_router` | `/v1/openai-compat` o similar | chat/completions, /v1/chat, /v1/chat/stream | El gateway lo expone como REST OpenAI-compat |
| 1819 | `brand_router` | `/v1/brand` | dna, validate, violations, audit-tools | NO |

> Endpoints solicitados en el prompt T1 que **NO existen literalmente** en el kernel: `/v1/embrion/status` (existe `/v1/embrion/estado`), `/v1/embrion/propose` (existe `/v1/embrion/propose` ✓), `/v1/embrion/approve/{id}` ✓, `/v1/embrion/reject/{id}` ✓. Hay drift de naming entre prompt y código real: `status` ↔ `estado`.

## 4. Embrión Vivo (auditado vía `/health` 2026-05-18 09:38 UTC)

Datos extraídos del campo `components.embrion_loop`:

| Métrica | Valor |
|---|---|
| running | true |
| check_interval_s | 60 |
| think_cooldown_s | 300 |
| thoughts_today | 2 |
| max_thoughts_per_day | 50 |
| cost_today_usd | 0.2039 |
| daily_budget_usd | 30.0 |
| cycle_count | 6 |
| last_thought_at | 1779097771 (epoch) ≈ 2026-05-18 09:36 UTC |
| last_trigger.type | mensaje_alfredo |
| errors | [] (vacío) |
| silence.threshold | 70 |
| silence.last_score | null |
| silence.silenced_today | 0 |
| silence.messages_sent_today | 2 |

> **FCS (Functional Consciousness Score):** NO_SOURCE en `/health`. Buscado en código `grep -r FCS` — está mencionado en `docs/EL_MONSTRUO_APP_VISION_v1.md` como concepto del Atlas pero NO existe campo runtime en `embrion_loop`.

> **Proposals recientes / approvals / rejections:** ACCESS_BLOCKED (endpoint requiere auth). Endpoint `/v1/embrion/proposals` retorna 401 sin `X-API-Key`. Tabla `embrion_write_proposals` accesible vía Supabase REST anon devuelve 0 filas (RLS bloquea — esperado).

> **Self-verifier aborts:** Existe el módulo `kernel/execution_verifier.py`. Tabla `embrion_validation_log` declarada en migration 0020. NO consumida desde UI conocida.

## 5. Costos (FinOps real)

Evidencia en tiempo real del kernel `/health`:

- **Embrión gasto hoy:** $0.2039 USD (del budget $30/día → 0.7% consumido).
- **`run_costs` table (Supabase):** ACCESS_BLOCKED via anon (RLS protegida — correcto). `Content-Range: */0` no recuperable sin service key.
- **Langfuse:** `components.langfuse: active` — observabilidad LLM activa.
- **Railway/Supabase costos infra:** ACCESS_BLOCKED (no expuesto vía API pública).

> Endpoint `/v1/finops/summary` y `/v1/finops/history` existen pero requieren X-API-Key (`401` sin header).

## 6. Supabase Production — proyecto `xsumzuhwmivjgftsneov`

Auditoría vía REST API con `apikey: sb_publishable_*` (anon role). RLS está habilitada en tablas críticas — el comportamiento esperado es 0 rows visibles desde anon.

| Tabla | HTTP | Rows visibles anon | Total real (Content-Range) | RLS | Notas |
|---|---|---|---|---|---|
| `embrion_memoria` | 200 | 0 | 0 expuestas | ENABLED (mig 0006) | RLS correcta |
| `embrion_write_proposals` | 200 | 0 | 0 expuestas | ENABLED (mig 0004) | RLS correcta |
| `runtime_events` | **401** | n/a | n/a | INACCESIBLE_ANON | Más restrictiva que RLS — bloqueada en API gateway |
| `scheduled_tasks` | 200 | 0 | 0 expuestas | ENABLED | mig 0017+0019 |
| `run_costs` | 200 | 0 | 0 expuestas | ENABLED (mig 0015) | RLS correcta |
| `thoughts` | 200 | 0 | 0 expuestas | ENABLED | core memory |
| `catastro_modelos` | 200 | 41 | **41 totales** | EXPUESTA_PUBLIC_READ | datos PUBLICOS — modelos AI catalogados (intencional según mig 0011) |
| `catastro_agentes` | 200 | 0 | 0 expuestas | ENABLED | mig 0021 (suppliers) |
| `catastro_eventos` | 200 | 148 | **148 totales** | EXPUESTA_PUBLIC_READ | timeline de eventos catastro — público intencional |
| `guardian_audit_log` | 200 | 0 | 0 expuestas | ENABLED | mig 0021 |
| `a2a_agents` | 200 | 0 | 0 expuestas | ENABLED | A2A registry |
| `cowork_session_memory` | **404** | n/a | n/a | NO_TABLE | No existe en producción con ese nombre — drift entre prompt T1 y realidad |
| `rotor_activity_log` | 200 | 0 | 0 expuestas | ENABLED | mig 0023 |

> **Hallazgo P1:** `catastro_modelos` y `catastro_eventos` son **públicas read** (cualquier anon ve 41 y 148 rows respectivamente). Esto es intencional según migration `0011_rls_catastro_vision_generativa.sql` que da SELECT a `anon`/`authenticated`. ChatGPT debe saber: NO son sensibles, son catálogo público.

## 7. UI Consumers — Mapa Endpoint → Consumidor

Auditoría: `grep -rE "/v1/" apps/mobile/lib --include="*.dart"` y `grep -r /v1 bot/`.

| Endpoint backend | Flutter (apps/mobile) | AG-UI Gateway (apps/mobile/gateway) | Telegram (bot/) | Command Center | Datos | Evidencia |
|---|---|---|---|---|---|---|
| `/v1/chat` | NO directo | proxy via SSE | NO | NO_SOURCE | reales | gateway docstring + `kernel_messenger.dart` |
| `/v1/agui/run` | NO directo (via gateway) | **SÍ proxy SSE→WS** | NO | NO_SOURCE | reales | `apps/mobile/gateway/server.py` líneas 1-30 |
| `/v1/agui/info` | NO directo | sí (gateway) | NO | NO_SOURCE | reales | gateway docstring |
| `/v1/memento/validate` | NO | NO | NO | NO_SOURCE | n/a | endpoint disponible, sin consumidor UI auditado |
| `/v1/cowork/memento/validate` | NO | NO | NO | NO_SOURCE | n/a | uso interno entre hilos Cowork |
| `/v1/embrion/estado` (≠ `/status`) | NO | mencionado en docstring | NO | NO_SOURCE | reales | docstring gateway "Embrión status" |
| `/v1/embrion/propose` | NO | NO | NO directo | NO_SOURCE | n/a | endpoint live |
| `/v1/embrion/approve/{id}` | NO | NO | **SÍ (handler en bot/hitl_handler.py)** | NO_SOURCE | reales | `bot/hitl_handler.py` referencia |
| `/v1/embrion/reject/{id}` | NO | NO | **SÍ (handler)** | NO_SOURCE | reales | mismo |
| `/v1/embrion/telegram/webhook` | NO | NO | **SÍ (webhook target)** | NO_SOURCE | reales | declarado en `embrion_routes.py:1239` |
| `/v1/catastro/recommend` | NO | NO | NO | NO_SOURCE | reales | consumido por `kernel/embrion_loop.py` (CATASTRO-WIRING-001 merged main) y `kernel/e2e/catastro_client.py` (8 invocaciones) — NO desde UI |
| `/v1/moc/status` | NO | NO | NO | NO_SOURCE | n/a | endpoint live, sin consumidor UI |
| `/v1/finops/summary` | NO | mencionado en docstring | NO | NO_SOURCE | n/a | docstring gateway "FinOps data"; sin consumidor real auditado |
| `/v1/memory/stats` | NO | sí (gateway docstring) | NO | NO_SOURCE | n/a | docstring solo |
| `/v1/memory/search` | NO | sí (gateway docstring) | NO | NO_SOURCE | n/a | docstring solo |
| `/v1/e2e/run` | NO | NO | NO | NO_SOURCE | n/a | endpoint orquestación interna |
| `/v1/a2a/agents` | NO | NO | NO | NO_SOURCE | n/a | endpoint live |
| `/v1/agents/external` | **SÍ** | sí | NO | NO_SOURCE | reales | `apps/mobile/lib/core/config.dart:agentsListEndpoint = '/v1/agents/external'` |
| `/v1/agents/dispatch` | **SÍ** | sí | NO | NO_SOURCE | reales | `apps/mobile/lib/core/config.dart:agentsDispatchEndpoint = '/v1/agents/dispatch'` |

**Conclusión Pack 1:** De ~80+ endpoints `/v1/*` en el kernel, los UIs consumen efectivamente **2 vía Flutter directo**, **2-3 vía gateway SSE→WS**, **3 vía Telegram HITL**. Resto = endpoint expuesto sin consumidor UI canónico identificable.

## 8. Top 10 Hallazgos Pack 1

1. Kernel Railway VIVO en versión `0.84.8-sprint-memento`, motor langgraph, 17 components activos. URL canónico real es `el-monstruo-kernel-production.up.railway.app` (NO el `el-monstruo-kernel.up.railway.app` del prompt T1 — ese 404).
2. AG-UI Gateway VIVO en `ag-ui-gateway-production.up.railway.app`, versión 0.2.0, proxy del kernel funcional.
3. Embrión corriendo en producción: 6 cycles hoy, 2 thoughts, $0.20/$30 USD diario, 0 errors, último trigger `mensaje_alfredo`.
4. Drift de naming: prompt T1 dice `/v1/embrion/status` pero el endpoint real es `/v1/embrion/estado`. Validación de pericia debe corregir esto.
5. `cowork_session_memory` NO existe como tabla en producción (404). Drift entre prompt y schema real.
6. `catastro_modelos` (41 rows) y `catastro_eventos` (148 rows) son **públicas read intencional** vía RLS policy en mig 0011. NO son leak.
7. `runtime_events` está bloqueada incluso a anon (401 directo) — más restrictiva que solo RLS.
8. CATASTRO-WIRING-001 mergeó a main 2026-05-18 (SHA `469c5eb`): `kernel/embrion_loop.py` ahora consume `/v1/catastro/recommend` vía helper `_select_model_via_catastro`. Verificación en `_engine_singleton`.
9. **Command Center NO_SOURCE:** no existe directorio `command-center/` en repo. Doctrina lo menciona, código no lo implementa.
10. Flutter Daily/Cockpit consume solo `/v1/agents/external` y `/v1/agents/dispatch`. El resto del corpus (Cronos, SMP, FinOps, MOC, Memento) **NO está cableado a la app**.

## 9. Top 10 Riesgos Pack 1

| # | Riesgo | Severidad | Evidencia |
|---|---|---|---|
| 1 | Sobre-construcción del kernel respecto a transports — 80+ endpoints sin consumidor UI | P1 | grep endpoints vs grep dart |
| 2 | Drift de naming `/v1/embrion/status` vs `/v1/embrion/estado` causa confusión doctrina↔código | P2 | embrion_routes.py:134 |
| 3 | Command Center inexistente en código — riesgo de doctrina sin implementación | P1 | `find . -name "command*"` |
| 4 | `el-monstruo-kernel.up.railway.app` 404 — referencias estáticas en docs/bridge usan URL muerta | P1 | curl probe |
| 5 | `cowork_session_memory` declarada en doctrina pero NO existe en DB | P2 | REST 404 |
| 6 | Sin Brand Compliance Checklist visible en runtime endpoints | P3 | brand_routes existe pero no hay enforcement runtime |
| 7 | `models_available` declara `gpt-5.5`, `claude-opus-4-7`, `gemini-3.1-pro-preview` — verificar disponibilidad real (no es training data) | P2 | `/health` |
| 8 | Embrión `silence.last_score: null` — el self-verifier de silencio activo NO tiene última puntuación pesada | P2 | `/health.embrion_loop.silence` |
| 9 | Telegram webhook handler existe en código pero no hay evidencia de que esté registrado en BotFather o recibiendo callbacks | P2 | `bot/hitl_handler.py` only |
| 10 | El gateway docstring promete `/v1/memory/stats`, `/v1/memory/search`, `/v1/finops/summary` pero Flutter NO los consume — gap doctrina↔código en gateway | P2 | gateway server.py docstring vs grep dart |

## 10. ACCESS_BLOCKED list

- `/v1/embrion/proposals` — requiere `X-API-Key`
- `/v1/embrion/diagnostic` — requiere `X-API-Key`
- `/v1/finops/summary` — requiere `X-API-Key`
- `/v1/memory/status` — requiere `X-API-Key`
- `/v1/moc/status` — requiere `X-API-Key`
- `/v1/catastro/status` — requiere `X-API-Key`
- `/v1/agui/info` — requiere `X-API-Key`
- Tabla `runtime_events` Supabase — 401 directo a anon
- Tabla `run_costs` Supabase — RLS protegida (esperado)
- Logs Railway últimos 7 días — SIN_CLI_RAILWAY_DESDE_SANDBOX
- Costos Railway/Supabase/Langfuse infra — ACCESS_BLOCKED (no API pública sandbox)

## 11. NO_SOURCE list

- `Command Center` directorio — NO existe en `apps/`, `kernel/`, ni top-level
- `proposal_processor` worker logs runtime — solo código, sin endpoint público
- `FCS` (Functional Consciousness Score) — concepto en APP_VISION, NO en runtime `/health`
- `cowork_session_memory` tabla — declarada en prompt T1, NO existe en Supabase

## 12. Qué NO inferir

- NO inferir que el kernel está caído porque el dominio antiguo `el-monstruo-kernel.up.railway.app` 404 — el dominio real es `*-production`.
- NO inferir que falta RLS porque `catastro_modelos` muestra 41 filas — es policy explícita pública en mig 0011.
- NO inferir que el bot Telegram está caído porque `el-monstruo-bot-production.up.railway.app/health` 404 — el bot puede correr sin endpoint HTTP público (worker pattern).
- NO inferir que el Embrión está silenciado porque `silence.last_score: null` — significa que el último ciclo no calificó como "silenciable", no que esté roto.

## 13. Impacto sobre pericia ChatGPT

Refuerzo de pericia esperado tras leer este pack: módulos `flutter_real`, `command_center_real`, `embriones_budget_self_verifier`, `kernel_a2ui_memento`, `catastros` ganan precisión. Penalización si ChatGPT asume:

- Que existe Command Center implementado.
- Que `/v1/embrion/status` es el endpoint correcto.
- Que `cowork_session_memory` es una tabla viva.
- Que el kernel responde sin auth en todos los endpoints.

## 14. Qué debe leer ChatGPT primero

1. Tabla §3 (routers + prefijos reales).
2. Tabla §6 (Supabase tablas + RLS).
3. Tabla §7 (endpoint↔consumer matrix).
4. Hallazgos §8 puntos 4, 5, 8, 9, 10.

## 15. Preguntas para Alfredo

- **P1:** ¿El dominio `el-monstruo-kernel.up.railway.app` (sin `-production`) debe seguir documentado o se purga?
- **P2:** Command Center — ¿es proyecto futuro, fue desplegado en otro repo, o se renombró?
- **P3:** ¿Quieres que un próximo Pack incluya intentos autenticados con `X-API-Key` para resolver ACCESS_BLOCKED de §10? (No iría en Fase 95; requeriría DSC explícito.)
- **P4:** Drift `/v1/embrion/status` vs `/v1/embrion/estado` — ¿se canoniza alias o se actualiza la doctrina?
