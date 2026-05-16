/**
 * La Forja — Ruta /api/tutor/chat (D2.6).
 *
 * Sprint LA-FORJA-001 v3.2.
 * Doctrina: §4 SPEC v3.2 — tutor adaptativo Claude Opus 4.7.
 *
 * En D2 (sin SSE): retorna JSON síncrono con full content + AC12 confidence
 *   + magna_validation citations cuando aplique.
 * En D3 (con SSE): se reemplaza el handler para streamear chunks via Vercel
 *   AI SDK adapter. La forma del payload final NO cambia.
 *
 * Pipeline binario por turn:
 *   1. AC12 classify del último mensaje del usuario
 *   2. Si confusion_detected con ≥0.7 → recordEvent(simplification_requested)
 *   3. Invokes Claude Opus 4.7 modo Adaptive con history
 *   4. Si flag requireValidation → llama Perplexity Sonar
 *   5. postCallCommit budget con tokens reales del LLM
 *   6. Retorna {content, intent, confidence, citations, model, costUsd}
 *
 * Dependency injection: el factory recibe BudgetClient para tests deterministas.
 */

import { Hono } from "hono";
import { invokeTutor } from "../lib/llm/anthropic";
import { invokeMagnaValidation } from "../lib/llm/perplexity";
import { classifyMessage, type AC12Classification } from "../lib/ac12";
import { postCallCommit, type BudgetClient } from "../lib/budget";
import { recordEvent } from "../lib/telemetry";
import type { ForjaAuthContext } from "../middleware/auth";
import type { ForjaBudgetContext } from "../middleware/budget";

export interface TutorChatRequest {
  messages: Array<{ role: "user" | "assistant"; content: string }>;
  systemPrompt?: string;
  requireValidation?: boolean;
}

export interface TutorRoutesDeps {
  budgetClient: BudgetClient;
  /** Override classifier para tests deterministas */
  classifier?: AC12Classification | (() => Promise<AC12Classification>);
}

export type TutorChatContext = ForjaAuthContext & ForjaBudgetContext;

export function tutorRoutes(deps: TutorRoutesDeps) {
  const app = new Hono<TutorChatContext>();

  app.post("/chat", async (c) => {
    const body = await c.req.json<TutorChatRequest>();
    if (!Array.isArray(body.messages) || body.messages.length === 0) {
      return c.json(
        {
          ok: false,
          error: "[la-forja:tutor_missing_messages] messages array required",
        },
        400,
      );
    }
    const lastUserMsg = [...body.messages]
      .reverse()
      .find((m) => m.role === "user");
    if (!lastUserMsg) {
      return c.json(
        {
          ok: false,
          error: "[la-forja:tutor_no_user_message] needs ≥1 user message",
        },
        400,
      );
    }

    const user = c.var.user;

    // 1. AC12 classify (Gemini Flash, override permitido para tests)
    const ac12: AC12Classification =
      typeof deps.classifier === "function"
        ? await deps.classifier()
        : deps.classifier ?? (await classifyMessage(lastUserMsg.content));

    // 2. Telemetry event si confusion
    if (ac12.passesThreshold) {
      await recordEvent({
        userId: user.id,
        type: "simplification_requested",
        confidence: ac12.confidence,
      });
    }

    // 3. Claude Opus 4.7 modo Adaptive
    const tutorResp = await invokeTutor({
      messages: body.messages,
      systemPrompt: body.systemPrompt,
    });

    // 4. Validación magna opcional (solo si flag)
    let citations: string[] = [];
    let validationModel: string | null = null;
    if (body.requireValidation) {
      const v = await invokeMagnaValidation({
        messages: [
          {
            role: "user",
            content: `Verifica esta afirmación con fuentes recientes: ${tutorResp.content}`,
          },
        ],
      });
      citations = v.citations;
      validationModel = v.model;
      await recordEvent({
        userId: user.id,
        type: "magna_validation_used",
        model: v.model,
      });
    }

    // 5. Post-call budget commit (tokens reales del tutor)
    const commit = await postCallCommit(
      deps.budgetClient,
      user.id,
      "tutor",
      tutorResp.inputTokens,
      tutorResp.outputTokens,
      c.var.budgetEstimated,
    );

    return c.json({
      ok: true,
      content: tutorResp.content,
      model: tutorResp.model,
      intent: ac12.intent,
      confidence: ac12.confidence,
      citations,
      validationModel,
      costUsd: commit.realCost,
    });
  });

  return app;
}
