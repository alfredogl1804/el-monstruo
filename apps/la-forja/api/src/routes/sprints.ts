/**
 * La Forja — Ruta /api/sprints (D2.6).
 *
 * Sprint LA-FORJA-001 v3.2.
 * Doctrina: §4 SPEC v3.2 — co-piloto sprints GPT-5.5 Pro Reasoning.
 *
 * Genera propuestas de sprint a partir de un objetivo libre del usuario.
 * En D2: response síncrona con propuesta generada + estado canónico.
 * En D5: persiste en forja_sprints con state machine 8 estados.
 *
 * State machine (§4 SPEC):
 *   propuesta → diseño → ejecución → validacion →
 *   cerrado_sin_pulir → pulir → cerrado_pulir → archivado
 */

import { Hono } from "hono";
import { invokeSprintCopilot } from "../lib/llm/openai";
import { postCallCommit, type BudgetClient } from "../lib/budget";
import { recordEvent } from "../lib/telemetry";
import type { ForjaAuthContext } from "../middleware/auth";
import type { ForjaBudgetContext } from "../middleware/budget";

export const SPRINT_STATES = [
  "propuesta",
  "diseño",
  "ejecución",
  "validacion",
  "cerrado_sin_pulir",
  "pulir",
  "cerrado_pulir",
  "archivado",
] as const satisfies readonly string[];

export type SprintState = (typeof SPRINT_STATES)[number];

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

    const resp = await invokeSprintCopilot({
      input: [
        { role: "system", content: systemPrompt },
        {
          role: "user",
          content: `Objetivo: ${body.objective}\n${body.context ? `Contexto: ${body.context}` : ""}`,
        },
      ],
    });

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
      state: "propuesta" as SprintState,
      model: resp.model,
      costUsd: commit.realCost,
    });
  });

  app.get("/states", (c) => {
    return c.json({ ok: true, states: SPRINT_STATES });
  });

  return app;
}
