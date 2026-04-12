-- El Monstruo — Migration 001: Event Store
-- Sprint 1 — Sovereign Memory Schema
-- Run against Supabase Postgres

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ── Events (append-only event log) ─────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
    event_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category       TEXT NOT NULL,
    severity       TEXT NOT NULL DEFAULT 'info',
    run_id         UUID,
    user_id        TEXT,
    channel        TEXT,
    actor          TEXT NOT NULL,
    action         TEXT NOT NULL,
    payload        JSONB NOT NULL DEFAULT '{}',
    parent_id      UUID REFERENCES events(event_id),
    trace_id       TEXT,
    span_id        TEXT,
    version        TEXT NOT NULL DEFAULT '1.0.0',
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_events_run_id ON events(run_id);
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_events_created_at ON events(created_at DESC);

-- ── Episodes ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS episodes (
    episode_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id        TEXT NOT NULL,
    channel        TEXT NOT NULL,
    summary        TEXT,
    started_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at       TIMESTAMPTZ
);

CREATE INDEX idx_episodes_user_id ON episodes(user_id);

-- ── Memory Events (with embeddings for semantic search) ────────────
CREATE TABLE IF NOT EXISTS memory_events (
    event_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    memory_type    TEXT NOT NULL,
    run_id         UUID,
    user_id        TEXT,
    channel        TEXT,
    content        TEXT NOT NULL,
    embedding      vector(1536),
    metadata       JSONB NOT NULL DEFAULT '{}',
    episode_id     UUID REFERENCES episodes(episode_id),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_memory_events_user_id ON memory_events(user_id);
CREATE INDEX idx_memory_events_type ON memory_events(memory_type);
CREATE INDEX idx_memory_events_embedding ON memory_events
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ── Entities (knowledge graph nodes) ───────────────────────────────
CREATE TABLE IF NOT EXISTS entities (
    entity_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type    TEXT NOT NULL,
    name           TEXT NOT NULL,
    attributes     JSONB NOT NULL DEFAULT '{}',
    first_seen     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_entities_type ON entities(entity_type);

-- ── Relations (knowledge graph edges) ──────────────────────────────
CREATE TABLE IF NOT EXISTS relations (
    relation_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id      UUID NOT NULL REFERENCES entities(entity_id),
    target_id      UUID NOT NULL REFERENCES entities(entity_id),
    relation_type  TEXT NOT NULL,
    weight         FLOAT NOT NULL DEFAULT 1.0,
    metadata       JSONB NOT NULL DEFAULT '{}',
    valid_from     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to       TIMESTAMPTZ
);

CREATE INDEX idx_relations_source ON relations(source_id);
CREATE INDEX idx_relations_target ON relations(target_id);
CREATE INDEX idx_relations_type ON relations(relation_type);

-- ── Tool Calls ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tool_calls (
    call_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id         UUID NOT NULL,
    tool_name      TEXT NOT NULL,
    tool_args      JSONB NOT NULL DEFAULT '{}',
    result         JSONB,
    status         TEXT NOT NULL DEFAULT 'pending',
    started_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at   TIMESTAMPTZ,
    duration_ms    FLOAT
);

CREATE INDEX idx_tool_calls_run_id ON tool_calls(run_id);

-- ── Policy Decisions ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS policy_decisions (
    decision_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id         UUID,
    policy_name    TEXT NOT NULL,
    verdict        TEXT NOT NULL,
    reason         TEXT,
    modifications  JSONB,
    evaluated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_policy_decisions_run_id ON policy_decisions(run_id);

-- ── Checkpoints ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    checkpoint_type TEXT NOT NULL DEFAULT 'auto',
    run_id         UUID,
    step           INT NOT NULL DEFAULT 0,
    kernel_state   JSONB NOT NULL DEFAULT '{}',
    memory_state   JSONB NOT NULL DEFAULT '{}',
    router_state   JSONB NOT NULL DEFAULT '{}',
    policy_state   JSONB NOT NULL DEFAULT '{}',
    active_tools   JSONB NOT NULL DEFAULT '[]',
    pending_actions JSONB NOT NULL DEFAULT '[]',
    conversation_context JSONB NOT NULL DEFAULT '{}',
    reason         TEXT,
    ttl_hours      INT NOT NULL DEFAULT 168,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_checkpoints_run_id ON checkpoints(run_id);

-- ── System State ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS system_state (
    state_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    health         TEXT NOT NULL DEFAULT 'healthy',
    active_runs    INT NOT NULL DEFAULT 0,
    total_runs_today INT NOT NULL DEFAULT 0,
    total_cost_today_usd FLOAT NOT NULL DEFAULT 0.0,
    total_tokens_today INT NOT NULL DEFAULT 0,
    models_available JSONB NOT NULL DEFAULT '[]',
    models_degraded JSONB NOT NULL DEFAULT '[]',
    last_error     TEXT,
    uptime_seconds FLOAT NOT NULL DEFAULT 0.0,
    checked_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Incidents ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS incidents (
    incident_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id         UUID,
    severity       TEXT NOT NULL,
    actor          TEXT NOT NULL,
    description    TEXT NOT NULL,
    stack_trace    TEXT,
    resolved       BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at    TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_resolved ON incidents(resolved);
