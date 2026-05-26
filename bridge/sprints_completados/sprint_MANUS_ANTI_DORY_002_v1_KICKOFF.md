# 🏛️ KICKOFF SPRINT MANUS-ANTI-DORY-002 V1 — SPEC + IMPLEMENTACIÓN REAL INMEDIATA

**Prompt auto-contenido para pegar a hilo Manus disponible. T1 Alfredo autorizó "implementacion real inmediata" 2026-05-13 ~22:55 UTC.**

## §0 Identidad + autoridad + ETA

**Tu rol:** Manus Hilo Ejecutor (cualquiera de los 3 disponibles post-cierre sus sprints actuales)
**Autoridad:** T1 firmó audit GPT-5.5 Pro como input doctrinal P0 + autorizó implementación real inmediata
**ETA total estimado:** 2-4 días continuos (SPEC + implementación + RAP-002 harness)
**Self-merge:** NO. Cowork T2-A audita + mergea.

**Frase canónica magna:** *"Anti-Dory no es memoria. Es attachment operativo verificable antes del primer pensamiento del agente."* — GPT-5.5 Pro

## §1 Contexto magno

### Antecedente
Audit completa GPT-5.5 Pro: `bridge/sabios/SABIO_GPT_5_5_PRO_audit_anti_dory_002_2026_05_13.md` (12,775 bytes). Leéla COMPLETA antes de tocar código. Input doctrinal P0 firmado T1.

### Convergencia Sabios independientes (señal magna)
GPT-5.5 Pro (2026-05-13) coincide con Claude Opus 4.7 Thinking Entregable A (2026-05-12 — `bridge/sabio_OPUS_4_7_THINKING_response_ronda_1_2026_05_12.md`) en diagnóstico arquitectónico: solución debe vivir FUERA del agente conversacional. **2 Sabios independientes coincidiendo = decisión arquitectónica fuerte.**

### Síndrome Dory 3 dimensiones (Opus)
- **D1** Memoria efímera cross-sesión — atacada centralmente por este sprint
- **D2** No-transfer cross-dominio intra-sesión — atacada por COWORK-MEMENTO-001 (en curso)
- **D3** Asimetría costo verificar vs afirmar — parcial AUTO-DISCIPLINE PR #118 + a fondo VERIFICADOR-001 futuro

## §2 Scope CROSS-AGENTE (no solo Manus)

GPT-5.5 escribió pensando en Manus. Pero arquitectura aplica idéntico a Cowork y Embrión.

| Agente | Componente attachment | Estado actual |
|---|---|---|
| Manus (T3) | task.create con prompt hidratado vía Context Broker | A implementar |
| Cowork (T2-A/T2-C) | session_memory + Pre-flight Memento + state digest auto-inyectado | Parcial existente, extender |
| Embrión (T3 autónomo) | par bicéfalo DSC-MO-006 v1.1 + heartbeat | Existente, integrar runtime_events |

**Todos comparten:** runtime_events (mismo schema), thread_snapshots (mismo schema, actor_type distingue), project_runtime_heads (un puntero por front_id), Context Broker externo (orquestador único pre-task.create).

## §3 Entregables 3 fases

### FASE A — SPEC V1 doctrinal firmable (Día 1, ~4-6h)

`bridge/sprints_propuestos/sprint_MANUS_ANTI_DORY_002_v1.md` (~800-1200 LOC markdown) con:

- **§A.1** Marco doctrinal (frase canónica + diagnóstico Dory + por qué solución debe vivir afuera)
- **§A.2** Arquitectura objetivo (diagrama T1 → Context Broker → Supabase → task.create hidratado → Agent → guardian verificador → snapshot incremental writer)
- **§A.3** Schema SQL completo (3 tablas con RLS + DO block + índices + CHECK constraints)
- **§A.4** RPCs Supabase: `rpc_write_runtime_event`, `rpc_write_thread_snapshot` (con state_hash+prev_hash), `rpc_get_context_head`, `rpc_accept_snapshot` (compare-and-swap), `rpc_recovery_scan`. Permisos restringidos: `anti_dory_writer_role` + `anti_dory_reader_role`. NO acceso directo a tablas desde service_key.
- **§A.5** Context Broker pseudocode (resolve intent → read project_runtime_heads → validate freshness → verify artifacts → build MONSTRUO_RUNTIME_ATTACHMENT pack)
- **§A.6** Guardian verifier (parse ATTACHMENT_OK contract → verify project/sprint/fase/last_t1_decision match snapshot → HALT_ATTACHMENT_MISMATCH si mismatch)
- **§A.7** Snapshot writer incremental (3 mecanismos: agent_explicit + external_polling + heartbeat 10-15min)
- **§A.8** Recovery mode (scan runtime_events + GitHub + artifacts + transcripts → propose 1 estado + confidence → T1 confirmación binaria, NO "¿dónde nos quedamos?")
- **§A.9** Staleness policy (fresh ≤60min normal / 60min-24h verify / >24h recovery / mismatch recovery / blocked_by_T1 halt)
- **§A.10** Contrato primer turno: ATTACHMENT_OK con snapshot_id, project_id, front_id, sprint_id, phase, last_t1_decision, next_expected_action, do_not_touch, evidence_refs
- **§A.11** RAP-002 test harness (7 casos: RAP-002-A virgen retoma sin reexplicación, B crash mid-thread recupera heartbeat, C concurrencia no mezcla frentes, D snapshot stale entra recovery, E artifact faltante HALT, F sprint bloqueado T1 no revive, G pregunta ambigua ofrece cabeza canónica)
- **§A.12** Definition of Done binaria
- **§A.13** Limitaciones + Consecuencias materiales DSC-G-008 v3 §4

### FASE B — Implementación real (Días 2-3, ~12-18h)

**Tarea B.1** — 3 migrations Supabase (`0029_runtime_events.sql`, `0030_thread_snapshots.sql`, `0031_project_runtime_heads.sql`). **Verificar números reales con `ls migrations/sql/ | sort | tail -1` (anti-F24).** Plantilla migration 0027 verbatim (RLS + DO block + RAISE EXCEPTION DSC-S-006).

**Tarea B.2** — 5 RPCs Supabase (functions PL/pgSQL con SECURITY DEFINER + permisos restrictivos)

**Tarea B.3** — Context Broker (`kernel/anti_dory/context_broker.py` ~400 LOC). Decisión arquitectónica: **integrado al kernel actual** (NO nuevo Railway service — Cowork T2-A recomienda B por velocidad + menos infra; A solo si performance issue post-implementación). Endpoint `/v1/anti_dory/broker/create_task` que recibe intención + crea hilo Manus hidratado vía Manus task API.

**Tarea B.4** — Snapshot writers (`kernel/anti_dory/writers.py` ~300 LOC) — 3 mecanismos

**Tarea B.5** — Guardian verifier (`kernel/anti_dory/guardian_verify.py` ~200 LOC) — integrar con `tools/cowork_guardian.py` existente, NO duplicar

**Tarea B.6** — Recovery mode (`kernel/anti_dory/recovery.py` ~250 LOC)

**Tarea B.7** — Integración cross-agente:
- Cowork `session_memory.py` consume Context Broker en Pre-flight Memento
- Manus task.create wrapper invoca Context Broker pre-creation
- Embrión `embrion_loop.py` escribe heartbeats a runtime_events

### FASE C — RAP-002 test harness + cierre (Día 4, ~4-6h)

**Tarea C.1** — 7 tests RAP-002 ejecutables (`tests/test_anti_dory_rap_002.py`) con mocks Supabase + GitHub + Manus task API
**Tarea C.2** — Postmortem + reporte cierre (`bridge/postmortems/MANUS_ANTI_DORY_002_v1_postmortem.md` + `bridge/manus_to_cowork_MANUS_ANTI_DORY_002_v1_DONE_*.md`)
**Tarea C.3** — Push branch `feat/anti-dory-002-v1` + PR draft

## §4 Constraints duros

### DSC enforced
DSC-V-001 (validation_log) · DSC-S-006 v1.1 (RLS + DO block) · DSC-S-012 (migration numbers verificados binario) · DSC-S-016 (anti-fabricación causalidad sin grep) · DSC-G-008 v3 §4 (Limitaciones + Consecuencias materiales) · DSC-G-017 (SPEC firmado = contrato) · DSC-MO-006 v1.1 (PBA) · F24 anti (verificar binariamente paths/tablas) · F26 anti (CÓDIGO ejecutable, no doctrina nueva) · F27 anti (frase canónica DECLARADO solo post-audit binario Cowork)

### Anti-F24 checklist obligatorio pre-SPEC

```bash
# 1. Migrations existentes
ls migrations/sql/ | sort | tail -5

# 2. Kernel structure
ls kernel/ && ls kernel/cowork_runtime/

# 3. Tablas Supabase existentes (vía MCP)
# SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;

# 4. PRs abiertos
gh pr list --state=open

# 5. AGENTS.md + CLAUDE.md
cat AGENTS.md | head -100 && cat CLAUDE.md | head -100

# 6. Audit GPT-5.5 verbatim (12,775 bytes)
cat bridge/sabios/SABIO_GPT_5_5_PRO_audit_anti_dory_002_2026_05_13.md
```

Reportá en `reports/anti_dory_002_v1_pre_spec_audit.json`.

### NO-CRUCE

- ❌ `kernel/cowork_runtime/{session_memory,f21_patterns,antipatterns,rule_reinjection,companion_agent,drift_detector,alfredo_veto_channel,pre_response_hook}.py` SIN coordinarlo con Cowork T2-A vía bridge file
- ❌ Branches en curso: `feat/cowork-auto-discipline-real-001` (PR #118), `feat/cowork-memento-001` (MEMENTO arranque)
- ❌ Migrations 0001-0027 (ni 0028 si MEMENTO ya la tomó)
- ❌ DSCs canonizados existentes
- ❌ Rotación secrets (T1 absoluto)

## §5 Coordinación sprints en curso

| Sprint | Owner | Migration que usa |
|---|---|---|
| COWORK-MEMENTO-001 | Ejecutor 1 | 0028 cowork_claims_calibration |
| REMONTOIR-001 v3 | Ejecutor 2 | sin migration nueva |
| DSC-G-008-V4-INDEX-DRIFT | Catastro | sin migration nueva |
| **MANUS-ANTI-DORY-002 v1** (este) | TBD | **0029, 0030, 0031** |

**Verificá `ls migrations/sql/ | sort | tail -1` binario al T1 del sprint. Si MEMENTO no creó 0028 todavía, usá los siguientes libres reales.**

## §6 Frase canónica condicional (F27)

**Pre-audit Cowork:** `📋 MANUS-ANTI-DORY-002 V1 — AUDIT_PENDIENTE`
**Post-audit verde 6/6 + 7 RAP-002 PASS:** `🏛️ MANUS-ANTI-DORY-002 V1 — DECLARADO + DORY MUERTO ESTRUCTURALMENTE`

## §7 Output esperado cierre

Bridge file `bridge/manus_to_cowork_MANUS_ANTI_DORY_002_V1_DONE_2026_05_NN.md` con: status FASE A+B+C, archivos entregados + LOC reales, ETA real vs estimado, 7/7 RAP-002 PASS verbatim, Limitaciones L1-LN, Consecuencias materiales §4, frase canónica AUDIT_PENDIENTE, bash+SQL verificación reproducible.

## §8 Blocker protocol

Si encontrás algo que el spec/audit no anticipa, pará y reportá `bridge/manus_to_cowork_ANTI_DORY_002_V1_BLOCKER_<descripcion>.md`. Cowork responde <30min. NO inventes solución unilateral (V25 antipattern).

## §9 Firmas

**Kickoff:** Cowork T2-A Arquitecto Orquestador, 2026-05-13 ~23:15 UTC
**Bajo autoridad T1 directa Alfredo:** "accion 1 y 2 pero con implementacion real inmediata"
**Input doctrinal P0:** audit GPT-5.5 Pro firmada (commit e64939e4)
**Convergencia magna:** Opus 4.7 Thinking Entregable A (2026-05-12) coincide independientemente
**Frase canónica magna:** *"Anti-Dory no es memoria. Es attachment operativo verificable antes del primer pensamiento del agente."* — GPT-5.5 Pro

**Procedé binario. FASE A primero (SPEC firmable). Cowork audita SPEC antes de autorizar FASE B implementación.**
