-- ============================================================================
-- Migration 043 — Sprint 88.3: Veo 3.1 trono video_clip_generativo + cierre
-- ============================================================================
-- Fecha: 2026-05-10
-- Sprint: MEGA-CATASTRO (88.3) — Tarea 3 cierre
-- Origen: Tras 042, Runway Gen-4.5 desempató a Veo 3.1 alfabéticamente en
--         video_clip_generativo (ambos tier=1, bonus=10, score=50). JSON
--         Perplexity dice Veo 3.1 = trono video_clip_generativo (Runway = trono
--         narrativo_cinematico).
--
-- Fix: bonus +5 a Veo 3.1 con razón "audio nativo + 8s clips + Gemini integration".
-- Author: Hilo Catastro (Manus B)
-- ============================================================================

BEGIN;

UPDATE catastro_vision_generativa
   SET bonus_curador = 15,
       audio_nativo = TRUE,
       duracion_max_clip_sec = 8,
       bonus_curador_razon = 'Trono video_clip_generativo según Perplexity. Veo 3.1 (Google) genera clips de 8s con audio nativo, referencias múltiples, video vertical (Gemini integration). Bonus 10→15 (+5 desempate Sprint 88.3) sobre Runway Gen-4.5 (que es trono natural de video_narrativo_cinematico). Audio nativo y duracion_max_clip_sec=8s actualizados con datos verificables. Acompañantes Tier 1: Runway Gen-4.5, Luma Ray2, Seedance 2.0, Pika.',
       updated_at = NOW()
 WHERE id = 'veo_3_1';

COMMIT;

REFRESH MATERIALIZED VIEW catastro_tronos_vision_generativa;

-- ----------------------------------------------------------------------------
-- Verificación final 12 tronos = consenso Perplexity exacto
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
  esperado TEXT;
  actual TEXT;
  fallas INT := 0;
BEGIN
  FOR rec IN SELECT subdominio, trono_id FROM catastro_tronos_vision_generativa LOOP
    esperado := expected_tronos ->> rec.subdominio;
    IF esperado IS NULL THEN
      RAISE EXCEPTION 'Subdominio inesperado: %', rec.subdominio;
    END IF;
    IF rec.trono_id <> esperado THEN
      RAISE WARNING 'MISMATCH subdominio=%: esperado=%, actual=%', rec.subdominio, esperado, rec.trono_id;
      fallas := fallas + 1;
    END IF;
  END LOOP;

  IF fallas > 0 THEN
    RAISE EXCEPTION 'Sprint 88.3 cierre: % tronos no coinciden con Perplexity', fallas;
  END IF;

  RAISE NOTICE 'Sprint 88.3 VISION_GENERATIVA cerrado: 12/12 tronos coinciden con Perplexity';
END $$;

-- ============================================================================
-- FIN MIGRACION 043 — VISION_GENERATIVA cerrada
-- ============================================================================
