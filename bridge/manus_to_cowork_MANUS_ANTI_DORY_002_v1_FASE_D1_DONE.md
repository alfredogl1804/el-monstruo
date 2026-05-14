# MANUS → COWORK — MANUS-ANTI-DORY-002 v1 — FASE D1 DONE

**Estado terminal:** 🔌 **D1 — AUDIT_PENDIENTE**

**Sprint:** MANUS-ANTI-DORY-002 v1
**Fase:** D1 — SupabaseRPCClient real + default factory + tests integration
**Owner:** Manus (este hilo)
**Autoridad:** T1 (Alfredo) + Cowork T2-A (kickoff FASE D firmado 2026-05-14)
**Timestamp:** 2026-05-14 (sandbox UTC)
**Commit:** *(asignado post-push, ver §8)*

---

## 1. Resumen ejecutivo

D1 implementa la **clase concreta** que falta para activar operacionalmente el
`ContextBroker` de FASE B y el wire opt-in de FASE C. Hasta hoy, el broker
existía pero requería que el callsite (`tools/manus_bridge.create_task`) le
pasara un cliente RPC real. Sin esa pieza, el flag `ANTI_DORY_ENABLED=true`
en producción habría fallado en runtime.

D1 entrega:

1. **`kernel/anti_dory/supabase_client.py`** — `HTTPXSupabaseRPCClient`,
   implementación sincrónica del `Protocol SupabaseRPCClient` declarado en
   `kernel/anti_dory/context_broker.py:41`.
2. **`build_default_broker_factory()`** — entry-point que
   `tools/manus_bridge.set_anti_dory_broker_factory()` invoca para obtener un
   `ContextBroker` configurado desde env vars (`SUPABASE_URL`,
   `SUPABASE_SERVICE_KEY`).
3. **10 tests integration** con `httpx.MockTransport` (sin Supabase real).

**NO** se aplican migrations, **NO** se toca Supabase prod, **NO** se enciende
`ANTI_DORY_ENABLED`, **NO** hay cron, **NO** hay self-merge. D2/D3/D4/D5/D6
quedan condicionados a Cowork audit + T1 explícito.

---

## 2. Decisiones técnicas tomadas

### 2.1 Naming sin colisión con el Protocol

El SPEC v1 (§A.5) refiere genéricamente a "SupabaseRPCClient", pero la lectura
binaria del repo reveló que **`SupabaseRPCClient` ya existe como `Protocol`**
en `kernel/anti_dory/context_broker.py:41`. Renombrar el Protocol habría sido
breaking change cross-módulo (importado en `context_broker.py`, `recovery.py`,
`writers.py`).

**Decisión F24 anti-fabricación:** la clase concreta se llama
**`HTTPXSupabaseRPCClient`**, implementa estructuralmente el Protocol sin
heredarlo (Protocols Python no requieren herencia). Cero NO-CRUCE.

### 2.2 Contrato sincrónico, no async

El Protocol declara `call_rpc(name, params) -> Any` como método **sincrónico**.
El callsite (`tools/manus_bridge.create_task`) también es sync. **Decisión:**
`HTTPXSupabaseRPCClient` usa `httpx.Client` (no `httpx.AsyncClient`).

Coherente con el `MockRPCClient` de FASE B (que es sync) y con el callsite.
Inconsistencia documentada vs `memory/supabase_client.py` (async) — pero ese
módulo es async porque `embrion_loop` lo necesita; nuestro broker corre dentro
de `create_task` sync. Sin contradicción material.

### 2.3 Fail-open al nivel del callsite, fail-loud al nivel del cliente

- **Cliente (`HTTPXSupabaseRPCClient.call_rpc`)**: propaga `httpx.HTTPError`
  (timeout, 4xx, 5xx, connection error) hacia arriba **sin tragárselos**.
- **Broker (`ContextBroker.hydrate_prompt`, FASE B `context_broker.py:166-174`)**:
  captura `Exception` y devuelve `attachment_ok=False` con
  `fallback_reason=f"rpc_error:{exc}"`.
- **Callsite (`tools/manus_bridge.create_task`, FASE C)**: si el broker devuelve
  pack vacío, sigue el flujo original sin prefijo (backward compat).

Esto es **fail-open en producción** sin fail-silent en debugging: los logs
estructurados (`anti_dory_rpc_error`) permiten auditoría sin interrumpir UX.

### 2.4 Singleton cacheado por proceso

`build_default_broker()` cachea el broker globalmente (`_GLOBAL_BROKER`) para
reutilizar conexiones TLS de `httpx.Client`. Reset disponible vía
`_reset_global_state_for_tests()` (público pero documentado como test-only).

### 2.5 Sin retry interno

`HTTPXSupabaseRPCClient` **no** implementa retry exponencial. Diseño deliberado:

- El callsite es `create_task` que ya tiene su propio retry (`manus_bridge`
  línea ~190+, `_call_with_retry`).
- Anti-Dory broker debe sumar **mínima latencia** al flujo de creación de hilo.
- Si Supabase está caído, fail-open es preferible a bloquear `task.create`.

---

## 3. Limitaciones esperadas (DSC-G-008 v3 §4)

- **L1 — Sin observabilidad backend todavía.** Los logs estructurados están en
  formato `extra={}` para `logging` estándar, no se exportan a Langfuse ni
  Supabase `runtime_events` aún. D3 (cron) o sprint posterior los conecta.
- **L2 — Sin retry interno.** Justificado en §2.5, pero documentado como
  trade-off.
- **L3 — Tests no validan PostgREST real.** `httpx.MockTransport` simula HTTP
  pero no comportamiento exacto de PostgREST (e.g. error codes
  `PGRST301`/`PGRST302` específicos). Cobertura de error genérica vía status
  code 4xx/5xx.
- **L4 — `_reset_global_state_for_tests` es público.** Necesario para tests
  parametrizados; bandera de visibilidad documentada.

---

## 4. Consecuencias materiales

- **C1 — D2 (migration 0034 GRANTs) ahora es ejecutable**. Sin D1, los GRANTs
  habrían sido inútiles porque ningún cliente real los usaría.
- **C2 — Flag `ANTI_DORY_ENABLED=true` en staging es seguro**: si Supabase no
  está configurado, fail-open. Si está configurado, los RPCs declarados en
  migration 0032 deben responder. **No** activar en prod sin D4 (shadow run).
- **C3 — `tools/manus_bridge.create_task` puede ahora ser invocado con
  `attach_context=True` con efecto real** (no solo con `MockRPCClient`).
- **C4 — Costo TLS de la primera invocación**: ~50-200ms (handshake). Singleton
  amortiza para invocaciones subsecuentes (<5ms overhead esperado).

---

## 5. Evidencia binaria

### 5.1 LOC verbatim (`wc -l`)

```
  349 kernel/anti_dory/supabase_client.py
  268 tests/anti_dory/test_supabase_client.py
  617 total
```

### 5.2 Pytest

```
============================== 28 passed in 0.38s ==============================
```

Breakdown:
- `test_rap_002_harness.py` — 12 PASS (sin regresión)
- `test_manus_bridge_integration.py` — 6 PASS (sin regresión)
- `test_supabase_client.py` — **10 PASS** (nuevos D1)

### 5.3 Tests D1 individuales

```
test_call_rpc_happy_path_returns_decoded_json                  PASSED
test_call_rpc_http_error_raises_httpx_error                    PASSED
test_build_default_broker_with_env_vars_returns_broker         PASSED
test_build_default_broker_without_env_vars_returns_none        PASSED
test_call_rpc_timeout_propagates_to_caller                     PASSED
test_client_implements_protocol_contract                       PASSED
test_constructor_rejects_empty_url                             PASSED
test_constructor_rejects_empty_service_key                     PASSED
test_call_rpc_rejects_invalid_name                             PASSED
test_call_rpc_rejects_non_dict_params                          PASSED
```

### 5.4 Grep secrets (DSC-S enforcement)

```
$ grep -RnE "eyJ[A-Za-z0-9_-]{10,}|sk-[A-Za-z0-9_-]{20,}|postgres://" \
    kernel/anti_dory/supabase_client.py tests/anti_dory/test_supabase_client.py
(0 matches — CLEAN)
```

### 5.5 NO-CRUCE binario

```
$ git diff --stat origin/main -- kernel/cowork_runtime/ tools/cowork_guardian.py kernel/main.py kernel/engine.py
(empty — 0 lines touched in protected paths)
```

### 5.6 Diff stat total vs `origin/main`

Solo 2 archivos nuevos:

```
kernel/anti_dory/supabase_client.py     |  +349  (new file)
tests/anti_dory/test_supabase_client.py |  +268  (new file)
```

---

## 6. Constraints duros respetados (10/10)

- [x] NO self-merge — PR ready-for-review, sin merge automático.
- [x] NO Supabase prod tocado — solo migrations escritas en repo, **no
      aplicadas**.
- [x] NO Railway tocado.
- [x] NO secrets en código (validado por grep).
- [x] NO `ANTI_DORY_ENABLED` activado.
- [x] NO PR #118 tocado.
- [x] NO Mac local tocada.
- [x] Backward compat preservada — `tools/manus_bridge.create_task` sigue
      funcionando exactamente igual sin `attach_context=True`.
- [x] NO-CRUCE total — 0 modificaciones en 4 paths protegidos.
- [x] F24 anti-fabricación — naming `HTTPXSupabaseRPCClient` evita colisión con
      Protocol existente; firma `call_rpc` idéntica al Protocol verbatim.

---

## 7. Próximo paso

**Cowork T2-A audita esta PR contra:**
- DSC-G-008 v3 §4 (limitaciones + consecuencias declaradas).
- Anti-F24, Anti-F26.
- NO-CRUCE en 4 paths protegidos.
- Contract fidelity con Protocol existente.

**Si verdict GREEN:** Cowork mergea PR via `gh pr merge --squash`.
**Si verdict AMBER:** patches discretos en misma rama.
**Si verdict RED:** revert + post-mortem.

**FASE D2 (migration 0034 con GRANTs reales) queda como
`READY_FOR_T1_APPROVAL`**, condicionada a Cowork GREEN sobre D1.

---

## 8. Metadata commit

- **Branch:** `sprint/MANUS-ANTI-DORY-002-fase-d1-supabase-client`
- **Commit:** *(asignado tras push)*
- **PR:** *(número asignado tras `gh pr create`)*
- **Base:** `main` (HEAD `d95a725`)
- **Reviewer:** Cowork T2-A
- **Draft:** **NO** — ready-for-review

---

## 9. Regla operativa LOC-VERBATIM cumplida

Conforme regla introducida en PR #125 cleanup: toda métrica LOC futura
**proviene de `wc -l` verbatim**, no estimación narrativa. Cumplido en §5.1.

---

**Frase canónica:** 🔌 **MANUS-ANTI-DORY-002 v1 FASE D1 — AUDIT_PENDIENTE**

Cowork standby. Manus standby para D2 post-audit.
