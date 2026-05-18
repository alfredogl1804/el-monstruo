/**
 * La Forja — Implementaciones concretas de BudgetClient.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.7 + D5.2.
 *
 * En D2-D4 (sin tabla forja_budget): InMemoryBudgetClient acumula spent
 *   por usuario en un Map. Pierde estado al restart del server. Apto para
 *   smoke test, no para producción.
 *
 * En D5.2+ (con tabla forja_budget aplicada): SupabaseBudgetClient (en
 *   `lib/repositories/budget.ts`) hace UPSERT atómico contra Supabase.
 *   El interface BudgetClient NO cambia.
 *
 * Selección binaria por NODE_ENV en `defaultBudgetClient()`:
 *   - production           → SupabaseBudgetClient real (lib/repositories/budget.ts)
 *   - development | test   → InMemoryBudgetClient (zero side effects en tests)
 */

import type { BudgetClient } from "./budget";
import { loadEnv } from "./env";
import { SupabaseBudgetClient as SupabaseBudgetClientReal } from "./repositories/budget";
import type { User } from "./env";

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
 * D5.2 alias re-exportado: la implementación real vive en
 * `lib/repositories/budget.ts` (queries reales contra forja_budget).
 * Re-exportado aquí para preservar compat con imports existentes que
 * referenciaban `SupabaseBudgetClient` desde `lib/budget_clients`.
 */
export { SupabaseBudgetClientReal as SupabaseBudgetClient };

/**
 * Resolver de User compartido entre BudgetClient y TelemetryClient cuando
 * corren en modo Supabase real. Lo rellena el pipeline de la app por request
 * (en `index.ts` después del middleware auth) y lo consulta el cliente.
 *
 * Patrón: process-wide Map<userId, User>. Las entradas se añaden ANTES de
 * invocar al budget/telemetry y NO se eliminan (cache para resolución de
 * profile_id en turnos posteriores). El crecimiento es O(usuarios distintos).
 */
const USER_RESOLVER_CACHE = new Map<string, User>();

export function registerUserForResolver(user: User): void {
  USER_RESOLVER_CACHE.set(user.id, user);
}

export function resolveUserById(userId: string): User | null {
  return USER_RESOLVER_CACHE.get(userId) ?? null;
}

export function _resetUserResolver(): void {
  USER_RESOLVER_CACHE.clear();
}

/**
 * Default budget client. Selección binaria por NODE_ENV:
 *   - production       → SupabaseBudgetClient real
 *   - development|test → InMemoryBudgetClient (preserva tests sin side effects)
 */
export function defaultBudgetClient(): BudgetClient {
  const env = loadEnv();
  if (env.NODE_ENV === "production") {
    return new SupabaseBudgetClientReal({
      resolveUser: resolveUserById,
      nodeEnv: env.NODE_ENV,
    });
  }
  return new InMemoryBudgetClient();
}
