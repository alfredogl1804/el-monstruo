-- =====================================================================
-- Sprint S-CONTRATOS-001 — DSC-G-011 (T4 Hilo Catastro)
-- Migration 0025: anti-bucle de rotación de credenciales
-- =====================================================================
-- Spec: bridge/sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md
-- DSCs aplicables:
--   DSC-G-011 (anti-bucle de rotación: máximo 1 rotación por credencial por día)
--   DSC-S-006 (RLS por defecto cerrado)
--   DSC-S-008 (rotación automatizada e inventario único)
--
-- Lección aplicada (post-V25, detectada por Perplexity T2-B):
--   `DATE(timestamptz)` es **STABLE**, no IMMUTABLE → NO se puede usar
--   directamente en CONSTRAINT UNIQUE ni en INDEX expression de manera segura.
--   Migración 0020 línea 95 dejó esa deuda para tiempos futuros.
--
--   FIX canónico aquí: columna generada STORED con
--   `(rotated_at AT TIME ZONE 'UTC')::date`. La operación
--   `timestamptz AT TIME ZONE 'UTC' → timestamp` es IMMUTABLE,
--   y `(timestamp)::date` también es IMMUTABLE. Eso permite
--   usarla en UNIQUE constraint sin riesgo de drift por session timezone.
--
-- Idempotencia: toda la migración usa IF NOT EXISTS / DO blocks defensivos.
-- =====================================================================

BEGIN;

-- ── 1) Tabla `credential_rotations` (idempotente) ──────────────────────
-- Si ya existe (creada por otro hilo), no la tocamos.
CREATE TABLE IF NOT EXISTS public.credential_rotations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

    -- Identificador lógico de la credencial rotada (p. ej. 'OPENAI_API_KEY',
    -- 'SUPABASE_DB_URL', 'GH_PAT_DEPLOY'). NO se guarda el secret real acá.
    credential_id TEXT NOT NULL,

    -- Quién/qué disparó la rotación (humano, workflow CI, manual).
    rotated_by TEXT NOT NULL DEFAULT 'unknown',

    -- Razón de la rotación (scheduled, leak_detected, post_incident, manual).
    razon TEXT NOT NULL DEFAULT 'scheduled' CHECK (razon IN
        ('scheduled', 'leak_detected', 'post_incident', 'manual', 'expired', 'other')),

    -- Timestamp completo de la rotación (TIMESTAMPTZ).
    rotated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,

    -- Notas operativas opcionales (workflow run, link al postmortem, etc.).
    notas TEXT,

    -- Snapshot de hash del secret nuevo (NO el secret) para auditar reuso accidental.
    new_secret_fingerprint TEXT,

    -- Columna generada IMMUTABLE para usar en UNIQUE constraint.
    -- Truco canónico: timestamptz AT TIME ZONE 'UTC' → timestamp (IMMUTABLE),
    -- luego cast a DATE (IMMUTABLE). El resultado es estable independiente
    -- del TimeZone de la sesión de quien inserta.
    rotated_at_date DATE GENERATED ALWAYS AS
        (((rotated_at AT TIME ZONE 'UTC'))::date) STORED
);

COMMENT ON TABLE public.credential_rotations IS
    'DSC-G-011: log de rotaciones de credenciales. UNIQUE (credential_id, rotated_at_date) previene bucles de rotación dentro del mismo día (en hora UTC).';

COMMENT ON COLUMN public.credential_rotations.rotated_at_date IS
    'Columna generada STORED: bucket diario en UTC. IMMUTABLE para uso seguro en UNIQUE constraint. Lección post-V25: NO usar DATE(rotated_at) directo (STABLE no IMMUTABLE).';


-- ── 2) Constraint UNIQUE anti-bucle (DSC-G-011) ────────────────────────
-- Si la tabla ya existía SIN columna generada, agrégala primero.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='credential_rotations'
          AND column_name='rotated_at_date'
    ) THEN
        ALTER TABLE public.credential_rotations
            ADD COLUMN rotated_at_date DATE GENERATED ALWAYS AS
                (((rotated_at AT TIME ZONE 'UTC'))::date) STORED;
    END IF;
END $$;

-- Constraint UNIQUE: máximo 1 rotación por credencial por día UTC.
-- Idempotente: si ya existe, no truena (DO block).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'unique_rotation_per_day_per_credential'
    ) THEN
        ALTER TABLE public.credential_rotations
            ADD CONSTRAINT unique_rotation_per_day_per_credential
            UNIQUE (credential_id, rotated_at_date);
    END IF;
END $$;


-- ── 3) RLS canónico (DSC-S-006: cerrado por defecto) ───────────────────
ALTER TABLE public.credential_rotations ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname='public' AND tablename='credential_rotations'
          AND policyname='credential_rotations_service_role_only'
    ) THEN
        CREATE POLICY "credential_rotations_service_role_only"
            ON public.credential_rotations
            AS PERMISSIVE
            FOR ALL
            TO public
            USING (auth.role() = 'service_role')
            WITH CHECK (auth.role() = 'service_role');
    END IF;
END $$;


-- ── 4) Índices operativos ──────────────────────────────────────────────
-- Consulta común: últimas rotaciones por credencial.
CREATE INDEX IF NOT EXISTS idx_credential_rotations_credential_at
    ON public.credential_rotations (credential_id, rotated_at DESC);

-- Consulta common: timeline general.
CREATE INDEX IF NOT EXISTS idx_credential_rotations_at
    ON public.credential_rotations (rotated_at DESC);

-- Consulta para auditoría de reuso de secrets.
CREATE INDEX IF NOT EXISTS idx_credential_rotations_fingerprint
    ON public.credential_rotations (new_secret_fingerprint)
    WHERE new_secret_fingerprint IS NOT NULL;


-- ── 5) Verificación post-migración ─────────────────────────────────────
DO $$
DECLARE
    v_rls_enabled BOOLEAN;
    v_policy_count INTEGER;
    v_constraint_exists BOOLEAN;
    v_generated_col_exists BOOLEAN;
BEGIN
    SELECT rowsecurity INTO v_rls_enabled
    FROM pg_tables
    WHERE schemaname='public' AND tablename='credential_rotations';

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'RLS NO habilitado en credential_rotations (viola DSC-S-006)';
    END IF;

    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname='public' AND tablename='credential_rotations';

    IF v_policy_count < 1 THEN
        RAISE EXCEPTION 'Sin policies en credential_rotations (viola DSC-S-006)';
    END IF;

    SELECT EXISTS(
        SELECT 1 FROM pg_constraint
        WHERE conname='unique_rotation_per_day_per_credential'
    ) INTO v_constraint_exists;

    IF NOT v_constraint_exists THEN
        RAISE EXCEPTION 'Constraint UNIQUE anti-bucle NO instalada (viola DSC-G-011)';
    END IF;

    SELECT EXISTS(
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='credential_rotations'
          AND column_name='rotated_at_date'
    ) INTO v_generated_col_exists;

    IF NOT v_generated_col_exists THEN
        RAISE EXCEPTION 'Columna generada rotated_at_date NO existe';
    END IF;

    RAISE NOTICE 'Migration 0025 OK: tabla credential_rotations + RLS + UNIQUE anti-bucle + columna generada IMMUTABLE.';
END $$;

COMMIT;

-- =====================================================================
-- TEST manual (idempotencia + IMMUTABLE):
--
-- INSERT INTO public.credential_rotations (credential_id, rotated_by, razon)
-- VALUES ('TEST_KEY', 'manus-hilo-catastro', 'manual');
--
-- INSERT INTO public.credential_rotations (credential_id, rotated_by, razon)
-- VALUES ('TEST_KEY', 'manus-hilo-catastro', 'manual');
-- → SEGUNDO INSERT debe fallar con violation de unique_rotation_per_day_per_credential
--
-- INSERT INTO public.credential_rotations (credential_id, rotated_at)
-- VALUES ('TEST_KEY', now() - interval '1 day');
-- → DEBE pasar (rotated_at_date diferente)
--
-- DELETE FROM public.credential_rotations WHERE credential_id='TEST_KEY';
-- =====================================================================
