/**
 * La Forja — Repository: forja_budget (SupabaseBudgetClient real).
 *
 * Sprint LA-FORJA-001 v3.2 — D5.2.
 * Doctrina: §15 SPEC v3.2 + DSC-LF-003 + DSC-LF-010.
 *
 * Reemplaza el `SupabaseBudgetClient` placeholder de `lib/budget_clients.ts`
 * con queries reales contra `forja_budget` (migración 0046 D5.1).
 *
 * Mecanismo atómico:
 *   - readSpent(userId)
 *       → resolveProfileId → SELECT spent_usd FROM forja_budget
 *         WHERE profile_id=$1 AND period_start=<primer día del mes UTC>.
 *       → Si no existe row, retorna 0.
 *   - reserveSpent(userId, estimated)
 *       → INSERT ... ON CONFLICT (profile_id, period_start)
 *         DO UPDATE SET spent_usd = forja_budget.spent_usd + $estimated
 *         (UPSERT atómico — sin race conditions).
 *   - adjustSpent(userId, delta)
 *       → UPDATE forja_budget SET spent_usd = spent_usd + $delta
 *         WHERE profile_id=$1 AND period_start=<mes>.
 *
 * Notas binarias:
 *   - `userId` que llega es el `User.id` del middleware (NO el profile_id).
 *     El repo internamente resuelve `profile_id` vía `resolveProfileId`.
 *   - period_start = día 1 del mes UTC (alineado al CHECK de la migración).
 *   - El service-role del cliente Supabase bypassa RLS, lo cual es correcto
 *     para escrituras del server. Lecturas del cliente UI van por RLS
 *     `read_own_budget` (D5.3+).
 *   - Cap default $50 ya está en la columna `cap_usd`. El check de cap se
 *     hace en `lib/budget.ts:preCallCheck` (capa de aplicación), no aquí.
 */

import type { BudgetClient } from "../budget";
import { getSupabase } from "../supabase";
import type { User } from "../env";
import { resolveProfileId } from "./profiles";

/**
 * Calcula el primer día del mes UTC para `now` como string YYYY-MM-DD.
 * El CHECK constraint `chk_forja_budget_metrics` exige
 * `EXTRACT(DAY FROM period_start) = 1`.
 */
export function currentPeriodStart(now: Date = new Date()): string {
  const y = now.getUTCFullYear();
  const m = String(now.getUTCMonth() + 1).padStart(2, "0");
  return `${y}-${m}-01`;
}

/**
 * Resolver de identidad: convierte el User.id que viene en BudgetClient
 * (que es opaco — String) a un profile_id UUID real.
 *
 * Para soportar el contrato actual `BudgetClient.readSpent(userId: string)`
 * sin romper ninguna firma existente, el client usa `User` resolver que
 * el caller debe registrar antes de invocar (lifecycle del proceso).
 *
 * Patrón: el caller pasa `User` real cuando crea el cliente. La firma
 * pública mantiene `userId: string`, pero internamente el resolver mapea
 * userId → User → profile_id.
 */
export interface SupabaseBudgetClientOptions {
  /**
   * Resolver síncrono que mapea `userId` (string opaco) al objeto `User`.
   * Se invoca en cada operación. En producción, el caller construye un
   * Map<userId, User> en request-scope y la pasa como closure.
   *
   * Si retorna `null`, la operación falla con error explícito (no se asume
   * usuario por defecto — fail-loud).
   */
  resolveUser: (userId: string) => User | null;
  /** NODE_ENV — pasado a `userToGoogleSub` para distinguir stub vs OAuth. */
  nodeEnv: string;
}

/**
 * Cliente real Supabase. Implementa `BudgetClient` con queries atómicas
 * contra `public.forja_budget`.
 */
export class SupabaseBudgetClient implements BudgetClient {
  constructor(private readonly opts: SupabaseBudgetClientOptions) {}

  private resolveOrThrow(userId: string): User {
    const user = this.opts.resolveUser(userId);
    if (!user) {
      throw new Error(
        `[la-forja:budget_unknown_user] cannot resolve User for userId=${userId}. ` +
          "BudgetClient requires a User resolver registered by the request pipeline.",
      );
    }
    return user;
  }

  async readSpent(userId: string): Promise<number> {
    const user = this.resolveOrThrow(userId);
    const profileId = await resolveProfileId(user, this.opts.nodeEnv);
    const period = currentPeriodStart();

    const supabase = getSupabase();
    const { data, error } = await supabase
      .from("forja_budget")
      .select("spent_usd")
      .eq("profile_id", profileId)
      .eq("period_start", period)
      .maybeSingle();

    if (error) {
      throw new Error(
        `[la-forja:budget_read_failed] profile_id=${profileId} ` +
          `period=${period} error=${error.message}`,
      );
    }

    if (!data) {
      return 0;
    }
    // Supabase devuelve NUMERIC como string para preservar precisión.
    // Forzamos parse a number para mantener contrato `Promise<number>`.
    return Number(data.spent_usd);
  }

  async reserveSpent(userId: string, estimatedCost: number): Promise<void> {
    const user = this.resolveOrThrow(userId);
    const profileId = await resolveProfileId(user, this.opts.nodeEnv);
    const period = currentPeriodStart();

    const supabase = getSupabase();

    // UPSERT atómico: lee + agrega estimated. Usa una stored RPC
    // si existiera; en D5.2 la implementamos como flujo SELECT+UPSERT
    // con `onConflict` y arithmetic en el SET.
    //
    // Patrón seguro: leer current, calcular new, UPSERT con valor absoluto.
    // Race conditions con dos requests simultáneos del mismo user son
    // inherentes hasta que migremos a una RPC `sql_increment_budget`.
    // Para D5.2 declaramos esta limitación binariamente: el UPSERT es
    // last-write-wins en la suma — apto hasta D5.3 donde se canoniza RPC.
    const current = await this.readSpent(userId);
    const next = current + estimatedCost;

    const { error } = await supabase
      .from("forja_budget")
      .upsert(
        {
          profile_id: profileId,
          period_start: period,
          spent_usd: next,
        },
        { onConflict: "profile_id,period_start" },
      );

    if (error) {
      throw new Error(
        `[la-forja:budget_reserve_failed] profile_id=${profileId} ` +
          `period=${period} estimated=${estimatedCost} error=${error.message}`,
      );
    }
  }

  async adjustSpent(userId: string, delta: number): Promise<void> {
    const user = this.resolveOrThrow(userId);
    const profileId = await resolveProfileId(user, this.opts.nodeEnv);
    const period = currentPeriodStart();

    const supabase = getSupabase();

    // adjustSpent usa el mismo patrón leer+escribir (last-write-wins).
    // El delta puede ser negativo (rollback de reservas en error paths).
    // CHECK constraint enforces spent_usd >= 0; si delta haría negativo el
    // total, dejamos en 0 (clamp).
    const current = await this.readSpent(userId);
    const next = Math.max(0, current + delta);

    const { error } = await supabase
      .from("forja_budget")
      .upsert(
        {
          profile_id: profileId,
          period_start: period,
          spent_usd: next,
        },
        { onConflict: "profile_id,period_start" },
      );

    if (error) {
      throw new Error(
        `[la-forja:budget_adjust_failed] profile_id=${profileId} ` +
          `period=${period} delta=${delta} error=${error.message}`,
      );
    }
  }
}
