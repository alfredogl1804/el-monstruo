-- Sprint 51: Magna Classifier — Cache de Freshness (Capa 0.2)
-- Tabla para persistir clasificaciones de contenido magna vs premium
-- con TTL configurable por categoría:
--   APIs/frameworks: 24h | Precios/tipos de cambio: 1h | Trending tech: 6h
-- El clasificador consulta esta cache antes de re-evaluar un input similar

CREATE TABLE IF NOT EXISTS magna_cache (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cache_key       TEXT NOT NULL UNIQUE,            -- hash(query_normalizado + tool_name)
    tool_name       TEXT NOT NULL,                   -- tool asociada (web_search, consult_sabios, etc.)
    query           TEXT NOT NULL,                   -- query original normalizada
    result          JSONB NOT NULL DEFAULT '{}',     -- {route, score, suggested_tool, category}
    ttl_seconds     INTEGER NOT NULL,                -- TTL en segundos según categoría
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,            -- created_at + ttl_seconds
    hit_count       INTEGER NOT NULL DEFAULT 0,      -- veces consultada (para métricas)
    last_hit_at     TIMESTAMPTZ                      -- última consulta exitosa
);

-- Índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_magna_cache_key ON magna_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_magna_cache_expires ON magna_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_magna_cache_tool ON magna_cache(tool_name);

-- Índice para limpieza de expirados
CREATE INDEX IF NOT EXISTS idx_magna_cache_expires_cleanup ON magna_cache(expires_at)
    WHERE expires_at < NOW();

-- RLS: solo el service role puede leer/escribir
ALTER TABLE magna_cache ENABLE ROW LEVEL SECURITY;

-- Política para service role (kernel en Railway)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'magna_cache' AND policyname = 'service_role_all'
    ) THEN
        CREATE POLICY service_role_all ON magna_cache
            FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;
END $$;

-- Comentarios con identidad
COMMENT ON TABLE magna_cache IS 'Sprint 51: Magna Classifier — cache de clasificaciones con TTL para freshness de datos tech vs estables';
COMMENT ON COLUMN magna_cache.cache_key IS 'Hash determinístico de query normalizada + tool_name para deduplicación';
COMMENT ON COLUMN magna_cache.result IS 'Resultado de clasificación: {route: graph|router, score: 0-1, suggested_tool: str|null, category: tech|action|reflection}';
COMMENT ON COLUMN magna_cache.ttl_seconds IS 'Time-to-live en segundos: APIs=86400, precios=3600, trending=21600';
COMMENT ON COLUMN magna_cache.hit_count IS 'Contador de consultas exitosas — métrica de utilidad del cache';
