-- migrations/sql/0004_enable_rls_p0_critico.sql
--
-- Sprint S-002.5 — Hardening RLS Producción — Tarea 1 (P0 CRÍTICO)
--
-- Origen: bridge/cowork_to_manus_HILO_EJECUTOR_2_sprint_s002_5_rls_2026_05_10.md
-- Auditoría base: bridge/audit_rls_2026_05_10.md
--
-- Objetivo: Activar Row Level Security en las 2 tablas P0 con datos
--   sensibles (credenciales y datos personales) para bloquear acceso
--   vía anon key. Solo el kernel (que usa service_role) sigue accediendo.
--
-- Tablas afectadas:
--   1. tool_secrets   (8 filas) — nombre indica credenciales/keys
--   2. user_dossier   (1 fila)  — datos personales del owner
--
-- Estado pre-aplicación verificado 2026-05-10:
--   - Ambas tablas tienen relrowsecurity=false
--   - 0 policies existentes en ambas
--
-- Aplicar vía:
--   psql "$SUPABASE_DB_URL" -f migrations/sql/0004_enable_rls_p0_critico.sql
-- O vía Management API:
--   python3 ~/.monstruo/sb_sql.py sql -f migrations/sql/0004_enable_rls_p0_critico.sql
--
-- Rollback (si kernel falla post-aplicación):
--   ALTER TABLE public.tool_secrets DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE public.user_dossier DISABLE ROW LEVEL SECURITY;
--   DROP POLICY IF EXISTS "service_role_only" ON public.tool_secrets;
--   DROP POLICY IF EXISTS "service_role_only" ON public.user_dossier;

BEGIN;

-- ============================================================
-- tool_secrets — P0 CRÍTICO
-- ============================================================
ALTER TABLE public.tool_secrets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.tool_secrets
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.tool_secrets IS
  'Sprint S-002.5 (2026-05-10): Solo service_role puede leer/escribir. Bloquea anon key.';

-- ============================================================
-- user_dossier — P0 (datos personales)
-- ============================================================
ALTER TABLE public.user_dossier ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.user_dossier
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.user_dossier IS
  'Sprint S-002.5 (2026-05-10): Solo service_role puede leer/escribir. Bloquea anon key.';

COMMIT;
