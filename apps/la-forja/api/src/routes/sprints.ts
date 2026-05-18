/**
 * La Forja — Ruta /api/sprints (D2.6 + hardening D2.5 + reconciliación D5.2).
 *
 * Sprint LA-FORJA-001 v3.2.
 * Doctrina: §4 SPEC v3.2 — co-piloto sprints GPT-5.5 Pro Reasoning.
 *
 * Genera propuestas de sprint a partir de un objetivo libre del usuario.
 * En D2: response síncrona con propuesta generada + estado canónico.
 * En D5: persiste en forja_sprints con state machine 8 estados.
 *
 * State machine canónica (D5.1 SQL `chk_forja_sprints_status` — fuente de verdad):
 *   proposed → confirmed → executing → waiting_audit → audited → merged
 *   Estados terminales: blocked | archived
 *
 * Hardening D2.5 (audit adversarial Perplexity 15-may-2026):
 *   - H-4: SPRINT_STATES alineado a la doctrina viva. La iteración previa
 *          alineaba al SPEC v3.2 §4:130 (inglés), pero D5.1 SQL canonizó
 *          un set distinto de 8 estados al implementar `forja_sprints`.
 *          La fuente única de verdad es el SQL en producción (DSC-LF-010).
 *   - H-2: try/catch alrededor de invokeSprintCopilot con rollback de
 *          c.var.budgetEstimated si el LLM falla. NO se retiene presupuesto
 *          por errores del modelo.
 *
 * Drift P2 reconciliado en D5.2 (caveat declarado en SIGNOFF Cowork D5.1):
 *   - SQL gana sobre TS. Estados TS previos `drafting, review_alfredo,
 *     review_cowork, ready_to_execute, canonized` reemplazados por
 *     `confirmed, waiting_audit, audited, blocked, archived` (canónicos SQL).
 *   - 3 estados se mantuvieron por nombre exacto: `proposed, executing, merged`.
 *   - `chk_forja_sprints_status` constraint en Postgres rechaza cualquier
 *     INSERT con estado fuera del whitelist; la TS ahora coincide binariamente.
 */

import { Hono } from "hono";
import { invokeSprintCopilot } from "../lib/llm/openai.js";
import { postCallCommit, type BudgetClient } from "../lib/budget.js";
import { recordEvent } from "../lib/telemetry.js";
import type { ForjaAuthContext } from "../middleware/auth.js";
import type { ForjaBudgetContext } from "../middleware/budget.js";

/**
 * Estados canónicos alineados al SQL D5.1 (`chk_forja_sprints_status`).
 * Tuple length=8 EXACTO. Cualquier 9° estado = expansión de schema requerida.
 *
 * Transiciones permitidas (D5.1 SQL + DSC-LF-010):
 *   proposed         → confirmed       (T1-Alfredo confirma propuesta)
 *   confirmed        → executing       (Manus arranca sprint)
 *   executing        → waiting_audit   (Manus pide audit a Cowork)
 *   waiting_audit    → audited         (Cowork firma VERDE)
 *   audited          → merged          (PR mergeado a main)
 *   *                → blocked         (cualquier estado puede bloquearse)
 *   *                → archived        (cualquier estado terminal puede archivarse)
 */
export const SPRINT_STATES = [
  "proposed",
  "confirmed",
  "executing",
  "waiting_audit",
  "audited",
  "merged",
  "blocked",
  "archived",
] as const satisfies readonly string[];

export type SprintState = (typeof SPRINT_STATES)[number];

/**
 * Estado inicial canónico cuando se crea un sprint nuevo.
 * Cualquier sprint nace en `proposed` antes de pasar a `confirmed` (D5.1 SQL).
 */
export const SPRINT_INITIAL_STATE: SprintState = "proposed";

export interface SprintCreateRequest {
  objective: string;
  context?: string;
}

export interface SprintsRoutesDeps {
  budgetClient: BudgetClient;
}

export type SprintsContext = ForjaAuthContext & ForjaBudgetContext;

export function sprintsRoutes(deps: SprintsRoutesDeps) {
  const app = new Hono<SprintsContext>();

  app.post("/", async (c) => {
    const body = await c.req.json<SprintCreateRequest>();
    if (!body.objective || body.objective.trim().length === 0) {
      return c.json(
        {
          ok: false,
          error: "[la-forja:sprints_missing_objective] objective required",
        },
        400,
      );
    }

    const user = c.var.user;
    const systemPrompt = `Eres co-piloto de sprints en La Forja. Genera una propuesta de sprint con:
1. Título corto (5-10 palabras)
2. Objetivo SMART
3. 3-5 entregables binariamente verificables
4. Criterios de aceptación binarios (cada uno demostrable con un comando o resultado)
5. ETA realista en días
Responde en JSON con campos: title, objective, deliverables[], acceptance_criteria[], eta_days.`;

    // H-2 hardening: try/catch con rollback en error path
    let resp;
    try {
      resp = await invokeSprintCopilot({
        input: [
          { role: "system", content: systemPrompt },
          {
            role: "user",
            content: `Objetivo: ${body.objective}\n${body.context ? `Contexto: ${body.context}` : ""}`,
          },
        ],
      });
    } catch (err) {
      // Liberar reserva del budget si LLM falla
      await deps.budgetClient.adjustSpent(user.id, -c.var.budgetEstimated);
      throw err;
    }

    const commit = await postCallCommit(
      deps.budgetClient,
      user.id,
      "sprint_copilot",
      resp.inputTokens,
      resp.outputTokens,
      c.var.budgetEstimated,
    );

    await recordEvent({
      userId: user.id,
      type: "sprint_started",
      model: resp.model,
      costUsd: commit.realCost,
    });

    return c.json({
      ok: true,
      proposal: resp.content,
      state: SPRINT_INITIAL_STATE,
      model: resp.model,
      costUsd: commit.realCost,
    });
  });

  app.get("/states", (c) => {
    return c.json({ ok: true, states: SPRINT_STATES });
  });

  return app;
}
