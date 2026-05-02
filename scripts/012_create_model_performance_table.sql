-- ============================================================
-- SP9: Adaptive Model Selection — model_performance table
-- Sprint: SP9 (Embrión Superpowers)
-- ============================================================
-- Tracks which model works best for each task class.
-- Updated by AdaptiveModelSelector after each LLM call.
-- ============================================================

CREATE TABLE IF NOT EXISTS model_performance (
    id              BIGSERIAL PRIMARY KEY,
    task_class      TEXT NOT NULL,           -- creative, reasoning, factual_search, etc.
    model_id        TEXT NOT NULL,           -- gpt-5.5, claude-opus-4-7, gemini-3.1-pro, etc.
    total_calls     INTEGER DEFAULT 0,
    successes       INTEGER DEFAULT 0,
    failures        INTEGER DEFAULT 0,
    avg_latency_ms  REAL DEFAULT 0.0,
    avg_cost_usd    REAL DEFAULT 0.0,
    avg_quality_score REAL DEFAULT 0.5,      -- 0.0-1.0 (EMA)
    composite_score REAL DEFAULT 0.5,        -- Weighted composite for ranking
    last_used       DOUBLE PRECISION DEFAULT 0,
    active          BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_model_performance_class_model UNIQUE (task_class, model_id)
);

-- Index for fast lookups by task_class
CREATE INDEX IF NOT EXISTS idx_model_performance_class
    ON model_performance(task_class)
    WHERE active = TRUE;

-- Index for ranking queries
CREATE INDEX IF NOT EXISTS idx_model_performance_score
    ON model_performance(task_class, composite_score DESC)
    WHERE active = TRUE;

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_model_performance_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_model_performance_updated ON model_performance;
CREATE TRIGGER trg_model_performance_updated
    BEFORE UPDATE ON model_performance
    FOR EACH ROW
    EXECUTE FUNCTION update_model_performance_timestamp();
