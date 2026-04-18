-- ============================================================
-- Sprint 10: Tool Registry + Usage Tracking
-- Run against Supabase via REST API or psql
-- ============================================================

-- ─── 1. Tool Registry ───────────────────────────────────────
-- Dynamic registry of all tools available to the kernel.
-- Replaces hardcoded tool metadata with queryable data.
CREATE TABLE IF NOT EXISTS tool_registry (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tool_name       TEXT NOT NULL UNIQUE,
    display_name    TEXT NOT NULL,
    category        TEXT NOT NULL DEFAULT 'general',  -- read, write, orchestration, autonomy, awareness
    description     TEXT,
    risk_level      TEXT NOT NULL DEFAULT 'LOW',       -- LOW, MEDIUM, HIGH
    requires_hitl   BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    parameters      JSONB DEFAULT '{}',                -- schema of accepted params
    metadata        JSONB DEFAULT '{}',                -- version, author, sprint_added, etc.
    invocation_count BIGINT NOT NULL DEFAULT 0,
    last_invoked_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 2. Usage Tracking (per-request) ────────────────────────
-- One row per kernel request with token counts and cost.
CREATE TABLE IF NOT EXISTS usage_log (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    thread_id       TEXT,
    model_used      TEXT NOT NULL,
    provider        TEXT,                              -- openai, anthropic, google, xai, openrouter, perplexity
    role_used       TEXT,                              -- estratega, investigador, etc.
    tokens_in       INTEGER NOT NULL DEFAULT 0,
    tokens_out      INTEGER NOT NULL DEFAULT 0,
    cost_usd        NUMERIC(10,6) NOT NULL DEFAULT 0,
    latency_ms      INTEGER DEFAULT 0,
    tool_calls      JSONB DEFAULT '[]',                -- list of tools invoked in this request
    status          TEXT NOT NULL DEFAULT 'completed',  -- completed, failed, timeout
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 3. Daily Aggregates (materialized for fast queries) ────
-- Pre-computed daily stats for the dashboard.
CREATE TABLE IF NOT EXISTS usage_daily (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date            DATE NOT NULL,
    model           TEXT NOT NULL,
    provider        TEXT,
    request_count   INTEGER NOT NULL DEFAULT 0,
    total_tokens_in BIGINT NOT NULL DEFAULT 0,
    total_tokens_out BIGINT NOT NULL DEFAULT 0,
    total_cost_usd  NUMERIC(12,6) NOT NULL DEFAULT 0,
    avg_latency_ms  INTEGER DEFAULT 0,
    error_count     INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, model)
);

-- ─── 4. Indexes ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_usage_log_created ON usage_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_log_model ON usage_log(model_used);
CREATE INDEX IF NOT EXISTS idx_usage_log_thread ON usage_log(thread_id);
CREATE INDEX IF NOT EXISTS idx_usage_daily_date ON usage_daily(date DESC);
CREATE INDEX IF NOT EXISTS idx_usage_daily_model ON usage_daily(model, date DESC);
CREATE INDEX IF NOT EXISTS idx_tool_registry_name ON tool_registry(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_registry_active ON tool_registry(is_active) WHERE is_active = TRUE;

-- ─── 5. Auto-update trigger ─────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_tool_registry_updated ON tool_registry;
CREATE TRIGGER trg_tool_registry_updated
    BEFORE UPDATE ON tool_registry
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_usage_daily_updated ON usage_daily;
CREATE TRIGGER trg_usage_daily_updated
    BEFORE UPDATE ON usage_daily
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ─── 6. RPC: Aggregate daily stats from usage_log ──────────
CREATE OR REPLACE FUNCTION aggregate_daily_usage(target_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO usage_daily (date, model, provider, request_count, total_tokens_in, total_tokens_out, total_cost_usd, avg_latency_ms, error_count)
    SELECT
        target_date,
        model_used,
        provider,
        COUNT(*)::INTEGER,
        COALESCE(SUM(tokens_in), 0),
        COALESCE(SUM(tokens_out), 0),
        COALESCE(SUM(cost_usd), 0),
        COALESCE(AVG(latency_ms)::INTEGER, 0),
        COUNT(*) FILTER (WHERE status = 'failed')::INTEGER
    FROM usage_log
    WHERE created_at::DATE = target_date
    GROUP BY model_used, provider
    ON CONFLICT (date, model)
    DO UPDATE SET
        request_count = EXCLUDED.request_count,
        total_tokens_in = EXCLUDED.total_tokens_in,
        total_tokens_out = EXCLUDED.total_tokens_out,
        total_cost_usd = EXCLUDED.total_cost_usd,
        avg_latency_ms = EXCLUDED.avg_latency_ms,
        error_count = EXCLUDED.error_count,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ─── 7. Seed tool_registry with current 12 tools ───────────
INSERT INTO tool_registry (tool_name, display_name, category, description, risk_level, requires_hitl, metadata)
VALUES
    ('web_search', 'Web Search', 'read', 'Search the web using Perplexity Sonar', 'LOW', FALSE, '{"sprint_added": 1, "provider": "perplexity"}'),
    ('consult_sabios', 'Consult Sabios', 'read', 'Consult one of the 6 AI models for specialized analysis', 'LOW', FALSE, '{"sprint_added": 1, "provider": "multi"}'),
    ('cidp_search', 'CIDP Search', 'read', 'Search the CIDP knowledge base', 'LOW', FALSE, '{"sprint_added": 1, "provider": "supabase"}'),
    ('cidp_get', 'CIDP Get', 'read', 'Retrieve a specific CIDP document', 'LOW', FALSE, '{"sprint_added": 1, "provider": "supabase"}'),
    ('cidp_analyze', 'CIDP Analyze', 'read', 'Analyze CIDP documents with AI', 'LOW', FALSE, '{"sprint_added": 1, "provider": "supabase"}'),
    ('email', 'Send Email', 'write', 'Send email via Gmail SMTP', 'HIGH', TRUE, '{"sprint_added": 1, "provider": "gmail"}'),
    ('call_webhook', 'Call Webhook', 'write', 'Call external webhooks (Zapier, Make, n8n, Slack)', 'HIGH', TRUE, '{"sprint_added": 5, "provider": "http"}'),
    ('github', 'GitHub', 'read', 'Interact with GitHub repositories, issues, PRs', 'MEDIUM', FALSE, '{"sprint_added": 6, "provider": "github"}'),
    ('notion', 'Notion', 'read', 'Search, read, write Notion pages and databases', 'MEDIUM', FALSE, '{"sprint_added": 6, "provider": "notion"}'),
    ('delegate_task', 'Delegate Task', 'orchestration', 'Delegate tasks to specialized AI models', 'LOW', FALSE, '{"sprint_added": 7, "provider": "multi"}'),
    ('schedule_task', 'Schedule Task', 'autonomy', 'Schedule tasks for future autonomous execution', 'MEDIUM', FALSE, '{"sprint_added": 8, "provider": "kernel"}'),
    ('user_dossier', 'User Dossier', 'awareness', 'Read/update user profile and active missions', 'MEDIUM', TRUE, '{"sprint_added": 9, "provider": "supabase"}')
ON CONFLICT (tool_name) DO NOTHING;
