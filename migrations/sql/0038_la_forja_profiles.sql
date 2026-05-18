-- =====================================================================
-- Migration 0038 — La Forja: forja_profiles
-- =====================================================================
-- Sprint: LA-FORJA-001 D5.1
-- Autor: Manus E1 (T1)
-- Fecha: 2026-05-17
-- Doctrina: DSC-S-006 v1.1 (RLS desde nacimiento) + DSC-S-007 (naming) + DSC-LF-009 (auth canónica)
-- =====================================================================
-- PROPÓSITO:
-- Identidad de usuarios de La Forja con whitelist de roles canónicos
-- (`t1_alfredo` | `t1_padre` | `user`). Anclado a `google_sub` (Google
-- OAuth subject claim) que es identificador único e inmutable.
--
-- Patrón de auth: el JWT firmado por `api/src/lib/jwt.ts` lleva
-- `sub = google_sub`, `role`, `name`, `email`. Backend verifica JWT y
-- consulta `forja_profiles` para metadata adicional. RLS canónica:
-- service_role escribe, lectura propia para auth users (AC2 SPEC v3.2).
-- =====================================================================

-- ---------------------------------------------------------------------
-- Schema base
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.forja_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  google_sub TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL,
  display_name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user',
  avatar_url TEXT,
  preferred_mode TEXT NOT NULL DEFAULT 'normal',
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ
);

-- Whitelist binaria de roles canónicos
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_profiles_role'
  ) THEN
    ALTER TABLE public.forja_profiles
      ADD CONSTRAINT chk_forja_profiles_role
      CHECK (role IN ('t1_alfredo', 't1_padre', 'user'));
  END IF;
END $$;

-- Whitelist de modos del tutor (espejo del frontend D3.3)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chk_forja_profiles_mode'
  ) THEN
    ALTER TABLE public.forja_profiles
      ADD CONSTRAINT chk_forja_profiles_mode
      CHECK (preferred_mode IN ('light', 'normal', 'heavy', 'power'));
  END IF;
END $$;

-- Trigger updated_at automático (reusa fn_set_updated_at existente)
DROP TRIGGER IF EXISTS trg_forja_profiles_updated_at ON public.forja_profiles;
CREATE TRIGGER trg_forja_profiles_updated_at
  BEFORE UPDATE ON public.forja_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.fn_set_updated_at();

-- Índices
CREATE INDEX IF NOT EXISTS idx_forja_profiles_email ON public.forja_profiles (email);
CREATE INDEX IF NOT EXISTS idx_forja_profiles_role ON public.forja_profiles (role);
CREATE INDEX IF NOT EXISTS idx_forja_profiles_last_seen ON public.forja_profiles (last_seen_at DESC NULLS LAST);

-- ---------------------------------------------------------------------
-- RLS por defecto (DSC-S-006)
-- ---------------------------------------------------------------------
ALTER TABLE public.forja_profiles ENABLE ROW LEVEL SECURITY;

-- Policy 1: service_role escribe/lee todo (operaciones de servidor)
DROP POLICY IF EXISTS "service_role_all" ON public.forja_profiles;
CREATE POLICY "service_role_all"
  ON public.forja_profiles
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Policy 2: read_own_profile — un usuario autenticado solo ve su propio perfil
-- Requiere que el JWT del usuario tenga `sub` = google_sub. Validación E2E en D5.3 (AC2).
DROP POLICY IF EXISTS "read_own_profile" ON public.forja_profiles;
CREATE POLICY "read_own_profile"
  ON public.forja_profiles
  FOR SELECT
  TO authenticated
  USING (google_sub = (current_setting('request.jwt.claims', true)::jsonb ->> 'sub'));

-- ---------------------------------------------------------------------
-- COMMENTS
-- ---------------------------------------------------------------------
COMMENT ON TABLE public.forja_profiles IS
  'La Forja D5.1: perfiles de usuarios anclados a Google OAuth sub. RLS: service_role total, authenticated lee solo su propio perfil (AC2).';

COMMENT ON COLUMN public.forja_profiles.google_sub IS
  'Google OAuth subject claim (sub). Identificador único inmutable. Match contra JWT.sub firmado por api/src/lib/jwt.ts.';

COMMENT ON COLUMN public.forja_profiles.role IS
  'Whitelist binaria: t1_alfredo (owner) | t1_padre (Cliente Cero) | user (futuros). DSC-LF-009.';

COMMENT ON COLUMN public.forja_profiles.preferred_mode IS
  'Modo del tutor preferido por el usuario: light | normal | heavy | power. Espejo del frontend D3.3.';

-- =====================================================================
-- FIN DE MIGRACIÓN 0038
-- =====================================================================
