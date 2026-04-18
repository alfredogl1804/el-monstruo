-- ============================================================
-- Sprint 9: Conciencia y Dossier
-- Tables: user_dossier, active_missions
-- Created: 2026-04-18
-- ============================================================

-- ===================== USER DOSSIER =====================
-- Dynamic, editable user profile that replaces the hardcoded
-- USER_DOSSIER string in prompts/system_prompts.py.
-- Designed for single-user (Alfredo) but schema supports multi-user.

CREATE TABLE IF NOT EXISTS user_dossier (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         TEXT NOT NULL UNIQUE,  -- e.g. "alfredo"
    
    -- Core identity
    full_name       TEXT NOT NULL DEFAULT '',
    company         TEXT DEFAULT '',
    rfc             TEXT DEFAULT '',
    location        TEXT DEFAULT '',
    role            TEXT DEFAULT '',
    industry        TEXT DEFAULT '',
    timezone        TEXT DEFAULT 'America/Merida',
    
    -- Digital identity
    email           TEXT DEFAULT '',
    github_username TEXT DEFAULT '',
    telegram_id     TEXT DEFAULT '',
    phone           TEXT DEFAULT '',
    
    -- Preferences (JSONB for flexibility)
    communication_prefs JSONB DEFAULT '{
        "language": "es-MX",
        "format": "bullet_points",
        "style": "direct",
        "include_in_proposals": ["cost", "time", "risk"],
        "avoid_words": ["sinergia", "apalancamiento"],
        "working_hours": "07:00-23:00 CST"
    }'::jsonb,
    
    -- Context (JSONB for evolving structure)
    context         JSONB DEFAULT '{
        "active_projects": [],
        "interests": [],
        "decision_style": "data_plus_intuition",
        "ai_usage": "multiplier_not_replacement"
    }'::jsonb,
    
    -- Custom fields (user can add anything)
    custom_fields   JSONB DEFAULT '{}'::jsonb,
    
    -- Metadata
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_dossier_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_dossier_updated
    BEFORE UPDATE ON user_dossier
    FOR EACH ROW
    EXECUTE FUNCTION update_dossier_timestamp();

-- ===================== ACTIVE MISSIONS =====================
-- Tracks what Alfredo is currently working on.
-- The LLM can read this to understand context and switch between projects.

CREATE TABLE IF NOT EXISTS active_missions (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id         TEXT NOT NULL DEFAULT 'alfredo',
    
    -- Mission identity
    name            TEXT NOT NULL,
    description     TEXT DEFAULT '',
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'paused', 'completed', 'archived')),
    priority        INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    
    -- Context
    tags            TEXT[] DEFAULT '{}',
    metadata        JSONB DEFAULT '{}'::jsonb,
    
    -- Tracking
    started_at      TIMESTAMPTZ DEFAULT now(),
    paused_at       TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_missions_user_status ON active_missions(user_id, status);
CREATE INDEX idx_missions_priority ON active_missions(priority DESC);

CREATE TRIGGER trg_missions_updated
    BEFORE UPDATE ON active_missions
    FOR EACH ROW
    EXECUTE FUNCTION update_dossier_timestamp();

-- ===================== SEED DATA =====================
-- Pre-populate Alfredo's dossier from the hardcoded USER_DOSSIER

INSERT INTO user_dossier (
    user_id, full_name, company, rfc, location, role, industry,
    timezone, email, github_username, telegram_id,
    communication_prefs, context
) VALUES (
    'alfredo',
    'Alfredo Góngora Lara',
    'Hive Business Center (Hivecom)',
    'HBC150928G89',
    'Mérida, Yucatán, México',
    'CEO / Fundador',
    'Coworking, tecnología, bienes raíces, consultoría',
    'America/Merida',
    'alfredogl1@hivecom.mx',
    'alfredogl1804',
    '',
    '{
        "language": "es-MX",
        "format": "bullet_points",
        "style": "direct",
        "include_in_proposals": ["cost", "time", "risk"],
        "avoid_words": ["sinergia", "apalancamiento"],
        "working_hours": "07:00-23:00 CST",
        "honesty_about_limitations": true
    }'::jsonb,
    '{
        "active_projects": ["El Monstruo", "CIP", "Hive Business Center", "Desarrollos inmobiliarios Yucatán"],
        "interests": ["IA soberana", "inversión inmobiliaria", "automatización"],
        "decision_style": "data_plus_intuition",
        "ai_usage": "multiplier_not_replacement",
        "simultaneous_projects": true,
        "execution_speed_over_perfection": true
    }'::jsonb
) ON CONFLICT (user_id) DO NOTHING;

-- Seed active missions
INSERT INTO active_missions (user_id, name, description, status, priority, tags) VALUES
    ('alfredo', 'El Monstruo', 'Sistema IA soberano — kernel, bot, herramientas, autonomía', 'active', 10, ARRAY['ia', 'core', 'soberanía']),
    ('alfredo', 'CIP', 'Plataforma de inversión inmobiliaria fraccionada con tokens', 'active', 8, ARRAY['fintech', 'inmobiliaria', 'tokens']),
    ('alfredo', 'Hive Business Center', 'Operación diaria del coworking', 'active', 7, ARRAY['coworking', 'operaciones']),
    ('alfredo', 'Desarrollos Inmobiliarios Yucatán', 'Proyectos de desarrollo inmobiliario en la región', 'active', 6, ARRAY['inmobiliaria', 'desarrollo'])
ON CONFLICT DO NOTHING;
