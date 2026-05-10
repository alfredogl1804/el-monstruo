-- ============================================================================
-- Migration 030 - Sprint 88 - Macroarea AGENTES del Catastro
-- ============================================================================
-- Objetivo: poblar la macroarea AGENTES del Catastro con productos/sustratos
-- completos (agentes, IDEs con LLM, frameworks de orquestacion, interfaces de
-- usuario). NO confundir con modelos LLM puros (macroarea INTELIGENCIA).
--
-- Decision arquitectonica: tabla SEPARADA `catastro_agentes` con FK opcional
-- a `catastro_modelos` (llm_base_id). Razon:
--   - Dimensiones fundamentalmente distintas (sandbox/fs/internet vs benchmarks)
--   - Un agente puede envolver multiples LLMs (Manus = Claude/GPT/Gemini)
--   - Tronos por dominio AGENTES requieren formula distinta a LLMs
--
-- Cruza con:
--   - DSC-MO-009: arsenal de herramientas seleccionable por Catastro
--   - DSC-G-007: integrar herramientas verticales lideres
--   - DSC-G-007.2 (este sprint): macroarea AGENTES canonizada
--
-- NO toca tablas del embrion (DSC-MO-006/007/008).
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TABLA: catastro_agentes
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catastro_agentes (
    id TEXT PRIMARY KEY,                                  -- slug kebab-case (ej. 'manus', 'claude-cowork')
    nombre TEXT NOT NULL,                                 -- nombre comercial (ej. 'Manus', 'Claude Cowork')
    proveedor TEXT NOT NULL,                              -- 'Manus' | 'Anthropic' | 'OpenAI' | etc.

    -- Taxonomia (espejo de schema.py DominioAgentes)
    macroarea TEXT NOT NULL DEFAULT 'agentes'
        CHECK (macroarea = 'agentes'),
    dominio TEXT NOT NULL
        CHECK (dominio IN (
            'agentes_desarrollo',
            'agentes_investigacion',
            'agentes_ejecutores',
            'agentes_multi_swarm',
            'interfaces_usuario'
        )),
    subcapacidades TEXT[] DEFAULT '{}',

    -- Relacion con LLM base (opcional — algunos agentes envuelven 1 LLM, otros varios)
    llm_base_id TEXT REFERENCES catastro_modelos(id) ON DELETE SET NULL,
    llm_bases_alternativos TEXT[] DEFAULT '{}',           -- otros LLMs que el agente puede usar

    -- Dimensiones tecnicas booleanas
    tiene_sandbox BOOLEAN NOT NULL DEFAULT false,         -- ejecuta en entorno aislado
    acceso_filesystem BOOLEAN NOT NULL DEFAULT false,     -- lee/escribe archivos del usuario
    acceso_internet BOOLEAN NOT NULL DEFAULT false,       -- navegacion web activa
    multi_step_capable BOOLEAN NOT NULL DEFAULT false,    -- puede ejecutar workflows
    multi_swarm_capable BOOLEAN NOT NULL DEFAULT false,   -- puede orquestar sub-agentes

    -- Persistencia de memoria
    persistencia_memoria TEXT NOT NULL DEFAULT 'none'
        CHECK (persistencia_memoria IN ('none', 'session', 'persistent')),

    -- Tools y casos de uso
    tools_nativas TEXT[] DEFAULT '{}',                    -- ['browser', 'shell', 'editor', 'mcp', ...]
    casos_de_uso_primarios TEXT[] DEFAULT '{}',           -- tags de uso primario

    -- Performance / costo
    costo_por_uso_tipico TEXT
        CHECK (costo_por_uso_tipico IS NULL OR costo_por_uso_tipico IN ('bajo', 'medio', 'alto', 'muy_alto')),
    latencia_tipica_segundos INT,                         -- RTT esperado

    -- Estado
    estado TEXT NOT NULL DEFAULT 'production'
        CHECK (estado IN ('production', 'beta', 'preview', 'open-source', 'deprecated', 'alpha')),
    open_weights BOOLEAN NOT NULL DEFAULT false,
    api_endpoint TEXT,                                    -- si aplica

    -- Metricas Trono (formula adaptada AGENTES — ver kernel/catastro/trono.py)
    -- Pesos Trono AGENTES (suma 1.0):
    --   capacidad_tecnica 0.30 (combinacion de sandbox/fs/internet/multi_swarm)
    --   adopcion          0.25 (popularity, github stars, comunidad)
    --   estabilidad       0.20 (uptime, breaking changes, soporte)
    --   integracion       0.15 (cuanto se conecta con otros tools/MCPs)
    --   costo_eficiencia  0.10 (capacidad por dolar)
    capacidad_tecnica NUMERIC(5,2),                       -- 0-100 normalizado
    adopcion_score NUMERIC(5,2),                          -- 0-100 (proxy de popularidad)
    estabilidad_score NUMERIC(5,2),                       -- 0-100
    integracion_score NUMERIC(5,2),                       -- 0-100
    costo_eficiencia_score NUMERIC(5,2),                  -- 0-100

    trono_dominio NUMERIC(5,2),                           -- 0-100 score final dominio AGENTES
    trono_delta NUMERIC(5,2),
    rank_dominio INT,                                     -- 1, 2, 3... dentro del dominio

    -- Datos extensibles
    fortalezas TEXT[] DEFAULT '{}',
    debilidades TEXT[] DEFAULT '{}',
    limitaciones TEXT[] DEFAULT '{}',

    -- Citation tracking obligatorio (DSC-G-007.1)
    fuentes_evidencia JSONB NOT NULL DEFAULT '[]',
    quorum_alcanzado BOOLEAN NOT NULL DEFAULT false,
    confidence NUMERIC(3,2) NOT NULL DEFAULT 0.50
        CHECK (confidence >= 0.00 AND confidence <= 1.00),
    curador_responsable TEXT,
    validacion_adversarial JSONB NOT NULL DEFAULT '{}',   -- {sabios:[...], acuerdo_pct, discrepancias:[...]}

    -- Extensibilidad
    data_extra JSONB NOT NULL DEFAULT '{}',
    schema_version INT NOT NULL DEFAULT 1,

    -- Audit
    ultima_validacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    proxima_revalidacion TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- INVARIANTE: multi_swarm_capable implica multi_step_capable
-- ----------------------------------------------------------------------------
ALTER TABLE catastro_agentes
    ADD CONSTRAINT chk_swarm_implies_multistep
    CHECK (NOT multi_swarm_capable OR multi_step_capable);

-- ----------------------------------------------------------------------------
-- Indices de performance
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_agentes_dominio ON catastro_agentes (dominio);
CREATE INDEX IF NOT EXISTS idx_agentes_proveedor ON catastro_agentes (proveedor);
CREATE INDEX IF NOT EXISTS idx_agentes_trono ON catastro_agentes (trono_dominio DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_agentes_estado ON catastro_agentes (estado) WHERE estado != 'deprecated';
CREATE INDEX IF NOT EXISTS idx_agentes_llm_base ON catastro_agentes (llm_base_id);
CREATE INDEX IF NOT EXISTS idx_agentes_swarm ON catastro_agentes (multi_swarm_capable) WHERE multi_swarm_capable = true;
CREATE INDEX IF NOT EXISTS idx_agentes_tools_nativas ON catastro_agentes USING GIN (tools_nativas);

-- ----------------------------------------------------------------------------
-- Trigger updated_at
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION trg_catastro_agentes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS catastro_agentes_updated_at ON catastro_agentes;
CREATE TRIGGER catastro_agentes_updated_at
    BEFORE UPDATE ON catastro_agentes
    FOR EACH ROW
    EXECUTE FUNCTION trg_catastro_agentes_updated_at();

-- ----------------------------------------------------------------------------
-- Comentario documentacion
-- ----------------------------------------------------------------------------
COMMENT ON TABLE catastro_agentes IS
    'Sprint 88 - Macroarea AGENTES del Catastro. Productos/sustratos completos clasificados por dominio. FK opcional a catastro_modelos para LLM base. Cruza con DSC-MO-009, DSC-G-007, DSC-G-007.2.';

COMMENT ON COLUMN catastro_agentes.llm_base_id IS
    'LLM principal que el agente envuelve (FK a catastro_modelos.id). NULL si el agente es agnostico de LLM (ej. n8n, Zapier).';

COMMENT ON COLUMN catastro_agentes.multi_swarm_capable IS
    'Capacidad de orquestar sub-agentes en paralelo (Kimi K2.6, AutoGen, CrewAI, LangGraph). Implica multi_step_capable=true.';

COMMENT ON COLUMN catastro_agentes.validacion_adversarial IS
    'JSON con resultado de validacion adversarial (DSC-G-007.1): sabios consultados, % de acuerdo, discrepancias resueltas.';
