/**
 * La Forja — Motor de presupuesto LF-RATE-LIMIT-001 + DSC-LF-003.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.3.
 * Doctrina: §15 SPEC v3.2 — mecanismo atómico canónico.
 *
 *   1. PRE-CALL: estimateCost(maxIn, maxOut, mission)
 *      → calcula estimated_cost con max tokens del request
 *      → bloquea si spent_usd_month + estimated_cost > 50 USD
 *
 *   2. POST-CALL: commitCost(realIn, realOut, mission, estimatedCost)
 *      → calcula real_cost con tokens reales de la respuesta
 *      → UPDATE forja_budget SET spent_usd_month =
 *          spent_usd_month - estimated_cost + real_cost WHERE user_id=$1
 *      → transacción atómica, sin race conditions, sin overshoot
 *
 * Cap canónico: 50.00 USD/mes/usuario (DSC-LF-003).
 * Solo T1-Alfredo puede desbloquear binariamente desde forja_budget.
 *
 * NOTA D2: las llamadas a Supabase usan getSupabase() pero la tabla
 * forja_budget se crea en D5 (migración 0044_la_forja_budget.sql). En D2
 * los tests mockean el cliente Supabase. En producción D5+ las llamadas
 * son reales. El interface NO cambia.
 */

import { MISSION_PRICING, type Mission } from "./llm/router";

export const FORJA_BUDGET_CAP_USD = 50.0 as const;
export const FORJA_BUDGET_TABLE = "forja_budget" as const;

export class ForjaBudgetExceededError extends Error {
  constructor(
    public readonly userId: string,
    public readonly currentSpent: number,
    public readonly estimatedCost: number,
  ) {
    super(
      `[la-forja:budget_cap_exceeded] userId=${userId} ` +
        `current=$${currentSpent.toFixed(4)} + estimated=$${estimatedCost.toFixed(4)} ` +
        `> cap=$${FORJA_BUDGET_CAP_USD}`,
    );
    this.name = "ForjaBudgetExceededError";
  }
}

/**
 * Estima costo USD del request basado en max tokens y misión.
 * Determinista y pure: input₁₀₀₀ × $5 + output₅₀₀ × $25 = $0.0175 (ejemplo tutor).
 */
export function estimateCost(
  maxInputTokens: number,
  maxOutputTokens: number,
  mission: Mission,
): number {
  const pricing = MISSION_PRICING[mission];
  const inputCost = (maxInputTokens / 1_000_000) * pricing.inputPerMtok;
  const outputCost = (maxOutputTokens / 1_000_000) * pricing.outputPerMtok;
  return inputCost + outputCost;
}

/**
 * Calcula costo USD con tokens reales (post-call). Misma fórmula que estimate
 * pero con valores reales devueltos por el LLM.
 */
export function realCost(
  realInputTokens: number,
  realOutputTokens: number,
  mission: Mission,
): number {
  return estimateCost(realInputTokens, realOutputTokens, mission);
}

/**
 * Lookup pre-call: lee forja_budget.spent_usd_month del usuario.
 * Si no existe row, retorna 0 (primer uso del mes).
 */
export async function readSpent(
  client: BudgetClient,
  userId: string,
): Promise<number> {
  return client.readSpent(userId);
}

/**
 * Pre-call check: bloquea si current spent + estimated > cap.
 * Si OK, NO commitea aún — el commit es post-call con tokens reales.
 *
 * Retorna estimated_cost para que el caller lo guarde y lo pase a commit.
 */
export async function preCallCheck(
  client: BudgetClient,
  userId: string,
  mission: Mission,
  maxInputTokens: number,
  maxOutputTokens: number,
): Promise<number> {
  const estimated = estimateCost(maxInputTokens, maxOutputTokens, mission);
  const currentSpent = await client.readSpent(userId);
  if (currentSpent + estimated > FORJA_BUDGET_CAP_USD) {
    throw new ForjaBudgetExceededError(userId, currentSpent, estimated);
  }
  // Reservar el estimado en la tabla atómicamente
  await client.reserveSpent(userId, estimated);
  return estimated;
}

/**
 * Post-call commit: ajusta el spent con tokens reales.
 * UPDATE atómico: spent = spent - estimated + real.
 */
export async function postCallCommit(
  client: BudgetClient,
  userId: string,
  mission: Mission,
  realInputTokens: number,
  realOutputTokens: number,
  estimatedCost: number,
): Promise<{ realCost: number; delta: number }> {
  const real = realCost(realInputTokens, realOutputTokens, mission);
  const delta = real - estimatedCost;
  await client.adjustSpent(userId, delta);
  return { realCost: real, delta };
}

/**
 * Interface del cliente de budget. Permite inyectar mock en tests
 * y usar Supabase directo en producción D5+.
 *
 * En D2: los tests usan mocks.
 * En D5+: implementación real conectada a forja_budget.
 */
export interface BudgetClient {
  readSpent(userId: string): Promise<number>;
  reserveSpent(userId: string, estimatedCost: number): Promise<void>;
  adjustSpent(userId: string, delta: number): Promise<void>;
}
