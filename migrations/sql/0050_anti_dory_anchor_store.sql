-- Migration: 0009_anti_dory_anchor_store.sql
-- Anti-Dory FORGE v3.0 — B1 Anchor Store
-- Purpose: Immutable doctrine store for Anti-Dory system.
-- Author: Manus C (Batch 005 Célula A)
-- Date: 2026-05-20
-- Status: NOT APPLIED — requires T1 confirmation per migration.
--
-- Doctrina: RLS habilitado por defecto (DSC-S-006).
-- Naming: SUPABASE_SERVICE_KEY (DSC-S-007).

BEGIN;

-- Table: anti_dory_anchor_store
-- Stores immutable doctrinal anchors that define the system's core truths.
-- Once inserted, rows should NEVER be updated or deleted (append-only semantics enforced by policy).
CREATE TABLE IF NOT EXISTS anti_dory_anchor_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept TEXT NOT NULL,
    definition TEXT NOT NULL,
    canon_source TEXT,
    canon_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    t1_signature TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Prevent accidental duplicates
    CONSTRAINT uq_anchor_concept UNIQUE (concept)
);

-- Comment on table
COMMENT ON TABLE anti_dory_anchor_store IS 'B1 Anti-Dory Anchor Store: immutable doctrine registry. Append-only.';

-- Enable RLS (DSC-S-006 mandatory)
ALTER TABLE anti_dory_anchor_store ENABLE ROW LEVEL SECURITY;

-- Policy: service_role can read all anchors
CREATE POLICY "service_role_read_anchors"
    ON anti_dory_anchor_store
    FOR SELECT
    TO service_role
    USING (true);

-- Policy: service_role can insert (append-only, no update/delete)
CREATE POLICY "service_role_insert_anchors"
    ON anti_dory_anchor_store
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- Explicitly deny update and delete for all roles
-- (No UPDATE or DELETE policies means they are denied by default with RLS enabled)

-- Index for fast concept lookup
CREATE INDEX IF NOT EXISTS idx_anchor_concept ON anti_dory_anchor_store (concept);

-- Index for temporal queries
CREATE INDEX IF NOT EXISTS idx_anchor_canon_date ON anti_dory_anchor_store (canon_date DESC);

COMMIT;
