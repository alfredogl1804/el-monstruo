# EXAMPLES: POLICY ENGINE IN ACTION

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Escenario 1: Loop de Auditoría (A2)
**Contexto:** El Dispatcher lanza un loop para revisar un PR. Le asigna `max_autonomy_level: A2`.
**Acción intentada:** El loop quiere ejecutar `prepare_draft_pr` para sugerir un fix.
**Preflight Check:**
- `action_registry_v0.yaml` dice que `prepare_draft_pr` requiere **A4**.
- Nivel del loop (A2) < Nivel requerido (A4).
- **Resultado:** REJECT (Autonomy Exceeded). El loop solo puede escribir un reporte (A2).

## Escenario 2: Nightly Builder en R1 (A3)
**Contexto:** El Nightly Builder lanza un loop de Self-Evolution con `max_autonomy_level: A3` (permitido por R1_UNLOCKED).
**Acción intentada:** El loop quiere ejecutar `update_thread_archive` en el path `bridge/thread_archives/`.
**Preflight Check:**
- Acción requiere A3. El loop es A3. (Pasa).
- Path `bridge/thread_archives/` está en `allowed_paths`. (Pasa).
- Evidencia adjunta: Sí. (Pasa).
- **Resultado:** ALLOW.

## Escenario 3: Ejecución Productiva sin T1 (A7)
**Contexto:** Un loop A7 (máximo nivel operativo) intenta ejecutar `touch_supabase`.
**Acción intentada:** Actualizar un registro en la base de datos de producción.
**Preflight Check:**
- Acción requiere A7. El loop es A7. (Pasa).
- Acción requiere `t1_required: true`.
- El loop busca la firma T1 en el State Fabric para esta acción específica. No la encuentra.
- **Resultado:** REJECT (Missing T1 Approval).

## Escenario 4: Auditor del mismo linaje (A4)
**Contexto:** El Loop 101 (A4) prepara un draft PR. El Dispatcher lanza el Loop 102 (A4) para auditarlo. Resulta que el Loop 102 fue forkeado del contexto del Loop 101.
**Acción intentada:** Loop 102 intenta aprobar el PR draft.
**Preflight Check:**
- Acción `prepare_draft_pr` requiere `auditor_required: true`.
- El Policy Engine detecta que `Loop 101.lineage_id == Loop 102.lineage_id`.
- **Resultado:** REJECT (Auditor Lineage Conflict).
