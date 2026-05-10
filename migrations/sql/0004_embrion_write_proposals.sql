-- Sprint EMBRION-NEEDS-001 — Tarea 3 — Write Policy con HITL real
-- Migración 0004: crear tabla embrion_write_proposals
-- Idempotente: usa IF NOT EXISTS en todo. Safe para re-aplicar.
--
-- Diseño: enum semántico para tipos y status (CHECK constraints en lugar de
-- ENUM type para mantener simplicidad y evitar requerir DROP TYPE en futuras
-- migraciones).
--
-- Estados:
--   pending   → recién creada, esperando aprobación humana
--   approved  → aprobada, lista para ejecución por worker
--   rejected  → rechazada explícitamente por humano (con razón)
--   expired   → no respondida en N horas (default 24h), no se ejecuta
--   executing → worker la tomó y está ejecutando (lock optimista)
--   executed  → ejecutada con éxito
--   failed    → ejecutada con error (result_json contiene detalle)
--
-- Tipos (proposal_type):
--   code_commit       → push a un repo via gh CLI o git
--   db_write          → INSERT/UPDATE/DELETE a una tabla
--   external_api_call → llamada a API externa con efectos (POST/PUT/DELETE)
--   other             → cualquier acción con efecto que no encaje arriba

CREATE TABLE IF NOT EXISTS embrion_write_proposals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Origen
    proposed_by     TEXT NOT NULL DEFAULT 'embrion_loop',
    cycle_id        INTEGER,                            -- cycle del embrión que generó la proposal
    latido_id       UUID,                               -- referencia al latido que la disparó
    idempotency_key TEXT UNIQUE,                        -- evita duplicados (sha256 del payload normalmente)

    -- Contenido
    proposal_type   TEXT NOT NULL CHECK (proposal_type IN (
                        'code_commit', 'db_write', 'external_api_call', 'other'
                    )),
    summary         TEXT NOT NULL,                      -- 1 línea humana para HITL
    payload_json    JSONB NOT NULL,                     -- payload completo para ejecución
    risk_level      TEXT NOT NULL DEFAULT 'medium' CHECK (risk_level IN (
                        'low', 'medium', 'high', 'critical'
                    )),

    -- HITL
    approval_status TEXT NOT NULL DEFAULT 'pending' CHECK (approval_status IN (
                        'pending', 'approved', 'rejected',
                        'expired', 'executing', 'executed', 'failed'
                    )),
    approved_by     TEXT,                               -- 'alfredo' / 'cowork' / 'telegram' / etc.
    approved_at     TIMESTAMPTZ,
    rejection_reason TEXT,
    expires_at      TIMESTAMPTZ NOT NULL DEFAULT (now() + INTERVAL '24 hours'),

    -- Ejecución
    executed_at     TIMESTAMPTZ,
    executor        TEXT,                               -- nombre del worker que ejecutó
    result_json     JSONB,                              -- resultado o error completo
    attempts        INTEGER NOT NULL DEFAULT 0,         -- contador de reintentos del worker

    -- Notificación
    notified_at     TIMESTAMPTZ,                        -- cuando se mandó al canal HITL
    notified_via    TEXT                                -- 'telegram' | 'cowork_bridge' | 'email' | etc.
);

COMMENT ON TABLE embrion_write_proposals IS
    'Sprint EMBRION-NEEDS-001 Tarea 3: cola de proposals de escritura del embrión que requieren aprobación humana antes de ejecutarse. Reemplaza ejecución directa por flujo propose → approve → execute con auditoría completa.';

-- ============================================================
-- Índices
-- ============================================================

-- Lookup por status (worker scanea pending/approved frecuentemente)
CREATE INDEX IF NOT EXISTS embrion_write_proposals_status_idx
    ON embrion_write_proposals (approval_status, created_at DESC);

-- Lookup por cycle (debug y forensics)
CREATE INDEX IF NOT EXISTS embrion_write_proposals_cycle_idx
    ON embrion_write_proposals (cycle_id) WHERE cycle_id IS NOT NULL;

-- Lookup por expiración (cron de expire_old)
CREATE INDEX IF NOT EXISTS embrion_write_proposals_expires_idx
    ON embrion_write_proposals (expires_at) WHERE approval_status = 'pending';

-- Lookup por tipo (analytics)
CREATE INDEX IF NOT EXISTS embrion_write_proposals_type_idx
    ON embrion_write_proposals (proposal_type, created_at DESC);

-- ============================================================
-- Trigger: actualizar updated_at automáticamente
-- ============================================================

CREATE OR REPLACE FUNCTION embrion_write_proposals_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS embrion_write_proposals_updated_at_trg
    ON embrion_write_proposals;

CREATE TRIGGER embrion_write_proposals_updated_at_trg
    BEFORE UPDATE ON embrion_write_proposals
    FOR EACH ROW
    EXECUTE FUNCTION embrion_write_proposals_set_updated_at();
