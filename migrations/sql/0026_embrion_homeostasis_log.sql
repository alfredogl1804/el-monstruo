-- Migration 0026: embrion_homeostasis_log
-- Sprint: ESPIRAL-001 (T1) — Hairspring Homeostasis Dinámica (pieza magna #5 Reloj Suizo)
-- DSC enforzado: DSC-S-006 v1.1 (RLS por defecto), DSC-G-017 (DSC-as-Contract),
--                DSC-MO-010 (Reloj Suizo §2.1 fila 5), DSC-G-008 v3 (anti-Goodhart + dedución),
--                DSC-S-012 (anti-deriva migraciones), Obj #11 + #2 + #4
-- Fecha: 2026-05-12
-- Owner: Hilo Ejecutor 2 (manus_hilo_b)
-- Spec firmado: bridge/sprints_propuestos/sprint_ESPIRAL_001_homeostasis_dinamica.md commit 0de35e6
--
-- Tabla persiste cada acción del Hairspring (feedback negativo dinámico).
-- Eventos posibles (adjustment_reason):
--   spike_dampening          → consumer pulsando >baseline+threshold, Espiral aumenta interval
--   undershoot_acceleration  → consumer pulsando <baseline-threshold, Espiral reduce interval
--   return_to_canonical      → deviation < threshold sostenida, restaura interval canonical
--
-- Patrón: lee escape_pulse_log (Pieza #2) en ventana móvil, calcula pulse_rate observed,
-- compara contra baseline canónico de kernel/escape/config.py, decide override y registra.
--
-- LECCIÓN POST-V25: NO usar DATE(TIMESTAMPTZ) en CREATE INDEX. Sólo índices simples.
-- Idempotencia: CREATE TABLE IF NOT EXISTS + DROP/CREATE POLICY (Postgres <16
-- no soporta CREATE POLICY IF NOT EXISTS).

BEGIN;

-- ===========================================================================
-- Tabla principal
-- ===========================================================================
CREATE TABLE IF NOT EXISTS public.embrion_homeostasis_log (
    id                          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at                  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    consumer                    TEXT         NOT NULL,                          -- consumer del Escape al que se aplicó homeostasis
    pulse_rate_observed         NUMERIC(10,4) NOT NULL,                         -- pulses/min observado en ventana móvil
    pulse_rate_baseline         NUMERIC(10,4) NOT NULL,                         -- baseline canónico calculado del consumer
    deviation_ratio             NUMERIC(10,4) NOT NULL,                         -- observed/baseline (1.0 = on target)
    pulse_interval_adjusted_to  INTEGER      NOT NULL,                          -- nuevo pulse_interval que aplicó Espiral
    pulse_interval_canonical    INTEGER      NOT NULL,                          -- canonical original del consumer (al que retornará)
    adjustment_reason           TEXT         NOT NULL,
    window_minutes              INTEGER      NOT NULL DEFAULT 15,               -- ventana móvil usada para sense
    metadata                    JSONB        NOT NULL DEFAULT '{}'::jsonb,

    -- consumer NO tiene CHECK constraint estricto a propósito: permite
    -- crecimiento futuro de consumers (ej: remontoir_fallback) sin migration nueva.
    -- Validación a nivel app vs REGISTRY_CONSUMERS de kernel/escape/config.py.

    CONSTRAINT homeostasis_log_pulse_rate_observed_nonneg CHECK (pulse_rate_observed >= 0),
    CONSTRAINT homeostasis_log_pulse_rate_baseline_nonneg CHECK (pulse_rate_baseline >= 0),
    CONSTRAINT homeostasis_log_deviation_ratio_nonneg CHECK (deviation_ratio >= 0),
    CONSTRAINT homeostasis_log_interval_adjusted_positive CHECK (pulse_interval_adjusted_to > 0),
    CONSTRAINT homeostasis_log_interval_canonical_positive CHECK (pulse_interval_canonical > 0),
    CONSTRAINT homeostasis_log_window_minutes_positive CHECK (window_minutes > 0),
    CONSTRAINT homeostasis_log_adjustment_reason_valid CHECK (
        adjustment_reason IN ('spike_dampening', 'undershoot_acceleration', 'return_to_canonical')
    )
);

COMMENT ON TABLE public.embrion_homeostasis_log IS
'Pieza Espiral (Hairspring) del Reloj Suizo — feedback negativo dinámico que ajusta pulse_intervals del Escape detectando deviation en ventana móvil 15min. '
'Spec: bridge/sprints_propuestos/sprint_ESPIRAL_001_homeostasis_dinamica.md (firmado T1 commit 0de35e6, gate VERDE 5325f17). '
'Cierra el feedback loop estructural Volante↔Escape (DSC-MO-010 Reloj Suizo §2.1 fila 5).';

COMMENT ON COLUMN public.embrion_homeostasis_log.consumer IS
'Nombre canónico del consumer del Escape (sin CHECK constraint a propósito). Validación a nivel app vs REGISTRY_CONSUMERS de kernel/escape/config.py.';

COMMENT ON COLUMN public.embrion_homeostasis_log.deviation_ratio IS
'observed/baseline. 1.0 = on target. >1.3 = spike (Espiral dampena). <0.7 = undershoot (Espiral acelera). Threshold default ±30%.';

COMMENT ON COLUMN public.embrion_homeostasis_log.adjustment_reason IS
'spike_dampening | undershoot_acceleration | return_to_canonical. DSC-G-008 v3 anti-Goodhart: tracking explícito del comportamiento correctivo.';

COMMENT ON COLUMN public.embrion_homeostasis_log.window_minutes IS
'Ventana móvil usada para calcular pulse_rate_observed. Default 15min (firmado T1 spec §2 lazos canonizados).';

-- ===========================================================================
-- Índices (sin DATE(TIMESTAMPTZ) — lección post-V25)
-- ===========================================================================
CREATE INDEX IF NOT EXISTS idx_homeostasis_log_consumer_created
    ON public.embrion_homeostasis_log (consumer, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_homeostasis_log_created_at_desc
    ON public.embrion_homeostasis_log (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_homeostasis_log_adjustment_reason
    ON public.embrion_homeostasis_log (adjustment_reason, created_at DESC);

-- ===========================================================================
-- RLS por defecto (DSC-S-006 v1.1)
-- ===========================================================================
ALTER TABLE public.embrion_homeostasis_log ENABLE ROW LEVEL SECURITY;

-- Drop + Create para idempotencia (Postgres <16 no soporta CREATE POLICY IF NOT EXISTS)
DROP POLICY IF EXISTS homeostasis_log_service_role_only ON public.embrion_homeostasis_log;
CREATE POLICY homeostasis_log_service_role_only
    ON public.embrion_homeostasis_log
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Revoke explícito de PUBLIC/anon/authenticated (defense in depth)
REVOKE ALL ON public.embrion_homeostasis_log FROM PUBLIC;
REVOKE ALL ON public.embrion_homeostasis_log FROM anon;
REVOKE ALL ON public.embrion_homeostasis_log FROM authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.embrion_homeostasis_log TO service_role;

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
    WHERE relname = 'embrion_homeostasis_log' AND relnamespace = 'public'::regnamespace;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: embrion_homeostasis_log creada sin RLS habilitado';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'embrion_homeostasis_log';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: embrion_homeostasis_log sin policies explícitas';
    END IF;

    RAISE NOTICE 'embrion_homeostasis_log creada OK: RLS=%, policies=%', v_rls_enabled, v_policy_count;
END $$;

COMMIT;
