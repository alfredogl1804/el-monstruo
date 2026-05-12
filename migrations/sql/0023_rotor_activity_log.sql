-- Migration 0023: rotor_activity_log
-- Sprint: ROTOR-001 (T1) — Reciclador de Actividad (pieza diferencial Reloj Suizo)
-- DSC enforzado: DSC-S-006 v1.1 (RLS por defecto), DSC-G-017 (DSC-as-Contract),
--                DSC-MO-010 (Reloj Suizo), Obj #11 + #15 + #8
-- Fecha: 2026-05-12
-- Owner: Hilo Ejecutor 2 (manus_hilo_b)
--
-- Tabla persiste cada evento de actividad capturado por el Rotor desde 6 sources:
--   github_commit | supabase_query | telegram_message | cowork_session
--   manus_session | embrion_latido
-- El Rotor convierte cada evento en `energy_units` (USD-equivalent) via
-- kernel/rotor/energy_calculator.py (defaults firmados por T1 2026-05-11).
-- recharge_mainspring (cada 5 min) consume estas filas y recarga embrion_budget.
--
-- Idempotencia: CREATE TABLE IF NOT EXISTS + CREATE POLICY IF NOT EXISTS.

BEGIN;

-- ===========================================================================
-- Tabla principal
-- ===========================================================================
CREATE TABLE IF NOT EXISTS public.rotor_activity_log (
    id                       UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    source                   TEXT         NOT NULL CHECK (source IN (
                                              'github_commit',
                                              'supabase_query',
                                              'telegram_message',
                                              'cowork_session',
                                              'manus_session',
                                              'embrion_latido'
                                          )),
    actor                    TEXT         NOT NULL,
    payload_jsonb            JSONB        NOT NULL DEFAULT '{}'::jsonb,
    energy_units             NUMERIC(8,4) NULL,  -- NULL hasta que energy_calculator lo procese
    energy_calculator_version TEXT        NULL,
    consumed_by_embrion_at   TIMESTAMPTZ  NULL,
    cycle_id_consumer        BIGINT       NULL,
    notes                    TEXT         NULL
);

COMMENT ON TABLE public.rotor_activity_log IS
'Pieza Rotor del Reloj Suizo — captura actividad humana + hilos Manus → energy_units → recharge embrion_budget. Spec: bridge/sprints_propuestos/sprint_ROTOR_001_reciclador_actividad.md (firmado T1 2026-05-11).';

COMMENT ON COLUMN public.rotor_activity_log.source IS
'6 sources canónicos. Defaults energy_units T3 firmados T1 2026-05-11.';

COMMENT ON COLUMN public.rotor_activity_log.energy_units IS
'NUMERIC(8,4) — USD-equivalent. NULL hasta que energy_calculator lo procese. Negativo permitido para penalizaciones (embrion_latido aborted = -0.05).';

COMMENT ON COLUMN public.rotor_activity_log.consumed_by_embrion_at IS
'Marcado por recharge_mainspring cuando esta fila se incluye en un recharge cycle. NULL = pendiente de consumo.';

COMMENT ON COLUMN public.rotor_activity_log.cycle_id_consumer IS
'ID del cycle del Embrión que consumió esta energía. Permite trazabilidad post-hoc.';

-- ===========================================================================
-- Índices (per spec §3 T1: source+created_at DESC + consumed_by_embrion_at)
-- ===========================================================================
CREATE INDEX IF NOT EXISTS idx_rotor_activity_log_source_created
    ON public.rotor_activity_log (source, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_rotor_activity_log_consumed
    ON public.rotor_activity_log (consumed_by_embrion_at NULLS FIRST, created_at)
    WHERE consumed_by_embrion_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_rotor_activity_log_actor_created
    ON public.rotor_activity_log (actor, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_rotor_activity_log_created_at
    ON public.rotor_activity_log (created_at DESC);

-- Índice parcial para anti-farming caps diarios (T3 query frecuente)
CREATE INDEX IF NOT EXISTS idx_rotor_activity_log_source_day
    ON public.rotor_activity_log (source, ((created_at AT TIME ZONE 'UTC')::DATE));

-- ===========================================================================
-- RLS por defecto (DSC-S-006 v1.1) — service_role_only desde nacimiento
-- ===========================================================================
ALTER TABLE public.rotor_activity_log ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'rotor_activity_log'
          AND policyname = 'rotor_activity_log_service_role_only'
    ) THEN
        CREATE POLICY rotor_activity_log_service_role_only
            ON public.rotor_activity_log
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END
$$;

-- ===========================================================================
-- Verificación automática (DSC-S-006 v1.1 — RAISE si RLS no quedó habilitado)
-- ===========================================================================
DO $$
DECLARE
    v_rls_enabled BOOLEAN;
    v_policy_count INTEGER;
    v_index_count INTEGER;
BEGIN
    SELECT relrowsecurity INTO v_rls_enabled
    FROM pg_class
    WHERE oid = 'public.rotor_activity_log'::regclass;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'rotor_activity_log: RLS no quedo habilitado (DSC-S-006 violado)';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'rotor_activity_log';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'rotor_activity_log: cero policies (DSC-S-006 violado)';
    END IF;

    SELECT COUNT(*) INTO v_index_count
    FROM pg_indexes
    WHERE schemaname = 'public' AND tablename = 'rotor_activity_log';

    -- 5 índices nuevos + el implícito del PK = 6 mínimo
    IF v_index_count < 6 THEN
        RAISE EXCEPTION 'rotor_activity_log: indices insuficientes (esperado >= 6, encontrado %)', v_index_count;
    END IF;
END
$$;

COMMIT;

-- ===========================================================================
-- Notas operativas
-- ===========================================================================
-- 1) `energy_units` permanece NULL hasta que `kernel/rotor/energy_calculator.py`
--    procesa la fila. Esto desacopla captura de cálculo (capturers son simples
--    INSERTers; el cálculo puede recalibrarse retroactivamente sin perder datos).
--
-- 2) `payload_jsonb` debe contener al menos los campos mínimos por source:
--    - github_commit:    {repo, sha, branch, merged_to_main: bool, files: int}
--    - supabase_query:   {table, query_type, rows_affected, duration_ms}
--    - telegram_message: {chat_id, message_id, text_length, sender}
--    - cowork_session:   {session_id, duration_seconds, ended_at}
--    - manus_session:    {hilo_origen, sprint_id, pr_merged: bool}
--    - embrion_latido:   {cycle_id, status, aborted_reason}
--
-- 3) `consumed_by_embrion_at IS NULL` = fila pendiente de consumo por
--    recharge_mainspring. La actualización ocurre en una sola transacción que
--    también incrementa `embrion_budget.daily_cap_remaining` (atomicidad).
--
-- 4) `cycle_id_consumer` provee trazabilidad: dado un cycle del Embrión, qué
--    energía exacta lo financió.
--
-- 5) Cap diario por source ($5 por día firmado T1) se valida en
--    `kernel/rotor/energy_calculator.py` consultando idx_rotor_activity_log_source_day.
--
-- 6) Cap superior recharge ($30/día firmado T1) se valida en
--    `kernel/rotor/recharge.py::recharge_mainspring()` antes de llamar a
--    `embrion_budget.add_recycled_energy()`.
