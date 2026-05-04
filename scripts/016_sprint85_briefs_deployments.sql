-- ============================================================================
-- El Monstruo — Sprint 85: Briefs + Deployments (Calidad Comercializable)
-- ============================================================================
-- Tablas para soportar el ciclo Product Architect → Executor → Critic Visual.
--
-- briefs:       Contrato estructurado producido por Product Architect a partir
--               del prompt del usuario. Define vertical, brand, structure y
--               qué información falta (data_missing) para que el Executor no
--               improvise.
--
-- deployments:  Registro de cada deploy generado, con score del Critic Visual,
--               findings, status (building / active / rejected_by_critic /
--               failed) y referencia al brief de origen.
--
-- El Command Center lee `deployments` para mostrar al usuario la cola de
-- proyectos generados, el score que sacaron y la URL para abrirlos.
--
-- Migración idempotente. Compatible con el patrón usado por
-- 015_brand_compliance_log.sql (Sprint 82).
-- ============================================================================

-- ── Tabla: briefs ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS briefs (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    prompt_original         TEXT NOT NULL,
    vertical                TEXT NOT NULL,
    client_brand            JSONB DEFAULT '{}'::jsonb,
    product_meta            JSONB DEFAULT '{}'::jsonb,
    structure               JSONB DEFAULT '{}'::jsonb,
    data_known              JSONB DEFAULT '{}'::jsonb,
    data_missing            JSONB DEFAULT '[]'::jsonb,
    user_question_emitted   TEXT,
    user_response           TEXT,
    architect_model         TEXT,
    architect_cost_usd      NUMERIC(10, 6) DEFAULT 0,
    architect_duration_ms   INTEGER DEFAULT 0,
    created_at              TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at              TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- ── Tabla: deployments ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS deployments (
    id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_name            TEXT NOT NULL,
    url                     TEXT NOT NULL,
    deploy_type             TEXT NOT NULL CHECK (deploy_type IN (
                                'github_pages',
                                'railway',
                                'vercel',
                                'cloudflare_pages',
                                'manual'
                            )),
    brief_id                UUID REFERENCES briefs(id) ON DELETE SET NULL,
    critic_score            INTEGER CHECK (critic_score BETWEEN 0 AND 100),
    quality_passed          BOOLEAN DEFAULT false NOT NULL,
    retry_count             INTEGER DEFAULT 0 NOT NULL,
    screenshot_url          TEXT,
    screenshot_mobile_url   TEXT,
    critic_findings         JSONB DEFAULT '[]'::jsonb,
    critic_breakdown        JSONB DEFAULT '{}'::jsonb,
    status                  TEXT DEFAULT 'building' NOT NULL CHECK (status IN (
                                'building',
                                'active',
                                'rejected_by_critic',
                                'failed',
                                'archived'
                            )),
    user_verdict            TEXT CHECK (user_verdict IN (
                                'commercializable',
                                'not_commercializable',
                                NULL
                            )),
    user_verdict_at         TIMESTAMPTZ,
    metadata                JSONB DEFAULT '{}'::jsonb,
    created_at              TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at              TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- ── Índices ────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_briefs_vertical
    ON briefs (vertical);
CREATE INDEX IF NOT EXISTS idx_briefs_created_at
    ON briefs (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_deployments_project_name
    ON deployments (project_name);
CREATE INDEX IF NOT EXISTS idx_deployments_brief_id
    ON deployments (brief_id);
CREATE INDEX IF NOT EXISTS idx_deployments_status
    ON deployments (status);
CREATE INDEX IF NOT EXISTS idx_deployments_quality_passed
    ON deployments (quality_passed);
CREATE INDEX IF NOT EXISTS idx_deployments_critic_score
    ON deployments (critic_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_deployments_created_at
    ON deployments (created_at DESC);

-- ── Trigger: actualizar updated_at automáticamente ─────────────────────────
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_briefs_updated_at ON briefs;
CREATE TRIGGER trg_briefs_updated_at
    BEFORE UPDATE ON briefs
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

DROP TRIGGER IF EXISTS trg_deployments_updated_at ON deployments;
CREATE TRIGGER trg_deployments_updated_at
    BEFORE UPDATE ON deployments
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

-- ── Row Level Security ─────────────────────────────────────────────────────
ALTER TABLE briefs ENABLE ROW LEVEL SECURITY;
ALTER TABLE deployments ENABLE ROW LEVEL SECURITY;

-- service_role tiene acceso total (kernel del Monstruo)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'briefs'
          AND policyname = 'briefs_service_role_all'
    ) THEN
        CREATE POLICY briefs_service_role_all ON briefs
            FOR ALL TO service_role
            USING (true) WITH CHECK (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'deployments'
          AND policyname = 'deployments_service_role_all'
    ) THEN
        CREATE POLICY deployments_service_role_all ON deployments
            FOR ALL TO service_role
            USING (true) WITH CHECK (true);
    END IF;

    -- authenticated: read-only para futuras integraciones del Command Center
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'deployments'
          AND policyname = 'deployments_authenticated_read'
    ) THEN
        CREATE POLICY deployments_authenticated_read ON deployments
            FOR SELECT TO authenticated
            USING (true);
    END IF;
END;
$$;

-- ── Comentarios para documentación in-DB ───────────────────────────────────
COMMENT ON TABLE briefs IS 'Sprint 85: contrato del Product Architect — entrada estructurada al Executor';
COMMENT ON TABLE deployments IS 'Sprint 85: registro de cada deploy con score del Critic Visual';
COMMENT ON COLUMN briefs.vertical IS 'Slug del vertical: education_arts, saas_b2b, restaurant, professional_services, ecommerce_artisanal, marketplace_services';
COMMENT ON COLUMN briefs.data_missing IS 'Array de keys que el Architect detectó como faltantes en el prompt original';
COMMENT ON COLUMN deployments.critic_score IS 'Score del Critic Visual (0-100). >= 80 = quality_passed=true';
COMMENT ON COLUMN deployments.critic_breakdown IS 'Score por componente: {estructura, contenido, visual, brand_fit, mobile, performance, cta, meta_tags}';
COMMENT ON COLUMN deployments.user_verdict IS 'Veredicto humano de Alfredo (Test 3): commercializable | not_commercializable';

-- ============================================================================
-- Fin de migración 016 — Sprint 85 (Calidad Comercializable)
-- ============================================================================
