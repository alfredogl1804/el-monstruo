-- ============================================================
-- Migration 0059: Specialists Memory
-- Memoria persistente para los embriones del Monstruo.
-- Cada embrión puede recordar lo que aprendió, consultar
-- su historial, y compartir conocimiento con otros.
-- ============================================================
-- Fecha: 2026-05-21
-- Autor: Manus Scheduled Thread
-- Contexto: Los 8 embriones (Creativo, Estratega, Financiero,
--   Investigador, ProductArchitect, Técnico, Ventas, CriticVisual)
--   son stateless. Pierden todo contexto entre invocaciones.
--   Esta migration les da memoria persistente.
-- ============================================================

-- ============================================================
-- Tabla: embrion_knowledge
-- Conocimiento aprendido por cada especialista.
-- Cada registro es algo que un embrión "sabe" de forma duradera.
-- ============================================================

CREATE TABLE IF NOT EXISTS embrion_knowledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Identidad del especialista
  specialist_id TEXT NOT NULL,  -- 'creativo', 'estratega', 'financiero', etc.
  
  -- El conocimiento
  knowledge_type TEXT NOT NULL CHECK (knowledge_type IN (
    'preference',      -- Preferencia de Alfredo descubierta
    'correction',      -- Corrección recibida (aprendizaje de error)
    'pattern',         -- Patrón detectado en múltiples tareas
    'expertise',       -- Conocimiento técnico adquirido
    'constraint',      -- Restricción o regla descubierta
    'relationship',    -- Relación entre conceptos
    'anti_pattern'     -- Algo que NO debe hacerse
  )),
  
  content TEXT NOT NULL,           -- El conocimiento en lenguaje natural
  content_hash TEXT NOT NULL,      -- md5(content) para dedup
  
  -- Contexto y origen
  source_task_id UUID,             -- Tarea donde se aprendió (FK a embrion_task_history)
  source_description TEXT,         -- Descripción breve del contexto de aprendizaje
  
  -- Relevancia y decaimiento
  confidence FLOAT NOT NULL DEFAULT 0.8,   -- 0-1, decrece si se contradice
  times_applied INT NOT NULL DEFAULT 0,    -- Cuántas veces se usó este conocimiento
  times_validated INT NOT NULL DEFAULT 0,  -- Cuántas veces se confirmó correcto
  times_contradicted INT NOT NULL DEFAULT 0, -- Cuántas veces se contradijo
  
  -- Compartibilidad
  is_shared BOOLEAN NOT NULL DEFAULT FALSE,  -- Visible para otros embriones
  shared_with TEXT[] NOT NULL DEFAULT '{}',  -- Embriones específicos que pueden verlo
  
  -- Lifecycle
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  superseded_by UUID REFERENCES embrion_knowledge(id),
  
  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_applied_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ  -- Conocimiento temporal (ej: "el cliente quiere X para este sprint")
);

-- ============================================================
-- Tabla: embrion_task_history
-- Historial de ejecuciones de cada embrión.
-- Permite recall de contexto y aprendizaje de outcomes.
-- ============================================================

CREATE TABLE IF NOT EXISTS embrion_task_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Identidad
  specialist_id TEXT NOT NULL,
  
  -- La tarea
  task_type TEXT NOT NULL,          -- 'brand_evaluation', 'financial_analysis', etc.
  task_input_summary TEXT NOT NULL, -- Resumen del input (no el input completo)
  task_output_summary TEXT,         -- Resumen del output producido
  
  -- Outcome
  outcome TEXT CHECK (outcome IN (
    'success',        -- Tarea completada satisfactoriamente
    'partial',        -- Completada parcialmente
    'rejected',       -- Output rechazado por Alfredo
    'corrected',      -- Output corregido por Alfredo
    'error'           -- Falló técnicamente
  )),
  
  -- Feedback
  feedback TEXT,                    -- Feedback textual recibido
  correction_applied TEXT,          -- Qué se corrigió
  
  -- Metadata
  project_context TEXT,             -- Proyecto donde se ejecutó
  duration_ms INT,                  -- Duración de ejecución
  tokens_used INT,                  -- Tokens consumidos
  model_used TEXT,                  -- Modelo IA usado
  
  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);

-- ============================================================
-- Índices
-- ============================================================

-- Búsqueda rápida por especialista
CREATE INDEX IF NOT EXISTS idx_embrion_knowledge_specialist 
ON embrion_knowledge (specialist_id, is_active, knowledge_type)
WHERE is_active = TRUE;

-- Búsqueda de conocimiento compartido
CREATE INDEX IF NOT EXISTS idx_embrion_knowledge_shared
ON embrion_knowledge (is_shared, specialist_id)
WHERE is_shared = TRUE AND is_active = TRUE;

-- Dedup por content_hash
CREATE UNIQUE INDEX IF NOT EXISTS idx_embrion_knowledge_dedup
ON embrion_knowledge (specialist_id, content_hash)
WHERE is_active = TRUE;

-- Historial por especialista
CREATE INDEX IF NOT EXISTS idx_embrion_task_history_specialist
ON embrion_task_history (specialist_id, created_at DESC);

-- Historial por outcome (para aprender de errores)
CREATE INDEX IF NOT EXISTS idx_embrion_task_history_outcome
ON embrion_task_history (specialist_id, outcome)
WHERE outcome IN ('rejected', 'corrected', 'error');

-- ============================================================
-- RLS
-- ============================================================

ALTER TABLE embrion_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE embrion_task_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_full_access_knowledge" ON embrion_knowledge
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_full_access_task_history" ON embrion_task_history
  FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- RPC: remember_specialist_knowledge
-- Un embrión almacena algo que aprendió.
-- ============================================================

CREATE OR REPLACE FUNCTION remember_specialist_knowledge(
  p_specialist_id TEXT,
  p_knowledge_type TEXT,
  p_content TEXT,
  p_source_description TEXT DEFAULT NULL,
  p_source_task_id UUID DEFAULT NULL,
  p_is_shared BOOLEAN DEFAULT FALSE,
  p_shared_with TEXT[] DEFAULT '{}'::TEXT[],
  p_confidence FLOAT DEFAULT 0.8,
  p_expires_at TIMESTAMPTZ DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_hash TEXT;
  v_existing_id UUID;
  v_new_id UUID;
BEGIN
  v_hash := md5(p_content);
  
  -- Check for existing active knowledge with same hash
  SELECT id INTO v_existing_id
  FROM embrion_knowledge
  WHERE specialist_id = p_specialist_id
    AND content_hash = v_hash
    AND is_active = TRUE;
  
  IF v_existing_id IS NOT NULL THEN
    -- Reinforce existing knowledge
    UPDATE embrion_knowledge
    SET times_validated = times_validated + 1,
        confidence = LEAST(confidence + 0.05, 1.0),
        last_applied_at = now()
    WHERE id = v_existing_id;
    
    RETURN jsonb_build_object(
      'status', 'reinforced',
      'knowledge_id', v_existing_id,
      'message', 'Existing knowledge reinforced'
    );
  END IF;
  
  -- Insert new knowledge
  INSERT INTO embrion_knowledge (
    specialist_id, knowledge_type, content, content_hash,
    source_task_id, source_description,
    confidence, is_shared, shared_with, expires_at
  ) VALUES (
    p_specialist_id, p_knowledge_type, p_content, v_hash,
    p_source_task_id, p_source_description,
    p_confidence, p_is_shared, p_shared_with, p_expires_at
  )
  RETURNING id INTO v_new_id;
  
  RETURN jsonb_build_object(
    'status', 'learned',
    'knowledge_id', v_new_id,
    'specialist_id', p_specialist_id,
    'knowledge_type', p_knowledge_type
  );
END;
$$;

-- ============================================================
-- RPC: recall_specialist_context
-- Un embrión recupera su contexto relevante antes de ejecutar.
-- Retorna: su conocimiento activo + conocimiento compartido +
-- historial reciente de tareas similares.
-- ============================================================

CREATE OR REPLACE FUNCTION recall_specialist_context(
  p_specialist_id TEXT,
  p_task_type TEXT DEFAULT NULL,
  p_limit_knowledge INT DEFAULT 20,
  p_limit_history INT DEFAULT 5
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_knowledge JSONB;
  v_shared_knowledge JSONB;
  v_history JSONB;
  v_corrections JSONB;
BEGIN
  -- Own active knowledge (most recently applied first)
  SELECT COALESCE(jsonb_agg(row_to_json(k)::jsonb ORDER BY k.times_applied DESC, k.confidence DESC), '[]'::jsonb)
  INTO v_knowledge
  FROM (
    SELECT id, knowledge_type, content, confidence, times_applied, created_at
    FROM embrion_knowledge
    WHERE specialist_id = p_specialist_id
      AND is_active = TRUE
      AND (expires_at IS NULL OR expires_at > now())
    ORDER BY times_applied DESC, confidence DESC
    LIMIT p_limit_knowledge
  ) k;
  
  -- Shared knowledge from other embriones
  SELECT COALESCE(jsonb_agg(row_to_json(s)::jsonb ORDER BY s.confidence DESC), '[]'::jsonb)
  INTO v_shared_knowledge
  FROM (
    SELECT id, specialist_id, knowledge_type, content, confidence
    FROM embrion_knowledge
    WHERE specialist_id != p_specialist_id
      AND is_active = TRUE
      AND (is_shared = TRUE OR p_specialist_id = ANY(shared_with))
      AND (expires_at IS NULL OR expires_at > now())
    ORDER BY confidence DESC
    LIMIT 10
  ) s;
  
  -- Recent task history (similar tasks)
  SELECT COALESCE(jsonb_agg(row_to_json(h)::jsonb ORDER BY h.created_at DESC), '[]'::jsonb)
  INTO v_history
  FROM (
    SELECT id, task_type, task_input_summary, task_output_summary, outcome, feedback, created_at
    FROM embrion_task_history
    WHERE specialist_id = p_specialist_id
      AND (p_task_type IS NULL OR task_type = p_task_type)
    ORDER BY created_at DESC
    LIMIT p_limit_history
  ) h;
  
  -- Recent corrections (critical for not repeating mistakes)
  SELECT COALESCE(jsonb_agg(row_to_json(c)::jsonb ORDER BY c.created_at DESC), '[]'::jsonb)
  INTO v_corrections
  FROM (
    SELECT id, task_type, feedback, correction_applied, created_at
    FROM embrion_task_history
    WHERE specialist_id = p_specialist_id
      AND outcome IN ('rejected', 'corrected')
    ORDER BY created_at DESC
    LIMIT 5
  ) c;
  
  RETURN jsonb_build_object(
    'specialist_id', p_specialist_id,
    'knowledge_count', jsonb_array_length(v_knowledge),
    'knowledge', v_knowledge,
    'shared_knowledge_count', jsonb_array_length(v_shared_knowledge),
    'shared_knowledge', v_shared_knowledge,
    'recent_history', v_history,
    'recent_corrections', v_corrections
  );
END;
$$;

-- ============================================================
-- RPC: log_specialist_task
-- Registra la ejecución de una tarea por un embrión.
-- ============================================================

CREATE OR REPLACE FUNCTION log_specialist_task(
  p_specialist_id TEXT,
  p_task_type TEXT,
  p_task_input_summary TEXT,
  p_task_output_summary TEXT DEFAULT NULL,
  p_outcome TEXT DEFAULT 'success',
  p_feedback TEXT DEFAULT NULL,
  p_correction_applied TEXT DEFAULT NULL,
  p_project_context TEXT DEFAULT NULL,
  p_duration_ms INT DEFAULT NULL,
  p_tokens_used INT DEFAULT NULL,
  p_model_used TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_task_id UUID;
BEGIN
  INSERT INTO embrion_task_history (
    specialist_id, task_type, task_input_summary, task_output_summary,
    outcome, feedback, correction_applied, project_context,
    duration_ms, tokens_used, model_used, completed_at
  ) VALUES (
    p_specialist_id, p_task_type, p_task_input_summary, p_task_output_summary,
    p_outcome, p_feedback, p_correction_applied, p_project_context,
    p_duration_ms, p_tokens_used, p_model_used, now()
  )
  RETURNING id INTO v_task_id;
  
  -- If task was corrected, auto-learn from the correction
  IF p_outcome IN ('corrected', 'rejected') AND p_correction_applied IS NOT NULL THEN
    PERFORM remember_specialist_knowledge(
      p_specialist_id,
      'correction',
      p_correction_applied,
      'Auto-learned from task correction: ' || p_task_type,
      v_task_id,
      TRUE,  -- Share corrections with all embriones
      '{}'::TEXT[],
      0.9
    );
  END IF;
  
  RETURN jsonb_build_object(
    'status', 'logged',
    'task_id', v_task_id,
    'specialist_id', p_specialist_id,
    'outcome', p_outcome,
    'auto_learned', (p_outcome IN ('corrected', 'rejected') AND p_correction_applied IS NOT NULL)
  );
END;
$$;

-- ============================================================
-- RPC: get_specialists_memory_stats
-- Estadísticas globales del sistema de memoria de especialistas.
-- ============================================================

CREATE OR REPLACE FUNCTION get_specialists_memory_stats()
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_knowledge_by_specialist JSONB;
  v_tasks_by_specialist JSONB;
  v_corrections_total INT;
  v_knowledge_total INT;
BEGIN
  SELECT COALESCE(jsonb_agg(row_to_json(k)::jsonb), '[]'::jsonb)
  INTO v_knowledge_by_specialist
  FROM (
    SELECT specialist_id, count(*) as knowledge_count,
           avg(confidence)::numeric(3,2) as avg_confidence,
           sum(times_applied) as total_applications
    FROM embrion_knowledge
    WHERE is_active = TRUE
    GROUP BY specialist_id
    ORDER BY knowledge_count DESC
  ) k;
  
  SELECT COALESCE(jsonb_agg(row_to_json(t)::jsonb), '[]'::jsonb)
  INTO v_tasks_by_specialist
  FROM (
    SELECT specialist_id, count(*) as task_count,
           count(*) FILTER (WHERE outcome = 'success') as successes,
           count(*) FILTER (WHERE outcome IN ('rejected', 'corrected')) as corrections
    FROM embrion_task_history
    GROUP BY specialist_id
    ORDER BY task_count DESC
  ) t;
  
  SELECT count(*) INTO v_corrections_total
  FROM embrion_task_history WHERE outcome IN ('rejected', 'corrected');
  
  SELECT count(*) INTO v_knowledge_total
  FROM embrion_knowledge WHERE is_active = TRUE;
  
  RETURN jsonb_build_object(
    'total_active_knowledge', v_knowledge_total,
    'total_corrections', v_corrections_total,
    'knowledge_by_specialist', v_knowledge_by_specialist,
    'tasks_by_specialist', v_tasks_by_specialist
  );
END;
$$;

-- ============================================================
-- Comentarios
-- ============================================================

COMMENT ON TABLE embrion_knowledge IS 
'Conocimiento persistente de cada embrión especialista. Cada registro es algo que el embrión aprendió y puede recordar en futuras invocaciones.';

COMMENT ON TABLE embrion_task_history IS
'Historial de ejecuciones de cada embrión. Permite recall de contexto y aprendizaje de outcomes.';

COMMENT ON FUNCTION remember_specialist_knowledge IS
'Un embrión almacena algo que aprendió. Deduplica por content_hash. Refuerza si ya existe.';

COMMENT ON FUNCTION recall_specialist_context IS
'Un embrión recupera su contexto antes de ejecutar: conocimiento propio + compartido + historial + correcciones.';

COMMENT ON FUNCTION log_specialist_task IS
'Registra ejecución de tarea. Si outcome es corrected/rejected, auto-aprende la corrección.';

COMMENT ON FUNCTION get_specialists_memory_stats IS
'Estadísticas globales del sistema de memoria de especialistas.';
