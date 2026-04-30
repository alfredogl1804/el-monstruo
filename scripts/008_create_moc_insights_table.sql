-- Sprint 36: MOC (Motor de Orquestación Central)
-- Tabla para almacenar insights generados por el Sintetizador del MOC.

CREATE TABLE IF NOT EXISTS moc_insights (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         TEXT NOT NULL DEFAULT 'anonymous',
    window_hours    INTEGER NOT NULL DEFAULT 24,
    summary         TEXT,
    patterns        JSONB DEFAULT '[]'::jsonb,
    alerts          JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    metrics         JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índice para consultas por usuario y fecha
CREATE INDEX IF NOT EXISTS idx_moc_insights_user_created
    ON moc_insights (user_id, created_at DESC);

-- Índice para alertas (búsqueda de insights con alertas activas)
CREATE INDEX IF NOT EXISTS idx_moc_insights_alerts
    ON moc_insights USING GIN (alerts);

-- RLS: solo el usuario propietario puede ver sus insights
ALTER TABLE moc_insights ENABLE ROW LEVEL SECURITY;

-- Política: service_role puede leer/escribir todo (para el kernel)
CREATE POLICY "service_role_full_access" ON moc_insights
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

COMMENT ON TABLE moc_insights IS
    'Insights consolidados generados por el MOC Sintetizador. Sprint 36.';
