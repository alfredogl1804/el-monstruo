# Sprint SPR-NIGHTLY-BUILDER-001 — Autonomía de Preparación, Ejecución Supervisada T1 (v0)

**Estado:** DRAFT v2.1
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
6. **Audit Invocation (Cowork/Perplexity):** Revisión doctrinal y técnica de la propuesta.
7. **Security / Integrity Gate Runner:** Evaluación contra 12 gates de seguridad.
8. **Morning Evidence Bundle:** Generación de un reporte consolidado con evidencia criptográfica.
9. **Learning Memory:** Registro del resultado para no repetir errores (Obj Maestro #4).
10. **HITL (Human-in-the-Loop):** Escalación obligatoria a Alfredo (T1) para firma y merge final.

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

## 4. Opportunity Queue schema

Toda oportunidad detectada se registra en una cola (JSON local en `bridge/autobuilder/queue_v0.json`) con el siguiente schema estricto:

```json
{
  "id": "string (uuid)",
  "source": "string (enum de las fuentes del scanner)",
  "title": "string",
  "description": "string",
  "evidence": ["string (rutas a logs, URLs, referencias a DSCs)"],
  "risk_class": "string (R0, R1, R2, R3, R4, R5)",
  "suggested_action": "string",
  "allowed_actions": ["string (enum de acciones permitidas)"],
  "forbidden_actions": ["string (enum de acciones prohibidas)"],
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

## 5. Risk classifier

La clasificación de riesgo determina el nivel de autonomía permitido. Se asigna determinísticamente antes de cualquier ejecución:

| Clase | Autonomía y Restricciones |
|---|---|
| **R0** | Permitido unattended. Máximo 1 artefacto generado. (Docs, evidence gathering, report only) |
| **R1** | Permitido unattended **solo después de R0 exitoso**. Requiere branch aislada. Prohibido tocar lógica de negocio. (Tests y validación read-only) |
| **R2** | **NO unattended**. Requiere auditor IA antes de generar PR draft. (Refactor menor no crítico) |
| **R3** | Requiere auditor IA + Alfredo (T1). (Código funcional kernel no peligroso) |
| **R4** | **Prohibido en modo nocturno**. Requiere spec firmado T1 previo. (DB, secrets, security, Supabase, auth) |
| **R5** | **Prohibido en v0**. (Self-modification: `embrion_loop`, `write_policy`, `memento`, `guardian`) |

## 6. Allowed actions v0

Durante la fase v0, el Nightly Builder solo tiene permitido ejecutar las siguientes acciones a través del `executor_registry`:

1. `generate_report` (sintetizar hallazgos en Markdown)
2. `create_local_branch` (aislamiento de trabajo)
3. `write_tests` (crear archivos `test_*.py`)
4. `run_tests` (ejecutar pytest en entorno efímero)
5. `create_artifact` (guardar diffs o scripts)
6. `prepare_pr_draft` (usar `gh pr create --draft`)
7. `request_audit` (enviar payload a Cowork/Perplexity)
8. `create_morning_report` (consolidar el trabajo de la noche)

## 7. Forbidden actions v0

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

## 8. Security / Integrity Gates

Toda oportunidad debe pasar 12 gates de seguridad criptográfica y lógica:

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
11. **Worktree Awareness Gate:** Antes de escribir en cualquier path, verifica que no exista otra worktree activa tocando los mismos archivos. Si detecta colisión, aborta con `FAILED_WORKTREE_COLLISION` y reporta las worktrees en conflicto.
12. **Latent Test Exposure Audit Gate:** Después de resolver un import error o dependency fix, ejecuta un scan de tests recién reactivados (tests que antes fallaban por import y ahora corren). Reporta tests latentes descubiertos como hallazgo en el Morning Evidence Bundle. No los marca como regresión propia.

## 9. External role protocol

Se aplica el principio estricto de DSC-MO-011: **Proposer ≠ Evaluator ≠ Merger**.

- **Embrión:** Runtime del Monstruo / Initiator / Coordinator. El modelo subyacente (Kimi/OpenClaw/Claude/GPT) es solo sustrato, no la identidad del Embrión.
- **ChatGPT 5.4 / GPT-5:** Architect. Diseña la solución y el plan de implementación.
- **Manus / Claude Code:** Executor. Escribe el código, corre tests, abre el PR Draft.
- **Claude Cowork:** Doctrinal Auditor. Revisa el PR contra los DSCs canonizados y las 7 Capas Transversales.
- **Perplexity Sonar:** External / State-of-art Auditor. Valida si la solución usa librerías obsoletas o patrones deprecados.
- **Alfredo Góngora:** T1 Signer. Autoridad final. Revisa el Morning Evidence Bundle y ejecuta el Merge/Deploy.

**Regla de oro:** Quien ejecuta no audita; quien propone no firma; quien falla 2 veces se detiene.

## 10. Tareas (First safe opportunity types)

Para la versión v0, el scanner solo poblará la cola con tipos de oportunidades R0-R1.

### Night 0 Scope Explícito
**Night 0 solo puede ejecutar una (1) tarea:**
- **Tarea:** OPP-NB-010 Endpoint Consumer Gap
- **Tipo:** R0
- **Restricciones:** Sin branch, sin PR, sin tests, sin código, sin DB, sin secrets, sin Supabase, sin deploy, sin canonización.
- **Artifact esperado:** Un reporte Markdown (`bridge/autobuilder/NIGHT_0_ENDPOINT_CONSUMER_GAP_2026_05_18.md`).

### Tareas futuras (post Night 0)
1. Escribir tests unitarios para `memory_routes` (R1)
2. Escribir tests unitarios para `finops_routes` (R1)
3. Escribir tests unitarios para `moc_routes` (R1)
4. Análisis y clasificación de errores `ACCESS_BLOCKED` (R0)
5. Reporte de drift entre estado documentado de endpoints y código real (R0)

## 11. Morning Evidence Bundle

Al finalizar el ciclo nocturno, se genera un artefacto único consolidado con evidencia inmutable:

- `base_sha` (hash inicial)
- `head_sha` (hash final)
- `branch` (nombre de la rama aislada)
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
- `gate_results` (status de los 12 Security Gates)
- `stop_reason` (por qué terminó el ciclo)
- `artifact_links` (enlaces a PRs o reportes)

## 12. Criterios de cierre (Definition of Done)

El spec queda listo si:
- define Opportunity Queue (JSON local)
- define risk classifier (R0-R5 actualizado)
- define allowed/forbidden actions
- define 12 Security / Integrity Gates
- define Morning Evidence Bundle
- define Night 0 scope explícito
- define no-go zones (No Evaluator Edits)
- no propone implementación peligrosa
- no toca producción
- no toca main
- no toca secrets
- no toca DB
- no modifica loop del Embrión
- no canoniza decisiones
- no cierra PRE-IA

## 13. Proposed File Paths

Para la implementación futura, se proponen los siguientes paths (ninguno modifica el kernel actual):

- `bridge/autobuilder/queue_v0.json` (Opportunity Queue)
- `scripts/nightly_builder/scanner.py`
- `scripts/nightly_builder/risk_classifier.py`
- `scripts/nightly_builder/security_gates.py`
- `scripts/nightly_builder/morning_bundle.py`
