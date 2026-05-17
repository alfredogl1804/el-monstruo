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
import {
  FORJA_TUTOR_HEADER_KEYS,
  FORJA_CITATIONS_HEADER_MAX_BYTES,
} from "../shared/headers";

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
    // tutorBudgetEstimated lo reserva el middleware ANTES de la ruta. Lo
    // capturamos aquí para revertirlo si classifier o magna fallan (F-D3.2-01).
    const tutorBudgetEstimated = c.var.budgetEstimated;
    let ac12: AC12Classification;
    try {
      ac12 =
        typeof deps.classifier === "function"
          ? await deps.classifier()
          : deps.classifier ?? (await classifyMessage(lastUserMsg.content));
    } catch (err) {
      // F-D3.2-01: si classifier falla, revertir AMBAS reservas para evitar
      // leak permanente del budget tutor que el middleware ya reservó.
      await deps.budgetClient.adjustSpent(user.id, -classifierEstimated);
      await deps.budgetClient.adjustSpent(user.id, -tutorBudgetEstimated);
      throw new Error("[la-forja:tutor_classifier_failed]", { cause: err });
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
        // F-D3.2-01: rollback AMBAS reservas (magna + tutor) para evitar leak.
        await deps.budgetClient.adjustSpent(user.id, -magnaEstimated);
        await deps.budgetClient.adjustSpent(user.id, -tutorBudgetEstimated);
        throw new Error("[la-forja:tutor_magna_failed]", { cause: err });
      }
    }

    // ---- 4. Tutor stream (Claude Opus 4.7 Adaptive — H-2 rollback en onError)
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
        // F-D3.2-02: try/catch también en el callsite (no solo en el wrapper
        // de lib/llm/anthropic.ts) porque los mocks del stream builder en
        // tests pueden invocar onError directo sin pasar por el wrapper.
        try {
          await deps.budgetClient.adjustSpent(user.id, -tutorBudgetEstimated);
        } catch (rollbackError) {
          console.error(
            "[la-forja:tutor_rollback_failed] adjustSpent threw inside onError",
            { rollbackError },
          );
        }
      },
    });

    // Headers SSE — DSC-LF-005 + protocolo Vercel AI SDK 6 (UI Message Stream).
    // F-D3.2-03/04: citations viajan en x-la-forja-citations-b64 (base64url JSON)
    // para soportar UTF-8 sin romper RFC 7230 + cap 2KB para evitar truncación
    // por límites de header de Cloud Run / Hono.
    const headers: Record<string, string> = {
      [FORJA_TUTOR_HEADER_KEYS.protocolVersion]: "v1",
      [FORJA_TUTOR_HEADER_KEYS.intent]: ac12.intent,
      [FORJA_TUTOR_HEADER_KEYS.confidence]: ac12.confidence.toFixed(4),
      [FORJA_TUTOR_HEADER_KEYS.model]: "claude-opus-4-7",
    };
    if (citations.length > 0) {
      // F-D3.2.1-01: truncar por CITATION COMPLETA (no por bytes ciegos).
      // El truncado por bytes cortaba el JSON a la mitad de un string/codepoint
      // y producía base64url cuyo decode rompía `JSON.parse` en el frontend,
      // perdiendo TODAS las citations silenciosamente (forjaHeaders.ts catch
      // retorna []). Ahora acumulamos citation por citation mientras quepa
      // dentro de FORJA_CITATIONS_HEADER_MAX_BYTES; el JSON resultante es
      // siempre parseable.
      const capped: typeof citations = [];
      for (const citation of citations) {
        const candidate = [...capped, citation];
        const candidateBytes = Buffer.byteLength(
          JSON.stringify(candidate),
          "utf-8",
        );
        if (candidateBytes > FORJA_CITATIONS_HEADER_MAX_BYTES) break;
        capped.push(citation);
      }
      if (capped.length > 0) {
        headers[FORJA_TUTOR_HEADER_KEYS.citationsB64] = Buffer.from(
          JSON.stringify(capped),
          "utf-8",
        ).toString("base64url");
      }
    }
    if (validationModel !== null) {
      headers[FORJA_TUTOR_HEADER_KEYS.validationModel] = validationModel;
    }

    return result.toUIMessageStreamResponse({ headers });
  });

  return app;
}
