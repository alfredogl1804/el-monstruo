-- Migration: 0054_knowledge_graph_layer.sql
-- SMS v4.0 — Knowledge Graph Layer
-- Purpose: Extract entities and relationships from memories to enable graph traversal,
--          multi-hop reasoning, and relational queries over the sovereign memory.
-- Architecture: POLE+O model (Person, Object, Location, Event + Organization)
--              implemented as lightweight tables over PostgreSQL (no Neo4j required).
-- Author: Manus C (SMS v4.0 — Knowledge Graph)
-- Date: 2026-05-21
--
-- Doctrina: RLS habilitado por defecto (DSC-S-006).

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE: memory_entities
-- Extracted entities from sovereign_memories. Each entity is a node in the graph.
-- Types follow POLE+O: Person, Object, Location, Event, Organization, Concept
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS memory_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL DEFAULT 'concept'
        CHECK (entity_type IN ('person', 'object', 'location', 'event', 'organization', 'concept', 'system', 'decision')),
    canonical_name TEXT NOT NULL,  -- Normalized lowercase for dedup (e.g., "el monstruo")
    description TEXT,
    embedding vector(1536),
    first_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
    mention_count INTEGER NOT NULL DEFAULT 1,
    confidence FLOAT NOT NULL DEFAULT 0.8,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_entity_canonical UNIQUE (canonical_name, entity_type)
);

COMMENT ON TABLE memory_entities IS 'SMS Knowledge Graph: Extracted entities (POLE+O model). Nodes in the memory graph.';

ALTER TABLE memory_entities ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_entities" ON memory_entities
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_entities_type ON memory_entities (entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_canonical ON memory_entities (canonical_name);
CREATE INDEX IF NOT EXISTS idx_entities_embedding ON memory_entities
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 30);
CREATE INDEX IF NOT EXISTS idx_entities_mentions ON memory_entities (mention_count DESC);
CREATE INDEX IF NOT EXISTS idx_entities_active ON memory_entities (is_active) WHERE is_active = true;

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE: memory_relations
-- Edges in the knowledge graph. Connect entities to entities OR entities to memories.
-- Typed relationships enable graph traversal queries.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS memory_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_entity_id UUID NOT NULL REFERENCES memory_entities(id) ON DELETE CASCADE,
    target_entity_id UUID NOT NULL REFERENCES memory_entities(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL DEFAULT 'related_to'
        CHECK (relation_type IN (
            'related_to', 'depends_on', 'created_by', 'part_of',
            'caused', 'preceded', 'succeeded', 'contradicts',
            'validates', 'implements', 'owns', 'uses', 'located_in'
        )),
    weight FLOAT NOT NULL DEFAULT 1.0 CHECK (weight >= 0 AND weight <= 1),
    evidence_memory_id UUID REFERENCES sovereign_memories(id) ON DELETE SET NULL,
    valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_until TIMESTAMPTZ,  -- NULL = still valid
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_relation UNIQUE (source_entity_id, target_entity_id, relation_type)
);

COMMENT ON TABLE memory_relations IS 'SMS Knowledge Graph: Typed edges between entities. Enables graph traversal and multi-hop reasoning.';

ALTER TABLE memory_relations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_relations" ON memory_relations
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_relations_source ON memory_relations (source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON memory_relations (target_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_type ON memory_relations (relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_evidence ON memory_relations (evidence_memory_id) WHERE evidence_memory_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_relations_valid ON memory_relations (valid_from, valid_until);

-- ═══════════════════════════════════════════════════════════════════════════════
-- TABLE: memory_entity_links
-- Junction table linking sovereign_memories to the entities they mention.
-- Enables: "given this memory, what entities does it reference?"
-- And: "given this entity, what memories mention it?"
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS memory_entity_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id UUID NOT NULL REFERENCES sovereign_memories(id) ON DELETE CASCADE,
    entity_id UUID NOT NULL REFERENCES memory_entities(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'mentions'
        CHECK (role IN ('mentions', 'subject', 'object', 'context', 'author')),
    confidence FLOAT NOT NULL DEFAULT 0.8,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_memory_entity_link UNIQUE (memory_id, entity_id, role)
);

COMMENT ON TABLE memory_entity_links IS 'SMS Knowledge Graph: Links memories to the entities they reference. Bidirectional navigation.';

ALTER TABLE memory_entity_links ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_entity_links" ON memory_entity_links
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_entity_links_memory ON memory_entity_links (memory_id);
CREATE INDEX IF NOT EXISTS idx_entity_links_entity ON memory_entity_links (entity_id);

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: get_entity_neighborhood
-- Given an entity, return its immediate neighbors (1-hop) with relationship info.
-- This is the core graph traversal primitive.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION get_entity_neighborhood(
    p_entity_id UUID,
    p_max_depth INTEGER DEFAULT 1,
    p_relation_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    entity_id UUID,
    entity_name TEXT,
    entity_type TEXT,
    relation_type TEXT,
    direction TEXT,
    weight FLOAT,
    depth INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    -- Outgoing relations
    SELECT
        mr.target_entity_id AS entity_id,
        me.name AS entity_name,
        me.entity_type,
        mr.relation_type,
        'outgoing'::TEXT AS direction,
        mr.weight,
        1 AS depth
    FROM memory_relations mr
    JOIN memory_entities me ON me.id = mr.target_entity_id
    WHERE mr.source_entity_id = p_entity_id
        AND me.is_active = true
        AND (mr.valid_until IS NULL OR mr.valid_until > now())
        AND (p_relation_filter IS NULL OR mr.relation_type = p_relation_filter)
    UNION ALL
    -- Incoming relations
    SELECT
        mr.source_entity_id AS entity_id,
        me.name AS entity_name,
        me.entity_type,
        mr.relation_type,
        'incoming'::TEXT AS direction,
        mr.weight,
        1 AS depth
    FROM memory_relations mr
    JOIN memory_entities me ON me.id = mr.source_entity_id
    WHERE mr.target_entity_id = p_entity_id
        AND me.is_active = true
        AND (mr.valid_until IS NULL OR mr.valid_until > now())
        AND (p_relation_filter IS NULL OR mr.relation_type = p_relation_filter)
    ORDER BY weight DESC;
END;
$$;

COMMENT ON FUNCTION get_entity_neighborhood IS
'Graph traversal: returns all entities connected to a given entity with relationship metadata. Core primitive for multi-hop reasoning.';

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: get_memories_for_entity
-- Given an entity, return all memories that reference it.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION get_memories_for_entity(
    p_entity_id UUID,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    memory_id UUID,
    content TEXT,
    memory_type TEXT,
    confidence FLOAT,
    strength FLOAT,
    role TEXT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        sm.id AS memory_id,
        sm.content,
        sm.memory_type,
        sm.confidence,
        sm.strength,
        mel.role,
        sm.created_at
    FROM memory_entity_links mel
    JOIN sovereign_memories sm ON sm.id = mel.memory_id
    WHERE mel.entity_id = p_entity_id
        AND sm.is_alive = true
    ORDER BY sm.created_at DESC
    LIMIT p_limit;
END;
$$;

COMMENT ON FUNCTION get_memories_for_entity IS
'Retrieve all alive memories that reference a specific entity. Enables entity-centric memory exploration.';

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: find_entity_by_name
-- Fuzzy entity lookup by canonical name (for entity resolution during ingest).
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION find_entity_by_name(
    p_name TEXT,
    p_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    entity_type TEXT,
    canonical_name TEXT,
    mention_count INTEGER,
    confidence FLOAT
)
LANGUAGE plpgsql
AS $$
DECLARE
    normalized TEXT;
BEGIN
    normalized := lower(trim(p_name));
    RETURN QUERY
    SELECT
        me.id,
        me.name,
        me.entity_type,
        me.canonical_name,
        me.mention_count,
        me.confidence
    FROM memory_entities me
    WHERE me.is_active = true
        AND (me.canonical_name = normalized OR me.canonical_name LIKE '%' || normalized || '%')
        AND (p_type IS NULL OR me.entity_type = p_type)
    ORDER BY
        CASE WHEN me.canonical_name = normalized THEN 0 ELSE 1 END,
        me.mention_count DESC
    LIMIT 10;
END;
$$;

COMMENT ON FUNCTION find_entity_by_name IS
'Fuzzy entity resolution by name. Used during ingest to link new memories to existing entities.';

-- ═══════════════════════════════════════════════════════════════════════════════
-- RPC: graph_enhanced_recall
-- Hybrid retrieval: vector similarity + graph expansion.
-- First finds memories by embedding similarity, then expands via entity graph.
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION graph_enhanced_recall(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.6,
    match_count INTEGER DEFAULT 10,
    graph_expansion BOOLEAN DEFAULT true
)
RETURNS TABLE (
    memory_id UUID,
    content TEXT,
    memory_type TEXT,
    confidence FLOAT,
    strength FLOAT,
    similarity FLOAT,
    source TEXT,  -- 'vector' or 'graph'
    related_entities JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Step 1: Direct vector matches
    RETURN QUERY
    SELECT
        sm.id AS memory_id,
        sm.content,
        sm.memory_type,
        sm.confidence,
        sm.strength,
        (1 - (sm.embedding <=> query_embedding))::FLOAT AS similarity,
        'vector'::TEXT AS source,
        COALESCE(
            (SELECT jsonb_agg(jsonb_build_object('name', me.name, 'type', me.entity_type))
             FROM memory_entity_links mel
             JOIN memory_entities me ON me.id = mel.entity_id
             WHERE mel.memory_id = sm.id),
            '[]'::jsonb
        ) AS related_entities
    FROM sovereign_memories sm
    WHERE sm.is_alive = true
        AND sm.embedding IS NOT NULL
        AND (1 - (sm.embedding <=> query_embedding)) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;

    -- Step 2: Graph expansion (memories connected to entities found in step 1)
    IF graph_expansion THEN
        RETURN QUERY
        SELECT DISTINCT
            sm2.id AS memory_id,
            sm2.content,
            sm2.memory_type,
            sm2.confidence,
            sm2.strength,
            0.0::FLOAT AS similarity,  -- Not from vector match
            'graph'::TEXT AS source,
            COALESCE(
                (SELECT jsonb_agg(jsonb_build_object('name', me2.name, 'type', me2.entity_type))
                 FROM memory_entity_links mel2
                 JOIN memory_entities me2 ON me2.id = mel2.entity_id
                 WHERE mel2.memory_id = sm2.id),
                '[]'::jsonb
            ) AS related_entities
        FROM sovereign_memories sm
        JOIN memory_entity_links mel ON mel.memory_id = sm.id
        JOIN memory_entity_links mel_linked ON mel_linked.entity_id = mel.entity_id
        JOIN sovereign_memories sm2 ON sm2.id = mel_linked.memory_id
        WHERE sm.is_alive = true
            AND sm2.is_alive = true
            AND sm.embedding IS NOT NULL
            AND (1 - (sm.embedding <=> query_embedding)) > match_threshold
            AND sm2.id != sm.id
        ORDER BY sm2.strength DESC
        LIMIT match_count;
    END IF;
END;
$$;

COMMENT ON FUNCTION graph_enhanced_recall IS
'Hybrid retrieval: vector similarity + 1-hop graph expansion via shared entities. Returns both direct matches and graph-connected memories.';

COMMIT;
