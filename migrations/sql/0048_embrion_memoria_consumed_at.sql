-- =============================================================================
-- Migración 0048 — Sprint S-EMBRION-009 — Tarea T1
-- Agregar consumed_at a embrion_memoria + índice parcial para detección eficiente
-- =============================================================================
--
-- Contexto:
--   Hallazgo H1 (auditoría 2026-05-17, Manus E2): el Embrión re-procesa el mismo
--   mensaje_alfredo cycle tras cycle cuando el self_verifier aborta el thought,
--   porque la heurística "ya respondido" en _detect_trigger compara timestamps
--   de respuesta_embrion contra mensaje_alfredo.created_at — si no se persiste
--   respuesta, el sistema interpreta que falta responder.
--
-- Causa raíz: kernel/embrion_loop.py:_detect_trigger (L686-726).
--
-- Solución (Cowork Opción 2, firmada en PR #139, mergeado 2026-05-17):
--   Marcar el mensaje como consumed ANTES de invocar el LLM, no después.
--   Si el verifier aborta, el mensaje sigue marcado como consumido — sin bucle.
--   La elección de "no responder" ocurre upstream del LLM, no downstream
--   (soberanía cognitiva del Embrión, Obj #12).
--
-- Cumplimiento DSC:
--   - DSC-S-006 (RLS por defecto): policy "service_role_only" FOR ALL ya cubre
--     UPDATE de consumed_at por service_role. No requiere policy nueva.
--     (verificado contra migrations/sql/0006_embrion_memoria_explicit_policy.sql)
--   - DSC-G-008 v2: archivo entregado a Cowork para audit content antes del merge.
--   - Idempotencia: ADD COLUMN IF NOT EXISTS + CREATE INDEX IF NOT EXISTS.
--
-- Atomicidad:
--   Transacción BEGIN/COMMIT. Rollback inmediato si falla.
--
-- Numeración:
--   0048 verificado disponible (último aplicado: 0047_embrion_memoria_tipo_check
--   _expand_vivos por Cowork T2-A 2026-05-17 vía MCP supabase-monstruo).
--
-- Aplicar con (modo canónico post-H12):
--   MCP supabase-monstruo apply_migration tool (Cowork autoridad T1 delegada).
--
-- Smoke test post-aplicación obligatorio:
--   1. \d embrion_memoria → muestra columna consumed_at TIMESTAMPTZ NULL
--   2. \di+ idx_embrion_memoria_unconsumed → muestra índice parcial
--   3. INSERT mensaje_alfredo de prueba con consumed_at NULL
--   4. UPDATE consumed_at = NOW() WHERE id = X — verifica RLS service_role OK
--   5. SELECT WHERE consumed_at IS NULL — verifica filtro funciona con índice
-- =============================================================================
BEGIN;

-- T1.1 — Agregar columna consumed_at
ALTER TABLE public.embrion_memoria
  ADD COLUMN IF NOT EXISTS consumed_at TIMESTAMPTZ NULL;

COMMENT ON COLUMN public.embrion_memoria.consumed_at IS
  'NULL = pendiente, NOT NULL = procesado por _detect_trigger. '
  'Marcado ANTES de invocar LLM, idempotente. Sprint S-EMBRION-009 (2026-05-17). '
  'Origen: hallazgo H1 — bucle infinito de re-detección cuando self_verifier aborta. '
  'Doctrina: soberanía cognitiva del Embrión, elección upstream del LLM.';

-- T1.2 — Índice parcial para detección eficiente de mensajes pendientes
-- WHERE consumed_at IS NULL: solo indexa los rows relevantes para _detect_trigger,
-- minimizando tamaño del índice y maximizando hit rate. PostgreSQL aplica este
-- índice automáticamente cuando la query incluye consumed_at IS NULL.
CREATE INDEX IF NOT EXISTS idx_embrion_memoria_unconsumed
  ON public.embrion_memoria (tipo, created_at DESC)
  WHERE consumed_at IS NULL;

COMMENT ON INDEX public.idx_embrion_memoria_unconsumed IS
  'Sprint S-EMBRION-009: acelera _detect_trigger filtrando solo mensajes pendientes. '
  'Parcial (consumed_at IS NULL) para eficiencia. Composite (tipo, created_at DESC) '
  'matches el ORDER BY del query original.';

COMMIT;

-- =============================================================================
-- Notas post-aplicación:
-- =============================================================================
--
-- 1. Backfill conservador en migración 0049 (T5 del sprint):
--    UPDATE embrion_memoria SET consumed_at = NOW()
--    WHERE tipo = 'mensaje_alfredo' AND consumed_at IS NULL
--      AND EXISTS (SELECT 1 FROM embrion_memoria r
--                  WHERE r.tipo = 'respuesta_embrion'
--                    AND r.created_at > m.created_at
--                    AND r.created_at < m.created_at + INTERVAL '5 minutes');
--    No incluido en esta migration para mantener scope mínimo (DSC-G-008 v2).
--
-- 2. Schema cache reload no requerido: ALTER TABLE ADD COLUMN dispara reload
--    automático en PostgREST/Supabase moderno.
--
-- 3. Backward compatibility: rows existentes pre-009 quedan con consumed_at NULL
--    y serán procesados FIFO por _detect_trigger. Backfill T5 los marca como
--    consumed solo si tienen respuesta_embrion en ventana de 5 minutos posterior.
-- =============================================================================
