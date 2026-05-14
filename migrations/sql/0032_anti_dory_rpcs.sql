-- =============================================================================
-- Migration 0032 — Anti-Dory RPCs (5 funciones SECURITY DEFINER)
-- =============================================================================
-- Sprint: MANUS-ANTI-DORY-002 v1, FASE B.2
-- Doctrina: SPEC §A.4 (RPCs Supabase y Permisos), §A.5 (Context Broker)
-- Origen: GPT-5.5 Pro audit + Opus 4.7 convergencia + Cowork T2-A APPROVED
--
-- NOTA T0 AUDIT: Cowork SPEC asume roles segregados
--   (anti_dory_writer_role, anti_dory_reader_role). v1 los DEFINE pero
--   las GRANT a usuarios reales quedan deferred — los RPCs son SECURITY
--   DEFINER y se ejecutan con privilegios del owner (postgres). Esto
--   evita acoplamiento con la política Supabase global de service_key.
--
-- Funciones expuestas (5):
--   1. rpc_write_runtime_event   — append a runtime_events
--   2. rpc_write_thread_snapshot — INSERT thread_snapshots, devuelve UUID
--   3. rpc_get_context_head      — JOIN heads + snapshots, devuelve estado
--   4. rpc_accept_snapshot       — compare-and-swap sobre heads (CAS)
--   5. rpc_recovery_scan         — reconstruye candidato desde runtime_events
-- =============================================================================

BEGIN;

-- =============================================================================
-- Roles segregados (DEFINIDOS aquí, GRANT a usuarios reales en FASE futura)
-- =============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anti_dory_writer_role') THEN
        CREATE ROLE anti_dory_writer_role NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anti_dory_reader_role') THEN
        CREATE ROLE anti_dory_reader_role NOLOGIN;
    END IF;
END $$;

-- =============================================================================
-- 1. rpc_write_runtime_event — Append a runtime_events
-- =============================================================================

CREATE OR REPLACE FUNCTION public.rpc_write_runtime_event(
    p_project_id  TEXT,
    p_front_id    TEXT,
    p_actor_type  TEXT,
    p_event_type  TEXT,
    p_payload     JSONB DEFAULT '{}'::jsonb,
    p_thread_id   TEXT DEFAULT NULL,
    p_snapshot_id UUID DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_event_id UUID;
BEGIN
    IF p_project_id IS NULL OR char_length(p_project_id) = 0 THEN
        RAISE EXCEPTION 'rpc_write_runtime_event: project_id required';
    END IF;
    IF p_front_id IS NULL OR char_length(p_front_id) = 0 THEN
        RAISE EXCEPTION 'rpc_write_runtime_event: front_id required';
    END IF;
    IF p_actor_type IS NULL OR p_actor_type NOT IN ('manus', 'cowork', 'embrion', 'system') THEN
        RAISE EXCEPTION 'rpc_write_runtime_event: invalid actor_type: %', p_actor_type;
    END IF;

    INSERT INTO public.runtime_events (
        project_id, front_id, actor_type, event_type, payload, thread_id, snapshot_id
    ) VALUES (
        p_project_id, p_front_id, p_actor_type, p_event_type, COALESCE(p_payload, '{}'::jsonb),
        p_thread_id, p_snapshot_id
    )
    RETURNING event_id INTO v_event_id;

    RETURN v_event_id;
END;
$$;

COMMENT ON FUNCTION public.rpc_write_runtime_event IS
'Append a runtime_events. SECURITY DEFINER. Sprint MANUS-ANTI-DORY-002 v1 §A.4.';

-- =============================================================================
-- 2. rpc_write_thread_snapshot — INSERT thread_snapshots
-- =============================================================================

CREATE OR REPLACE FUNCTION public.rpc_write_thread_snapshot(
    p_project_id           TEXT,
    p_front_id             TEXT,
    p_actor_type           TEXT,
    p_state_hash           TEXT,
    p_writer_mode          TEXT,
    p_parent_snapshot_id   UUID DEFAULT NULL,
    p_sprint_id            TEXT DEFAULT NULL,
    p_phase                TEXT DEFAULT NULL,
    p_last_t1_decision     TEXT DEFAULT NULL,
    p_next_expected_action TEXT DEFAULT NULL,
    p_do_not_touch         JSONB DEFAULT '[]'::jsonb,
    p_evidence_refs        JSONB DEFAULT '[]'::jsonb,
    p_confidence_score     NUMERIC DEFAULT 1.00,
    p_summary              TEXT DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_snapshot_id UUID;
BEGIN
    IF p_writer_mode NOT IN (
        'explicit_start', 'explicit_transition', 'explicit_artifact',
        'explicit_final', 'heartbeat', 'external_polling', 'recovery_scan'
    ) THEN
        RAISE EXCEPTION 'rpc_write_thread_snapshot: invalid writer_mode: %', p_writer_mode;
    END IF;

    INSERT INTO public.thread_snapshots (
        project_id, front_id, actor_type, parent_snapshot_id,
        state_hash, sprint_id, phase, last_t1_decision, next_expected_action,
        do_not_touch, evidence_refs, confidence_score, writer_mode, summary,
        status
    ) VALUES (
        p_project_id, p_front_id, p_actor_type, p_parent_snapshot_id,
        p_state_hash, p_sprint_id, p_phase, p_last_t1_decision, p_next_expected_action,
        COALESCE(p_do_not_touch, '[]'::jsonb),
        COALESCE(p_evidence_refs, '[]'::jsonb),
        COALESCE(p_confidence_score, 1.00),
        p_writer_mode, p_summary,
        'pending'
    )
    RETURNING snapshot_id INTO v_snapshot_id;

    RETURN v_snapshot_id;
END;
$$;

COMMENT ON FUNCTION public.rpc_write_thread_snapshot IS
'INSERT thread_snapshots con status=pending. Devuelve snapshot_id. SECURITY DEFINER. Sprint MANUS-ANTI-DORY-002 v1 §A.4.';

-- =============================================================================
-- 3. rpc_get_context_head — JOIN heads + snapshots, devuelve estado
-- =============================================================================

CREATE OR REPLACE FUNCTION public.rpc_get_context_head(
    p_project_id TEXT,
    p_front_id   TEXT
)
RETURNS TABLE (
    snapshot_id          UUID,
    project_id           TEXT,
    front_id             TEXT,
    actor_type           TEXT,
    sprint_id            TEXT,
    phase                TEXT,
    last_t1_decision     TEXT,
    next_expected_action TEXT,
    do_not_touch         JSONB,
    evidence_refs        JSONB,
    confidence_score     NUMERIC,
    state_hash           TEXT,
    writer_mode          TEXT,
    snapshot_created_at  TIMESTAMPTZ,
    head_updated_at      TIMESTAMPTZ,
    lock_version         INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.snapshot_id,
        s.project_id,
        s.front_id,
        s.actor_type,
        s.sprint_id,
        s.phase,
        s.last_t1_decision,
        s.next_expected_action,
        s.do_not_touch,
        s.evidence_refs,
        s.confidence_score,
        s.state_hash,
        s.writer_mode,
        s.created_at AS snapshot_created_at,
        h.updated_at AS head_updated_at,
        h.lock_version
    FROM public.project_runtime_heads h
    JOIN public.thread_snapshots s ON s.snapshot_id = h.head_snapshot_id
    WHERE h.project_id = p_project_id AND h.front_id = p_front_id
    LIMIT 1;
END;
$$;

COMMENT ON FUNCTION public.rpc_get_context_head IS
'Devuelve el snapshot accepted vigente (head) para (project_id, front_id). SECURITY DEFINER. Sprint MANUS-ANTI-DORY-002 v1 §A.4+§A.5.';

-- =============================================================================
-- 4. rpc_accept_snapshot — Compare-and-swap sobre heads (CAS)
-- =============================================================================

CREATE OR REPLACE FUNCTION public.rpc_accept_snapshot(
    p_project_id              TEXT,
    p_front_id                TEXT,
    p_snapshot_id             UUID,
    p_expected_lock_version   INTEGER
)
RETURNS TABLE (
    accepted        BOOLEAN,
    new_lock_version INTEGER,
    conflict_reason  TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_existing_head_id UUID;
    v_existing_lock    INTEGER;
    v_new_lock         INTEGER;
    v_snapshot_status  TEXT;
BEGIN
    -- 1. Verificar que el snapshot exista y sea válido para promoción.
    SELECT status INTO v_snapshot_status
    FROM public.thread_snapshots
    WHERE snapshot_id = p_snapshot_id;

    IF v_snapshot_status IS NULL THEN
        RETURN QUERY SELECT FALSE, NULL::INTEGER, 'snapshot_not_found'::TEXT;
        RETURN;
    END IF;
    IF v_snapshot_status NOT IN ('pending', 'accepted') THEN
        RETURN QUERY SELECT FALSE, NULL::INTEGER, ('invalid_snapshot_status:' || v_snapshot_status)::TEXT;
        RETURN;
    END IF;

    -- 2. Lock optimistic sobre heads.
    SELECT head_snapshot_id, lock_version
      INTO v_existing_head_id, v_existing_lock
    FROM public.project_runtime_heads
    WHERE project_id = p_project_id AND front_id = p_front_id
    FOR UPDATE;

    IF v_existing_head_id IS NULL THEN
        -- Primer head para este (project, front). lock_version inicial = 1.
        IF p_expected_lock_version <> 0 THEN
            RETURN QUERY SELECT FALSE, NULL::INTEGER, 'expected_zero_for_first_head'::TEXT;
            RETURN;
        END IF;
        INSERT INTO public.project_runtime_heads (project_id, front_id, head_snapshot_id, lock_version, updated_at)
        VALUES (p_project_id, p_front_id, p_snapshot_id, 1, NOW());
        v_new_lock := 1;
    ELSE
        IF v_existing_lock <> p_expected_lock_version THEN
            RETURN QUERY SELECT FALSE, v_existing_lock, ('lock_version_conflict:expected=' || p_expected_lock_version || ',actual=' || v_existing_lock)::TEXT;
            RETURN;
        END IF;
        v_new_lock := v_existing_lock + 1;
        -- Marcar snapshot previo como superseded.
        UPDATE public.thread_snapshots
           SET status = 'superseded', updated_at = NOW()
         WHERE snapshot_id = v_existing_head_id AND status = 'accepted';
        UPDATE public.project_runtime_heads
           SET head_snapshot_id = p_snapshot_id,
               lock_version = v_new_lock,
               updated_at = NOW()
         WHERE project_id = p_project_id AND front_id = p_front_id;
    END IF;

    -- 3. Promover snapshot a accepted.
    UPDATE public.thread_snapshots
       SET status = 'accepted', updated_at = NOW()
     WHERE snapshot_id = p_snapshot_id;

    RETURN QUERY SELECT TRUE, v_new_lock, NULL::TEXT;
END;
$$;

COMMENT ON FUNCTION public.rpc_accept_snapshot IS
'Compare-and-swap sobre project_runtime_heads. Promueve snapshot a accepted y supersede previo. SECURITY DEFINER. Sprint MANUS-ANTI-DORY-002 v1 §A.4.';

-- =============================================================================
-- 5. rpc_recovery_scan — Reconstruye candidato desde runtime_events
-- =============================================================================

CREATE OR REPLACE FUNCTION public.rpc_recovery_scan(
    p_project_id TEXT,
    p_front_id   TEXT
)
RETURNS TABLE (
    last_event_id    UUID,
    last_event_type  TEXT,
    last_actor_type  TEXT,
    last_payload     JSONB,
    last_thread_id   TEXT,
    last_event_at    TIMESTAMPTZ,
    event_count      BIGINT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    WITH last_event AS (
        SELECT
            e.event_id,
            e.event_type,
            e.actor_type,
            e.payload,
            e.thread_id,
            e.created_at
        FROM public.runtime_events e
        WHERE e.project_id = p_project_id AND e.front_id = p_front_id
        ORDER BY e.created_at DESC
        LIMIT 1
    ),
    counts AS (
        SELECT COUNT(*) AS total
        FROM public.runtime_events e
        WHERE e.project_id = p_project_id AND e.front_id = p_front_id
    )
    SELECT
        le.event_id,
        le.event_type,
        le.actor_type,
        le.payload,
        le.thread_id,
        le.created_at,
        c.total
    FROM last_event le
    CROSS JOIN counts c;
END;
$$;

COMMENT ON FUNCTION public.rpc_recovery_scan IS
'Devuelve último evento + total de eventos para (project_id, front_id). Insumo de Recovery Mode cuando head está stale o ausente. SECURITY DEFINER. Sprint MANUS-ANTI-DORY-002 v1 §A.4+§A.8.';

-- =============================================================================
-- Permisos: GRANT EXECUTE a service_role (canonical) y roles segregados (futuro)
-- =============================================================================

REVOKE ALL ON FUNCTION public.rpc_write_runtime_event FROM PUBLIC;
REVOKE ALL ON FUNCTION public.rpc_write_thread_snapshot FROM PUBLIC;
REVOKE ALL ON FUNCTION public.rpc_get_context_head FROM PUBLIC;
REVOKE ALL ON FUNCTION public.rpc_accept_snapshot FROM PUBLIC;
REVOKE ALL ON FUNCTION public.rpc_recovery_scan FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.rpc_write_runtime_event   TO service_role, anti_dory_writer_role;
GRANT EXECUTE ON FUNCTION public.rpc_write_thread_snapshot TO service_role, anti_dory_writer_role;
GRANT EXECUTE ON FUNCTION public.rpc_get_context_head      TO service_role, anti_dory_reader_role;
GRANT EXECUTE ON FUNCTION public.rpc_accept_snapshot       TO service_role, anti_dory_writer_role;
GRANT EXECUTE ON FUNCTION public.rpc_recovery_scan         TO service_role, anti_dory_reader_role;

-- =============================================================================
-- Verificación: las 5 funciones existen
-- =============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
      AND p.proname IN (
          'rpc_write_runtime_event',
          'rpc_write_thread_snapshot',
          'rpc_get_context_head',
          'rpc_accept_snapshot',
          'rpc_recovery_scan'
      );

    IF v_count < 5 THEN
        RAISE EXCEPTION 'Anti-Dory RPCs incompletos: expected 5, got %', v_count;
    END IF;

    RAISE NOTICE 'Anti-Dory RPCs creadas OK: % funciones', v_count;
END $$;

COMMIT;
