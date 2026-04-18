-- ============================================================
-- El Monstruo — Sprint 8: Autonomía Temporal
-- Migration: 002_create_autonomy_tables.sql
-- Created: 2026-04-18
-- ============================================================

-- Table: scheduled_jobs
-- Stores all scheduled tasks created by the schedule_task tool
CREATE TABLE IF NOT EXISTS scheduled_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         TEXT NOT NULL,
    thread_id       TEXT,
    title           TEXT NOT NULL,
    instruction     TEXT NOT NULL,
    run_at          TIMESTAMPTZ NOT NULL,
    timezone        TEXT NOT NULL DEFAULT 'America/Mexico_City',
    channel         TEXT NOT NULL DEFAULT 'telegram',
    status          TEXT NOT NULL DEFAULT 'scheduled'
                    CHECK (status IN ('scheduled', 'running', 'completed', 'failed', 'cancelled')),
    recurrence      TEXT DEFAULT NULL,  -- NULL = one-shot, 'daily' = repeat daily
    max_retries     INT NOT NULL DEFAULT 1,
    retry_count     INT NOT NULL DEFAULT 0,
    last_error      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table: job_executions
-- Stores the execution history of each scheduled job run
CREATE TABLE IF NOT EXISTS job_executions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheduled_job_id    UUID NOT NULL REFERENCES scheduled_jobs(id) ON DELETE CASCADE,
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at         TIMESTAMPTZ,
    status              TEXT NOT NULL DEFAULT 'running'
                        CHECK (status IN ('running', 'completed', 'failed')),
    trace_id            TEXT,
    result_summary      TEXT,
    error               TEXT,
    tokens_used         INT DEFAULT 0,
    cost_usd            NUMERIC(10, 6) DEFAULT 0
);

-- Indexes for efficient polling and querying
CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_status_run_at
    ON scheduled_jobs (status, run_at)
    WHERE status = 'scheduled';

CREATE INDEX IF NOT EXISTS idx_scheduled_jobs_user_id
    ON scheduled_jobs (user_id);

CREATE INDEX IF NOT EXISTS idx_job_executions_job_id
    ON job_executions (scheduled_job_id);

-- Auto-update updated_at on scheduled_jobs
CREATE OR REPLACE FUNCTION update_scheduled_jobs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_scheduled_jobs_updated_at ON scheduled_jobs;
CREATE TRIGGER trg_scheduled_jobs_updated_at
    BEFORE UPDATE ON scheduled_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_scheduled_jobs_updated_at();

-- RPC function: get_due_jobs
-- Called by the autonomous runner to find jobs ready to execute
CREATE OR REPLACE FUNCTION get_due_jobs(max_jobs INT DEFAULT 10)
RETURNS SETOF scheduled_jobs AS $$
BEGIN
    RETURN QUERY
    UPDATE scheduled_jobs
    SET status = 'running', updated_at = now()
    WHERE id IN (
        SELECT id FROM scheduled_jobs
        WHERE status = 'scheduled'
          AND run_at <= now()
        ORDER BY run_at ASC
        LIMIT max_jobs
        FOR UPDATE SKIP LOCKED
    )
    RETURNING *;
END;
$$ LANGUAGE plpgsql;
