-- =============================================================================
-- Migration 0031 — project_runtime_heads (Anti-Dory punteros canónicos)
-- =============================================================================
-- Sprint: MANUS-ANTI-DORY-002 v1, FASE B.1
-- Doctrina: SPEC §A.3 (Schema SQL), §A.4 (RPCs), §A.5 (Context Broker)
-- Origen: GPT-5.5 Pro audit + Opus 4.7 convergencia + Cowork T2-A APPROVED
--
-- Propósito: Puntero canónico (head) que apunta al snapshot accepted vigente
--   para cada combinación (project_id, front_id). Es el primer recurso que
--   consulta el Context Broker al recibir un task.create.
--
-- Concurrencia: compare-and-swap vía lock_version (optimistic locking).
--   Cualquier UPDATE de head_snapshot_id debe pasar p_expected_lock_version.
--   Si difiere → conflict (otro writer escribió antes) → falla duro, no merge.
--
-- RLS: DSC-S-006 v1.1.
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS public.project_runtime_heads (
    project_id        TEXT         NOT NULL,
    front_id          TEXT         NOT NULL,
    head_snapshot_id  UUID         NOT NULL,
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    lock_version      INTEGER      NOT NULL DEFAULT 1,
    PRIMARY KEY (project_id, front_id),
    CONSTRAINT project_runtime_heads_lock_version_positive CHECK (
        lock_version > 0
    ),
    CONSTRAINT project_runtime_heads_project_id_nonempty CHECK (
        char_length(project_id) > 0
    ),
    CONSTRAINT project_runtime_heads_front_id_nonempty CHECK (
        char_length(front_id) > 0
    ),
    CONSTRAINT project_runtime_heads_snapshot_fk
        FOREIGN KEY (head_snapshot_id)
        REFERENCES public.thread_snapshots(snapshot_id)
);

COMMENT ON TABLE public.project_runtime_heads IS
'Puntero canónico (head) al snapshot accepted vigente por (project_id, front_id). '
'Primer recurso consultado por Context Broker en rpc_get_context_head. '
'Concurrencia: compare-and-swap vía lock_version. '
'Sprint MANUS-ANTI-DORY-002 v1 FASE B.1. SPEC §A.3+§A.4+§A.5. Cowork T2-A GREEN.';

COMMENT ON COLUMN public.project_runtime_heads.lock_version IS
'Optimistic locking. Cualquier UPDATE debe pasar p_expected_lock_version igual al actual. '
'Si difiere → conflict (otro writer ganó la carrera) → falla duro, NO merge automático.';

COMMENT ON COLUMN public.project_runtime_heads.head_snapshot_id IS
'FK a thread_snapshots. Solo apunta a snapshots con status=accepted (enforcement a nivel RPC).';

-- Índice de soporte para queries por snapshot.
CREATE INDEX IF NOT EXISTS idx_project_runtime_heads_snapshot
    ON public.project_runtime_heads (head_snapshot_id);

CREATE INDEX IF NOT EXISTS idx_project_runtime_heads_updated
    ON public.project_runtime_heads (updated_at DESC);

-- =============================================================================
-- RLS por defecto (DSC-S-006 v1.1)
-- =============================================================================

ALTER TABLE public.project_runtime_heads ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS project_runtime_heads_service_role_only ON public.project_runtime_heads;
CREATE POLICY project_runtime_heads_service_role_only
    ON public.project_runtime_heads
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

REVOKE ALL ON public.project_runtime_heads FROM PUBLIC;
REVOKE ALL ON public.project_runtime_heads FROM anon;
REVOKE ALL ON public.project_runtime_heads FROM authenticated;
GRANT SELECT, INSERT, UPDATE ON public.project_runtime_heads TO service_role;
-- DELETE NO autorizado por diseño. Si un frente se cierra, se marca via
-- snapshot de cierre (status=accepted con next_expected_action='ARCHIVED'),
-- no se borra el puntero.

-- =============================================================================
-- Verificación automática post-apply
-- =============================================================================

DO $$
DECLARE
    v_rls_enabled  BOOLEAN;
    v_policy_count INTEGER;
BEGIN
    SELECT relrowsecurity INTO v_rls_enabled
    FROM pg_class
    WHERE relname = 'project_runtime_heads' AND relnamespace = 'public'::regnamespace;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: project_runtime_heads creada sin RLS habilitado';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'project_runtime_heads';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: project_runtime_heads sin policies explícitas';
    END IF;

    RAISE NOTICE 'project_runtime_heads creada OK: RLS=%, policies=%', v_rls_enabled, v_policy_count;
END $$;

COMMIT;
