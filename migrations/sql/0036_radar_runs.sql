-- =============================================================================
-- Migration 0036 — radar_runs + radar_run_repos (Persistencia Radar GitHub Biblia)
-- =============================================================================
-- Sprint: AUDITOR-CATASTROS-001
-- Doctrina: T1 firmada 2026-05-16 (Alfredo) + DSC-S-006 v1.1 (RLS por defecto)
-- Origen: Auditoría externa Perplexity sonar-reasoning-pro + decisión arquitectónica T1
--
-- Propósito:
--   Persistir el histórico de ejecuciones del Radar GitHub Biblia (sistema
--   externo en repo `biblia-github-motor`, cron diario via launchd 7AM CST)
--   en Supabase como Single Source of Truth (SOT) histórico, sin contaminar
--   `public.documents` (que es Catálogo Soberano del Monstruo / LightRAG).
--
-- Contexto de la decisión:
--   El Radar intentaba escribir en `public.documents` con columna `content`
--   inexistente, fallando con PGRST204 en cada cron desde su creación.
--   Adaptar el Radar a `documents` requería inventar doc_id/file_id/relative_path
--   sintéticos y romper el contrato semántico del Catálogo Soberano.
--
-- Diseño:
--   - Append-only: cada run es un evento inmutable con estado completo.
--   - Schema padre-hija: radar_runs (1 fila/día) + radar_run_repos (1 fila/repo/día).
--   - jsonb para summary/config/metadata (NO json strings).
--   - run_date UNIQUE: idempotencia natural si el cron se ejecuta dos veces.
--   - Sin FKs externas en esta fase: model_used queda como text libre.
--
-- RLS: DSC-S-006 v1.1.
-- =============================================================================

BEGIN;

-- =============================================================================
-- TABLA 1: radar_runs (cabecera de cada ejecución del Radar)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.radar_runs (
    run_id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    run_date                 DATE         NOT NULL,
    period_start             TIMESTAMPTZ,
    period_end               TIMESTAMPTZ,
    status                   TEXT         NOT NULL,
    total_repos_scanned      INTEGER      NOT NULL,
    total_repos_considered   INTEGER,
    total_repos_recommended  INTEGER,
    adoptar_overall          BOOLEAN,
    decision_notes           TEXT,
    model_used               TEXT         NOT NULL,
    model_version            TEXT,
    config                   JSONB        NOT NULL DEFAULT '{}'::jsonb,
    summary                  JSONB,
    report_md                TEXT,
    metadata                 JSONB        NOT NULL DEFAULT '{}'::jsonb,
    created_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT radar_runs_status_valid CHECK (
        status IN ('success', 'partial', 'failed')
    ),
    CONSTRAINT radar_runs_total_scanned_nonneg CHECK (
        total_repos_scanned >= 0
    ),
    CONSTRAINT radar_runs_model_used_nonempty CHECK (
        char_length(model_used) > 0
    ),
    CONSTRAINT radar_runs_period_consistent CHECK (
        period_start IS NULL OR period_end IS NULL OR period_start <= period_end
    )
);

-- Idempotencia natural: un run por día calendario.
CREATE UNIQUE INDEX IF NOT EXISTS radar_runs_run_date_uniq
    ON public.radar_runs (run_date);

CREATE INDEX IF NOT EXISTS radar_runs_status_created_idx
    ON public.radar_runs (status, created_at DESC);

CREATE INDEX IF NOT EXISTS radar_runs_model_used_idx
    ON public.radar_runs (model_used);

CREATE INDEX IF NOT EXISTS radar_runs_created_at_idx
    ON public.radar_runs (created_at DESC);

COMMENT ON TABLE public.radar_runs IS
'Cabecera append-only de ejecuciones del Radar GitHub Biblia. '
'Una fila por ejecución diaria del cron (launchd 7AM CST). '
'SOT histórico del Radar — NO mezclar con public.documents (Catálogo Soberano). '
'Sprint AUDITOR-CATASTROS-001. T1 firmada 2026-05-16.';

COMMENT ON COLUMN public.radar_runs.run_date IS
'Fecha calendario del run (UNIQUE — un run por día). Si se reintenta el mismo día, usar UPSERT.';

COMMENT ON COLUMN public.radar_runs.status IS
'success | partial | failed. partial = se completó parcialmente con errores no fatales.';

COMMENT ON COLUMN public.radar_runs.config IS
'Configuración con la que corrió el Radar (thresholds, filters, reposet) — para reproducibilidad.';

COMMENT ON COLUMN public.radar_runs.summary IS
'Resumen máquina-readable: { top_repos: [...], scores: {...}, métricas agregadas }. '
'Equivalente al campo "content" que se intentaba meter en documents.';

COMMENT ON COLUMN public.radar_runs.report_md IS
'Reporte humano en Markdown (mismo que se sube a Drive). Indexable para RAG futuro.';


-- =============================================================================
-- TABLA 2: radar_run_repos (detalle por repo escaneado en cada run)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.radar_run_repos (
    run_id            UUID         NOT NULL,
    repo_full_name    TEXT         NOT NULL,
    repo_url          TEXT         NOT NULL,
    rank              INTEGER,
    score             NUMERIC(6,3),
    decision          TEXT         NOT NULL,
    rationale         TEXT,
    categories        TEXT[]       NOT NULL DEFAULT ARRAY[]::TEXT[],
    metadata          JSONB        NOT NULL DEFAULT '{}'::jsonb,

    PRIMARY KEY (run_id, repo_full_name),

    CONSTRAINT radar_run_repos_run_fk
        FOREIGN KEY (run_id)
        REFERENCES public.radar_runs(run_id)
        ON DELETE CASCADE,

    CONSTRAINT radar_run_repos_decision_valid CHECK (
        decision IN ('adopt', 'watch', 'ignore')
    ),
    CONSTRAINT radar_run_repos_repo_full_name_nonempty CHECK (
        char_length(repo_full_name) > 0
    ),
    CONSTRAINT radar_run_repos_repo_url_nonempty CHECK (
        char_length(repo_url) > 0
    ),
    CONSTRAINT radar_run_repos_score_range CHECK (
        score IS NULL OR (score >= 0.0 AND score <= 1000.0)
    ),
    CONSTRAINT radar_run_repos_rank_positive CHECK (
        rank IS NULL OR rank > 0
    )
);

CREATE INDEX IF NOT EXISTS radar_run_repos_repo_full_name_idx
    ON public.radar_run_repos (repo_full_name);

CREATE INDEX IF NOT EXISTS radar_run_repos_decision_idx
    ON public.radar_run_repos (decision);

CREATE INDEX IF NOT EXISTS radar_run_repos_score_idx
    ON public.radar_run_repos (score DESC NULLS LAST)
    WHERE score IS NOT NULL;

COMMENT ON TABLE public.radar_run_repos IS
'Detalle por repo escaneado en cada run del Radar. '
'Permite análisis de evolución de scores, joins futuros con catastros. '
'Append-only por (run_id, repo_full_name). ON DELETE CASCADE desde radar_runs.';

COMMENT ON COLUMN public.radar_run_repos.decision IS
'adopt | watch | ignore. Decisión del clasificador LLM sobre el repo en este run.';

COMMENT ON COLUMN public.radar_run_repos.score IS
'Score normalizado del repo en este run. Semántica definida por el Radar (típicamente score_compuesto).';

COMMENT ON COLUMN public.radar_run_repos.categories IS
'Tags de categorización del repo (ej. agentic_memory, observability, knowledge_graphs).';


-- =============================================================================
-- RLS por defecto (DSC-S-006 v1.1)
-- =============================================================================

ALTER TABLE public.radar_runs       ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.radar_run_repos  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS radar_runs_service_role_only       ON public.radar_runs;
DROP POLICY IF EXISTS radar_run_repos_service_role_only  ON public.radar_run_repos;

CREATE POLICY radar_runs_service_role_only
    ON public.radar_runs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY radar_run_repos_service_role_only
    ON public.radar_run_repos
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

REVOKE ALL ON public.radar_runs       FROM PUBLIC, anon, authenticated;
REVOKE ALL ON public.radar_run_repos  FROM PUBLIC, anon, authenticated;

GRANT SELECT, INSERT, UPDATE ON public.radar_runs       TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.radar_run_repos TO service_role;
-- DELETE en radar_run_repos permitido solo para idempotencia de re-runs (CASCADE).


-- =============================================================================
-- Verificación automática post-apply (DSC-S-006 v1.1 enforcement)
-- =============================================================================

DO $$
DECLARE
    v_rls_runs       BOOLEAN;
    v_rls_repos      BOOLEAN;
    v_policies_runs  INTEGER;
    v_policies_repos INTEGER;
BEGIN
    SELECT relrowsecurity INTO v_rls_runs
    FROM pg_class
    WHERE relname = 'radar_runs' AND relnamespace = 'public'::regnamespace;

    SELECT relrowsecurity INTO v_rls_repos
    FROM pg_class
    WHERE relname = 'radar_run_repos' AND relnamespace = 'public'::regnamespace;

    IF NOT v_rls_runs THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: radar_runs creada sin RLS habilitado';
    END IF;

    IF NOT v_rls_repos THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: radar_run_repos creada sin RLS habilitado';
    END IF;

    SELECT COUNT(*) INTO v_policies_runs
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'radar_runs';

    SELECT COUNT(*) INTO v_policies_repos
    FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'radar_run_repos';

    IF v_policies_runs = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: radar_runs sin policies explícitas';
    END IF;

    IF v_policies_repos = 0 THEN
        RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION: radar_run_repos sin policies explícitas';
    END IF;

    RAISE NOTICE 'radar_runs OK: RLS=%, policies=%', v_rls_runs, v_policies_runs;
    RAISE NOTICE 'radar_run_repos OK: RLS=%, policies=%', v_rls_repos, v_policies_repos;
END $$;

COMMIT;
