-- migrations/sql/0002_embrion_budget_state.sql
--
-- Sprint EMBRION-NEEDS-001 — Tarea 1 (Budget Tracker estricto)
--
-- Origen: bridge/sprints_propuestos/sprint_EMBRION_NEEDS_001.md
-- Decision: Crear tabla nueva `embrion_budget_state` en lugar de extender
--   la tabla `budget_state` existente.
--
-- Razon: `budget_state` tiene semantica de "presupuesto por plan/orquestacion"
--   (atado a plan_id del task_planner). El budget del embrion es por LATIDO
--   (cycle individual). Mezclar ambas semanticas en la misma tabla genera
--   columnas opcionales y queries condicionales innecesarias. Tabla separada
--   = invariantes claras + telemetria mas limpia para el dashboard del
--   embrion.
--
-- Aplicar via:
--   psql "$SUPABASE_DB_URL" -f migrations/sql/0002_embrion_budget_state.sql
-- O via MCP:
--   mcp__supabase-monstruo__apply_migration con nombre "0002_embrion_budget_state"

CREATE TABLE IF NOT EXISTS embrion_budget_state (
    id BIGSERIAL PRIMARY KEY,

    -- Identificacion del cycle/latido del embrion
    cycle_id INTEGER NOT NULL,
    latido_id UUID,  -- opcional: id del registro en embrion_memoria tipo='latido'

    -- Presupuesto y costo
    cap_per_latido_usd NUMERIC(8, 4) NOT NULL,    -- el cap activo en este momento
    cost_estimated_usd NUMERIC(8, 4),             -- proyeccion antes de ejecutar
    cost_actual_usd NUMERIC(8, 4) NOT NULL DEFAULT 0,
    cap_excedido BOOLEAN NOT NULL DEFAULT FALSE,
    abort_reason TEXT,  -- ej: "estimated_exceeds_cap", "post_actual_exceeds_cap", "daily_cap_reached"

    -- Telemetria de modelo y tokens
    tokens_used INTEGER NOT NULL DEFAULT 0,
    tokens_input INTEGER,
    tokens_output INTEGER,
    model_used TEXT,  -- ej: "gpt-5", "gpt-5.5"

    -- Trigger / contexto del cycle
    trigger_type TEXT,
    trigger_detail TEXT,

    -- Estado de aprobacion (HITL)
    requires_approval BOOLEAN NOT NULL DEFAULT FALSE,
    approval_status TEXT CHECK (approval_status IN ('pending', 'approved', 'rejected', 'auto_approved') OR approval_status IS NULL),

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Indices para queries operativas
CREATE INDEX IF NOT EXISTS embrion_budget_state_cycle_id_idx
    ON embrion_budget_state (cycle_id);

CREATE INDEX IF NOT EXISTS embrion_budget_state_created_at_idx
    ON embrion_budget_state (created_at DESC);

CREATE INDEX IF NOT EXISTS embrion_budget_state_excedido_idx
    ON embrion_budget_state (created_at DESC)
    WHERE cap_excedido = TRUE;

-- Comentarios para auto-documentacion (visible en pgAdmin / Supabase Studio)
COMMENT ON TABLE embrion_budget_state IS
    'Telemetria de presupuesto por latido del embrion. Sprint EMBRION-NEEDS-001 Tarea 1.';
COMMENT ON COLUMN embrion_budget_state.cap_per_latido_usd IS
    'Cap configurado al momento de este cycle (env EMBRION_CAP_PER_LATIDO_USD).';
COMMENT ON COLUMN embrion_budget_state.cost_estimated_usd IS
    'Costo proyectado antes de ejecutar. Si excede cap_per_latido_usd, el cycle se aborta y abort_reason se llena.';
COMMENT ON COLUMN embrion_budget_state.cost_actual_usd IS
    'Costo real al cierre del cycle. Si supera el estimated en > 30%, registra advertencia (no aborta retro).';
COMMENT ON COLUMN embrion_budget_state.cap_excedido IS
    'TRUE si en algun momento del cycle se intento gastar mas del cap. Usado para escalacion HITL.';
COMMENT ON COLUMN embrion_budget_state.requires_approval IS
    'TRUE cuando se acumulan 3+ cycles excedidos en el mismo dia. Activa flow HITL.';
