-- ═══════════════════════════════════════════════════════════════════
-- Migration 013: La Memoria de Errores + pgvector (Sprint 81, Capa 0.1)
-- ═══════════════════════════════════════════════════════════════════
-- Tabla persistente de errores del kernel con búsqueda semántica.
-- Implementa Obj #4 — No equivocarse dos veces.
-- Filosofía: cada fallo es lección. Cada lección es regla. Cada regla
-- baja la probabilidad del siguiente fallo.
--
-- Soberanía: si pgvector no está disponible, las columnas embedding
-- quedan NULL y el sistema degrada a búsqueda por module/action exacto.
-- El sistema sigue operativo, solo con menos cobertura semántica.
-- ═══════════════════════════════════════════════════════════════════

-- ─── 0. Extensión pgvector ─────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;

-- ─── 1. Tabla principal: error_memory ─────────────────────────────
CREATE TABLE IF NOT EXISTS error_memory (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    error_signature     TEXT NOT NULL UNIQUE,         -- hash(error_type|module|sanitized)
    error_type          TEXT NOT NULL,                 -- TimeoutError, KeyError, ToolNotFound, etc.
    module              TEXT NOT NULL,                 -- kernel.task_planner, kernel.tool_dispatch, etc.
    action              TEXT NOT NULL DEFAULT '',      -- nombre de función/step donde falló
    message             TEXT NOT NULL,                 -- error message original (truncado a 2000)
    sanitized_message   TEXT NOT NULL,                 -- mensaje sin TS/UUIDs/paths (para dedupe)
    context             JSONB NOT NULL DEFAULT '{}',   -- run_id, thread_id, tool_calls previos
    embedding           vector(1536),                  -- text-embedding-3-small (NULL si fallback)
    occurrences         INTEGER NOT NULL DEFAULT 1,
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolution          TEXT,                          -- regla aprendida si la hay
    confidence          NUMERIC(3,2) NOT NULL DEFAULT 0.5,  -- 0-1, sube con uso exitoso
    status              TEXT NOT NULL DEFAULT 'open'
                        CHECK (status IN ('open', 'resolved', 'superseded'))
);

-- Índices estructurales
CREATE INDEX IF NOT EXISTS idx_error_memory_signature
    ON error_memory(error_signature);
CREATE INDEX IF NOT EXISTS idx_error_memory_module
    ON error_memory(module);
CREATE INDEX IF NOT EXISTS idx_error_memory_module_action
    ON error_memory(module, action);
CREATE INDEX IF NOT EXISTS idx_error_memory_status_open
    ON error_memory(status) WHERE status = 'open';
CREATE INDEX IF NOT EXISTS idx_error_memory_last_seen
    ON error_memory(last_seen_at DESC);
CREATE INDEX IF NOT EXISTS idx_error_memory_confidence
    ON error_memory(confidence DESC) WHERE status = 'open';

-- Índice vectorial IVFFlat para búsqueda semántica
-- (lists=100 es razonable hasta ~10k filas; ajustar si crece)
CREATE INDEX IF NOT EXISTS idx_error_memory_embedding
    ON error_memory USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ─── 2. Tabla de patrones agregados ───────────────────────────────
CREATE TABLE IF NOT EXISTS error_memory_patterns (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pattern_name        TEXT NOT NULL UNIQUE,
    description         TEXT NOT NULL,
    signature_cluster   TEXT[] NOT NULL,               -- array de error_signatures
    confidence          NUMERIC(3,2) NOT NULL DEFAULT 0.5,
    suggested_rule      TEXT,
    detected_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_validated_at   TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_error_patterns_confidence
    ON error_memory_patterns(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_error_patterns_detected
    ON error_memory_patterns(detected_at DESC);

-- ─── 3. RPC: búsqueda semántica vía cosine similarity ─────────────
-- Llamada desde ErrorMemory.consult() en modo pgvector
CREATE OR REPLACE FUNCTION search_similar_errors(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.78,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    error_signature TEXT,
    error_type TEXT,
    module TEXT,
    action TEXT,
    sanitized_message TEXT,
    resolution TEXT,
    confidence NUMERIC,
    occurrences INTEGER,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        em.id,
        em.error_signature,
        em.error_type,
        em.module,
        em.action,
        em.sanitized_message,
        em.resolution,
        em.confidence,
        em.occurrences,
        1 - (em.embedding <=> query_embedding) as similarity
    FROM error_memory em
    WHERE em.status = 'open'
      AND em.embedding IS NOT NULL
      AND 1 - (em.embedding <=> query_embedding) > match_threshold
    ORDER BY em.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- ─── 4. Trigger: auto-validate timestamp en patterns ──────────────
CREATE OR REPLACE FUNCTION update_error_pattern_validated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_validated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_error_pattern_validated ON error_memory_patterns;
CREATE TRIGGER trg_error_pattern_validated
    BEFORE UPDATE OF confidence ON error_memory_patterns
    FOR EACH ROW
    EXECUTE FUNCTION update_error_pattern_validated();

-- ─── 5. Reglas semilla — lecciones del Hilo B (cierre Sprint 50) ───
-- Errores ya conocidos con resolución preliminar. Confidence 0.7 inicial.
INSERT INTO error_memory (
    error_signature, error_type, module, action,
    message, sanitized_message, resolution, confidence, status
) VALUES
    ('seed_taskplanner_step_timeout',
     'TimeoutError',
     'kernel.task_planner',
     'execute_step',
     'Step timeout exceeded 60s',
     'Step timeout exceeded <N>s',
     'TaskPlanner: incrementar timeout para steps con manus_bridge o code_exec. El default 60s es bajo para tools externas. Sugerencia: 180s para manus_bridge, 90s para code_exec.',
     0.7,
     'open'),
    ('seed_tool_unknown',
     'ValueError',
     'kernel.tool_dispatch',
     '_execute_tool',
     'Unknown tool',
     'Unknown tool: <NAME>',
     'Tool no registrada en tool_dispatch.get_tool_specs() o nombre con typo. Verificar contra inventario canónico de scripts/activate_tools.py.',
     0.8,
     'open'),
    ('seed_supabase_no_connected',
     'AttributeError',
     'kernel.tool_registry',
     'initialize',
     'NoneType object has no attribute connected',
     'NoneType object has no attribute connected',
     'SupabaseClient.connect() falló silenciosamente. Verificar SUPABASE_URL y SUPABASE_SERVICE_KEY en env. El kernel NO debe arrancar si DB no responde — fail-closed.',
     0.75,
     'open'),
    ('seed_embrion_chat_only',
     'DesignError',
     'kernel.embrion_loop',
     '_think_with_router',
     'Reflexion autonoma sin acceso a tools',
     'Reflexion autonoma sin acceso a tools',
     'Sprint 81: el Embrión autónomo (reflexion_autonoma, contribucion_sabio) usa router.execute() chat-only. Resultado: tool_calls_total=0. Solución: Magna Classifier decide ruta graph vs router según contenido del prompt.',
     0.9,
     'open')
ON CONFLICT (error_signature) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-aplicación (ejecutar manualmente):
--
--   SELECT extname FROM pg_extension WHERE extname = 'vector';
--     → debe retornar 1 fila
--
--   SELECT COUNT(*) FROM error_memory WHERE status = 'open';
--     → debe retornar ≥ 4 (las semillas)
--
--   SELECT * FROM search_similar_errors(
--     (SELECT embedding FROM error_memory WHERE error_signature='seed_tool_unknown'),
--     0.5, 5
--   );
--     → si las semillas no tienen embedding (NULL), retorna 0 filas.
--       Eso es esperado hasta que ErrorMemory.record() empiece a generar embeddings.
-- ═══════════════════════════════════════════════════════════════════
