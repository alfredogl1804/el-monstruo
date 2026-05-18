-- =====================================================================
-- Migration 0042 — La Forja: forja_actions
-- =====================================================================
-- Sprint: LA-FORJA-001 D5.1
-- Autor: Manus E1 (T1)
-- Fecha: 2026-05-17
-- Doctrina: DSC-S-006 v1.1 (RLS desde nacimiento)
-- =====================================================================
-- PROPÓSITO:
-- Acciones disparadas a las 5 puertas de comunicación (Manus, Cowork,
-- Cuora, Supabase, GitHub) con resultado y latencia. Append-only.
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.forja_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sprint_id UUID REFERENCES public.forja_sprints(id) ON DELETE SET NULL,
  thread_id UUID REFERENCES public.forja_threads(id) ON DELETE SET NULL,
  profile_id UUID NOT NULL REFERENCES public.forja_profiles(id) ON DELETE CASCADE,
  gate TEXT NOT NULL,
  action_type TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  status TEXT NOT NULL DEFAULT 'pending',
  result JSONB,
  error TEXT,
  latency_ms INTEGER,
  cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Whitelist 5 puertas canónicas (SPEC v3.2 §2.1)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_actions_gate'
  ) THEN
    ALTER TABLE public.forja_actions
      ADD CONSTRAINT chk_forja_actions_gate
      CHECK (gate IN ('manus', 'cowork', 'cuora', 'supabase', 'github'));
  END IF;
END $$;

-- Whitelist de status
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_actions_status'
  ) THEN
    ALTER TABLE public.forja_actions
      ADD CONSTRAINT chk_forja_actions_status
      CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'));
  END IF;
END $$;

-- Métricas no-negativas
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_actions_metrics'
  ) THEN
    ALTER TABLE public.forja_actions
      ADD CONSTRAINT chk_forja_actions_metrics
      CHECK (
        (latency_ms IS NULL OR latency_ms >= 0)
        AND cost_usd >= 0
      );
  END IF;
END $$;

-- Índices
CREATE INDEX IF NOT EXISTS idx_forja_actions_sprint
  ON public.forja_actions (sprint_id, started_at DESC) WHERE sprint_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_forja_actions_profile_recent
  ON public.forja_actions (profile_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_forja_actions_failed
  ON public.forja_actions (started_at DESC) WHERE status = 'failed';
CREATE INDEX IF NOT EXISTS idx_forja_actions_gate
  ON public.forja_actions (gate, status);

-- ---------------------------------------------------------------------
-- RLS (DSC-S-006)
-- ---------------------------------------------------------------------
ALTER TABLE public.forja_actions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all" ON public.forja_actions;
CREATE POLICY "service_role_all"
  ON public.forja_actions
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "read_own_actions" ON public.forja_actions;
CREATE POLICY "read_own_actions"
  ON public.forja_actions
  FOR SELECT
  TO authenticated
  USING (
    profile_id IN (
      SELECT id FROM public.forja_profiles
      WHERE google_sub = (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
    )
  );

COMMENT ON TABLE public.forja_actions IS
  'La Forja D5.1: acciones a las 5 puertas (manus, cowork, cuora, supabase, github). Append-only. Errores logueados en error column.';

COMMENT ON COLUMN public.forja_actions.gate IS
  'Whitelist binaria de las 5 puertas canónicas SPEC v3.2 §2.1.';

-- =====================================================================
-- FIN DE MIGRACIÓN 0042
-- =====================================================================
