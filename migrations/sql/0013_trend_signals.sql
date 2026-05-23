-- migrations/sql/0013_trend_signals.sql
--
-- Sprint TRANSVERSAL-001 T5 — Tabla trend_signals.
--
-- Almacena senales de tendencias capturadas por TendenciasLayer desde
-- fuentes canonicas (SUPPORTED_DATA_SOURCES en
-- kernel/transversales/tendencias/_canonical_constraints.py).
--
-- Cada row es una observacion atomica de un signal_type detectado en
-- una fuente especifica para un vertical especifico, con magnitud (score)
-- y metadata estructurada.
--
-- DOCTRINA DSC-S-006 (RLS por defecto):
--   Esta tabla NACE con RLS habilitado y policy service_role_only.
--   Universo RLS post-aplicacion debera ser 125/125 (validation_log + esta).
--
-- Aplicar en Supabase via:
--   python3 ~/.monstruo/sb_sql.py sql -f migrations/sql/0013_trend_signals.sql
--   (precedente DSC-S-012: Management API, no psql directo)
--
-- Origen: TendenciasLayer (Capa 4 de las 7 Transversales), DSC-G-002,
-- DSC-V-001, DSC-S-006, DSC-S-012.

CREATE TABLE IF NOT EXISTS trend_signals (
    id BIGSERIAL PRIMARY KEY,

    -- Vertical al que aplica la senal (CIP, LIKETICKETS, KUKULKAN_365, etc.).
    -- No usamos FK porque verticals viven como enum en codigo, no como tabla.
    vertical TEXT NOT NULL,

    -- Una de las SUPPORTED_DATA_SOURCES (blockchain_analytics,
    -- real_estate_market_reports, regulatory_feeds, events_calendar,
    -- sports_leagues_feeds, social_trends, search_trend_signals, etc.).
    source TEXT NOT NULL,

    -- Tipo de signal canonico (ej. 'pricing_change', 'volume_spike',
    -- 'regulatory_update', 'competitor_launch', 'weather_alert').
    signal_type TEXT NOT NULL,

    -- Magnitud numerica de la senal (z-score, % delta, intensity index).
    -- Cap 1000 para evitar abuso. Negativos permitidos (senal contraria).
    score DOUBLE PRECISION NOT NULL,

    -- Detail del signal: link, descripcion, full payload, etc.
    -- Schema esperado per source_type esta documentado en
    -- kernel/transversales/tendencias/_canonical_constraints.py.
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Cuando se observo la senal (Unix timestamp).
    observed_at_unix DOUBLE PRECISION NOT NULL,

    -- TTL en segundos antes de considerar la senal "stale" para alerting.
    -- Default 24h. Critical signals pueden tener TTL mas corto (3600s).
    ttl_seconds INTEGER NOT NULL DEFAULT 86400,

    -- Quien capturo la senal: 'perplexity', 'rss_feed_scraper',
    -- 'polygon_api', 'manus_realtime', 'cron_job_<name>'.
    collector TEXT NOT NULL,

    -- Created at (para orden estable + auditoria).
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indices para lookups primarios del monitor:
CREATE INDEX IF NOT EXISTS trend_signals_vertical_observed_idx
    ON trend_signals (vertical, observed_at_unix DESC);

CREATE INDEX IF NOT EXISTS trend_signals_signal_type_observed_idx
    ON trend_signals (signal_type, observed_at_unix DESC);

CREATE INDEX IF NOT EXISTS trend_signals_source_observed_idx
    ON trend_signals (source, observed_at_unix DESC);

-- RLS canonico (DSC-S-006): toda tabla nueva nace con RLS habilitado.
ALTER TABLE trend_signals ENABLE ROW LEVEL SECURITY;

-- Policy unica: solo service_role accede (read + write).
-- El kernel usa SUPABASE_SERVICE_KEY (DSC-S-007) para autenticarse.
-- anon y authenticated NO tienen acceso (zero-trust).
CREATE POLICY trend_signals_service_role_only
    ON trend_signals
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
