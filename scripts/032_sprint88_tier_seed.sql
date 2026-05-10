-- Sprint 88 - Migración 032: agregar columna tier_seed a catastro_agentes
-- DSC-G-007.3 - Escalonamiento de validación adversarial
--   tier_seed=1: top-5 por dominio (validación profunda 3 sabios + tronos)
--   tier_seed=2: resto (validación ligera 1 sabio, candidatos Sprint 88.1)
--
-- Idempotente.
-- 2026-05-10 — Manus (Hilo Catastro)

ALTER TABLE catastro_agentes
ADD COLUMN IF NOT EXISTS tier_seed SMALLINT NOT NULL DEFAULT 1
    CHECK (tier_seed IN (1, 2));

COMMENT ON COLUMN catastro_agentes.tier_seed IS
    'Tier de profundidad de validación adversarial. '
    '1=profunda (3 sabios + tronos), 2=ligera (1 sabio, Sprint 88.1). '
    'Definido en DSC-G-007.3.';

-- Index para queries por tier
CREATE INDEX IF NOT EXISTS idx_catastro_agentes_tier_seed
    ON catastro_agentes (tier_seed);
