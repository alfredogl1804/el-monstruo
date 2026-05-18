-- =====================================================================
-- Migration 0046 — La Forja: forja_budget
-- =====================================================================
-- Sprint: LA-FORJA-001 D5.1
-- Autor: Manus E1 (T1)
-- Fecha: 2026-05-17
-- Doctrina: DSC-S-006 v1.1 (RLS desde nacimiento)
-- =====================================================================
-- PROPÓSITO:
-- Tracking USD/mes/usuario para rate limit cap $50 (SPEC v3.2 §11).
-- Una fila por (profile_id, period_start). period_start es siempre el
-- primer día del mes UTC. La columna mode_breakdown lleva un objeto
-- JSONB con {light, normal, heavy, power} para reporting.
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.forja_budget (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES public.forja_profiles(id) ON DELETE CASCADE,
  period_start DATE NOT NULL,
  spent_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
  cap_usd NUMERIC(10, 2) NOT NULL DEFAULT 50.00,
  mode_breakdown JSONB NOT NULL DEFAULT '{"light": 0, "normal": 0, "heavy": 0, "power": 0}'::jsonb,
  message_count INTEGER NOT NULL DEFAULT 0,
  validation_count INTEGER NOT NULL DEFAULT 0,
  warning_sent_at TIMESTAMPTZ,
  cap_hit_at TIMESTAMPTZ,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (profile_id, period_start)
);

-- Cap y spent no-negativos, period_start = primer día del mes
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_budget_metrics'
  ) THEN
    ALTER TABLE public.forja_budget
      ADD CONSTRAINT chk_forja_budget_metrics
      CHECK (
        spent_usd >= 0
        AND cap_usd > 0
        AND message_count >= 0
        AND validation_count >= 0
        AND EXTRACT(DAY FROM period_start) = 1
      );
  END IF;
END $$;

-- Trigger updated_at
DROP TRIGGER IF EXISTS trg_forja_budget_updated_at ON public.forja_budget;
CREATE TRIGGER trg_forja_budget_updated_at
  BEFORE UPDATE ON public.forja_budget
  FOR EACH ROW
  EXECUTE FUNCTION public.fn_set_updated_at();

-- Índices
CREATE INDEX IF NOT EXISTS idx_forja_budget_profile_period
  ON public.forja_budget (profile_id, period_start DESC);
CREATE INDEX IF NOT EXISTS idx_forja_budget_cap_hit
  ON public.forja_budget (period_start DESC) WHERE cap_hit_at IS NOT NULL;

-- ---------------------------------------------------------------------
-- RLS (DSC-S-006)
-- ---------------------------------------------------------------------
ALTER TABLE public.forja_budget ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all" ON public.forja_budget;
CREATE POLICY "service_role_all"
  ON public.forja_budget
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "read_own_budget" ON public.forja_budget;
CREATE POLICY "read_own_budget"
  ON public.forja_budget
  FOR SELECT
  TO authenticated
  USING (
    profile_id IN (
      SELECT id FROM public.forja_profiles
      WHERE google_sub = (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
    )
  );

COMMENT ON TABLE public.forja_budget IS
  'La Forja D5.1: tracking USD/mes/usuario. Cap default $50 (SPEC v3.2 §11). UNIQUE(profile_id, period_start). period_start = día 1 del mes.';

COMMENT ON COLUMN public.forja_budget.mode_breakdown IS
  'Reparto de spent_usd por modo: {light, normal, heavy, power}. Útil para UX y reporting.';

COMMENT ON COLUMN public.forja_budget.warning_sent_at IS
  'Timestamp cuando se envió la advertencia 80% al usuario. NULL = no enviada.';

COMMENT ON COLUMN public.forja_budget.cap_hit_at IS
  'Timestamp cuando se alcanzó el cap. NULL = no hit. Backend debe rechazar requests cuando este campo no es NULL.';

-- =====================================================================
-- FIN DE MIGRACIÓN 0046
-- =====================================================================
