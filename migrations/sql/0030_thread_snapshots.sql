-- =============================================================================
-- Migration 0030 — thread_snapshots (Anti-Dory snapshots versionados con hash)
-- =============================================================================
-- Sprint: MANUS-ANTI-DORY-002 v1, FASE B.1
-- Doctrina: SPEC §A.3 (Schema SQL), §A.10 (Contrato ATTACHMENT_OK)
-- Origen: GPT-5.5 Pro audit + Opus 4.7 convergencia + Cowork T2-A APPROVED
--
-- Propósito: Snapshots versionados (con parent_snapshot_id) que materializan
--   el estado operativo recuperable para un (project_id, front_id) dado.
--   Estos son los registros que el Context Broker lee en rpc_get_context_head
--   y serializa al contrato ATTACHMENT_OK que se inyecta al prompt antes de
--   que el agente Manus razone.
--
-- Diferencias clave vs runtime_events:
--   - thread_snapshots es estado materializado, NO append log.
--   - state_hash permite integridad / detección de tampering.
--   - parent_snapshot_id crea cadena de versiones (DAG, no árbol estricto).
--   - do_not_touch es campo explícito (regla T1 dura) para prevenir que el
--     agente recuperado rompa artefactos protegidos (PR #118, Mac, secrets).
--   - confidence_score numérico [0.0-1.0] para Recovery Mode.
--   - status canonizado: pending | accepted | superseded | rejected.
--
-- RLS: DSC-S-006 v1.1.
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS public.thread_snapshots (
    snapshot_id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    project_id           TEXT         NOT NULL,
    front_id             TEXT         NOT NULL,
    actor_type           TEXT         NOT NULL,
    parent_snapshot_id   UUID,
    state_hash           TEXT         NOT NULL,
    sprint_id            TEXT,
    phase                TEXT,
    last_t1_decision     TEXT,
    next_expected_action TEXT,
    do_not_touch         JSONB        NOT NULL DEFAULT '[]'::jsonb,
    evidence_refs        JSONB        NOT NULL DEFAULT '[]'::jsonb,
    confidence_score     NUMERIC(3,2) NOT NULL DEFAULT 1.00,
    status               TEXT         NOT NULL DEFAULT 'pending',
    writer_mode          TEXT         NOT NULL DEFAULT 'explicit',
    summary              TEXT,
    CONSTRAINT thread_snapshots_actor_type_valid CHECK (
        actor_type IN ('manus', 'cowork', 'embrion', 'system')
    ),
    CONSTRAINT thread_snapshots_status_valid CHECK (
        status IN ('pending', 'accepted', 'superseded', 'rejected')
    ),
    CONSTRAINT thread_snapshots_writer_mode_valid CHECK (
        writer_mode IN ('explicit_start', 'explicit_transition',
                        'explicit_artifact', 'explicit_final',
                        'heartbeat', 'external_polling', 'recovery_scan')
    ),
    CONSTRAINT thread_snapshots_confidence_range CHECK (
        confidence_score >= 0.0 AND confidence_score <= 1.0
    ),
    CONSTRAINT thread_snapshots_state_hash_nonempty CHECK (
        char_length(state_hash) > 0
    ),
    CONSTRAINT thread_snapshots_project_id_nonempty CHECK (
        char_length(project_id) > 0
    ),
    CONSTRAINT thread_snapshots_front_id_nonempty CHECK (
        char_length(front_id) > 0
    ),
    -- FK self-referencial (DAG). Si parent_snapshot_id no existe, fallar duro.
    CONSTRAINT thread_snapshots_parent_fk
        FOREIGN KEY (parent_snapshot_id)
        REFERENCES public.thread_snapshots(snapshot_id)
        DEFERRABLE INITIALLY DEFERRED
);

COMMENT ON TABLE public.thread_snapshots IS
'Snapshots versionados de estado operativo por (project_id, front_id). '
'Materializan el contrato ATTACHMENT_OK que se inyecta al prompt antes del primer razonamiento del agente. '
'Sprint MANUS-ANTI-DORY-002 v1 FASE B.1. SPEC §A.3+§A.10. Cowork T2-A GREEN.';

COMMENT ON COLUMN public.thread_snapshots.state_hash IS
'Hash del payload canónico del snapshot (SHA-256 hex). Permite integridad y detección de tampering por el Guardian.';

COMMENT ON COLUMN public.thread_snapshots.parent_snapshot_id IS
'FK self-referencial. NULL = snapshot raíz (write_on_start). Permite reconstruir cadena DAG de versiones.';

COMMENT ON COLUMN public.thread_snapshots.do_not_touch IS
'Array JSONB de artefactos/recursos protegidos por regla T1 (PR #118, /mnt/desktop, secrets). Guardian rechaza con HALT_ATTACHMENT_MISMATCH si el agente recuperado intenta tocarlos.';

COMMENT ON COLUMN public.thread_snapshots.evidence_refs IS
'Array JSONB de referencias a evidencia (gh PRs, commits, Railway endpoints, archivos). Context Broker verifica vigencia antes de inyectar.';

COMMENT ON COLUMN public.thread_snapshots.confidence_score IS
'Score [0.0-1.0] de qué tan seguro está el writer del estado capturado. Recovery Mode usa este score para preguntar "¿Sí/No?" al usuario.';

COMMENT ON COLUMN public.thread_snapshots.writer_mode IS
'Quien escribió este snapshot: explicit_start | explicit_transition | explicit_artifact | explicit_final | heartbeat | external_polling | recovery_scan. Trazabilidad del black-box recorder.';

COMMENT ON COLUMN public.thread_snapshots.status IS
'pending | accepted | superseded | rejected. project_runtime_heads apunta solo a status=accepted.';

-- Índices.
CREATE INDEX IF NOT EXISTS idx_thread_snapshots_project_front_created
    ON public.thread_snapshots (project_id, front_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_thread_snapshots_parent
    ON public.thread_snapshots (parent_snapshot_id)
    WHERE parent_snapshot_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_thread_snapshots_sprint_phase
    ON public.thread_snapshots (sprint_id, phase, created_at DESC)
    WHERE sprint_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_thread_snapshots_status_created
    ON public.thread_snapshots (status, created_at DESC);

-- =============================================================================
-- RLS por defecto (DSC-S-006 v1.1)
-- =============================================================================

ALTER TABLE public.thread_snapshots ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS thread_snapshots_service_role_only ON public.thread_snapshots;
CREATE POLICY thread_snapshots_service_role_only
    ON public.thread_snapshots
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

REVOKE ALL ON public.thread_snapshots FROM PUBLIC;
REVOKE ALL ON public.thread_snapshots FROM anon;
REVOKE ALL ON public.thread_snapshots FROM authenticated;
GRANT SELECT, INSERT, UPDATE ON public.thread_snapshots TO service_role;
-- UPDATE permitido SOLO para status transitions (pending → accepted/superseded/rejected)
-- y para updated_at. Resto del contenido se considera inmutable (enforcement vía RPC).

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
    WHERE relname = 'thread_snapshots' AND relnamespace = 'public'::regnamespace;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: thread_snapshots creada sin RLS habilitado';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'thread_snapshots';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: thread_snapshots sin policies explícitas';
    END IF;

    RAISE NOTICE 'thread_snapshots creada OK: RLS=%, policies=%', v_rls_enabled, v_policy_count;
END $$;

COMMIT;
