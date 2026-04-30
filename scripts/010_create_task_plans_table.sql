-- Sprint 40: Task Planner — tabla para persistir planes de tareas del Embrión
-- Almacena el estado completo de cada plan: pasos, progreso, costos, resultados

CREATE TABLE IF NOT EXISTS task_plans (
    plan_id         TEXT PRIMARY KEY,
    objective       TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'created',  -- created|running|done|failed|cancelled|revised
    steps_json      JSONB NOT NULL DEFAULT '[]',
    progress_pct    NUMERIC(5,2) DEFAULT 0,
    total_steps     INTEGER DEFAULT 0,
    done_steps      INTEGER DEFAULT 0,
    failed_steps    INTEGER DEFAULT 0,
    total_tokens    INTEGER DEFAULT 0,
    total_cost_usd  NUMERIC(10,6) DEFAULT 0,
    revision_count  INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    finished_at     TIMESTAMPTZ,
    final_summary   TEXT,
    context_json    JSONB DEFAULT '{}'
);

-- Índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_task_plans_status ON task_plans(status);
CREATE INDEX IF NOT EXISTS idx_task_plans_created_at ON task_plans(created_at DESC);

-- RLS: solo el service role puede leer/escribir
ALTER TABLE task_plans ENABLE ROW LEVEL SECURITY;

-- Política para service role (kernel en Railway)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'task_plans' AND policyname = 'service_role_all'
    ) THEN
        CREATE POLICY service_role_all ON task_plans
            FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;
END $$;

-- Comentarios
COMMENT ON TABLE task_plans IS 'Sprint 40: Task Planner — planes de tareas multi-paso del Embrión';
COMMENT ON COLUMN task_plans.status IS 'created|running|done|failed|cancelled|revised';
COMMENT ON COLUMN task_plans.steps_json IS 'Array de TaskStep serializado como JSON';
COMMENT ON COLUMN task_plans.revision_count IS 'Número de veces que el plan fue revisado por fallos';
