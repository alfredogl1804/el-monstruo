-- =====================================================================
-- Sprint PAR_BICEFALO_001 — Brand Engine como segundo embrión
-- Migration 0020: tabla embrion_validation_log + RLS canónico
-- =====================================================================
-- Spec: bridge/sprint_PAR_BICEFALO_001_brand_engine_spec_2026_05_11.md (T3)
-- DSCs aplicables:
--   DSC-MO-006 (par bicéfalo siempre)
--   DSC-S-006 (RLS por defecto)
--   DSC-G-004 (naming canónico — tabla con nombre de dominio)
--
-- Nota de numeración:
--   La spec original pedía 0012, pero ese slot ya está ocupado por
--   0012_embrion_inbox.sql (Sprint EMBRION-NEEDS-002 T5 merged).
--   Se usa 0020 que es el siguiente libre tras 0019 (Sprint D-2 scheduled_tasks).
-- =====================================================================

BEGIN;

-- ── 1) Tabla principal ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.embrion_validation_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,

    -- Referencia opcional a la memoria que originó la respuesta candidata.
    embrion_1_memoria_id UUID REFERENCES public.embrion_memoria(id) ON DELETE SET NULL,

    -- Snapshot de la respuesta evaluada.
    respuesta_candidata TEXT NOT NULL,

    -- Veredicto final del Brand Engine.
    veredicto TEXT NOT NULL CHECK (veredicto IN ('approved', 'rejected', 'timeout', 'error')),

    -- Scores por dimensión (NULL si la dimensión está deshabilitada en config).
    d1_brand_tono_score    NUMERIC(3, 2) CHECK (d1_brand_tono_score    IS NULL OR (d1_brand_tono_score    >= 0 AND d1_brand_tono_score    <= 1)),
    d2_honestidad_score    NUMERIC(3, 2) CHECK (d2_honestidad_score    IS NULL OR (d2_honestidad_score    >= 0 AND d2_honestidad_score    <= 1)),
    d3_doctrina_score      NUMERIC(3, 2) CHECK (d3_doctrina_score      IS NULL OR (d3_doctrina_score      >= 0 AND d3_doctrina_score      <= 1)),
    d4_apple_tesla_score   NUMERIC(3, 2) CHECK (d4_apple_tesla_score   IS NULL OR (d4_apple_tesla_score   >= 0 AND d4_apple_tesla_score   <= 1)),

    -- Razón estructurada del rejection y sugerencia para reintento.
    razon_rejection TEXT,
    sugerencia_reintento TEXT,

    -- Métricas operativas.
    reintentos_count INTEGER DEFAULT 0 NOT NULL CHECK (reintentos_count >= 0),
    cost_usd NUMERIC(10, 6) DEFAULT 0.0 NOT NULL CHECK (cost_usd >= 0),
    latency_ms INTEGER CHECK (latency_ms IS NULL OR latency_ms >= 0),

    -- Identificador del modelo evaluador efectivamente usado.
    evaluator_llm TEXT,

    -- Modo operativo en momento de evaluación.
    mode TEXT NOT NULL CHECK (mode IN ('shadow', 'enforce'))
);

COMMENT ON TABLE public.embrion_validation_log IS
    'Brand Engine — log forense de cada validación VETO emitida sobre respuestas candidatas del Embrión 1. Spec PAR_BICEFALO_001.';

COMMENT ON COLUMN public.embrion_validation_log.veredicto IS
    'Veredicto final: approved | rejected | timeout | error. Sólo rejected en mode=enforce bloquea output.';

COMMENT ON COLUMN public.embrion_validation_log.mode IS
    'shadow=loguea sin bloquear (canary); enforce=veredicto vincula (producción).';


-- ── 2) RLS canónico (DSC-S-006: por defecto cerrado) ───────────────────
ALTER TABLE public.embrion_validation_log ENABLE ROW LEVEL SECURITY;

-- Policy: solo service_role puede leer/escribir. El plano de datos del
-- Monstruo es cerrado por defecto (Regla Dura #7).
CREATE POLICY "embrion_validation_log_service_role_only"
    ON public.embrion_validation_log
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- ── 3) Índices para consultas operativas ──────────────────────────────
-- Consulta más común: últimas N validaciones (replay analysis, dashboard).
CREATE INDEX IF NOT EXISTS idx_validation_log_created_at
    ON public.embrion_validation_log (created_at DESC);

-- Consulta para análisis: filtrar por veredicto.
CREATE INDEX IF NOT EXISTS idx_validation_log_veredicto
    ON public.embrion_validation_log (veredicto);

-- Consulta para trazabilidad: encontrar todas las validaciones de una memoria.
CREATE INDEX IF NOT EXISTS idx_validation_log_memoria_id
    ON public.embrion_validation_log (embrion_1_memoria_id)
    WHERE embrion_1_memoria_id IS NOT NULL;

-- Consulta para budget tracking: costo acumulado por día.
CREATE INDEX IF NOT EXISTS idx_validation_log_cost_day
    ON public.embrion_validation_log (DATE(created_at), cost_usd)
    WHERE cost_usd > 0;


-- ── 4) Verificación post-migración ─────────────────────────────────────
DO $$
DECLARE
    v_rls_enabled BOOLEAN;
    v_policy_count INTEGER;
BEGIN
    -- Confirmar RLS habilitado.
    SELECT rowsecurity INTO v_rls_enabled
    FROM pg_tables
    WHERE schemaname = 'public' AND tablename = 'embrion_validation_log';

    IF NOT v_rls_enabled THEN
        RAISE EXCEPTION 'RLS NO habilitado en embrion_validation_log — viola DSC-S-006';
    END IF;

    -- Confirmar al menos una policy presente.
    SELECT COUNT(*) INTO v_policy_count
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'embrion_validation_log';

    IF v_policy_count < 1 THEN
        RAISE EXCEPTION 'Sin policies en embrion_validation_log — viola DSC-S-006';
    END IF;

    RAISE NOTICE 'Migration 0020 OK: tabla creada, RLS habilitado, % polic(ies) instaladas.', v_policy_count;
END $$;

COMMIT;
