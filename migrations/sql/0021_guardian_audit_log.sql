-- Migration 0021: guardian_audit_log
-- Sprint: GUARDIAN-AUTONOMO-001 (T5)
-- DSC enforzado: DSC-S-006 v1.1 (RLS por defecto), DSC-G-017 (DSC-as-Contract)
-- Fecha: 2026-05-12
-- Owner: Hilo Ejecutor 2 (manus_hilo_b)
--
-- Tabla persiste cada ejecución del cron diario del Guardian de los Objetivos.
-- Una fila por (objective_id, audit_run_id) — un audit_run_id agrupa las 15
-- evaluaciones de una sola corrida cron.
--
-- Idempotencia: CREATE TABLE IF NOT EXISTS + CREATE POLICY IF NOT EXISTS.

BEGIN;

-- Tabla principal
CREATE TABLE IF NOT EXISTS public.guardian_audit_log (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    audit_run_id    UUID            NOT NULL,
    objective_id    INTEGER         NOT NULL CHECK (objective_id BETWEEN 1 AND 15),
    objective_name  TEXT            NOT NULL,
    score_pct       NUMERIC(5,2)    NOT NULL CHECK (score_pct >= 0 AND score_pct <= 100),
    delta_vs_previous NUMERIC(5,2)  NULL,
    rubrica_version TEXT            NOT NULL,
    evidence_jsonb  JSONB           NOT NULL DEFAULT '{}'::jsonb,
    status          TEXT            NOT NULL CHECK (status IN ('ok','warning','critical','emergency')),
    triggered_alert BOOLEAN         NOT NULL DEFAULT FALSE,
    notes           TEXT            NULL
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_guardian_audit_log_created_at
    ON public.guardian_audit_log (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_guardian_audit_log_audit_run_id
    ON public.guardian_audit_log (audit_run_id);

CREATE INDEX IF NOT EXISTS idx_guardian_audit_log_objective_id_created
    ON public.guardian_audit_log (objective_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_guardian_audit_log_status
    ON public.guardian_audit_log (status)
    WHERE status IN ('critical','emergency');

-- RLS por defecto (DSC-S-006 v1.1) — service_role_only desde nacimiento
ALTER TABLE public.guardian_audit_log ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'guardian_audit_log'
          AND policyname = 'guardian_audit_log_service_role_only'
    ) THEN
        CREATE POLICY guardian_audit_log_service_role_only
            ON public.guardian_audit_log
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END
$$;

-- Verificación automática (RAISE EXCEPTION si RLS no quedó habilitado)
DO $$
DECLARE
    v_rls_enabled BOOLEAN;
    v_policy_count INTEGER;
BEGIN
    SELECT relrowsecurity INTO v_rls_enabled
    FROM pg_class
    WHERE oid = 'public.guardian_audit_log'::regclass;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'guardian_audit_log: RLS no quedo habilitado (DSC-S-006 violado)';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'guardian_audit_log';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'guardian_audit_log: cero policies (DSC-S-006 violado)';
    END IF;
END
$$;

COMMIT;

-- Notas operativas:
-- 1) audit_run_id permite agrupar las 15 evaluaciones de una sola corrida cron.
-- 2) evidence_jsonb permite guardar el JSON arbitrario que la rúbrica produzca
--    (cuentas de tablas, RLS coverage, count de DSCs, etc.).
-- 3) triggered_alert = TRUE registra que esta fila disparó alerting Telegram (T3).
-- 4) Para reportes: agregar por audit_run_id o filtrar por status IN ('critical','emergency').
