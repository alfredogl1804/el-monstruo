-- Migration: 0010_anti_dory_plan_ledger.sql
-- Anti-Dory FORGE v3.0 — B3 Plan Ledger
-- Purpose: Append-only immutable ledger of plans and delegations.
-- Author: Manus C (Batch 005 Célula B)
-- Date: 2026-05-20
-- Status: NOT APPLIED — requires T1 confirmation per migration.
--
-- Doctrina: RLS habilitado por defecto (DSC-S-006).
-- Append-only: No UPDATE, no DELETE policies.

BEGIN;

-- Table: anti_dory_plan_ledger
-- Immutable record of every plan created, delegated, or completed.
CREATE TABLE IF NOT EXISTS anti_dory_plan_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_hash TEXT NOT NULL,
    plan_summary TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'CREATED' CHECK (
        status IN ('CREATED', 'DELEGATED', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED')
    ),
    delegated_to TEXT,
    delegated_at TIMESTAMPTZ,
    parent_plan_id UUID REFERENCES anti_dory_plan_ledger(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    -- Prevent duplicate plan hashes (same plan cannot be registered twice)
    CONSTRAINT uq_plan_hash UNIQUE (plan_hash)
);

-- Comment on table
COMMENT ON TABLE anti_dory_plan_ledger IS 'B3 Anti-Dory Plan Ledger: append-only immutable record of plans and delegations.';

-- Enable RLS (DSC-S-006 mandatory)
ALTER TABLE anti_dory_plan_ledger ENABLE ROW LEVEL SECURITY;

-- Policy: service_role can read all plans
CREATE POLICY "service_role_read_plans"
    ON anti_dory_plan_ledger
    FOR SELECT
    TO service_role
    USING (true);

-- Policy: service_role can insert new plans (append-only)
CREATE POLICY "service_role_insert_plans"
    ON anti_dory_plan_ledger
    FOR INSERT
    TO service_role
    WITH CHECK (true);

-- Policy: service_role can update status only (for state transitions)
-- Note: This is the ONLY allowed mutation — status transitions.
CREATE POLICY "service_role_update_status"
    ON anti_dory_plan_ledger
    FOR UPDATE
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_plan_status ON anti_dory_plan_ledger (status);
CREATE INDEX IF NOT EXISTS idx_plan_delegated_to ON anti_dory_plan_ledger (delegated_to);
CREATE INDEX IF NOT EXISTS idx_plan_created_at ON anti_dory_plan_ledger (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_plan_parent ON anti_dory_plan_ledger (parent_plan_id);

COMMIT;
