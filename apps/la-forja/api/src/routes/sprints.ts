/**
 * La Forja — Ruta /api/sprints (D2.6 + hardening D2.5).
 *
 * Sprint LA-FORJA-001 v3.2.
 * Doctrina: §4 SPEC v3.2 — co-piloto sprints GPT-5.5 Pro Reasoning.
 *
 * Genera propuestas de sprint a partir de un objetivo libre del usuario.
 * En D2: response síncrona con propuesta generada + estado canónico.
 * En D5: persiste en forja_sprints con state machine 8 estados.
 *
 * State machine canónica (§4 SPEC v3.2:130 — inglés):
 *   proposed → drafting → review_alfredo → review_cowork → ready_to_execute
 *                                                                  ↓
 *                                            canonized ← merged ← executing
 *
 * Hardening D2.5 (audit adversarial Perplexity 15-may-2026):
 *   - H-4: SPRINT_STATES alineado binariamente al SPEC §4:130 (inglés).
 *          El código previo usaba estados español semánticamente distintos
 *          (propuesta, diseño, ejecución, validacion, cerrado_sin_pulir,
 *          pulir, cerrado_pulir, archivado) que no aparecen en el SPEC.
 *   - H-2: try/catch alrededor de invokeSprintCopilot con rollback de
 *          c.var.budgetEstimated si el LLM falla. NO se retiene presupuesto
 *          por errores del modelo.
 */

import { Hono } from "hono";
import { invokeSprintCopilot } from "../lib/llm/openai";
import { postCallCommit, type BudgetClient } from "../lib/budget";
import { recordEvent } from "../lib/telemetry";
import type { ForjaAuthContext } from "../middleware/auth";
import type { ForjaBudgetContext } from "../middleware/budget";

/**
 * Estados canónicos alineados al SPEC v3.2 §4:130 (inglés).
 * Tuple length=8 EXACTO. Cualquier 9° estado = SPEC nuevo.
 *
 * Transiciones permitidas (declaradas en SPEC §4:135-144):
 *   proposed         → drafting
 *   drafting         → review_alfredo  (T1-Alfredo bloqueo)
 *   review_alfredo   → review_cowork   (firma DSC requerida)
 *   review_cowork    → ready_to_execute
 *   ready_to_execute → executing
 *   executing        → merged          (sistema, webhook GitHub)
 *   merged           → canonized       (sistema + T1, archivo bridge _DONE)
 */
export const SPRINT_STATES = [
  "proposed",
  "drafting",
  "review_alfredo",
  "review_cowork",
  "ready_to_execute",
  "executing",
  "merged",
  "canonized",
] as const satisfies readonly string[];

export type SprintState = (typeof SPRINT_STATES)[number];

/**
 * Estado inicial canónico cuando se crea un sprint nuevo.
 * Cualquier sprint nace en `proposed` antes de pasar a `drafting`.
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
