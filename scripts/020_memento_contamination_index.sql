-- ============================================================================
-- Migration 020 — Sprint Memento Bloque 6
-- Capa Memoria Soberana v1.0 — Detector de Contexto Contaminado
-- ============================================================================
--
-- CONTEXTO:
--   Las columnas `contamination_warning BOOLEAN DEFAULT FALSE` y
--   `contamination_evidence JSONB` ya fueron creadas en migration 017
--   (Sprint Memento Bloque 1). Verificación:
--
--     SELECT column_name FROM information_schema.columns
--     WHERE table_name = 'memento_validations'
--       AND column_name IN ('contamination_warning', 'contamination_evidence');
--
-- 27ma SEMILLA APLICADA:
--   No re-creamos columnas que ya existen — utility centralizada (B1) ya las
--   declaró. Esta migration SOLO agrega:
--   1. Índice parcial sobre contamination_warning=TRUE (queries de monitoreo)
--   2. COMMENT ON COLUMN para documentar el formato JSONB esperado
--
-- IDEMPOTENTE:
--   Usa CREATE INDEX IF NOT EXISTS y COMMENT (que es UPSERT por naturaleza).
--   Reejecutar la migration es seguro.
-- ============================================================================

-- 1) Índice parcial: solo filas con warning activo (más liviano que un índice
--    completo sobre la columna boolean).
CREATE INDEX IF NOT EXISTS idx_memento_validations_contamination_warning
    ON memento_validations (contamination_warning, ts DESC)
    WHERE contamination_warning = TRUE;

-- 2) Documentación inline (sirve como contrato del shape JSONB)
COMMENT ON COLUMN memento_validations.contamination_warning IS
    'Sprint Memento B6 — TRUE si ContaminationDetector encontró >= 1 finding (cualquier severidad). NO altera proceed en v1.0 (shadow mode).';

COMMENT ON COLUMN memento_validations.contamination_evidence IS
    'Sprint Memento B6 — JSONB con shape: {findings: [{rule_id, severity, evidence, recommendation, validation_id_ref}], detector_runtime_ms, timed_out_rules, skipped_rules, has_warning, has_high_severity}.';

-- ============================================================================
-- /Migration 020
-- ============================================================================
