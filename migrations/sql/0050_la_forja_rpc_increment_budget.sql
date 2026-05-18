-- =============================================================================
-- Migración 0050 — Sprint LA-FORJA-001 v3.2 D5.3
-- RPC atómico rpc_increment_budget para forja_budget (cierre L_B1 declarada D5.2)
-- =============================================================================
--
-- Contexto:
--   Issue #149 (LA-FORJA-D5.3-BUDGET-DOC-HEADER-FIX) discoverer Cowork T2-A
--   audit content PR #147 (D5.2 mergeado dc79cb71). budget.ts líneas 130-138
--   declara binariamente la limitación L_B1: "el UPSERT es last-write-wins en
--   la suma — apto hasta D5.3 donde se canoniza RPC".
--
--   Esta migration entrega esa RPC. Path B recomendado por Cowork (alternativa
--   superior al Path A doc-only) bajo razonamiento "mientras se toca budget.ts
--   ya, hacer el fix real en vez de solo doc".
--
-- Causa raíz binaria:
--   `reserveSpent()` y `adjustSpent()` usan flujo SELECT-then-UPSERT (read in
--   TS, compute en TS, write absolute en TS). Entre el SELECT y el UPSERT pueden
--   entrar requests concurrentes del MISMO user causando race conditions: el
--   último UPSERT escribe valor absoluto basado en su SELECT obsoleto, perdiendo
--   los incrementos intermedios.
--
-- Solución (Path B — Cowork recommended):
--   Función plpgsql atómica `rpc_increment_budget(profile_id, period_start, delta)`
--   que hace INSERT...ON CONFLICT DO UPDATE SET spent_usd = forja_budget.spent_usd
--   + p_delta en una sola transacción Postgres. Postgres garantiza atomicidad
--   por row (UNIQUE constraint forja_budget_profile_id_period_start_key actúa
--   como lock implícito durante el UPSERT).
--
-- Cumplimiento DSC:
--   - DSC-S-006 (RLS por defecto): tabla ya tiene RLS habilitado (migration 0046).
--     La RPC corre con SECURITY DEFINER → bypass RLS controlado vía GRANT EXECUTE
--     explícito a service_role. NO grant a anon/authenticated (escritura denegada
--     desde clientes UI).
--   - DSC-G-008 v2: archivo entregado a Cowork para audit content antes del merge.
--   - DSC-LF-010 (atomicidad data plane): cumplido binariamente — Postgres
--     garantiza atomicidad de UPSERT por row.
--   - Idempotencia: CREATE OR REPLACE FUNCTION es idempotente. Re-aplicar la
--     migration no daña función existente (la sustituye con misma definición).
--
-- Atomicidad:
--   Transacción BEGIN/COMMIT. Rollback inmediato si falla.
--
-- Numeración:
--   0050 verificado disponible (último aplicado: 0049_embrion_memoria_consumed_at
--   _backfill por Cowork T2-A 2026-05-18 vía MCP, mergeado PR #151).
--
-- Aplicar con:
--   MCP supabase-monstruo apply_migration tool (Cowork autoridad T1 delegada).
--
-- Smoke test post-aplicación obligatorio:
--   1. Verificar función existe y es callable:
--      SELECT proname, prosecdef, proconfig FROM pg_proc WHERE proname = 'rpc_increment_budget';
--      → 1 row, prosecdef=true (SECURITY DEFINER)
--
--   2. Verificar grants:
--      SELECT grantee, privilege_type FROM information_schema.routine_privileges
--        WHERE routine_name = 'rpc_increment_budget';
--      → service_role: EXECUTE
--      → anon, authenticated: NO rows
--
--   3. Smoke test funcional (en transacción con ROLLBACK):
--      BEGIN;
--        -- setup: insert profile + budget row
--        SELECT rpc_increment_budget('<profile_id>', '2026-05-01'::DATE, 1.50);
--        -- verifica spent_usd subió 1.50
--        SELECT rpc_increment_budget('<profile_id>', '2026-05-01'::DATE, -0.50);
--        -- verifica spent_usd subió a 1.00
--        SELECT rpc_increment_budget('<profile_id>', '2026-05-01'::DATE, -100);
--        -- verifica spent_usd clamp a 0 (GREATEST)
--      ROLLBACK;
-- =============================================================================
BEGIN;

-- T-D5.3.1 — Función atómica rpc_increment_budget
CREATE OR REPLACE FUNCTION public.rpc_increment_budget(
  p_profile_id UUID,
  p_period_start DATE,
  p_delta NUMERIC
) RETURNS NUMERIC
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
  v_new_spent NUMERIC;
BEGIN
  -- Validación binaria: period_start debe ser día 1 del mes (matchea CHECK
  -- constraint chk_forja_budget_metrics de migration 0046).
  IF EXTRACT(DAY FROM p_period_start) <> 1 THEN
    RAISE EXCEPTION 'rpc_increment_budget: period_start must be day 1 of month, got %', p_period_start
      USING ERRCODE = 'check_violation';
  END IF;

  -- INSERT ON CONFLICT atómico. Postgres garantiza atomicidad por row gracias
  -- al UNIQUE constraint (profile_id, period_start) que actúa como lock implícito.
  -- GREATEST(0, ...) clampa a 0 cuando delta haría negativo (matchea behavior
  -- del Math.max(0, ...) en adjustSpent del TS legacy).
  INSERT INTO public.forja_budget (profile_id, period_start, spent_usd)
  VALUES (p_profile_id, p_period_start, GREATEST(0, p_delta))
  ON CONFLICT (profile_id, period_start)
  DO UPDATE SET
    spent_usd = GREATEST(0, public.forja_budget.spent_usd + p_delta),
    updated_at = NOW()
  RETURNING spent_usd INTO v_new_spent;

  RETURN v_new_spent;
END;
$$;

COMMENT ON FUNCTION public.rpc_increment_budget(UUID, DATE, NUMERIC) IS
  'La Forja D5.3: incremento atómico de forja_budget.spent_usd. '
  'Cierra L_B1 declarada en D5.2 (budget.ts líneas 130-138). '
  'Atomicidad garantizada por UNIQUE(profile_id, period_start) + UPSERT por row. '
  'GREATEST(0, ...) clampa a 0 (matchea CHECK constraint spent_usd >= 0). '
  'Validación binaria: period_start debe ser día 1 del mes UTC. '
  'Sprint LA-FORJA-001 v3.2 D5.3 (2026-05-18). Issue #149 Path B (Cowork recommended).';

-- T-D5.3.2 — Grants explícitos (RLS bypass controlado)
-- Solo service_role puede ejecutar. anon y authenticated denegados (escritura
-- de budget desde UI no permitida — sigue patrón D5.2).
REVOKE ALL ON FUNCTION public.rpc_increment_budget(UUID, DATE, NUMERIC) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.rpc_increment_budget(UUID, DATE, NUMERIC) FROM anon;
REVOKE ALL ON FUNCTION public.rpc_increment_budget(UUID, DATE, NUMERIC) FROM authenticated;
GRANT EXECUTE ON FUNCTION public.rpc_increment_budget(UUID, DATE, NUMERIC) TO service_role;

COMMIT;

-- =============================================================================
-- Notas post-aplicación:
-- =============================================================================
--
-- 1. Reemplazo en budget.ts (PR mismo D5.3):
--    Las funciones reserveSpent() y adjustSpent() del SupabaseBudgetClient
--    deben migrar de SELECT-then-UPSERT a un solo `supabase.rpc(...)`. Single
--    round-trip, atomicidad real garantizada por Postgres.
--
-- 2. Backward compatibility:
--    La columna spent_usd, schema y constraints de forja_budget no cambian.
--    Rows existentes funcionan con la nueva RPC sin migración de datos.
--
-- 3. Schema cache reload:
--    PostgREST/Supabase recarga schema cache automáticamente al detectar nueva
--    función. No requiere reload manual.
--
-- 4. Reversibilidad:
--    DROP FUNCTION public.rpc_increment_budget(UUID, DATE, NUMERIC);
--    El TS revertido al patrón SELECT-then-UPSERT funciona sin esta función.
-- =============================================================================
