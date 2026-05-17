/**
 * La Forja — Middleware de presupuesto LF-RATE-LIMIT-001 + DSC-LF-003.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.5.
 * Doctrina: §15 SPEC v3.2.
 *
 * Aplica preCallCheck() del motor budget ANTES de procesar la ruta.
 *   - Si pasa: setea c.var.budgetEstimated con el costo reservado.
 *     La ruta DEBE llamar postCallCommit() después del LLM call.
 *   - Si falla: 429 Too Many Requests con detalle del cap excedido.
 *
 * Decisión binaria de modelo: las rutas saben qué modelo usan, por eso
 * el middleware necesita un `missionFor(c)` que extrae la misión del contexto
 * (path, query o body parsed previamente).
 *
 * Tokens estimados: las rutas pueden override `maxIn`/`maxOut` con los
 * specs reales del request (chat largos = más tokens). Default conservador
 * 4000 in / 2000 out (sufficient for most calls).
 */

import type { Context, MiddlewareHandler, Next } from "hono";
import {
  type BudgetClient,
  FORJA_BUDGET_CAP_USD,
  ForjaBudgetExceededError,
  preCallCheck,
} from "../lib/budget";
import type { Mission } from "../lib/llm/router";
import type { User } from "../lib/env";

export interface ForjaBudgetContext {
  Variables: {
    user: User;
    budgetEstimated: number;
    budgetMission: Mission;
  };
}

export interface ForjaBudgetMiddlewareOptions {
  /** Cliente Supabase-backed (D5) o mock (D2 tests) */
  client: BudgetClient;
  /** Función que decide la misión del request (default: lee body.mission) */
  missionFor: (c: Context) => Mission;
  /** Override defaults conservadores (4000/2000) */
  maxInputTokens?: number;
  maxOutputTokens?: number;
}

const DEFAULT_MAX_INPUT = 4000;
const DEFAULT_MAX_OUTPUT = 2000;

export function forjaBudgetGuard(
  opts: ForjaBudgetMiddlewareOptions,
): MiddlewareHandler<ForjaBudgetContext> {
  return async (c: Context, next: Next) => {
    const user = c.get("user") as User | undefined;
    if (!user) {
      return c.json(
        {
          ok: false,
          error:
            "[la-forja:budget_user_missing] forjaAuthStub() must run before forjaBudgetGuard()",
        },
        500,
      );
    }
    const mission = opts.missionFor(c);
    const maxIn = opts.maxInputTokens ?? DEFAULT_MAX_INPUT;
    const maxOut = opts.maxOutputTokens ?? DEFAULT_MAX_OUTPUT;

    try {
      const estimated = await preCallCheck(
        opts.client,
        user.id,
        mission,
        maxIn,
        maxOut,
      );
      c.set("budgetEstimated", estimated);
      c.set("budgetMission", mission);
      await next();
      return;
    } catch (err) {
      if (err instanceof ForjaBudgetExceededError) {
        return c.json(
          {
            ok: false,
            error: err.message,
            currentSpent: err.currentSpent,
            estimatedCost: err.estimatedCost,
            // F-D3.2-09: usar la constante canónica DSC-LF-003, no literal.
            cap: FORJA_BUDGET_CAP_USD,
          },
          429,
        );
      }
      throw err;
    }
  };
}
