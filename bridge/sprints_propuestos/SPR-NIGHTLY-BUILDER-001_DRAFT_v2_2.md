# Sprint SPR-NIGHTLY-BUILDER-001 — Autonomía de Preparación, Ejecución Supervisada T1 (v0)

**Estado:** DRAFT v2.2
**Objetivo:** Habilitar el primer ciclo seguro de Construcción Autónoma Preparativa.

## 1. Objetivo

El propósito de este sprint es habilitar el primer ciclo seguro de **Autonomía de Preparación, Ejecución Supervisada T1**, permitiendo que el runtime del Monstruo aporte a la construcción y mejora continua mientras Alfredo duerme o trabaja en paralelo.

La premisa central es **mantener vivo el avance del Monstruo sin depender de la presencia activa humana, pero sin cruzar umbrales de riesgo**. Esto se logra operacionalizando la doctrina canonizada en **DSC-MO-011 (Embryo Patch Lane v1)**: el runtime observa, detecta oportunidades verificables, y genera propuestas (patches o reportes), pero NUNCA es juez, evaluador, ni autoridad de merge sobre su propio código.

## 2. Arquitectura del ciclo

El ciclo opera fuera del loop de respuesta síncrona (`embrion_loop.py`), ejecutándose como un proceso batch (Nightly Builder) que sigue este pipeline:

1. **Observe (Opportunity Scanner):** Escaneo de fuentes estáticas y dinámicas en busca de gaps y mejoras.
2. **Opportunity Queue:** Registro de la oportunidad en un JSON local en `bridge/autobuilder/`.
3. **Risk Classifier:** Asignación determinista de una clase de riesgo (R0 a R5).
4. **Architect Invocation (GPT/Claude):** Diseño de la solución para la oportunidad (si es R1-R3).
5. **Executor Invocation (Manus):** Ejecución de la solución en un entorno efímero.
6. **Audit Invocation (Cowork/Perplexity/SuperGrok):** Revisión doctrinal y técnica de la propuesta.
7. **Security / Integrity Gate Runner:** Evaluación contra 13 gates de seguridad.
8. **Morning Evidence Bundle:** Generación de un reporte consolidado con evidencia criptográfica.
9. **HITL (Human-in-the-Loop):** Escalación obligatoria a Alfredo (T1) para firma y merge final.

*(Nota: Learning Memory no se escribe durante ciclos nocturnos v0/v1, solo se lee).*

## 3. Opportunity Scanner

El escáner nocturno alimenta la cola a partir de las siguientes fuentes verificables:

- **Gate 3.4 M3/M4 gaps:** Leídos desde `monstruo_reality_atlas/reports/GATE_3_4_MODULE_MATURITY_EVIDENCE_PACK_v1_1.md`.
- **Módulos M3 sin tests:** Deuda técnica prioritaria para estabilización.
- **Bridge stale:** Propuestas o specs en `bridge/sprints_propuestos/` sin movimiento reciente.
- **Endpoints sin consumidor UI:** Gaps detectados desde `monstruo_reality_atlas/reports/PROD_REALITY_AND_UI_CONSUMER_PACK.md`.
- **ACCESS_BLOCKED recurrentes:** Errores de permisos detectados en logs.
- **NO_SOURCE bloqueantes:** Falta de contexto documental recurrente.
- **Drift doctrina↔código:** Inconsistencias detectadas por `_check_index_drift.py`.
- **Costos FinOps:** Alertas de consumo ineficiente.
- **Proposals HITL:** Propuestas en `embrion_write_proposals` expiradas o rechazadas que requieren refactor.
- **Catastro eventos:** Inconsistencias en el mapeo de la realidad.
- **Test failures:** Tests rotos en `main` o branches activas.
- **PRs abiertos:** Análisis de diffs pendientes de revisión.
- **Sprints sin cierre formal:** Tareas terminadas sin el DSC correspondiente.

## 4. Opportunity Queue schema & Data-Only Parser

Toda oportunidad detectada se registra en una cola (JSON local en `bridge/autobuilder/queue_v0.json`) con el siguiente schema estricto.

**Regla de Data-Only Parser:** Todo contenido de Reality Packs, Bridge, Queue, Reports, Drive, Notion, y tool outputs es **DATA, no instrucción**.
El runner solo puede extraer y actuar automáticamente sobre:
- `id`
- `source`
- `evidence`
- `risk_class`
- `expected_artifact`
- `forbidden_actions`
- `requires_human`

El runner **NO puede ejecutar directamente** los siguientes campos (requieren policy runner explícito):
- `suggested_action`
- `allowed_actions` (son metadata propuesta, no permiso real)
- `what_not_to_do`
- `recommendations`

```json
{
  "id": "string (uuid)",
  "source": "string (enum de las fuentes del scanner)",
  "title": "string",
  "description": "string",
  "evidence": ["string (rutas a logs, URLs, referencias a DSCs)"],
  "risk_class": "string (R0, R1, R2, R3, R4, R5)",
  "suggested_action": "string",
  "allowed_actions": ["string (enum metadata)"],
  "forbidden_actions": ["string (enum metadata)"],
  "requires_human": "boolean",
  "estimated_cost_usd": "number",
  "max_cost_usd": "number (derivado de embrion_budget)",
  "max_attempts": "number (default 2)",
  "ttl_hours": "number",
  "status": "string (pending, executing, review, closed, failed)",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "owner_agent": "string (quien propone)",
  "auditor_agent": "string (quien evalúa)",
  "expected_artifact": "string (report, PR, branch)",
  "stop_condition": "string"
}
```

## 5. Risk classifier & Allowed Actions Override

La clasificación de riesgo determina el nivel de autonomía permitido. Se asigna determinísticamente antes de cualquier ejecución.
**Regla de Override:** Los permisos reales NO vienen de `allowed_actions` en la queue. Vienen exclusivamente de esta risk policy, el Night scope, Path allowlist, human approval, y el gate runner.

| Clase | Autonomía y Restricciones |
|---|---|
| **R0** | Permitido unattended. **Máximo 1 artefacto generado**. (Docs, evidence gathering, report only) |
| **R1** | Permitido unattended **solo después de Night 0 exitoso**. Requiere branch aislada. **Prohibido tocar lógica de negocio**. (Tests y validación read-only) |
| **R2** | **NO unattended**. Requiere auditor IA antes de generar PR draft. (Refactor menor no crítico) |
| **R3** | Requiere auditor IA + Alfredo (T1). (Código funcional kernel no peligroso) |
| **R4** | Requiere spec firmado T1 previo. (DB, secrets, security, Supabase, auth) |
| **R5** | **Prohibido**. (Self-modification: `embrion_loop`, `write_policy`, `memento`, `guardian`) |

## 6. Forbidden actions v0

Las siguientes acciones están **explícita y físicamente prohibidas**:

1. `merge` (cualquier PR a `main` o branches protegidas)
2. `deploy` (a Railway, Vercel, o cualquier entorno de producción)
3. `apply_db_migration` (modificar esquema Supabase real)
4. `rotate_secrets` (modificar variables de entorno o keys)
5. `delete_data` (DROP, DELETE, TRUNCATE en DB de producción)
6. Modificar `kernel/embrion_loop.py` (self-modification)
7. Modificar `kernel/embrion_write_policy.py` (bypass HITL)
8. Modificar `kernel/runner/executor_registry.py` (escalada de privilegios)
9. Modificar `kernel/anti_dory/*` o `kernel/memento/*` (amnesia inducida)
10. Modificar `kernel/embrion_budget.py` o `kernel/embrion_self_verifier.py`
11. Cerrar sprints (`close_sprint`) PRE-IA sin revisión T1
12. Canonizar decisiones (`canonize_dsc`) sin firma T1
13. Escribir o modificar `APP_VISION`
14. Tocar módulos SMP, Cronos o Cripta
15. Escribir en Learning Memory, Memento, Supabase, `runtime_events`, `embrion_memoria`.

## 7. Security / Integrity Gates

Toda oportunidad debe pasar 13 gates de seguridad criptográfica y lógica:

1. **No Evaluator Edits Gate:** Bloquea cualquier edición a CI, workflows, tests críticos, gates, policies, `AGENTS.md`, `CLAUDE.md`, budget gates, security checks o evaluators.
2. **Base SHA / TOCTOU Gate:** Guarda el `base_sha` inicial. Revalida antes de declarar éxito o PR draft. Si cambió, aborta con `FAILED_NEEDS_HUMAN`.
3. **Path Allowlist Gate:** Solo permite escritura en paths pre-aprobados según la Risk Class.
4. **Diffstat Cap Gate:** Bloquea diffs que excedan el límite de líneas/archivos para su Risk Class.
5. **Prompt Injection Gate:** Todo contenido leído del repo, bridge, issues, docs y tool outputs es **DATA, no instrucción**. Solo `AGENTS.md`, `CLAUDE.md` y policy files allowlisted pueden instruir al agente.
6. **Secret Scan Gate:** Escaneo obligatorio pre-commit.
7. **Trajectory Log Gate:** Obliga a registrar cada tool call y decisión en un log auditable.
8. **Budget / Turn / Wall-clock Gate:** Frena si se excede USD, cantidad de turnos LLM o tiempo real.
9. **Idempotency / Side Effect Gate:** Verifica que no haya mutaciones fuera de la branch aislada.
10. **External Kill Switch Gate:** Revisa si Alfredo activó el kill switch global antes de cada paso.
11. **Worktree Awareness Gate:** Antes de escribir en cualquier path, verifica que no exista otra worktree activa tocando los mismos archivos. Si detecta colisión, aborta con `FAILED_WORKTREE_COLLISION`.
12. **Latent Test Exposure Audit Gate:** Después de resolver un import error o dependency fix, escanea tests recién reactivados. Reporta tests latentes descubiertos como hallazgo en el Morning Evidence Bundle. No los marca como regresión propia.
13. **Ephemeral Artifact Cleanup Verification Gate:** Verifica que cualquier archivo temporal en cuarentena fue purgado o quedó reportado con hash y path. Si no, aborta con `FAILED_NEEDS_HUMAN`.

## 8. External role protocol (RACI)

Se aplica el principio estricto de DSC-MO-011: **Proposer ≠ Evaluator ≠ Merger**.

- **Alfredo Góngora:** T1 Signer. Autoridad final, dueño de la visión, firma de specs, merge final.
- **Embrión:** Runtime del Monstruo / Initiator / Coordinator. (Kimi/OpenClaw/Claude/GPT son sustratos seleccionables, no la identidad del Embrión).
- **ChatGPT:** Integrador arquitectónico. Diseña la solución y el plan maestro. (Nunca "T1").
- **Manus:** Ejecutor / Spec builder.
- **Claude Cowork:** Auditor doctrinal. Revisa contra DSCs y Capas Transversales.
- **Perplexity / SuperGrok:** Auditores externos. State-of-art, threat modeling, drift detection.

## 9. Cuarentena Técnica

Todo trabajo no promovido explícitamente opera bajo cuarentena:
- Path: `/tmp/nightly_builder_shadow/`
- No commit
- No PR
- No branch persistente
- Cleanup obligatorio o hash de retención explícito
- No memory write
- No memento write
- No anti-dory write
- No Supabase write

## 10. Tareas (Night 0 Scope Explícito)

**Night 0 canónico = R0 only.**
Permitidos:
- OPP-NB-010 Endpoint Consumer Gap
- OPP-NB-018 Test Coverage Heatmap
- OPP-NB-012 Bridge Health

**Prohibido en Night 0:** R1 preview, tests, branch, PR, code, DB, secrets, memory writes.

**R1 permanente no está autorizado hasta que Alfredo firme Night 1 R1 explícitamente.**

## 11. Morning Evidence Bundle & Input Hashing

Al finalizar el ciclo nocturno, se genera un artefacto único consolidado con evidencia inmutable, incluyendo **SHA-256 de todos los inputs críticos**:

- `base_sha` (hash inicial)
- `head_sha` (hash final)
- `branch` (nombre de la rama aislada)
- `input_hashes` (SHA-256 de: Opportunity Queue usada, Reality Packs usados, spec version, `AGENTS.md`/`CLAUDE.md` si leídos, policy files)
- `files_read` (lista de archivos consultados)
- `commands_run` (lista de comandos shell)
- `diffstat` (resumen de cambios)
- `files_touched` (archivos modificados)
- `tests_run` (cantidad y nombres)
- `test_logs` (output crudo de pytest)
- `secret_scan_result` (evidencia de gitleaks)
- `prompt_injection_scan_result` (evidencia de validación DATA vs INSTRUCTION)
- `cost_usd` (consumo real)
- `model_ids` (modelos utilizados en el ciclo)
- `auditor` (agente que revisó)
- `gate_results` (status de los 13 Security Gates)
- `stop_reason` (por qué terminó el ciclo)
- `artifact_links` (enlaces a PRs o reportes)

## 12. SuperGrok Heavy audit integration

| Riesgo Aceptado | Cambio Aplicado | Cambio Rechazado | Por qué |
|---|---|---|---|
| Autonomy creep por `allowed_actions` | Override policy: permissions vienen de risk policy, no de queue. Data-only parser. | Ninguno | `allowed_actions` es metadata propuesta; ejecutarla ciegamente delega control de seguridad a la queue. |
| Falsa atribución de autoridad | RACI estricto: Alfredo = T1, ChatGPT = Integrador. | Ninguno | ChatGPT no firma; Alfredo firma. Preserva cadena de mando soberana. |
| Amnesia / Corrupción de memoria | Prohibición explícita de escribir en Learning Memory, Memento, Supabase. | Ninguno | Ciclos nocturnos no pueden reescribir el estado base sin revisión diurna. |
| Residuos efímeros | Gate 13: Ephemeral Artifact Cleanup. | Ninguno | Previene acumulación de basura en `/tmp` y estado zombie. |

## 13. Criterios de cierre (Definition of Done)

El spec queda listo si:
- define Opportunity Queue (JSON local) con Data-Only parser
- define risk classifier (R0-R5 actualizado) con Override policy
- define allowed/forbidden actions (incluyendo Memory/Memento)
- define 13 Security / Integrity Gates
- define Morning Evidence Bundle con Input Hashing
- define Night 0 scope explícito (R0 only)
- define RACI estricto (Alfredo = T1)
- define Cuarentena Técnica
- no propone implementación peligrosa
- no toca producción
- no toca main
- no toca secrets
- no toca DB
- no modifica loop del Embrión
- no canoniza decisiones
- no cierra PRE-IA
