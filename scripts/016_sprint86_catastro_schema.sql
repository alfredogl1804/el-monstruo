-- ============================================================================
-- El Monstruo — Sprint 86 — Bloque 1 — Schema Supabase de El Catastro
-- ============================================================================
-- Migration: 016
-- Sprint: 86 (Catastro Cimientos)
-- Autor: [Hilo Manus Catastro]
-- Fecha: 2026-05-04
--
-- Fusiona la spec de Cowork (cowork_to_manus.md L953) con el mockup
-- pre-investigado en bridge/sprint86_preinvestigation/_03_schema_supabase_mockup.sql
-- y los Addendum 001 (4 cambios) + 002 (3 decisiones Radar).
--
-- 5 tablas:
--   1. catastro_modelos          — fuente de verdad viva
--   2. catastro_historial        — snapshots diarios
--   3. catastro_eventos          — alertas, deltas, drift
--   4. catastro_notas            — anotaciones humanas + brand fit
--   5. catastro_curadores        — Trust Score por LLM curador (Addendum 001)
--
-- 1 vista materializada:
--   catastro_metricas_diarias    — derivada del histórico (NO heredamos columnas vacías del Radar)
--
-- 1 función:
--   match_catastro_modelos       — semantic search pgvector ivfflat
--
-- Decisiones de fusión (documentadas en bridge KICKOFF):
--   - id TEXT PRIMARY KEY (slug) en lugar de UUID — legibilidad URL/MCP
--   - dominios TEXT[] (no dominio TEXT) — modelos cubren múltiples dominios
--   - híbrido columnas + JSONB — métricas en columnas, datos extensibles en JSONB
--   - quorum_alcanzado BOOLEAN + fuentes_evidencia JSONB — citation tracking robusto
--   - RLS: read public, write solo service_role (Supabase by-passea con service key)
-- ============================================================================

-- ============================================================================
-- PRE-REQUISITO: extensión pgvector (debería estar activa desde Sprint 81)
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS vector;


-- ============================================================================
-- TABLA 1: catastro_modelos — La fuente de verdad viva
-- ============================================================================
CREATE TABLE IF NOT EXISTS catastro_modelos (
    -- Identidad
    id TEXT PRIMARY KEY,                            -- slug ej. 'gpt-5-5-mini' (legible para MCP/URLs)
    nombre TEXT NOT NULL,                           -- 'GPT-5.5 Mini'
    proveedor TEXT NOT NULL,                        -- 'OpenAI'

    -- Taxonomía (Sprint 86 = solo Macroárea 1 'inteligencia')
    macroarea TEXT NOT NULL,                        -- 'inteligencia' | 'vision_generativa' | 'agentes' (futuras)
    dominios TEXT[] NOT NULL DEFAULT '{}',          -- {'llm_frontier','coding'} — modelos pueden cubrir varios
    subcapacidades TEXT[] DEFAULT '{}',             -- {'reasoning','vision','tool_use'}

    -- Estado del modelo en el mercado
    estado TEXT NOT NULL DEFAULT 'production'
        CHECK (estado IN ('production', 'beta', 'open-source', 'deprecated', 'alpha', 'preview')),
    tipo TEXT NOT NULL DEFAULT 'propietario'
        CHECK (tipo IN ('propietario', 'open-weights', 'open-weights-restricted', 'open-source-mit', 'open-source-apache')),
    licencia TEXT,                                  -- 'OpenAI ToS' | 'Apache-2.0' | 'BFL Commercial' | etc.
    open_weights BOOLEAN NOT NULL DEFAULT false,
    api_endpoint TEXT,                              -- 'https://api.openai.com/v1/chat/completions'

    -- Métricas estructuradas (Trono Score components — bandas de confianza visibles)
    quality_score NUMERIC(5,2),                     -- 0-100 normalized (z-score por dominio + media calibrada)
    quality_delta NUMERIC(5,2),                     -- Cambio vs snapshot anterior
    cost_efficiency NUMERIC(5,2),                   -- 0-100 (calidad por dólar)
    speed_score NUMERIC(5,2),                       -- 0-100 (latency p50 + throughput)
    reliability_score NUMERIC(5,2),                 -- 0-100 (uptime + error rate)
    brand_fit NUMERIC(3,2),                         -- 0.00-1.00 (alineación con identidad El Monstruo)
    sovereignty NUMERIC(3,2),                       -- 0.00-1.00 (independencia de proveedor)
    velocity NUMERIC(3,2),                          -- 0.00-1.00 (velocidad de mejora del proveedor)

    -- Trono Global (fórmula: 0.40*Q + 0.25*CE + 0.15*S + 0.10*R + 0.10*BF, ajustable por dominio)
    trono_global NUMERIC(5,2),
    trono_delta NUMERIC(5,2),                       -- Cambio vs snapshot anterior
    rank_dominio INT,                               -- 1, 2, 3... dentro del dominio principal

    -- Datos comerciales
    precio_input_per_million NUMERIC(10,4),         -- USD por 1M tokens input
    precio_output_per_million NUMERIC(10,4),        -- USD por 1M tokens output

    -- Datos extensibles (sin migrations futuras)
    capacidades_tecnicas JSONB NOT NULL DEFAULT '{}',  -- {context_window, max_output, multimodal, etc.}
    velocidad JSONB NOT NULL DEFAULT '{}',             -- {latencia_p50_seg, throughput_tps, ttft_ms}
    limitaciones TEXT[] DEFAULT '{}',
    fortalezas TEXT[] DEFAULT '{}',
    debilidades TEXT[] DEFAULT '{}',
    casos_uso_recomendados_monstruo TEXT[] DEFAULT '{}',

    -- Citation tracking obligatorio (Addendum 001 — anti-alucinación)
    fuentes_evidencia JSONB NOT NULL DEFAULT '[]',  -- [{url, fetched_at, payload_hash, curador, tipo_dato}]
    quorum_alcanzado BOOLEAN NOT NULL DEFAULT false,-- true si 2+ fuentes coinciden en métricas críticas
    confidence NUMERIC(3,2) NOT NULL DEFAULT 0.50
        CHECK (confidence >= 0.00 AND confidence <= 1.00),
    curador_responsable TEXT,                       -- 'claude-opus-4.7' | 'gpt-5.5-pro' | etc.

    -- Búsqueda semántica
    embedding vector(1536),                         -- text-embedding-3-small (OpenAI) o equivalent

    -- Extensibilidad pura
    data_extra JSONB NOT NULL DEFAULT '{}',
    schema_version INT NOT NULL DEFAULT 1,

    -- Audit trail
    ultima_validacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    proxima_revalidacion TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices de performance para queries frecuentes
CREATE INDEX IF NOT EXISTS idx_catastro_macroarea ON catastro_modelos (macroarea);
CREATE INDEX IF NOT EXISTS idx_catastro_dominios ON catastro_modelos USING GIN (dominios);
CREATE INDEX IF NOT EXISTS idx_catastro_trono ON catastro_modelos (trono_global DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_catastro_estado ON catastro_modelos (estado) WHERE estado != 'deprecated';
CREATE INDEX IF NOT EXISTS idx_catastro_proveedor ON catastro_modelos (proveedor);
CREATE INDEX IF NOT EXISTS idx_catastro_quorum ON catastro_modelos (quorum_alcanzado);
CREATE INDEX IF NOT EXISTS idx_catastro_embedding ON catastro_modelos
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);


-- ============================================================================
-- TABLA 2: catastro_historial — Snapshots diarios para series temporales
-- ============================================================================
CREATE TABLE IF NOT EXISTS catastro_historial (
    fecha DATE NOT NULL,
    modelo_id TEXT NOT NULL REFERENCES catastro_modelos(id) ON DELETE CASCADE,
    snapshot JSONB NOT NULL,                        -- copia completa del registro de catastro_modelos ese día
    trono_global NUMERIC(5,2),                      -- denormalizado para queries rápidas sobre série
    rank_dominio INT,                               -- denormalizado
    PRIMARY KEY (fecha, modelo_id)
);

CREATE INDEX IF NOT EXISTS idx_historial_fecha ON catastro_historial (fecha DESC);
CREATE INDEX IF NOT EXISTS idx_historial_modelo ON catastro_historial (modelo_id, fecha DESC);


-- ============================================================================
-- TABLA 3: catastro_eventos — Alertas, deltas, drift, deprecations
-- ============================================================================
CREATE TABLE IF NOT EXISTS catastro_eventos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tipo TEXT NOT NULL
        CHECK (tipo IN (
            'top3_change',          -- cambio en Top 3 de un dominio
            'deprecation',          -- modelo marcado como deprecated
            'price_change',         -- cambio significativo de precio (>5%)
            'new_model',            -- modelo nuevo entró al Catastro
            'cve',                  -- vulnerabilidad reportada
            'model_drift_detected', -- detector de drift del clasificador (Addendum 002, decisión 3)
            'quorum_failed',        -- curador-LLM no alcanzó cuórum 2-de-3
            'source_down'           -- fuente API caída
        )),
    prioridad TEXT NOT NULL DEFAULT 'info'
        CHECK (prioridad IN ('critico', 'importante', 'info')),
    modelo_id TEXT REFERENCES catastro_modelos(id) ON DELETE SET NULL,
    descripcion TEXT NOT NULL,
    contexto JSONB NOT NULL DEFAULT '{}',           -- {old_value, new_value, source_urls, etc.}
    notificado BOOLEAN NOT NULL DEFAULT false,      -- true cuando Telegram bot ya lo envió
    curador_origen TEXT                             -- quién detectó el evento
);

CREATE INDEX IF NOT EXISTS idx_eventos_fecha ON catastro_eventos (fecha DESC);
CREATE INDEX IF NOT EXISTS idx_eventos_tipo ON catastro_eventos (tipo, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_eventos_no_notificados ON catastro_eventos (notificado) WHERE notificado = false;
CREATE INDEX IF NOT EXISTS idx_eventos_criticos ON catastro_eventos (prioridad, fecha DESC) WHERE prioridad = 'critico';


-- ============================================================================
-- TABLA 4: catastro_notas — Anotaciones humanas y de agentes (BrandFit feedback)
-- ============================================================================
CREATE TABLE IF NOT EXISTS catastro_notas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    modelo_id TEXT NOT NULL REFERENCES catastro_modelos(id) ON DELETE CASCADE,
    autor TEXT NOT NULL,                            -- 'alfredo' | 'cowork' | 'manus_catastro' | 'embrion_critic_visual'
    contenido TEXT NOT NULL,
    caso_uso TEXT,                                  -- 'hero_images_landings_education' | 'agent_orchestration' | etc.
    rating INT CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5)),
    fecha TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notas_modelo ON catastro_notas (modelo_id, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_notas_caso_uso ON catastro_notas (caso_uso) WHERE caso_uso IS NOT NULL;


-- ============================================================================
-- TABLA 5: catastro_curadores — Trust Score por LLM curador (Addendum 001 cambio 2)
-- ============================================================================
CREATE TABLE IF NOT EXISTS catastro_curadores (
    id TEXT PRIMARY KEY,                            -- 'claude-opus-4.7-inteligencia' (un curador por macroarea)
    macroarea TEXT NOT NULL,                        -- macroarea que cura
    modelo_llm TEXT NOT NULL,                      -- 'claude-opus-4.7'
    proveedor TEXT NOT NULL,                        -- 'Anthropic'
    rol TEXT NOT NULL DEFAULT 'curador'
        CHECK (rol IN ('curador', 'validador', 'arbitro')),  -- arquitectura quorum 2-de-3 + 1 árbitro
    trust_score NUMERIC(3,2) NOT NULL DEFAULT 1.00
        CHECK (trust_score >= 0.00 AND trust_score <= 1.00),
    total_validaciones INT NOT NULL DEFAULT 0,
    aciertos_quorum INT NOT NULL DEFAULT 0,        -- consensos donde su voto coincidió con la mayoría
    fallos_quorum INT NOT NULL DEFAULT 0,          -- veces que su voto fue rechazado por minoría
    requiere_hitl BOOLEAN NOT NULL DEFAULT false,  -- true si trust_score < 0.70 (HITL = Human In The Loop)
    last_run TIMESTAMPTZ,
    notas TEXT,                                    -- ej. 'temperatura ajustada a 0.1 desde 2026-05-01'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_curadores_macroarea ON catastro_curadores (macroarea);
CREATE INDEX IF NOT EXISTS idx_curadores_hitl ON catastro_curadores (requiere_hitl) WHERE requiere_hitl = true;


-- ============================================================================
-- VISTA MATERIALIZADA: catastro_metricas_diarias
-- ============================================================================
-- Derivada del histórico — evita columnas vacías del Radar.
-- Refresh diario (07:30 CST) por el pipeline.
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS catastro_metricas_diarias AS
SELECT
    h.fecha,
    COUNT(DISTINCT h.modelo_id)                                 AS modelos_totales,
    COUNT(DISTINCT h.modelo_id) FILTER (
        WHERE (h.snapshot->>'ultima_validacion')::timestamptz > h.fecha::timestamptz - INTERVAL '24 hours'
    )                                                            AS modelos_validados_24h,
    COUNT(DISTINCT h.modelo_id) FILTER (
        WHERE (h.snapshot->>'created_at')::timestamptz::date = h.fecha
    )                                                            AS modelos_nuevos_24h,
    COUNT(DISTINCT h.modelo_id) FILTER (
        WHERE h.snapshot->>'estado' = 'deprecated'
    )                                                            AS modelos_deprecados_24h,
    (
        SELECT COUNT(*) FROM catastro_eventos e
        WHERE e.fecha::date = h.fecha AND e.prioridad = 'critico'
    )                                                            AS eventos_criticos,
    'high'::TEXT                                                 AS trust_level  -- placeholder Sprint 86, lógica real Sprint 87
FROM catastro_historial h
GROUP BY h.fecha;

CREATE UNIQUE INDEX IF NOT EXISTS idx_metricas_diarias_fecha ON catastro_metricas_diarias (fecha);


-- ============================================================================
-- FUNCIÓN: match_catastro_modelos — Semantic search con pgvector ivfflat
-- ============================================================================
-- Soporta filtros opcionales por macroarea y por dominio.
-- Devuelve los Top N modelos más similares al query embedding.
-- Uso desde MCP server: catastro.recommend(caso_uso, restricciones)
-- ============================================================================
CREATE OR REPLACE FUNCTION match_catastro_modelos (
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.70,
    match_count INT DEFAULT 10,
    filtro_macroarea TEXT DEFAULT NULL,
    filtro_dominio TEXT DEFAULT NULL,
    excluir_deprecated BOOLEAN DEFAULT true
)
RETURNS TABLE (
    id TEXT,
    nombre TEXT,
    proveedor TEXT,
    macroarea TEXT,
    dominios TEXT[],
    estado TEXT,
    trono_global NUMERIC,
    rank_dominio INT,
    precio_input_per_million NUMERIC,
    precio_output_per_million NUMERIC,
    confidence NUMERIC,
    quorum_alcanzado BOOLEAN,
    fuentes_evidencia JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.nombre,
        m.proveedor,
        m.macroarea,
        m.dominios,
        m.estado,
        m.trono_global,
        m.rank_dominio,
        m.precio_input_per_million,
        m.precio_output_per_million,
        m.confidence,
        m.quorum_alcanzado,
        m.fuentes_evidencia,
        (1 - (m.embedding <=> query_embedding))::FLOAT AS similarity
    FROM catastro_modelos m
    WHERE m.embedding IS NOT NULL
      AND (1 - (m.embedding <=> query_embedding)) > match_threshold
      AND (filtro_macroarea IS NULL OR m.macroarea = filtro_macroarea)
      AND (filtro_dominio IS NULL OR filtro_dominio = ANY(m.dominios))
      AND (NOT excluir_deprecated OR m.estado != 'deprecated')
    ORDER BY m.embedding <=> query_embedding ASC
    LIMIT match_count;
END;
$$;


-- ============================================================================
-- TRIGGER: updated_at automático en catastro_modelos y catastro_curadores
-- ============================================================================
CREATE OR REPLACE FUNCTION trg_catastro_set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS catastro_modelos_set_updated_at ON catastro_modelos;
CREATE TRIGGER catastro_modelos_set_updated_at
    BEFORE UPDATE ON catastro_modelos
    FOR EACH ROW EXECUTE FUNCTION trg_catastro_set_updated_at();

DROP TRIGGER IF EXISTS catastro_curadores_set_updated_at ON catastro_curadores;
CREATE TRIGGER catastro_curadores_set_updated_at
    BEFORE UPDATE ON catastro_curadores
    FOR EACH ROW EXECUTE FUNCTION trg_catastro_set_updated_at();


-- ============================================================================
-- RLS POLICIES — Read public, write solo service_role
-- ============================================================================
-- Supabase service_role by-passea RLS por default — no se necesitan policies
-- explícitas para INSERT/UPDATE/DELETE si el kernel usa service_role key.
-- Las policies SELECT permiten al Command Center (anon key) leer todo.
-- ============================================================================
ALTER TABLE catastro_modelos    ENABLE ROW LEVEL SECURITY;
ALTER TABLE catastro_historial  ENABLE ROW LEVEL SECURITY;
ALTER TABLE catastro_eventos    ENABLE ROW LEVEL SECURITY;
ALTER TABLE catastro_notas      ENABLE ROW LEVEL SECURITY;
ALTER TABLE catastro_curadores  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "catastro_modelos_read_public"   ON catastro_modelos;
DROP POLICY IF EXISTS "catastro_historial_read_public" ON catastro_historial;
DROP POLICY IF EXISTS "catastro_eventos_read_public"   ON catastro_eventos;
DROP POLICY IF EXISTS "catastro_notas_read_public"     ON catastro_notas;
DROP POLICY IF EXISTS "catastro_curadores_read_public" ON catastro_curadores;

CREATE POLICY "catastro_modelos_read_public"   ON catastro_modelos   FOR SELECT USING (true);
CREATE POLICY "catastro_historial_read_public" ON catastro_historial FOR SELECT USING (true);
CREATE POLICY "catastro_eventos_read_public"   ON catastro_eventos   FOR SELECT USING (true);
CREATE POLICY "catastro_notas_read_public"     ON catastro_notas     FOR SELECT USING (true);
CREATE POLICY "catastro_curadores_read_public" ON catastro_curadores FOR SELECT USING (true);


-- ============================================================================
-- COMMENTS — documentación inline para introspección desde Supabase Studio
-- ============================================================================
COMMENT ON TABLE catastro_modelos    IS 'El Catastro — fuente de verdad viva de modelos IA. Sprint 86, Macroarea 1 Inteligencia.';
COMMENT ON TABLE catastro_historial  IS 'Snapshots diarios de catastro_modelos. Permite series temporales y rollback.';
COMMENT ON TABLE catastro_eventos    IS 'Feed de alertas, deltas, drift, deprecations. Notificado vía Telegram bot.';
COMMENT ON TABLE catastro_notas      IS 'Anotaciones humanas + brand fit feedback de embriones (Critic Visual, Product Architect).';
COMMENT ON TABLE catastro_curadores  IS 'Trust Score de cada LLM curador. Si trust<0.70 → flag HITL. Addendum 001 cambio 2.';
COMMENT ON FUNCTION match_catastro_modelos IS 'Semantic search pgvector ivfflat. Usado por catastro.recommend() en MCP server.';

-- ============================================================================
-- FIN del Bloque 1 Sprint 86 — Schema Supabase
-- ============================================================================
