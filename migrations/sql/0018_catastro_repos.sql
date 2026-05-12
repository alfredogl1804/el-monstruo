-- ============================================================================
-- Migracion: 0018_catastro_repos
-- Sprint:    CATASTRO-C-SLICE-001 (slice vertical end-to-end)
-- Autor:     Manus (Hilo B - Ejecutor Tecnico)
-- Fecha:     2026-05-11
--
-- Proposito:
-- Sexta tabla del Catastro. Persiste repos descubiertos por el agents-radar
-- diario (https://agents-radar-mcp.duanyytop.workers.dev) cuando el embrion
-- ejecuta _check_agents_radar(). Cierra el bucle descubrir->catalogar->decidir
-- definido en el spec_integracion_radar_catastro.md (Sprint 86.5 entrega C).
--
-- Doctrina:
--  - DSC-S-006: RLS por defecto + service_role_only.
--  - DSC-G-008 v2: validacion idempotente (CREATE IF NOT EXISTS).
--  - Anti-Dory: schema fiel al spec entrega C, columnas tipadas, indices GIN
--    sobre topics (consultas por tags semanticos del radar).
-- ============================================================================
BEGIN;

CREATE TABLE IF NOT EXISTS public.catastro_repos (
    id                   TEXT        PRIMARY KEY,
    nombre               TEXT        NOT NULL,
    proveedor            TEXT        NOT NULL,
    url                  TEXT        NOT NULL,
    descripcion          TEXT,
    fuente               TEXT        NOT NULL,
    stars_count          INTEGER     DEFAULT 0,
    last_release_tag     TEXT,
    last_release_date    TIMESTAMPTZ,
    license              TEXT,
    topics               JSONB       NOT NULL DEFAULT '[]'::jsonb,
    model_card_url       TEXT,
    radar_report_ref     TEXT,
    radar_report_date    DATE,
    radar_discovered_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    classification       JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.catastro_repos IS
  'Sprint CATASTRO-C-SLICE-001: persistencia de repos descubiertos por agents-radar.';
COMMENT ON COLUMN public.catastro_repos.id IS
  'ID compuesto: github:owner/repo, hf:owner/repo, prodhunt:slug, etc.';
COMMENT ON COLUMN public.catastro_repos.fuente IS
  'Fuente del radar: github_trending, huggingface, product_hunt, hn, arxiv, anthropic, openai, dev_to, lobsters.';
COMMENT ON COLUMN public.catastro_repos.classification IS
  'Output del radar_classifier (tags + categoria + razonamiento + confianza).';

-- Indices
CREATE INDEX IF NOT EXISTS idx_catastro_repos_stars
    ON public.catastro_repos (stars_count DESC);
CREATE INDEX IF NOT EXISTS idx_catastro_repos_topics
    ON public.catastro_repos USING GIN (topics);
CREATE INDEX IF NOT EXISTS idx_catastro_repos_classification
    ON public.catastro_repos USING GIN (classification);
CREATE INDEX IF NOT EXISTS idx_catastro_repos_radar_date
    ON public.catastro_repos (radar_report_date DESC);
CREATE INDEX IF NOT EXISTS idx_catastro_repos_fuente
    ON public.catastro_repos (fuente);

-- Trigger updated_at (reusa funcion existente del proyecto si existe)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc WHERE proname = 'set_updated_at_now'
    ) THEN
        CREATE FUNCTION public.set_updated_at_now() RETURNS TRIGGER AS $func$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;
    END IF;
END $$;

DROP TRIGGER IF EXISTS trg_catastro_repos_updated_at ON public.catastro_repos;
CREATE TRIGGER trg_catastro_repos_updated_at
    BEFORE UPDATE ON public.catastro_repos
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_now();

-- RLS: service_role_only (DSC-S-006 v1.1)
ALTER TABLE public.catastro_repos ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename  = 'catastro_repos'
          AND policyname = 'service_role_only'
    ) THEN
        CREATE POLICY service_role_only
            ON public.catastro_repos
            AS PERMISSIVE
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

REVOKE ALL ON public.catastro_repos FROM PUBLIC, anon, authenticated;
GRANT  ALL ON public.catastro_repos TO service_role;

COMMIT;
