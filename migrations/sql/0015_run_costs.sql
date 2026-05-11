-- ============================================================================
-- Migración 0015: run_costs
-- Origen retroactivo: Sprint 15 — FinOps Soberano (2026-04-20)
-- Resolución gap: 2026-05-11 (Hilo Ejecutor 1, Manus)
-- DSC referenciado: DSC-S-006 v1.1 (RLS por defecto), DSC-S-007 (naming canónico)
--
-- Contexto:
--   El Sprint 15 introdujo en main `kernel/finops.py` y `kernel/finops_routes.py`
--   asumiendo la existencia de la tabla `public.run_costs`, pero la migración
--   SQL nunca fue creada. Tests (`tests/test_sprint38_manus_bridge_finops_moc.py`)
--   asseran su uso. Verificación 2026-05-11: la tabla NO existe en producción.
--   Reporte: bridge/ejecutor1_to_cowork_INVESTIGACION_RUN_COSTS_2026_05_11.md
--
-- Objetivo:
--   Persistir el costo individual de cada run del kernel para alimentar:
--     1. FinOpsController (kernel/finops.py): budget hard stop diario/mensual.
--     2. Dashboard FinOps (kernel/finops_routes.py): costos hoy/semana/mes,
--        agregación por modelo, historial de runs.
--     3. Detección de cost spikes (telemetría LLM).
--
-- Diseño:
--   - Append-only por convención (no triggers; el modelo de uso es INSERT-only).
--   - RLS habilitado con policy `service_role_only` (DSC-S-006 v1.1).
--   - Índices optimizados para queries del dashboard (created_at DESC, model_used).
--
-- Compatibilidad con código existente:
--   - kernel/finops.py:64 → SELECT total_cost_usd ... LIMIT 500 (filtrado client-side por created_at).
--   - kernel/finops.py:172 → INSERT con 8 campos: run_id, model_used, tokens_in,
--     tokens_out, total_cost_usd, latency_ms, tool_count, status.
--   - kernel/finops_routes.py:63 → SELECT run_id, model_used, total_cost_usd,
--     tokens_in, tokens_out, latency_ms, tool_count, status, created_at.
--
-- Idempotencia: CREATE TABLE/INDEX IF NOT EXISTS + DROP POLICY IF EXISTS antes de
-- CREATE POLICY (PostgreSQL < 15 no soporta CREATE POLICY IF NOT EXISTS).
-- ============================================================================

BEGIN;

-- 1. Crear tabla run_costs
CREATE TABLE IF NOT EXISTS public.run_costs (
    -- Identidad
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id TEXT NOT NULL,                        -- correlación con orquestador

    -- Modelo y consumo
    model_used TEXT NOT NULL,                    -- ej. "claude-sonnet-4-7", "gpt-5"
    tokens_in INTEGER NOT NULL DEFAULT 0,
    tokens_out INTEGER NOT NULL DEFAULT 0,
    total_cost_usd NUMERIC(12, 6) NOT NULL DEFAULT 0,

    -- Telemetría operacional
    latency_ms INTEGER,                          -- NULL si run no completó
    tool_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,                        -- "completed", "failed", "timeout", "budget_exceeded"

    -- Tiempo
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints defensivos
    CONSTRAINT run_costs_status_chk CHECK (
        status IN ('completed', 'failed', 'timeout', 'budget_exceeded', 'cancelled')
    ),
    CONSTRAINT run_costs_tokens_nonnegative CHECK (tokens_in >= 0 AND tokens_out >= 0),
    CONSTRAINT run_costs_cost_nonnegative CHECK (total_cost_usd >= 0)
);

-- 2. Índices para queries del dashboard
-- Búsqueda por timestamp (más común): "qué pasó hoy / esta semana"
CREATE INDEX IF NOT EXISTS idx_run_costs_created_at
    ON public.run_costs (created_at DESC);

-- Búsqueda por run_id: correlación inversa
CREATE INDEX IF NOT EXISTS idx_run_costs_run_id
    ON public.run_costs (run_id);

-- Agregación por modelo + ventana temporal
CREATE INDEX IF NOT EXISTS idx_run_costs_model_time
    ON public.run_costs (model_used, created_at DESC);

-- 3. RLS habilitado con policy service_role_only (DSC-S-006 v1.1)
ALTER TABLE public.run_costs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_only" ON public.run_costs;
CREATE POLICY "service_role_only"
    ON public.run_costs
    AS PERMISSIVE
    FOR ALL
    TO public
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- 4. Comments para autodocumentación (Obj #5 Magna/Premium)
COMMENT ON TABLE public.run_costs IS
    'Costo y telemetría por run del kernel. Sprint 15 (FinOps Soberano), migración retroactiva 2026-05-11.';
COMMENT ON COLUMN public.run_costs.run_id IS
    'ID del run asignado por el orquestador. No único (mismo run puede tener múltiples sub-cargos en el futuro).';
COMMENT ON COLUMN public.run_costs.model_used IS
    'Identificador del modelo LLM usado (ej. claude-sonnet-4-7, gpt-5, gemini-2-5-pro).';
COMMENT ON COLUMN public.run_costs.total_cost_usd IS
    'Costo total del run en USD (suma de input + output + tool calls).';
COMMENT ON COLUMN public.run_costs.status IS
    'Estado terminal del run: completed, failed, timeout, budget_exceeded, cancelled.';

COMMIT;

-- ============================================================================
-- Verificación post-aplicación esperada:
--
--   SELECT count(*) FROM information_schema.tables
--    WHERE table_schema='public' AND table_name='run_costs';
--   → 1
--
--   SELECT relrowsecurity FROM pg_class WHERE relname='run_costs';
--   → true
--
--   SELECT count(*) FROM pg_policies
--    WHERE schemaname='public' AND tablename='run_costs';
--   → 1 (service_role_only)
--
--   SELECT count(*) FROM pg_indexes
--    WHERE schemaname='public' AND tablename='run_costs';
--   → 4 (PK + 3 índices)
--
--   SELECT count(*) FROM information_schema.columns
--    WHERE table_schema='public' AND table_name='run_costs';
--   → 10 (id, run_id, model_used, tokens_in, tokens_out, total_cost_usd,
--          latency_ms, tool_count, status, created_at)
--
-- Aplicación post-merge:
--   python3 ~/.monstruo/sb_sql.py sql -f migrations/sql/0015_run_costs.sql
-- ============================================================================
