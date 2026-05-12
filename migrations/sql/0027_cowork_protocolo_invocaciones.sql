-- Migration 0027: cowork_protocolo_invocaciones
-- Sprint: COWORK-AUTO-DISCIPLINE-REAL-001 (T1) — Audit log runtime de invocaciones del pre_response_hook
-- DSC enforzado: DSC-S-006 v1.1 (RLS por defecto), DSC-S-012 (anti-deriva migraciones),
--                DSC-G-017 (DSC-as-Contract), DSC-G-008 v3 (anti-Goodhart + deducción),
--                DSC-S-016 (anti-fabricación causalidad sin grep)
-- Fecha: 2026-05-12
-- Owner: Manus Hilo Ejecutor 1 (manus_hilo_a, cuenta apple)
-- Spec firmado: bridge/sprints_propuestos/sprint_COWORK_AUTO_DISCIPLINE_REAL_001.md commit d53b80ff
--
-- Tabla persiste cada invocación del pre_response_hook con:
--   - turn_id + decision_magnitude (trivial/medium/magna) para correlación con sesión
--   - queries_done JSONB con tablas consultadas (embrion_memoria, cowork_sesiones, etc.)
--   - violations_detected JSONB con F21 patterns matched + missing tool calls
--   - output_passed BOOLEAN + memory_seeds_inserted + duration_ms para métricas runtime
--
-- Objetivo: reducir F21 reincidente Cowork de 10/sesión hoy a ≤0.3/sesión proyectado
-- via enforcement runtime kernel REAL (no doctrina markdown que Cowork puede olvidar).
--
-- NOTA divergencia de spec: spec firmado pedía migration 0031 pero last existing es
-- 0026 (verificado binario `ls migrations/sql/ | tail -1`). Usar 0031 saltando
-- 0027-0030 violaría DSC-S-012 (anti-deriva migraciones). Sustancia del spec se
-- preserva integralmente; solo cambia el número secuencial. F21 propio del spec
-- documentado en reports/cowork_auto_discipline_pre_sprint_audit.json §L1.
--
-- LECCIÓN POST-V25: NO usar DATE(TIMESTAMPTZ) en CREATE INDEX. Solo índices simples.
-- Idempotencia: CREATE TABLE IF NOT EXISTS + DROP/CREATE POLICY (Postgres <16
-- no soporta CREATE POLICY IF NOT EXISTS).

BEGIN;

-- ===========================================================================
-- Tabla principal
-- ===========================================================================

CREATE TABLE IF NOT EXISTS public.cowork_protocolo_invocaciones (
    id                        UUID         DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at                TIMESTAMPTZ  NOT NULL DEFAULT now(),
    session_uuid              UUID,                                   -- FK soft a cowork_sesiones.id (nullable para invocaciones standalone CLI)
    turn_index                INTEGER      NOT NULL,                  -- turno secuencial en la sesión Cowork
    decision_magnitude        TEXT         NOT NULL,                  -- trivial | medium | magna
    queries_done              JSONB        NOT NULL DEFAULT '[]'::jsonb,  -- ["embrion_memoria", "cowork_sesiones", ...]
    violations_detected       JSONB        NOT NULL DEFAULT '[]'::jsonb,  -- [{"pattern_id":"diff_stats","match":"...","missing_tool_call":"..."}, ...]
    output_passed             BOOLEAN      NOT NULL,                  -- false si F21 patterns matched sin tool call previo
    output_length_chars       INTEGER,                                -- longitud del output candidato (para histogramas)
    memory_seeds_inserted     INTEGER      NOT NULL DEFAULT 0,        -- cuántas seeds embrion_memoria insertó esta invocación
    duration_ms               INTEGER,                                -- duración total del hook en milisegundos
    metadata                  JSONB        NOT NULL DEFAULT '{}'::jsonb,  -- libre: tool_calls_count, kernel_version, etc.

    CONSTRAINT cowork_protocolo_invocaciones_decision_magnitude_valid CHECK (
        decision_magnitude IN ('trivial', 'medium', 'magna')
    ),
    CONSTRAINT cowork_protocolo_invocaciones_turn_index_nonneg CHECK (turn_index >= 0),
    CONSTRAINT cowork_protocolo_invocaciones_output_length_nonneg CHECK (
        output_length_chars IS NULL OR output_length_chars >= 0
    ),
    CONSTRAINT cowork_protocolo_invocaciones_memory_seeds_nonneg CHECK (memory_seeds_inserted >= 0),
    CONSTRAINT cowork_protocolo_invocaciones_duration_ms_nonneg CHECK (
        duration_ms IS NULL OR duration_ms >= 0
    )
);

COMMENT ON TABLE public.cowork_protocolo_invocaciones IS
'Audit log runtime del pre_response_hook de Cowork. Cada invocación del hook crea una fila '
'con violations_detected (F21 patterns matched), output_passed, queries_done (memoria auto-leída), '
'memory_seeds_inserted y duration_ms. Sprint COWORK-AUTO-DISCIPLINE-REAL-001 spec commit d53b80ff. '
'Reduce F21 reincidente Cowork via enforcement runtime kernel REAL (DSC-S-016 anti-fabricación + DSC-G-008 v3 §4).';

COMMENT ON COLUMN public.cowork_protocolo_invocaciones.decision_magnitude IS
'trivial = output corto sin claims técnicos | medium = output con claims pero sin schema/migrations | '
'magna = output con claims sobre schema/migrations/PRs/commits/diffs (requiere F21 enforcement strict).';

COMMENT ON COLUMN public.cowork_protocolo_invocaciones.violations_detected IS
'JSONB array: [{"pattern_id": "diff_stats|db_schema|model_versions|...", "match": "<substring>", '
'"missing_tool_call": "<tool requerido no encontrado en history>", "severity": "P0|P1|P2"}, ...]';

COMMENT ON COLUMN public.cowork_protocolo_invocaciones.queries_done IS
'JSONB array de queries que el hook ejecutó esta invocación. Ej: '
'["embrion_memoria.importancia>=8", "cowork_sesiones.last_row"]. Cero queries = warning (auto-lectura no funcionó).';

COMMENT ON COLUMN public.cowork_protocolo_invocaciones.output_passed IS
'TRUE = output autorizado a llegar a Alfredo. FALSE = F21 pattern matched sin tool call previo '
'O verbatim citation no validable contra history. Hook return (False, feedback_correction).';

-- ===========================================================================
-- Índices (sin DATE(TIMESTAMPTZ) — lección post-V25)
-- ===========================================================================

CREATE INDEX IF NOT EXISTS idx_cowork_protocolo_invocaciones_session_turn
    ON public.cowork_protocolo_invocaciones (session_uuid, turn_index);

CREATE INDEX IF NOT EXISTS idx_cowork_protocolo_invocaciones_created_desc
    ON public.cowork_protocolo_invocaciones (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cowork_protocolo_invocaciones_passed_created
    ON public.cowork_protocolo_invocaciones (output_passed, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cowork_protocolo_invocaciones_magnitude
    ON public.cowork_protocolo_invocaciones (decision_magnitude, created_at DESC);

-- ===========================================================================
-- RLS por defecto (DSC-S-006 v1.1)
-- ===========================================================================

ALTER TABLE public.cowork_protocolo_invocaciones ENABLE ROW LEVEL SECURITY;

-- Drop + Create para idempotencia (Postgres <16 no soporta CREATE POLICY IF NOT EXISTS)
DROP POLICY IF EXISTS cowork_protocolo_invocaciones_service_role_only
    ON public.cowork_protocolo_invocaciones;

CREATE POLICY cowork_protocolo_invocaciones_service_role_only
    ON public.cowork_protocolo_invocaciones
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Revoke explícito de PUBLIC/anon/authenticated (defense in depth)
REVOKE ALL ON public.cowork_protocolo_invocaciones FROM PUBLIC;
REVOKE ALL ON public.cowork_protocolo_invocaciones FROM anon;
REVOKE ALL ON public.cowork_protocolo_invocaciones FROM authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.cowork_protocolo_invocaciones TO service_role;

-- ===========================================================================
-- Verificación automática post-apply (RAISE EXCEPTION si RLS no quedó habilitada)
-- ===========================================================================

DO $$
DECLARE
    v_rls_enabled BOOLEAN;
    v_policy_count INTEGER;
BEGIN
    SELECT relrowsecurity INTO v_rls_enabled
    FROM pg_class
    WHERE relname = 'cowork_protocolo_invocaciones' AND relnamespace = 'public'::regnamespace;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: cowork_protocolo_invocaciones creada sin RLS habilitado';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'cowork_protocolo_invocaciones';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: cowork_protocolo_invocaciones sin policies explícitas';
    END IF;

    RAISE NOTICE 'cowork_protocolo_invocaciones creada OK: RLS=%, policies=%', v_rls_enabled, v_policy_count;
END $$;

COMMIT;
