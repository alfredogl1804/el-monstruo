-- =================================================================
-- Migration 028 — Sprint 87.2 Bloque 4 Traffic Soberano
-- Tabla e2e_traffic: instrumentación propia, sin GA / Plausible.
-- Idempotente (CREATE TABLE IF NOT EXISTS, CREATE INDEX IF NOT EXISTS)
-- Brand DNA: nombres directos, sin "service" ni "handler"
-- Capa Memento: source of truth de tráfico de landings deployadas
-- Privacy-first: cookie soberana de primera parte, cero tracking externo
-- =================================================================

CREATE TABLE IF NOT EXISTS e2e_traffic (
    id              BIGSERIAL PRIMARY KEY,
    run_id          TEXT NOT NULL REFERENCES e2e_runs(id) ON DELETE CASCADE,
    -- Run del Pipeline E2E del que vino esta visita
    session_id      TEXT NOT NULL,
    -- Cookie de primera parte (UUID soberano del Monstruo)
    event_type      TEXT NOT NULL,
    -- 'pageview' | 'cta_click' | 'unload' | otros futuros
    url             TEXT NOT NULL,
    -- URL completa de la página visitada
    referrer        TEXT,
    -- Referrer (puede ser cadena vacía para tráfico directo)
    device          TEXT NOT NULL,
    -- 'desktop' | 'mobile'
    extra           JSONB,
    -- Datos adicionales por evento (ej: time_on_page_ms, cta text)
    ts              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE e2e_traffic IS 'Sprint 87.2 — Tráfico soberano del Monstruo. Sin GA, sin Plausible, sin trackers externos.';
COMMENT ON COLUMN e2e_traffic.session_id IS 'Cookie de primera parte UUID soberano. SameSite=Lax, TTL 30min.';

-- Índices para queries de dashboard por run y serie temporal
CREATE INDEX IF NOT EXISTS idx_e2e_traffic_run
    ON e2e_traffic (run_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_e2e_traffic_event
    ON e2e_traffic (event_type, ts DESC);
CREATE INDEX IF NOT EXISTS idx_e2e_traffic_session
    ON e2e_traffic (session_id, ts DESC);
