-- =====================================================================
-- Migration 0045 — La Forja: forja_validations
-- =====================================================================
-- Sprint: LA-FORJA-001 D5.1
-- Autor: Manus E1 (T1)
-- Fecha: 2026-05-17
-- Doctrina: DSC-S-006 v1.1 (RLS desde nacimiento)
-- =====================================================================
-- PROPÓSITO:
-- Logs Perplexity citations + tópicos validados cuando el usuario
-- activa requireValidation=true en el tutor (D3.3). Cada fila es una
-- validación individual con citaciones (URLs, snippets, scores).
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.forja_validations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  message_id UUID REFERENCES public.forja_messages(id) ON DELETE CASCADE,
  thread_id UUID NOT NULL REFERENCES public.forja_threads(id) ON DELETE CASCADE,
  profile_id UUID NOT NULL REFERENCES public.forja_profiles(id) ON DELETE CASCADE,
  topic TEXT NOT NULL,
  query TEXT NOT NULL,
  provider TEXT NOT NULL DEFAULT 'perplexity',
  model TEXT,
  citations JSONB NOT NULL DEFAULT '[]'::jsonb,
  citation_count INTEGER NOT NULL DEFAULT 0,
  raw_response JSONB,
  status TEXT NOT NULL DEFAULT 'completed',
  error TEXT,
  cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
  latency_ms INTEGER,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Whitelist de provider
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_validations_provider'
  ) THEN
    ALTER TABLE public.forja_validations
      ADD CONSTRAINT chk_forja_validations_provider
      CHECK (provider IN ('perplexity', 'gemini_grounding', 'manus_search', 'other'));
  END IF;
END $$;

-- Whitelist de status
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_validations_status'
  ) THEN
    ALTER TABLE public.forja_validations
      ADD CONSTRAINT chk_forja_validations_status
      CHECK (status IN ('pending', 'running', 'completed', 'failed'));
  END IF;
END $$;

-- Métricas no-negativas + citation_count consistente
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_validations_metrics'
  ) THEN
    ALTER TABLE public.forja_validations
      ADD CONSTRAINT chk_forja_validations_metrics
      CHECK (
        citation_count >= 0
        AND cost_usd >= 0
        AND (latency_ms IS NULL OR latency_ms >= 0)
      );
  END IF;
END $$;

-- Índices
CREATE INDEX IF NOT EXISTS idx_forja_validations_thread
  ON public.forja_validations (thread_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forja_validations_profile
  ON public.forja_validations (profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forja_validations_message
  ON public.forja_validations (message_id) WHERE message_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_forja_validations_provider_failed
  ON public.forja_validations (provider, created_at DESC) WHERE status = 'failed';

-- ---------------------------------------------------------------------
-- RLS (DSC-S-006)
-- ---------------------------------------------------------------------
ALTER TABLE public.forja_validations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all" ON public.forja_validations;
CREATE POLICY "service_role_all"
  ON public.forja_validations
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "read_own_validations" ON public.forja_validations;
CREATE POLICY "read_own_validations"
  ON public.forja_validations
  FOR SELECT
  TO authenticated
  USING (
    profile_id IN (
      SELECT id FROM public.forja_profiles
      WHERE google_sub = (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
    )
  );

COMMENT ON TABLE public.forja_validations IS
  'La Forja D5.1: validaciones Perplexity citations cuando requireValidation=true (D3.3). 1 fila = 1 query validada.';

COMMENT ON COLUMN public.forja_validations.citations IS
  'Array JSONB: [{url, title, snippet, score}, ...].';

COMMENT ON COLUMN public.forja_validations.citation_count IS
  'Conteo materializado de citations para queries rápidas (sin parsear JSONB).';

-- =====================================================================
-- FIN DE MIGRACIÓN 0045
-- =====================================================================
