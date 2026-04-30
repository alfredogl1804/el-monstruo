-- ============================================================
-- El Monstruo — Sprint 35: Background Mode Completo
-- Migration: 007_create_background_jobs_table.sql
-- Created: 2026-04-29
-- ============================================================
-- Table: background_jobs
-- Persiste los jobs del endpoint /v1/background en Supabase.
-- Reemplaza el dict en memoria (background_jobs: dict[str, dict])
-- que se perdía en cada reinicio de Railway.
--
-- Diferencia con scheduled_jobs:
--   - scheduled_jobs: tareas programadas para el futuro (cron/autonomy)
--   - background_jobs: tareas enviadas ahora, ejecutadas inmediatamente en background
-- ============================================================

CREATE TABLE IF NOT EXISTS background_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         TEXT NOT NULL DEFAULT 'anonymous',
    channel         TEXT NOT NULL DEFAULT 'api',
    message         TEXT NOT NULL,
    brain           TEXT,
    session_id      TEXT,
    metadata        JSONB,
    webhook_url     TEXT,
    status          TEXT NOT NULL DEFAULT 'queued'
                    CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
    -- Progress streaming (Gap 2)
    progress        INT NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    progress_log    JSONB NOT NULL DEFAULT '[]'::jsonb,  -- [{ts, pct, msg}]
    -- Result
    result          JSONB,
    error           TEXT,
    -- Timing
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    -- Cost tracking
    tokens_in       INT DEFAULT 0,
    tokens_out      INT DEFAULT 0,
    cost_usd        NUMERIC(10, 6) DEFAULT 0,
    latency_ms      NUMERIC(10, 2) DEFAULT 0,
    -- Cancellation (Gap 3)
    cancelled_at    TIMESTAMPTZ,
    cancel_requested BOOLEAN NOT NULL DEFAULT FALSE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_background_jobs_status
    ON background_jobs (status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_background_jobs_user_id
    ON background_jobs (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_background_jobs_session_id
    ON background_jobs (session_id)
    WHERE session_id IS NOT NULL;

-- Auto-cleanup: delete jobs older than 7 days (keep DB lean)
CREATE OR REPLACE FUNCTION cleanup_old_background_jobs()
RETURNS void AS $$
BEGIN
    DELETE FROM background_jobs
    WHERE created_at < now() - INTERVAL '7 days'
      AND status IN ('completed', 'failed', 'cancelled');
END;
$$ LANGUAGE plpgsql;

-- RPC: append a progress entry to progress_log
CREATE OR REPLACE FUNCTION bg_job_append_progress(
    p_job_id UUID,
    p_pct    INT,
    p_msg    TEXT
)
RETURNS void AS $$
BEGIN
    UPDATE background_jobs
    SET
        progress = p_pct,
        progress_log = progress_log || jsonb_build_object(
            'ts',  to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
            'pct', p_pct,
            'msg', p_msg
        )::jsonb
    WHERE id = p_job_id;
END;
$$ LANGUAGE plpgsql;
