-- =============================================================================
-- Migración 0006 — Sprint S-002.6 — Tarea 2
-- Policy explícita en embrion_memoria (cierra deuda detectada en S-002.5)
-- =============================================================================
--
-- Contexto:
--   embrion_memoria tenía rls=true / num_policies=0 desde antes de S-002.5.
--   Esto significaba que la tabla dependía implícitamente del bypass de
--   service_role (Postgres permite bypassrls al rol service_role por defecto).
--   El estado funcionaba pero era frágil: cualquier rol nuevo con privilegios
--   sin bypassrls quedaría bloqueado sin política explícita.
--
-- Objetivo:
--   Agregar policy "service_role_only" explícita para auditabilidad y para
--   alinear con el patrón canónico de las 8 tablas activadas en S-002.5.
--
-- Cumplimiento DSC:
--   - DSC-S-006 (RLS por defecto en tablas nuevas): policy explícita = OK
--   - DSC-S-001..005: cero credenciales en código, solo SQL
--   - DSC-G-008 v2: archivo entregado para audit de Cowork antes del cierre
--
-- Atomicidad:
--   Transacción BEGIN/COMMIT. Rollback inmediato si falla.
--
-- Smoke test post-aplicación obligatorio (cowork_bridge):
--   INSERT/SELECT/DELETE de un mensaje de prueba con
--   hilo_origen='cowork_audit_test_s002_6'.
--
-- Aplicar con:
--   python3 ~/.monstruo/sb_sql.py sql -f migrations/sql/0006_embrion_memoria_explicit_policy.sql
-- =============================================================================

BEGIN;

-- Crear policy explícita para service_role
CREATE POLICY "service_role_only"
  ON public.embrion_memoria
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

COMMENT ON POLICY "service_role_only" ON public.embrion_memoria IS
  'Sprint S-002.6 (2026-05-10): Policy explicita para auditabilidad. Cierra deuda detectada en S-002.5 (rls=true / num_policies=0). DSC-S-006 regla 1 (RLS por defecto). Bloquea anon/authenticated.';

COMMIT;
