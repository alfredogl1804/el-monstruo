-- =====================================================================
-- Migration 0043 — La Forja: forja_telemetry
-- =====================================================================
-- Sprint: LA-FORJA-001 D5.1
-- Autor: Manus E1 (T1)
-- Fecha: 2026-05-17
-- Doctrina: DSC-S-006 v1.1 (RLS desde nacimiento)
-- =====================================================================
-- PROPÓSITO:
-- Test Bench (SPEC v3.2 §7 AC11/AC12): captura señales del cliente
-- (confusión, simplificación, abandono, completitud) con clasificador
-- semántico Gemini Flash (intent + confidence) sobre cada mensaje.
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.forja_telemetry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID REFERENCES public.forja_threads(id) ON DELETE CASCADE,
  message_id UUID REFERENCES public.forja_messages(id) ON DELETE SET NULL,
  profile_id UUID NOT NULL REFERENCES public.forja_profiles(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  subject TEXT,
  evidence TEXT,
  classifier_score NUMERIC(4, 3),
  intent TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Whitelist de eventos canónicos Test Bench (SPEC v3.2 §7 AC11/AC12)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_telemetry_event'
  ) THEN
    ALTER TABLE public.forja_telemetry
      ADD CONSTRAINT chk_forja_telemetry_event
      CHECK (event IN (
        'confusion_detected',
        'simplification_requested',
        'abandonment_detected',
        'completion_signal',
        'invalid_state_transition',
        'family_relation_risk',
        'budget_warning',
        'budget_cap_hit',
        'tutor_validation_toggled',
        'mode_changed',
        'session_long',
        'summary_refreshed',
        'other'
      ));
  END IF;
END $$;

-- Score 0-1 cuando aplica
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_telemetry_score_range'
  ) THEN
    ALTER TABLE public.forja_telemetry
      ADD CONSTRAINT chk_forja_telemetry_score_range
      CHECK (classifier_score IS NULL OR (classifier_score >= 0 AND classifier_score <= 1));
  END IF;
END $$;

-- Índices
CREATE INDEX IF NOT EXISTS idx_forja_telemetry_thread_event
  ON public.forja_telemetry (thread_id, event, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forja_telemetry_profile_recent
  ON public.forja_telemetry (profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forja_telemetry_confusion_recent
  ON public.forja_telemetry (thread_id, created_at DESC)
  WHERE event = 'confusion_detected';
CREATE INDEX IF NOT EXISTS idx_forja_telemetry_subject
  ON public.forja_telemetry (subject, created_at DESC) WHERE subject IS NOT NULL;

-- ---------------------------------------------------------------------
-- RLS (DSC-S-006)
-- ---------------------------------------------------------------------
ALTER TABLE public.forja_telemetry ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all" ON public.forja_telemetry;
CREATE POLICY "service_role_all"
  ON public.forja_telemetry
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "read_own_telemetry" ON public.forja_telemetry;
CREATE POLICY "read_own_telemetry"
  ON public.forja_telemetry
  FOR SELECT
  TO authenticated
  USING (
    profile_id IN (
      SELECT id FROM public.forja_profiles
      WHERE google_sub = (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
    )
  );

COMMENT ON TABLE public.forja_telemetry IS
  'La Forja D5.1: Test Bench. Eventos canónicos AC11/AC12 con clasificador semántico Gemini Flash.';

COMMENT ON COLUMN public.forja_telemetry.classifier_score IS
  'Confianza 0-1 del clasificador semántico. AC12: confusion_detected con score>=0.7 → row.';

COMMENT ON COLUMN public.forja_telemetry.subject IS
  'Subject opcional del evento (ej: "family_relation_risk" para R9 SPEC v3.2 §9).';

-- =====================================================================
-- FIN DE MIGRACIÓN 0043
-- =====================================================================
