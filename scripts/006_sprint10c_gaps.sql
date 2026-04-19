-- ============================================================
-- Sprint 10c: Close Gaps — pricing_catalog + circuit_breaker_log
-- Fecha: 2026-04-18
-- ============================================================

-- ── 1. pricing_catalog: Versioned model pricing ─────────────
-- Allows tracking price changes over time for accurate cost reconciliation.
CREATE TABLE IF NOT EXISTS pricing_catalog (
    id              BIGSERIAL PRIMARY KEY,
    model_id        TEXT NOT NULL,                -- e.g. "gpt-5.4", "claude-opus-4-7"
    provider        TEXT NOT NULL,                -- e.g. "openai", "anthropic"
    price_input_per_1m  NUMERIC(10,4) NOT NULL,   -- $/1M input tokens
    price_output_per_1m NUMERIC(10,4) NOT NULL,   -- $/1M output tokens
    effective_from  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_to    TIMESTAMPTZ,                  -- NULL = currently active
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Index for quick lookups of current pricing
CREATE INDEX IF NOT EXISTS idx_pricing_catalog_model_active
    ON pricing_catalog (model_id, effective_from DESC)
    WHERE effective_to IS NULL;

-- ── 2. circuit_breaker_log: Track circuit breaker activations ──
CREATE TABLE IF NOT EXISTS circuit_breaker_log (
    id              BIGSERIAL PRIMARY KEY,
    run_id          TEXT NOT NULL,
    thread_id       TEXT DEFAULT '',
    tool_name       TEXT NOT NULL,
    trigger_reason  TEXT NOT NULL,  -- "max_calls_per_run", "input_hash_loop", "rate_limit"
    call_count      INT DEFAULT 0,
    input_hash      TEXT DEFAULT '',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_circuit_breaker_created
    ON circuit_breaker_log (created_at DESC);

-- ── 3. Seed pricing_catalog with current model prices ───────
-- Source: config/model_catalog.py validated 2026-04-18
INSERT INTO pricing_catalog (model_id, provider, price_input_per_1m, price_output_per_1m, notes)
VALUES
    ('gpt-5.4',              'openai',      2.5000, 10.0000, 'Flagship. Validated 2026-04-12.'),
    ('claude-opus-4-7',      'anthropic',   5.0000, 25.0000, 'Flagship. Launched 2026-04-16.'),
    ('claude-opus-4-6',      'anthropic',   5.0000, 25.0000, 'Previous flagship. Validated 2026-04-12.'),
    ('grok-4.20',            'xai',         2.0000,  6.0000, 'Non-reasoning variant. Validated 2026-04-12.'),
    ('deepseek-r1-0528',     'openrouter',  0.5000,  2.1500, 'Via OpenRouter. Validated 2026-04-12.'),
    ('sonar-reasoning-pro',  'perplexity',  2.0000,  8.0000, 'Reasoning search. Validated 2026-04-12.'),
    ('gpt-5.4-mini',         'openai',      0.7500,  3.0000, 'Fast/cheap. Validated 2026-04-12.'),
    ('claude-sonnet-4-6',    'anthropic',   3.0000, 15.0000, 'Code specialist. Validated 2026-04-12.'),
    ('gemini-3.1-flash-lite','google',      0.0000,  0.0000, 'Free tier. Validated 2026-04-12.'),
    ('gemini-3.1-pro',       'google',      1.2500,  5.0000, 'Multimodal. Validated 2026-04-12.'),
    ('kimi-k2.5',            'openrouter',  0.3827,  1.7200, 'Budget. Corrected pricing. Validated 2026-04-12.'),
    ('sonar-pro',            'perplexity',  3.0000, 15.0000, 'General search. Validated 2026-04-12.')
ON CONFLICT DO NOTHING;

-- ── 4. RPC: get_current_pricing ─────────────────────────────
-- Returns the active price for a model (effective_to IS NULL)
CREATE OR REPLACE FUNCTION get_current_pricing(target_model TEXT DEFAULT NULL)
RETURNS TABLE (
    model_id TEXT,
    provider TEXT,
    price_input_per_1m NUMERIC,
    price_output_per_1m NUMERIC,
    effective_from TIMESTAMPTZ
) AS $$
BEGIN
    IF target_model IS NOT NULL THEN
        RETURN QUERY
            SELECT pc.model_id, pc.provider, pc.price_input_per_1m, pc.price_output_per_1m, pc.effective_from
            FROM pricing_catalog pc
            WHERE pc.model_id = target_model AND pc.effective_to IS NULL
            ORDER BY pc.effective_from DESC
            LIMIT 1;
    ELSE
        RETURN QUERY
            SELECT DISTINCT ON (pc.model_id)
                pc.model_id, pc.provider, pc.price_input_per_1m, pc.price_output_per_1m, pc.effective_from
            FROM pricing_catalog pc
            WHERE pc.effective_to IS NULL
            ORDER BY pc.model_id, pc.effective_from DESC;
    END IF;
END;
$$ LANGUAGE plpgsql;
