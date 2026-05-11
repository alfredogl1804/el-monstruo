# Cartografía 1B — `kernel/` módulos núcleo

**Fecha:** 2026-05-10
**Autor:** Cowork (Arquitecto Jefe)
**Sub-fase:** 1B del Estudio Forense del Monstruo
**Método:** lectura + `wc -l` + `grep` sobre `kernel/` y `tests/` con bash workspace mount. NO inferencia desde memoria.
**Alcance:** 15 módulos núcleo del kernel solicitados por el scheduled task. Auditoría de subdirectorios especializados (`brand/`, `transversales/`, `vanguard/`, `catastro/`, `collective/`, `sovereignty/`, etc.) queda para Sub-Fase 1C.
**Doctrina:** `embrion_loop.py` solo se LEE — no se modifica (DSC-MO-008 + Doctrina del Silencio).

---

## 1. Resumen ejecutivo

- **15 módulos auditados.** Total: **11,823 LOC** Python (`wc -l` verificado).
- **13/15 viven en `main` y están integrados** al flujo principal del kernel.
- **2/15 NO existen en `main`** (`audit_middleware.py`, `audit_routes.py`): viven solo en la branch `sprint/s-003-b-audit-middleware-pentest` (commit `29dc298`). Riesgo: se pierden si la branch se elimina sin merge. **El commit `29dc298` NO modifica `kernel/main.py`** — incluso en la branch, el middleware NO está registrado en el ASGI stack.
- **`kernel/main.py` con 3232 LOC** orquesta 21 routers via `include_router(...)` — densidad alta, candidato a refactor en sub-fase posterior.
- **5/15 módulos sin test directo asociado** (gap de cobertura): `embrion_routes`, `embrion_scheduler`, `telegram_notifier`, `autonomous_runner`, `agui_adapter`, `state.py`, `engine.py`. Algunos tienen cobertura tangencial (`test_embrion_vigilia.py`, `test_embrion_telegram.py`) pero NO un `test_<modulo>.py` 1:1.
- **Artefacto residual detectado:** `tests/__pycache__/test_audit_middleware.cpython-311-pytest-9.0.3.pyc` existe pero el `.py` fuente NO está en disco. Bytecode huérfano de un test que vivió en la branch S-003.B.

---

## 2. Tabla maestra de módulos

LOC = output `wc -l`. Estado: ✅ integrado al flujo / 🟡 parcial / ❌ aislado.

| # | Módulo | LOC | Propósito (1 línea) | Integración | Test directo |
|---|---|---:|---|---|---|
| 1 | `kernel/embrion_loop.py` | 2067 | Loop autónomo 24/7 del Embrión: trigger → think → judge → report. Doctrina del silencio. | ✅ `main.py:626` `await embrion_loop.start()` | ✅ `tests/test_embrion_loop_integration.py` |
| 2 | `kernel/embrion_routes.py` | 1425 | 15 endpoints REST del Embrión: estado, debug, mensajes, latidos, proposals (propose/approve/reject/list). | ✅ `main.py:618` `app.include_router(embrion_router)` | 🟡 cobertura indirecta (`test_embrion_vigilia.py`, `test_embrion_telegram.py`); no test 1:1 |
| 3 | `kernel/embrion_budget.py` | 484 | Budget Tracker: pre-flight `check_before_cycle()`, post-flight `record_after_cycle()`, `daily_summary()`. Cap $0.25/cycle. | ✅ Importado por `embrion_loop.py:60` (eager import doctrinario) | ✅ `tests/test_embrion_budget.py` |
| 4 | `kernel/embrion_scheduler.py` | 706 | Scheduler interno persistido en `scheduled_tasks`. Tipos: periodic / daily / triggered / one_shot. | ✅ `main.py:646-1068` registra default tasks + handlers + `await scheduler.start()` | ❌ sin test 1:1 |
| 5 | `kernel/embrion_write_policy.py` | 804 | Cola HITL: `propose() → approve() → execute_next()`. UNIQUE idempotency_key. Multi-canal (cowork_bridge + telegram). | ✅ Importado por `embrion_routes.py:747` y `runner/proposal_processor.py:32` | ✅ `tests/test_embrion_write_policy.py` |
| 6 | `kernel/runner/proposal_processor.py` | 260 | Worker independiente Railway: `expire_loop()` + `execute_loop()` que cierra el ciclo HITL. Graceful shutdown SIGTERM. | ✅ Servicio Railway separado `Dockerfile.worker` + `railway.worker.toml` | ✅ `tests/test_proposal_processor.py` |
| 7 | `kernel/runner/executor_registry.py` | 200 | Registry `proposal_type → función ejecutora`. Default noop; opt-in real via `payload_json.executor='real'`. | ✅ Usado por `proposal_processor.py:171,231` | ✅ Cubierto en `tests/test_proposal_processor.py:59-74` |
| 8 | `kernel/runner/telegram_notifier.py` | 398 | Cliente HTTP Telegram Bot API (sin `python-telegram-bot`). `send_message()` + `answer_callback()`. | ✅ Usado por `embrion_loop`, `embrion_routes` (3 sitios), `embrion_write_policy`, `main.py` (3 sitios) | ❌ sin test 1:1 (cubierto indirectamente por `test_embrion_telegram.py`) |
| 9 | `kernel/runner/autonomous_runner.py` | 591 | Background asyncio task: poll `scheduled_jobs` → MOC priority → re-entra al kernel → notifica Telegram. | ✅ `main.py:256-265` `await autonomous_runner.start()` + `app.state._autonomous_runner` | ❌ sin test 1:1 |
| 10 | `kernel/audit_middleware.py` | 279 | (Branch S-003.B) Audit middleware FastAPI INSERT-only a `kernel_audit_log`. Async fire-and-forget. | ❌ **NO está en `main`.** Vive solo en `sprint/s-003-b-audit-middleware-pentest` (commit `29dc298`). Y **el commit NO modifica `kernel/main.py`** → ni siquiera en la branch está registrado en `add_middleware()`. | 🟡 `test_audit_middleware.cpython-311-pytest-9.0.3.pyc` huérfano (sin .py) |
| 11 | `kernel/audit_routes.py` | 287 | (Branch S-003.B) Endpoint `GET /v1/audit/logs` con cursor pagination. service_role only. | ❌ **NO está en `main`.** Mismo estado que (10). Tampoco hay `include_router(audit_router)` en la branch. | ❌ sin test |
| 12 | `kernel/main.py` | 3232 | Bootstrap FastAPI: `lifespan()` arranca embrión + scheduler + autonomous_runner + 21 routers. ASGI stack: CORS → APIKeyAuth → RateLimiter. | ✅ Punto de entrada Railway (`run.py` → `uvicorn`) | 🟡 cobertura indirecta vía `tests/test_e2e_kernel_*.py` |
| 13 | `kernel/engine.py` | 1107 | `LangGraphKernel(KernelInterface)`: build_graph + start_run + step + stream + checkpoint + cancel + hooks. | ✅ Único motor instanciado en `main.py` | ❌ sin test 1:1. (`tests/test_brand_engine.py` es OTRO motor — Brand Engine.) |
| 14 | `kernel/agui_adapter.py` | 440 | Adaptador SSE AG-UI: `agui_run()` traduce eventos LangGraph → AG-UI events. Heartbeat asyncio.Queue (Sprint 42 fix v2). | ✅ `main.py:437-441` `app.include_router(agui_router)` | ❌ sin test 1:1 |
| 15 | `kernel/state.py` | 109 | `MonstruoState(TypedDict, total=False)` — schema compartido del grafo. Lifecycle phases documentados. | ✅ Importado por `engine.py` y `nodes.py` (no auditados aquí) | ❌ sin test 1:1 |

**Verificación LOC raw (output `wc -l` literal):**

```
  2067 kernel/embrion_loop.py
  1425 kernel/embrion_routes.py
   484 kernel/embrion_budget.py
   706 kernel/embrion_scheduler.py
   804 kernel/embrion_write_policy.py
   260 kernel/runner/proposal_processor.py
   200 kernel/runner/executor_registry.py
   398 kernel/runner/telegram_notifier.py
   591 kernel/runner/autonomous_runner.py
  3232 kernel/main.py
  1107 kernel/engine.py
   440 kernel/agui_adapter.py
   109 kernel/state.py
 11823 total
```

`audit_middleware.py` (279) y `audit_routes.py` (287) provienen de `git show 29dc298:<path> | wc -l`.

---

## 3. Detalle por módulo (funciones/clases públicas + dependencias)

### 3.1 `kernel/embrion_loop.py` — 2067 LOC — DOCTRINA DEL SILENCIO

**Header verificado:** Sprint 33C → 33B → 34. Self-Evaluation Loop con quarantine (provisional → consolidated). Validado por Claude Opus 4.7 (Sabios consultation 2026-04-29). Cost model declarado: loop $0, thinking $0.05-0.15/cycle, judge $0.01/eval.

**Clase principal (única):** `EmbrionLoop` (línea 137).

**Métodos públicos relevantes:**
- `start()` / `stop()` — control de ciclo de vida.
- `start_orchestration()` / `report_orchestration_step()` / `end_orchestration()` — API para que orquestaciones externas reporten al loop.
- `stats()` / `debug()` — telemetría.

**Métodos internos críticos (privados, citados solo por inventario):**
- `_loop()` (360) — el pulso.
- `_check_and_think()` (499) — gate principal.
- `_detect_trigger()` (564), `_judge_before()` (660), `_think()` (752), `_think_with_graph()` (1096), `_think_with_router()` (1143).
- `_compute_fcs_score()` (1173) — Functional Consciousness Score.
- `_judge_after()` (1226), `_extract_and_save_lesson()` (1341), `_get_relevant_lessons()` (1445).
- `_consolidate_memories()` (1500), `_apply_consolidation_decisions()` (1620).
- `_report()` (1729), `_save_memory()` (1773).
- `_consult_sabios_strategic()` (1847), `_check_agents_radar()` (1978).
- `_should_speak()` (427) y `_reset_daily_counters_if_needed()` (414) — Doctrina del Silencio Inteligente: 5 niveles silencio→voz, silence_score>70 para hablar.

**Dependencias kernel:** `kernel.embrion_budget` (eager import L60), `kernel.utils.keyword_matcher`. Importa también `kernel.runner.telegram_notifier` para reportes (línea 144 docstring).

**Integración:** `main.py:626` instancia `EmbrionLoop(...)` y arranca `await embrion_loop.start()` dentro del `lifespan()`. Almacenado en `app.state._embrion_loop`. Magna classifier inyectado en `main.py:1095`.

**Test asociado:** `tests/test_embrion_loop_integration.py` + fixtures `tests/fixtures/embrion_loop_samples.json`.

**Honestidad pura:** este audit NO entró a evaluar la lógica interna del loop. Solo inventarió la superficie pública. Cualquier pregunta sobre comportamiento (ej: ¿el `_judge_before` realmente valida purpose?) requiere análisis dirigido futuro fuera de la 1B.

---

### 3.2 `kernel/embrion_routes.py` — 1425 LOC

**Endpoints expuestos:** 15 (`grep -cE "@router\." = 15`).

Familias detectadas vía `grep`:
- **Estado/debug:** `obtener_memorias`, `obtener_estado`, `embrion_debug`, `embrion_diagnostic` (L95–245).
- **Comunicación:** `enviar_mensaje` (L387), `registrar_latido` (L439), `notificar_alfredo` (L501).
- **Patrones:** `obtener_patron` (L567), `guardar_patron` (L618), `contribuir_al_embrion` (L676).
- **Write Policy / HITL:** `crear_proposal` (L852), `aprobar_proposal` (L1061), `rechazar_proposal` (L1117), `listar_proposals` (L1162).

**Adapter interno notable:** `_DbToWritePolicyAdapter` (L750) + `_parse_postgrest_filter` (L765) — capa que transforma queries del DB cliente al formato esperado por `embrion_write_policy`.

**Modelos Pydantic:** `MensajeRequest`, `LatidoRequest`, `NotificarRequest`, `PatronRequest`, `ContribucionRequest`, `ProposeRequest`, `ApproveRequest`, `RejectRequest`.

**Inyección de dependencias:** `set_dependencies(db, notifier)` en L51 — patrón consistente con `agui_adapter.set_dependencies`.

**Dependencia kernel:** `from kernel import embrion_write_policy as _wp` (L747). Telegram via lazy import dentro de funciones (3 sitios: L965, L1304, L1395).

**Integración:** `main.py:611-619`. `set_embrion_deps` configura DB + notifier antes de `include_router`.

**Tests:** sin `test_embrion_routes.py`. Cobertura indirecta: `test_embrion_vigilia.py`, `test_embrion_telegram.py` (presentes en disco). **Gap declarado.**

---

### 3.3 `kernel/embrion_budget.py` — 484 LOC

**Misión documentada (header):** "Frenar el sangrado de costo del embrión que el 1 de mayo gastó $105 USD en un solo día".

**Diseño 3 capas:**
1. Pre-flight `check_before_cycle()` — proyección antes de gastar; abort si > cap o > 95% diario.
2. Post-flight `record_after_cycle()` — costo real; warning si actual > estimated × 1.3.
3. `record_aborted_cycle()` + `maybe_escalate_hitl()` + `daily_summary()`.

**Estructuras:**
- `BudgetDecision` (dataclass L68).
- `CycleResult` (dataclass L84).
- `_SupabaseRest` (L101) — cliente HTTP propio (sin SDK).
- Helpers: `estimate_cost_usd()` (L159), `_today_iso_date()` (L185), `_group_cost_by_model()` (L476).

**Dependencias kernel:** ninguna explícita. Usa solo stdlib + `_SupabaseRest` propio.

**Integración:** importado eager por `embrion_loop.py:60` (`from kernel import embrion_budget as _embrion_budget` con comentario "para que la falla de import sea ruidosa al boot").

**Tests:** ✅ `tests/test_embrion_budget.py`.

---

### 3.4 `kernel/embrion_scheduler.py` — 706 LOC

**Tipos de tarea:** `periodic` / `daily` / `triggered` / `one_shot`.

**Clases:**
- `ScheduledTask` (dataclass L51).
- `EmbrionScheduler` (L147) — clase principal, `initialize() / start() / register_handler() / get_all_tasks()`.

**Funciones módulo-nivel:**
- `register_default_tasks(scheduler)` (L534) — registra las 5 tareas default.
- `register_stub_handlers(scheduler)` (L666) — registra handlers stub.
- `get_embrion_scheduler(db)` (L692) — factory singleton.

**Stubs de handlers visibles:** `_stub_handler_causal_seeding`, `_stub_handler_prediction_validation`, `_stub_handler_vanguard_scan`, `_stub_handler_health_check`, `_stub_handler_memory_consolidation` (L621-666).

**Persistencia:** declara tabla `scheduled_tasks` (Supabase) — ver header L20 "Corrección C3 del cruce detractor".

**Governance documentado:** budget máximo USD/ejecución, 3 fallos seguidos → pausa, EMBRION_DAILY_BUDGET compartido.

**Integración:** `main.py:646-1077`:
```
embrion_scheduler = get_embrion_scheduler(db=...)
await embrion_scheduler.initialize()
register_default_tasks(embrion_scheduler)
register_stub_handlers(embrion_scheduler)
# ... más register_handler() en líneas 696, 727 ...
await embrion_scheduler.start()
app.state.embrion_scheduler = embrion_scheduler
```

**Tests:** ❌ sin `test_embrion_scheduler.py`. **Gap declarado.**

---

### 3.5 `kernel/embrion_write_policy.py` — 804 LOC

**Estados (header L29-31):** `pending → approved → executing → executed | failed | rejected`.

**Funciones públicas principales:**
- `compute_idempotency_key()` (L199) — hash determinista del payload normalizado.
- `propose(...)` (L222) — crea proposal pending.
- `approve(...)` (L338) / `reject(...)` (L386) — transiciones HITL.
- `list_pending(...)` (L432), `expire_old(...)` (L451).
- `execute_next(...)` (L501) — toma próximo approved y delega a executor.
- `notify_hitl(...)` (L703) — multi-canal con `_parse_channels()` (L691).
- `get_pending_count()` / `get_proposal()` (L784, L798).

**Helpers de notificación:**
- `_notify_via_cowork_bridge()` (L606) — INSERT directo a `embrion_memoria`.
- `_notify_via_telegram()` (L632) — vía `kernel.runner.telegram_notifier.TelegramNotifier`.

**Dataclasses:** `ProposalCreated` (L164), `ExecutionResult` (L175).

**Cliente HTTP propio:** `_SupabaseRest` (L92).

**Dependencia kernel:** lazy import de `kernel.runner.telegram_notifier` (L639).

**Integración:** importado por `embrion_routes.py` (L747) y `runner/proposal_processor.py` (L32).

**Tests:** ✅ `tests/test_embrion_write_policy.py`.

---

### 3.6 `kernel/runner/proposal_processor.py` — 260 LOC

**Doctrina (header):** "NO toca `kernel/embrion_loop.py` (silencio del embrión preservado). Conexión DB independiente."

**Funciones:**
- `_format_execution_message()` (L51), `_notify_post_execute()` (L83).
- `expire_loop(db, stop_event)` (L151).
- `execute_loop(db, registry, notifier, stop_event)` (L169).
- `_install_signal_handlers(loop, stop_event)` (L204).
- `main_async()` (L219) / `main()` (L254) — entrypoint del worker.

**Dependencias kernel:**
```
from kernel.embrion_write_policy import (...)            # L32
from kernel.runner.executor_registry import ExecutorRegistry  # L37
from kernel.runner.telegram_notifier import TelegramNotifier  # L38
```

**Variables de entorno requeridas (header):** `SUPABASE_REST_URL`, `SUPABASE_SERVICE_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `PROPOSAL_EXPIRE_INTERVAL_SEC=60`.

**Integración:** servicio Railway separado. Confirmado en `Dockerfile.worker` + `railway.worker.toml` (top-level del repo, observados en 1A).

**Tests:** ✅ `tests/test_proposal_processor.py`.

---

### 3.7 `kernel/runner/executor_registry.py` — 200 LOC

**Doctrina v1 (Sprint EMBRION-NEEDS-002):** "Default: TODOS los executors son noop. Opt-in real: `payload_json.executor=='real'`."

**Funciones internas:**
- `_is_real(proposal)` (L31).
- `_exec_noop(proposal)` (L39).
- `_exec_external_api_call(proposal)` (L52).
- `_exec_db_write(proposal)` (L98).
- `_exec_code_commit(proposal)` (L146) — TODO (clonar repo, commit, push).

**Clase pública:** `ExecutorRegistry` (L163).

**Dependencia kernel:** `from kernel.embrion_write_policy import ExecutionResult` (L24).

**Tests:** cubierto por `tests/test_proposal_processor.py:55-74` (3 casos: defaults, dispatch, override real). También listado por `tests/test_sprint1_day3.py:342` (smoke `hasattr` check).

---

### 3.8 `kernel/runner/telegram_notifier.py` — 398 LOC

**Diseño:** cliente HTTP directo (sin `python-telegram-bot`). Lee `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` de env.

**Funciones:**
- `_escape_telegram_markdown(text)` (L32).

**Clase pública:** `TelegramNotifier` (L46).

**Sitios de uso (10 sitios verificados via `grep -rn telegram_notifier`):**
- `embrion_loop.py:144` (docstring), `embrion_routes.py` (L46, 511, 965, 1304, 1395), `embrion_write_policy.py:639,647`, `main.py:257,259,346`.

**Tests:** ❌ sin `test_telegram_notifier.py`. Cobertura tangencial en `tests/test_embrion_telegram.py`.

---

### 3.9 `kernel/runner/autonomous_runner.py` — 591 LOC

**Misión (header):** background asyncio task que:
1. Polls Supabase cada `POLL_INTERVAL_S` por `scheduled_jobs` due.
2. Sprint 37: pasa jobs al MOC para priorización dinámica.
3. Re-entra al kernel para cada job.
4. Feedback loop — actualiza `success_rate`.
5. Registra en `job_executions` con `cost_usd` real.
6. Notifica vía Telegram.
7. Maneja recurrencia (daily/weekly).

**Guardrails declarados:** max concurrent=3, anti-recursión `source="scheduled_job"` bloquea `schedule_task`, TTL 30 días auto-cancel, retry hasta `max_retries`.

**Clase pública:** `AutonomousRunner` (L43) — la única.

**Integración:** `main.py:254-272`:
```
from kernel.runner.autonomous_runner import AutonomousRunner
autonomous_runner = AutonomousRunner(...)
await autonomous_runner.start()
app.state._autonomous_runner = autonomous_runner
```
+ `set_autonomy_deps(db=..., runner=autonomous_runner)` en L279, y consumo en L575/L583.

**Tests:** ❌ sin `test_autonomous_runner.py`. **Gap declarado.**

---

### 3.10 `kernel/audit_middleware.py` — 279 LOC — **NO EN MAIN**

**Origen:** branch `sprint/s-003-b-audit-middleware-pentest`, commit `29dc298` ("feat(security): Sprint S-003.B audit middleware + linter v1.1 (Hilo Ejecutor 2)" 2026-05-10).

**Funciones públicas (verificadas vía `git show`):**
- `redact_secrets(value)` (L96), `redact_headers(headers)` (L105).
- `extract_caller_identity(request)` (L118).
- `get_supabase_credentials()` (L147).
- `_insert_audit_log(record)` (L163) — async fire-and-forget.

**Clase pública:** `AuditMiddleware(BaseHTTPMiddleware)` (L204).

**Performance gate declarado (header):** <5% p50 latency overhead. INSERT fire-and-forget vía `asyncio.create_task()`.

**Orden ASGI declarado en docstring:**
```
1. CORSMiddleware
2. APIKeyAuthMiddleware (kernel/auth.py — NO TOCAR)
3. AuditMiddleware ← este
4. RateLimiterMiddleware
```

**Estado actual (verificado):**
- `git show 29dc298 --stat | grep main.py` → **vacío**. El commit NO modifica `kernel/main.py`.
- `git show 29dc298:kernel/main.py | grep -i "AuditMiddleware\|audit_middleware\|audit_routes"` → **vacío**.
- **Conclusión:** el middleware existe en código pero NO está enganchado al ASGI stack ni siquiera dentro de su propia branch. **Spec firmado en docstring NO ejecutado.** Necesita una segunda iteración de wiring antes de cualquier merge.

**Tests:** `tests/__pycache__/test_audit_middleware.cpython-311-pytest-9.0.3.pyc` existe pero el `.py` fuente NO está en disco (ni en `main` ni listado en `git show 29dc298 --stat`). Bytecode huérfano.

---

### 3.11 `kernel/audit_routes.py` — 287 LOC — **NO EN MAIN**

**Origen:** mismo commit `29dc298`, mismo branch.

**Modelos Pydantic:** `AuditLogEntry` (L42), `AuditLogsResponse` (L60), `AuditStats` (L68).

**Endpoints:**
- `list_audit_logs(...)` (L122) — `GET /v1/audit/logs` con cursor pagination y filtros.
- `get_audit_log(log_id)` (L174) — `GET /v1/audit/logs/{id}`.
- `get_audit_stats()` (L184).

**Helpers:** `_get_supabase_creds()` (L83), `_supabase_get(path, params)` (L95).

**Estado:** mismo problema que `audit_middleware.py` — el commit NO incluye `app.include_router(audit_router)` en `main.py` ni en main ni en su branch.

**Tablas SQL mencionadas en commit:** `migrations/sql/0009_kernel_audit_log.sql` + `0010_kernel_audit_log_truncate_guard.sql` (BEFORE TRUNCATE trigger).

**Tests:** ❌ ninguno.

---

### 3.12 `kernel/main.py` — 3232 LOC

**Función principal:** `lifespan(app: FastAPI)` (L89) — startup/shutdown del proceso web.

**Routers registrados (`include_router`) — 21 sitios:**
`autonomy_router` (280), `mission_router` (298), `dossier_router` (299), `usage_router` (336), `finops_router` (376), `memory_router` (419), `deployments_router` (430), `agui_router` (441), `alerts_router` (450), `moc_router` (596), `planner_router` (604), `embrion_router` (618), `a2a_router` (748), `magna_router` (1092), `memento_router` (1238, prefix `/v1/memento`), `_catastro_routes.router` (1267, prefix `/v1/catastro`), `e2e_router` (1303), `traffic_router` (1327), `openai_router` (1704), `brand_router` (1709).

**ASGI middlewares (`add_middleware`):**
- L1680: `CORSMiddleware`.
- L1692: `APIKeyAuthMiddleware`.
- L1699: `RateLimiterMiddleware`.

**Endpoints definidos directamente en `main.py`:**
- `/v1/chat` (L1789), `/v1/chat/stream` (L2184), `/v1/step` (L2212), `/v1/cancel` (L2243), `/v1/feedback` (L2261), `/v1/status/{run_id}` (L2344), `/v1/replay/{run_id}` (L2362).
- Background jobs: `create_background_job` (L1999), `get_background_job` (L2046), `cancel_background_job` (L2066), `stream_background_job_progress` (L2083), `list_background_jobs` (L2121).
- `trigger_backup` (L2162).

**Modelos Pydantic locales:** `ChatRequest` (1718), `ChatResponse` (1731), `StepRequest` (1753), `CancelRequest` (1759), `FeedbackRequest` (1764), `BackgroundJobRequest` (1883), `BackgroundJobResponse` (1893), `BackgroundJobStatus` (1899), `BackupRequest` (2155).

**Sub-arrancadas en `lifespan()` (verificado):** `autonomous_runner`, `embrion_loop`, `embrion_scheduler`, magna_classifier injection, dependencias de routers (set_*_deps).

**Observación 1B:** `main.py` con 3232 LOC y 21 routers + 3 middlewares + 18 endpoints es candidato a refactor estructural (split por dominio). NO es scope 1B proponer cambios — solo declarar el riesgo de fricción cognitiva.

**Tests:** sin `test_main.py`. Cobertura indirecta vía `tests/test_e2e_kernel_*.py` (no auditados aquí).

---

### 3.13 `kernel/engine.py` — 1107 LOC

**Clase única:** `LangGraphKernel(KernelInterface)` (L62).

**Métodos públicos (interface contract):**
- `__init__()` (L76).
- `_build_graph()` (L159) — construye el `StateGraph` LangGraph con 8 nodos (Sprint 19 declarado en header).
- `start_run(input)` (L242) — entry point principal.
- `step(run_id, input)` (L518) — continuar HITL-paused run.
- `checkpoint(run_id)` (L601), `resume(run_id)` (L626).
- `cancel(run_id, reason)` (L630) — kill switch.
- `stream(input)` (L667) — async iterator para SSE.
- `get_status(run_id)` (L1062), `get_graph_mermaid()` (L1083), `get_graph_ascii()` (L1090).
- `register_hook(event, callback)` (L1074), `_fire_hook()` (L1099).
- `_log_usage()` (L473).

**Routing helper:** `_should_dispatch_tools_fn()` (L127) — gate para Sprint 2 "Las Manos".

**Header doctrinal:** "LangGraph es un motor intercambiable. KernelInterface es nuestro contrato."

**Dependencias declaradas en header:** `kernel/nodes.py` (8 nodos), `kernel/multi_agent.py` (Multi-Agent Dispatcher), `memory/mempalace_bridge.py`. NO auditados aquí (1C).

**Tests:** ❌ sin `test_engine.py` (`tests/test_brand_engine.py` es OTRO motor — Brand Engine, no LangGraphKernel). **Gap declarado y crítico** dado que es el motor central.

---

### 3.14 `kernel/agui_adapter.py` — 440 LOC

**Endpoints AG-UI:** 2 (`grep -cE "@router\." = 2`).
- `agui_run(req, request)` (L115) — `POST` SSE streaming.
- `agui_info()` (L428) — metadata.

**Modelo Pydantic:** `AGUIRunRequest` (L67).

**Constantes:** `AGUIEventType` (L97) — eventos del protocolo (`RUN_STARTED`, `THINKING_STATE`, etc., declarados en header).

**Helpers SSE:** `_sse_event(event_type, data)` (L81), `_heartbeat()` (L87).

**Inyección:** `set_dependencies(kernel, thoughts_store)` (L57).

**Doctrina (header Sprint 42 fix v2):** usa `asyncio.Queue` para desacoplar streaming del kernel del heartbeat — evita `asyncio.wait_for()` que cancela el async generator y corrompe su estado.

**Integración:** `main.py:437-441`:
```
from kernel.agui_adapter import router as agui_router
from kernel.agui_adapter import set_dependencies as set_agui_deps
app.include_router(agui_router)
```

**Tests:** ❌ sin `test_agui_adapter.py`. **Gap declarado** dado que es el puente con el Command Center y la app móvil.

---

### 3.15 `kernel/state.py` — 109 LOC

**Estructura única:** `MonstruoState(TypedDict, total=False)` (L17).

**Lifecycle phases declarados (verificado leyendo el archivo completo):**
1. **Input** (intake): `run_id`, `user_id`, `channel`, `message`, `attachments`, `context`, `parent_run_id`.
2. **Routing** (classify+route): `intent`, `model`, `fallback_models`, `route_reason`.
3. **Enrichment** (enrich): `conversation_context`, `relevant_memories`, `knowledge_entities`, `system_prompt`, `enriched`.
4. **Execution** (execute): `response`, `tool_calls`, `tokens_in/out`, `cost_usd`, `latency_ms`, `model_used`, `execution_attempts`.
5. **Tool Calling** (Sprint 2): `pending_tool_calls`, `tool_results`, `tool_loop_count` (max 3).
6. **Memory** (memory_write): `memory_written`, `entities_extracted`, `relations_extracted`, `episode_id`.
7. **Output** (respond): `final_response`, `response_channel`.
8. **Meta**: `status`, `step_count`, `events`, `error`, `error_type`, `cancelled`, `cancel_reason`, `started_at`, `completed_at`.
9. **HITL**: `needs_human_approval`, `human_approval_reason`, `human_response`.
10. **Supervisor** (Sprint 39): `skip_enrich`, `supervisor_tier`.
11. **Multi-Agent** (Sprint 21): `agent_type`, `agent_system_prompt`, `agent_tools`.
12. **Governance** (Action Envelope v2.0): `action_envelope`, `policy_decision`, `risk_level`, `trust_ring`.

**Doctrina (header):** "El estado es nuestro. LangGraph solo lo transporta."

**Tests:** ❌ sin `test_state.py`. **Aceptable** — es un TypedDict de schema, sin lógica.

---

## 4. Inconsistencias y gaps detectados (1B)

1. **Branch S-003.B nunca completó wiring.** `audit_middleware.py` y `audit_routes.py` (566 LOC combinados) existen pero el commit `29dc298` NO modifica `kernel/main.py` para registrarlos. Riesgo: Sprint S-003.B Tarea 1 declarada "completa" en `COWORK_DECISIONES_VIVAS §3` (estado 🟡 "en branch Cowork pendiente push"), pero internamente la pieza está rota.
2. **Bytecode huérfano:** `tests/__pycache__/test_audit_middleware.cpython-311-pytest-9.0.3.pyc` sin `.py` fuente. Limpiar `__pycache__` o restaurar el test.
3. **Gap sistémico de tests 1:1** — sin test directo: `embrion_routes`, `embrion_scheduler`, `telegram_notifier`, `autonomous_runner`, `engine.py`, `agui_adapter`, `main.py`. **El más crítico es `engine.py`** — motor central LangGraph sin `test_engine.py`. `tests/test_brand_engine.py` es OTRO motor.
4. **`main.py` con 3232 LOC + 21 routers + 18 endpoints locales** — densidad alta. Refactor estructural (split por dominio: chat, jobs, backup, status, replay) sería sano pero NO es 1B proponer cambios.
5. **`embrion_loop.py` (2067 LOC) y `engine.py` (1107 LOC)** — los dos archivos más grandes del núcleo. `embrion_loop.py` está bajo Doctrina del Silencio, lo cual hace su tamaño aceptable; `engine.py` no tiene esa protección y carga 12+ métodos públicos en una sola clase.
6. **Lazy imports cruzados** entre `embrion_routes.py` ↔ `runner/telegram_notifier.py` (5 sitios) y entre `embrion_write_policy.py` ↔ `runner/telegram_notifier.py` (1 sitio) — patrón aceptable para evitar circular imports, pero merece revisión arquitectónica.
7. **`audit_middleware` declara orden ASGI específico** (CORS → APIKeyAuth → AuditMiddleware → RateLimiter), pero `main.py` actual solo tiene 3 middlewares (CORS, APIKeyAuth, RateLimiter) — al integrar habrá que insertar AuditMiddleware entre los dos últimos sin romper el orden de auth.

---

## 5. Estado: vivo / aislado / pendiente integración

- **Vivo y operativo en producción Railway:** `embrion_loop`, `embrion_routes`, `embrion_budget`, `embrion_scheduler`, `embrion_write_policy`, `runner/proposal_processor` (worker), `runner/executor_registry`, `runner/telegram_notifier`, `runner/autonomous_runner`, `main`, `engine`, `agui_adapter`, `state`.
- **Aislado / pendiente integración:** `audit_middleware`, `audit_routes` (branch sin wiring).
- **Bajo Doctrina del Silencio:** `embrion_loop` — solo lectura.

---

## 6. Autoaudit (Cowork sobre Cowork)

- ✅ Documento ≤ 8 páginas (estimado ~7).
- ✅ Cada afirmación tiene path + número de línea o output de bash citado (ej: `wc -l`, `git show 29dc298`, `grep -nE`, `grep -cE`).
- ✅ NO modifiqué `embrion_loop.py` (solo lectura).
- ✅ NO uso "Hilo A" ni "Hilo B" para Cowork. Cowork = Arquitecto Jefe.
- ✅ Honestidad pura: gaps de tests declarados explícitamente, branch S-003.B descrita como rota internamente, `engine.py` señalado como hueco crítico.
- ⚠ Limitación reconocida 1: NO entré a evaluar la lógica interna de los métodos. Solo inventarié superficie pública. Ej: `_judge_before` puede tener bug que esta auditoría no detectaría.
- ⚠ Limitación reconocida 2: Los "tests asociados" se buscaron por nombre de archivo. Pueden existir tests en archivos con nombres distintos que cubran funcionalidad de estos módulos (ej: `test_e2e_kernel_*.py`). Una auditoría de cobertura real (`pytest --cov`) queda fuera del scope 1B.
- ⚠ Limitación reconocida 3: NO ejecuté el código (no booted Railway, no smoke test). El estado "✅ integrado" significa "el código de cableado existe en `main.py`", NO "verificado que arranque sin error".

---

## 7. Para próxima sub-fase 1C

Notas para 1C basadas en evidencia recolectada hoy:

1. **Subdirectorios `kernel/` no auditados que merecen 1C:** `brand/`, `transversales/`, `vanguard/`, `catastro/`, `collective/`, `sovereignty/`, `embrion_specializations/`, `embriones/`, `dashboards/`, `e2e/`, `browser/`, `i18n/`. Algunos están listados en `COWORK_BASE_CONOCIMIENTO §3`.
2. **Cruce pendiente kernel/ vs root:** `transversal/` (root, 7 .py) vs `kernel/transversales/` (canónico). Ya señalado en 1A. Sigue pendiente decidir delete vs archive.
3. **Auditoría dirigida del motor (engine.py):** dado que es el motor LangGraph y carece de test 1:1, una 1C-bis específica de `engine.py` + `nodes.py` + `multi_agent.py` daría señal alta de salud arquitectónica.
4. **Audit de `kernel/runner/`:** este dir tiene 4 archivos auditados aquí. Verificar si hay más archivos (`ls kernel/runner/`) y si `autonomous_runner` ↔ `proposal_processor` comparten doctrina o solapan responsabilidades (ambos son "workers").
5. **Sprint S-003.B requiere remediación antes de merge:** PR debe agregar `app.add_middleware(AuditMiddleware)` + `app.include_router(audit_router)` en `main.py` ANTES de pushear a `main`. Recomendación: cerrar la branch sin merge hasta que el wiring sea parte del commit.
6. **Test gaps prioritarios** (orden propuesto Sprint S-XXX):
   1. `test_engine.py` (motor central, sin coverage).
   2. `test_agui_adapter.py` (puente con app móvil + Command Center).
   3. `test_autonomous_runner.py` (worker de jobs programados).
   4. `test_embrion_scheduler.py` (5 tareas default sin test).
7. **Limpieza cosmética:** eliminar `tests/__pycache__/test_audit_middleware.cpython-311-pytest-9.0.3.pyc` (bytecode huérfano).

---

*Generado por Cowork 2026-05-10 como Sub-Fase 1B del Estudio Forense del Monstruo. Próxima sub-fase: 1C — audit `kernel/` módulos especializados (`brand/`, `transversales/`, `vanguard/`, `catastro/`, `collective/`, `sovereignty/`).*
