# 🏛️ SPEC MANUS-ANTI-DORY-002 V1 — ATTACHMENT OPERATIVO VERIFICABLE

**Sprint:** MANUS-ANTI-DORY-002 v1
**Estado:** `📋 SPEC V1 — AUDIT_PENDIENTE`
**Owner FASE A:** Manus Hilo Ejecutor
**Audit FASE A:** Cowork T2-A
**Autoridad T1:** Alfredo Góngora (autorizó implementación real inmediata)
**Migrations Asignadas:** `0029_runtime_events.sql`, `0030_thread_snapshots.sql`, `0031_project_runtime_heads.sql` (Verificado: gap 0027 ignorado, 0028 existe).

---

## §A.1 Marco Doctrinal

**Frase canónica:** *"Anti-Dory no es memoria. Es attachment operativo verificable antes del primer pensamiento del agente."* — GPT-5.5 Pro

**Diagnóstico Dory:** El Síndrome Dory (D1: memoria efímera cross-sesión) ocurre porque el agente nace virgen y depende de sí mismo para recuperar contexto. Esto es un error circular: un agente amnésico no puede auto-instruirse para dejar de ser amnésico sin intervención humana.

**Decisión Arquitectónica:** La solución debe vivir **fuera** del agente. El hilo nuevo no nace virgen; nace hidratado con un *attachment pack* inyectado por un orquestador externo (Context Broker) antes del primer turno.

## §A.2 Arquitectura Objetivo

```mermaid
graph TD
    T1[Alfredo T1] -->|Prompt natural| CB[Context Broker]
    CB -->|1. rpc_get_context_head| SUP[Supabase]
    SUP -->|2. project_runtime_heads| CB
    CB -->|3. verify freshness| CB
    CB -->|4. task.create(prompt + ATTACHMENT_OK)| MANUS[Manus API]
    MANUS -->|5. Hilo hidratado| AGENT[Agente Manus]
    AGENT -->|6. Guardian pre-hook| VER[Guardian Verifier]
    AGENT -->|7. agent_explicit_writer| SUP
    CRON[Railway Cron] -->|8. heartbeat_writer| SUP
```

## §A.3 Schema SQL Completo (3 tablas)

```sql
-- migrations/sql/0029_runtime_events.sql
CREATE TABLE IF NOT EXISTS public.runtime_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    project_id TEXT NOT NULL,
    front_id TEXT NOT NULL,
    actor_type TEXT NOT NULL CHECK (actor_type IN ('manus', 'cowork', 'embrion', 'system')),
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);
ALTER TABLE public.runtime_events ENABLE ROW LEVEL SECURITY;
-- (Policies segregadas en §A.4)

-- migrations/sql/0030_thread_snapshots.sql
CREATE TABLE IF NOT EXISTS public.thread_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    project_id TEXT NOT NULL,
    front_id TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    parent_snapshot_id UUID REFERENCES public.thread_snapshots(snapshot_id),
    state_hash TEXT NOT NULL,
    sprint_id TEXT,
    phase TEXT,
    last_t1_decision TEXT,
    next_expected_action TEXT,
    do_not_touch JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
    confidence_score NUMERIC(3,2) NOT NULL CHECK (confidence_score BETWEEN 0.0 AND 1.0)
);
ALTER TABLE public.thread_snapshots ENABLE ROW LEVEL SECURITY;

-- migrations/sql/0031_project_runtime_heads.sql
CREATE TABLE IF NOT EXISTS public.project_runtime_heads (
    project_id TEXT NOT NULL,
    front_id TEXT NOT NULL,
    head_snapshot_id UUID NOT NULL REFERENCES public.thread_snapshots(snapshot_id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    lock_version INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (project_id, front_id)
);
ALTER TABLE public.project_runtime_heads ENABLE ROW LEVEL SECURITY;
```
*(Nota: Las migrations reales incluirán el DO block de validación DSC-S-006 v1.1).*

## §A.4 RPCs Supabase y Permisos

Roles segregados: `anti_dory_writer_role`, `anti_dory_reader_role`. `service_role` NO accede directo a tablas, asume estos roles vía `SECURITY DEFINER`.

1. `rpc_write_runtime_event(p_project_id, p_front_id, p_actor, p_type, p_payload)`
2. `rpc_write_thread_snapshot(...)` → retorna `snapshot_id`.
3. `rpc_get_context_head(p_project_id, p_front_id)` → retorna el snapshot activo.
4. `rpc_accept_snapshot(p_project_id, p_front_id, p_snapshot_id, p_expected_lock_version)` → Compare-and-swap para concurrencia.
5. `rpc_recovery_scan(p_project_id, p_front_id)` → Scan forense si head es stale.

## §A.5 Context Broker (Pseudocode)

Ubicación: `kernel/anti_dory/context_broker.py` (integrado al kernel, intercepta `tools.manus_bridge.create_task`).

```python
def create_task_with_attachment(prompt: str, account: str, project_id: str, front_id: str):
    # 1. Read head
    head = rpc_get_context_head(project_id, front_id)
    
    # 2. Validate freshness
    staleness = check_staleness(head.updated_at)
    if staleness == "STALE_RECOVERY":
        head = execute_recovery_scan(project_id, front_id)
        
    # 3. Verify artifacts (GH PRs, Railway health)
    verify_evidence(head.evidence_refs)
    
    # 4. Build pack
    attachment_pack = build_attachment_ok_contract(head)
    
    # 5. Hydrate prompt
    hydrated_prompt = f"{attachment_pack}\n\nUSER_PROMPT:\n{prompt}"
    
    # 6. Call actual Manus API
    return manus_bridge.create_task(hydrated_prompt, account, project_id)
```

## §A.6 Guardian Verifier

Ubicación: Extensión a `tools/cowork_guardian.py`.

El agente Manus, al recibir el `ATTACHMENT_OK`, debe invocar a Guardian.
Si el agente intenta ejecutar una acción que viola `do_not_touch` o se desvía del `front_id` inyectado, Guardian emite `HALT_ATTACHMENT_MISMATCH` y bloquea la ejecución.

## §A.7 Snapshot Writer Incremental

La escritura de snapshots no depende de un solo evento de cierre. Se usan 3 mecanismos para mitigar crashes y staleness:

**1. agent_explicit_writer** (`kernel/anti_dory/writers.py`):
El agente (o el kernel en su nombre) llama a estos métodos durante su ciclo de vida.

```python
# kernel/anti_dory/writers.py — agent_explicit_writer
class AgentExplicitWriter:
    def write_on_start(self, project_id: str, front_id: str, sprint_id: str, ...) -> UUID:
        """Llamado por agent al iniciar sesión. INSERT runtime_events + snapshot tipo session_started."""

    def write_on_transition(self, snapshot_id: UUID, new_phase: str, previous_phase: str, ...) -> UUID:
        """Llamado en cambio de fase (audit→spec, spec→impl, etc.). Crea snapshot con parent_snapshot_id."""

    def write_on_artifact(self, snapshot_id: UUID, artifact_path: str, artifact_type: str, ...) -> None:
        """Llamado tras crear/modificar artifact relevante (PR, commit, migration, módulo). INSERT runtime_events."""

    def write_on_final(self, snapshot_id: UUID, exit_status: str, summary: str, ...) -> UUID:
        """Llamado al cierre limpio sesión. Marca snapshot status=accepted + actualiza project_runtime_heads."""
```

**2. heartbeat_writer** (INDEPENDIENTE):
Cron job externo (ej. cron de Railway) ejecutado cada 10-15 minutos. 
Escanea `runtime_events` recientes. Si detecta actividad sin un snapshot reciente (posible crash o freeze del agente), infiere el estado y escribe un snapshot de backup. 
**CRÍTICO:** NO depende del `agent_explicit_writer` ni del agente mismo. Es el "black box recorder" que garantiza recuperación incluso si el hilo Manus muere abruptamente.

**3. external_polling** (Opcional):
Cowork observando pasivamente a Manus.

## §A.8 Recovery Mode

Si el `head` está stale (>24h) o hubo crash sin `write_on_final`, el Broker entra en Recovery.
Escanea `runtime_events`, commits en GH, y logs de Railway.
Produce UN (1) solo estado probable.
Prompt al usuario: *"Encontré snapshot [ID] en sprint [X] con confianza 0.85. ¿Retomo? Sí/No."*
Cero reexplicación humana.

## §A.9 Staleness Policy

1. **≤ 60 min:** FRESH. Se inyecta directo.
2. **60 min - 24h:** VERIFY. Se inyecta pero Guardian fuerza re-check de `evidence_refs`.
3. **> 24h:** STALE. Dispara Recovery Scan.
4. **Mismatch:** HALT. (Ej: snapshot dice PR #118 open, pero GH dice merged).
5. **Blocked by T1:** HALT. (Sprint explícitamente pausado por Alfredo).

## §A.10 Contrato ATTACHMENT_OK

Bloque JSON/Markdown inyectado pre-prompt:
```json
{
  "contract": "ATTACHMENT_OK",
  "snapshot_id": "uuid",
  "project_id": "el-monstruo",
  "front_id": "anti-dory",
  "sprint_id": "MANUS-ANTI-DORY-002",
  "phase": "FASE B",
  "last_t1_decision": "Implementación real inmediata autorizada",
  "next_expected_action": "Crear migrations 0029, 0030, 0031",
  "do_not_touch": ["PR #118", "/mnt/desktop/el-monstruo", "secrets"],
  "evidence_refs": ["gh pr view 122", "railway /health"]
}
```

## §A.11 RAP-002 Test Harness

`tests/test_anti_dory_rap_002.py` (7 casos):
- **A:** Virgen retoma sin reexplicación (Happy path).
- **B:** Crash mid-thread recupera vía heartbeat.
- **C:** Concurrencia (compare-and-swap rechaza update stale).
- **D:** Snapshot stale (>24h) fuerza Recovery Mode.
- **E:** Artifact faltante (Mismatch GH) dispara HALT.
- **F:** Sprint bloqueado por T1 no revive.
- **G:** Pregunta ambigua del usuario ofrece cabeza canónica binaria.

## §A.12 Definition of Done (Binaria)

- [ ] 3 migrations creadas y aplicadas (0029, 0030, 0031).
- [ ] 5 RPCs creados con `SECURITY DEFINER`.
- [ ] `tools/manus_bridge.py` interceptado por Context Broker.
- [ ] 4 modos `agent_explicit_writer` implementados.
- [ ] `heartbeat_writer` configurado independiente.
- [ ] 7/7 tests RAP-002 PASS.
- [ ] Cero leaks de secrets.

## §A.13 Limitaciones y Consecuencias (DSC-G-008 v3 §4)

**Limitaciones Esperadas:**
- L1: Si Supabase cae, el Context Broker no puede hidratar y bloquea la creación del hilo (Fail-closed).
- L2: El `heartbeat_writer` requiere infraestructura externa (Railway cron) para no depender del agente.

**Consecuencias Materiales:**
- C1: Costo de latencia pre-task.create (~2-4s adicionales por llamadas a Supabase y GH).
- C2: Manus consumirá ~200-300 tokens extra por hilo de entrada (el tamaño del `ATTACHMENT_OK`).
- C3: La memoria no es infinita; es un puntero (head) al estado operativo. Para memoria profunda de código, sigue dependiendo de grep/find.
