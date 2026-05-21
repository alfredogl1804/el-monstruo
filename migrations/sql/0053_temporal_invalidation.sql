-- Migration 0053: Temporal Invalidation for Sovereign Memory System
-- Adds valid_at/invalid_at columns to enable point-in-time memory queries
-- "What did the system know on Tuesday?" becomes answerable
-- Author: Manus C (SMS v3.1 — Temporal Invalidation)
-- Date: 2026-05-21

-- Add temporal columns to sovereign_memories
ALTER TABLE sovereign_memories
ADD COLUMN IF NOT EXISTS valid_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS invalid_at TIMESTAMPTZ DEFAULT NULL;

-- Add temporal columns to sovereign_axioms
ALTER TABLE sovereign_axioms
ADD COLUMN IF NOT EXISTS valid_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS invalid_at TIMESTAMPTZ DEFAULT NULL;

-- Index for temporal queries (point-in-time lookups)
CREATE INDEX IF NOT EXISTS idx_sovereign_memories_temporal
ON sovereign_memories (valid_at, invalid_at)
WHERE is_alive = true;

CREATE INDEX IF NOT EXISTS idx_sovereign_axioms_temporal
ON sovereign_axioms (valid_at, invalid_at)
WHERE is_active = true;

-- RPC: search memories valid at a specific point in time
CREATE OR REPLACE FUNCTION match_sovereign_memories_temporal(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 10,
    point_in_time TIMESTAMPTZ DEFAULT NOW(),
    filter_agent text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    content text,
    memory_type text,
    agent_id text,
    confidence float,
    strength float,
    tags text[],
    valid_at TIMESTAMPTZ,
    invalid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    similarity float
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
        sm.confidence::float,
        sm.strength::float,
        sm.tags,
        sm.valid_at,
        sm.invalid_at,
        sm.created_at,
        (1 - (sm.embedding <=> query_embedding))::float AS similarity
    FROM sovereign_memories sm
    WHERE sm.is_alive = true
        AND sm.embedding IS NOT NULL
        AND (1 - (sm.embedding <=> query_embedding)) > match_threshold
        AND sm.valid_at <= point_in_time
        AND (sm.invalid_at IS NULL OR sm.invalid_at > point_in_time)
        AND (filter_agent IS NULL OR sm.agent_id = filter_agent)
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION match_sovereign_memories_temporal IS
'Semantic search over memories valid at a specific point in time. Enables temporal queries like "what did the system know last Tuesday?"';
