-- ============================================================================
-- Migration 027 · Sprint 86.8 · Catastro Confidentiality Tier
-- ============================================================================
-- Autor: Hilo Manus Catastro (Hilo B)
-- Fecha: 2026-05-05
-- Sprint: 86.8 — Catastro confidentiality_tier por modelo
-- Spec: bridge/sprint_86_8_preinvestigation/spec_catastro_confidentiality_tier.md
--
-- OBJETIVO
-- Agregar atributo `confidentiality_tier` a cada modelo del Catastro para
-- habilitar filtrado de candidatos por sensibilidad del prompt entrante.
-- Prerequisito magna del SMP (Sovereign Memory Protocol) firmado en
-- docs/EL_MONSTRUO_APP_VISION_v1.md Cap 7.
--
-- 4 TIERS DE SENSIBILIDAD
--   - local_only: corre on-device, ningún byte sale al exterior
--   - tee_capable: confidential computing (TEE / Nitro Enclaves)
--   - cloud_anonymized_ok: cloud LLM acepta prompts anonimizados
--   - cloud_only: cloud LLM sin garantías (DEFAULT conservador)
--
-- IDEMPOTENTE: usa IF NOT EXISTS y ALTER TABLE...ADD COLUMN IF NOT EXISTS.
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. Agregar columna confidentiality_tier (idempotente vía IF NOT EXISTS)
-- ----------------------------------------------------------------------------
ALTER TABLE catastro_modelos
    ADD COLUMN IF NOT EXISTS confidentiality_tier TEXT NOT NULL DEFAULT 'cloud_only'
        CHECK (confidentiality_tier IN (
            'local_only',
            'tee_capable',
            'cloud_anonymized_ok',
            'cloud_only'
        ));

COMMENT ON COLUMN catastro_modelos.confidentiality_tier IS
    'Sprint 86.8: Tier de sensibilidad. Habilita filtrado SMP. Default conservador cloud_only — promover manualmente vía scripts/027_sprint86_8_assign_confidentiality_tiers.sql.';

-- ----------------------------------------------------------------------------
-- 2. Índice para filtrado eficiente en runtime
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_catastro_modelos_confidentiality
    ON catastro_modelos (confidentiality_tier);

-- ----------------------------------------------------------------------------
-- 3. Refrescar la vista catastro_trono_view para que exponga la nueva columna
--    (la vista hace SELECT * — no necesita recrearse, pero PostgREST cachea
--    el schema; tocar la vista invalida el cache para clientes Supabase)
-- ----------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_views WHERE viewname = 'catastro_trono_view'
    ) THEN
        -- Refrescar metadata sin recrear la vista (NOTIFY a PostgREST)
        NOTIFY pgrst, 'reload schema';
    END IF;
END
$$;

COMMIT;

-- ============================================================================
-- Verificación
-- ============================================================================
-- SELECT column_name, data_type, column_default
--   FROM information_schema.columns
--  WHERE table_name = 'catastro_modelos' AND column_name = 'confidentiality_tier';
--
-- Esperado: confidentiality_tier | text | 'cloud_only'::text
-- ============================================================================
