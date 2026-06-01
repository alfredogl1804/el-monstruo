-- Function: catastro_trigger_curacion
-- Purpose: Mark a record for curation and log the trigger event.
-- Curadores asignados: solo Manus (arbitro) + Perplexity (validador con tiempo real).
-- Los otros sabios NO validan datos factuales — solo opinan sobre estrategia/arquitectura.
CREATE OR REPLACE FUNCTION public.catastro_trigger_curacion(
  p_tabla text,
  p_record_id text,
  p_motivo text DEFAULT 'nuevo_registro',
  p_urgencia text DEFAULT 'normal'
) RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  v_result jsonb;
  v_curadores_asignados text[];
BEGIN
  IF p_motivo NOT IN ('nuevo_registro', 'desempate_trono', 'disputa_dato', 'revalidacion_periodica') THEN
    RAISE EXCEPTION 'Motivo inválido: %', p_motivo;
  END IF;

  -- Solo Manus + Perplexity para validación factual en tiempo real
  v_curadores_asignados := ARRAY['curador-manus', 'curador-sonar'];

  INSERT INTO catastro_eventos (tipo, descripcion, metadata, created_at)
  VALUES (
    'curacion_trigger',
    format('Curación solicitada para %s.%s — motivo: %s', p_tabla, p_record_id, p_motivo),
    jsonb_build_object(
      'tabla', p_tabla,
      'record_id', p_record_id,
      'motivo', p_motivo,
      'urgencia', p_urgencia,
      'curadores_asignados', to_jsonb(v_curadores_asignados),
      'status', 'pending'
    ),
    now()
  );

  IF p_tabla = 'catastro_modelos' THEN
    UPDATE catastro_modelos SET quorum_alcanzado = false, updated_at = now() WHERE id = p_record_id;
  ELSIF p_tabla = 'catastro_agentes' THEN
    UPDATE catastro_agentes SET quorum_alcanzado = false, updated_at = now() WHERE id = p_record_id;
  END IF;

  v_result := jsonb_build_object(
    'status', 'curacion_enqueued',
    'tabla', p_tabla,
    'record_id', p_record_id,
    'motivo', p_motivo,
    'curadores', to_jsonb(v_curadores_asignados),
    'next_step', 'manus_ejecuta_scraping_perplexity_valida'
  );

  RETURN v_result;
END;
$$;
