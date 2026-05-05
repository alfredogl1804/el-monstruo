-- =============================================================================
-- 019.1 — Hotfix Sprint 86 Bloque 6 / Audit Cowork B7
-- Agrega columna validated_by TEXT que la función catastro_apply_quorum_outcome
-- (redeclarada en 019) referencia pero NUNCA fue creada en ninguna migration
-- previa. Sin esta columna el primer run productivo del Catastro falla con
-- ERROR 42703 en los 37 modelos persistibles.
--
-- Idempotente: usa IF NOT EXISTS en la columna y comentario.
-- Aplicada a Supabase production: 2026-05-05
-- =============================================================================

BEGIN;

ALTER TABLE catastro_modelos
    ADD COLUMN IF NOT EXISTS validated_by TEXT;

COMMENT ON COLUMN catastro_modelos.validated_by IS
    'Identificador del actor que aprobó la última validación '
    '(curator alias, agent id, hilo). Poblada por la RPC '
    'catastro_apply_quorum_outcome. Nullable. Sprint 86 Bloque 6 hotfix.';

-- Index opcional para queries por validador
CREATE INDEX IF NOT EXISTS idx_catastro_modelos_validated_by
    ON catastro_modelos(validated_by)
 WHERE validated_by IS NOT NULL;

COMMIT;

-- =============================================================================
-- FIN scripts/019_1_hotfix_validated_by_column.sql
-- =============================================================================
