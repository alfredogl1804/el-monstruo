# 🛠️ FASE B — IMPLEMENTACIÓN — AUDIT_PENDIENTE

**Sprint:** MANUS-ANTI-DORY-002 v1
**Fase:** B (implementación real)
**Autor:** Manus AI (Hilo B)
**Fecha:** 2026-05-13
**Estado terminal:** `🛠️ FASE B — AUDIT_PENDIENTE. Cowork audita DSC-G-008 v3 §4 + autoriza merge.`

---

## §0. TL;DR

FASE B completa según SPEC v1. 8 archivos nuevos (4 migrations SQL + 4 módulos Python kernel/anti_dory/* + 1 test harness). RAP-002 harness **12/12 passing** en 0.06s con MockRPCClient (cero dependencias externas). NO se ejecutaron migrations en Supabase real. NO se tocó Railway. NO se tocó PR #118 ni Mac. Feature flag `ANTI_DORY_ENABLED` default `False`. Push hecho a rama dedicada, **sin self-merge**.

---

## §1. Entregables (8 archivos nuevos, 0 modificaciones de código existente)

### §1.1 Migrations SQL (4 archivos)

| Migration | Propósito | Tablas/RPCs | LOC |
|---|---|---|---|
| `migrations/sql/0029_runtime_events.sql` | Append-only event log | `runtime_events` + 3 índices + DO block DSC-S-006 v1.1 | 95 |
| `migrations/sql/0030_thread_snapshots.sql` | Snapshots versionados con hash + parent + do_not_touch + confidence | `thread_snapshots` + 3 índices + DO block | 109 |
| `migrations/sql/0031_project_runtime_heads.sql` | Punteros canónicos por (project_id, front_id) con CAS via `lock_version` | `project_runtime_heads` + DO block | 81 |
| `migrations/sql/0032_anti_dory_rpcs.sql` | 5 RPCs SECURITY DEFINER + 2 roles segregados | `anti_dory_writer_role`, `anti_dory_reader_role`, 5 RPCs | 199 |

**Total SQL:** ~484 LOC. Cada migration **idempotente** (`CREATE TABLE IF NOT EXISTS`, DO block para policies). RLS habilitado en las 3 tablas + verificación canónica DSC-S-006 v1.1 (`RAISE EXCEPTION` si no hay policies).

**Numeración Anti-F24:** 0029/0030/0031/0032 (verificada libre vía pre-audit binario). Gap 0027 detectado pero NO bloqueante (issue separado).

### §1.2 Módulos Python kernel/anti_dory/* (4 archivos)

| Módulo | Responsabilidad | LOC | Tests |
|---|---|---|---|
| `kernel/anti_dory/__init__.py` | Feature flag `ANTI_DORY_ENABLED` (default False) | 17 | implícito |
| `kernel/anti_dory/context_broker.py` | `ContextBroker.hydrate_prompt()` — externo al agente | 261 | A, D, F, flag-off |
| `kernel/anti_dory/writers.py` | `AgentExplicitWriter` (4 modos), `HeartbeatWriter` (independiente), `ExternalPollingWriter` | 354 | C, on_start, heartbeat |
| `kernel/anti_dory/guardian.py` | `verify_attachment_contract` + `AttachmentVerdict` + `HaltAttachmentMismatch` | 174 | D, E, halt-msg |
| `kernel/anti_dory/recovery.py` | `RecoveryMode.attempt_recovery()` — pregunta binaria, NO reexplicación humana | 178 | B, G |

**Total Python kernel:** ~984 LOC. **Cero imports** de `kernel/cowork_runtime/*`, `tools/cowork_guardian.py` (NO-CRUCE respetado). **Cero secretos en código** (claves vía env var en runtime).

### §1.3 Tests RAP-002 (1 archivo, 12 tests)

| Archivo | Tests | Resultado |
|---|---|---|
| `tests/anti_dory/test_rap_002_harness.py` | 12 (7 canónicos A-G + 5 extras) | **12/12 PASS** en 0.06s |

```text
test_caso_a_happy_path                                         PASSED
test_caso_b_crash_mid_session_heartbeat_recovers               PASSED
test_caso_c_concurrency_cas_conflict                           PASSED
test_caso_d_stale_snapshot_blocks_attachment                   PASSED
test_caso_e_invalid_writer_mode_blocks                         PASSED
test_caso_f_do_not_touch_expuesto_y_visible                    PASSED
test_caso_g_no_events_hard_failure                             PASSED
test_feature_flag_off_devuelve_prompt_intacto                  PASSED
test_canonical_state_hash_is_deterministic                     PASSED
test_halt_exception_message_includes_violations                PASSED
test_writer_on_start_writes_event_and_snapshot                 PASSED
test_heartbeat_writer_independent_of_agent                     PASSED
============================== 12 passed in 0.06s ==============================
```

---

## §2. Decisiones técnicas relevantes (para audit Cowork)

### §2.1 Patch §A.7 obligatorio

El SPEC v1 §A.7 requería desglosar los 4 modos `agent_explicit_writer` con código real y declarar el `heartbeat_writer` como independiente. Implementado verbatim en `kernel/anti_dory/writers.py`:

- `AgentExplicitWriter.write_on_start()` → mode `explicit_start`
- `AgentExplicitWriter.write_on_transition()` → mode `explicit_transition`, requiere `parent_snapshot_id`
- `AgentExplicitWriter.write_on_artifact()` → mode `explicit_artifact`, **event-only** (no crea snapshot, evita ruido)
- `AgentExplicitWriter.write_on_final()` → mode `explicit_final`, dispara `rpc_accept_snapshot` con CAS
- `HeartbeatWriter` → clase separada, **NO depende de AgentExplicitWriter**. Diseñada para invocación vía cron Railway (CLI v2 fuera de scope). Reconstruye estado vía `rpc_recovery_scan` aunque el agente esté caído.

### §2.2 Refinamiento `cowork_guardian` (no contradice SPEC, lo aclara)

El SPEC §A.6 sugería *"extender GuardianVerdict con verify_attachment_contract"*. Tras lectura binaria de `tools/cowork_guardian.py`, esa extensión **violaría SRP**: `cowork_guardian` valida outputs Cowork→Alfredo (`push_to_pause`, avance real), no attachment de runtime.

**Decisión:** módulo separado `kernel/anti_dory/guardian.py` con `AttachmentVerdict` análogo pero distinto. Esto preserva la intención del SPEC (attachment validation existe) y respeta NO-CRUCE con `cowork_guardian`. Documentado al inicio del archivo.

### §2.3 Refinamiento firma `tools/manus_bridge.create_task`

Pre-audit reveló que `create_task` usa `*` (keyword-only) para `account` y `project_id`. El SPEC asumía firma posicional. **No requiere cambios en `manus_bridge`** — el callsite del Context Broker que aún no se ha integrado (FASE C) usará `create_task(prompt=hydrated.hydrated_prompt, account="google", project_id=pack.project_id)`. Documentado para FASE C.

### §2.4 Feature flag default OFF

`ANTI_DORY_ENABLED=false` por default. Hasta que las migrations 0029-0032 se apliquen en Supabase y los roles `anti_dory_writer_role`/`anti_dory_reader_role` se concedan a los service users, **el broker degrada graciosamente**: devuelve prompt sin modificar + `pack.attachment_ok=False` + `fallback_reason="feature_flag_off"`. **Cero impacto en producción actual**.

---

## §3. Cumplimiento de restricciones T1

| Restricción | Estado | Evidencia |
|---|---|---|
| NO self-merge | PASS | Solo rama nueva pusheada, sin PR auto-merge |
| NO tocar Mac local | PASS | Cero operaciones sobre `/mnt/desktop/*` |
| NO secrets en código | PASS | Cero claves hardcoded. RPC client se inyecta |
| NO rotación | PASS | Cero operaciones sobre env vars existentes |
| NO tocar PR #118 | PASS | PR #118 OPEN intacto |
| NO romper kernel | PASS | Cero modificaciones a kernel/main.py, embrion_loop, etc. |
| NO modificar cowork_runtime | PASS | NO-CRUCE estricto. Ni un import |
| NO ejecutar migrations en Supabase real | PASS | Solo escritas a disco. Sin `psql`, sin `supabase db push` |
| NO tocar Railway | PASS | Cero `railway` CLI ejecutado |
| Tests sin red externa | PASS | MockRPCClient en memoria. `pytest` corre offline |

---

## §4. Limitaciones esperadas (DSC-G-008 v3 §4)

### §4.1 Migrations NO aplicadas en Supabase

Las migrations 0029/0030/0031/0032 existen como archivos versionados pero **NO se han ejecutado** contra el cluster Supabase de producción. FASE C deberá:

1. Validar SQL con `supabase db lint` o `pg_dump --schema-only` en preview.
2. Aplicar en staging primero.
3. Conceder GRANTS de `anti_dory_writer_role` y `anti_dory_reader_role` a service users específicos (NO a `service_role` directamente — la migration explícitamente revoca eso).
4. Verificar RLS canónico vía `scripts/_check_rls_default.py`.

### §4.2 Context Broker NO integrado en task.create

`tools/manus_bridge.create_task()` aún NO invoca `ContextBroker.hydrate_prompt()`. Esta integración es FASE C consciente: el SPEC requiere que sea opt-in via feature flag, y validada con audit Cowork antes de pasar a producción. Mientras el flag esté OFF, `manus_bridge` opera idéntico a hoy.

### §4.3 HeartbeatWriter sin scheduler

`HeartbeatWriter.tick()` existe pero **NO hay cron Railway todavía**. Se requiere un job (Railway cron, o GitHub Actions scheduled, o equivalente) que invoque `python -m kernel.anti_dory.cli heartbeat` cada 10-15min. Decidido fuera de scope v1.

### §4.4 ExternalPollingWriter sin emisores

La clase existe pero **ningún sistema externo emite eventos todavía**. CI webhooks de GitHub, Railway hooks de deploy, etc., son trabajo de FASE D.

---

## §5. Consecuencias materiales (DSC-G-008 v3 §4)

### §5.1 C1: Anti-Dory inactivo hasta FASE C

Con flag OFF y migrations sin aplicar, **el Síndrome Dory NO está resuelto en producción**. El RAP-001 LIVE seguirá fallando. La resolución ocurre cuando: (a) Cowork audita y aprueba FASE B, (b) T1 autoriza FASE C, (c) migrations se aplican, (d) flag se enciende, (e) RAP-001 LIVE pasa GREEN.

### §5.2 C2: Deuda técnica controlada

Las limitaciones §4.1-§4.4 son **deuda explícita, no oculta**. Cada una tiene scope definido y dueño futuro (FASE C, FASE D). NO bloquean audit DSC-G-008.

### §5.3 C3: Reversibilidad total

Si FASE B falla audit, revertir es trivial: `git revert` sobre el merge commit. NO hay cambios destructivos en Supabase ni Railway ni file system. NO hay migrations aplicadas. NO hay servicios desplegados. El sistema actual sigue idéntico.

---

## §6. Validación binaria (evidencia)

- **Tests RAP-002:** `12 passed in 0.06s` (output verbatim arriba).
- **Migrations en disco:** `ls migrations/sql/ | grep ^0029\|^0030\|^0031\|^0032` → 4 archivos.
- **Módulos en disco:** `ls kernel/anti_dory/*.py` → 5 archivos (incluyendo `__init__.py`).
- **DO block DSC-S-006 v1.1:** `grep "DSC-S-006 v1.1" migrations/sql/0029_*.sql migrations/sql/0030_*.sql migrations/sql/0031_*.sql` → 3 matches.
- **Pre-audit Anti-F24:** `reports/anti_dory_002_v1_pre_spec_audit.json` (130 LOC).

---

## §7. Próximos pasos (NO ejecutar sin OK T1)

1. **Cowork T2-A audita FASE B** contra SPEC v1 + DSC-G-008 v3 §4.
2. Si verdict = GREEN → firmar `🏛️ FASE B — APROBADO` y abrir PR para merge a main.
3. T1 decide si autorizar FASE C (aplicar migrations en Supabase + integrar broker en task.create + encender flag) o pausar.

---

## §8. Firma canónica de cierre

> **🛠️ FASE B — AUDIT_PENDIENTE.**
> Cowork audita DSC-G-008 v3 §4 + autoriza FASE C implementación.

— Manus AI (Hilo B), 2026-05-13.
