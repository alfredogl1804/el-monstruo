-- =================================================================
-- Migration 021 — Sprint 87 NUEVO Ejecución Autónoma E2E
-- Esquema productivo: e2e_runs + e2e_step_log
-- Idempotente (CREATE TABLE IF NOT EXISTS, CREATE INDEX IF NOT EXISTS)
-- Brand DNA: nombres directos, sin "service" ni "handler"
-- Capa Memento aplicada: source of truth de runs E2E + audit trail completo
-- =================================================================

-- ---------- Tabla principal: e2e_runs ----------
CREATE TABLE IF NOT EXISTS e2e_runs (
    id              TEXT PRIMARY KEY,
    -- ID con formato 'e2e_<utc_epoch>_<hash6>' para legibilidad humana

    frase_input     TEXT NOT NULL,
    -- Frase original de Alfredo (sin tocar)

    estado          TEXT NOT NULL,
    -- 'in_progress' | 'completed' | 'failed' | 'awaiting_judgment'
    -- Constraint validado en aplicación (no CHECK SQL para flexibilidad)

    pipeline_step   INT NOT NULL DEFAULT 0,
    -- 0..12 según pipeline lineal del Sprint 87

    brief           JSONB,
    -- Output de product_architect (paso 3)

    stack_decision  JSONB,
    -- Output de embrion_estratega (paso 4)

    deploy_url      TEXT,
    -- URL viva del deploy (paso 9)

    critic_visual_score NUMERIC(5,2),
    -- Score 0-100 del critic_visual (paso 10)

    veredicto_alfredo   TEXT,
    -- 'comercializable' | 'rework' | 'descartar' | NULL
    -- Emitido por humano vía POST /v1/e2e/runs/{id}/judgment

    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    metadata        JSONB DEFAULT '{}'::jsonb
    -- Bolsa para extras: total_duration_ms, total_cost_usd, traffic_seeded, etc.
);

COMMENT ON TABLE  e2e_runs IS 'Sprint 87 — Pipeline E2E run-level state. Source of truth de runs autónomos frase->URL.';
COMMENT ON COLUMN e2e_runs.estado IS 'in_progress | completed | failed | awaiting_judgment';
COMMENT ON COLUMN e2e_runs.pipeline_step IS '0..12 según pipeline lineal de 12 pasos';

-- ---------- Tabla audit trail: e2e_step_log ----------
CREATE TABLE IF NOT EXISTS e2e_step_log (
    id              BIGSERIAL PRIMARY KEY,
    run_id          TEXT NOT NULL REFERENCES e2e_runs(id) ON DELETE CASCADE,

    step_number     INT NOT NULL,
    -- 0..12

    step_name       TEXT NOT NULL,
    -- 'INTAKE' | 'INVESTIGAR' | 'ARCHITECT' | 'ESTRATEGIA' | 'FINANZAS'
    -- 'CREATIVO' | 'VENTAS' | 'TECNICO' | 'DEPLOY' | 'CRITIC' | 'TRAFFIC' | 'VEREDICTO'

    embrion_id      TEXT,
    -- 'product_architect' | 'embrion_estratega' | ... | NULL si paso no es Embrión

    modelo_consultado   TEXT,
    -- ID del modelo del Catastro que se eligió en runtime (NULL si paso no requirió LLM)

    input_payload   JSONB,
    output_payload  JSONB,

    duration_ms     INT,
    status          TEXT NOT NULL,
    -- 'ok' | 'failed' | 'skipped'

    error_message   TEXT,

    ts              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  e2e_step_log IS 'Sprint 87 — Audit trail granular por paso. Permite replay/debug.';
COMMENT ON COLUMN e2e_step_log.step_name IS 'INTAKE|INVESTIGAR|ARCHITECT|ESTRATEGIA|FINANZAS|CREATIVO|VENTAS|TECNICO|DEPLOY|CRITIC|TRAFFIC|VEREDICTO';

-- ---------- Índices ----------
CREATE INDEX IF NOT EXISTS idx_e2e_runs_estado
    ON e2e_runs (estado, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_e2e_runs_started_at
    ON e2e_runs (started_at DESC);

CREATE INDEX IF NOT EXISTS idx_e2e_step_log_run
    ON e2e_step_log (run_id, step_number);

CREATE INDEX IF NOT EXISTS idx_e2e_step_log_status_ts
    ON e2e_step_log (status, ts DESC);
