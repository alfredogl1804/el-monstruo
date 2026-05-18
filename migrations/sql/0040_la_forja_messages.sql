-- =====================================================================
-- Migration 0040 — La Forja: forja_messages
-- =====================================================================
-- Sprint: LA-FORJA-001 D5.1
-- Autor: Manus E1 (T1)
-- Fecha: 2026-05-17
-- Doctrina: DSC-S-006 v1.1 (RLS desde nacimiento)
-- =====================================================================
-- PROPÓSITO:
-- Mensajes individuales con metadata (modelo, tokens, latencia, modo,
-- citaciones cuando requireValidation=true). Append-only por diseño.
-- =====================================================================

CREATE TABLE IF NOT EXISTS public.forja_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID NOT NULL REFERENCES public.forja_threads(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  model TEXT,
  mode TEXT,
  tokens_in INTEGER NOT NULL DEFAULT 0,
  tokens_out INTEGER NOT NULL DEFAULT 0,
  latency_ms INTEGER,
  cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0,
  require_validation BOOLEAN NOT NULL DEFAULT false,
  citations JSONB,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Whitelist de role
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_messages_role'
  ) THEN
    ALTER TABLE public.forja_messages
      ADD CONSTRAINT chk_forja_messages_role
      CHECK (role IN ('system', 'user', 'assistant', 'tool'));
  END IF;
END $$;

-- Whitelist de mode (cuando aplica)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_messages_mode'
  ) THEN
    ALTER TABLE public.forja_messages
      ADD CONSTRAINT chk_forja_messages_mode
      CHECK (mode IS NULL OR mode IN ('light', 'normal', 'heavy', 'power'));
  END IF;
END $$;

-- Tokens y latencia no-negativos
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_messages_metrics'
  ) THEN
    ALTER TABLE public.forja_messages
      ADD CONSTRAINT chk_forja_messages_metrics
      CHECK (
        tokens_in >= 0
        AND tokens_out >= 0
        AND (latency_ms IS NULL OR latency_ms >= 0)
        AND cost_usd >= 0
      );
  END IF;
END $$;

-- Índices
CREATE INDEX IF NOT EXISTS idx_forja_messages_thread
  ON public.forja_messages (thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_forja_messages_validation
  ON public.forja_messages (thread_id) WHERE require_validation = true;

-- ---------------------------------------------------------------------
-- RLS (DSC-S-006)
-- ---------------------------------------------------------------------
ALTER TABLE public.forja_messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all" ON public.forja_messages;
CREATE POLICY "service_role_all"
  ON public.forja_messages
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "read_own_messages" ON public.forja_messages;
CREATE POLICY "read_own_messages"
  ON public.forja_messages
  FOR SELECT
  TO authenticated
  USING (
    thread_id IN (
      SELECT t.id FROM public.forja_threads t
      JOIN public.forja_profiles p ON p.id = t.profile_id
      WHERE p.google_sub = (current_setting('request.jwt.claims', true)::jsonb ->> 'sub')
    )
  );

COMMENT ON TABLE public.forja_messages IS
  'La Forja D5.1: mensajes append-only del tutor. Metadata: modelo, tokens, latencia, modo, citaciones (cuando requireValidation=true).';

COMMENT ON COLUMN public.forja_messages.citations IS
  'JSONB con array de citaciones Perplexity (url, title, snippet) cuando require_validation=true. NULL cuando false.';

-- =====================================================================
-- FIN DE MIGRACIÓN 0040
-- =====================================================================
