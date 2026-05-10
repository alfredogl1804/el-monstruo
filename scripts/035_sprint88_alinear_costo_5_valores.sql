-- Sprint 88.0.1 - Migración 035: Alinear CHECK costo_por_uso_tipico a 5 valores
--
-- Cowork follow-up audit: el SQL CHECK aceptaba 6 valores (gratis/bajo/medio/
-- alto/muy_alto/enterprise) pero el enum Pydantic solo tiene 5
-- (gratis/bajo/medio/alto/enterprise). Asimetría peligrosa: permitía INSERTs
-- desde fuera del modelo Pydantic con muy_alto.
--
-- Verificado pre-migración: 0 registros usan 'muy_alto' (distribución real:
-- bajo=21, medio=32, alto=12, gratis=9, enterprise=10).
--
-- 'enterprise' ya cubre el rango ">$500/mes o pricing on-demand", haciendo
-- 'muy_alto' redundante.
--
-- Idempotente.
-- 2026-05-10 — Manus (Hilo Catastro) post-audit Cowork DSC-G-008 v2

BEGIN;

ALTER TABLE catastro_agentes
    DROP CONSTRAINT IF EXISTS catastro_agentes_costo_por_uso_tipico_check;

ALTER TABLE catastro_agentes
    ADD CONSTRAINT catastro_agentes_costo_por_uso_tipico_check
    CHECK (costo_por_uso_tipico IS NULL OR costo_por_uso_tipico = ANY (
        ARRAY['gratis', 'bajo', 'medio', 'alto', 'enterprise']
    ));

COMMIT;
