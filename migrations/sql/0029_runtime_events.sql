-- =============================================================================
-- Migration 0029 — runtime_events (Anti-Dory event log append-only)
-- =============================================================================
-- Sprint: MANUS-ANTI-DORY-002 v1, FASE B.1
-- Doctrina: SPEC §A.3 (Schema SQL), §A.7 (Snapshot Writer Incremental)
-- Origen: GPT-5.5 Pro audit + Opus 4.7 convergencia + Cowork T2-A APPROVED
--
-- Propósito: Log append-only de eventos de runtime emitidos por agentes
--   (manus | cowork | embrion | system) durante sesiones operativas.
--   Es el insumo del heartbeat_writer (independiente del agente) para
--   reconstruir estado vía recovery_scan cuando el agent_explicit_writer
--   no alcanzó a hacer write_on_final (crash, freeze, terminación abrupta).
--
-- Contrato:
--   - APPEND-ONLY (UPDATE/DELETE bloqueados por trigger en futuras migrations
--     si Cowork lo solicita; v1 confía en service_role discipline + audit log).
--   - Hash de payload NO requerido en v1 (sí en thread_snapshots).
--   - actor_type controlado por CHECK constraint para evitar typos de agente.
--   - payload JSONB libre para extensibilidad.
--
-- RLS: DSC-S-006 v1.1 (RLS habilitada + policy explícita + DO block validador).
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS public.runtime_events (
    event_id        UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    project_id      TEXT         NOT NULL,
    front_id        TEXT         NOT NULL,
    actor_type      TEXT         NOT NULL,
    event_type      TEXT         NOT NULL,
    payload         JSONB        NOT NULL DEFAULT '{}'::jsonb,
    thread_id       TEXT,
    snapshot_id     UUID,
    CONSTRAINT runtime_events_actor_type_valid CHECK (
        actor_type IN ('manus', 'cowork', 'embrion', 'system')
    ),
    CONSTRAINT runtime_events_event_type_nonempty CHECK (
        char_length(event_type) > 0
    ),
    CONSTRAINT runtime_events_project_id_nonempty CHECK (
        char_length(project_id) > 0
    ),
    CONSTRAINT runtime_events_front_id_nonempty CHECK (
        char_length(front_id) > 0
    )
);

COMMENT ON TABLE public.runtime_events IS
'Append-only event log emitido por agentes (manus/cowork/embrion/system) durante sesiones operativas. '
'Insumo del heartbeat_writer (independiente del agente) para recovery_scan ante crashes. '
'Sprint MANUS-ANTI-DORY-002 v1 FASE B.1. SPEC §A.3+§A.7. Cowork T2-A GREEN.';

COMMENT ON COLUMN public.runtime_events.actor_type IS
'manus | cowork | embrion | system. CHECK constraint para evitar typos de agente.';

COMMENT ON COLUMN public.runtime_events.event_type IS
'Nombre canónico del evento (session_started | phase_transition | artifact_created | session_final | heartbeat | etc.). Libre por diseño v1.';

COMMENT ON COLUMN public.runtime_events.payload IS
'JSONB libre. Contiene datos específicos del evento (paths, refs, hashes, metadata). NO contiene secrets (validado a nivel app).';

COMMENT ON COLUMN public.runtime_events.thread_id IS
'ID opcional del hilo Manus (task_id) o de la sesión Cowork. Permite reconstruir cadena de eventos por sesión.';

COMMENT ON COLUMN public.runtime_events.snapshot_id IS
'FK opcional a thread_snapshots (no constraint formal: ese constraint vive en migration 0030 para evitar dependencia circular).';

-- Índices (DSC-G lección post-V25: NO DATE(TIMESTAMPTZ); usar created_at DESC).
CREATE INDEX IF NOT EXISTS idx_runtime_events_project_front_created
    ON public.runtime_events (project_id, front_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_runtime_events_actor_event_created
    ON public.runtime_events (actor_type, event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_runtime_events_thread_created
    ON public.runtime_events (thread_id, created_at DESC)
    WHERE thread_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_runtime_events_snapshot
    ON public.runtime_events (snapshot_id)
    WHERE snapshot_id IS NOT NULL;

-- =============================================================================
-- RLS por defecto (DSC-S-006 v1.1)
-- =============================================================================

ALTER TABLE public.runtime_events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS runtime_events_service_role_only ON public.runtime_events;
CREATE POLICY runtime_events_service_role_only
    ON public.runtime_events
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Defense in depth: revoke PUBLIC/anon/authenticated.
REVOKE ALL ON public.runtime_events FROM PUBLIC;
REVOKE ALL ON public.runtime_events FROM anon;
REVOKE ALL ON public.runtime_events FROM authenticated;
GRANT SELECT, INSERT ON public.runtime_events TO service_role;
-- Nota: NO se otorga UPDATE/DELETE por diseño (append-only). Si Cowork pide
-- enforcement vía trigger en futura migration, queda como deuda explícita.

-- =============================================================================
-- Verificación automática post-apply (DO block, RAISE EXCEPTION si falta RLS)
-- =============================================================================

DO $$
DECLARE
    v_rls_enabled  BOOLEAN;
    v_policy_count INTEGER;
BEGIN
    SELECT relrowsecurity INTO v_rls_enabled
    FROM pg_class
    WHERE relname = 'runtime_events' AND relnamespace = 'public'::regnamespace;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: runtime_events creada sin RLS habilitado';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'runtime_events';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: runtime_events sin policies explícitas';
    END IF;

    RAISE NOTICE 'runtime_events creada OK: RLS=%, policies=%', v_rls_enabled, v_policy_count;
END $$;

COMMIT;
