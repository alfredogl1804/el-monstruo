-- =============================================================================
-- Migración 0007 — Sprint S-002.6 — Tarea 3
-- RLS sobre 3 tablas creadas DESPUÉS de S-002.5 (delegadas por Cowork)
-- =============================================================================
--
-- Tablas afectadas:
--   1. embrion_write_proposals   (PR #42 — cola HITL para escrituras del kernel)
--   2. catastro_agentes          (Sprint 88 — macroárea AGENTES, 84 productos)
--   3. catastro_tronos_agentes   (Sprint 88 — vista materializada de tronos)
--
-- Patrón: service_role_only (idéntico a S-002.5 migración 0004 y 0005).
--
-- Nota sobre vistas materializadas:
--   En PostgreSQL 17, las vistas materializadas (relkind='m') NO soportan
--   RLS directamente porque no son tablas. Sin embargo, REFRESH MATERIALIZED
--   VIEW se ejecuta con los privilegios del propietario y materializa el
--   resultado de la query subyacente. Si la query lee de catastro_agentes
--   (que sí tiene RLS), el refresh ejecutado por service_role bypass-ea RLS y
--   materializa todos los datos. Lecturas a la vista por anon devuelven el
--   contenido materializado (igual que cualquier vista). Por tanto, la
--   protección efectiva ocurre vía RLS en las tablas base + control de
--   GRANT SELECT en la vista. Aplicaremos GRANT REVOKE sobre catastro_tronos_agentes
--   para anon (DSC-S-006 espíritu).
--
-- Atomicidad: BEGIN/COMMIT.
-- Smoke test post-aplicación obligatorio: kernel /v1/health + 19 endpoints.
--
-- Aplicar:
--   python3 ~/.monstruo/sb_sql.py sql -f migrations/sql/0007_rls_tablas_post_s002_5.sql
-- =============================================================================

BEGIN;

-- ──────────────────────────────────────────────────────────────────────────
-- 1. embrion_write_proposals (tabla normal, RLS aplicable directamente)
-- ──────────────────────────────────────────────────────────────────────────
ALTER TABLE public.embrion_write_proposals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.embrion_write_proposals
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.embrion_write_proposals IS
  'Sprint S-002.6 (2026-05-10): cola HITL del PR #42. Bloquea anon. DSC-S-006.';

-- ──────────────────────────────────────────────────────────────────────────
-- 2. catastro_agentes (tabla normal del Sprint 88)
-- ──────────────────────────────────────────────────────────────────────────
ALTER TABLE public.catastro_agentes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.catastro_agentes
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.catastro_agentes IS
  'Sprint S-002.6 (2026-05-10): Macroarea AGENTES Sprint 88. Bloquea anon. DSC-S-006.';

-- ──────────────────────────────────────────────────────────────────────────
-- 3. catastro_tronos_agentes (vista materializada — proteger via REVOKE)
-- ──────────────────────────────────────────────────────────────────────────
-- Las vistas materializadas no soportan ENABLE ROW LEVEL SECURITY.
-- Protegemos vía REVOKE de privilegios sobre los roles públicos.
REVOKE ALL ON public.catastro_tronos_agentes FROM PUBLIC;
REVOKE ALL ON public.catastro_tronos_agentes FROM anon;
REVOKE ALL ON public.catastro_tronos_agentes FROM authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.catastro_tronos_agentes TO service_role;

COMMENT ON MATERIALIZED VIEW public.catastro_tronos_agentes IS
  'Sprint S-002.6 (2026-05-10): vista materializada Sprint 88. Proteccion via REVOKE PUBLIC + GRANT service_role. Equivalente a service_role_only para tablas. DSC-S-006.';

COMMIT;
