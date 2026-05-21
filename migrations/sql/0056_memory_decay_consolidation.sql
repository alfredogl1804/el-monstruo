-- Migration: 0056_memory_decay_consolidation.sql
-- SMS v4.0 — Memory Decay + Consolidation (Importance Scoring & Archival)
-- Purpose: Implement dynamic importance scoring that combines recency, frequency,
--          graph connectivity, and confidence. Memories below threshold are archived
--          (not deleted), keeping retrieval quality constant as the corpus grows.
-- Author: Manus C (SMS v4.0 — Decay & Consolidation)
-- Date: 2026-05-21
--
-- Doctrina: RLS habilitado por defecto (DSC-S-006).

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Add importance_score and archival columns to sovereign_memories
-- ═══════════════════════════════════════════════════════════════════════════════
ALTER TABLE sovereign_memories
ADD COLUMN IF NOT EXISTS importance_score FLOAT DEFAULT 1.0;

ALTER TABLE sovereign_memories
ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT false;

ALTER TABLE sovereign_memories
ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;

ALTER TABLE sovereign_memories
ADD COLUMN IF NOT EXISTS archive_reason TEXT;

ALTER TABLE sovereign_memories
ADD COLUMN IF NOT EXISTS merged_into_id UUID REFERENCES sovereign_memories(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_memories_importance
ON sovereign_memories (importance_score DESC)
WHERE is_alive = true AND is_archived = false;

CREATE INDEX IF NOT EXISTS idx_memories_archived
ON sovereign_memories (is_archived)
WHERE is_archived = true;

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE: memory_access_log
-- Track every time a memory is retrieved (for frequency-based scoring).
-- Lightweight append-only log.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS memory_access_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES sovereign_memories(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL DEFAULT 'system',
    access_type TEXT NOT NULL DEFAULT 'recall'
        CHECK (access_type IN ('recall', 'injection', 'revalidation', 'consolidation')),
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE memory_access_log IS 'SMS Decay: Tracks memory access patterns for importance scoring. Append-only.';

ALTER TABLE memory_access_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_access_log" ON memory_access_log
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_access_log_memory ON memory_access_log (memory_id);
CREATE INDEX IF NOT EXISTS idx_access_log_time ON memory_access_log (accessed_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE: memory_merge_log
-- Tracks when redundant memories are merged into a consolidated one.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS memory_merge_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_memory_ids UUID[] NOT NULL,
    target_memory_id UUID NOT NULL REFERENCES sovereign_memories(id) ON DELETE CASCADE,
    merge_reason TEXT NOT NULL DEFAULT 'semantic_dedup',
    similarity_score FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE memory_merge_log IS 'SMS Consolidation: Tracks memory merges during deduplication. Audit trail for merged memories.';

ALTER TABLE memory_merge_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_merge_log" ON memory_merge_log
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_merge_log_target ON memory_merge_log (target_memory_id);

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: compute_importance_scores
-- Recalculates importance_score for all alive memories.
-- Formula: importance = w1*recency + w2*frequency + w3*connectivity + w4*confidence
-- Where:
--   recency = 1 / (1 + days_since_last_access / 30)
--   frequency = min(access_count / 10, 1.0)
--   connectivity = min(entity_link_count / 5, 1.0)
--   confidence = memory.confidence
-- Weights: recency=0.25, frequency=0.25, connectivity=0.25, confidence=0.25
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION compute_importance_scores(
    p_batch_size INTEGER DEFAULT 500
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    updated_count INTEGER := 0;
    rec RECORD;
    recency_score FLOAT;
    frequency_score FLOAT;
    connectivity_score FLOAT;
    new_importance FLOAT;
    days_since FLOAT;
    link_count INTEGER;
BEGIN
    FOR rec IN
        SELECT
            sm.id,
            sm.confidence,
            sm.access_count,
            sm.last_accessed,
            sm.created_at
        FROM sovereign_memories sm
        WHERE sm.is_alive = true
          AND sm.is_archived = false
        ORDER BY sm.last_accessed ASC NULLS FIRST
        LIMIT p_batch_size
    LOOP
        -- Recency: exponential decay based on days since last access
        days_since := EXTRACT(EPOCH FROM (now() - COALESCE(rec.last_accessed, rec.created_at))) / 86400.0;
        recency_score := 1.0 / (1.0 + days_since / 30.0);

        -- Frequency: normalized access count (cap at 10 accesses = max score)
        frequency_score := LEAST(COALESCE(rec.access_count, 0)::FLOAT / 10.0, 1.0);

        -- Connectivity: how many entities link to this memory
        SELECT COUNT(*) INTO link_count
        FROM memory_entity_links mel
        WHERE mel.memory_id = rec.id;
        connectivity_score := LEAST(link_count::FLOAT / 5.0, 1.0);

        -- Weighted combination
        new_importance := (
            0.25 * recency_score +
            0.25 * frequency_score +
            0.25 * connectivity_score +
            0.25 * COALESCE(rec.confidence, 0.5)
        );

        -- Update
        UPDATE sovereign_memories
        SET importance_score = ROUND(new_importance::NUMERIC, 4)::FLOAT
        WHERE id = rec.id;

        updated_count := updated_count + 1;
    END LOOP;

    RETURN jsonb_build_object(
        'updated_count', updated_count,
        'batch_size', p_batch_size
    );
END;
$$;

COMMENT ON FUNCTION compute_importance_scores IS
'Recalculates importance_score for memories using weighted formula: recency + frequency + connectivity + confidence. Called by REM Cycle.';

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: archive_low_importance_memories
-- Archives memories below a threshold. They remain in DB but excluded from recall.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION archive_low_importance_memories(
    p_threshold FLOAT DEFAULT 0.15,
    p_min_age_days INTEGER DEFAULT 30,
    p_max_archive INTEGER DEFAULT 100
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    archived_count INTEGER;
    now_ts TIMESTAMPTZ := now();
BEGIN
    WITH to_archive AS (
        SELECT id
        FROM sovereign_memories
        WHERE is_alive = true
          AND is_archived = false
          AND importance_score < p_threshold
          AND layer < 4  -- Never archive Layer 4 (sovereign) or Layer 5 (metacognition)
          AND memory_type != 'procedural'  -- Never archive procedural memories
          AND revalidation_status = 'valid'  -- Don't archive things pending review
          AND created_at < now_ts - (p_min_age_days || ' days')::INTERVAL
        ORDER BY importance_score ASC
        LIMIT p_max_archive
    )
    UPDATE sovereign_memories sm
    SET is_archived = true,
        archived_at = now_ts,
        archive_reason = 'low_importance_score (' || ROUND(sm.importance_score::NUMERIC, 3) || ')',
        updated_at = now_ts
    FROM to_archive
    WHERE sm.id = to_archive.id;

    GET DIAGNOSTICS archived_count = ROW_COUNT;

    RETURN jsonb_build_object(
        'archived_count', archived_count,
        'threshold', p_threshold,
        'min_age_days', p_min_age_days
    );
END;
$$;

COMMENT ON FUNCTION archive_low_importance_memories IS
'Archives memories with importance_score below threshold. Preserves data but excludes from recall. Never archives Layer 4+, procedural, or pending-review memories.';

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: merge_similar_memories
-- Finds semantically similar memories and merges them into one consolidated memory.
-- The merged memory inherits the highest confidence and combined access count.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION merge_similar_memories(
    p_similarity_threshold FLOAT DEFAULT 0.95,
    p_max_merges INTEGER DEFAULT 20
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    merge_count INTEGER := 0;
    rec RECORD;
    similar_rec RECORD;
    merged_ids UUID[];
BEGIN
    -- Find pairs of very similar memories
    FOR rec IN
        SELECT
            sm1.id AS id1,
            sm2.id AS id2,
            sm1.content AS content1,
            sm2.content AS content2,
            sm1.confidence AS conf1,
            sm2.confidence AS conf2,
            sm1.access_count AS ac1,
            sm2.access_count AS ac2,
            (1 - (sm1.embedding <=> sm2.embedding))::FLOAT AS sim
        FROM sovereign_memories sm1
        JOIN sovereign_memories sm2 ON sm1.id < sm2.id  -- Avoid duplicates
        WHERE sm1.is_alive = true
          AND sm2.is_alive = true
          AND sm1.is_archived = false
          AND sm2.is_archived = false
          AND sm1.embedding IS NOT NULL
          AND sm2.embedding IS NOT NULL
          AND (1 - (sm1.embedding <=> sm2.embedding)) > p_similarity_threshold
        ORDER BY sim DESC
        LIMIT p_max_merges
    LOOP
        -- Keep the one with higher confidence (or older if tied)
        IF rec.conf1 >= rec.conf2 THEN
            -- Keep id1, archive id2
            UPDATE sovereign_memories
            SET is_archived = true,
                archived_at = now(),
                archive_reason = 'merged_duplicate (sim=' || ROUND(rec.sim::NUMERIC, 3) || ')',
                merged_into_id = rec.id1,
                updated_at = now()
            WHERE id = rec.id2;

            -- Boost survivor
            UPDATE sovereign_memories
            SET access_count = access_count + rec.ac2,
                validation_count = validation_count + 1,
                updated_at = now()
            WHERE id = rec.id1;
        ELSE
            -- Keep id2, archive id1
            UPDATE sovereign_memories
            SET is_archived = true,
                archived_at = now(),
                archive_reason = 'merged_duplicate (sim=' || ROUND(rec.sim::NUMERIC, 3) || ')',
                merged_into_id = rec.id2,
                updated_at = now()
            WHERE id = rec.id1;

            UPDATE sovereign_memories
            SET access_count = access_count + rec.ac1,
                validation_count = validation_count + 1,
                updated_at = now()
            WHERE id = rec.id2;
        END IF;

        -- Log the merge
        INSERT INTO memory_merge_log (source_memory_ids, target_memory_id, merge_reason, similarity_score)
        VALUES (
            ARRAY[rec.id1, rec.id2],
            CASE WHEN rec.conf1 >= rec.conf2 THEN rec.id1 ELSE rec.id2 END,
            'semantic_dedup',
            rec.sim
        );

        merge_count := merge_count + 1;
    END LOOP;

    RETURN jsonb_build_object(
        'merges_performed', merge_count,
        'similarity_threshold', p_similarity_threshold
    );
END;
$$;

COMMENT ON FUNCTION merge_similar_memories IS
'Finds and merges semantically duplicate memories. Keeps highest-confidence version, archives the other. Logs all merges.';

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: deduplicate_sovereign_memories (replaces the missing one from REM cycle)
-- Wrapper that the existing REM cycle step_3 already calls.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION deduplicate_sovereign_memories(
    similarity_threshold FLOAT DEFAULT 0.95
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN merge_similar_memories(similarity_threshold, 20);
END;
$$;

COMMENT ON FUNCTION deduplicate_sovereign_memories IS
'Wrapper for merge_similar_memories. Called by existing REM Cycle step_3_deduplicate.';

-- ═══════════════════════════════════════════════════════════════════════════════
-- Update match_sovereign_memories to exclude archived memories
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
        (1 - (sm.embedding <=> query_embedding))::FLOAT AS similarity,
        sm.created_at
    FROM sovereign_memories sm
    WHERE
        sm.embedding IS NOT NULL
        AND (NOT only_alive OR sm.is_alive = true)
        AND sm.is_archived = false  -- NEW: exclude archived
        AND (filter_agent IS NULL OR sm.agent_id = filter_agent)
        AND (filter_type IS NULL OR sm.memory_type = filter_type)
        AND (1 - (sm.embedding <=> query_embedding))::FLOAT > match_threshold
    ORDER BY sm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

COMMIT;
