-- ============================================================================
-- Migration 045 — Sprint 88.3: Runway Gen-4.5 primario = narrativo
-- ============================================================================
-- Origen: tras 044, Veo 3.1 sin bonus (secundario) empata con Runway sin bonus
--         (secundario) en video_narrativo_cinematico, gana por ID alfabético.
--         Solución: cambiar subdominio_primario de Runway a video_narrativo
--         (donde Perplexity lo declara trono). video_clip pasa a secundario.
-- ============================================================================

BEGIN;

UPDATE catastro_vision_generativa
   SET subdominio_primario = 'video_narrativo_cinematico',
       subdominios_secundarios = ARRAY['video_clip_generativo']::TEXT[],
       bonus_curador_razon = 'Trono video_narrativo_cinematico según Perplexity. Runway Gen-4.5 top Artificial Analysis (1247 Elo): visual fidelity + prompt adherence + motion quality + creative control + multi-shot workflow. Sprint 88.3 cambia subdominio_primario a video_narrativo_cinematico (donde Perplexity lo declara trono). video_clip_generativo queda como secundario donde compite contra Veo 3.1 (trono natural ahí).',
       updated_at = NOW()
 WHERE id = 'runway_gen_4_5';

COMMIT;

REFRESH MATERIALIZED VIEW catastro_tronos_vision_generativa;

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
