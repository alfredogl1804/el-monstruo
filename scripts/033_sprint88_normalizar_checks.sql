-- Sprint 88 - Migración 033: Normalizar CHECK constraints
-- Razones:
--   1. Eliminar el CHECK viejo de 'dominio' (5 dominios) que sobrevivió cuando
--      la migración 031 agregó 'chk_dominio_valido' (9 dominios). Coexisten dos
--      checks y el viejo bloquea 4 dominios nuevos.
--   2. Ampliar CHECK 'costo_por_uso_tipico' para incluir 'gratis' y 'enterprise'
--      que aparecen en el dataset Sprint 88.
--   3. Ampliar CHECK 'persistencia_memoria' para incluir 'external_db'.
--
-- Idempotente.
-- 2026-05-10 — Manus (Hilo Catastro)

BEGIN;

-- 1. Drop viejo CHECK de dominio (5 dominios)
ALTER TABLE catastro_agentes
    DROP CONSTRAINT IF EXISTS catastro_agentes_dominio_check;

-- 2. Ampliar CHECK costo_por_uso_tipico
ALTER TABLE catastro_agentes
    DROP CONSTRAINT IF EXISTS catastro_agentes_costo_por_uso_tipico_check;
ALTER TABLE catastro_agentes
    ADD CONSTRAINT catastro_agentes_costo_por_uso_tipico_check
    CHECK (costo_por_uso_tipico IS NULL OR costo_por_uso_tipico = ANY (
        ARRAY['gratis', 'bajo', 'medio', 'alto', 'muy_alto', 'enterprise']
    ));

-- 3. Ampliar CHECK persistencia_memoria
ALTER TABLE catastro_agentes
    DROP CONSTRAINT IF EXISTS catastro_agentes_persistencia_memoria_check;
ALTER TABLE catastro_agentes
    ADD CONSTRAINT catastro_agentes_persistencia_memoria_check
    CHECK (persistencia_memoria = ANY (
        ARRAY['none', 'session', 'persistent', 'external_db']
    ));

COMMIT;

-- Verificación
SELECT con.conname, pg_get_constraintdef(con.oid)
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
WHERE rel.relname = 'catastro_agentes' AND con.contype = 'c'
ORDER BY con.conname;
