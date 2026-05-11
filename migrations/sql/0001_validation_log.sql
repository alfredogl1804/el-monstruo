-- migrations/sql/0001_validation_log.sql
--
-- Schema canonico de la tabla `validation_log` (DSC-V-001).
--
-- Cualquier claim de estado-del-mundo (pricing benchmarks, audience size,
-- ad formats, keyword research, regulatory landscape, etc.) que el codigo
-- del Monstruo produzca DEBE tener un registro vigente aqui antes de
-- shipear a produccion.
--
-- DOCTRINA DSC-S-006 (RLS por defecto):
--   Esta tabla NACE con RLS habilitado y policy service_role_only.
--   Estado en produccion (Supabase, 2026-05-11):
--     relrowsecurity = true
--     policy validation_log_service_role_only : ALL  TO service_role  USING true WITH CHECK true
--   Universo RLS: 124/124 (sin regresion).
--
-- Aplicar en Supabase via:
--   python3 ~/.monstruo/sb_sql.py sql -f migrations/sql/0001_validation_log.sql
--   (precedente DSC-S-012: migraciones via Management API, no psql directo)
--
-- Origen: DSC-V-001, DSC-G-017, DSC-S-006, DSC-S-012.

CREATE TABLE IF NOT EXISTS validation_log (
    id BIGSERIAL PRIMARY KEY,

    -- Categoria canonica del claim (ej. "cpc_benchmark_2026:saas_b2b",
    -- "model_availability_top_llm", "regulatory_landscape_2026:cip").
    claim_type TEXT NOT NULL,

    -- SHA256[:32] del claim_type + claim_value para dedup eficiente.
    claim_fingerprint TEXT NOT NULL,

    -- Representacion textual del claim validado (cap 1000 chars).
    claim_value TEXT NOT NULL,

    -- Quien valido. Valores canonicos: 'perplexity', 'manus_realtime',
    -- 'alfredo_human', 'gong_call_evidence', 'fireflies_evidence'.
    validator TEXT NOT NULL,

    -- Link a la evidencia (URL Perplexity, screenshot, transcript, etc.).
    evidence_url TEXT,

    -- Cuando se valido (Unix timestamp).
    timestamp_unix DOUBLE PRECISION NOT NULL,

    -- TTL en segundos antes de requerir re-validacion.
    ttl_seconds INTEGER NOT NULL DEFAULT 86400,  -- 24h default

    -- Campos arbitrarios (Perplexity query ID, model usado, confianza, etc.).
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Created at (para orden estable + auditoria).
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indices para los lookups primarios del decorator:
CREATE INDEX IF NOT EXISTS validation_log_claim_type_ts_idx
    ON validation_log (claim_type, timestamp_unix DESC);

CREATE INDEX IF NOT EXISTS validation_log_fingerprint_ts_idx
    ON validation_log (claim_fingerprint, timestamp_unix DESC);

-- RLS canonico (DSC-S-006): toda tabla nueva nace con RLS habilitado.
ALTER TABLE validation_log ENABLE ROW LEVEL SECURITY;

-- Policy unica: solo service_role accede (read + write).
-- El kernel usa SUPABASE_SERVICE_KEY (DSC-S-007) para autenticarse como service_role.
-- anon y authenticated NO tienen acceso por defecto (zero-trust).
CREATE POLICY validation_log_service_role_only
    ON validation_log
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
