-- ============================================================================
-- Migration 042 — Sprint 88.3: Ajustar bonus Topaz Video (trono upscaling)
-- ============================================================================
-- Fecha: 2026-05-10
-- Sprint: MEGA-CATASTRO (88.3) — Tarea 3 fix #2
-- Origen: Tras 041 (vista UNNEST), Adobe Firefly y Topaz empataron en score 50
--         para upscaling_restauracion_enhancement. Adobe ganó por desempate
--         alfabético, lo cual contradice consenso Perplexity (Topaz = estándar
--         de la industria para upscaling+restauración objetiva).
--
-- Fix: bonus +5 a Topaz Video específicamente por su especialización dominante
--      en upscaling. Adobe Firefly mantiene trono de generative_editing_inpainting.
-- Idempotente: UPDATE
-- Author: Hilo Catastro (Manus B)
-- ============================================================================

BEGIN;

UPDATE catastro_vision_generativa
   SET bonus_curador = 15,
       bonus_curador_razon = 'Trono upscaling_restauracion_enhancement según Perplexity. Topaz Video es el estándar de la industria para upscaling+restauración objetiva (especialización dominante 2026). Bonus 10→15 (+5 desempate Sprint 88.3) sobre Adobe Firefly Video Editor que es trono natural de generative_editing_inpainting pero solo aparece como secundario en upscaling. Magnific Tier 1 acompañante para upscaling creativo multimodal. Acompañantes: Adobe Firefly Video Editor, Magnific.',
       updated_at = NOW()
 WHERE id = 'topaz_video';

COMMIT;

REFRESH MATERIALIZED VIEW catastro_tronos_vision_generativa;

DO $$
DECLARE
  v_topaz_trono BOOLEAN;
  v_runway_narrativo BOOLEAN;
  v_adobe_editing BOOLEAN;
BEGIN
  SELECT EXISTS(
    SELECT 1 FROM catastro_tronos_vision_generativa
    WHERE subdominio = 'upscaling_restauracion_enhancement' AND trono_id = 'topaz_video'
  ) INTO v_topaz_trono;
  SELECT EXISTS(
    SELECT 1 FROM catastro_tronos_vision_generativa
    WHERE subdominio = 'video_narrativo_cinematico' AND trono_id = 'runway_gen_4_5'
  ) INTO v_runway_narrativo;
  SELECT EXISTS(
    SELECT 1 FROM catastro_tronos_vision_generativa
    WHERE subdominio = 'generative_editing_inpainting' AND trono_id = 'adobe_firefly_video_editor'
  ) INTO v_adobe_editing;

  RAISE NOTICE 'Sprint 88.3 fix #2: Topaz=upscaling: %. Runway=narrativo: %. Adobe=editing: %',
    v_topaz_trono, v_runway_narrativo, v_adobe_editing;

  IF NOT v_topaz_trono THEN
    RAISE EXCEPTION 'topaz_video debe ser trono de upscaling_restauracion_enhancement';
  END IF;
  IF NOT v_runway_narrativo THEN
    RAISE EXCEPTION 'runway_gen_4_5 debe ser trono de video_narrativo_cinematico';
  END IF;
  IF NOT v_adobe_editing THEN
    RAISE EXCEPTION 'adobe_firefly_video_editor debe ser trono de generative_editing_inpainting';
  END IF;
END $$;

-- ============================================================================
-- FIN MIGRACION 042
-- ============================================================================
