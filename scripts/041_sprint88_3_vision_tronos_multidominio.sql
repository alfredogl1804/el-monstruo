-- ============================================================================
-- Migration 041 — Sprint 88.3: Corregir vista tronos VISION_GENERATIVA
-- ============================================================================
-- Fecha: 2026-05-10
-- Sprint: MEGA-CATASTRO (88.3) — Tarea 3 fix
-- Origen: Detectado tras aplicar 040: runway_gen_4_5 es trono de
--         video_narrativo_cinematico según Perplexity, pero solo aparecía como
--         subdominio_primario de video_clip_generativo. La vista filtraba por
--         subdominio_primario, dejando higgsfield como trono.
--
-- Fix: vista materializada usa UNNEST(subdominio_primario || subdominios_secundarios)
--      para que cada producto compita en TODOS los subdominios donde aparece.
-- Idempotente: DROP + CREATE
-- Author: Hilo Catastro (Manus B)
-- ============================================================================

BEGIN;

DROP MATERIALIZED VIEW IF EXISTS catastro_tronos_vision_generativa CASCADE;

CREATE MATERIALIZED VIEW catastro_tronos_vision_generativa AS
WITH expandido AS (
    SELECT
        cvg.id,
        cvg.nombre,
        cvg.proveedor,
        UNNEST(ARRAY[cvg.subdominio_primario] || cvg.subdominios_secundarios) AS subdominio,
        cvg.tier_seed,
        cvg.open_weights,
        cvg.estado,
        cvg.licensing_risk,
        cvg.consent_required,
        cvg.bonus_curador,
        cvg.bonus_curador_razon,
        cvg.score_subdominio_origen,
        cvg.api_disponible,
        cvg.mcp_server_disponible,
        cvg.audio_nativo,
        cvg.multi_shot_capable,
        cvg.consistencia_personaje,
        cvg.c2pa_provenance,
        (
            (CASE WHEN cvg.tier_seed = 1 THEN 30 ELSE 0 END)
          + (CASE WHEN cvg.api_disponible THEN 15 ELSE 0 END)
          + (CASE WHEN cvg.mcp_server_disponible THEN 10 ELSE 0 END)
          + (CASE WHEN cvg.audio_nativo THEN 10 ELSE 0 END)
          + (CASE WHEN cvg.multi_shot_capable THEN 10 ELSE 0 END)
          + (CASE WHEN cvg.consistencia_personaje THEN 10 ELSE 0 END)
          + (CASE WHEN cvg.c2pa_provenance THEN 5 ELSE 0 END)
          + (CASE WHEN cvg.estado = 'production' THEN 5 ELSE 0 END)
          + (CASE WHEN cvg.licensing_risk = 'low' THEN 5 ELSE 0 END)
          + cvg.bonus_curador
        ) AS score
    FROM catastro_vision_generativa cvg
)
SELECT DISTINCT ON (subdominio)
    subdominio,
    id AS trono_id,
    nombre AS trono_nombre,
    proveedor,
    tier_seed,
    open_weights,
    estado,
    licensing_risk,
    consent_required,
    bonus_curador,
    bonus_curador_razon,
    score_subdominio_origen,
    score,
    NOW() AS calculado_at
FROM expandido
ORDER BY subdominio, score DESC, open_weights DESC, tier_seed ASC, id ASC;

CREATE UNIQUE INDEX idx_catastro_tronos_vision_generativa_subdominio
    ON catastro_tronos_vision_generativa (subdominio);

COMMIT;

-- ----------------------------------------------------------------------------
-- Verificación: 12 tronos, runway_gen_4_5 trono de video_narrativo_cinematico
-- ----------------------------------------------------------------------------
DO $$
DECLARE
  v_tronos INT;
  v_runway_narrativo BOOLEAN;
BEGIN
  SELECT COUNT(*) INTO v_tronos FROM catastro_tronos_vision_generativa;
  SELECT EXISTS(
    SELECT 1 FROM catastro_tronos_vision_generativa
    WHERE subdominio = 'video_narrativo_cinematico' AND trono_id = 'runway_gen_4_5'
  ) INTO v_runway_narrativo;

  RAISE NOTICE 'Sprint 88.3 fix: % tronos. Runway=trono video_narrativo: %',
    v_tronos, v_runway_narrativo;

  IF v_tronos <> 12 THEN
    RAISE EXCEPTION 'Esperado 12 tronos, encontrados %', v_tronos;
  END IF;
  IF NOT v_runway_narrativo THEN
    RAISE EXCEPTION 'runway_gen_4_5 debe ser trono de video_narrativo_cinematico';
  END IF;
END $$;

-- ============================================================================
-- FIN MIGRACION 041
-- ============================================================================
