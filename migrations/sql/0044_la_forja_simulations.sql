-- =====================================================================
-- Migration 0044 — La Forja: forja_simulations
-- =====================================================================
-- Sprint: LA-FORJA-001 D5.1
-- Autor: Manus E1 (T1)
-- Fecha: 2026-05-17
-- Doctrina: DSC-S-006 v1.1 (RLS desde nacimiento)
-- =====================================================================
-- PROPÓSITO:
-- Resultados del Simulador externo (motor en Railway) asociados a hilos.
-- Cada fila es 1 simulación ejecutada (escenario, parámetros, resultados,
-- recomendaciones). El servicio externo se invoca desde forja_actions
-- gate=manus o gate=cuora.
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.forja_simulations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID REFERENCES public.forja_threads(id) ON DELETE SET NULL,
  profile_id UUID NOT NULL REFERENCES public.forja_profiles(id) ON DELETE CASCADE,
  external_id TEXT,
  scenario_name TEXT NOT NULL,
  scenario_type TEXT NOT NULL,
  inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
  results JSONB,
  recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
  status TEXT NOT NULL DEFAULT 'pending',
  error TEXT,
  cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
  duration_ms INTEGER,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Whitelist de scenario_type (alineado al simulador-escenarios-ia skill)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_simulations_type'
  ) THEN
    ALTER TABLE public.forja_simulations
      ADD CONSTRAINT chk_forja_simulations_type
      CHECK (scenario_type IN (
        'electoral',
        'financiero',
        'crisis',
        'legal',
        'supply_chain',
        'tecnologia',
        'marketing',
        'inmobiliario',
        'estrategico',
        'personal',
        'other'
      ));
  END IF;
END $$;

-- Whitelist de status
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_simulations_status'
  ) THEN
    ALTER TABLE public.forja_simulations
      ADD CONSTRAINT chk_forja_simulations_status
      CHECK (status IN ('pending', 'running', 'completed', 'failed'));
  END IF;
END $$;

-- Cost no-negativo
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_simulations_cost'
  ) THEN
    ALTER TABLE public.forja_simulations
      ADD CONSTRAINT chk_forja_simulations_cost
      CHECK (cost_usd >= 0 AND (duration_ms IS NULL OR duration_ms >= 0));
  END IF;
END $$;

-- Índices
CREATE INDEX IF NOT EXISTS idx_forja_simulations_thread
  ON public.forja_simulations (thread_id, created_at DESC) WHERE thread_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_forja_simulations_profile
  ON public.forja_simulations (profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forja_simulations_external
  ON public.forja_simulations (external_id) WHERE external_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_forja_simulations_type
  ON public.forja_simulations (scenario_type, status);

-- ---------------------------------------------------------------------
-- RLS (DSC-S-006)
-- ---------------------------------------------------------------------
ALTER TABLE public.forja_simulations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all" ON public.forja_simulations;
CREATE POLICY "service_role_all"
  ON public.forja_simulations
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "read_own_simulations" ON public.forja_simulations;
CREATE POLICY "read_own_simulations"
  ON public.forja_simulations
  FOR SELECT
  TO authenticated
  USING (
    profile_id IN (
      SELECT id FROM public.forja_profiles
      WHERE google_sub = (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
    )
  );

COMMENT ON TABLE public.forja_simulations IS
  'La Forja D5.1: simulaciones del motor externo en Railway. external_id ancla a la corrida del simulador. Resultado en JSONB.';

COMMENT ON COLUMN public.forja_simulations.scenario_type IS
  'Whitelist alineada al skill simulador-escenarios-ia (10 dominios + other).';

-- =====================================================================
-- FIN DE MIGRACIÓN 0044
-- =====================================================================
