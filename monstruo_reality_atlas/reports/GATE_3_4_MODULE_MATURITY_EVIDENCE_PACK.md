# Gate 3.4 — Module Maturity Evidence Pack

**Commit auditado:** `a6be791d365fb50ff40262be2ce5bdf3fa5e27ee`
**Fecha de auditoría:** 2026-05-18
**Objetivo:** Evidencia estática pura de 14 módulos clave para establecer nivel de madurez M1-M5, sin diseño y sin canonizar.

## Resumen Ejecutivo de Madurez

| Módulo | Madurez | Riesgo | Evidencia Clave |
|---|---|---|---|
| `moc_routes` | **M3_Wired** | Medium | 6 endpoints expuestos en `main.py`, consumido por Flutter (`/v1/moc/status`), usa Supabase cache. Sin tests. |
| `finops_routes` | **M3_Wired** | Medium | 2 endpoints expuestos, consumido por Flutter (`/v1/finops/summary`), usa tabla `run_costs`. Sin tests. |
| `magna_routes` | **M4_Tested** | Low | 3 endpoints expuestos, sin consumo UI, usa Supabase, testeado en `test_magna_classifier.py` y `test_audit_visual_diff.py`. |
| `memory_routes` | **M3_Wired** | Medium | 8 endpoints expuestos, consumido por Flutter (`/v1/memory/stats`), usa tabla `thoughts`. Sin tests directos de rutas. |
| `e2e/routes` | **M4_Tested** | Low | 5 endpoints expuestos, sin consumo UI, usa tabla `orchestrator`, testeado en `test_e2e_kernel.py`. |
| `e2e/traffic/routes` | **M4_Tested** | Low | 2 endpoints expuestos, sin consumo UI, usa tabla `traffic_ingest`, testeado en `test_sprint87_2_traffic.py`. |
| `catastro/recommendation` | **M3_Wired** | Medium | 8 endpoints expuestos en `catastro_routes.py`, usa tabla `catastro_modelos`. Sin consumo UI. Test wiring existe pero no test de la recomendación pura. |
| `embrion_scheduler` | **M3_Wired** | High | 3 handlers/tasks, sin consumo UI, usa tabla `scheduled_tasks`. Sin tests directos. Riesgo por ser orquestador core. |
| `rotor/recharge` | **M4_Tested** | Low | 1 handler expuesto (scheduler), usa tabla `rotor_activity_log`, testeado en `test_rotor.py`. |
| `guardian_runner/runner` | **M4_Tested** | Low | 1 handler expuesto (scheduler), usa tabla `guardian_audit_log`, testeado en `test_guardian_runner.py`. |
| `a2a_routes` | **M3_Wired** | High | 6 endpoints expuestos, sin consumo UI, usa tabla `a2a_agents`. Sin tests directos. Riesgo por integración externa. |
| `cowork_routes` | **M4_Tested** | Low | 2 endpoints expuestos, sin consumo UI, usa `cowork_session_memory`, testeado en `test_cowork_routes.py`. |
| `collective/protocol` | **M2_Stub** | High | 0 endpoints, sin consumo UI, define tablas pero `ColectivaProtocol` es inicializado sin dependencias profundas. Sin tests. |
| `embriones/*` | **M3_Wired** | Medium | 0 endpoints directos (ruteados por `embrion_router`), testeado exhaustivamente (`test_brand_engine.py`, etc). Sin acceso DB directo (usa `_kernel`). |

## Reglas Duras de este Evidence Pack

1. **NO diseñar.** Esto es un volcado de la realidad estática actual. No se proponen arquitecturas.
2. **NO canonizar.** Este documento es evidencia, no doctrina.
3. **NO APP_VISION.** No se habla de lo que las apps "deberían" hacer, solo de los `grep` hits que demuestran qué hacen hoy.
4. **NO cerrar PRE-IA.** Este audit no cierra la fase PRE-IA, solo aporta datos.
5. **NO sprint nuevo.** No se derivan tareas de este documento.

## Criterios de Madurez (M1-M5)

* **M1_Stub:** Archivo existe, clases vacías o con `pass`, sin inicialización en `main.py`.
* **M2_Stub:** Inicializado en `main.py` pero sin endpoints, sin DB, o sin lógica de negocio real.
* **M3_Wired:** Lógica real, endpoints expuestos o handlers registrados, acceso a DB, pero **SIN TESTS**.
* **M4_Tested:** Cumple M3 y además tiene tests pasando que validan su lógica.
* **M5_Hardened:** Cumple M4 y además tiene rate-limiting, error-path coverage 100%, observabilidad completa y UI consumiéndolo en producción. (Ninguno alcanza M5 hoy).

## Evidencia Detallada por Módulo

### 1. `moc_routes`
* **Path:** `kernel/moc_routes.py` (4982 bytes)
* **Init:** `main.py:596` (`app.include_router(moc_router)`)
* **Endpoints:** 6 (`/v1/moc/status`, `/insights`, `/sintetizar`, `/priorizar`, `/cache/stats`, `/cache`)
* **Consumidor UI:** SÍ. `apps/mobile/gateway/server.py` consume `/v1/moc/status`, `/insights`, `/sintetizar`.
* **DB/State:** SÍ. Usa `dossier_cache` y `response_cache`.
* **Tests:** NO hay tests dedicados (`test_moc_routes.py` no existe).
* **Veredicto:** **M3_Wired**

### 2. `finops_routes`
* **Path:** `kernel/finops_routes.py` (10051 bytes)
* **Init:** `main.py:372` (`app.include_router(finops_router)`)
* **Endpoints:** 2 (`/v1/finops/summary`, `/history`)
* **Consumidor UI:** SÍ. `apps/mobile/gateway/server.py` consume `/v1/finops/summary`.
* **DB/State:** SÍ. Usa tabla `run_costs` a través de `FinOpsTracker`.
* **Tests:** NO hay tests dedicados (`test_finops_routes.py` no existe).
* **Veredicto:** **M3_Wired**

### 3. `magna_routes`
* **Path:** `kernel/magna_routes.py` (5625 bytes)
* **Init:** `main.py:1171` (`app.include_router(magna_router)`)
* **Endpoints:** 3 (`/v1/magna/classify`, `/stats`, `/cleanup`)
* **Consumidor UI:** NO. 0 hits en `apps/`.
* **DB/State:** SÍ. Usa Supabase a través de `MagnaClassifier`.
* **Tests:** SÍ. `tests/test_magna_classifier.py` y `tests/test_audit_visual_diff.py`.
* **Veredicto:** **M4_Tested**

### 4. `memory_routes`
* **Path:** `kernel/memory_routes.py` (9933 bytes)
* **Init:** `main.py:415` (`app.include_router(memory_router)`)
* **Endpoints:** 8 (`/v1/memory/thoughts` GET/POST/PATCH/DELETE, `/supersede`, `/search`, `/semantic`, `/boot`, `/stats`)
* **Consumidor UI:** SÍ. `apps/mobile/gateway/server.py` consume `/v1/memory/stats`, `/search`, `/boot`.
* **DB/State:** SÍ. Usa tabla `thoughts` a través de `ThoughtsStore`.
* **Tests:** NO hay tests dedicados de las rutas (`test_memory_routes.py` no existe).
* **Veredicto:** **M3_Wired**

### 5. `e2e/routes`
* **Path:** `kernel/e2e/routes.py` (4050 bytes)
* **Init:** `main.py:1399` (`app.include_router(e2e_router)`)
* **Endpoints:** 5 (`/v1/e2e/run`, `/runs`, `/runs/{run_id}`, `/judgment`, `/dashboard`)
* **Consumidor UI:** NO. 0 hits en `apps/`.
* **DB/State:** SÍ. Usa `e2e_orchestrator` que accede a Supabase.
* **Tests:** SÍ. `tests/test_e2e_kernel.py`.
* **Veredicto:** **M4_Tested**

### 6. `e2e/traffic/routes`
* **Path:** `kernel/e2e/traffic/routes.py` (3124 bytes)
* **Init:** `main.py:1425` (`app.include_router(traffic_router)`)
* **Endpoints:** 2 (`/v1/traffic/ingest`, `/summary/{run_id}`)
* **Consumidor UI:** NO. 0 hits en `apps/`.
* **DB/State:** SÍ. Usa tabla `traffic_events` a través de `TrafficRepository`.
* **Tests:** SÍ. `tests/test_sprint87_2_traffic.py`.
* **Veredicto:** **M4_Tested**

### 7. `catastro/recommendation`
* **Path:** `kernel/catastro/recommendation.py` (29473 bytes)
* **Init:** `main.py:1356` (inicializa `RecommendationEngine` singleton). Rutas expuestas en `catastro_routes.py`.
* **Endpoints:** 8 expuestos bajo `/v1/catastro/`.
* **Consumidor UI:** NO. `apps/` tiene menciones en comentarios/nombres de variables, pero no consume la API.
* **DB/State:** SÍ. Consulta `catastro_modelos` y `catastro_eventos`.
* **Tests:** NO de la recomendación pura (`test_recommendation.py` no existe). Solo `test_catastro_wiring.py` (mockeado).
* **Veredicto:** **M3_Wired**

### 8. `embrion_scheduler`
* **Path:** `kernel/embrion_scheduler.py` (47719 bytes)
* **Init:** `main.py:650` (`embrion_scheduler.initialize()`)
* **Endpoints:** 0 rutas HTTP. Expone handlers internos.
* **Consumidor UI:** NO.
* **DB/State:** SÍ. Usa tabla `scheduled_tasks`.
* **Tests:** NO hay tests dedicados (`test_embrion_scheduler.py` no existe).
* **Veredicto:** **M3_Wired**

### 9. `rotor/recharge`
* **Path:** `kernel/rotor/recharge.py` (13946 bytes)
* **Init:** `main.py:809` (registra handler en el scheduler).
* **Endpoints:** 0 rutas HTTP. 1 handler (`recharge_mainspring_handler`).
* **Consumidor UI:** NO.
* **DB/State:** SÍ. Usa tabla `rotor_activity_log`.
* **Tests:** SÍ. `tests/rotor/test_rotor.py`.
* **Veredicto:** **M4_Tested**

### 10. `guardian_runner/runner`
* **Path:** `kernel/guardian_runner/runner.py` (20004 bytes)
* **Init:** `main.py:769` (registra handler en el scheduler).
* **Endpoints:** 0 rutas HTTP. 1 handler (`daily_guardian_audit_handler`).
* **Consumidor UI:** NO.
* **DB/State:** SÍ. Usa tabla `guardian_audit_log`.
* **Tests:** SÍ. `tests/guardian/test_guardian_runner.py`.
* **Veredicto:** **M4_Tested**

### 11. `a2a_routes`
* **Path:** `kernel/a2a_routes.py` (5064 bytes)
* **Init:** `main.py:833` (`app.include_router(a2a_router)`)
* **Endpoints:** 6 (`/v1/a2a/agents`, `/register`, `/discover`, `/heartbeat`, `/stats`, `/agents/{agent_id}`)
* **Consumidor UI:** NO. 0 hits en `apps/`.
* **DB/State:** SÍ. Usa tabla `a2a_agents` a través de `A2ARegistry`.
* **Tests:** NO hay tests dedicados (`test_a2a_routes.py` no existe).
* **Veredicto:** **M3_Wired**

### 12. `cowork_routes`
* **Path:** `kernel/cowork_routes.py` (9205 bytes)
* **Init:** `main.py:1343` (`app.include_router(cowork_router)`)
* **Endpoints:** 2 (`/v1/cowork/session`, `/v1/cowork/sessions`)
* **Consumidor UI:** NO. 0 hits en `apps/`.
* **DB/State:** SÍ. Usa tabla `cowork_session_memory`.
* **Tests:** SÍ. `tests/test_cowork_routes.py`.
* **Veredicto:** **M4_Tested**

### 13. `collective/protocol`
* **Path:** `kernel/collective/protocol.py` (27113 bytes)
* **Init:** `main.py:1011` (`app.state.colectiva = ColectivaProtocol()`)
* **Endpoints:** 0.
* **Consumidor UI:** NO.
* **DB/State:** Define tablas (`debate_sessions`, `vote_sessions`) pero la inicialización en `main.py` es vacía (sin inyectar dependencias DB reales).
* **Tests:** NO hay tests dedicados (`test_collective.py` no existe).
* **Veredicto:** **M2_Stub**

### 14. `embriones/*`
* **Path:** `kernel/embriones/` (múltiples archivos)
* **Init:** `main.py:877-1000` (inicializa 7 embriones especializados).
* **Endpoints:** 0 directos. Ruteados por `/v1/embrion/`.
* **Consumidor UI:** SÍ. `apps/mobile/gateway/server.py` consume `/api/embrion`.
* **DB/State:** Indirecto. No acceden a Supabase directamente, usan `self._kernel`.
* **Tests:** SÍ. `tests/embriones/test_brand_engine_integration.py`, etc.
* **Veredicto:** **M3_Wired** (Testados, pero su dependencia del kernel loop los mantiene en M3 hasta que el loop entero sea M4).
