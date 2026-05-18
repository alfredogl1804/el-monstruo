-- =====================================================================
-- Migration 0039 — La Forja: forja_threads
-- =====================================================================
-- Sprint: LA-FORJA-001 D5.1
-- Autor: Manus E1 (T1)
-- Fecha: 2026-05-17
-- Doctrina: DSC-S-006 v1.1 (RLS desde nacimiento)
-- =====================================================================
-- PROPÓSITO:
-- Conversaciones del tutor adaptativo. Cada hilo tiene un owner
-- (`profile_id` → forja_profiles), un canonical_summary que se refresca
-- cada 1h en sesiones >5h (AC13 Anti-Dory embebido), y metadata de
-- estado de la sesión.
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.forja_threads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID NOT NULL REFERENCES public.forja_profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL DEFAULT 'Hilo sin título',
  status TEXT NOT NULL DEFAULT 'active',
  mode TEXT NOT NULL DEFAULT 'normal',
  canonical_summary TEXT,
  summary_refreshed_at TIMESTAMPTZ,
  message_count INTEGER NOT NULL DEFAULT 0,
  total_tokens_in INTEGER NOT NULL DEFAULT 0,
  total_tokens_out INTEGER NOT NULL DEFAULT 0,
  total_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  archived_at TIMESTAMPTZ
);

-- Whitelist de status
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_threads_status'
  ) THEN
    ALTER TABLE public.forja_threads
      ADD CONSTRAINT chk_forja_threads_status
      CHECK (status IN ('active', 'archived', 'flagged'));
  END IF;
END $$;

-- Whitelist de mode (espejo de profiles)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_threads_mode'
  ) THEN
    ALTER TABLE public.forja_threads
      ADD CONSTRAINT chk_forja_threads_mode
      CHECK (mode IN ('light', 'normal', 'heavy', 'power'));
  END IF;
END $$;

-- Trigger updated_at
DROP TRIGGER IF EXISTS trg_forja_threads_updated_at ON public.forja_threads;
CREATE TRIGGER trg_forja_threads_updated_at
  BEFORE UPDATE ON public.forja_threads
  FOR EACH ROW
  EXECUTE FUNCTION public.fn_set_updated_at();

-- Índices
CREATE INDEX IF NOT EXISTS idx_forja_threads_profile ON public.forja_threads (profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forja_threads_status ON public.forja_threads (status) WHERE status != 'archived';
CREATE INDEX IF NOT EXISTS idx_forja_threads_summary_stale
  ON public.forja_threads (summary_refreshed_at NULLS FIRST)
  WHERE status = 'active';

-- ---------------------------------------------------------------------
-- RLS (DSC-S-006)
-- ---------------------------------------------------------------------
ALTER TABLE public.forja_threads ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all" ON public.forja_threads;
CREATE POLICY "service_role_all"
  ON public.forja_threads
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Authenticated solo ve sus hilos (join transitivo via profile_id → forja_profiles.google_sub)
DROP POLICY IF EXISTS "read_own_threads" ON public.forja_threads;
CREATE POLICY "read_own_threads"
  ON public.forja_threads
  FOR SELECT
  TO authenticated
  USING (
    profile_id IN (
      SELECT id FROM public.forja_profiles
      WHERE google_sub = (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
    )
  );

-- ---------------------------------------------------------------------
COMMENT ON TABLE public.forja_threads IS
  'La Forja D5.1: conversaciones del tutor. canonical_summary se refresca cada 1h en sesiones >5h (AC13 Anti-Dory).';

COMMENT ON COLUMN public.forja_threads.canonical_summary IS
  'Resumen canónico Anti-Dory. Refrescado cada 1h por job en sesiones activas >5h. AC13 SPEC v3.2.';

COMMENT ON COLUMN public.forja_threads.total_usd IS
  'USD acumulado en este hilo (suma de forja_messages.cost_usd). Útil para UI de costos visible al usuario.';

-- =====================================================================
-- FIN DE MIGRACIÓN 0039
-- =====================================================================
