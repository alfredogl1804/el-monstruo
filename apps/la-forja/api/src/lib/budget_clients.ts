/**
 * La Forja — Implementaciones concretas de BudgetClient.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.7.
 *
 * En D2-D4 (sin tabla forja_budget): InMemoryBudgetClient acumula spent
 *   por usuario en un Map. Pierde estado al restart del server. Apto para
 *   smoke test, no para producción.
 *
 * En D5 (con tabla forja_budget): SupabaseBudgetClient hace SELECT/UPDATE
 *   atómico contra Supabase. El interface BudgetClient NO cambia.
 */

import type { BudgetClient } from "./budget";

/**
 * Implementación in-memory para D2-D4. Solo apta para arranque de boot.
 * En D5 SupabaseBudgetClient lo reemplaza.
 */
export class InMemoryBudgetClient implements BudgetClient {
  private readonly spents = new Map<string, number>();

  async readSpent(userId: string): Promise<number> {
    return this.spents.get(userId) ?? 0;
  }

  async reserveSpent(userId: string, estimatedCost: number): Promise<void> {
    const current = this.spents.get(userId) ?? 0;
    this.spents.set(userId, current + estimatedCost);
  }

  async adjustSpent(userId: string, delta: number): Promise<void> {
    const current = this.spents.get(userId) ?? 0;
    this.spents.set(userId, current + delta);
  }

  /** Solo para tests/debug */
  _peek(userId: string): number {
    return this.spents.get(userId) ?? 0;
  }
}

/**
 * D5 placeholder. Lanza error explícito si se invoca antes de migración.
 *
 * En D5 esta clase se implementa con queries Supabase atómicas:
 *   readSpent  → SELECT spent_usd_month FROM forja_budget WHERE user_id=$1
 *   reserve    → INSERT ... ON CONFLICT UPDATE spent_usd_month = spent_usd_month + $2
 *   adjust     → UPDATE forja_budget SET spent_usd_month = spent_usd_month + $2
 */
export class SupabaseBudgetClient implements BudgetClient {
  async readSpent(_userId: string): Promise<number> {
    throw new Error(
      "[la-forja:budget_supabase_not_implemented] forja_budget table does not exist until D5. " +
        "Use InMemoryBudgetClient until migrations are applied.",
    );
  }
  async reserveSpent(_userId: string, _estimatedCost: number): Promise<void> {
    throw new Error(
      "[la-forja:budget_supabase_not_implemented] forja_budget table does not exist until D5.",
    );
  }
  async adjustSpent(_userId: string, _delta: number): Promise<void> {
    throw new Error(
      "[la-forja:budget_supabase_not_implemented] forja_budget table does not exist until D5.",
    );
  }
}

/** Default budget client para D2-D4 boot. D5 cambia a SupabaseBudgetClient. */
export function defaultBudgetClient(): BudgetClient {
  return new InMemoryBudgetClient();
}
