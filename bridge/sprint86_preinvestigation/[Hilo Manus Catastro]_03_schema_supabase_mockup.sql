-- [Hilo Manus Catastro] · Tarea 3 — Mockup Schema Supabase Sprint 86
-- Fecha: 2026-05-04
-- Descripción: Script de migración 016 para crear la base de datos de El Catastro
-- Incluye mejoras del ADDENDUM (Quorum, Trust Score, Dominios nuevos)

-- Pre-requisito: extensión pgvector (ya debería estar activa desde Sprint 81)
CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================
-- TABLA 1: catastro_modelos (La fuente de verdad viva)
-- ==========================================
CREATE TABLE IF NOT EXISTS catastro_modelos (
    id TEXT PRIMARY KEY,                           -- ej. 'flux-1-1-pro-ultra'
    nombre TEXT NOT NULL,                          -- ej. 'Flux 1.1 Pro Ultra'
    proveedor TEXT NOT NULL,                       -- ej. 'Black Forest Labs'
    macroarea TEXT NOT NULL,                       -- ej. 'vision-generativa'
    dominios TEXT[] NOT NULL,                      -- ej. '{text-to-image-calidad, hero-images}'
    subcapacidades TEXT[] DEFAULT '{}',            -- ej. '{fotorrealismo, prompt-adherence}'
    
    estado TEXT DEFAULT 'production',              -- production | beta | deprecated | alpha
    tipo TEXT DEFAULT 'propietario',               -- propietario | open-weights | open-weights-restricted
    licencia TEXT,                                 -- ej. 'BFL Commercial'
    
    -- Atributos estructurados
    capacidades_tecnicas JSONB NOT NULL DEFAULT '{}',
    calidad JSONB NOT NULL DEFAULT '{}',           -- elo_score, rank_global, metricas_aux
    precio JSONB NOT NULL DEFAULT '{}',            -- costo_usd, unidad, free_tier
    velocidad JSONB NOT NULL DEFAULT '{}',         -- latencia_p50_seg, throughput
    limitaciones TEXT[] DEFAULT '{}',
    fortalezas TEXT[] DEFAULT '{}',
    debilidades TEXT[] DEFAULT '{}',
    casos_uso_recomendados_monstruo TEXT[] DEFAULT '{}',
    
    -- Metadatos de curaduría y validación
    fuentes_datos TEXT[] NOT NULL DEFAULT '{}',    -- URLs de donde salió la data
    quorum_alcanzado BOOLEAN DEFAULT FALSE,        -- NUEVO (ADDENDUM): True si 2+ fuentes coinciden en precio/elo
    curador_responsable TEXT,                      -- ej. 'claude-opus-4.7'
    
    -- Ranking
    trono_score NUMERIC(5,2),                      -- Fórmula: 0.40*Q + 0.25*CE + 0.15*S + 0.10*R + 0.10*BF
    rank_dominio INT,                              -- 1, 2, 3...
    
    -- Búsqueda semántica
    embedding VECTOR(1536),                        -- Para "Pregúntale al Catastro"
    
    -- Timestamps
    ultima_validacion TIMESTAMPTZ DEFAULT NOW(),
    proxima_revalidacion TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices de performance para catastro_modelos
CREATE INDEX IF NOT EXISTS idx_catastro_macroarea ON catastro_modelos (macroarea);
CREATE INDEX IF NOT EXISTS idx_catastro_dominios ON catastro_modelos USING GIN (dominios);
CREATE INDEX IF NOT EXISTS idx_catastro_trono ON catastro_modelos (trono_score DESC);
CREATE INDEX IF NOT EXISTS idx_catastro_embedding ON catastro_modelos USING ivfflat (embedding vector_cosine_ops);

-- ==========================================
-- TABLA 2: catastro_historial (Snapshots diarios)
-- ==========================================
CREATE TABLE IF NOT EXISTS catastro_historial (
    fecha DATE NOT NULL,
    modelo_id TEXT NOT NULL REFERENCES catastro_modelos(id) ON DELETE CASCADE,
    data JSONB NOT NULL,                           -- Snapshot completo del modelo ese día
    trono_score NUMERIC(5,2),
    rank_dominio INT,
    PRIMARY KEY (fecha, modelo_id)
);

-- ==========================================
-- TABLA 3: catastro_eventos (Alertas y feed)
-- ==========================================
CREATE TABLE IF NOT EXISTS catastro_eventos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fecha TIMESTAMPTZ DEFAULT NOW(),
    tipo TEXT NOT NULL,                            -- nuevo | deprecado | cambio_precio | cambio_top3 | cve | quorum_fallido
    modelo_id TEXT REFERENCES catastro_modelos(id) ON DELETE SET NULL,
    contenido JSONB NOT NULL,                      -- ej. {"old_price": 0.08, "new_price": 0.06}
    prioridad TEXT DEFAULT 'info',                 -- info | importante | critico
    notificado BOOLEAN DEFAULT FALSE,              -- True cuando el bot de Telegram ya lo envió
    curador_origen TEXT                            -- Quién detectó el evento
);

CREATE INDEX IF NOT EXISTS idx_catastro_eventos_fecha ON catastro_eventos (fecha DESC);
CREATE INDEX IF NOT EXISTS idx_catastro_eventos_notificado ON catastro_eventos (notificado) WHERE notificado = FALSE;

-- ==========================================
-- TABLA 4: catastro_notas_monstruo (Anotaciones humanas/BrandFit)
-- ==========================================
CREATE TABLE IF NOT EXISTS catastro_notas_monstruo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    modelo_id TEXT NOT NULL REFERENCES catastro_modelos(id) ON DELETE CASCADE,
    autor TEXT NOT NULL,                           -- alfredo | claude | hilo-X
    contenido TEXT NOT NULL,
    fecha TIMESTAMPTZ DEFAULT NOW(),
    caso_uso TEXT                                  -- ej. 'renders_kukulcan'
);

-- ==========================================
-- TABLA 5: catastro_curadores (NUEVO ADDENDUM - Trust Score)
-- ==========================================
CREATE TABLE IF NOT EXISTS catastro_curadores (
    id TEXT PRIMARY KEY,                           -- ej. 'claude-opus-4.7-vision'
    macroarea TEXT NOT NULL,                       -- ej. 'vision-generativa'
    modelo_llm TEXT NOT NULL,                      -- ej. 'claude-opus-4.7'
    trust_score NUMERIC(3,2) DEFAULT 1.00,         -- Empieza en 1.00 (100%)
    total_validaciones INT DEFAULT 0,
    fallos_quorum INT DEFAULT 0,                   -- Veces que su data fue rechazada por falta de cuórum
    requiere_hitl BOOLEAN DEFAULT FALSE,           -- Se pone True si trust_score < 0.70
    last_run TIMESTAMPTZ
);

-- ==========================================
-- RLS POLICIES (Seguridad para el Command Center)
-- ==========================================
-- Habilitar RLS
ALTER TABLE catastro_modelos ENABLE ROW LEVEL SECURITY;
ALTER TABLE catastro_historial ENABLE ROW LEVEL SECURITY;
ALTER TABLE catastro_eventos ENABLE ROW LEVEL SECURITY;
ALTER TABLE catastro_notas_monstruo ENABLE ROW LEVEL SECURITY;
ALTER TABLE catastro_curadores ENABLE ROW LEVEL SECURITY;

-- Políticas de lectura (Command Center puede leer todo)
CREATE POLICY "Command Center read access for catastro_modelos" ON catastro_modelos FOR SELECT USING (true);
CREATE POLICY "Command Center read access for catastro_historial" ON catastro_historial FOR SELECT USING (true);
CREATE POLICY "Command Center read access for catastro_eventos" ON catastro_eventos FOR SELECT USING (true);
CREATE POLICY "Command Center read access for catastro_notas_monstruo" ON catastro_notas_monstruo FOR SELECT USING (true);
CREATE POLICY "Command Center read access for catastro_curadores" ON catastro_curadores FOR SELECT USING (true);

-- Políticas de escritura (Solo service_role del kernel puede escribir)
-- Nota: En Supabase, service_role by-passea RLS por default, así que no se necesitan policies explícitas
-- para INSERT/UPDATE/DELETE si el kernel usa la key de service_role.

-- ==========================================
-- FUNCIÓN DE UTILIDAD: Búsqueda Semántica
-- ==========================================
CREATE OR REPLACE FUNCTION match_catastro_modelos (
  query_embedding VECTOR(1536),
  match_threshold FLOAT,
  match_count INT,
  filtro_macroarea TEXT DEFAULT NULL
)
RETURNS TABLE (
  id TEXT,
  nombre TEXT,
  proveedor TEXT,
  macroarea TEXT,
  dominios TEXT[],
  trono_score NUMERIC,
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
    m.trono_score,
    1 - (m.embedding <=> query_embedding) AS similarity
  FROM catastro_modelos m
  WHERE 1 - (m.embedding <=> query_embedding) > match_threshold
    AND (filtro_macroarea IS NULL OR m.macroarea = filtro_macroarea)
  ORDER BY m.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
