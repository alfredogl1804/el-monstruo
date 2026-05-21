-- Migration: 0052_sovereign_memory_system.sql
-- Sovereign Memory System v1.0 — Persistent Storage Layer
-- Purpose: Tables for sovereign axioms, memories, causal chains, knowledge gaps,
--          and multi-agent memory sharing. Universal adapter for any AI thread.
-- Author: Manus C (Batch 011 — SMS Implementation)
-- Date: 2026-05-21
-- Status: NOT APPLIED — requires T1 confirmation per migration.
--
-- Doctrina: RLS habilitado por defecto (DSC-S-006).
-- Naming: SUPABASE_SERVICE_KEY (DSC-S-007).
-- pgvector 0.8.0 already installed (confirmed in migration 0028).
-- Embedding dimension: 1536 (text-embedding-3-small, consistent with memory_events).

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE 1: sovereign_axioms
-- Crystallized understandings that NEVER decay. Compaction-proof.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sovereign_axioms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    statement TEXT NOT NULL,
    embedding vector(1536),
    confidence FLOAT NOT NULL DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    validation_count INTEGER NOT NULL DEFAULT 0,
    contradiction_count INTEGER NOT NULL DEFAULT 0,
    first_observed TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_validated TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_agent TEXT NOT NULL DEFAULT 'monstruo',
    implications JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_memories JSONB NOT NULL DEFAULT '[]'::jsonb,
    tags TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_axiom_statement UNIQUE (statement)
);

COMMENT ON TABLE sovereign_axioms IS 'SMS Layer 4: Crystallized sovereign axioms. NEVER forgotten. Compaction-proof truths.';

ALTER TABLE sovereign_axioms ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_axioms" ON sovereign_axioms
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_axioms_embedding ON sovereign_axioms
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 20);
CREATE INDEX IF NOT EXISTS idx_axioms_source_agent ON sovereign_axioms (source_agent);
CREATE INDEX IF NOT EXISTS idx_axioms_tags ON sovereign_axioms USING gin (tags);
CREATE INDEX IF NOT EXISTS idx_axioms_confidence ON sovereign_axioms (confidence DESC);
CREATE INDEX IF NOT EXISTS idx_axioms_active ON sovereign_axioms (is_active) WHERE is_active = true;

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE 2: sovereign_memories
-- Long-term memories with decay tracking. Layer 3 storage.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sovereign_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    embedding vector(1536),
    memory_type TEXT NOT NULL DEFAULT 'episodic' CHECK (memory_type IN ('episodic', 'semantic', 'procedural', 'causal')),
    layer INTEGER NOT NULL DEFAULT 3 CHECK (layer >= 1 AND layer <= 5),
    source TEXT NOT NULL DEFAULT 'system',
    agent_id TEXT NOT NULL DEFAULT 'monstruo',
    confidence FLOAT NOT NULL DEFAULT 0.7,
    strength FLOAT NOT NULL DEFAULT 1.0,
    relevance_score FLOAT NOT NULL DEFAULT 1.0,
    validation_count INTEGER NOT NULL DEFAULT 0,
    contradiction_count INTEGER NOT NULL DEFAULT 0,
    access_count INTEGER NOT NULL DEFAULT 0,
    causal_parent_id UUID REFERENCES sovereign_memories(id) ON DELETE SET NULL,
    implications JSONB NOT NULL DEFAULT '[]'::jsonb,
    entities JSONB NOT NULL DEFAULT '[]'::jsonb,
    tags TEXT[] NOT NULL DEFAULT '{}',
    is_alive BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_accessed TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_consolidated TIMESTAMPTZ,
    forgotten_at TIMESTAMPTZ,
    CONSTRAINT uq_memory_hash UNIQUE (content_hash)
);

COMMENT ON TABLE sovereign_memories IS 'SMS Layer 3: Long-term memories with Ebbinghaus decay. Subject to consolidation and forgetting.';

ALTER TABLE sovereign_memories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_memories" ON sovereign_memories
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_memories_embedding ON sovereign_memories
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX IF NOT EXISTS idx_memories_agent ON sovereign_memories (agent_id);
CREATE INDEX IF NOT EXISTS idx_memories_type ON sovereign_memories (memory_type);
CREATE INDEX IF NOT EXISTS idx_memories_alive ON sovereign_memories (is_alive) WHERE is_alive = true;
CREATE INDEX IF NOT EXISTS idx_memories_strength ON sovereign_memories (strength DESC) WHERE is_alive = true;
CREATE INDEX IF NOT EXISTS idx_memories_causal ON sovereign_memories (causal_parent_id) WHERE causal_parent_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_memories_created ON sovereign_memories (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memories_hash ON sovereign_memories (content_hash);

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE 3: sovereign_causal_chains
-- WHY chains linking events causally. Preserves reasoning history.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sovereign_causal_chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    root_memory_id UUID NOT NULL REFERENCES sovereign_memories(id) ON DELETE CASCADE,
    nodes JSONB NOT NULL DEFAULT '[]'::jsonb,  -- ordered list of memory IDs
    depth INTEGER NOT NULL DEFAULT 1,
    agent_id TEXT NOT NULL DEFAULT 'monstruo',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE sovereign_causal_chains IS 'SMS Comprehension: Causal WHY chains linking events. Preserves reasoning history.';

ALTER TABLE sovereign_causal_chains ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_chains" ON sovereign_causal_chains
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_chains_root ON sovereign_causal_chains (root_memory_id);
CREATE INDEX IF NOT EXISTS idx_chains_agent ON sovereign_causal_chains (agent_id);
CREATE INDEX IF NOT EXISTS idx_chains_depth ON sovereign_causal_chains (depth DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE 4: sovereign_knowledge_gaps
-- Self-detected gaps in understanding. Metacognition layer.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sovereign_knowledge_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    evidence TEXT NOT NULL DEFAULT '',
    severity TEXT NOT NULL DEFAULT 'MEDIUM' CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    resolution_strategy TEXT NOT NULL DEFAULT 'search',
    agent_id TEXT NOT NULL DEFAULT 'monstruo',
    is_resolved BOOLEAN NOT NULL DEFAULT false,
    resolved_by_memory_id UUID REFERENCES sovereign_memories(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE sovereign_knowledge_gaps IS 'SMS Metacognition: Self-detected knowledge gaps. Drives proactive learning.';

ALTER TABLE sovereign_knowledge_gaps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_gaps" ON sovereign_knowledge_gaps
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_gaps_resolved ON sovereign_knowledge_gaps (is_resolved) WHERE is_resolved = false;
CREATE INDEX IF NOT EXISTS idx_gaps_severity ON sovereign_knowledge_gaps (severity);
CREATE INDEX IF NOT EXISTS idx_gaps_agent ON sovereign_knowledge_gaps (agent_id);

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE 5: sovereign_conflict_log
-- Arbitration history when agents disagree.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sovereign_conflict_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_a_id UUID NOT NULL,
    memory_b_id UUID NOT NULL,
    winner_id UUID NOT NULL,
    reason TEXT NOT NULL,
    resolution_method TEXT NOT NULL DEFAULT 'confidence_based',
    resolved_by TEXT NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE sovereign_conflict_log IS 'SMS Conflict Resolution: Arbitration log when memories or agents contradict.';

ALTER TABLE sovereign_conflict_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_conflicts" ON sovereign_conflict_log
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_conflicts_created ON sovereign_conflict_log (created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE 6: sovereign_agent_registry
-- Universal registry of AI agents that can read/write to the SMS.
-- Supports: Manus, ChatGPT, Claude, Gemini, Grok, Cowork, any custom agent.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sovereign_agent_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    agent_type TEXT NOT NULL DEFAULT 'llm' CHECK (agent_type IN ('llm', 'human', 'system', 'tool')),
    provider TEXT NOT NULL DEFAULT 'manus' CHECK (provider IN ('manus', 'openai', 'anthropic', 'google', 'xai', 'custom')),
    model TEXT,
    permissions JSONB NOT NULL DEFAULT '{"read": true, "write": true, "crystallize": false, "forget": false}'::jsonb,
    last_active TIMESTAMPTZ NOT NULL DEFAULT now(),
    memory_count INTEGER NOT NULL DEFAULT 0,
    axiom_count INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_agent_id UNIQUE (agent_id)
);

COMMENT ON TABLE sovereign_agent_registry IS 'SMS Multi-Agent: Universal registry of AI agents. Any LLM/human can participate.';

ALTER TABLE sovereign_agent_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_agents" ON sovereign_agent_registry
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_agents_provider ON sovereign_agent_registry (provider);
CREATE INDEX IF NOT EXISTS idx_agents_active ON sovereign_agent_registry (is_active) WHERE is_active = true;

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE 7: sovereign_consolidation_log
-- REM Cycle execution history. Tracks nightly consolidation runs.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sovereign_consolidation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_type TEXT NOT NULL DEFAULT 'nightly' CHECK (run_type IN ('nightly', 'manual', 'emergency')),
    memories_processed INTEGER NOT NULL DEFAULT 0,
    memories_forgotten INTEGER NOT NULL DEFAULT 0,
    axioms_crystallized INTEGER NOT NULL DEFAULT 0,
    conflicts_resolved INTEGER NOT NULL DEFAULT 0,
    gaps_detected INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'completed' CHECK (status IN ('running', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE sovereign_consolidation_log IS 'SMS REM Cycle: Consolidation run history. Tracks nightly memory processing.';

ALTER TABLE sovereign_consolidation_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_consolidation" ON sovereign_consolidation_log
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_consolidation_created ON sovereign_consolidation_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_consolidation_status ON sovereign_consolidation_log (status);

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: match_sovereign_memories
-- Vector similarity search for memories with agent-scoped filtering.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION match_sovereign_memories(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INTEGER DEFAULT 10,
    filter_agent TEXT DEFAULT NULL,
    filter_type TEXT DEFAULT NULL,
    only_alive BOOLEAN DEFAULT true
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    memory_type TEXT,
    agent_id TEXT,
    confidence FLOAT,
    strength FLOAT,
    similarity FLOAT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sm.id,
        sm.content,
        sm.memory_type,
        sm.agent_id,
        sm.confidence,
        sm.strength,
        1 - (sm.embedding <=> query_embedding) AS similarity,
        sm.created_at
    FROM sovereign_memories sm
    WHERE
        sm.embedding IS NOT NULL
        AND (NOT only_alive OR sm.is_alive = true)
        AND (filter_agent IS NULL OR sm.agent_id = filter_agent)
        AND (filter_type IS NULL OR sm.memory_type = filter_type)
        AND 1 - (sm.embedding <=> query_embedding) > match_threshold
    ORDER BY sm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: match_sovereign_axioms
-- Vector similarity search for axioms (compaction-proof truths).
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION match_sovereign_axioms(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.6,
    match_count INTEGER DEFAULT 5,
    filter_agent TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    statement TEXT,
    confidence FLOAT,
    validation_count INTEGER,
    implications JSONB,
    similarity FLOAT,
    first_observed TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sa.id,
        sa.statement,
        sa.confidence,
        sa.validation_count,
        sa.implications,
        1 - (sa.embedding <=> query_embedding) AS similarity,
        sa.first_observed
    FROM sovereign_axioms sa
    WHERE
        sa.embedding IS NOT NULL
        AND sa.is_active = true
        AND (filter_agent IS NULL OR sa.source_agent = filter_agent)
        AND 1 - (sa.embedding <=> query_embedding) > match_threshold
    ORDER BY sa.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Seed default agents
-- ═══════════════════════════════════════════════════════════════════════════════
INSERT INTO sovereign_agent_registry (agent_id, agent_name, agent_type, provider, model, permissions) VALUES
    ('monstruo', 'El Monstruo (Orchestrator)', 'system', 'custom', NULL, '{"read": true, "write": true, "crystallize": true, "forget": true}'),
    ('manus_c', 'Manus C (Executor)', 'llm', 'manus', 'manus-agent', '{"read": true, "write": true, "crystallize": false, "forget": false}'),
    ('cowork_t2', 'Cowork T2 (Auditor)', 'llm', 'anthropic', 'claude-opus-4', '{"read": true, "write": true, "crystallize": false, "forget": false}'),
    ('chatgpt_sop', 'ChatGPT SOP (Brain)', 'llm', 'openai', 'gpt-5', '{"read": true, "write": true, "crystallize": false, "forget": false}'),
    ('gemini_sabio', 'Gemini (Sabio)', 'llm', 'google', 'gemini-2.5-pro', '{"read": true, "write": false, "crystallize": false, "forget": false}'),
    ('grok_sabio', 'Grok (Sabio)', 'llm', 'xai', 'grok-4', '{"read": true, "write": false, "crystallize": false, "forget": false}'),
    ('alfredo_t1', 'Alfredo (T1 Human)', 'human', 'custom', NULL, '{"read": true, "write": true, "crystallize": true, "forget": true}')
ON CONFLICT (agent_id) DO NOTHING;

COMMIT;
