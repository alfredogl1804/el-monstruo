-- ============================================================================
-- Migration 044 — Sprint 88.3: Vista tronos VISION_GENERATIVA — bonus solo en primario
-- ============================================================================
-- Fecha: 2026-05-10
-- Sprint: MEGA-CATASTRO (88.3) — Tarea 3 cierre arquitectónico
--
-- Decisión arquitectónica:
--   El bonus_curador de un producto justifica SU rol de trono en su
--   subdominio_primario. Cuando aparece como secundario, NO debe aplicar bonus
--   (es competencia, no especialización). Esto resuelve el problema "Veo 3.1
--   con bonus +5 también gana en narrativo donde es secundario".
--
-- Fórmula corregida:
--   - Score subdominio primario = base + bonus_curador
--   - Score subdominio secundario = base (sin bonus)
--
-- Resultado esperado: tronos = consenso Perplexity exacto sin más bonuses.
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
        cvg.subdominio_primario AS subdominio_primario,
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
        cvg.c2pa_provenance
    FROM catastro_vision_generativa cvg
),
con_score AS (
    SELECT *,
        (
            (CASE WHEN tier_seed = 1 THEN 30 ELSE 0 END)
          + (CASE WHEN api_disponible THEN 15 ELSE 0 END)
          + (CASE WHEN mcp_server_disponible THEN 10 ELSE 0 END)
          + (CASE WHEN audio_nativo THEN 10 ELSE 0 END)
          + (CASE WHEN multi_shot_capable THEN 10 ELSE 0 END)
          + (CASE WHEN consistencia_personaje THEN 10 ELSE 0 END)
          + (CASE WHEN c2pa_provenance THEN 5 ELSE 0 END)
          + (CASE WHEN estado = 'production' THEN 5 ELSE 0 END)
          + (CASE WHEN licensing_risk = 'low' THEN 5 ELSE 0 END)
          + (CASE WHEN subdominio = subdominio_primario THEN bonus_curador ELSE 0 END)
        ) AS score
    FROM expandido
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
    (subdominio = subdominio_primario) AS es_subdominio_primario,
    NOW() AS calculado_at
FROM con_score
ORDER BY subdominio, score DESC, open_weights DESC, tier_seed ASC, id ASC;

CREATE UNIQUE INDEX idx_catastro_tronos_vision_generativa_subdominio
    ON catastro_tronos_vision_generativa (subdominio);

COMMIT;

-- ----------------------------------------------------------------------------
-- Verificación 12 tronos = consenso Perplexity exacto
-- ----------------------------------------------------------------------------
DO $$
DECLARE
  expected_tronos JSONB := '{
    "imagen_estatica_premium": "midjourney_v7",
    "video_clip_generativo": "veo_3_1",
    "video_narrativo_cinematico": "runway_gen_4_5",
    "avatar_humano_animado": "synthesia",
    "realtime_video_agents_characters": "runway_characters",
    "lip_sync_visual_dubbing": "sync_labs",
    "tts_voces_sinteticas": "elevenlabs_tts",
    "musica_generada": "suno_v5_5",
    "efectos_sonido_sfx": "elevenlabs_sfx",
    "generative_editing_inpainting": "adobe_firefly_video_editor",
    "upscaling_restauracion_enhancement": "topaz_video",
    "3d_mocap_assets": "meshy"
  }'::jsonb;
  rec RECORD;
  fallas INT := 0;
BEGIN
  FOR rec IN SELECT subdominio, trono_id FROM catastro_tronos_vision_generativa LOOP
    IF (expected_tronos ->> rec.subdominio) <> rec.trono_id THEN
      RAISE WARNING 'MISMATCH %: esperado=%, actual=%',
        rec.subdominio, expected_tronos ->> rec.subdominio, rec.trono_id;
      fallas := fallas + 1;
    END IF;
  END LOOP;

  IF fallas > 0 THEN
    RAISE EXCEPTION 'Sprint 88.3: % tronos no coinciden con Perplexity', fallas;
  END IF;
  RAISE NOTICE 'Sprint 88.3 VISION_GENERATIVA: 12/12 tronos coinciden con Perplexity';
END $$;
