-- Migration 0024: escape_pulse_log
-- Sprint: ESCAPE-001 (T1) — Throttler Determinístico (pieza magna #2 Reloj Suizo)
-- DSC enforzado: DSC-S-006 v1.1 (RLS por defecto), DSC-G-017 (DSC-as-Contract),
--                DSC-MO-010 (Reloj Suizo §2.1 fila 2), DSC-G-008 v2 (anti-Goodhart),
--                DSC-S-012 (anti-deriva migraciones), Obj #11 + #8
-- Fecha: 2026-05-12
-- Owner: Hilo Ejecutor 2 (manus_hilo_b)
--
-- Tabla persiste cada pulso del Escapement por 6 consumers canónicos:
--   embrion_loop_latido    (60s default, 1 ciclo Volante/min)
--   guardian_daily_audit   (86400s default, 1 audit/día)
--   rotor_recharge         (300s default, mismo que recharge_mainspring)
--   self_verifier_call     (30s default, max 2 Self-Verifier/min)
--   embrion_specialization (120s default, especializaciones cada 2min)
--   external_llm_call      (10s default, llamadas LLM agresivas)
--
-- Idempotencia: CREATE TABLE IF NOT EXISTS + DROP/CREATE POLICY (Postgres <16
-- no soporta CREATE POLICY IF NOT EXISTS).
--
-- LECCIÓN POST-V25: NO usar DATE(TIMESTAMPTZ) en CREATE INDEX. Si necesario
-- índice por día, usar columna generada STORED. Aquí solo índices simples.

BEGIN;

-- ===========================================================================
-- Tabla principal
-- ===========================================================================
CREATE TABLE IF NOT EXISTS public.escape_pulse_log (
    id                      UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    pulse_id                BIGSERIAL    NOT NULL,                          -- secuencia monotónica
    consumer                TEXT         NOT NULL,                          -- nombre canónico (ver doctrina §2.T2)
    energy_consumed         NUMERIC(10,6) NOT NULL DEFAULT 1.000000,        -- unidades de energía consumidas
    pulse_interval_seconds  INTEGER      NOT NULL DEFAULT 60,               -- intervalo configurado para ese consumer
    blocked_count           INTEGER      NOT NULL DEFAULT 0,                -- veces que el consumer fue bloqueado en este intervalo
    metadata                JSONB        NOT NULL DEFAULT '{}'::jsonb,
    -- consumer NO tiene CHECK constraint estricto a propósito: permite
    -- crecimiento futuro de consumers (ej: espiral_feedback, remontoir_quality)
    -- sin migration nueva. Los 6 nombres canónicos viven en kernel/escape/config.py
    -- como REGISTRY_CONSUMERS para validación a nivel app.
    CONSTRAINT escape_pulse_log_energy_consumed_nonneg CHECK (energy_consumed >= 0),
    CONSTRAINT escape_pulse_log_interval_positive CHECK (pulse_interval_seconds > 0),
    CONSTRAINT escape_pulse_log_blocked_count_nonneg CHECK (blocked_count >= 0)
);

COMMENT ON TABLE public.escape_pulse_log IS
'Pieza Escape del Reloj Suizo — dosifica el consumo del embrion_budget en pulsos discretos por consumer. '
'Spec: bridge/sprints_propuestos/sprint_ESCAPE_001_throttler_deterministico.md (firmado T1 2026-05-12 ~07:55 UTC). '
'6 consumers canónicos viven en kernel/escape/config.py. Único caller autorizado a consume() del budget: Escapement.record_pulse().';

COMMENT ON COLUMN public.escape_pulse_log.pulse_id IS
'BIGSERIAL monotónico. Gaps post-reinicio Postgres son expected (no es bug).';

COMMENT ON COLUMN public.escape_pulse_log.consumer IS
'Nombre canónico del consumer (sin CHECK constraint a propósito). Validación a nivel app vs REGISTRY_CONSUMERS de kernel/escape/config.py. Los 6 default firmados T1: embrion_loop_latido, guardian_daily_audit, rotor_recharge, self_verifier_call, embrion_specialization, external_llm_call.';

COMMENT ON COLUMN public.escape_pulse_log.energy_consumed IS
'NUMERIC(10,6) — unidades de energía consumidas en este pulso. Default 1.0 según doctrina §4 paso 2.';

COMMENT ON COLUMN public.escape_pulse_log.blocked_count IS
'Cuántas veces el consumer intentó pulsar pero fue bloqueado dentro del intervalo. DSC-G-008 v2 anti-Goodhart: tracking explícito de presión sobre el throttler.';

-- ===========================================================================
-- Índices (sin DATE(TIMESTAMPTZ) — lección post-V25)
-- ===========================================================================
CREATE INDEX IF NOT EXISTS idx_escape_pulse_log_consumer_created
    ON public.escape_pulse_log (consumer, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_escape_pulse_log_pulse_id_desc
    ON public.escape_pulse_log (pulse_id DESC);

CREATE INDEX IF NOT EXISTS idx_escape_pulse_log_created_at_desc
    ON public.escape_pulse_log (created_at DESC);

-- ===========================================================================
-- RLS por defecto (DSC-S-006 v1.1)
-- ===========================================================================
ALTER TABLE public.escape_pulse_log ENABLE ROW LEVEL SECURITY;

-- Drop + Create para idempotencia (Postgres <16 no soporta CREATE POLICY IF NOT EXISTS)
DROP POLICY IF EXISTS escape_pulse_log_service_role_only ON public.escape_pulse_log;
CREATE POLICY escape_pulse_log_service_role_only
    ON public.escape_pulse_log
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Revoke explícito de PUBLIC/anon/authenticated (defense in depth)
REVOKE ALL ON public.escape_pulse_log FROM PUBLIC;
REVOKE ALL ON public.escape_pulse_log FROM anon;
REVOKE ALL ON public.escape_pulse_log FROM authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.escape_pulse_log TO service_role;

-- ===========================================================================
-- Verificación automática post-apply (RAISE EXCEPTION si RLS no quedó habilitada)
-- ===========================================================================
DO $$
DECLARE
    v_rls_enabled BOOLEAN;
    v_policy_count INTEGER;
BEGIN
    SELECT relrowsecurity INTO v_rls_enabled
    FROM pg_class
    WHERE relname = 'escape_pulse_log' AND relnamespace = 'public'::regnamespace;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: escape_pulse_log creada sin RLS habilitado';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'escape_pulse_log';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: escape_pulse_log sin policies explícitas';
    END IF;

    RAISE NOTICE 'escape_pulse_log creada OK: RLS=%, policies=%', v_rls_enabled, v_policy_count;
END $$;

COMMIT;
