-- ============================================================================
-- Migration 0033 — Anti-Dory GRANTs role-membership a service_role
-- ============================================================================
-- Sprint:        MANUS-ANTI-DORY-002 v1 FASE D2
-- Created:       2026-05-14
-- Author:        Manus (Ejecutor 1) bajo autoridad delegada T1 Alfredo Góngora
-- Doctrina:      DSC-S-006 v1.1 (RLS por defecto) + segregación de roles
-- Depends on:    0029 (runtime_events), 0030 (thread_snapshots),
--                0031 (project_runtime_heads), 0032 (RPCs + roles segregados)
-- ============================================================================
-- Contexto:
--   La migration 0032 creó los roles segregados `anti_dory_writer_role` y
--   `anti_dory_reader_role` (NOLOGIN, no asignables a usuarios directos) y
--   emitió GRANT EXECUTE de los 5 RPCs a estos roles + service_role canónico.
--
--   Falta el último eslabón: que `service_role` (el role de Supabase usado
--   por el cliente HTTP del kernel) PUEDA ASUMIR los permisos de los roles
--   segregados vía membresía (`GRANT role TO role`). Sin esta migration,
--   los RPCs ejecutados como service_role llaman a SECURITY DEFINER que
--   re-asume role segregado, pero el modelo de membresía explícita queda
--   incompleto y la auditoría de permisos `pg_has_role` falla.
--
--   Esta migration cierra ese gap. Es idempotente (DO block con guard
--   `pg_has_role(...)` previo a GRANT) y verifica binariamente que la
--   membresía quedó establecida (RAISE EXCEPTION si no).
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. GRANT membership: service_role hereda permisos de roles segregados
-- ============================================================================
-- Patrón: GRANT <member_role> TO <inheriting_role>
-- Esto permite que cuando service_role ejecuta un RPC SECURITY DEFINER,
-- pg_has_role(service_role, anti_dory_writer_role, 'MEMBER') sea TRUE.
-- También permite GRANT EXECUTE / SELECT futuros a los roles segregados
-- sin requerir GRANT redundante a service_role.

DO $$
BEGIN
    -- Pre-verificación: roles deben existir (creados en 0032)
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anti_dory_writer_role') THEN
        RAISE EXCEPTION 'DSC-S-012 VIOLATION: role anti_dory_writer_role NO existe (corre 0032 primero)';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anti_dory_reader_role') THEN
        RAISE EXCEPTION 'DSC-S-012 VIOLATION: role anti_dory_reader_role NO existe (corre 0032 primero)';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'service_role') THEN
        RAISE EXCEPTION 'DSC-S-012 VIOLATION: role service_role NO existe (canonical Supabase)';
    END IF;
    RAISE NOTICE 'D2 pre-check OK: 3 roles existen';
END $$;

-- GRANT membership idempotente (Postgres es idempotente para GRANT TO ROLE)
GRANT anti_dory_writer_role TO service_role;
GRANT anti_dory_reader_role TO service_role;

-- ============================================================================
-- 2. Verificación post-apply binaria (RAISE EXCEPTION si membresía falla)
-- ============================================================================
DO $$
DECLARE
    v_writer_member BOOLEAN;
    v_reader_member BOOLEAN;
BEGIN
    SELECT pg_has_role('service_role', 'anti_dory_writer_role', 'MEMBER')
      INTO v_writer_member;
    SELECT pg_has_role('service_role', 'anti_dory_reader_role', 'MEMBER')
      INTO v_reader_member;

    IF NOT v_writer_member THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: service_role NO es miembro de anti_dory_writer_role';
    END IF;
    IF NOT v_reader_member THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: service_role NO es miembro de anti_dory_reader_role';
    END IF;

    RAISE NOTICE 'D2 post-check OK: service_role MEMBER OF writer=%, reader=%',
        v_writer_member, v_reader_member;
END $$;

COMMIT;

-- ============================================================================
-- Notas operacionales (no SQL, solo documentación inline)
-- ============================================================================
-- Aplicación esperada: Cowork T2-A aplica via Supabase MCP al cierre FASE D
-- consolidado (kickoff explícito: "Cowork aplica al cierre total via MCP").
--
-- Idempotencia: GRANT...TO role es idempotente en Postgres (no falla en re-run).
-- El DO block pre-check protege contra re-run prematuro (0032 no aplicado).
--
-- Rollback (manual, NO automático):
--   REVOKE anti_dory_writer_role FROM service_role;
--   REVOKE anti_dory_reader_role FROM service_role;
-- ============================================================================
