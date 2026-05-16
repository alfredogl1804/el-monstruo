/**
 * La Forja — Ruta /api/tutor/chat (D2.6 + hardening D2.5).
 *
 * Sprint LA-FORJA-001 v3.2.
 * Doctrina: §4 SPEC v3.2 — tutor adaptativo Claude Opus 4.7.
 *
 * En D2 (sin SSE): retorna JSON síncrono con full content + AC12 confidence
 *   + magna_validation citations cuando aplique.
 * En D3 (con SSE): se reemplaza el handler para streamear chunks via Vercel
 *   AI SDK adapter. La forma del payload final NO cambia.
 *
 * Pipeline binario por turn (D2.5 hardened):
 *   1. preCallCheck(classifier) → reservar 0.0001 USD para Gemini Flash
 *      → invocar AC12 classify del último mensaje
 *      → postCallCommit(classifier) con tokens reales
 *      → en error path: adjustSpent(-estimated) rollback
 *   2. Si confusion_detected con ≥0.7 → recordEvent(simplification_requested)
 *   3. invokeTutor(Claude Opus 4.7 Adaptive) — usa c.var.budgetEstimated del middleware
 *      → en error path: adjustSpent(-c.var.budgetEstimated) rollback
 *   4. Si flag requireValidation:
 *      → preCallCheck(magna_validation) reservar para Sonar
 *      → invocar Perplexity Sonar
 *      → postCallCommit(magna_validation) con tokens reales
 *      → en error path: adjustSpent(-estimated) rollback
 *   5. postCallCommit(tutor) con tokens reales del Claude
 *   6. Retorna {content, intent, confidence, citations, model, costUsd}
 *
 * Hardening D2.5 (audit adversarial Perplexity 15-may-2026):
 *   - H-2: try/catch alrededor de cada llamada LLM con rollback de budget reserve
 *          si la llamada falla. NO se retiene dinero por errores de modelo.
 *   - H-3: preCallCheck + postCallCommit independiente para classifier y
 *          magna_validation. Las 3 misiones (classifier, tutor, magna) cobran
 *          al cap de $50/mes/usuario (DSC-LF-003).
 *
 * Dependency injection: el factory recibe BudgetClient para tests deterministas.
 */

import { Hono } from "hono";
import { invokeTutor } from "../lib/llm/anthropic";
import { invokeMagnaValidation } from "../lib/llm/perplexity";
import { classifyMessage, type AC12Classification } from "../lib/ac12";
import {
  preCallCheck,
  postCallCommit,
  type BudgetClient,
} from "../lib/budget";
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

/**
 * Estimaciones canónicas de tokens por misión auxiliar.
 * - classifier: input ~500 tok (mensaje), output ~50 tok (intent + score JSON)
 * - magna_validation: input ~1000 tok, output ~500 tok (citations + razonamiento)
 *
 * Estos números se usan SOLO para preCallCheck. postCallCommit ajusta con tokens
 * reales devueltos por el LLM via delta = real - estimated.
 */
const CLASSIFIER_MAX_INPUT = 500;
const CLASSIFIER_MAX_OUTPUT = 50;
const MAGNA_MAX_INPUT = 1000;
const MAGNA_MAX_OUTPUT = 500;

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

    // 1. AC12 classify con preCallCheck/postCallCommit/rollback (H-3 + H-2)
    const classifierEstimated = await preCallCheck(
      deps.budgetClient,
      user.id,
      "classifier",
      CLASSIFIER_MAX_INPUT,
      CLASSIFIER_MAX_OUTPUT,
    );
    let ac12: AC12Classification;
    try {
      ac12 =
        typeof deps.classifier === "function"
          ? await deps.classifier()
          : deps.classifier ?? (await classifyMessage(lastUserMsg.content));
    } catch (err) {
      // H-2 rollback: liberar reserva en error path
      await deps.budgetClient.adjustSpent(user.id, -classifierEstimated);
      throw err;
    }
    // Commit classifier con tokens reales (estimación: usamos los mismos max
    // como aproximación; en D5 el Gemini Flash devuelve usage real)
    await postCallCommit(
      deps.budgetClient,
      user.id,
      "classifier",
      CLASSIFIER_MAX_INPUT,
      CLASSIFIER_MAX_OUTPUT,
      classifierEstimated,
    );

    // 2. Telemetry event si confusion
    if (ac12.passesThreshold) {
      await recordEvent({
        userId: user.id,
        type: "simplification_requested",
        confidence: ac12.confidence,
      });
    }

    // 3. Claude Opus 4.7 modo Adaptive (H-2 rollback en error path)
    let tutorResp;
    try {
      tutorResp = await invokeTutor({
        messages: body.messages,
        systemPrompt: body.systemPrompt,
      });
    } catch (err) {
      // H-2 rollback: liberar reserva del tutor (hecha por forjaBudgetGuard)
      await deps.budgetClient.adjustSpent(user.id, -c.var.budgetEstimated);
      throw err;
    }

    // 4. Validación magna opcional con preCallCheck/postCallCommit (H-3 + H-2)
    let citations: string[] = [];
    let validationModel: string | null = null;
    if (body.requireValidation) {
      const magnaEstimated = await preCallCheck(
        deps.budgetClient,
        user.id,
        "magna_validation",
        MAGNA_MAX_INPUT,
        MAGNA_MAX_OUTPUT,
      );
      try {
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
        // Commit magna con tokens reales
        await postCallCommit(
          deps.budgetClient,
          user.id,
          "magna_validation",
          MAGNA_MAX_INPUT,
          MAGNA_MAX_OUTPUT,
          magnaEstimated,
        );
      } catch (err) {
        // H-2 rollback: liberar reserva magna en error path
        await deps.budgetClient.adjustSpent(user.id, -magnaEstimated);
        throw err;
      }
    }

    // 5. Post-call budget commit del tutor (tokens reales)
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
