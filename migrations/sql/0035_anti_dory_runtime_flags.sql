-- ============================================================================
-- Migration 0035 — Anti-Dory Runtime Flags (Kill-Switch DB + Write Budget)
-- ============================================================================
-- Sprint:        MANUS-ANTI-DORY-002 v1 FASE D4
-- Created:       2026-05-14
-- Author:        Manus (Ejecutor 1) bajo autoridad triple T1 + Cowork T2-A + GPT-5.5 Pro
-- Doctrina:      DSC-S-006 v1.1 (RLS por defecto) + Cowork audit bd11733b §5 C2+C3
-- Convergencia:  Tier 1 DSC-V-001 (3 sabios independientes converged)
-- Depends on:    0029 (runtime_events), 0030 (thread_snapshots),
--                0031 (project_runtime_heads), 0032 (RPCs), 0034 (grants)
-- ============================================================================
-- Frase canónica magna GPT-5.5 Pro:
--   "Shadow prod no es activación: es instrumentación reversible con cero
--    hidratación hasta que el attachment real pase prueba binaria."
-- ============================================================================
-- Contexto:
--   FASE D4 activa el HeartbeatWriter en Railway cron con flag OFF en wire
--   (ANTI_DORY_ENABLED=false) y flag ON solo en cron (ANTI_DORY_CRON_ENABLED=true).
--
--   Cowork T2-A + GPT-5.5 Pro Sabio exigen 2 controles DB obligatorios antes
--   de activar el cron (audit bd11733b §5):
--
--   C2 — Kill switch DB: tabla anti_dory_runtime_flags con shadow_write_enabled
--        boolean. Cada write del cron verifica antes. Si false → NO escribe.
--        Permite a T1 detener el shadow desde el SQL Editor sin tocar Railway.
--
--   C3 — Write budget hardcap observable: tabla anti_dory_write_budget con
--        contadores por ventana de 10min / 1h / 24h. Self-disable si excede:
--        max 1 heartbeat / 10min, 6 / hora, 150 / 24h.
--        Self-disable es UPDATE shadow_write_enabled=false desde el cron.
--
--   Esta migration crea ambas tablas con RLS, policies, seeds operativos y
--   verificación binaria post-apply.
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Tabla anti_dory_runtime_flags — Kill switch DB (C2)
-- ============================================================================
-- Diseño:
--   - Singleton lógico (UNIQUE constraint en singleton_lock)
--   - shadow_write_enabled boolean controla TODA escritura del cron
--   - kill_reason auditable cuando T1 lo apaga manualmente
--   - last_disabled_at auditable timestamp
--   - last_disabled_by auditable actor (T1 humano, self_disable_budget,
--     self_disable_error, etc.)

CREATE TABLE IF NOT EXISTS public.anti_dory_runtime_flags (
    flag_id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    singleton_lock    TEXT        NOT NULL UNIQUE
                                  DEFAULT 'anti_dory_singleton',
    -- Kill switch principal: si false, el cron NO escribe.
    shadow_write_enabled BOOLEAN  NOT NULL DEFAULT false,
    -- Audit trail
    last_enabled_at   TIMESTAMPTZ,
    last_enabled_by   TEXT,
    last_disabled_at  TIMESTAMPTZ,
    last_disabled_by  TEXT,
    kill_reason       TEXT,
    -- Metadata
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Constraints
    CONSTRAINT singleton_lock_canonical CHECK (singleton_lock = 'anti_dory_singleton'),
    CONSTRAINT kill_reason_when_disabled CHECK (
        shadow_write_enabled = true
        OR (shadow_write_enabled = false AND last_disabled_at IS NOT NULL)
        OR (shadow_write_enabled = false AND created_at = updated_at)
    )
);

COMMENT ON TABLE public.anti_dory_runtime_flags IS
    'Cowork audit bd11733b §5 C2 — Kill switch DB para Anti-Dory shadow writer. Singleton lógico. shadow_write_enabled controla TODA escritura del cron. T1 puede flip a false desde SQL Editor sin tocar Railway.';

COMMENT ON COLUMN public.anti_dory_runtime_flags.shadow_write_enabled IS
    'Kill switch principal. Si false, cron NO escribe. Default false (fail-closed). T1 firma flip a true para activar D4.';

COMMENT ON COLUMN public.anti_dory_runtime_flags.last_disabled_by IS
    'Audit: actor que apagó. Valores esperados: T1_alfredo, self_disable_budget_10min, self_disable_budget_1h, self_disable_budget_24h, self_disable_error_burst.';

-- Trigger updated_at
CREATE OR REPLACE FUNCTION anti_dory_runtime_flags_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_anti_dory_runtime_flags_updated_at
    ON public.anti_dory_runtime_flags;

CREATE TRIGGER trg_anti_dory_runtime_flags_updated_at
    BEFORE UPDATE ON public.anti_dory_runtime_flags
    FOR EACH ROW
    EXECUTE FUNCTION anti_dory_runtime_flags_set_updated_at();

-- Seed singleton row (fail-closed: shadow_write_enabled=false por default).
-- T1 debe firmar UPDATE manual para activar.
INSERT INTO public.anti_dory_runtime_flags (singleton_lock, shadow_write_enabled)
VALUES ('anti_dory_singleton', false)
ON CONFLICT (singleton_lock) DO NOTHING;

-- ============================================================================
-- 2. Tabla anti_dory_write_budget — Hardcap observable (C3)
-- ============================================================================
-- Diseño:
--   - Una fila por ventana temporal (10min / 1h / 24h)
--   - window_kind ENUM: 'w10min' | 'w1h' | 'w24h'
--   - window_start_utc inmutable (bucket alineado)
--   - write_count incrementa con cada escritura del cron
--   - max_writes hardcap configurable (default por window_kind)
--   - UNIQUE (window_kind, window_start_utc) previene duplicados de ventana
--
-- Self-disable trigger: cuando write_count > max_writes en cualquier ventana
-- activa, el cron debe hacer UPDATE anti_dory_runtime_flags
-- SET shadow_write_enabled=false, kill_reason='budget_exceeded'.

CREATE TABLE IF NOT EXISTS public.anti_dory_write_budget (
    budget_id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    window_kind       TEXT        NOT NULL,
    window_start_utc  TIMESTAMPTZ NOT NULL,
    write_count       INTEGER     NOT NULL DEFAULT 0,
    max_writes        INTEGER     NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Constraints
    CONSTRAINT window_kind_valid CHECK (window_kind IN ('w10min', 'w1h', 'w24h')),
    CONSTRAINT write_count_non_negative CHECK (write_count >= 0),
    CONSTRAINT max_writes_positive CHECK (max_writes > 0)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_write_budget_window
    ON public.anti_dory_write_budget (window_kind, window_start_utc);

CREATE INDEX IF NOT EXISTS idx_write_budget_recent
    ON public.anti_dory_write_budget (window_start_utc DESC);

COMMENT ON TABLE public.anti_dory_write_budget IS
    'Cowork audit bd11733b §5 C3 — Write budget hardcap observable. 3 ventanas: 10min/1h/24h. Cron incrementa write_count tras cada escritura; si > max_writes en cualquier ventana activa, self-disable via UPDATE anti_dory_runtime_flags.';

COMMENT ON COLUMN public.anti_dory_write_budget.max_writes IS
    'Hardcap por ventana. Defaults: w10min=1, w1h=6, w24h=150. Cron lee este valor (no hardcoded en código) para permitir ajustes T1 sin redeploy.';

-- Trigger updated_at
CREATE OR REPLACE FUNCTION anti_dory_write_budget_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_anti_dory_write_budget_updated_at
    ON public.anti_dory_write_budget;

CREATE TRIGGER trg_anti_dory_write_budget_updated_at
    BEFORE UPDATE ON public.anti_dory_write_budget
    FOR EACH ROW
    EXECUTE FUNCTION anti_dory_write_budget_set_updated_at();

-- ============================================================================
-- 3. RLS — Plano de datos cerrado por defecto (Regla Dura #7)
-- ============================================================================
ALTER TABLE public.anti_dory_runtime_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.anti_dory_write_budget   ENABLE ROW LEVEL SECURITY;

-- Drop policies si existen (idempotencia)
DROP POLICY IF EXISTS anti_dory_runtime_flags_service_role_all
    ON public.anti_dory_runtime_flags;
DROP POLICY IF EXISTS anti_dory_write_budget_service_role_all
    ON public.anti_dory_write_budget;

-- Policies service_role-only (modelo canónico Anti-Dory)
CREATE POLICY anti_dory_runtime_flags_service_role_all
    ON public.anti_dory_runtime_flags
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY anti_dory_write_budget_service_role_all
    ON public.anti_dory_write_budget
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Revoke PUBLIC/anon/authenticated
REVOKE ALL ON public.anti_dory_runtime_flags FROM PUBLIC, anon, authenticated;
REVOKE ALL ON public.anti_dory_write_budget   FROM PUBLIC, anon, authenticated;

GRANT SELECT, INSERT, UPDATE ON public.anti_dory_runtime_flags TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.anti_dory_write_budget   TO service_role;

-- ============================================================================
-- 4. RPC rpc_check_shadow_enabled — Lectura atómica del kill switch
-- ============================================================================
-- Diseño: SECURITY DEFINER con search_path explícito (DSC-S-016 hardening).
-- Returns TRUE solo si singleton flag está ON. Default FALSE.

CREATE OR REPLACE FUNCTION public.rpc_check_shadow_enabled()
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_enabled BOOLEAN;
BEGIN
    SELECT shadow_write_enabled
      INTO v_enabled
      FROM public.anti_dory_runtime_flags
     WHERE singleton_lock = 'anti_dory_singleton'
     LIMIT 1;

    RETURN COALESCE(v_enabled, false);
END;
$$;

REVOKE ALL ON FUNCTION public.rpc_check_shadow_enabled() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.rpc_check_shadow_enabled() TO service_role;
GRANT EXECUTE ON FUNCTION public.rpc_check_shadow_enabled() TO anti_dory_writer_role;
GRANT EXECUTE ON FUNCTION public.rpc_check_shadow_enabled() TO anti_dory_reader_role;

COMMENT ON FUNCTION public.rpc_check_shadow_enabled() IS
    'Cowork audit bd11733b §5 C2 — Lee kill switch atómicamente. Cron invoca antes de cada write. Si false → no-op. Default fail-closed.';

-- ============================================================================
-- 5. RPC rpc_increment_write_budget — Increment + check atómico (C3)
-- ============================================================================
-- Diseño:
--   Toma window_start (alineado a 10min) y devuelve:
--     within_budget BOOLEAN
--     write_count_after INTEGER
--     max_writes INTEGER
--     window_kind TEXT
--   Aplica 3 ventanas en una sola transacción. Si CUALQUIERA excede,
--   devuelve within_budget=false y el cron debe self-disable.
--
-- Defaults hardcap:
--   w10min: 1 write máximo (1 heartbeat por ventana de 10 min)
--   w1h:    6 writes máximo
--   w24h:   150 writes máximo

CREATE OR REPLACE FUNCTION public.rpc_increment_write_budget(
    p_now TIMESTAMPTZ DEFAULT now()
)
RETURNS TABLE (
    within_budget BOOLEAN,
    exceeded_window TEXT,
    w10min_count INTEGER,
    w1h_count INTEGER,
    w24h_count INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_w10min_start TIMESTAMPTZ;
    v_w1h_start    TIMESTAMPTZ;
    v_w24h_start   TIMESTAMPTZ;
    v_w10min_count INTEGER;
    v_w1h_count    INTEGER;
    v_w24h_count   INTEGER;
    v_w10min_max   INTEGER;
    v_w1h_max      INTEGER;
    v_w24h_max     INTEGER;
    v_exceeded     TEXT := NULL;
    v_within       BOOLEAN := true;
BEGIN
    -- Alinear ventanas en UTC
    v_w10min_start := date_trunc('hour', p_now AT TIME ZONE 'UTC')
                      + (floor(EXTRACT(MINUTE FROM p_now AT TIME ZONE 'UTC')::int / 10) * 10) * interval '1 minute';
    v_w10min_start := v_w10min_start AT TIME ZONE 'UTC';
    v_w1h_start    := date_trunc('hour', p_now AT TIME ZONE 'UTC') AT TIME ZONE 'UTC';
    v_w24h_start   := date_trunc('day',  p_now AT TIME ZONE 'UTC') AT TIME ZONE 'UTC';

    -- Upsert + increment ventana 10min
    INSERT INTO public.anti_dory_write_budget
        (window_kind, window_start_utc, write_count, max_writes)
    VALUES ('w10min', v_w10min_start, 1, 1)
    ON CONFLICT (window_kind, window_start_utc) DO UPDATE
        SET write_count = anti_dory_write_budget.write_count + 1
    RETURNING write_count, max_writes INTO v_w10min_count, v_w10min_max;

    -- Upsert + increment ventana 1h
    INSERT INTO public.anti_dory_write_budget
        (window_kind, window_start_utc, write_count, max_writes)
    VALUES ('w1h', v_w1h_start, 1, 6)
    ON CONFLICT (window_kind, window_start_utc) DO UPDATE
        SET write_count = anti_dory_write_budget.write_count + 1
    RETURNING write_count, max_writes INTO v_w1h_count, v_w1h_max;

    -- Upsert + increment ventana 24h
    INSERT INTO public.anti_dory_write_budget
        (window_kind, window_start_utc, write_count, max_writes)
    VALUES ('w24h', v_w24h_start, 1, 150)
    ON CONFLICT (window_kind, window_start_utc) DO UPDATE
        SET write_count = anti_dory_write_budget.write_count + 1
    RETURNING write_count, max_writes INTO v_w24h_count, v_w24h_max;

    -- Check budget
    IF v_w10min_count > v_w10min_max THEN
        v_exceeded := 'w10min';
        v_within := false;
    ELSIF v_w1h_count > v_w1h_max THEN
        v_exceeded := 'w1h';
        v_within := false;
    ELSIF v_w24h_count > v_w24h_max THEN
        v_exceeded := 'w24h';
        v_within := false;
    END IF;

    -- Si excedió, auto-trigger self-disable del kill switch
    IF NOT v_within THEN
        UPDATE public.anti_dory_runtime_flags
           SET shadow_write_enabled = false,
               last_disabled_at = now(),
               last_disabled_by = 'self_disable_budget_' || v_exceeded,
               kill_reason = format(
                   'Budget exceeded in window=%s count_after=%s max=%s',
                   v_exceeded,
                   CASE v_exceeded
                       WHEN 'w10min' THEN v_w10min_count
                       WHEN 'w1h'    THEN v_w1h_count
                       WHEN 'w24h'   THEN v_w24h_count
                   END,
                   CASE v_exceeded
                       WHEN 'w10min' THEN v_w10min_max
                       WHEN 'w1h'    THEN v_w1h_max
                       WHEN 'w24h'   THEN v_w24h_max
                   END
               )
         WHERE singleton_lock = 'anti_dory_singleton';
    END IF;

    RETURN QUERY SELECT v_within, v_exceeded, v_w10min_count, v_w1h_count, v_w24h_count;
END;
$$;

REVOKE ALL ON FUNCTION public.rpc_increment_write_budget(TIMESTAMPTZ) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.rpc_increment_write_budget(TIMESTAMPTZ) TO service_role;
GRANT EXECUTE ON FUNCTION public.rpc_increment_write_budget(TIMESTAMPTZ) TO anti_dory_writer_role;

COMMENT ON FUNCTION public.rpc_increment_write_budget(TIMESTAMPTZ) IS
    'Cowork audit bd11733b §5 C3 — Increment atómico + budget check. 3 ventanas (10min/1h/24h). Si excede, self-disable del kill switch automático.';

-- ============================================================================
-- 6. Verificación post-apply binaria
-- ============================================================================
DO $$
DECLARE
    v_flag_rls_enabled    BOOLEAN;
    v_budget_rls_enabled  BOOLEAN;
    v_flag_policy_count   INTEGER;
    v_budget_policy_count INTEGER;
    v_singleton_count     INTEGER;
    v_rpc_check_exists    BOOLEAN;
    v_rpc_increment_exists BOOLEAN;
BEGIN
    -- RLS habilitado en ambas tablas
    SELECT relrowsecurity INTO v_flag_rls_enabled
      FROM pg_class WHERE oid = 'public.anti_dory_runtime_flags'::regclass;
    SELECT relrowsecurity INTO v_budget_rls_enabled
      FROM pg_class WHERE oid = 'public.anti_dory_write_budget'::regclass;

    IF NOT v_flag_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: anti_dory_runtime_flags RLS NOT enabled';
    END IF;
    IF NOT v_budget_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: anti_dory_write_budget RLS NOT enabled';
    END IF;

    -- Al menos una policy por tabla
    SELECT count(*) INTO v_flag_policy_count
      FROM pg_policies
     WHERE schemaname = 'public' AND tablename = 'anti_dory_runtime_flags';
    SELECT count(*) INTO v_budget_policy_count
      FROM pg_policies
     WHERE schemaname = 'public' AND tablename = 'anti_dory_write_budget';

    IF v_flag_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: anti_dory_runtime_flags sin policies';
    END IF;
    IF v_budget_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: anti_dory_write_budget sin policies';
    END IF;

    -- Singleton seed exists
    SELECT count(*) INTO v_singleton_count
      FROM public.anti_dory_runtime_flags
     WHERE singleton_lock = 'anti_dory_singleton';

    IF v_singleton_count <> 1 THEN
        RAISE EXCEPTION 'C2 VIOLATION: singleton row missing or duplicated (count=%)', v_singleton_count;
    END IF;

    -- RPCs exist
    SELECT EXISTS (
        SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid
         WHERE n.nspname = 'public' AND p.proname = 'rpc_check_shadow_enabled'
    ) INTO v_rpc_check_exists;
    SELECT EXISTS (
        SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid
         WHERE n.nspname = 'public' AND p.proname = 'rpc_increment_write_budget'
    ) INTO v_rpc_increment_exists;

    IF NOT v_rpc_check_exists THEN
        RAISE EXCEPTION 'C2 VIOLATION: rpc_check_shadow_enabled does NOT exist';
    END IF;
    IF NOT v_rpc_increment_exists THEN
        RAISE EXCEPTION 'C3 VIOLATION: rpc_increment_write_budget does NOT exist';
    END IF;

    RAISE NOTICE 'D4 0035 post-check OK: RLS=2/2, policies=%/%, singleton=1, rpcs=2/2',
        v_flag_policy_count, v_budget_policy_count;
END $$;

COMMIT;

-- ============================================================================
-- Rollback manual (NO automático):
--   DROP FUNCTION IF EXISTS public.rpc_increment_write_budget(TIMESTAMPTZ);
--   DROP FUNCTION IF EXISTS public.rpc_check_shadow_enabled();
--   DROP TABLE IF EXISTS public.anti_dory_write_budget;
--   DROP TABLE IF EXISTS public.anti_dory_runtime_flags;
--   DROP FUNCTION IF EXISTS anti_dory_write_budget_set_updated_at();
--   DROP FUNCTION IF EXISTS anti_dory_runtime_flags_set_updated_at();
-- ============================================================================
