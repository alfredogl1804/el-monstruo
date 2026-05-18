# GATE 3.4 — Module Maturity Evidence Pack v1.1
**Estado:** `EVIDENCE_PACK_v1_1` (Microfix consistency drift)
**Fecha:** 2026-05-18
**Commit de referencia:** `a6be791` (Sprint CATASTRO-WIRING-001)

## Reglas duras de este documento
1. **NO diseñar arquitectura.** Este documento es auditoría estática de lo que EXISTE hoy en `kernel/`.
2. **NO canonizar.** Esto es evidencia, no doctrina.
3. **NO actualizar APP_VISION.** Cero especulación sobre lo que los módulos "deberían" hacer.
4. **NO cerrar la fase PRE-IA.** La fase `ARQUITECTO_EN_CERTIFICACION_AVANZADO` se mantiene.
5. **NO proponer sprint nuevo.** Sin firma T1 explícita, no hay sprint derivado de este audit.

## Resumen Ejecutivo

Auditoría estática de 14 módulos del kernel.
- **M4_Tested:** 6/14 (magna_routes, e2e/routes, e2e/traffic/routes, rotor/recharge, guardian_runner/runner, cowork_routes)
- **M3_Wired:** 7/14 (moc_routes, finops_routes, memory_routes, catastro/recommendation, embrion_scheduler, a2a_routes, embriones/*)
- **M2_Stub:** 1/14 (collective/protocol)
- **M1_Stub:** 0/14
- **M5_Hardened:** 0/14

**Caveat de Madurez M4:**
> **⚠️ IMPORTANTE:** M4_Tested significa que existen tests de lógica o de módulo pasando en `tests/`. NO significa necesariamente route-hardening completo, madurez de UI, 100% error-path coverage, ni preparación para producción (M5).

---

## 1. Módulos M4_Tested (Lógica + Tests)

### 1.1 `magna_routes`
- **Path:** `kernel/magna/magna_routes.py`
- **Endpoints HTTP:** 3 (`/v1/magna/status`, `/v1/magna/classify`, `/v1/magna/context`)
- **Consumidor UI:** No
- **Tests:** Sí (`tests/test_magna_classifier.py` - 11 tests)
- **Riesgo:** Low

### 1.2 `e2e/routes`
- **Path:** `kernel/e2e/routes.py`
- **Endpoints HTTP:** 5 (`/v1/e2e/status`, `/v1/e2e/run`, `/v1/e2e/results`, `/v1/e2e/metrics`, `/v1/e2e/config`)
- **Consumidor UI:** No
- **Tests:** Sí (`tests/test_e2e_pipeline.py` - 14 tests)
- **Riesgo:** Low

### 1.3 `e2e/traffic/routes`
- **Path:** `kernel/e2e/traffic/routes.py`
- **Endpoints HTTP:** 2 (`/v1/traffic/status`, `/v1/traffic/simulate`)
- **Consumidor UI:** No
- **Tests:** Sí (`tests/test_traffic_simulator.py` - 8 tests)
- **Riesgo:** Low

### 1.4 `rotor/recharge`
- **Path:** `kernel/rotor/recharge.py`
- **Endpoints HTTP:** 0
- **Handlers/Tasks:** 1 (`recharge_all_balances`)
- **Consumidor UI:** No
- **Tests:** Sí (`tests/test_rotor_recharge.py` - 6 tests)
- **Riesgo:** Low

### 1.5 `guardian_runner/runner`
- **Path:** `kernel/guardian_runner/runner.py`
- **Endpoints HTTP:** 0
- **Handlers/Tasks:** 1 (`run_guardian_checks`)
- **Consumidor UI:** No
- **Tests:** Sí (`tests/test_guardian_runner.py` - 9 tests)
- **Riesgo:** Low

### 1.6 `cowork_routes`
- **Path:** `kernel/cowork_runtime/cowork_routes.py`
- **Endpoints HTTP:** 2 (`/v1/cowork/status`, `/v1/cowork/sync`)
- **Consumidor UI:** No
- **Tests:** Sí (`tests/test_cowork_sync.py` - 5 tests)
- **Riesgo:** Low

---

## 2. Módulos M3_Wired (Lógica + DB, sin tests dedicados)

### 2.1 `moc_routes`
- **Path:** `kernel/moc/moc_routes.py`
- **Endpoints HTTP:** 6
- **Consumidor UI:** Sí (`apps/mobile/gateway/server.py`)
- **Tests:** No
- **Riesgo:** Medium

### 2.2 `finops_routes`
- **Path:** `kernel/finops/finops_routes.py`
- **Endpoints HTTP:** 2
- **Consumidor UI:** Sí (`apps/mobile/gateway/server.py`)
- **Tests:** No
- **Riesgo:** Medium

### 2.3 `memory_routes`
- **Path:** `kernel/memory/memory_routes.py`
- **Endpoints HTTP:** 8
- **Consumidor UI:** Sí (`apps/mobile/gateway/server.py`)
- **Tests:** No
- **Riesgo:** Medium

### 2.4 `catastro/recommendation`
- **Path:** `kernel/catastro/recommendation.py`
- **Endpoints HTTP:** 8 (vía `catastro_routes.py`)
- **Consumidor UI:** No
- **Tests:** No (solo wiring tests en `test_catastro_wiring.py`)
- **Riesgo:** Medium

### 2.5 `embrion_scheduler`
- **Path:** `kernel/embrion_scheduler.py`
- **Endpoints HTTP:** 0
- **Handlers/Tasks:** 3 (`schedule_next_run`, `cancel_run`, `get_schedule`)
- **Consumidor UI:** No
- **Tests:** No
- **Riesgo:** High (Orquestador core sin tests)

### 2.6 `a2a_routes`
- **Path:** `kernel/a2a/a2a_routes.py`
- **Endpoints HTTP:** 6
- **Consumidor UI:** No
- **Tests:** No
- **Riesgo:** High (Integración externa sin tests)

### 2.7 `embriones/*`
- **Path:** `kernel/embriones/` (brand_engine, tecnico, ventas, etc.)
- **Endpoints HTTP:** 0
- **Consumidor UI:** `indirect_generic_embrion_api` (Gateway consume `/v1/embrion/status`, no los especializados)
- **Tests:** Sí (`tests/test_embriones.py` - tests genéricos de factory)
- **Riesgo:** Medium

---

## 3. Módulos M2_Stub (Stub declarado)

### 3.1 `collective/protocol`
- **Path:** `kernel/collective/protocol.py`
- **Endpoints HTTP:** 0
- **Consumidor UI:** No
- **DB Injected:** False (Schema declarado, pero no inyectado)
- **Tests:** No
- **Riesgo:** High
- **Nota:** El archivo existe (27 KB) y se instancia en `main.py:1011` como `app.state.colectiva = ColectivaProtocol()`, pero la inicialización es vacía, 0 endpoints, 0 tests. Realidad estática por debajo de la canónica.
