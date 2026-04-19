-- ═══════════════════════════════════════════════════════════════
-- Migration 005: ADR Tool Broker — Bindings, Secrets, Executions
-- Sprint 10b — Implements ADR_SPRINT_10_Tool_Registry.md
-- ═══════════════════════════════════════════════════════════════
-- Existing tables (from 004): tool_registry, usage_log, usage_daily
-- New tables: tool_bindings, tool_secrets, tool_executions
-- Changes to tool_registry: add schema column for ADR compatibility
-- ═══════════════════════════════════════════════════════════════

-- ─── 1. Evolve tool_registry to match ADR 'tools' table ────
ALTER TABLE tool_registry
  ADD COLUMN IF NOT EXISTS schema JSONB DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS secret_env_var TEXT,
  ADD COLUMN IF NOT EXISTS max_calls_per_request INTEGER DEFAULT 5,
  ADD COLUMN IF NOT EXISTS timeout_ms INTEGER DEFAULT 30000;

-- Populate schema column from existing tool specs
UPDATE tool_registry SET schema = '{"type":"object","properties":{"query":{"type":"string"}}}'
  WHERE tool_name = 'web_search' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"model":{"type":"string"},"prompt":{"type":"string"}}}'
  WHERE tool_name = 'consult_sabios' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"query":{"type":"string"}}}'
  WHERE tool_name = 'cidp_search' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"doc_id":{"type":"string"}}}'
  WHERE tool_name = 'cidp_get' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"doc_id":{"type":"string"},"question":{"type":"string"}}}'
  WHERE tool_name = 'cidp_analyze' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"to":{"type":"string"},"subject":{"type":"string"},"body":{"type":"string"}}}'
  WHERE tool_name = 'email' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"url":{"type":"string"},"payload":{"type":"object"}}}'
  WHERE tool_name = 'call_webhook' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"action":{"type":"string"},"args":{"type":"object"}}}'
  WHERE tool_name = 'github' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"action":{"type":"string"},"args":{"type":"object"}}}'
  WHERE tool_name = 'notion' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"task":{"type":"string"},"role":{"type":"string"}}}'
  WHERE tool_name = 'delegate_task' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"task_description":{"type":"string"},"run_at":{"type":"string"}}}'
  WHERE tool_name = 'schedule_task' AND schema = '{}';
UPDATE tool_registry SET schema = '{"type":"object","properties":{"action":{"type":"string"},"args":{"type":"object"}}}'
  WHERE tool_name = 'user_dossier' AND schema = '{}';

-- Populate secret_env_var for tools that need secrets
UPDATE tool_registry SET secret_env_var = 'SONAR_API_KEY' WHERE tool_name = 'web_search';
UPDATE tool_registry SET secret_env_var = 'GITHUB_TOKEN' WHERE tool_name = 'github';
UPDATE tool_registry SET secret_env_var = 'NOTION_TOKEN' WHERE tool_name = 'notion';
UPDATE tool_registry SET secret_env_var = 'GMAIL_APP_PASSWORD' WHERE tool_name = 'email';

-- ─── 2. Tool Bindings (ADR table 2) ────────────────────────
CREATE TABLE IF NOT EXISTS tool_bindings (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id   TEXT NOT NULL DEFAULT 'alfredo',
    user_id     TEXT,
    tool_name   TEXT NOT NULL REFERENCES tool_registry(tool_name),
    is_enabled  BOOLEAN DEFAULT TRUE,
    capabilities JSONB DEFAULT '{}',
    rate_limit  INTEGER DEFAULT 100,  -- max calls per day
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, tool_name)
);

-- Seed bindings for all 12 tools (single tenant: alfredo)
INSERT INTO tool_bindings (tenant_id, user_id, tool_name, is_enabled, capabilities, rate_limit)
VALUES
    ('alfredo', 'alfredo', 'web_search', TRUE, '{"can_read": true}', 200),
    ('alfredo', 'alfredo', 'consult_sabios', TRUE, '{"can_read": true}', 50),
    ('alfredo', 'alfredo', 'cidp_search', TRUE, '{"can_read": true}', 200),
    ('alfredo', 'alfredo', 'cidp_get', TRUE, '{"can_read": true}', 200),
    ('alfredo', 'alfredo', 'cidp_analyze', TRUE, '{"can_read": true}', 100),
    ('alfredo', 'alfredo', 'email', TRUE, '{"can_read": true, "can_write": true}', 20),
    ('alfredo', 'alfredo', 'call_webhook', TRUE, '{"can_read": true, "can_write": true}', 50),
    ('alfredo', 'alfredo', 'github', TRUE, '{"can_read": true, "can_write": true}', 100),
    ('alfredo', 'alfredo', 'notion', TRUE, '{"can_read": true, "can_write": true}', 100),
    ('alfredo', 'alfredo', 'delegate_task', TRUE, '{"can_delegate": true}', 30),
    ('alfredo', 'alfredo', 'schedule_task', TRUE, '{"can_schedule": true}', 20),
    ('alfredo', 'alfredo', 'user_dossier', TRUE, '{"can_read": true, "can_write": true}', 50)
ON CONFLICT (tenant_id, tool_name) DO NOTHING;

-- ─── 3. Tool Secrets (ADR table 3) ─────────────────────────
-- References to env vars (pragmatic: no Vault/KMS for single-user)
CREATE TABLE IF NOT EXISTS tool_secrets (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    binding_id  UUID REFERENCES tool_bindings(id) ON DELETE CASCADE,
    secret_ref  TEXT NOT NULL,       -- env var name (e.g., 'SONAR_API_KEY')
    secret_type TEXT NOT NULL,       -- 'api_key', 'token', 'password'
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Seed secrets for tools that need them
INSERT INTO tool_secrets (binding_id, secret_ref, secret_type)
SELECT b.id, 'SONAR_API_KEY', 'api_key'
FROM tool_bindings b WHERE b.tool_name = 'web_search' AND b.tenant_id = 'alfredo'
ON CONFLICT DO NOTHING;

INSERT INTO tool_secrets (binding_id, secret_ref, secret_type)
SELECT b.id, 'GITHUB_TOKEN', 'token'
FROM tool_bindings b WHERE b.tool_name = 'github' AND b.tenant_id = 'alfredo'
ON CONFLICT DO NOTHING;

INSERT INTO tool_secrets (binding_id, secret_ref, secret_type)
SELECT b.id, 'NOTION_TOKEN', 'token'
FROM tool_bindings b WHERE b.tool_name = 'notion' AND b.tenant_id = 'alfredo'
ON CONFLICT DO NOTHING;

INSERT INTO tool_secrets (binding_id, secret_ref, secret_type)
SELECT b.id, 'GMAIL_APP_PASSWORD', 'password'
FROM tool_bindings b WHERE b.tool_name = 'email' AND b.tenant_id = 'alfredo'
ON CONFLICT DO NOTHING;

-- ─── 4. Tool Executions (ADR tables 4+5 merged) ────────────
CREATE TABLE IF NOT EXISTS tool_executions (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id          UUID NOT NULL,
    thread_id       TEXT,
    tenant_id       TEXT NOT NULL DEFAULT 'alfredo',
    tool_name       TEXT NOT NULL REFERENCES tool_registry(tool_name),
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending, running, success, failed
    input_args      JSONB DEFAULT '{}',
    output_summary  TEXT,
    error_message   TEXT,
    -- Usage metrics (merged from tool_usage_metrics)
    input_tokens    INTEGER DEFAULT 0,
    output_tokens   INTEGER DEFAULT 0,
    api_calls       INTEGER DEFAULT 1,
    wall_ms         INTEGER DEFAULT 0,
    cost_usd        NUMERIC(12,6) DEFAULT 0,
    -- Timestamps
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── 5. Indexes ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_tool_bindings_tenant ON tool_bindings(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tool_bindings_tool ON tool_bindings(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_secrets_binding ON tool_secrets(binding_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_run ON tool_executions(run_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_tool ON tool_executions(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_executions_status ON tool_executions(status);
CREATE INDEX IF NOT EXISTS idx_tool_executions_created ON tool_executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tool_executions_tenant ON tool_executions(tenant_id);

-- ─── 6. Triggers ────────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_tool_bindings_updated ON tool_bindings;
CREATE TRIGGER trg_tool_bindings_updated
    BEFORE UPDATE ON tool_bindings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ─── 7. RPC: Get allowed tools for a tenant ────────────────
CREATE OR REPLACE FUNCTION get_allowed_tools(p_tenant_id TEXT DEFAULT 'alfredo')
RETURNS TABLE (
    tool_name TEXT,
    display_name TEXT,
    category TEXT,
    description TEXT,
    risk_level TEXT,
    requires_hitl BOOLEAN,
    schema JSONB,
    secret_env_var TEXT,
    is_enabled BOOLEAN,
    capabilities JSONB,
    rate_limit INTEGER,
    binding_id UUID
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        tr.tool_name,
        tr.display_name,
        tr.category,
        tr.description,
        tr.risk_level,
        tr.requires_hitl,
        tr.schema,
        tr.secret_env_var,
        tb.is_enabled,
        tb.capabilities,
        tb.rate_limit,
        tb.id AS binding_id
    FROM tool_registry tr
    JOIN tool_bindings tb ON tr.tool_name = tb.tool_name
    WHERE tb.tenant_id = p_tenant_id
      AND tb.is_enabled = TRUE
      AND tr.is_active = TRUE
    ORDER BY tr.category, tr.tool_name;
END;
$$ LANGUAGE plpgsql;

-- ─── 8. RPC: Record tool execution ─────────────────────────
CREATE OR REPLACE FUNCTION record_tool_execution(
    p_run_id UUID,
    p_thread_id TEXT,
    p_tenant_id TEXT DEFAULT 'alfredo',
    p_tool_name TEXT DEFAULT '',
    p_status TEXT DEFAULT 'pending',
    p_input_args JSONB DEFAULT '{}',
    p_output_summary TEXT DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL,
    p_wall_ms INTEGER DEFAULT 0,
    p_api_calls INTEGER DEFAULT 1,
    p_cost_usd NUMERIC DEFAULT 0
)
RETURNS UUID AS $$
DECLARE
    v_exec_id UUID;
BEGIN
    INSERT INTO tool_executions (
        run_id, thread_id, tenant_id, tool_name, status,
        input_args, output_summary, error_message,
        wall_ms, api_calls, cost_usd,
        completed_at
    ) VALUES (
        p_run_id, p_thread_id, p_tenant_id, p_tool_name, p_status,
        p_input_args, p_output_summary, p_error_message,
        p_wall_ms, p_api_calls, p_cost_usd,
        CASE WHEN p_status IN ('success', 'failed') THEN NOW() ELSE NULL END
    )
    RETURNING id INTO v_exec_id;

    -- Update tool_registry last_used and invocation_count
    UPDATE tool_registry
    SET last_used_at = NOW(),
        invocation_count = invocation_count + 1
    WHERE tool_registry.tool_name = p_tool_name;

    RETURN v_exec_id;
END;
$$ LANGUAGE plpgsql;
