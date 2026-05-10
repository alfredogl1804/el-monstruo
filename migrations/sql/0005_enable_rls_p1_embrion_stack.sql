-- migrations/sql/0005_enable_rls_p1_embrion_stack.sql
--
-- Sprint S-002.5 — Hardening RLS Producción — Tarea 2 (P1 EMBRION STACK)
--
-- Origen: bridge/cowork_to_manus_HILO_EJECUTOR_2_sprint_s002_5_rls_2026_05_10.md
-- Auditoría base: bridge/audit_rls_2026_05_10.md
-- Pre-requisito: 0004_enable_rls_p0_critico.sql aplicado y smoke test PASS
--
-- Objetivo: Activar Row Level Security en las 6 tablas P1 del stack del
--   Embrión y memoria operativa. Solo el kernel (service_role) sigue
--   accediendo. Esta migración EXCLUYE intencionalmente embrion_memoria
--   porque ya tiene RLS habilitado (verificado 2026-05-10).
--
-- Tablas afectadas:
--   1. monstruo_memory       (68 filas)  — memoria a largo plazo
--   2. error_memory          (34 filas)  — historial de errores
--   3. error_memory_patterns (0 filas)   — patrones extraídos
--   4. episodic_memory       (0 filas)   — memoria episódica
--   5. embrion_budget_state  (33 filas)  — estado de presupuesto del embrión
--   6. frontend_sessions     (0 filas)   — sesiones del frontend
--
-- Tablas EXCLUIDAS (NO TOCAR):
--   - embrion_memoria        (1588 filas) — ya tiene relrowsecurity=true
--
-- Estado pre-aplicación verificado 2026-05-10:
--   - 6 tablas con relrowsecurity=false
--   - 0 policies existentes en cada una
--
-- Aplicar vía:
--   python3 ~/.monstruo/sb_sql.py sql -f migrations/sql/0005_enable_rls_p1_embrion_stack.sql
--
-- Rollback (si kernel falla post-aplicación):
--   ALTER TABLE public.monstruo_memory       DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE public.error_memory          DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE public.error_memory_patterns DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE public.episodic_memory       DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE public.embrion_budget_state  DISABLE ROW LEVEL SECURITY;
--   ALTER TABLE public.frontend_sessions     DISABLE ROW LEVEL SECURITY;
--   DROP POLICY IF EXISTS "service_role_only" ON public.monstruo_memory;
--   DROP POLICY IF EXISTS "service_role_only" ON public.error_memory;
--   DROP POLICY IF EXISTS "service_role_only" ON public.error_memory_patterns;
--   DROP POLICY IF EXISTS "service_role_only" ON public.episodic_memory;
--   DROP POLICY IF EXISTS "service_role_only" ON public.embrion_budget_state;
--   DROP POLICY IF EXISTS "service_role_only" ON public.frontend_sessions;

BEGIN;

-- ============================================================
-- monstruo_memory — P1 (memoria a largo plazo)
-- ============================================================
ALTER TABLE public.monstruo_memory ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.monstruo_memory
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.monstruo_memory IS
  'Sprint S-002.5 (2026-05-10): Solo service_role puede leer/escribir. Bloquea anon key.';

-- ============================================================
-- error_memory — P1
-- ============================================================
ALTER TABLE public.error_memory ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.error_memory
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.error_memory IS
  'Sprint S-002.5 (2026-05-10): Solo service_role puede leer/escribir. Bloquea anon key.';

-- ============================================================
-- error_memory_patterns — P1
-- ============================================================
ALTER TABLE public.error_memory_patterns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.error_memory_patterns
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.error_memory_patterns IS
  'Sprint S-002.5 (2026-05-10): Solo service_role puede leer/escribir. Bloquea anon key.';

-- ============================================================
-- episodic_memory — P1
-- ============================================================
ALTER TABLE public.episodic_memory ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.episodic_memory
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.episodic_memory IS
  'Sprint S-002.5 (2026-05-10): Solo service_role puede leer/escribir. Bloquea anon key.';

-- ============================================================
-- embrion_budget_state — P1 (telemetría del embrión)
-- ============================================================
ALTER TABLE public.embrion_budget_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.embrion_budget_state
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.embrion_budget_state IS
  'Sprint S-002.5 (2026-05-10): Solo service_role puede leer/escribir. Bloquea anon key.';

-- ============================================================
-- frontend_sessions — P1 (sesiones del frontend)
-- ============================================================
ALTER TABLE public.frontend_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.frontend_sessions
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.frontend_sessions IS
  'Sprint S-002.5 (2026-05-10): Solo service_role puede leer/escribir. Bloquea anon key.';

COMMIT;
