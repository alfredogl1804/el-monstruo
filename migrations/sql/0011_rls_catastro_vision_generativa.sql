-- =============================================================================
-- Migracion 0011 - P0 RLS Fix - catastro_vision_generativa
-- =============================================================================
-- Contexto: Tabla nacida sin RLS (regresión post-S-002.6). Estado pre-fix:
--   - rowsecurity: false
--   - policy_count: 0
--   - row_count: 38 expuestos a rol `anon`
--   - Origen: macroarea vision_generativa (Sprint 88 Catastro), creada por hilo
--     Catastro vía cliente Postgres directo, bypaseando linter pre-commit
--     scripts/_check_rls_default.py (que solo escanea archivos de migración en
--     PR, no detecta tablas creadas fuera del flujo de migraciones versionadas).
--
-- Patrón: service_role_only (idéntico a las 117 tablas migradas en 0004-0008).
-- Atomicidad: BEGIN/COMMIT. Smoke test post-aplicación obligatorio.
-- DSC-S-006 v1.1 (RLS default), DSC-G-008 v2 (audit pre-cierre).
-- Sprint: P0 RLS Fix 2026-05-11.
-- =============================================================================

BEGIN;

-- 1/1: catastro_vision_generativa
-- Habilitar RLS y crear policy service_role_only siguiendo el patrón canónico
-- usado en las otras 6 tablas catastro_* hermanas (catastro_agentes ya tiene
-- ese patrón explícito).
ALTER TABLE public.catastro_vision_generativa ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only" ON public.catastro_vision_generativa
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.catastro_vision_generativa IS
  'P0 RLS Fix (2026-05-11): regression post-S-002.6. Tabla nacida sin RLS por bypass del linter. DSC-S-006.';

COMMIT;
