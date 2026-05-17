/**
 * La Forja — Ruta /api/tutor/chat (D3.2 SSE migration — DSC-LF-005).
 *
 * Sprint LA-FORJA-001 v3.2.
 * Doctrina: §4 SPEC v3.2 — tutor adaptativo Claude Opus 4.7.
 *
 * D3.2 (DSC-LF-005): el handler retorna text/event-stream construido por
 * `result.toUIMessageStreamResponse()` de Vercel AI SDK 6. JSON solo se
 * mantiene en error paths (validación, budget exceeded) y en error responses
 * tempranos antes de iniciar el stream.
 *
 * Pipeline binario por turn (preservado palabra por palabra de D2.5/D2.6):
 *   1. Validación shape del request (400 JSON si messages vacío / no user msg)
 *   2. preCallCheck(classifier) → reservar Gemini Flash → invokeClassifier
 *      → postCallCommit(classifier) → en error path: adjustSpent(-estimated)
 *   3. Si confusion_detected con ≥0.7 → recordEvent(simplification_requested)
 *   4. Si requireValidation=true:
 *      → preCallCheck(magna_validation) reservar Sonar
 *      → invokeMagnaValidation(últ_user_msg)
 *      → postCallCommit(magna_validation)
 *      → en error path: adjustSpent(-estimated) rollback + throw → 500 JSON
 *      Las citations se EMITEN como header SSE (`x-la-forja-citations`)
 *      para que el cliente las lea pre-stream.
 *   5. buildTutorStream(Claude Opus 4.7 Adaptive)
 *      → onFinish: postCallCommit(tutor) con tokens reales
 *      → onError: adjustSpent(-c.var.budgetEstimated) rollback
 *   6. Retorna result.toUIMessageStreamResponse({...}) — text/event-stream
 *
 * Ordering rationale: magna_validation se mueve ANTES del tutor en D3.2
 * (D2.6 era después). Justificación binaria:
 *   - En SSE el caller necesita las citations en headers, no después del
 *     stream cerrado. Si magna corre después, las citations llegarían tarde
 *     y romperían el contrato `useChat` del cliente.
 *   - El significado de "validación magna" no cambia: Sonar valida el tema
 *     del usuario contra fuentes recientes. La validación NO depende del
 *     output del tutor (verifica el tema, no la respuesta).
 *
 * Hardening D2.5 preservado:
 *   - H-2: try/catch con adjustSpent(-estimated) rollback en cada llamada LLM
 *   - H-3: preCallCheck/postCallCommit independiente para classifier y magna
 *   - DSC-G-008 v4: error path coverage explícito en cada LLM call
 *
 * Brand Engine: error namespace `[la-forja:tutor_*]`.
 */

import { Hono } from "hono";
import { buildTutorStream } from "../lib/llm/anthropic";
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
  /**
   * Override del builder de stream para tests. Si presente, se usa en lugar
   * de `buildTutorStream`. Permite a los tests devolver un stream mock que
   * no toca el SDK Vercel ni el provider Anthropic.
   */
  streamBuilder?: typeof buildTutorStream;
}

export type TutorChatContext = ForjaAuthContext & ForjaBudgetContext;

/**
 * Estimaciones canónicas de tokens por misión auxiliar.
 * - classifier: input ~500 tok, output ~50 tok (intent + score JSON)
 * - magna_validation: input ~1000 tok, output ~500 tok (citations + razonamiento)
 *
 * Usados SOLO para preCallCheck. postCallCommit ajusta con tokens reales.
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

    // ---- 1. AC12 classify (preCallCheck/postCallCommit/rollback — H-2 + H-3)
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
      await deps.budgetClient.adjustSpent(user.id, -classifierEstimated);
      throw err;
    }
    await postCallCommit(
      deps.budgetClient,
      user.id,
      "classifier",
      CLASSIFIER_MAX_INPUT,
      CLASSIFIER_MAX_OUTPUT,
      classifierEstimated,
    );

    // ---- 2. Telemetry event si confusion
    if (ac12.passesThreshold) {
      await recordEvent({
        userId: user.id,
        type: "simplification_requested",
        confidence: ac12.confidence,
      });
    }

    // ---- 3. Magna validation (PRE-STREAM en D3.2 — ver rationale arriba)
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
              content: `Verifica con fuentes recientes este tema/pregunta del usuario para que el tutor pueda responder citando: ${lastUserMsg.content}`,
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
        await postCallCommit(
          deps.budgetClient,
          user.id,
          "magna_validation",
          MAGNA_MAX_INPUT,
          MAGNA_MAX_OUTPUT,
          magnaEstimated,
        );
      } catch (err) {
        await deps.budgetClient.adjustSpent(user.id, -magnaEstimated);
        throw err;
      }
    }

    // ---- 4. Tutor stream (Claude Opus 4.7 Adaptive — H-2 rollback en onError)
    const tutorBudgetEstimated = c.var.budgetEstimated;
    const builder = deps.streamBuilder ?? buildTutorStream;

    const result = builder({
      messages: body.messages,
      systemPrompt: body.systemPrompt,
      onFinish: async ({ inputTokens, outputTokens }) => {
        await postCallCommit(
          deps.budgetClient,
          user.id,
          "tutor",
          inputTokens,
          outputTokens,
          tutorBudgetEstimated,
        );
      },
      onError: async () => {
        await deps.budgetClient.adjustSpent(user.id, -tutorBudgetEstimated);
      },
    });

    // Headers SSE — DSC-LF-005 + protocolo Vercel AI SDK 6 (UI Message Stream).
    // Las citations viajan en x-la-forja-citations (JSON encoded) para que el
    // cliente las lea pre-stream sin parsear chunks.
    const headers: Record<string, string> = {
      "x-vercel-ai-ui-message-stream": "v1",
      "x-la-forja-intent": ac12.intent,
      "x-la-forja-confidence": ac12.confidence.toFixed(4),
      "x-la-forja-model": "claude-opus-4-7",
    };
    if (citations.length > 0) {
      headers["x-la-forja-citations"] = JSON.stringify(citations);
    }
    if (validationModel !== null) {
      headers["x-la-forja-validation-model"] = validationModel;
    }

    return result.toUIMessageStreamResponse({ headers });
  });

  return app;
}
