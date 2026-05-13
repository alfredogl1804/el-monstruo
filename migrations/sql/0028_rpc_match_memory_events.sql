-- Migration 0028: rpc_match_memory_events
-- Sprint: ANTI-DORY-OPCION-A (F1) — RPC pgvector real sustituye stub _search_semantic_supabase
-- DSC enforzado: DSC-S-006 v1.1 (RLS por defecto, RPC como SECURITY INVOKER),
--                DSC-S-012 (anti-deriva migraciones, secuencia 0028 post 0027),
--                DSC-G-008 v3 (anti-Goodhart: prueba de carga real con 4,829 embeddings vivos),
--                Obj #15 (Memoria Soberana — búsqueda semántica deja de ser stub),
--                Obj #3 (Mínima Complejidad — un solo RPC, sin abstracciones extras)
-- Fecha: 2026-05-12
-- Owner: Manus Hilo Principal
-- Spec: reports/runtime_reality/RUNTIME_REALITY_REPORT_2026_05_12.md §F1
--
-- Contexto binario:
--   - memory_events.embedding ya existe como vector(1536) — pgvector 0.8.0 instalado
--   - 4,829 filas con embedding NOT NULL (verificado vía sb_sql)
--   - memory_events tiene RLS habilitada (relrowsecurity=true)
--   - índices existentes: pkey, event_id_key, user, type — falta vector index
--
-- Esta migración:
--   1. Crea índice HNSW sobre embedding (cosine ops) — supera ivfflat en recall y latencia (pgvector 0.5+)
--   2. Crea RPC public.match_memory_events(query_embedding, match_threshold, match_count, p_user_id, p_memory_types)
--      con SECURITY INVOKER para respetar RLS de memory_events
--   3. Otorga EXECUTE solo a service_role (RLS del Monstruo, NO anon/authenticated)
--
-- Verificación post-deploy obligatoria (binaria):
--   python3 ~/.monstruo/sb_sql.py sql -q \
--     "SELECT count(*) FROM match_memory_events('[0,...,0]'::vector, 0.0, 5, NULL, NULL)"
--   → debe devolver 5 (sin error)

BEGIN;

-- ============================================================
-- 1) Índice HNSW para búsqueda semántica eficiente
-- ============================================================
-- HNSW (Hierarchical Navigable Small World) es el state-of-the-art en pgvector 0.5+.
-- Ventajas vs ivfflat: mejor recall@k, latencia menor, sin necesidad de tunear nlist/probes.
-- Trade-off: build más lento (aceptable, una sola vez), uso de RAM mayor (4,829 vectores = ~30 MB).
-- m=16 ef_construction=64 son los defaults canónicos de la doc oficial pgvector.
CREATE INDEX IF NOT EXISTS idx_memory_events_embedding_hnsw
    ON public.memory_events
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================
-- 2) RPC match_memory_events — búsqueda semántica con filtros
-- ============================================================
-- SECURITY INVOKER (default) — la RPC corre con permisos del caller, respetando RLS.
-- En el Monstruo, el caller siempre es service_role (vía SUPABASE_SERVICE_KEY),
-- que ya tiene policy "service_role_only" sobre memory_events.
--
-- Firma: igual al stub _search_semantic_supabase + opcional run_id (futuro)
-- Retorna: SearchResult-compatible (event_id, memory_type, content, metadata, score)

CREATE OR REPLACE FUNCTION public.match_memory_events(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    p_user_id text DEFAULT NULL,
    p_memory_types text[] DEFAULT NULL
)
RETURNS TABLE (
    event_id uuid,
    memory_type text,
    run_id uuid,
    user_id text,
    channel text,
    content text,
    metadata jsonb,
    created_at timestamptz,
    score float
)
LANGUAGE plpgsql
STABLE
SECURITY INVOKER
SET search_path = public, pg_temp
AS $$
BEGIN
    RETURN QUERY
    SELECT
        me.event_id,
        me.memory_type,
        me.run_id,
        me.user_id,
        me.channel,
        me.content,
        me.metadata,
        me.created_at,
        (1 - (me.embedding <=> query_embedding))::float AS score
    FROM public.memory_events me
    WHERE
        me.embedding IS NOT NULL
        AND (p_user_id IS NULL OR me.user_id = p_user_id)
        AND (p_memory_types IS NULL OR me.memory_type = ANY(p_memory_types))
        AND (1 - (me.embedding <=> query_embedding)) >= match_threshold
    ORDER BY me.embedding <=> query_embedding ASC
    LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION public.match_memory_events IS
    'Anti-Dory F1 (Sprint 2026-05-12): semantic search RPC over memory_events using pgvector HNSW + cosine. SECURITY INVOKER respects RLS service_role_only policy.';

-- ============================================================
-- 3) Permisos — solo service_role (consistente con DSC-S-006)
-- ============================================================
REVOKE ALL ON FUNCTION public.match_memory_events(vector, float, int, text, text[]) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.match_memory_events(vector, float, int, text, text[]) FROM anon, authenticated;
GRANT  EXECUTE ON FUNCTION public.match_memory_events(vector, float, int, text, text[]) TO service_role;

COMMIT;
