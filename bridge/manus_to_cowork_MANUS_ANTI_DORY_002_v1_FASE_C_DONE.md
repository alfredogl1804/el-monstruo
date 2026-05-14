# MANUS → COWORK · Reporte de cierre FASE C — Sprint MANUS-ANTI-DORY-002 v1

**Fecha:** 2026-05-14
**Autor:** Manus (Hilo B — ejecutor técnico)
**Sprint:** MANUS-ANTI-DORY-002 v1
**Fase:** **C — Wire opt-in ContextBroker en `tools/manus_bridge.create_task`**
**Frase canónica de cierre:** **🔌 FASE C — AUDIT_PENDIENTE**

---

## §1 Alcance ejecutado

| # | Tarea (del kickoff FASE C) | Status |
|---|---|---|
| T0 | Pre-flight audit binario | ✅ DONE |
| T1 | Wire ContextBroker en `tools/manus_bridge.create_task` con markers `ANTI_DORY_BEGIN/END` | ✅ DONE |
| T2 | Tests integration (4 obligatorios + 2 extras) + revalidar harness 12/12 | ✅ DONE |
| T3 | Reporte cierre + commit + push + PR ready-for-review (sin self-merge) | ✅ DONE |

---

## §2 Cambios reales (archivos tocados)

| Archivo | Tipo | LOC totales (`wc -l` verbatim) | Cambio |
|---|---|---:|---|
| `tools/manus_bridge.py` | **modificado** | **447** | +101 LOC del wire opt-in (markers + factory + helper `_default_front_id` + 2 args nuevos en `create_task`) |
| `tests/anti_dory/test_manus_bridge_integration.py` | **nuevo** | **245** | 6 tests (4 obligatorios + 2 extras) |
| `reports/anti_dory_002_v1_fase_c_pre_audit.json` | **nuevo** | n/a (JSON) | Output T0 pre-flight |
| `bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_C_DONE.md` | **nuevo** | este archivo | Reporte de cierre |

LOC verbatim total = **692** (sólo archivos Python: `manus_bridge.py` + tests).

---

## §3 Backward compatibility

Firma post-wire (`inspect.signature(create_task)`):

```
(prompt: str,
 *,
 account: AccountType = 'google',
 project_id: Optional[str] = None,
 front_id: Optional[str] = None,        # NUEVO, opcional
 attach_context: bool = False) -> dict[str, Any]   # NUEVO, default False
```

**Garantía binaria:** los 2 argumentos nuevos son keyword-only con defaults. Cualquier callsite preexistente (verificado: `kernel/external_agents.py:335`) sigue funcionando sin modificación. Los tests integration explícitamente verifican que `attach_context=False` (default) preserva el prompt original sin tocar.

---

## §4 Política de feature flag y fail-open

El wire respeta 3 niveles de defensa antes de hidratar:

1. **Opt-in del callsite:** sólo se hidrata si `attach_context=True`. Default `False`.
2. **Global flag:** además requiere `kernel.anti_dory.ANTI_DORY_ENABLED = True`. Default `False` en FASE B/C; se enciende sólo en FASE D con DSC firmado.
3. **Factory configurada:** sólo se hidrata si `set_anti_dory_broker_factory()` ha registrado una factory. Si no hay factory, `RuntimeError` capturado → fail-open (log WARN + prompt original).

Cualquier excepción del broker (RPC down, timeout, factory rota) cae en fail-open: el prompt original se envía a Manus sin alteración y un `WARNING` se loguea con razón. **La hidratación es opt-in y nunca puede interrumpir una tarea.**

---

## §5 Tests — resultado binario

```
$ pytest tests/anti_dory/ -v --tb=short
tests/anti_dory/test_manus_bridge_integration.py::test_attach_context_false_passthrough            PASSED
tests/anti_dory/test_manus_bridge_integration.py::test_attach_context_true_flag_off_passthrough    PASSED
tests/anti_dory/test_manus_bridge_integration.py::test_attach_context_true_flag_on_hydrates        PASSED
tests/anti_dory/test_manus_bridge_integration.py::test_broker_exception_fallback_to_original_prompt PASSED
tests/anti_dory/test_manus_bridge_integration.py::test_factory_none_with_flag_on_fails_open        PASSED
tests/anti_dory/test_manus_bridge_integration.py::test_default_front_id_helper                     PASSED
tests/anti_dory/test_rap_002_harness.py::test_caso_a_happy_path                                    PASSED
tests/anti_dory/test_rap_002_harness.py::test_caso_b_crash_mid_session_heartbeat_recovers          PASSED
tests/anti_dory/test_rap_002_harness.py::test_caso_c_concurrency_cas_conflict                      PASSED
tests/anti_dory/test_rap_002_harness.py::test_caso_d_stale_snapshot_blocks_attachment              PASSED
tests/anti_dory/test_rap_002_harness.py::test_caso_e_invalid_writer_mode_blocks                    PASSED
tests/anti_dory/test_rap_002_harness.py::test_caso_f_do_not_touch_expuesto_y_visible               PASSED
tests/anti_dory/test_rap_002_harness.py::test_caso_g_no_events_hard_failure                        PASSED
tests/anti_dory/test_rap_002_harness.py::test_feature_flag_off_devuelve_prompt_intacto             PASSED
tests/anti_dory/test_rap_002_harness.py::test_canonical_state_hash_is_deterministic                PASSED
tests/anti_dory/test_rap_002_harness.py::test_halt_exception_message_includes_violations           PASSED
tests/anti_dory/test_rap_002_harness.py::test_writer_on_start_writes_event_and_snapshot            PASSED
tests/anti_dory/test_rap_002_harness.py::test_heartbeat_writer_independent_of_agent                PASSED
============================== 18 passed in 0.16s ==============================
```

**Resultado: 18/18 PASS. 0 fallos. 0 warnings. Sin regresiones.**

---

## §6 NO-CRUCE binario

`git status --short` filtrado sobre los 5 paths protegidos:

| Path | Diff |
|---|---|
| `kernel/cowork_runtime/*` | **0 matches** |
| `tools/cowork_guardian.py` | **0 matches** |
| `kernel/main.py` | **0 matches** |
| `kernel/engine.py` | **0 matches** |
| `migrations/sql/0001*` → `migrations/sql/0028*` | **0 matches** |

NO-CRUCE respetado al 100%.

---

## §7 Grep secrets (DSC-S enforcement)

```
$ grep -RnE 'eyJ[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9_-]{20,}|postgres://' \
       tools/manus_bridge.py tests/anti_dory/test_manus_bridge_integration.py
(0 matches)
```

---

## §8 Constraints duros respetados

| Constraint T1/T2-A | Estado |
|---|---|
| NO self-merge | **PASS** (PR queda en ready-for-review esperando Cowork) |
| NO tocar Supabase prod | **PASS** (mock httpx + broker mock) |
| NO tocar Railway | **PASS** |
| NO activar `ANTI_DORY_ENABLED` | **PASS** (sigue OFF en todos los entornos) |
| NO secrets en código | **PASS** (grep 0 matches) |
| NO romper backward compat | **PASS** (firma extendida con keyword-only defaults) |
| NO cruzar kernel/cowork_runtime | **PASS** (NO-CRUCE 0 matches) |
| Markers `ANTI_DORY_BEGIN/END` para audit | **PASS** (presentes en `tools/manus_bridge.py` líneas 234 y 271) |
| Fail-open obligatorio en excepciones broker | **PASS** (test `test_broker_exception_fallback_to_original_prompt`) |
| LOC con `wc -l` verbatim (regla cleanup) | **PASS** (§2) |

---

## §9 Decisiones técnicas relevantes

### §9.1 Firma real de `ContextBroker` vs kickoff

El kickoff sugería `ContextBroker()` sin args y `hydrate_prompt(prompt=...)`. La firma real (verificada vía `file read kernel/anti_dory/context_broker.py`) es:

- Constructor: `ContextBroker(rpc_client: SupabaseRPCClient, *, now_fn=..., enabled=...)` — `rpc_client` obligatorio.
- Método: `hydrate_prompt(*, project_id, front_id, user_prompt) -> HydratedPrompt` — keyword-only, parámetro se llama `user_prompt`.
- Resultado: `HydratedPrompt(hydrated_prompt, pack)`, con `pack.attachment_ok`.

**Decisión:** adapté el wire a la firma real sin redefinirla. Esto es un refinamiento del kickoff, no contradicción.

### §9.2 Por qué no construyo el RPC client desde `manus_bridge`

Construir un cliente Supabase real desde `tools/manus_bridge.py` violaría:
- **SRP**: `manus_bridge` es un adapter HTTP de Manus, no un cliente de Supabase.
- **NO-CRUCE**: arrastraría dependencias de `kernel/anti_dory/*` en sentido inverso.
- **Testability**: forzaría mocks de Supabase en tests de Manus bridge.

**Solución:** factory inyectable (`set_anti_dory_broker_factory`). FASE D introducirá una factory default que conecte a Supabase real, sin tocar el wire de FASE C.

### §9.3 Helper `_default_front_id`

L1 del SPEC §A.13 quedó documentada explícitamente: si callsite no pasa `front_id`, se usa `project_id` (o `"unknown-project"` si ambos son `None`). FASE D introduce mapping real `(project_id) → (sprint_id, front_id)` desde `project_runtime_heads`.

---

## §10 Limitaciones declaradas (DSC-G-008 v3 §4)

1. **L_C1 — Sin RPC client real configurado en FASE C.** Cualquier callsite con `attach_context=True` y flag ON cae en fail-open hasta que FASE D configure la factory. Resultado material: durante FASE C, el wire es semánticamente activable pero funcionalmente inactivo. **Esto es deseado** y validado por test `test_factory_none_with_flag_on_fails_open`.

2. **L_C2 — Heurística `_default_front_id`.** En callsites que no pasan `front_id` explícito, FASE C usa `project_id` como fallback. Consecuencia material: hasta FASE D, varios proyectos compartirán front_id si todos pasan el mismo `project_id`. Mitigación: callsites críticos (ej. el de prueba RAP-001 LIVE) deben pasar `front_id` explícito.

3. **L_C3 — Tests usan mocks, no Supabase.** Validan el contrato wire→broker, no la integración end-to-end. Validación end-to-end queda para FASE D con staging Supabase.

4. **L_C4 — Rate limiter compartido con tests.** Tests reseteán `_call_timestamps` vía fixture autouse para evitar contaminación entre tests. Producción no usa este reset.

---

## §11 Consecuencias materiales deducidas

1. **C_C1 — `tools/manus_bridge.create_task` ahora tiene 2 args nuevos opcionales.** Todos los callsites pre-existentes siguen funcionando sin modificación (validado binariamente).

2. **C_C2 — FASE D queda como `READY_FOR_T1_APPROVAL`.** Pre-requisitos documentados: (a) DSCs para staging Supabase, (b) factory default que conecte a Supabase con keys segregadas (`anti_dory_writer_role` / `anti_dory_reader_role`), (c) cron Railway para `HeartbeatWriter.tick()`, (d) encendido controlado de `ANTI_DORY_ENABLED=true`, (e) prueba RAP-001 LIVE re-ejecutada con `attach_context=True`.

3. **C_C3 — Markers `ANTI_DORY_BEGIN/END` en código permiten audit binaria.** Cowork puede grepear el bloque exacto y verificar que no se modifica nada fuera del marker.

4. **C_C4 — El wire es reversible con 1 commit `git revert`.** Markers + 2 args opcionales + factory inyectable = scope quirúrgico.

---

## §12 Próximo paso

Cowork T2-A audita PR (link al hacer push). Si verdict GREEN, T1 decide si autoriza FASE D (activación controlada en staging) o pausa.

**FASE D NO está autorizada todavía.** Sólo dejarla preparada como `READY_FOR_T1_APPROVAL`.

---

**Estado terminal: 🔌 FASE C — AUDIT_PENDIENTE**
