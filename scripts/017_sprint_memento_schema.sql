-- ============================================================================
-- El Monstruo — Sprint Memento — Bloque 1 — Schema Supabase Capa Memoria Soberana
-- ============================================================================
-- Migration: 017
-- Sprint: Memento (Capa Memoria Soberana v1.0)
-- Autor: [Hilo Manus Ejecutor]
-- Fecha: 2026-05-04
--
-- Implementa la infraestructura formal de la Capa Memento (Capa 8 de
-- Transversalidad) que convierte el folklore anti-Síndrome-Dory disperso
-- en hilos Manus en contratos auditables del kernel.
--
-- 3 tablas:
--   1. memento_validations          — log de cada call a /v1/memento/validate
--   2. memento_critical_operations  — catálogo de operaciones críticas
--   3. memento_sources_of_truth     — catálogo de fuentes de verdad
--
-- Decisiones de diseño:
--   - id BIGSERIAL en validations (volumen alto, FK no necesaria)
--   - id TEXT (slug) en critical_operations y sources_of_truth (legible)
--   - context_used JSONB para flexibilidad (cada operación tiene shape distinto)
--   - validation_id TEXT formato "mv_<timestamp>_<hash6>" para correlación cliente-servidor
--   - RLS: read service_role only, write service_role only (kernel es gatekeeper)
--   - Índices: timestamp desc + hilo_id + operation + validation_status
-- ============================================================================

-- ============================================================================
-- TABLA 1: memento_validations — Log de cada validación
-- ============================================================================
CREATE TABLE IF NOT EXISTS memento_validations (
    -- Identidad
    id BIGSERIAL PRIMARY KEY,
    validation_id TEXT NOT NULL UNIQUE,         -- "mv_2026-05-04T18:30:42_a1b2c3"

    -- Quién y qué
    hilo_id TEXT NOT NULL,                       -- "hilo_manus_ticketlike", "hilo_manus_ejecutor", etc.
    operation TEXT NOT NULL,                     -- "rotate_credential", "sql_against_production", etc.

    -- Contexto declarado por el hilo
    context_used JSONB NOT NULL,                 -- {"host": "...", "user": "...", "credential_hash_first_8": "..."}
    intent_summary TEXT,                         -- texto libre, propósito declarado

    -- Resultado de la validación
    validation_status TEXT NOT NULL              -- 'ok' | 'discrepancy_detected' | 'unknown_operation' | 'source_unavailable'
        CHECK (validation_status IN ('ok', 'discrepancy_detected', 'unknown_operation', 'source_unavailable')),
    proceed BOOLEAN NOT NULL,                    -- true => hilo puede proceder; false => debe abortar
    discrepancy JSONB,                           -- detalles de discrepancia si validation_status='discrepancy_detected'
    contamination_warning BOOLEAN DEFAULT FALSE, -- v1.0: flag no bloqueante; v1.1: puede ser bloqueante
    contamination_evidence JSONB,                -- razones del flag (heurísticas que dispararon)

    -- Auditoría
    context_freshness_seconds INTEGER,           -- segundos desde la última actualización de la fuente de verdad
    source_consulted TEXT,                       -- ruta o identificador de la fuente consultada
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Remediación sugerida (si proceed=false)
    remediation TEXT
);

CREATE INDEX IF NOT EXISTS idx_memento_validations_ts
    ON memento_validations (ts DESC);

CREATE INDEX IF NOT EXISTS idx_memento_validations_hilo
    ON memento_validations (hilo_id, ts DESC);

CREATE INDEX IF NOT EXISTS idx_memento_validations_operation
    ON memento_validations (operation, ts DESC);

CREATE INDEX IF NOT EXISTS idx_memento_validations_status
    ON memento_validations (validation_status, ts DESC);

CREATE INDEX IF NOT EXISTS idx_memento_validations_contamination
    ON memento_validations (contamination_warning, ts DESC)
    WHERE contamination_warning = TRUE;

COMMENT ON TABLE memento_validations IS
    'Sprint Memento v1.0 — log de cada validación de contexto operativo. Métrica directa del Objetivo #15 (Memoria Soberana).';

-- ============================================================================
-- TABLA 2: memento_critical_operations — Catálogo de operaciones críticas
-- ============================================================================
CREATE TABLE IF NOT EXISTS memento_critical_operations (
    -- Identidad
    id TEXT PRIMARY KEY,                         -- slug, ej. "rotate_credential"
    nombre TEXT NOT NULL,                        -- "Rotate Credential"
    descripcion TEXT NOT NULL,

    -- Triggers que identifican esta operación
    triggers JSONB NOT NULL,                     -- ["tidb_password", "stripe_api_key", ...]

    -- Política de validación
    requires_validation BOOLEAN NOT NULL DEFAULT TRUE,
    requires_confirmation TEXT,                  -- "cowork_signature + alfredo_chat_ok" | "pre_flight_credentials_md" | etc.

    -- Fuentes de verdad asociadas (FK lógica a memento_sources_of_truth.id)
    source_of_truth_ids TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Estado
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    version INTEGER NOT NULL DEFAULT 1,

    -- Auditoría
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    creado_por TEXT NOT NULL DEFAULT 'sprint_memento_bootstrap'
);

CREATE INDEX IF NOT EXISTS idx_memento_critical_ops_activo
    ON memento_critical_operations (activo)
    WHERE activo = TRUE;

COMMENT ON TABLE memento_critical_operations IS
    'Sprint Memento v1.0 — catálogo de operaciones críticas que deben pasar por validación Memento. Configurable.';

-- Bootstrap del catálogo inicial (v1.0) según spec_sprint_memento.md
INSERT INTO memento_critical_operations (id, nombre, descripcion, triggers, requires_confirmation, source_of_truth_ids)
VALUES
    (
        'rotate_credential',
        'Rotate Credential',
        'Rotación de credenciales productivas (TiDB, Stripe, Railway, GitHub PAT, JWT secrets).',
        '["tidb_password", "stripe_api_key", "railway_token", "github_pat", "jwt_secret"]'::jsonb,
        'cowork_signature + alfredo_chat_ok',
        ARRAY['ticketlike_credentials', 'railway_env_vars']
    ),
    (
        'sql_against_production',
        'SQL Against Production',
        'Ejecución de SQL DDL/DML contra base de datos productiva (TiDB ticketlike, Supabase production).',
        '["host_matches_production_pattern", "user_has_admin_role"]'::jsonb,
        'pre_flight_credentials_md',
        ARRAY['ticketlike_credentials', 'supabase_db_url']
    ),
    (
        'deploy_to_production',
        'Deploy To Production',
        'Deploy de código a entorno productivo (Railway main, Vercel main) con migraciones DB.',
        '["target_env=production", "includes_db_migration"]'::jsonb,
        'pre_flight_validation_endpoint',
        ARRAY['railway_env_vars']
    ),
    (
        'financial_transaction',
        'Financial Transaction',
        'Cargos Stripe en modo live, creación de payouts, transferencias monetarias reales.',
        '["stripe_charge_live", "payout_creation"]'::jsonb,
        'alfredo_chat_ok + amount_threshold',
        ARRAY['stripe_live_credentials']
    )
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- TABLA 3: memento_sources_of_truth — Catálogo de fuentes de verdad
-- ============================================================================
CREATE TABLE IF NOT EXISTS memento_sources_of_truth (
    -- Identidad
    id TEXT PRIMARY KEY,                         -- slug, ej. "ticketlike_credentials"
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL,

    -- Tipo de fuente y localización
    source_type TEXT NOT NULL                    -- 'repo_file' | 'railway_env' | 'supabase_table' | 'external_dashboard' | 'env_var'
        CHECK (source_type IN ('repo_file', 'railway_env', 'supabase_table', 'external_dashboard', 'env_var')),
    location TEXT NOT NULL,                      -- ruta del archivo, nombre de env var, URL, etc.

    -- Schema declarado para parser determinístico
    parser_id TEXT,                              -- 'credentials_md_v1' | 'env_var_string' | 'json_path' | etc.
    parser_config JSONB DEFAULT '{}'::jsonb,     -- config extra para el parser (ej. JSON path, regex)

    -- Cache TTL para reducir lecturas repetidas
    cache_ttl_seconds INTEGER NOT NULL DEFAULT 60,

    -- Última actualización conocida (poblada por el kernel cuando lee la fuente)
    last_known_update TIMESTAMPTZ,
    last_known_hash TEXT,                        -- SHA-256 truncado del contenido normalizado

    -- Estado
    activo BOOLEAN NOT NULL DEFAULT TRUE,

    -- Auditoría
    creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_memento_sources_activo
    ON memento_sources_of_truth (activo)
    WHERE activo = TRUE;

CREATE INDEX IF NOT EXISTS idx_memento_sources_type
    ON memento_sources_of_truth (source_type);

COMMENT ON TABLE memento_sources_of_truth IS
    'Sprint Memento v1.0 — catálogo de fuentes de verdad consultadas por MementoValidator. Cache + TTL configurables.';

-- Bootstrap del catálogo inicial (v1.0)
INSERT INTO memento_sources_of_truth (id, nombre, descripcion, source_type, location, parser_id, cache_ttl_seconds)
VALUES
    (
        'ticketlike_credentials',
        'Ticketlike Credentials (skills/ticketlike-ops/references/credentials.md)',
        'Fuente de verdad de credenciales TiDB y Stripe live de ticketlike.mx. Path en repo del Monstruo.',
        'repo_file',
        'skills/ticketlike-ops/references/credentials.md',
        'credentials_md_v1',
        60
    ),
    (
        'railway_env_vars',
        'Railway Environment Variables (production)',
        'Variables de entorno del servicio el-monstruo-kernel en Railway production.',
        'railway_env',
        'celebrated-achievement/production/el-monstruo-kernel',
        'env_var_string',
        300
    ),
    (
        'supabase_db_url',
        'Supabase Database URL (production)',
        'Connection string de Supabase production. Almacenado en Railway env como SUPABASE_DB_URL.',
        'env_var',
        'SUPABASE_DB_URL',
        'env_var_string',
        300
    ),
    (
        'stripe_live_credentials',
        'Stripe Live API Keys',
        'Claves API live de Stripe para procesamiento de pagos reales. En Railway env como STRIPE_LIVE_*.',
        'env_var',
        'STRIPE_LIVE_SECRET_KEY',
        'env_var_string',
        300
    )
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- RLS — service_role only (kernel es el único cliente legítimo)
-- ============================================================================
ALTER TABLE memento_validations ENABLE ROW LEVEL SECURITY;
ALTER TABLE memento_critical_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE memento_sources_of_truth ENABLE ROW LEVEL SECURITY;

-- service_role bypassea RLS por defecto en Supabase, pero declaramos políticas explícitas
DROP POLICY IF EXISTS "service_role_all_validations" ON memento_validations;
CREATE POLICY "service_role_all_validations" ON memento_validations
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_critical_ops" ON memento_critical_operations;
CREATE POLICY "service_role_all_critical_ops" ON memento_critical_operations
    FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "service_role_all_sources" ON memento_sources_of_truth;
CREATE POLICY "service_role_all_sources" ON memento_sources_of_truth
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================================================
-- TRIGGER: actualizar `actualizado_en` automáticamente
-- ============================================================================
CREATE OR REPLACE FUNCTION update_memento_actualizado_en()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_memento_critical_ops_actualizado ON memento_critical_operations;
CREATE TRIGGER trg_memento_critical_ops_actualizado
    BEFORE UPDATE ON memento_critical_operations
    FOR EACH ROW EXECUTE FUNCTION update_memento_actualizado_en();

DROP TRIGGER IF EXISTS trg_memento_sources_actualizado ON memento_sources_of_truth;
CREATE TRIGGER trg_memento_sources_actualizado
    BEFORE UPDATE ON memento_sources_of_truth
    FOR EACH ROW EXECUTE FUNCTION update_memento_actualizado_en();

-- ============================================================================
-- FIN DE LA MIGRACIÓN 017
-- ============================================================================
