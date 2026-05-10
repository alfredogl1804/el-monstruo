-- migrations/sql/0003_loop_detection_log_self_verifier.sql
--
-- Sprint EMBRION-NEEDS-001 — Tarea 2 (Self-Verifier 3-decisiones)
--
-- Origen: bridge/sprints_propuestos/sprint_EMBRION_NEEDS_001.md (Tarea 2)
--
-- La tabla `loop_detection_log` ya existe (creada en sprint anterior para
-- detectar loops del task_planner). Tiene columnas:
--   id, detected_pattern, affected_plans, severity, auto_action_taken,
--   resolved, created_at
--
-- Self-Verifier necesita registrar también:
--   - cycle_id del embrión que disparó la evaluación
--   - resultado individual de cada una de las 3 decisiones
--   - votos NO (si >= 2, el cycle se aborta)
--   - el pensamiento evaluado (para auditoría humana)
--   - referencia opcional al embrion_memoria con el que coincidió (D2 fail)
--
-- Estrategia: ADD COLUMN IF NOT EXISTS — backward compatible, idempotente.
-- Las filas existentes (0 a la fecha del 10-may-2026) quedarán con NULLs en
-- las columnas nuevas, lo cual está bien porque el Self-Verifier marca con
-- `detected_pattern='self_verifier_abort'` y filtra por eso.

ALTER TABLE loop_detection_log
    ADD COLUMN IF NOT EXISTS cycle_id INTEGER,
    ADD COLUMN IF NOT EXISTS decision_purpose BOOLEAN,
    ADD COLUMN IF NOT EXISTS decision_novelty BOOLEAN,
    ADD COLUMN IF NOT EXISTS decision_verifiable BOOLEAN,
    ADD COLUMN IF NOT EXISTS votes_no INTEGER,
    ADD COLUMN IF NOT EXISTS aborted BOOLEAN,
    ADD COLUMN IF NOT EXISTS embrion_thought TEXT,
    ADD COLUMN IF NOT EXISTS embrion_thought_hash TEXT,
    ADD COLUMN IF NOT EXISTS similarity_match_id UUID,
    ADD COLUMN IF NOT EXISTS trigger_type TEXT,
    ADD COLUMN IF NOT EXISTS reasoning JSONB;

-- Índices para queries operativas del verifier
CREATE INDEX IF NOT EXISTS loop_detection_log_cycle_id_idx
    ON loop_detection_log (cycle_id) WHERE cycle_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS loop_detection_log_aborted_idx
    ON loop_detection_log (created_at DESC) WHERE aborted = TRUE;

CREATE INDEX IF NOT EXISTS loop_detection_log_thought_hash_idx
    ON loop_detection_log (embrion_thought_hash) WHERE embrion_thought_hash IS NOT NULL;

-- Comentarios
COMMENT ON COLUMN loop_detection_log.cycle_id IS
    'Cycle del embrion que disparo el self-verifier (Tarea 2 sprint EMBRION-NEEDS-001).';
COMMENT ON COLUMN loop_detection_log.decision_purpose IS
    'D1: contribuye al PURPOSE? TRUE=si, FALSE=no.';
COMMENT ON COLUMN loop_detection_log.decision_novelty IS
    'D2: nuevo o repite uno anterior 24h? TRUE=nuevo, FALSE=repetido.';
COMMENT ON COLUMN loop_detection_log.decision_verifiable IS
    'D3: produce output verificable o eco puro? TRUE=verificable, FALSE=eco.';
COMMENT ON COLUMN loop_detection_log.votes_no IS
    'Cuantas decisiones dieron NO. Si >= 2, aborted=true.';
COMMENT ON COLUMN loop_detection_log.embrion_thought_hash IS
    'sha256 del pensamiento normalizado, usado para detectar repeticiones D2.';
COMMENT ON COLUMN loop_detection_log.similarity_match_id IS
    'Si D2=FALSE, id de embrion_memoria con el que coincidio.';
