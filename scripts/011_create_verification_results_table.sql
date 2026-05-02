-- SP5: ACI Repair — Execution Verification
-- Tabla para persistir resultados de verificación post-ejecución
-- Cada paso de un plan se verifica antes de marcarse como DONE
-- Verdicts: success (ejecutó realmente), continue (falta algo), pivot (cambiar enfoque)

CREATE TABLE IF NOT EXISTS verification_results (
    verification_id TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL,               -- plan_id del TaskPlan
    step_id         TEXT NOT NULL,               -- step_id del TaskStep
    step_index      INTEGER NOT NULL,            -- índice del paso en el plan
    verdict         TEXT NOT NULL DEFAULT 'continue',  -- success|continue|pivot
    evidence        JSONB NOT NULL DEFAULT '[]', -- array de evidencias concretas
    reasoning       TEXT,                        -- explicación humana del veredicto
    tool_calls_count INTEGER DEFAULT 0,          -- herramientas realmente ejecutadas
    cost_usd        NUMERIC(10,6) DEFAULT 0,     -- costo de la verificación
    verified_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_verification_results_task_id ON verification_results(task_id);
CREATE INDEX IF NOT EXISTS idx_verification_results_verdict ON verification_results(verdict);
CREATE INDEX IF NOT EXISTS idx_verification_results_verified_at ON verification_results(verified_at DESC);

-- Índice compuesto para buscar verificaciones de un paso específico
CREATE INDEX IF NOT EXISTS idx_verification_results_task_step ON verification_results(task_id, step_index);

-- RLS: solo el service role puede leer/escribir
ALTER TABLE verification_results ENABLE ROW LEVEL SECURITY;

-- Política para service role (kernel en Railway)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'verification_results' AND policyname = 'service_role_all'
    ) THEN
        CREATE POLICY service_role_all ON verification_results
            FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;
END $$;

-- Comentarios
COMMENT ON TABLE verification_results IS 'SP5: ACI Repair — verificación post-ejecución de pasos del Task Planner';
COMMENT ON COLUMN verification_results.verdict IS 'success = ejecutó realmente | continue = falta algo | pivot = cambiar enfoque';
COMMENT ON COLUMN verification_results.evidence IS 'Array de evidencias: tool_output, file_created, api_response, code_executed, etc.';
COMMENT ON COLUMN verification_results.tool_calls_count IS 'Número de herramientas realmente ejecutadas en el paso';
COMMENT ON COLUMN verification_results.cost_usd IS 'Costo de la verificación LLM (solo se usa en casos ambiguos)';
