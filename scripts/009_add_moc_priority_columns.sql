-- =====================================================================
-- Sprint 37: MOC Priority Columns
-- Agrega columnas de priorización al scheduler existente.
-- Estas columnas alimentan al Priorizador del MOC para scoring dinámico.
-- =====================================================================

-- Columnas de priorización en scheduled_jobs
ALTER TABLE scheduled_jobs
  ADD COLUMN IF NOT EXISTS task_type TEXT DEFAULT 'default',
  ADD COLUMN IF NOT EXISTS estimated_cost_usd FLOAT DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS success_rate FLOAT DEFAULT 1.0,
  ADD COLUMN IF NOT EXISTS moc_priority_score FLOAT DEFAULT 50.0,
  ADD COLUMN IF NOT EXISTS last_prioritized_at TIMESTAMPTZ;

-- Índice para consultas del MOC por score
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_moc_score
  ON scheduled_jobs(moc_priority_score DESC, run_at ASC)
  WHERE status = 'scheduled';

-- Columna cost_usd en job_executions (si no existe)
ALTER TABLE job_executions
  ADD COLUMN IF NOT EXISTS cost_usd FLOAT DEFAULT 0.0;

-- Función para calcular success_rate de un job
-- Cuenta las últimas 20 ejecuciones y calcula el ratio de éxito
CREATE OR REPLACE FUNCTION calculate_job_success_rate(p_job_id UUID)
RETURNS FLOAT AS $$
DECLARE
  v_total INT;
  v_completed INT;
BEGIN
  SELECT
    COUNT(*),
    COUNT(*) FILTER (WHERE status = 'completed')
  INTO v_total, v_completed
  FROM job_executions
  WHERE scheduled_job_id = p_job_id
  ORDER BY started_at DESC
  LIMIT 20;

  IF v_total = 0 THEN
    RETURN 1.0; -- Sin historial → asumir éxito
  END IF;

  RETURN v_completed::FLOAT / v_total::FLOAT;
END;
$$ LANGUAGE plpgsql;

-- Vista para observabilidad del MOC
CREATE OR REPLACE VIEW moc_jobs_overview AS
SELECT
  sj.id,
  sj.title,
  sj.task_type,
  sj.status,
  sj.run_at,
  sj.success_rate,
  sj.moc_priority_score,
  sj.estimated_cost_usd,
  sj.last_prioritized_at,
  COUNT(je.id) AS total_executions,
  MAX(je.finished_at) AS last_executed_at
FROM scheduled_jobs sj
LEFT JOIN job_executions je ON je.scheduled_job_id = sj.id
GROUP BY sj.id, sj.title, sj.task_type, sj.status, sj.run_at,
         sj.success_rate, sj.moc_priority_score, sj.estimated_cost_usd,
         sj.last_prioritized_at
ORDER BY sj.moc_priority_score DESC, sj.run_at ASC;
