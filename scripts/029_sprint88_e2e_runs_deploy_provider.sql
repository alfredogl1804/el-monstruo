-- Migration 029 — Sprint 88 Tarea 3.B.2
-- Propagar deploy_provider al rollup del run (no solo al e2e_step_log).
--
-- Contexto: Sprint 87.2 dejó deploy_provider visible solo en e2e_step_log.output_payload
-- del step 9 (JSONB). El dashboard lee directamente de e2e_runs y mostraba "provider"
-- vacío. Esta migración agrega la columna como mirror del payload del step de deploy.
--
-- Idempotente. Safe to re-run.

ALTER TABLE e2e_runs
    ADD COLUMN IF NOT EXISTS deploy_provider TEXT;

COMMENT ON COLUMN e2e_runs.deploy_provider IS
    'Proveedor de hosting del deploy real: github_pages, railway, fallback. Sprint 88 T3.B.2.';

-- Backfill cosmético: para runs antiguos cuyo step_log dice deploy_provider, copiarlo.
-- Esto es opcional pero útil para auditoría histórica.
UPDATE e2e_runs r
SET deploy_provider = sub.provider
FROM (
    SELECT
        sl.run_id,
        sl.output_payload ->> 'deploy_provider' AS provider
    FROM e2e_step_log sl
    WHERE sl.step_number = 9
      AND sl.status = 'ok'
      AND sl.output_payload ? 'deploy_provider'
) sub
WHERE r.id = sub.run_id
  AND r.deploy_provider IS NULL;
