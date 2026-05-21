# 10 SPLIT-BRAIN RISK MODEL

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Riesgo P0: Split-Brain
Ocurre cuando dos loops creen tener la autoridad exclusiva sobre el mismo estado y toman decisiones contradictorias, o cuando la base de datos se bifurca en dos versiones de la verdad.

## Mitigaciones en v0 (Local-First)
1. **Single-Writer Lock:** Solo el proceso Reducer puede escribir `current_state.v0.json`.
2. **Git como Lock Distribuido:** En un entorno file-backed, Git actúa como árbitro. Si dos loops intentan pushear eventos contradictorios al `event_log.v0.jsonl`, Git rechazará el segundo push (merge conflict). El loop perdedor debe hacer pull, re-leer el estado, y re-evaluar si su evento sigue siendo válido.
3. **Cursores Estrictos:** Si un loop detecta que el `last_event_id` en el `current_state` es menor que su propio cursor interno, sabe que el estado consolidado está atrasado y debe esperar antes de actuar.

## Evolución a v1 (Productivo)
Cuando se migre a Supabase/Postgres, el Event Log usará transacciones ACID y constraints de unicidad (`dedupe_key`) para rechazar eventos duplicados o contradictorios a nivel de base de datos.
