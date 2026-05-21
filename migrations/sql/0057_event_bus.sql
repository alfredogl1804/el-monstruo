-- Migration 0057: Monstruo Event Bus
-- El stream de eventos fundacional del Reactor de Coherencia.
-- Principio: "La Operación ES el Registro" — todo lo que altera el Monstruo
-- se emite como evento inmutable. El estado se DERIVA, no se escribe.
-- Fecha: 2026-05-21

-- ============================================================
-- TABLA PRINCIPAL: monstruo_event_stream
-- Cada fila es un evento inmutable. Nunca se edita. Nunca se borra.
-- ============================================================

CREATE TABLE IF NOT EXISTS monstruo_event_stream (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Clasificación del evento
  event_type TEXT NOT NULL CHECK (event_type IN (
    'decision',     -- Se tomó una decisión arquitectónica/estratégica
    'discovery',    -- Se descubrió algo nuevo (concepto, patrón, insight)
    'error',        -- Algo falló y se aprendió de ello
    'concept',      -- Nació un concepto nuevo (axioma candidato)
    'build',        -- Se construyó algo (PR, migration, deploy)
    'destroy',      -- Se demolió/deprecó algo
    'emotion',      -- Momento emocional relevante (capa personal)
    'proposal',     -- Se propuso algo que aún no se aprueba
    'validation',   -- Se validó o invalidó una creencia previa
    'connection'    -- Se conectaron dos ideas/sistemas que estaban separados
  )),
  
  -- Origen del evento
  source TEXT NOT NULL,              -- quién lo emitió (manus_hilo_xyz, chatgpt_session, alfredo_voice, github_webhook, embrion_tecnico)
  source_type TEXT NOT NULL CHECK (source_type IN (
    'manus_thread',    -- Hilo de Manus
    'chatgpt',         -- Sesión de ChatGPT
    'claude',          -- Claude/Cowork
    'sabio',           -- Consulta a un sabio
    'embrion',         -- Un embrión operando
    'human',           -- Alfredo directamente
    'webhook',         -- GitHub/Railway/Supabase webhook
    'system'           -- El propio Reactor/sistema
  )),
  
  -- Contenido del evento
  title TEXT NOT NULL,                -- Resumen en 1 línea (para índice rápido)
  content TEXT NOT NULL,              -- Contenido completo del evento
  context TEXT,                       -- Lo que precedió al evento (opcional)
  
  -- Señales de valor
  value_signal TEXT NOT NULL DEFAULT 'medium' CHECK (value_signal IN ('critical', 'high', 'medium', 'low')),
  
  -- Clasificación automática (llenada por el trigger)
  auto_classification JSONB DEFAULT '{}'::jsonb,  -- {is_axiom_candidate, is_lesson, is_concept, is_pattern, entities_detected}
  
  -- Conexiones con el grafo existente
  related_entities TEXT[] DEFAULT '{}',           -- Entidades detectadas automáticamente
  related_memories UUID[] DEFAULT '{}',           -- Links a sovereign_memories existentes
  related_events UUID[] DEFAULT '{}',             -- Links a otros eventos (cadena causal)
  
  -- Metadata del Reactor
  crystallized BOOLEAN DEFAULT FALSE,             -- ¿Ya se procesó y se ingresó al SMS?
  crystallized_at TIMESTAMPTZ,
  crystallized_memory_id UUID,                    -- ID de la memoria soberana resultante (si aplica)
  
  -- Proyecciones afectadas
  affects_genome BOOLEAN DEFAULT FALSE,           -- ¿Cambia algo en el MONSTRUO_GENOME?
  affects_plan_regulador BOOLEAN DEFAULT FALSE,   -- ¿Cambia algo en el PLAN_REGULADOR?
  affects_bitacora BOOLEAN DEFAULT TRUE,          -- Siempre va a la bitácora (default)
  
  -- Capa personal (solo para eventos tipo emotion o con señal personal)
  personal_layer JSONB,  -- {feeling, inspiration, significance, milestone}
  
  -- Timestamps inmutables
  emitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  -- Nunca se modifica después de crear
  CONSTRAINT immutable_event CHECK (TRUE)  -- Placeholder para RLS policy que previene UPDATE
);

-- Índices para consulta rápida
CREATE INDEX IF NOT EXISTS idx_event_stream_type ON monstruo_event_stream(event_type);
CREATE INDEX IF NOT EXISTS idx_event_stream_source ON monstruo_event_stream(source_type);
CREATE INDEX IF NOT EXISTS idx_event_stream_value ON monstruo_event_stream(value_signal);
CREATE INDEX IF NOT EXISTS idx_event_stream_emitted ON monstruo_event_stream(emitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_event_stream_crystallized ON monstruo_event_stream(crystallized) WHERE crystallized = FALSE;
CREATE INDEX IF NOT EXISTS idx_event_stream_entities ON monstruo_event_stream USING GIN(related_entities);

-- RLS
ALTER TABLE monstruo_event_stream ENABLE ROW LEVEL SECURITY;
CREATE POLICY "service_role_full_access" ON monstruo_event_stream
  FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- RPC: emit_event — Punto de entrada principal del Event Bus
-- Cualquier IA/servicio llama a esto para emitir un evento
-- ============================================================

CREATE OR REPLACE FUNCTION emit_event(
  p_event_type TEXT,
  p_source TEXT,
  p_source_type TEXT,
  p_title TEXT,
  p_content TEXT,
  p_context TEXT DEFAULT NULL,
  p_value_signal TEXT DEFAULT 'medium',
  p_related_entities TEXT[] DEFAULT '{}',
  p_related_events UUID[] DEFAULT '{}',
  p_personal_layer JSONB DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_event_id UUID;
  v_auto_class JSONB;
BEGIN
  -- Auto-clasificación básica basada en señales del contenido
  v_auto_class := jsonb_build_object(
    'is_axiom_candidate', (p_value_signal = 'critical' AND p_event_type IN ('decision', 'concept', 'discovery')),
    'is_lesson', (p_event_type = 'error'),
    'is_concept', (p_event_type IN ('concept', 'discovery')),
    'is_pattern', (p_event_type = 'connection'),
    'is_personal', (p_event_type = 'emotion' OR p_personal_layer IS NOT NULL)
  );

  INSERT INTO monstruo_event_stream (
    event_type, source, source_type, title, content, context,
    value_signal, auto_classification, related_entities, related_events,
    personal_layer,
    affects_genome, affects_plan_regulador
  ) VALUES (
    p_event_type, p_source, p_source_type, p_title, p_content, p_context,
    p_value_signal, v_auto_class, p_related_entities, p_related_events,
    p_personal_layer,
    (p_event_type IN ('build', 'destroy', 'decision')),
    (p_event_type IN ('decision', 'proposal', 'destroy') AND p_value_signal IN ('critical', 'high'))
  )
  RETURNING id INTO v_event_id;

  RETURN jsonb_build_object(
    'event_id', v_event_id,
    'status', 'emitted',
    'auto_classification', v_auto_class,
    'crystallization_pending', (p_value_signal IN ('critical', 'high'))
  );
END;
$$;

-- ============================================================
-- RPC: crystallize_pending_events — El Reactor consume eventos pendientes
-- y los ingesta al SMS como memorias soberanas
-- ============================================================

CREATE OR REPLACE FUNCTION crystallize_pending_events(p_limit INT DEFAULT 50)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_event RECORD;
  v_memory_id UUID;
  v_crystallized_count INT := 0;
  v_results JSONB := '[]'::jsonb;
  v_entities_jsonb JSONB;
  v_content_hash TEXT;
BEGIN
  FOR v_event IN
    SELECT * FROM monstruo_event_stream
    WHERE crystallized = FALSE
      AND value_signal IN ('critical', 'high')
    ORDER BY emitted_at ASC
    LIMIT p_limit
  LOOP
    v_entities_jsonb := to_jsonb(v_event.related_entities);
    v_content_hash := md5(v_event.title || v_event.content);

    -- Insertar como memoria soberana
    INSERT INTO sovereign_memories (
      content,
      content_hash,
      memory_type,
      source,
      agent_id,
      confidence,
      layer,
      tags,
      entities
    ) VALUES (
      v_event.title || E'\n\n' || v_event.content,
      v_content_hash,
      CASE 
        WHEN v_event.event_type IN ('concept', 'discovery', 'decision') THEN 'semantic'
        ELSE 'episodic'
      END,
      'event_bus:' || v_event.source,
      v_event.source,
      CASE v_event.value_signal
        WHEN 'critical' THEN 1.0
        WHEN 'high' THEN 0.85
        ELSE 0.7
      END,
      3,  -- layer 3 = sovereign
      ARRAY[v_event.event_type, v_event.source_type, 'event_bus'],
      v_entities_jsonb
    )
    RETURNING id INTO v_memory_id;

    -- Marcar evento como cristalizado
    UPDATE monstruo_event_stream
    SET crystallized = TRUE,
        crystallized_at = now(),
        crystallized_memory_id = v_memory_id
    WHERE id = v_event.id;

    v_crystallized_count := v_crystallized_count + 1;
    v_results := v_results || jsonb_build_object(
      'event_id', v_event.id,
      'memory_id', v_memory_id,
      'title', v_event.title
    );
  END LOOP;

  RETURN jsonb_build_object(
    'crystallized_count', v_crystallized_count,
    'events', v_results
  );
END;
$$;

-- ============================================================
-- RPC: query_event_stream — Consultar la bitácora con filtros
-- ============================================================

CREATE OR REPLACE FUNCTION query_event_stream(
  p_event_type TEXT DEFAULT NULL,
  p_source_type TEXT DEFAULT NULL,
  p_value_signal TEXT DEFAULT NULL,
  p_since TIMESTAMPTZ DEFAULT NULL,
  p_entity TEXT DEFAULT NULL,
  p_limit INT DEFAULT 50
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_results JSONB;
BEGIN
  SELECT jsonb_agg(row_to_json(e)::jsonb ORDER BY e.emitted_at DESC)
  INTO v_results
  FROM (
    SELECT id, event_type, source, source_type, title, content,
           value_signal, auto_classification, related_entities,
           personal_layer, emitted_at, crystallized
    FROM monstruo_event_stream
    WHERE (p_event_type IS NULL OR event_type = p_event_type)
      AND (p_source_type IS NULL OR source_type = p_source_type)
      AND (p_value_signal IS NULL OR value_signal = p_value_signal)
      AND (p_since IS NULL OR emitted_at >= p_since)
      AND (p_entity IS NULL OR p_entity = ANY(related_entities))
    ORDER BY emitted_at DESC
    LIMIT p_limit
  ) e;

  RETURN COALESCE(v_results, '[]'::jsonb);
END;
$$;

-- ============================================================
-- RPC: get_event_stream_stats — Estado del bus para el Reactor
-- ============================================================

CREATE OR REPLACE FUNCTION get_event_stream_stats()
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_total INT;
  v_pending INT;
  v_by_type JSONB;
  v_by_source JSONB;
  v_by_value JSONB;
BEGIN
  SELECT count(*) INTO v_total FROM monstruo_event_stream;
  SELECT count(*) INTO v_pending FROM monstruo_event_stream WHERE crystallized = FALSE AND value_signal IN ('critical', 'high');
  
  SELECT jsonb_object_agg(event_type, cnt)
  INTO v_by_type
  FROM (SELECT event_type, count(*) as cnt FROM monstruo_event_stream GROUP BY event_type) t;

  SELECT jsonb_object_agg(source_type, cnt)
  INTO v_by_source
  FROM (SELECT source_type, count(*) as cnt FROM monstruo_event_stream GROUP BY source_type) t;

  SELECT jsonb_object_agg(value_signal, cnt)
  INTO v_by_value
  FROM (SELECT value_signal, count(*) as cnt FROM monstruo_event_stream GROUP BY value_signal) t;

  RETURN jsonb_build_object(
    'total_events', v_total,
    'pending_crystallization', v_pending,
    'by_type', COALESCE(v_by_type, '{}'::jsonb),
    'by_source', COALESCE(v_by_source, '{}'::jsonb),
    'by_value', COALESCE(v_by_value, '{}'::jsonb)
  );
END;
$$;

-- Comments
COMMENT ON TABLE monstruo_event_stream IS 'Event Bus del Monstruo — stream inmutable de todo lo que ocurre. Principio: La Operación ES el Registro.';
COMMENT ON FUNCTION emit_event IS 'Punto de entrada principal del Event Bus. Cualquier IA/servicio emite eventos aquí.';
COMMENT ON FUNCTION crystallize_pending_events IS 'El Reactor consume eventos de alto valor y los cristaliza como memorias soberanas.';
COMMENT ON FUNCTION query_event_stream IS 'Consultar la bitácora universal con filtros por tipo, fuente, valor, tiempo, o entidad.';
COMMENT ON FUNCTION get_event_stream_stats IS 'Estado del bus para monitoreo del Reactor.';
