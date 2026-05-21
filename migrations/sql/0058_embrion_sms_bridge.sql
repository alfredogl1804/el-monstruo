-- ============================================================
-- Migration 0058: Embrión Loop → SMS Bridge
-- Conecta las memorias aisladas del Embrión Loop al
-- Sovereign Memory System (SMS)
-- ============================================================
-- Fecha: 2026-05-21
-- Autor: Manus Scheduled Thread
-- Contexto: embrion_memoria tiene 2,772 registros aislados.
--   Solo 14 han sido "consumidos". Este bridge migra las
--   memorias de alto valor al SMS y crea una RPC para
--   auto-bridge futuro.
-- ============================================================

-- ============================================================
-- RPC: bridge_embrion_to_sms
-- Migra memorias de embrion_memoria al SMS con filtro de valor
-- Parámetros:
--   p_min_importancia: importancia mínima para migrar (default 7)
--   p_tipos_soberanos: tipos que van a layer 3 (sovereign)
--   p_batch_size: tamaño del batch (default 100)
--   p_mark_consumed: si marca consumed_at en origen (default true)
-- ============================================================

CREATE OR REPLACE FUNCTION bridge_embrion_to_sms(
  p_min_importancia INT DEFAULT 7,
  p_batch_size INT DEFAULT 100,
  p_mark_consumed BOOLEAN DEFAULT TRUE
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_record RECORD;
  v_memory_id UUID;
  v_bridged_count INT := 0;
  v_skipped_dedup INT := 0;
  v_results JSONB := '[]'::jsonb;
  v_content_hash TEXT;
  v_memory_type TEXT;
  v_layer INT;
  v_confidence FLOAT;
  v_tags TEXT[];
  v_entities JSONB;
  v_existing_hash INT;
BEGIN
  -- Tipos soberanos van a layer 3
  -- Tipos consolidados van a layer 2
  -- Respuestas de alto valor van a layer 2
  
  FOR v_record IN
    SELECT * FROM embrion_memoria
    WHERE consumed_at IS NULL
      AND (
        -- Tipos soberanos: siempre migrar
        tipo IN ('doctrina', 'decision', 'mensaje_alfredo')
        OR
        -- Tipos consolidados: siempre migrar
        tipo IN ('contribucion_sabio', 'reflexion', 'pensamiento')
        OR
        -- Respuestas de alto valor: filtrar por importancia
        (tipo = 'respuesta_embrion' AND importancia >= p_min_importancia)
      )
    ORDER BY
      CASE tipo
        WHEN 'doctrina' THEN 1
        WHEN 'decision' THEN 2
        WHEN 'mensaje_alfredo' THEN 3
        WHEN 'contribucion_sabio' THEN 4
        WHEN 'reflexion' THEN 5
        WHEN 'pensamiento' THEN 6
        WHEN 'respuesta_embrion' THEN 7
        ELSE 8
      END,
      importancia DESC NULLS LAST,
      created_at ASC
    LIMIT p_batch_size
  LOOP
    -- Calcular content_hash para dedup
    v_content_hash := md5(v_record.contenido);
    
    -- Verificar si ya existe en sovereign_memories
    SELECT count(*) INTO v_existing_hash
    FROM sovereign_memories
    WHERE content_hash = v_content_hash;
    
    IF v_existing_hash > 0 THEN
      v_skipped_dedup := v_skipped_dedup + 1;
      -- Marcar como consumido aunque sea duplicado
      IF p_mark_consumed THEN
        UPDATE embrion_memoria
        SET consumed_at = now()
        WHERE id = v_record.id;
      END IF;
      CONTINUE;
    END IF;
    
    -- Determinar memory_type y layer
    CASE v_record.tipo
      WHEN 'doctrina' THEN
        v_memory_type := 'semantic';
        v_layer := 3;
      WHEN 'decision' THEN
        v_memory_type := 'semantic';
        v_layer := 3;
      WHEN 'mensaje_alfredo' THEN
        v_memory_type := 'semantic';
        v_layer := 3;
      WHEN 'contribucion_sabio' THEN
        v_memory_type := 'semantic';
        v_layer := 2;
      WHEN 'reflexion' THEN
        v_memory_type := 'semantic';
        v_layer := 2;
      WHEN 'pensamiento' THEN
        v_memory_type := 'semantic';
        v_layer := 2;
      WHEN 'respuesta_embrion' THEN
        v_memory_type := 'episodic';
        v_layer := 2;
      ELSE
        v_memory_type := 'episodic';
        v_layer := 1;
    END CASE;
    
    -- Calcular confidence desde importancia
    v_confidence := COALESCE(v_record.importancia, 5) / 10.0;
    
    -- Construir tags
    v_tags := ARRAY[v_record.tipo, 'embrion_loop', 'bridge_0058'];
    
    -- Construir entities desde contexto
    v_entities := COALESCE(v_record.contexto, '[]'::jsonb);
    -- Si contexto no es un array, wrapearlo
    IF jsonb_typeof(v_entities) != 'array' THEN
      v_entities := jsonb_build_array(v_entities);
    END IF;
    
    -- Insertar en sovereign_memories
    INSERT INTO sovereign_memories (
      content,
      content_hash,
      memory_type,
      layer,
      source,
      agent_id,
      confidence,
      tags,
      entities,
      importance_score,
      created_at
    ) VALUES (
      v_record.contenido,
      v_content_hash,
      v_memory_type,
      v_layer,
      'embrion_loop:' || COALESCE(v_record.hilo_origen, 'unknown'),
      COALESCE(v_record.hilo_origen, 'embrion_loop'),
      v_confidence,
      v_tags,
      v_entities,
      v_confidence,
      v_record.created_at
    )
    RETURNING id INTO v_memory_id;
    
    -- Marcar como consumido en origen
    IF p_mark_consumed THEN
      UPDATE embrion_memoria
      SET consumed_at = now()
      WHERE id = v_record.id;
    END IF;
    
    v_bridged_count := v_bridged_count + 1;
    
    -- Solo guardar primeros 20 en results para no explotar el JSON
    IF v_bridged_count <= 20 THEN
      v_results := v_results || jsonb_build_object(
        'embrion_id', v_record.id,
        'memory_id', v_memory_id,
        'tipo', v_record.tipo,
        'layer', v_layer
      );
    END IF;
    
  END LOOP;
  
  RETURN jsonb_build_object(
    'bridged_count', v_bridged_count,
    'skipped_dedup', v_skipped_dedup,
    'batch_size', p_batch_size,
    'sample_results', v_results
  );
END;
$$;

-- ============================================================
-- RPC: get_embrion_bridge_status
-- Retorna estadísticas del estado del bridge
-- ============================================================

CREATE OR REPLACE FUNCTION get_embrion_bridge_status()
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_total INT;
  v_consumed INT;
  v_pending_sovereign INT;
  v_pending_consolidated INT;
  v_pending_responses INT;
  v_skippable INT;
BEGIN
  SELECT count(*) INTO v_total FROM embrion_memoria;
  
  SELECT count(*) INTO v_consumed
  FROM embrion_memoria WHERE consumed_at IS NOT NULL;
  
  SELECT count(*) INTO v_pending_sovereign
  FROM embrion_memoria
  WHERE consumed_at IS NULL
    AND tipo IN ('doctrina', 'decision', 'mensaje_alfredo');
  
  SELECT count(*) INTO v_pending_consolidated
  FROM embrion_memoria
  WHERE consumed_at IS NULL
    AND tipo IN ('contribucion_sabio', 'reflexion', 'pensamiento');
  
  SELECT count(*) INTO v_pending_responses
  FROM embrion_memoria
  WHERE consumed_at IS NULL
    AND tipo = 'respuesta_embrion'
    AND importancia >= 7;
  
  SELECT count(*) INTO v_skippable
  FROM embrion_memoria
  WHERE consumed_at IS NULL
    AND (
      tipo IN ('evaluacion', 'latido')
      OR (tipo = 'respuesta_embrion' AND (importancia < 7 OR importancia IS NULL))
    );
  
  RETURN jsonb_build_object(
    'total_records', v_total,
    'already_consumed', v_consumed,
    'pending_sovereign', v_pending_sovereign,
    'pending_consolidated', v_pending_consolidated,
    'pending_high_value_responses', v_pending_responses,
    'skippable_noise', v_skippable,
    'total_to_bridge', v_pending_sovereign + v_pending_consolidated + v_pending_responses
  );
END;
$$;

-- ============================================================
-- RPC: mark_embrion_noise_consumed
-- Marca como consumido el ruido (evaluaciones, latidos,
-- respuestas de baja importancia) sin migrar al SMS
-- ============================================================

CREATE OR REPLACE FUNCTION mark_embrion_noise_consumed()
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_count INT;
BEGIN
  UPDATE embrion_memoria
  SET consumed_at = now()
  WHERE consumed_at IS NULL
    AND (
      tipo IN ('evaluacion', 'latido')
      OR (tipo = 'respuesta_embrion' AND (importancia < 7 OR importancia IS NULL))
    );
  
  GET DIAGNOSTICS v_count = ROW_COUNT;
  
  RETURN jsonb_build_object(
    'noise_marked_consumed', v_count,
    'reason', 'Low-value records (evaluacion, latido, respuesta_embrion imp<7) marked consumed without SMS migration'
  );
END;
$$;

-- ============================================================
-- Índice para optimizar el bridge query
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_embrion_memoria_bridge_pending
ON embrion_memoria (tipo, importancia DESC)
WHERE consumed_at IS NULL;

-- ============================================================
-- Comentarios
-- ============================================================

COMMENT ON FUNCTION bridge_embrion_to_sms IS 
'Bridge que migra memorias de alto valor del Embrión Loop al SMS.
Filtra por importancia y tipo. Deduplica por content_hash.
Ejecutar en batches de 100 hasta que pending = 0.';

COMMENT ON FUNCTION get_embrion_bridge_status IS
'Retorna estadísticas del estado del bridge embrion→SMS.
Muestra cuántos registros faltan por migrar vs ya consumidos.';

COMMENT ON FUNCTION mark_embrion_noise_consumed IS
'Marca como consumido el ruido sin valor para el SMS.
Evaluaciones, latidos, y respuestas de baja importancia.';
