-- Migration: 0055_belief_revision.sql
-- SMS v4.0 — Belief Revision (AGM-Inspired Cascading Invalidation)
-- Purpose: When a memory is invalidated or contradicted, propagate the invalidation
--          to all memories that logically depend on it. Prevents "drift silencioso"
--          where downstream beliefs remain active after their premise is disproven.
-- Theory: Inspired by AGM (Alchourrón, Gärdenfors, Makinson) belief revision semantics.
-- Author: Manus C (SMS v4.0 — Belief Revision)
-- Date: 2026-05-21
--
-- Doctrina: RLS habilitado por defecto (DSC-S-006).

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE: memory_dependencies
-- Explicit dependency graph between memories. "Memory B depends on Memory A"
-- means if A is invalidated, B needs revalidation.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS memory_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    premise_id UUID NOT NULL REFERENCES sovereign_memories(id) ON DELETE CASCADE,
    dependent_id UUID NOT NULL REFERENCES sovereign_memories(id) ON DELETE CASCADE,
    dependency_type TEXT NOT NULL DEFAULT 'logical'
        CHECK (dependency_type IN ('logical', 'temporal', 'causal', 'evidential')),
    strength FLOAT NOT NULL DEFAULT 1.0 CHECK (strength >= 0 AND strength <= 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_dependency UNIQUE (premise_id, dependent_id),
    CONSTRAINT no_self_dependency CHECK (premise_id != dependent_id)
);

COMMENT ON TABLE memory_dependencies IS 'SMS Belief Revision: Dependency graph. If premise is invalidated, dependent needs revalidation.';

ALTER TABLE memory_dependencies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_dependencies" ON memory_dependencies
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_deps_premise ON memory_dependencies (premise_id);
CREATE INDEX IF NOT EXISTS idx_deps_dependent ON memory_dependencies (dependent_id);
CREATE INDEX IF NOT EXISTS idx_deps_type ON memory_dependencies (dependency_type);

-- ═══════════════════════════════════════════════════════════════════════════════
-- Add revalidation status column to sovereign_memories
-- ═══════════════════════════════════════════════════════════════════════════════
ALTER TABLE sovereign_memories
ADD COLUMN IF NOT EXISTS revalidation_status TEXT DEFAULT 'valid'
    CHECK (revalidation_status IN ('valid', 'needs_revalidation', 'invalidated', 'revalidated'));

ALTER TABLE sovereign_memories
ADD COLUMN IF NOT EXISTS invalidation_reason TEXT;

ALTER TABLE sovereign_memories
ADD COLUMN IF NOT EXISTS invalidated_by UUID REFERENCES sovereign_memories(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_memories_revalidation
ON sovereign_memories (revalidation_status)
WHERE revalidation_status != 'valid';

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE: belief_revision_log
-- Audit trail for every belief revision cascade event.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS belief_revision_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger_memory_id UUID NOT NULL,
    trigger_action TEXT NOT NULL CHECK (trigger_action IN ('invalidated', 'contradicted', 'superseded', 'decayed')),
    affected_memories UUID[] NOT NULL DEFAULT '{}',
    affected_count INTEGER NOT NULL DEFAULT 0,
    cascade_depth INTEGER NOT NULL DEFAULT 0,
    revision_strategy TEXT NOT NULL DEFAULT 'mark_for_revalidation'
        CHECK (revision_strategy IN ('mark_for_revalidation', 'auto_invalidate', 'reduce_confidence')),
    agent_id TEXT NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE belief_revision_log IS 'SMS Belief Revision: Audit trail of cascading invalidations. Tracks what triggered what.';

ALTER TABLE belief_revision_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_revision_log" ON belief_revision_log
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_revision_log_trigger ON belief_revision_log (trigger_memory_id);
CREATE INDEX IF NOT EXISTS idx_revision_log_created ON belief_revision_log (created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: cascade_invalidation
-- Core belief revision function. When a memory is invalidated:
-- 1. Marks it as invalidated
-- 2. Finds all dependents (recursively up to max_depth)
-- 3. Marks dependents as needs_revalidation
-- 4. Logs the cascade event
-- Returns the count of affected memories.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION cascade_invalidation(
    p_memory_id UUID,
    p_reason TEXT DEFAULT 'contradicted by newer evidence',
    p_agent_id TEXT DEFAULT 'system',
    p_strategy TEXT DEFAULT 'mark_for_revalidation',
    p_max_depth INTEGER DEFAULT 5
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    affected UUID[];
    current_level UUID[];
    next_level UUID[];
    depth INTEGER := 0;
    total_affected INTEGER := 0;
    mem_id UUID;
BEGIN
    -- Step 1: Invalidate the trigger memory
    UPDATE sovereign_memories
    SET revalidation_status = 'invalidated',
        invalidation_reason = p_reason,
        invalid_at = now(),
        is_alive = CASE WHEN p_strategy = 'auto_invalidate' THEN false ELSE is_alive END,
        updated_at = now()
    WHERE id = p_memory_id;

    -- Step 2: BFS traversal of dependency graph
    current_level := ARRAY[p_memory_id];
    affected := ARRAY[]::UUID[];

    WHILE depth < p_max_depth AND array_length(current_level, 1) > 0 LOOP
        depth := depth + 1;
        next_level := ARRAY[]::UUID[];

        -- Find all dependents of current level
        FOR mem_id IN
            SELECT md.dependent_id
            FROM memory_dependencies md
            WHERE md.premise_id = ANY(current_level)
              AND md.dependent_id != ALL(affected)  -- Avoid cycles
              AND md.dependent_id != p_memory_id
        LOOP
            next_level := array_append(next_level, mem_id);
            affected := array_append(affected, mem_id);

            -- Apply strategy to dependent
            IF p_strategy = 'mark_for_revalidation' THEN
                UPDATE sovereign_memories
                SET revalidation_status = 'needs_revalidation',
                    invalidated_by = p_memory_id,
                    updated_at = now()
                WHERE id = mem_id AND revalidation_status = 'valid';
            ELSIF p_strategy = 'auto_invalidate' THEN
                UPDATE sovereign_memories
                SET revalidation_status = 'invalidated',
                    invalidation_reason = 'cascade from ' || p_memory_id::TEXT,
                    invalid_at = now(),
                    is_alive = false,
                    updated_at = now()
                WHERE id = mem_id;
            ELSIF p_strategy = 'reduce_confidence' THEN
                UPDATE sovereign_memories
                SET confidence = GREATEST(confidence * 0.5, 0.1),
                    revalidation_status = 'needs_revalidation',
                    invalidated_by = p_memory_id,
                    updated_at = now()
                WHERE id = mem_id;
            END IF;
        END LOOP;

        current_level := next_level;
    END LOOP;

    total_affected := COALESCE(array_length(affected, 1), 0);

    -- Step 3: Log the cascade
    INSERT INTO belief_revision_log (
        trigger_memory_id, trigger_action, affected_memories,
        affected_count, cascade_depth, revision_strategy, agent_id
    ) VALUES (
        p_memory_id, 'invalidated', affected,
        total_affected, depth, p_strategy, p_agent_id
    );

    RETURN jsonb_build_object(
        'trigger_id', p_memory_id,
        'affected_count', total_affected,
        'cascade_depth', depth,
        'strategy', p_strategy,
        'affected_ids', to_jsonb(affected)
    );
END;
$$;

COMMENT ON FUNCTION cascade_invalidation IS
'AGM-inspired belief revision: invalidates a memory and cascades to all dependents via BFS. Supports mark_for_revalidation, auto_invalidate, and reduce_confidence strategies.';

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: get_pending_revalidations
-- Returns memories that need revalidation (for REM Cycle to process).
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION get_pending_revalidations(
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    memory_type TEXT,
    confidence FLOAT,
    revalidation_status TEXT,
    invalidated_by UUID,
    invalidation_reason TEXT,
    premise_content TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sm.id,
        sm.content,
        sm.memory_type,
        sm.confidence,
        sm.revalidation_status,
        sm.invalidated_by,
        sm.invalidation_reason,
        premise.content AS premise_content
    FROM sovereign_memories sm
    LEFT JOIN sovereign_memories premise ON premise.id = sm.invalidated_by
    WHERE sm.revalidation_status = 'needs_revalidation'
        AND sm.is_alive = true
    ORDER BY sm.confidence DESC
    LIMIT p_limit;
END;
$$;

COMMENT ON FUNCTION get_pending_revalidations IS
'Returns memories pending revalidation after a belief revision cascade. Used by REM Cycle.';

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: register_dependency
-- Helper to register a dependency between two memories.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION register_dependency(
    p_premise_id UUID,
    p_dependent_id UUID,
    p_type TEXT DEFAULT 'logical',
    p_strength FLOAT DEFAULT 1.0
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    dep_id UUID;
BEGIN
    INSERT INTO memory_dependencies (premise_id, dependent_id, dependency_type, strength)
    VALUES (p_premise_id, p_dependent_id, p_type, p_strength)
    ON CONFLICT (premise_id, dependent_id) DO UPDATE
        SET strength = EXCLUDED.strength,
            dependency_type = EXCLUDED.dependency_type
    RETURNING id INTO dep_id;

    RETURN dep_id;
END;
$$;

COMMENT ON FUNCTION register_dependency IS
'Register a logical dependency between two memories. Used during ingest when a new memory references an existing one.';

COMMIT;
