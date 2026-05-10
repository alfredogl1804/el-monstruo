-- =============================================================================
-- Migracion 0008 - Sprint S-002.6 - Tarea 1
-- RLS sobre 85 tablas P2 + 1 matview (catastro_metricas_diarias)
-- =============================================================================
-- Patron: service_role_only (identico a 0004-0007).
-- Atomicidad: BEGIN/COMMIT. Smoke test post-aplicacion obligatorio.
-- DSC-S-006 (RLS default), DSC-G-008 v2 (audit pre-cierre).
-- =============================================================================

BEGIN;

-- 1/85: a2a_agents
ALTER TABLE public.a2a_agents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.a2a_agents
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.a2a_agents IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 2/85: active_missions
ALTER TABLE public.active_missions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.active_missions
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.active_missions IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 3/85: agui_channel_audit
ALTER TABLE public.agui_channel_audit ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.agui_channel_audit
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.agui_channel_audit IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 4/85: articulo_objetivos
ALTER TABLE public.articulo_objetivos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.articulo_objetivos
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.articulo_objetivos IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 5/85: articulos
ALTER TABLE public.articulos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.articulos
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.articulos IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 6/85: background_jobs
ALTER TABLE public.background_jobs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.background_jobs
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.background_jobs IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 7/85: behavior_mutations
ALTER TABLE public.behavior_mutations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.behavior_mutations
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.behavior_mutations IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 8/85: budget_state
ALTER TABLE public.budget_state ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.budget_state
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.budget_state IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 9/85: cadena_custodia
ALTER TABLE public.cadena_custodia ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.cadena_custodia
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.cadena_custodia IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 10/85: checkpoint_blobs
ALTER TABLE public.checkpoint_blobs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.checkpoint_blobs
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.checkpoint_blobs IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 11/85: checkpoint_migrations
ALTER TABLE public.checkpoint_migrations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.checkpoint_migrations
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.checkpoint_migrations IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 12/85: checkpoint_writes
ALTER TABLE public.checkpoint_writes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.checkpoint_writes
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.checkpoint_writes IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 13/85: checkpoints
ALTER TABLE public.checkpoints ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.checkpoints
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.checkpoints IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 14/85: chunk_embeddings
ALTER TABLE public.chunk_embeddings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.chunk_embeddings
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.chunk_embeddings IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 15/85: chunks
ALTER TABLE public.chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.chunks
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.chunks IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 16/85: circuit_breaker_log
ALTER TABLE public.circuit_breaker_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.circuit_breaker_log
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.circuit_breaker_log IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 17/85: comentarios
ALTER TABLE public.comentarios ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.comentarios
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.comentarios IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 18/85: datos_campo
ALTER TABLE public.datos_campo ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.datos_campo
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.datos_campo IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 19/85: decision_records
ALTER TABLE public.decision_records ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.decision_records
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.decision_records IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 20/85: documents
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.documents
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.documents IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 21/85: e2e_runs
ALTER TABLE public.e2e_runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.e2e_runs
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.e2e_runs IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 22/85: e2e_step_log
ALTER TABLE public.e2e_step_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.e2e_step_log
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.e2e_step_log IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 23/85: e2e_traffic
ALTER TABLE public.e2e_traffic ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.e2e_traffic
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.e2e_traffic IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 24/85: elecciones_historicas
ALTER TABLE public.elecciones_historicas ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.elecciones_historicas
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.elecciones_historicas IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 25/85: encuestas_tracking
ALTER TABLE public.encuestas_tracking ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.encuestas_tracking
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.encuestas_tracking IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 26/85: firma_tecnica
ALTER TABLE public.firma_tecnica ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.firma_tecnica
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.firma_tecnica IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 27/85: github_radar_reports
ALTER TABLE public.github_radar_reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.github_radar_reports
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.github_radar_reports IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 28/85: github_radar_scans
ALTER TABLE public.github_radar_scans ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.github_radar_scans
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.github_radar_scans IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 29/85: governance_log
ALTER TABLE public.governance_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.governance_log
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.governance_log IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 30/85: job_executions
ALTER TABLE public.job_executions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.job_executions
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.job_executions IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 31/85: lightrag_doc_chunks
ALTER TABLE public.lightrag_doc_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_doc_chunks
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_doc_chunks IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 32/85: lightrag_doc_full
ALTER TABLE public.lightrag_doc_full ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_doc_full
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_doc_full IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 33/85: lightrag_doc_status
ALTER TABLE public.lightrag_doc_status ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_doc_status
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_doc_status IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 34/85: lightrag_entity_chunks
ALTER TABLE public.lightrag_entity_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_entity_chunks
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_entity_chunks IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 35/85: lightrag_full_entities
ALTER TABLE public.lightrag_full_entities ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_full_entities
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_full_entities IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 36/85: lightrag_full_relations
ALTER TABLE public.lightrag_full_relations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_full_relations
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_full_relations IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 37/85: lightrag_llm_cache
ALTER TABLE public.lightrag_llm_cache ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_llm_cache
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_llm_cache IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 38/85: lightrag_relation_chunks
ALTER TABLE public.lightrag_relation_chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_relation_chunks
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_relation_chunks IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 39/85: lightrag_vdb_chunks_gemini_embedding_001_1536d
ALTER TABLE public.lightrag_vdb_chunks_gemini_embedding_001_1536d ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_vdb_chunks_gemini_embedding_001_1536d
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_vdb_chunks_gemini_embedding_001_1536d IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 40/85: lightrag_vdb_chunks_text_embedding_3_small_1536d
ALTER TABLE public.lightrag_vdb_chunks_text_embedding_3_small_1536d ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_vdb_chunks_text_embedding_3_small_1536d
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_vdb_chunks_text_embedding_3_small_1536d IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 41/85: lightrag_vdb_entity_gemini_embedding_001_1536d
ALTER TABLE public.lightrag_vdb_entity_gemini_embedding_001_1536d ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_vdb_entity_gemini_embedding_001_1536d
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_vdb_entity_gemini_embedding_001_1536d IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 42/85: lightrag_vdb_entity_text_embedding_3_small_1536d
ALTER TABLE public.lightrag_vdb_entity_text_embedding_3_small_1536d ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_vdb_entity_text_embedding_3_small_1536d
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_vdb_entity_text_embedding_3_small_1536d IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 43/85: lightrag_vdb_relation_gemini_embedding_001_1536d
ALTER TABLE public.lightrag_vdb_relation_gemini_embedding_001_1536d ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_vdb_relation_gemini_embedding_001_1536d
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_vdb_relation_gemini_embedding_001_1536d IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 44/85: lightrag_vdb_relation_text_embedding_3_small_1536d
ALTER TABLE public.lightrag_vdb_relation_text_embedding_3_small_1536d ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.lightrag_vdb_relation_text_embedding_3_small_1536d
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.lightrag_vdb_relation_text_embedding_3_small_1536d IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 45/85: loop_detection_log
ALTER TABLE public.loop_detection_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.loop_detection_log
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.loop_detection_log IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 46/85: medios
ALTER TABLE public.medios ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.medios
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.medios IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 47/85: mem0
ALTER TABLE public.mem0 ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.mem0
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.mem0 IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 48/85: mem0migrations
ALTER TABLE public.mem0migrations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.mem0migrations
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.mem0migrations IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 49/85: mempalace_episodes
ALTER TABLE public.mempalace_episodes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.mempalace_episodes
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.mempalace_episodes IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 50/85: mempalace_semantic
ALTER TABLE public.mempalace_semantic ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.mempalace_semantic
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.mempalace_semantic IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 51/85: menciones_bm
ALTER TABLE public.menciones_bm ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.menciones_bm
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.menciones_bm IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 52/85: monstruo_graph_snapshots
ALTER TABLE public.monstruo_graph_snapshots ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.monstruo_graph_snapshots
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.monstruo_graph_snapshots IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 53/85: objetivos
ALTER TABLE public.objetivos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.objetivos
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.objetivos IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 54/85: operator_preferences
ALTER TABLE public.operator_preferences ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.operator_preferences
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.operator_preferences IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 55/85: predictions
ALTER TABLE public.predictions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.predictions
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.predictions IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 56/85: pricing_catalog
ALTER TABLE public.pricing_catalog ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.pricing_catalog
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.pricing_catalog IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 57/85: scheduled_jobs
ALTER TABLE public.scheduled_jobs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.scheduled_jobs
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.scheduled_jobs IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 58/85: scheduled_tasks
ALTER TABLE public.scheduled_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.scheduled_tasks
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.scheduled_tasks IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 59/85: secciones_electorales
ALTER TABLE public.secciones_electorales ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.secciones_electorales
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.secciones_electorales IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 60/85: security_web_events
ALTER TABLE public.security_web_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.security_web_events
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.security_web_events IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 61/85: seeding_cycles
ALTER TABLE public.seeding_cycles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.seeding_cycles
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.seeding_cycles IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 62/85: simulation_results
ALTER TABLE public.simulation_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.simulation_results
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.simulation_results IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 63/85: simulation_rounds
ALTER TABLE public.simulation_rounds ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.simulation_rounds
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.simulation_rounds IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 64/85: simulations
ALTER TABLE public.simulations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.simulations
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.simulations IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 65/85: summaries
ALTER TABLE public.summaries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.summaries
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.summaries IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 66/85: tool_bindings
ALTER TABLE public.tool_bindings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.tool_bindings
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.tool_bindings IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 67/85: tool_executions
ALTER TABLE public.tool_executions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.tool_executions
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.tool_executions IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 68/85: tool_registry
ALTER TABLE public.tool_registry ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.tool_registry
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.tool_registry IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 69/85: ui_view_state
ALTER TABLE public.ui_view_state ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.ui_view_state
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.ui_view_state IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 70/85: usage_daily
ALTER TABLE public.usage_daily ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.usage_daily
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.usage_daily IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 71/85: usage_log
ALTER TABLE public.usage_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.usage_log
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.usage_log IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 72/85: v5_accounts
ALTER TABLE public.v5_accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_accounts
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_accounts IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 73/85: v5_comments
ALTER TABLE public.v5_comments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_comments
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_comments IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 74/85: v5_coordination_scores
ALTER TABLE public.v5_coordination_scores ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_coordination_scores
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_coordination_scores IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 75/85: v5_discovery_queue
ALTER TABLE public.v5_discovery_queue ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_discovery_queue
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_discovery_queue IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 76/85: v5_doc_links
ALTER TABLE public.v5_doc_links ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_doc_links
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_doc_links IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 77/85: v5_doc_similarity
ALTER TABLE public.v5_doc_similarity ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_doc_similarity
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_doc_similarity IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 78/85: v5_documents
ALTER TABLE public.v5_documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_documents
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_documents IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 79/85: v5_entities
ALTER TABLE public.v5_entities ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_entities
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_entities IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 80/85: v5_hashtags
ALTER TABLE public.v5_hashtags ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_hashtags
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_hashtags IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 81/85: v5_investigation_log
ALTER TABLE public.v5_investigation_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_investigation_log
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_investigation_log IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 82/85: v5_propagation_edges
ALTER TABLE public.v5_propagation_edges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_propagation_edges
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_propagation_edges IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 83/85: v5_sources
ALTER TABLE public.v5_sources ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.v5_sources
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.v5_sources IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 84/85: verification_results
ALTER TABLE public.verification_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.verification_results
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.verification_results IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- 85/85: write_policy_log
ALTER TABLE public.write_policy_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_only" ON public.write_policy_log
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
COMMENT ON POLICY "service_role_only" ON public.write_policy_log IS
  'Sprint S-002.6 (2026-05-10): completacion universo RLS. DSC-S-006.';

-- Matview catastro_metricas_diarias (REVOKE pattern)
REVOKE ALL ON public.catastro_metricas_diarias FROM PUBLIC;
REVOKE ALL ON public.catastro_metricas_diarias FROM anon;
REVOKE ALL ON public.catastro_metricas_diarias FROM authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.catastro_metricas_diarias TO service_role;
COMMENT ON MATERIALIZED VIEW public.catastro_metricas_diarias IS
  'Sprint S-002.6 (2026-05-10): REVOKE PUBLIC + GRANT service_role. DSC-S-006.';

COMMIT;
