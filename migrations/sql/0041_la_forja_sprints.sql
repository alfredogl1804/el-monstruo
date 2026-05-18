-- =====================================================================
-- Migration 0041 — La Forja: forja_sprints
-- =====================================================================
-- Sprint: LA-FORJA-001 D5.1
-- Autor: Manus E1 (T1)
-- Fecha: 2026-05-17
-- Doctrina: DSC-S-006 v1.1 (RLS desde nacimiento)
-- =====================================================================
-- PROPÓSITO:
-- Sprints diseñados desde la app, con la máquina de estados canónica
-- de 8 estados (SPEC v3.2 §4): proposed → confirmed → executing →
-- waiting_audit → audited → merged. Estados terminales: blocked, archived.
-- Transiciones inválidas son bloqueadas en backend (AC10).
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.forja_sprints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID REFERENCES public.forja_threads(id) ON DELETE SET NULL,
  profile_id UUID NOT NULL REFERENCES public.forja_profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'proposed',
  goal TEXT,
  acceptance_criteria JSONB NOT NULL DEFAULT '[]'::jsonb,
  estimated_usd NUMERIC(10, 2),
  spent_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
  proposed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  confirmed_at TIMESTAMPTZ,
  executing_at TIMESTAMPTZ,
  audit_requested_at TIMESTAMPTZ,
  audited_at TIMESTAMPTZ,
  merged_at TIMESTAMPTZ,
  blocked_at TIMESTAMPTZ,
  archived_at TIMESTAMPTZ,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Whitelist canónica de 8 estados (SPEC v3.2 §4)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_sprints_status'
  ) THEN
    ALTER TABLE public.forja_sprints
      ADD CONSTRAINT chk_forja_sprints_status
      CHECK (status IN (
        'proposed',
        'confirmed',
        'executing',
        'waiting_audit',
        'audited',
        'merged',
        'blocked',
        'archived'
      ));
  END IF;
END $$;

-- Trigger updated_at
DROP TRIGGER IF EXISTS trg_forja_sprints_updated_at ON public.forja_sprints;
CREATE TRIGGER trg_forja_sprints_updated_at
  BEFORE UPDATE ON public.forja_sprints
  FOR EACH ROW
  EXECUTE FUNCTION public.fn_set_updated_at();

-- Índices
CREATE INDEX IF NOT EXISTS idx_forja_sprints_profile
  ON public.forja_sprints (profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forja_sprints_status
  ON public.forja_sprints (status) WHERE status NOT IN ('archived', 'merged');
CREATE INDEX IF NOT EXISTS idx_forja_sprints_thread
  ON public.forja_sprints (thread_id) WHERE thread_id IS NOT NULL;

-- ---------------------------------------------------------------------
-- RLS (DSC-S-006)
-- ---------------------------------------------------------------------
ALTER TABLE public.forja_sprints ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all" ON public.forja_sprints;
CREATE POLICY "service_role_all"
  ON public.forja_sprints
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "read_own_sprints" ON public.forja_sprints;
CREATE POLICY "read_own_sprints"
  ON public.forja_sprints
  FOR SELECT
  TO authenticated
  USING (
    profile_id IN (
      SELECT id FROM public.forja_profiles
      WHERE google_sub = (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
    )
  );

COMMENT ON TABLE public.forja_sprints IS
  'La Forja D5.1: sprints con máquina de estados de 8 estados (SPEC v3.2 §4). Transiciones inválidas bloqueadas en backend Hono (AC10).';

COMMENT ON COLUMN public.forja_sprints.status IS
  'Whitelist 8 estados: proposed → confirmed → executing → waiting_audit → audited → merged. Terminales: blocked, archived.';

COMMENT ON COLUMN public.forja_sprints.acceptance_criteria IS
  'Array JSONB de ACs binarios verificables (SPEC v3.2 §7 patrón).';

-- =====================================================================
-- FIN DE MIGRACIÓN 0041
-- =====================================================================
