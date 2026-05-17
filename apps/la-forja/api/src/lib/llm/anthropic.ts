/**
 * La Forja — Anthropic Claude Opus 4.7 client (tutor adaptativo).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.2 + D3.2 (DSC-LF-005 SSE migration).
 * Modelo verificado magna 15-may-2026: claude-opus-4-7 (lanzado 16-abr-2026).
 * Pricing: $5 input / $25 output por Mtok.
 *
 * SDKs:
 *   - @anthropic-ai/sdk@0.96.0 — invokeTutor() blocking. Path legacy preservado
 *     para compat de tests; NO usado por /api/tutor/chat desde D3.2.
 *   - @ai-sdk/anthropic@3.0.78 + ai@6.0.184 — buildTutorStream() streaming SSE
 *     compatible con toUIMessageStreamResponse() (DSC-LF-005, D3.2).
 *
 * Doctrina:
 *   - §2.4 SPEC v3.2 — modo `adaptive` thinking obligatorio.
 *   - DSC-LF-005 — todos los endpoints LLM retornan text/event-stream con
 *     toUIMessageStreamResponse(); JSON solo para metadata no-LLM.
 *   - Restricción: temperature puede usarse pero NO junto con thinking activo.
 *
 * Dependency injection: getTutorProvider() permite override en tests via
 * _setTutorProviderForTesting() para evitar llamadas reales al SDK.
 */

import Anthropic from "@anthropic-ai/sdk";
import { createAnthropic } from "@ai-sdk/anthropic";
import {
  streamText,
  type StreamTextResult,
  type ModelMessage,
  type ToolSet,
} from "ai";
import { loadEnv } from "../env";

export const ANTHROPIC_TUTOR_MODEL = "claude-opus-4-7" as const;

export interface AnthropicMessage {
  role: "user" | "assistant";
  content: string;
}

export interface AnthropicTutorRequest {
  messages: AnthropicMessage[];
  systemPrompt?: string;
  maxTokens?: number;
}

export interface AnthropicTutorResponse {
  content: string;
  inputTokens: number;
  outputTokens: number;
  model: string;
  stopReason: string | null;
}

// ----------------------------------------------------------------------------
// Legacy blocking client (D2.2) — conservado para compat tests pre-D3.2
// ----------------------------------------------------------------------------

let _cached: Anthropic | null = null;

function getClient(): Anthropic {
  if (_cached) return _cached;
  const env = loadEnv();
  _cached = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });
  return _cached;
}

export function _resetAnthropicCache(): void {
  _cached = null;
  _cachedProvider = null;
}

/**
 * Invoca Claude Opus 4.7 en modo Adaptive (tutor del Cliente Cero T1-Padre).
 * Retorna respuesta + tokens reales para post-call commit del budget.
 */
export async function invokeTutor(
  req: AnthropicTutorRequest,
): Promise<AnthropicTutorResponse> {
  const client = getClient();
  const response = await client.messages.create({
    model: ANTHROPIC_TUTOR_MODEL,
    max_tokens: req.maxTokens ?? 2048,
    system: req.systemPrompt,
    messages: req.messages,
    // Modo Adaptive obligatorio §2.4 — el modelo decide thinking budget por turn.
    // Cuando thinking está activo, NO se debe pasar temperature.
    thinking: { type: "enabled", budget_tokens: 1024 },
  });

  // Extraer texto de los blocks (puede haber thinking blocks que ignoramos para output).
  const textBlocks = response.content.filter((b) => b.type === "text");
  const content = textBlocks.map((b) => b.text).join("\n");

  return {
    content,
    inputTokens: response.usage.input_tokens,
    outputTokens: response.usage.output_tokens,
    model: response.model,
    stopReason: response.stop_reason,
  };
}

// ----------------------------------------------------------------------------
// Streaming client (D3.2 — DSC-LF-005) — Vercel AI SDK 6 + @ai-sdk/anthropic
// ----------------------------------------------------------------------------

type AnthropicProviderFactory = ReturnType<typeof createAnthropic>;

let _cachedProvider: AnthropicProviderFactory | null = null;

function getTutorProvider(): AnthropicProviderFactory {
  if (_cachedProvider) return _cachedProvider;
  const env = loadEnv();
  _cachedProvider = createAnthropic({ apiKey: env.ANTHROPIC_API_KEY });
  return _cachedProvider;
}

/**
 * Inyección para tests: override del provider Anthropic. Pasar `null` resetea.
 */
export function _setTutorProviderForTesting(
  provider: AnthropicProviderFactory | null,
): void {
  _cachedProvider = provider;
}

export interface BuildTutorStreamOptions {
  messages: AnthropicMessage[];
  systemPrompt?: string;
  maxTokens?: number;
  /**
   * Callback con tokens reales tras el cierre del stream. Usado por la ruta
   * para invocar postCallCommit del budget pipeline.
   */
  onFinish: (event: {
    inputTokens: number;
    outputTokens: number;
    model: string;
    finishReason: string | undefined;
  }) => Promise<void> | void;
  /**
   * Callback de error mid-stream. Usado por la ruta para rollback del budget
   * (adjustSpent con valor negativo).
   */
  onError: (error: unknown) => Promise<void> | void;
}

export type TutorStreamResult = StreamTextResult<ToolSet, never>;

/**
 * Construye un stream de Claude Opus 4.7 modo Adaptive compatible con
 * toUIMessageStreamResponse() de Vercel AI SDK 6.
 *
 * El caller invoca `result.toUIMessageStreamResponse({ headers })` para
 * obtener un Response con text/event-stream listo para Hono.
 */
export function buildTutorStream(
  opts: BuildTutorStreamOptions,
): TutorStreamResult {
  const provider = getTutorProvider();

  const modelMessages: ModelMessage[] = opts.messages.map((m) => ({
    role: m.role,
    content: m.content,
  }));

  const result = streamText({
    model: provider(ANTHROPIC_TUTOR_MODEL),
    system: opts.systemPrompt,
    messages: modelMessages,
    maxRetries: 2,
    // Modo Adaptive §2.4 — el modelo decide thinking budget por turn.
    providerOptions: {
      anthropic: {
        thinking: { type: "enabled", budgetTokens: 1024 },
      },
    },
    onFinish: async (event) => {
      const usage = event.totalUsage;
      await opts.onFinish({
        inputTokens: usage.inputTokens ?? 0,
        outputTokens: usage.outputTokens ?? 0,
        model: ANTHROPIC_TUTOR_MODEL,
        finishReason: event.finishReason,
      });
    },
    onError: async ({ error }) => {
      // F-D3.2-02: try/catch alrededor del rollback. Si la DB del budget
      // ledger falla, NO podemos dejar el error silenciado dentro del stream
      // o el cap quedaría inconsistente sin trazabilidad.
      try {
        await opts.onError(error);
      } catch (rollbackError) {
        // Fail-loud: namespace [la-forja:*] (Brand Engine + Regla Dura #6).
        console.error(
          "[la-forja:tutor_rollback_failed] onError handler threw",
          {
            originalError: error,
            rollbackError,
          },
        );
      }
    },
  });

  return result;
}
