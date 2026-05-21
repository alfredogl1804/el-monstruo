-- ============================================================
-- Migration 0060: Colmena Persistence
-- Persistencia para kernel/collective/ — la inteligencia
-- colectiva del Monstruo que opera en RAM y se pierde en
-- cada redeploy.
-- ============================================================
-- Fecha: 2026-05-21
-- Autor: Manus Scheduled Thread
-- Contexto: kernel/collective/ tiene 3 módulos:
--   1. ColectivaProtocol (pub/sub, debates, votaciones)
--   2. KnowledgePropagator (patrones aprendidos, propagación)
--   3. EmergenceDetector (detección de comportamiento emergente)
--   Los 3 operan con dicts in-memory que se pierden.
--   El código YA intenta persistir a tablas que no existen.
--   Esta migration crea las tablas que el código espera.
-- ============================================================

-- ============================================================
-- Tabla: learned_patterns
-- Patrones aprendidos por embriones, candidatos a propagación.
-- Esperada por: KnowledgePropagator.register_pattern()
-- Schema derivado de: LearnedPattern dataclass
-- ============================================================

CREATE TABLE IF NOT EXISTS learned_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Origen
  source_embrion TEXT NOT NULL,
  
  -- Clasificación
  pattern_type TEXT NOT NULL CHECK (pattern_type IN (
    'strategy',          -- Estrategia descubierta
    'tool_usage',        -- Uso efectivo de herramienta
    'error_avoidance',   -- Cómo evitar un error
    'optimization'       -- Optimización de proceso
  )),
  
  -- Contenido
  description TEXT NOT NULL,
  context TEXT NOT NULL,          -- Cuándo aplicar el patrón
  
  -- Métricas de efectividad
  success_rate FLOAT NOT NULL DEFAULT 0.0,
  times_applied INT NOT NULL DEFAULT 0,
  times_succeeded INT NOT NULL DEFAULT 0,
  
  -- Propagación
  propagated_to TEXT[] NOT NULL DEFAULT '{}',
  
  -- Estado
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  retracted_at TIMESTAMPTZ,
  retraction_reason TEXT,
  
  -- Timestamps
  discovered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_applied_at TIMESTAMPTZ
);

-- ============================================================
-- Tabla: embrion_messages
-- Mensajes inter-embrión del protocolo colectivo.
-- Esperada por: ColectivaProtocol.publish()
-- Schema derivado de: EmbrionMessage.to_dict()
-- ============================================================

CREATE TABLE IF NOT EXISTS embrion_messages (
  id TEXT PRIMARY KEY,  -- UUID generado por el código Python
  
  -- Identidad
  sender TEXT NOT NULL,
  
  -- Clasificación
  type TEXT NOT NULL CHECK (type IN (
    'insight',       -- Compartir descubrimiento
    'request',       -- Solicitar acción
    'response',      -- Respuesta a request
    'alert',         -- Alerta crítica
    'debate_open',   -- Invitación a debate
    'debate_arg',    -- Argumento en debate
    'vote_call',     -- Convocatoria a votación
    'vote_cast'      -- Voto emitido
  )),
  
  -- Contenido
  topic TEXT NOT NULL,
  content JSONB NOT NULL DEFAULT '{}',
  
  -- Routing
  recipients TEXT[] NOT NULL DEFAULT '{}',  -- Vacío = broadcast
  requires_response BOOLEAN NOT NULL DEFAULT FALSE,
  
  -- Estado
  responded BOOLEAN NOT NULL DEFAULT FALSE,
  response_id TEXT,  -- ID del mensaje de respuesta
  
  -- Timestamp
  timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Tabla: emergent_behaviors
-- Comportamientos emergentes detectados y validados.
-- Esperada por: EmergenceDetector._record_emergence()
-- ============================================================

CREATE TABLE IF NOT EXISTS emergent_behaviors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Clasificación
  type TEXT NOT NULL,  -- 'spontaneous_collaboration', 'novel_strategy', 'optimization'
  
  -- Detalle
  embriones_involved TEXT[] NOT NULL DEFAULT '{}',
  description TEXT NOT NULL,
  
  -- Validación
  validated BOOLEAN NOT NULL DEFAULT TRUE,
  validation_score FLOAT,
  
  -- Impacto
  impact_level TEXT CHECK (impact_level IN ('low', 'medium', 'high', 'critical')),
  
  -- Timestamps
  detected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Tabla: collective_debates
-- Debates estructurados entre embriones (persistencia).
-- Permite retomar debates después de redeploy.
-- ============================================================

CREATE TABLE IF NOT EXISTS collective_debates (
  id TEXT PRIMARY KEY,  -- UUID generado por el código Python
  
  -- Debate
  topic TEXT NOT NULL,
  context TEXT NOT NULL,
  
  -- Participantes
  participants TEXT[] NOT NULL,
  
  -- Configuración
  max_rounds INT NOT NULL DEFAULT 2,
  decision_method TEXT NOT NULL DEFAULT 'qualified_majority',
  
  -- Estado
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed', 'synthesized')),
  
  -- Argumentos (JSONB array para flexibilidad)
  arguments JSONB NOT NULL DEFAULT '[]',
  
  -- Resultado
  synthesis TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at TIMESTAMPTZ
);

-- ============================================================
-- Tabla: collective_votes
-- Votaciones colectivas entre embriones.
-- ============================================================

CREATE TABLE IF NOT EXISTS collective_votes (
  id TEXT PRIMARY KEY,  -- UUID generado por el código Python
  
  -- Votación
  topic TEXT NOT NULL,
  proposer TEXT NOT NULL,
  
  -- Configuración
  options TEXT[] NOT NULL,
  decision_method TEXT NOT NULL DEFAULT 'majority_vote',
  
  -- Votos (JSONB: {embrion: option})
  votes JSONB NOT NULL DEFAULT '{}',
  
  -- Resultado
  result JSONB,  -- {winner, vote_count, total_voters, method}
  
  -- Estado
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'tallied')),
  
  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  tallied_at TIMESTAMPTZ
);

-- ============================================================
-- Índices
-- ============================================================

-- Patrones por embrión fuente
CREATE INDEX IF NOT EXISTS idx_learned_patterns_source
ON learned_patterns (source_embrion, is_active)
WHERE is_active = TRUE;

-- Patrones por tipo
CREATE INDEX IF NOT EXISTS idx_learned_patterns_type
ON learned_patterns (pattern_type, success_rate DESC)
WHERE is_active = TRUE;

-- Mensajes por sender + timestamp
CREATE INDEX IF NOT EXISTS idx_embrion_messages_sender
ON embrion_messages (sender, timestamp DESC);

-- Mensajes por topic + timestamp (para receive con filtro de topic)
CREATE INDEX IF NOT EXISTS idx_embrion_messages_topic
ON embrion_messages (topic, timestamp DESC);

-- Mensajes pendientes de respuesta
CREATE INDEX IF NOT EXISTS idx_embrion_messages_pending
ON embrion_messages (requires_response, responded)
WHERE requires_response = TRUE AND responded = FALSE;

-- Emergencias por tipo
CREATE INDEX IF NOT EXISTS idx_emergent_behaviors_type
ON emergent_behaviors (type, detected_at DESC);

-- Debates activos
CREATE INDEX IF NOT EXISTS idx_collective_debates_status
ON collective_debates (status)
WHERE status = 'open';

-- Votaciones activas
CREATE INDEX IF NOT EXISTS idx_collective_votes_status
ON collective_votes (status)
WHERE status = 'open';

-- ============================================================
-- RLS
-- ============================================================

ALTER TABLE learned_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE embrion_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE emergent_behaviors ENABLE ROW LEVEL SECURITY;
ALTER TABLE collective_debates ENABLE ROW LEVEL SECURITY;
ALTER TABLE collective_votes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_learned_patterns" ON learned_patterns
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_embrion_messages" ON embrion_messages
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_emergent_behaviors" ON emergent_behaviors
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_collective_debates" ON collective_debates
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_collective_votes" ON collective_votes
  FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- RPC: get_colmena_stats
-- Estadísticas del sistema colectivo completo.
-- ============================================================

CREATE OR REPLACE FUNCTION get_colmena_stats()
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_patterns_total INT;
  v_patterns_active INT;
  v_messages_total INT;
  v_messages_24h INT;
  v_emergences_total INT;
  v_debates_open INT;
  v_votes_open INT;
  v_top_patterns JSONB;
BEGIN
  SELECT count(*) INTO v_patterns_total FROM learned_patterns;
  SELECT count(*) INTO v_patterns_active FROM learned_patterns WHERE is_active = TRUE;
  SELECT count(*) INTO v_messages_total FROM embrion_messages;
  SELECT count(*) INTO v_messages_24h FROM embrion_messages 
    WHERE timestamp > now() - interval '24 hours';
  SELECT count(*) INTO v_emergences_total FROM emergent_behaviors WHERE validated = TRUE;
  SELECT count(*) INTO v_debates_open FROM collective_debates WHERE status = 'open';
  SELECT count(*) INTO v_votes_open FROM collective_votes WHERE status = 'open';
  
  SELECT COALESCE(jsonb_agg(row_to_json(p)::jsonb), '[]'::jsonb)
  INTO v_top_patterns
  FROM (
    SELECT source_embrion, pattern_type, description, success_rate, times_applied
    FROM learned_patterns
    WHERE is_active = TRUE
    ORDER BY times_applied DESC, success_rate DESC
    LIMIT 10
  ) p;
  
  RETURN jsonb_build_object(
    'patterns', jsonb_build_object(
      'total', v_patterns_total,
      'active', v_patterns_active,
      'top_10', v_top_patterns
    ),
    'messages', jsonb_build_object(
      'total', v_messages_total,
      'last_24h', v_messages_24h
    ),
    'emergence', jsonb_build_object(
      'total_validated', v_emergences_total
    ),
    'debates_open', v_debates_open,
    'votes_open', v_votes_open
  );
END;
$$;

-- ============================================================
-- RPC: propagate_pattern_to_embriones
-- Propagar un patrón a embriones específicos (batch).
-- ============================================================

CREATE OR REPLACE FUNCTION propagate_pattern_to_embriones(
  p_pattern_id UUID,
  p_target_embriones TEXT[]
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_pattern RECORD;
  v_current_propagated TEXT[];
  v_new_targets TEXT[];
BEGIN
  SELECT * INTO v_pattern FROM learned_patterns WHERE id = p_pattern_id AND is_active = TRUE;
  
  IF v_pattern IS NULL THEN
    RETURN jsonb_build_object('status', 'error', 'message', 'Pattern not found or inactive');
  END IF;
  
  v_current_propagated := v_pattern.propagated_to;
  v_new_targets := ARRAY(
    SELECT unnest(p_target_embriones) 
    EXCEPT SELECT unnest(v_current_propagated)
  );
  
  IF array_length(v_new_targets, 1) IS NULL THEN
    RETURN jsonb_build_object('status', 'no_new_targets', 'already_propagated_to', v_current_propagated);
  END IF;
  
  UPDATE learned_patterns
  SET propagated_to = v_current_propagated || v_new_targets
  WHERE id = p_pattern_id;
  
  RETURN jsonb_build_object(
    'status', 'propagated',
    'pattern_id', p_pattern_id,
    'new_targets', v_new_targets,
    'total_propagated', v_current_propagated || v_new_targets
  );
END;
$$;

-- ============================================================
-- Comentarios
-- ============================================================

COMMENT ON TABLE learned_patterns IS
'Patrones aprendidos por embriones, candidatos a propagación inter-embrión. Usado por KnowledgePropagator.';

COMMENT ON TABLE embrion_messages IS
'Bus de mensajería inter-embrión. Pub/sub con tópicos, requests y responses. Usado por ColectivaProtocol.';

COMMENT ON TABLE emergent_behaviors IS
'Comportamientos emergentes detectados y validados. Usado por EmergenceDetector.';

COMMENT ON TABLE collective_debates IS
'Debates estructurados entre embriones con argumentos y síntesis.';

COMMENT ON TABLE collective_votes IS
'Votaciones colectivas con opciones, votos y resultado.';

COMMENT ON FUNCTION get_colmena_stats IS
'Estadísticas completas del sistema de inteligencia colectiva.';

COMMENT ON FUNCTION propagate_pattern_to_embriones IS
'Propagar un patrón aprendido a embriones específicos.';
