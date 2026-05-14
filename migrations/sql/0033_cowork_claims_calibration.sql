-- Migration 0033: cowork_claims_calibration
-- Sprint: COWORK-MEMENTO-001 (T1) — Claim calibration retrospectiva (pieza 1 anti-Dory D2+D3)
-- DSC enforzado: DSC-V-001 (validación claims), DSC-S-006 v1.1 (RLS por defecto),
--                DSC-S-012 (anti-deriva migraciones), DSC-G-017 (DSC-as-Contract),
--                DSC-G-008 v3 §4 (anti-Goodhart + deducción consecuencias materiales),
--                DSC-S-016 (anti-fabricación causalidad sin grep), DSC-MO-006 v1.1 (PBA permanente)
-- Fecha: 2026-05-14
-- Owner: Hilo Ejecutor 2 (manus_hilo_b) bajo autoridad T1 directa
-- Spec firmado: bridge/sprints_propuestos/sprint_COWORK_MEMENTO_001.md commit 78d1fb00
--
-- DIVERGENCIA SPEC↔REALIDAD documentada verbatim (DSC-S-012 anti-deriva):
--   El spec §3.1 + §5 asumió migration number 0028 (pre-merge PR #118).
--   Realidad al T0 audit binario 2026-05-14:
--     last migration aplicada en main = 0032_anti_dory_rpcs (post FASE C Anti-Dory commit d95a725).
--     Migrations 0028-0032 ya ocupadas:
--       0027 cowork_protocolo_invocaciones
--       0028 rpc_match_memory_events
--       0029 runtime_events
--       0030 thread_snapshots
--       0031 project_runtime_heads
--       0032 anti_dory_rpcs
--     Siguiente libre = 0033.
--   Spec §3.1 cláusula fallback verbatim:
--     "Si #118 NO mergeado al T1 del sprint, Ejecutor 1 verifica
--      `ls migrations/sql/ | sort | tail -1` y usa el siguiente libre,
--      documentando divergencia verbatim en migration comment (patrón canonizado
--      AUTO-DISCIPLINE-REAL-001 T1). Esta cláusula respeta DSC-S-012 anti-deriva."
--   Procedemos con 0033 — divergencia documentada verbatim aquí.
--
-- Patrón: registra cada afirmación factual de Cowork con verification_status binario.
-- Dataset retrospectivo permite responder "¿cuántas F21 cometí en los últimos 7 días?"
-- con número binario, no estimación (Opus 4.7 Dirección 4 verbatim).
--
-- Eventos posibles (verification_status):
--   verified_pre              → register_tool_call() pre-emit con el claim verbatim
--   verified_post_match       → claim matchea exacto contra tool result en history
--   verified_post_mismatch    → tool call existe pero strings divergen (F21 latente)
--   unverified                → no hay tool call relacionado (F21 candidato)
--
-- Idempotencia: CREATE TABLE IF NOT EXISTS + DROP/CREATE POLICY (Postgres <16
-- no soporta CREATE POLICY IF NOT EXISTS).

BEGIN;

-- ===========================================================================
-- Tabla principal
-- ===========================================================================
CREATE TABLE IF NOT EXISTS public.cowork_claims_calibration (
    id                      UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    session_uuid            UUID,                                         -- FK soft a cowork_sesiones.id (nullable para CLI standalone)
    turn_index              INTEGER      NOT NULL,                        -- índice del turno Cowork dentro de la sesión
    claim_type              TEXT         NOT NULL,                        -- categoría del claim (file_path, table_name, etc.)
    claim_value             TEXT         NOT NULL,                        -- el valor exacto afirmado por Cowork
    verification_status     TEXT         NOT NULL,                        -- verified_pre / verified_post_match / verified_post_mismatch / unverified
    tool_call_evidence      TEXT,                                         -- string del tool call que verifica (o NULL si unverified)
    detected_in_output      TEXT,                                         -- snippet contextual ±50 chars del output Cowork
    extraction_regex_id     TEXT,                                         -- qué regex de ClaimExtractor lo capturó
    metadata                JSONB        NOT NULL DEFAULT '{}'::jsonb,

    CONSTRAINT cowork_claims_calibration_claim_type_valid CHECK (
        claim_type IN (
            'file_path', 'table_name', 'column_name', 'migration_number',
            'pr_number', 'commit_hash', 'branch_name', 'sprint_name',
            'loc_count', 'test_count', 'fecha_iso', 'version_string'
        )
    ),
    CONSTRAINT cowork_claims_calibration_verification_status_valid CHECK (
        verification_status IN (
            'verified_pre', 'verified_post_match',
            'verified_post_mismatch', 'unverified'
        )
    ),
    CONSTRAINT cowork_claims_calibration_turn_index_nonneg CHECK (turn_index >= 0)
);

COMMENT ON TABLE public.cowork_claims_calibration IS
'Calibration retrospectiva de claims factuales Cowork. Sprint COWORK-MEMENTO-001 (pieza 1 anti-Dory). '
'Dataset para iterar harness con evidencia (Opus 4.7 Direccion 4) no hipotesis. '
'verification_status binario: verified_pre / verified_post_match / verified_post_mismatch / unverified.';

COMMENT ON COLUMN public.cowork_claims_calibration.session_uuid IS
'FK soft a public.cowork_sesiones.id. Nullable para invocaciones CLI standalone (sin sesión activa).';

COMMENT ON COLUMN public.cowork_claims_calibration.verification_status IS
'Status binario calculado por ClaimLogger.intercept(): '
'verified_pre (tool call previo con claim verbatim), '
'verified_post_match (tool call existe y strings matchean), '
'verified_post_mismatch (tool call existe pero strings divergen — F21 latente), '
'unverified (sin tool call relacionado — F21 candidato).';

COMMENT ON COLUMN public.cowork_claims_calibration.tool_call_evidence IS
'String del tool call que evidencia el claim. NULL solo si verification_status=unverified.';

COMMENT ON COLUMN public.cowork_claims_calibration.detected_in_output IS
'Snippet contextual ±50 chars del output Cowork donde el ClaimExtractor capturó el claim.';

COMMENT ON COLUMN public.cowork_claims_calibration.extraction_regex_id IS
'Identificador interno del regex de ClaimExtractor que capturó este claim (para iterar regex).';

-- ===========================================================================
-- Índices (4 índices simples, sin DATE/TIMESTAMPTZ — lección post-V25)
-- ===========================================================================
CREATE INDEX IF NOT EXISTS idx_cowork_claims_calibration_session_turn
    ON public.cowork_claims_calibration (session_uuid, turn_index);

CREATE INDEX IF NOT EXISTS idx_cowork_claims_calibration_created_desc
    ON public.cowork_claims_calibration (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cowork_claims_calibration_type_status
    ON public.cowork_claims_calibration (claim_type, verification_status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_cowork_claims_calibration_unverified
    ON public.cowork_claims_calibration (created_at DESC)
    WHERE verification_status IN ('unverified', 'verified_post_mismatch');

-- ===========================================================================
-- RLS habilitado por defecto (DSC-S-006 v1.1)
-- ===========================================================================
ALTER TABLE public.cowork_claims_calibration ENABLE ROW LEVEL SECURITY;

-- Policy explícita: solo service_role accede (DSC-S-006 v1.1)
DROP POLICY IF EXISTS cowork_claims_calibration_service_role_only
    ON public.cowork_claims_calibration;

CREATE POLICY cowork_claims_calibration_service_role_only
    ON public.cowork_claims_calibration
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Revoke explícito de PUBLIC/anon/authenticated (defense in depth)
REVOKE ALL ON public.cowork_claims_calibration FROM PUBLIC;
REVOKE ALL ON public.cowork_claims_calibration FROM anon;
REVOKE ALL ON public.cowork_claims_calibration FROM authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.cowork_claims_calibration TO service_role;

-- ===========================================================================
-- Verificación automática post-apply (DSC-G-017 DSC-as-Contract enforzado runtime)
-- ===========================================================================
DO $$
DECLARE
    v_rls_enabled BOOLEAN;
    v_policy_count INTEGER;
BEGIN
    SELECT relrowsecurity INTO v_rls_enabled
    FROM pg_class
    WHERE relname = 'cowork_claims_calibration' AND relnamespace = 'public'::regnamespace;

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: cowork_claims_calibration creada sin RLS habilitado';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'cowork_claims_calibration';

    IF v_policy_count = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: cowork_claims_calibration sin policies explícitas';
    END IF;

    RAISE NOTICE 'cowork_claims_calibration creada OK: RLS=%, policies=%', v_rls_enabled, v_policy_count;
END $$;

COMMIT;
