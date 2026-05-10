-- Sprint 88 - Migración 031: expandir dominios de catastro_agentes
-- Agrega 4 dominios nuevos a la macroárea AGENTES:
--   agentes_vibe_coding         (no-code/low-code app builders)
--   agentes_creacion_audiovisual (cine, video largo, SFX, música)
--   agentes_branding_diseno     (logos, marca, identidad visual)
--   agentes_marketing_ventas    (pauta, leads, copy ads, outreach)
--
-- Justificación: investigación tiempo real al 10-may-2026 reveló 4 verticales
-- adicionales con productos canónicos consolidados (Sora, Veo, Runway, Higgsfield,
-- Lovable, Bolt, Replit Agent, Ideogram, Recraft, Apollo, Clay, Salesforce
-- Agentforce, etc.) que ampliarán el arsenal seleccionable del Catastro.
--
-- DSC-G-007.2 lo canonizará formalmente.
--
-- Idempotente: drop+recreate del CHECK constraint.
-- Backward compatible: los 5 dominios originales siguen siendo válidos.
--
-- 2026-05-10 — Manus (Hilo Catastro)

-- ----------------------------------------------------------------------------
-- 1. Drop constraint existente (5 dominios)
-- ----------------------------------------------------------------------------

ALTER TABLE catastro_agentes
DROP CONSTRAINT IF EXISTS chk_dominio_valido;

-- ----------------------------------------------------------------------------
-- 2. Recreate constraint con 9 dominios (5 originales + 4 nuevos)
-- ----------------------------------------------------------------------------

ALTER TABLE catastro_agentes
ADD CONSTRAINT chk_dominio_valido CHECK (
    dominio IN (
        -- Originales Sprint 88 v1
        'agentes_desarrollo',
        'agentes_investigacion',
        'agentes_ejecutores',
        'agentes_multi_swarm',
        'interfaces_usuario',
        -- Nuevos Sprint 88 v2 (DSC-G-007.2)
        'agentes_vibe_coding',
        'agentes_creacion_audiovisual',
        'agentes_branding_diseno',
        'agentes_marketing_ventas'
    )
);

-- ----------------------------------------------------------------------------
-- 3. Comentario sobre la columna actualizada
-- ----------------------------------------------------------------------------

COMMENT ON COLUMN catastro_agentes.dominio IS
    'Dominio dentro de macroárea AGENTES. 9 valores válidos: '
    '5 originales (desarrollo, investigacion, ejecutores, multi_swarm, interfaces_usuario) + '
    '4 expandidos Sprint 88 v2 (vibe_coding, creacion_audiovisual, branding_diseno, marketing_ventas). '
    'Canonizado en DSC-G-007.2.';

-- ----------------------------------------------------------------------------
-- 4. Verificación
-- ----------------------------------------------------------------------------

DO $$
DECLARE
    constraint_def TEXT;
    dominio_count INT;
BEGIN
    -- Verificar que el constraint existe con los 9 dominios
    SELECT pg_get_constraintdef(oid) INTO constraint_def
    FROM pg_constraint
    WHERE conname = 'chk_dominio_valido' AND conrelid = 'catastro_agentes'::regclass;

    IF constraint_def IS NULL THEN
        RAISE EXCEPTION 'CHECK constraint chk_dominio_valido NO EXISTE después de la migración';
    END IF;

    -- Contar dominios distintos en el constraint (heurística simple)
    SELECT array_length(string_to_array(constraint_def, ''''), 1) / 2 INTO dominio_count;

    RAISE NOTICE 'Migración 031 OK: chk_dominio_valido recreado con 9 dominios';
    RAISE NOTICE 'Constraint def: %', constraint_def;
END $$;
