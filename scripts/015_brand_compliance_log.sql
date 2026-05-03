-- ============================================================================
-- El Monstruo — Sprint 82: Brand Compliance Log
-- ============================================================================
-- Tabla para registrar validaciones de compliance de marca.
-- Cada entrada es un resultado de BrandValidator: score, issues, target.
-- El Command Center consume esta tabla para mostrar tendencias de compliance.
-- ============================================================================

-- Crear tabla si no existe (idempotente)
CREATE TABLE IF NOT EXISTS brand_compliance_log (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    target          TEXT NOT NULL,
    target_type     TEXT NOT NULL CHECK (target_type IN ('output_name', 'endpoint', 'tool_spec', 'error_message')),
    score           INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    passes          BOOLEAN NOT NULL DEFAULT true,
    threshold       INTEGER NOT NULL DEFAULT 60,
    issues          JSONB DEFAULT '[]'::jsonb,
    suggestions     JSONB DEFAULT '[]'::jsonb,
    context         JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_brand_compliance_target_type
    ON brand_compliance_log (target_type);

CREATE INDEX IF NOT EXISTS idx_brand_compliance_passes
    ON brand_compliance_log (passes);

CREATE INDEX IF NOT EXISTS idx_brand_compliance_created_at
    ON brand_compliance_log (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_brand_compliance_score
    ON brand_compliance_log (score);

-- RLS
ALTER TABLE brand_compliance_log ENABLE ROW LEVEL SECURITY;

-- Policy: service_role tiene acceso total
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'brand_compliance_log'
        AND policyname = 'service_role_brand_compliance'
    ) THEN
        CREATE POLICY service_role_brand_compliance
            ON brand_compliance_log
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

-- Comentarios
COMMENT ON TABLE brand_compliance_log IS 'Sprint 82: Registro de validaciones de compliance de marca del Brand Engine';
COMMENT ON COLUMN brand_compliance_log.target IS 'Nombre del elemento validado (tool, endpoint, módulo)';
COMMENT ON COLUMN brand_compliance_log.target_type IS 'Tipo: output_name, endpoint, tool_spec, error_message';
COMMENT ON COLUMN brand_compliance_log.score IS 'Score de compliance 0-100';
COMMENT ON COLUMN brand_compliance_log.passes IS 'Si pasó el threshold de compliance';
COMMENT ON COLUMN brand_compliance_log.issues IS 'Lista de problemas encontrados (JSONB array)';
COMMENT ON COLUMN brand_compliance_log.suggestions IS 'Sugerencias de mejora (JSONB array)';
