-- ═══════════════════════════════════════════════════════════════════
-- Migration 014: Sprint 81.5 — alinear schema con código actual
-- ═══════════════════════════════════════════════════════════════════
-- Resuelve los errores activos detectados en producción tras Sprint 81:
--   1. verification_results.cost_usd (PGRST204) — la tabla en prod se
--      creó antes de la migración 011 que añadió esta columna.
--   2. task_plans.cycles (42703) — PENDIENTE: requiere stack trace de
--      Manus antes de tocar. No hay código que escriba "cycles" a
--      task_plans según grep recursivo del kernel. Ver bridge/cowork_to_manus.md
-- ═══════════════════════════════════════════════════════════════════

-- ─── 1. verification_results.cost_usd ─────────────────────────────
-- Migración 011 ya define cost_usd. Si la tabla en prod se creó antes
-- de esa migración, la columna falta. Añadirla idempotente.
ALTER TABLE verification_results
    ADD COLUMN IF NOT EXISTS cost_usd NUMERIC(10,6) DEFAULT 0;

COMMENT ON COLUMN verification_results.cost_usd IS
    'Costo de la verificación LLM (solo se usa en casos ambiguos). Sprint 81.5: añadido vía ALTER porque la tabla original se creó antes de la migración 011.';

-- ─── 2. task_plans.cycles ─────────────────────────────────────────
-- PENDIENTE: requiere stack trace exacto del error 42703.
-- Según búsqueda en kernel/, NO existe código que escriba "cycles" a
-- task_plans. Posibles causas a investigar:
--   - Trigger SQL legacy en Supabase
--   - Otro proceso (no el kernel) que escribe a la tabla
--   - El log muestra el campo equivocado
-- NO se aplica ALTER hasta confirmar la causa raíz.

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-aplicación
-- ═══════════════════════════════════════════════════════════════════
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'verification_results' AND column_name = 'cost_usd';
-- Esperado: 1 fila con cost_usd | numeric | YES | 0
-- ═══════════════════════════════════════════════════════════════════
