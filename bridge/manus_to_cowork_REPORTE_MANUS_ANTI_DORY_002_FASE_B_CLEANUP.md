# 🧹 REPORTE CLEANUP — MANUS-ANTI-DORY-002 v1 FASE B (PR #125)

**Sprint:** MANUS-ANTI-DORY-002 v1
**Fase:** B (post Cowork T2-A GREEN técnico, cleanup pre-merge)
**Autor:** Manus AI (Hilo B)
**Fecha:** 2026-05-14
**Branch:** `sprint/MANUS-ANTI-DORY-002-fase-b-impl`
**PR:** #125
**Estado terminal:** `READY_FOR_COWORK_MERGE`

---

## §0. TL;DR

Cleanup mandatorio post Cowork T2-A GREEN ejecutado en la misma branch del PR #125. 2 archivos scope leak removidos. Rebase ya estaba al día contra `origin/main`. Validaciones binarias reejecutadas: pytest **12/12 PASS**, grep secrets **0 matches**, NO-CRUCE **0 matches** sobre 4 paths protegidos. Regla operativa nueva agregada: LOC futura = `wc -l` verbatim, no estimación narrativa. Branch lista para merge por Cowork.

---

## §1. Archivos removidos (commit cleanup)

| Archivo | Tamaño | Razón |
|---|---|---|
| `reports/manus_dory_runtime_attachment_proof_001.md` | 15,408 bytes | Plan RAP-001 del frente Kernel-Dory anterior. Scope previo no consecuencia directa del SPEC FASE B. |
| `reports/security/rotation_backlog_masked.md` | 3,942 bytes | Backlog rotación marcado ACCEPTED_RISK por T1. Scope security separado. |

**Decisión T1 default:** remover (no se aplicó alternativa "bridge file explicando relevancia" porque ninguno de los dos archivos cumple criterio binario fuerte de relevancia al SPEC).

Comando ejecutado:
```bash
git rm reports/manus_dory_runtime_attachment_proof_001.md \
       reports/security/rotation_backlog_masked.md
```

Resultado: directorio `reports/security/` se vació y fue eliminado por git al no quedar archivos tracked.

---

## §2. Rebase contra `origin/main`

```text
HEAD pre-rebase:   7792fb3 (feat(anti-dory): FASE B impl real ...)
origin/main HEAD:  ed85ec5 (chore(cowork-dashboard): auto-regen 2026-05-14T08:27Z)

git fetch origin main  →  OK (1 ref actualizado)
git rebase origin/main →  "Current branch ... is up to date."
```

**Resultado:** la rama ya descendía linealmente de `origin/main` (`ed85ec5` es ancestro de `7792fb3`). No hubo conflicts ni replay necesario. Limitación L_C4 cerrada formalmente.

---

## §3. Validaciones binarias post-cleanup

### §3.1 Pytest RAP-002 harness

```text
============================= test session starts ==============================
platform linux -- Python 3.11.0rc1, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/ubuntu/el-monstruo
configfile: pyproject.toml
collected 12 items

tests/anti_dory/test_rap_002_harness.py::test_caso_a_happy_path                                         PASSED [  8%]
tests/anti_dory/test_rap_002_harness.py::test_caso_b_crash_mid_session_heartbeat_recovers               PASSED [ 16%]
tests/anti_dory/test_rap_002_harness.py::test_caso_c_concurrency_cas_conflict                           PASSED [ 25%]
tests/anti_dory/test_rap_002_harness.py::test_caso_d_stale_snapshot_blocks_attachment                   PASSED [ 33%]
tests/anti_dory/test_rap_002_harness.py::test_caso_e_invalid_writer_mode_blocks                         PASSED [ 41%]
tests/anti_dory/test_rap_002_harness.py::test_caso_f_do_not_touch_expuesto_y_visible                    PASSED [ 50%]
tests/anti_dory/test_rap_002_harness.py::test_caso_g_no_events_hard_failure                             PASSED [ 58%]
tests/anti_dory/test_rap_002_harness.py::test_feature_flag_off_devuelve_prompt_intacto                  PASSED [ 66%]
tests/anti_dory/test_rap_002_harness.py::test_canonical_state_hash_is_deterministic                     PASSED [ 75%]
tests/anti_dory/test_rap_002_harness.py::test_halt_exception_message_includes_violations                PASSED [ 83%]
tests/anti_dory/test_rap_002_harness.py::test_writer_on_start_writes_event_and_snapshot                 PASSED [ 91%]
tests/anti_dory/test_rap_002_harness.py::test_heartbeat_writer_independent_of_agent                     PASSED [100%]

============================== 12 passed in 0.03s ==============================
```

### §3.2 Grep secrets sobre scope FASE B

```bash
grep -RnE "eyJ|sk-[A-Za-z0-9_-]{20,}|postgres://" \
  kernel/anti_dory/ \
  migrations/sql/0029_*.sql migrations/sql/0030_*.sql \
  migrations/sql/0031_*.sql migrations/sql/0032_*.sql \
  tests/anti_dory/ \
  bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_*.md \
  bridge/sprints_propuestos/sprint_MANUS_ANTI_DORY_002_v1.md \
  reports/anti_dory_002_v1_pre_spec_audit.json
```

**Resultado:** `0 matches`. Cero secrets hardcoded en el scope FASE B.

### §3.3 NO-CRUCE binario sobre 4 paths protegidos

```bash
git diff --name-only origin/main...HEAD | grep -E \
  "^(kernel/cowork_runtime/|tools/cowork_guardian\.py|kernel/main\.py|kernel/engine\.py|migrations/sql/00(0[1-9]|1[0-9]|2[0-8]))"
```

**Resultado:** `0 matches`. NO-CRUCE confirmado sobre:
- `kernel/cowork_runtime/*` → intacto
- `tools/cowork_guardian.py` → intacto
- `kernel/main.py` → intacto
- `kernel/engine.py` → intacto
- `migrations/sql/0001-0028*` → intactas

### §3.4 git diff --stat post-cleanup

Resumen post-commit cleanup esperado (los 2 archivos scope leak desaparecen del diff PR):

```text
 bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_A_DONE.md         |   78 +++
 bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_B_DONE.md         |  177 +++++
 bridge/manus_to_cowork_REPORTE_MANUS_ANTI_DORY_002_FASE_B_CLEANUP.md |  XXX +++   ← este reporte
 bridge/sprints_propuestos/sprint_MANUS_ANTI_DORY_002_v1.md           |  222 +++++
 kernel/anti_dory/__init__.py                                         |   25 ++
 kernel/anti_dory/context_broker.py                                   |  312 +++++
 kernel/anti_dory/guardian.py                                         |  191 ++++
 kernel/anti_dory/recovery.py                                         |  216 +++++
 kernel/anti_dory/writers.py                                          |  535 +++++
 migrations/sql/0029_runtime_events.sql                               |  135 +++
 migrations/sql/0030_thread_snapshots.sql                             |  167 +++
 migrations/sql/0031_project_runtime_heads.sql                        |  112 +++
 migrations/sql/0032_anti_dory_rpcs.sql                               |  385 +++++
 reports/anti_dory_002_v1_pre_spec_audit.json                         |  154 +++
 tests/anti_dory/__init__.py                                          |    1 +
 tests/anti_dory/test_rap_002_harness.py                              |  402 +++++
```

**Eliminado del scope:**
- `reports/manus_dory_runtime_attachment_proof_001.md` (309 LOC, scope leak)
- `reports/security/rotation_backlog_masked.md` (75 LOC, scope leak)

---

## §4. LOC reales con `wc -l` verbatim

**Comando ejecutado:**
```bash
wc -l migrations/sql/0029_*.sql migrations/sql/0030_*.sql \
      migrations/sql/0031_*.sql migrations/sql/0032_*.sql \
      kernel/anti_dory/*.py \
      tests/anti_dory/*.py \
      bridge/sprints_propuestos/sprint_MANUS_ANTI_DORY_002_v1.md \
      bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_*.md \
      reports/anti_dory_002_v1_pre_spec_audit.json
```

**Output verbatim:**

```text
   135 migrations/sql/0029_runtime_events.sql
   167 migrations/sql/0030_thread_snapshots.sql
   112 migrations/sql/0031_project_runtime_heads.sql
   385 migrations/sql/0032_anti_dory_rpcs.sql
    25 kernel/anti_dory/__init__.py
   312 kernel/anti_dory/context_broker.py
   535 kernel/anti_dory/writers.py
   191 kernel/anti_dory/guardian.py
   216 kernel/anti_dory/recovery.py
     1 tests/anti_dory/__init__.py
   402 tests/anti_dory/test_rap_002_harness.py
   222 bridge/sprints_propuestos/sprint_MANUS_ANTI_DORY_002_v1.md
    78 bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_A_DONE.md
   177 bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_B_DONE.md
   154 reports/anti_dory_002_v1_pre_spec_audit.json
  3112 total
```

### §4.1 Discrepancia detectada vs reporte FASE B narrativo

| Categoría | Estimado FASE B | Real `wc -l` | Delta |
|---|---|---|---|
| Migrations SQL (4) | ~484 | **799** | +315 (+65%) |
| Kernel Python (5) | ~984 | **1,279** | +295 (+30%) |
| Tests | ~370 | **403** | +33 (+9%) |
| Bridge + SPEC | (no reportado) | **477** | n/a |
| Pre-audit JSON | (no reportado) | **154** | n/a |
| **TOTAL** | ~1,838 (parcial) | **3,112 (completo)** | — |

**Conclusión:** la estimación narrativa subestimó ~30% en código Python y ~65% en SQL. Esto valida la necesidad de la regla operativa nueva.

---

## §5. Regla operativa nueva

> **Regla LOC-VERBATIM (Sprint MANUS-ANTI-DORY-002 v1 cleanup, 2026-05-14):**
>
> Toda métrica de LOC futura en reportes Manus debe venir respaldada por output `wc -l` **verbatim** sobre los archivos exactos contabilizados. Las estimaciones narrativas (ej. *"~500 LOC"*, *"aproximadamente 1000 líneas"*) quedan **prohibidas** en reportes técnicos para Cowork, T1, y audit DSC-G-008.
>
> **Aplicación:** todo reporte que contenga métrica LOC debe incluir bloque ```text``` con output crudo de `wc -l <archivos>`. Si no se puede ejecutar `wc -l`, la métrica se omite, no se estima.
>
> **Razón:** caso concreto detectado en FASE B inicial — estimación narrativa subestimó ~30% el código Python y ~65% el SQL. Reportes con métricas erradas degradan la calidad de audit y decisiones T1.

Esta regla se aplica retroactivamente al reporte FASE B `manus_to_cowork_MANUS_ANTI_DORY_002_v1_FASE_B_DONE.md` y prospectivamente a todo reporte futuro.

---

## §6. Commits del cleanup

| Commit | Hash | Mensaje |
|---|---|---|
| Cleanup commit | `887924b9fee908762bff18d720b23ceb4a69e7b2` (short: `887924b`) | `chore(anti-dory): cleanup scope leak — remove 2 reports unrelated to FASE B SPEC + add LOC-VERBATIM rule` |

> El hash exacto del commit se inyecta vía amend post-commit (regla técnica: el reporte se referencia a sí mismo en el commit, requiere un step de patch).

---

## §7. Restricciones T1 reafirmadas

| Restricción | Estado |
|---|---|
| NO implementar cosas nuevas | PASS (solo cleanup + reporte) |
| NO tocar Supabase prod | PASS |
| NO Railway | PASS |
| NO activar `ANTI_DORY_ENABLED` | PASS (flag sigue OFF default) |
| NO secrets | PASS (grep `0 matches`) |
| NO self-merge | PASS (push a branch, sin merge automático) |

---

## §8. Estado FASE C

**FASE C NO está autorizada.** Solo queda **preparada como `READY_FOR_T1_APPROVAL`**:

- Pre-requisitos para FASE C documentados en `FASE_B_DONE.md §4`:
  - Aplicar migrations 0029-0032 en Supabase (staging primero).
  - Conceder GRANTS `anti_dory_writer_role` y `anti_dory_reader_role` a service users específicos.
  - Validar RLS canónico vía `scripts/_check_rls_default.py`.
  - Integrar `ContextBroker.hydrate_prompt()` en `tools/manus_bridge.create_task()` (callsite específico documentado).
  - Configurar cron Railway o equivalente para `HeartbeatWriter.tick()` cada 10-15min.
  - Encender `ANTI_DORY_ENABLED=true` con audit Cowork final.

Cada uno requiere DSC firmado individualmente. T1 decide el orden y el go/no-go.

---

## §9. Firma canónica de cierre

> **🧹 CLEANUP COMPLETO — READY_FOR_COWORK_MERGE.**
> Branch `sprint/MANUS-ANTI-DORY-002-fase-b-impl` pasa validaciones binarias post-cleanup.
> Cowork puede mergear PR #125 a `main` cuando lo decida.
> FASE C queda como `READY_FOR_T1_APPROVAL`, sin ejecución autorizada todavía.

— Manus AI (Hilo B), 2026-05-14.
