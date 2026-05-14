---
id: SABIO_GPT_5_5_PRO_audit_anti_dory_002_2026_05_13
fecha: 2026-05-13T22:50:00Z
emisor: GPT-5.5 Pro (OpenAI) — Sabio razonamiento profundo
receptor: Cowork T2-A + Alfredo Góngora T1
tipo: audit_arquitectonico_magno_anti_dory_pre_implementacion
firma_T1: Alfredo Góngora firmó como input doctrinal P0 2026-05-13
firma_T2A: Cowork T2-A canonizó verbatim sin modificar
status: input_doctrinal_firme — convertir a SPEC V1 via Manus + implementación real autorizada
frase_canonica_magna: "Anti-Dory no es memoria. Es attachment operativo verificable antes del primer pensamiento del agente."
---

# Audit GPT-5.5 Pro — MANUS-ANTI-DORY-002 v0 → v1

## §0 Veredicto ejecutivo

**NO autorizar implementación tal cual. Autorizar solo como base v0 para rediseño corto a v1.**

La propuesta de Manus identifica bien la causa visible: falta un attachment dinámico al runtime. Pero su arquitectura v0 todavía depende demasiado de que el propio agente haga lo correcto: que escriba snapshot al final, que ejecute guardian.py, que invoque skills, que no se caiga antes del cierre y que interprete bien el último estado.

Eso no es Magna/Premium. Eso es mejor que nada, pero sigue siendo frágil.

La solución correcta debe mover la responsabilidad crítica fuera del agente conversacional y ponerla en una capa externa de runtime: **No confiar en que Manus recuerde adjuntarse. El orquestador debe crear cada hilo Manus ya hidratado con el contexto operativo canónico.**

## §1 Evaluación de los 5 componentes propuestos

### 1.1 thread_snapshots — APROBAR CON MODIFICACIONES FUERTES

Problemas: no hay project_id como PK lógico, no hay schema_version, no hay parent_snapshot_id (linaje), no hay state_hash/prev_hash (detección corrupción), no hay confidence/source_evidence, no hay separación snapshot bruto vs estado canónico actual.

Separar en dos estructuras:

```
thread_snapshots (historia append-only): snapshot_id, project_id, actor_type, actor_id, source_thread_id, source_task_id, parent_snapshot_id, schema_version, created_at, valid_until, state_json, evidence_refs_json, artifact_refs_json, next_action_json, confidence_score, state_hash, prev_hash, writer, write_reason, status: candidate|accepted|superseded|rejected|recovery

project_runtime_heads (puntero canónico actual): project_id, account_id, front_id, active_snapshot_id, active_sprint_id, active_phase, lock_version, updated_at, updated_by
```

### 1.2 manus-snapshot-write — RECHAZAR TAL COMO ESTÁ

"El agente debe invocarlo antes del mensaje final" NO resuelve Dory. Casos que rompe: hilo muere por contexto, error API, colgado, interrupción, cambio de frente sin cierre, agente olvida, write falla, snapshot obsoleto post-acción externa.

**Cuatro modos obligatorios:** write_on_start, write_on_transition, write_on_artifact, write_on_final + heartbeat cada 10-15min. Convierte el snapshot en **black box recorder, no despedida ceremonial**.

### 1.3 monstruo-auto-attach — APROBAR SOLO SI SE MUEVE FUERA DE MANUS

`SELECT ... ORDER BY timestamp DESC LIMIT 1` es peligroso: mezcla frentes, no resuelve concurrencia, no valida intención, depende del hilo nuevo ejecutar la skill (lo que Dory no garantiza).

**Modificación: monstruo-context-broker externo** que recibe intención → detecta project_id → lee project_runtime_heads → valida vigencia (branch existe, PR estado correcto, artifact paths existen, sprint no bloqueado, snapshot no vencido) → genera Context Attachment Pack → crea hilo Manus ya hidratado vía API. **El agente no debe auto-attach. El orquestador debe pre-attach.**

### 1.4 Pre-hook guardian.py — APROBAR COMO SEGUNDA LÍNEA, NO PRIMARIO

Si Manus no clona repo / primer turno no ejecuta shell / agente contesta conversacionalmente / AGENTS.md no se carga → guardian no existe. RAP-001 demostró que hilo virgen responde antes de disciplina correcta.

**Jerarquía correcta:**
- Nivel 0 — Context Broker externo antes de crear hilo
- Nivel 1 — Prompt hidratado con Attachment Pack
- Nivel 2 — guardian.py verifica que agente cargó snapshot correcto
- Nivel 3 — si mismatch: HALT técnico ("snapshot no verificable. Motivo: PR #X no existe / branch divergió / artifact faltante. Acción: autorizar recovery scan o snapshot alternativo"), NO "reexplícame"

### 1.5 project_id canónico — APROBAR Y ELEVAR A REGLA P0

Sin project_id, todo lo demás se contamina. Pero no basta: necesita front_id + sprint_id + actor_id + account_id + environment_id + branch_id + task_id. Porque El Monstruo tiene varios frentes vivos (Cowork runtime, Manus runtime, Anti-Dory, Embrión, GitHub/PRs, Supabase, Memento, Seguridad, Docs). **Attach correcto = última cabeza canónica aceptada del frente operativo relevante.**

## §2 Puntos ciegos críticos

### 2.1 Write final no cubre crash
Sistema debe usar: **event log + heartbeat + snapshot incremental**, no solo snapshot final.

### 2.2 Concurrencia no resuelta
Solución: project_runtime_heads con lock_version + compare-and-swap:

```sql
UPDATE project_runtime_heads
SET active_snapshot_id = :new_snapshot, lock_version = lock_version + 1
WHERE project_id = :project_id AND front_id = :front_id AND lock_version = :expected_lock_version;
```

Si falla: conflicto. No sobrescribir silenciosamente.

### 2.3 Política de staleness
- fresh ≤60min: attach normal
- 60min-24h: attach + verify artifacts
- >24h: recovery mode
- branch/PR mismatch: recovery mode
- snapshot blocked_by_T1: no ejecutar

### 2.4 Contrato primer turno obligatorio

```
ATTACHMENT_OK
snapshot_id:
project_id:
front_id:
sprint_id:
fase:
última decisión T1:
próximo paso:
artifactos clave:
riesgos/bloqueos:
```

Si no puede llenar eso, no debe operar.

### 2.5 Métrica éxito dura — 7 criterios RAP-002

```
RAP-002-A: hilo virgen API + prompt literal → retoma sin reexplicación
RAP-002-B: hilo anterior muere sin final write → recupera heartbeat
RAP-002-C: dos hilos concurrentes → no mezcla frentes
RAP-002-D: snapshot viejo → entra recovery, no alucina
RAP-002-E: artifact faltante → HALT técnico específico
RAP-002-F: sprint bloqueado T1 → no lo revive
RAP-002-G: pregunta ambigua → ofrece cabeza canónica, no inventa
```

### 2.6 Seguridad service_key
Mejor: anti_dory_writer_key + anti_dory_reader_key + RPCs con permisos mínimos (rpc_write_thread_snapshot, rpc_get_context_head, rpc_accept_snapshot). NO acceso directo a tablas desde cada agente.

### 2.7 Memoria vs continuidad operativa
Snapshot Magna debe incluir: qué estaba haciendo, por qué, **qué está bloqueado**, **qué NO hacer**, qué decisión T1 rige, qué evidencia lo prueba, próximo paso exacto, artifactos a tocar/no tocar, rama/PR/entorno aplica. **Sin "qué NO hacer", el agente puede recuperar contexto y aun así ejecutar mal.**

## §3 Diseño v1 — 7 componentes

### Arquitectura objetivo
```
T1 Alfredo → Monstruo Context Broker externo → Supabase Runtime State
→ Manus task.create hidratado → Manus Agent → guardian.py verifica attachment
→ Snapshot/event writer incremental
```

**Principio: el hilo nuevo no nace virgen. Nace con un attachment pack inyectado antes de su primer razonamiento operativo.**

### Componente 1 — runtime_events (append-only log)
Eventos: session_started, heartbeat, decision_t1, artifact_created, artifact_modified, phase_changed, blocker_detected, handoff_ready, session_final, crash_recovery. Permite reconstrucción aunque no exista snapshot final.

### Componente 2 — thread_snapshots (compactos JSON validados)
```json
{
  "project_id": "el-monstruo",
  "front_id": "manus_anti_dory",
  "sprint_id": "MANUS-ANTI-DORY-002",
  "phase": "audit_to_spec",
  "status": "active",
  "last_t1_decision": "...",
  "blocked_items": [],
  "do_not_touch": ["PR #118", "Mac local", "keys"],
  "active_artifacts": [],
  "next_expected_action": "...",
  "evidence_refs": [],
  "freshness": {"created_at": "...", "valid_until": "..."}
}
```

### Componente 3 — project_runtime_heads (punteros canónicos)
Resuelve: cuál snapshot activo, para qué frente, con qué lock_version, quién aceptó, si bloqueado, si requiere recovery.

### Componente 4 — monstruo-context-broker (runtime EXTERNO, no skill Manus)
Responsabilidades: resolver intención → leer cabeza canónica → validar vigencia → construir prompt hidratado → crear tarea Manus → registrar attachment_id → exigir handshake inicial.

Formato pack:
```
[MONSTRUO_RUNTIME_ATTACHMENT]
attachment_id: snapshot_id: project_id: front_id: sprint_id: phase:
last_t1_decision: current_objective: next_expected_action:
do_not_touch: artifacts: evidence: staleness_status:
required_first_response_contract:
[/MONSTRUO_RUNTIME_ATTACHMENT]
```

### Componente 5 — guardian.py verificador (no fuente)
Valida: attachment_id existe, project_id coincide, sprint coincide, snapshot no stale, agente declaró bloqueos, próximo paso coincide. Si no: HALT_ATTACHMENT_MISMATCH técnico.

### Componente 6 — Snapshot writer incremental (3 mecanismos)
- agent_explicit_writer (skill llamada por agente)
- external_task_polling_writer (cron poll Manus task API)
- heartbeat_writer (cada 10-15min via runtime_events)

Si el agente muere, hay recuperación.

### Componente 7 — Recovery mode (sin reexplicación humana)
1. NO pedir reexplicación amplia a Alfredo
2. Escanear: Supabase runtime_events + GitHub branch/PR + artifacts recientes + último transcript Manus + AGENTS.md + mementos
3. Proponer 1 estado probable + nivel de confianza
4. Pedir solo confirmación binaria si hace falta

**Pregunta permitida NO: "¿dónde nos quedamos?"**
**Pregunta permitida SÍ: "Encontré snapshot X con 0.82 confianza. ¿Retomo desde aquí? Sí/No."**

## §4 Cambios concretos al spec Manus

### Objetivo
De: "Erradicar Dory usando snapshots al cierre"
A: "Erradicar Dory mediante runtime attachment externo, snapshot incremental, cabeza canónica por frente y recuperación sin reexplicación humana"

### Flujo v1
```
Durante Hilo A:
- escribe eventos + heartbeats + snapshots parciales

Al crear Hilo B:
- Context Broker lee cabeza canónica
- valida snapshot
- crea prompt hidratado
- task.create nace con attachment

Dentro de Hilo B:
- guardian verifica attachment
- agente declara ATTACHMENT_OK
- continúa sin pedir reexplicación
```

### Criterio Magna/Premium
Hilo nuevo recupera: (1) sprint activo correcto, (2) fase exacta, (3) último artifacto, (4) siguiente acción, (5) bloqueos T1, (6) cosas prohibidas, (7) evidencia frescura, (8) sin reexplicación humana, (9) sin alucinación P0, (10) en <30 segundos.

## §5 Riesgos si se implementa v0 tal cual

1. **Falsa sensación de solución** — pasa demo simple, falla en mundo real (crash mid-thread)
2. **Último snapshot equivocado** — `ORDER BY timestamp DESC LIMIT 1` adjunta frente incorrecto = confianza alta + estado incorrecto = peor que pedir contexto
3. **Reanimar trabajo bloqueado** — RAP-001 mostró alucinación de sprint activo (COWORK-MEMENTO-001) bloqueado por T1. Snapshot debe cargar blocked_by_T1, do_not_resume, requires_T1_approval
4. **Dependencia disciplina interna** — si agente debe recordar ejecutar manus-snapshot-write, diseño sigue dependiendo del agente que tiene Dory. Circular.

## §6 Veredicto final

**REQUIERE REDISEÑO MEDIO, NO REDISEÑO PROFUNDO.**

V0 tiene intuición correcta, conservar como esqueleto. NO autorizar implementación directa.

**Autorizar Manus a escribir SPEC técnico v1 solo si incorpora 10 modificaciones obligatorias:**

1. project_runtime_heads como puntero canónico
2. runtime_events append-only
3. snapshots incrementales + heartbeat (no solo final write)
4. monstruo-context-broker externo antes de task.create
5. guardian.py como verificador secundario
6. compare-and-swap / lock_version para concurrencia
7. staleness policy
8. recovery mode sin reexplicación humana
9. contrato ATTACHMENT_OK en primer turno
10. harness RAP-002 con pruebas de crash, concurrencia, stale, sprint bloqueado

## §7 Frase canónica magna

> **Anti-Dory no es memoria. Es attachment operativo verificable antes del primer pensamiento del agente.**

— GPT-5.5 Pro, 2026-05-13

## §8 Firmas + autoridad

**Audit emitida:** GPT-5.5 Pro (Sabio razonamiento profundo DSC-V-001), 2026-05-13 ~22:30 UTC
**Pasada a Cowork T2-A:** 2026-05-13 ~22:45 UTC
**Convergencia magna independiente:** Opus 4.7 Thinking Entregable A 2026-05-12 (`bridge/sabio_OPUS_4_7_THINKING_response_ronda_1_2026_05_12.md`) coincide en arquitectura
**Firma T1 input doctrinal P0:** Alfredo "accion 1 y 2 pero con implementacion real inmediata" 2026-05-13 ~22:55 UTC
**Status:** input doctrinal firme — convertir a SPEC V1 vía sprint MANUS-ANTI-DORY-002 v1 con implementación real inmediata autorizada T1
