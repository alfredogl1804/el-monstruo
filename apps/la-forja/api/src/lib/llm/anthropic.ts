/**
 * La Forja — Anthropic Claude Opus 4.7 client (tutor adaptativo).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.2 + D3.2 (DSC-LF-005 SSE migration)
 *                          + D6 (DSC-LF-D6 circuit breaker pre-call).
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
 *   - SPRINT D6: circuit breaker pre-call detecta credit-depleted y abre
 *     cooldown 5min para fail-fast (vs esperar 2-3s timeout API real).
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
import { loadEnv } from "../env.js";

export const ANTHROPIC_TUTOR_MODEL = "claude-opus-4-7" as const;

// ----------------------------------------------------------------------------
// Circuit breaker pre-call (Sprint D6 — DSC-LF-D6).
//
// Detecta proactivamente respuestas "credit balance is too low" del API
// Anthropic y abre un cooldown de 5min durante el cual cualquier invocación
// posterior falla rápido en <1ms, evitando:
//   - Latencia P99 elevada durante credit outage
//   - Spam de calls al API que sabemos van a fallar
//   - Rate-limit churn
//
// Observabilidad: log namespaced [la-forja:anthropic_credit_depleted] aparece
// en stdout y telemetry para alerts operacionales.
//
// Reset: post-cooldown 5min auto-reset, o llamar
// _resetAnthropicCircuitBreaker() en tests.
// ----------------------------------------------------------------------------

const CIRCUIT_BREAKER_COOLDOWN_MS = 5 * 60 * 1000; // 5 min

/**
 * Patrones binarios que disparan el circuit breaker.
 * Cubren mensajes oficiales del API Anthropic en HTTP 400/402.
 */
const ANTHROPIC_CREDIT_DEPLETED_PATTERNS = [
  /credit balance is too low/i,
  /insufficient[_\s-]+credits?/i,
  /credit[_\s-]+balance[_\s-]+too[_\s-]+low/i,
] as const;

let _anthropicCreditDepletedUntil: number | null = null;

/**
 * @internal — uso solo en tests. Resetea el flag del circuit breaker.
 */
export function _resetAnthropicCircuitBreaker(): void {
  _anthropicCreditDepletedUntil = null;
}

/**
 * @internal — uso solo en tests. Devuelve el timestamp de cooldown actual o
 * null si el circuit está cerrado (operación normal).
 */
export function _getAnthropicCircuitState(): {
  open: boolean;
  cooldownUntil: number | null;
} {
  const open =
    _anthropicCreditDepletedUntil !== null &&
    Date.now() < _anthropicCreditDepletedUntil;
  return { open, cooldownUntil: _anthropicCreditDepletedUntil };
}

/**
 * Pre-call check: si el circuit breaker está abierto (cooldown vigente),
 * lanza error namespaced sin invocar el API.
 *
 * @throws Error con prefix `[la-forja:anthropic_credit_depleted]`
 */
function _assertAnthropicCircuitClosed(): void {
  if (
    _anthropicCreditDepletedUntil !== null &&
    Date.now() < _anthropicCreditDepletedUntil
  ) {
    const until = new Date(_anthropicCreditDepletedUntil).toISOString();
    throw new Error(
      `[la-forja:anthropic_credit_depleted] circuit breaker open until ${until}`,
    );
  }
  // Auto-reset post-cooldown: limpia el flag para evitar comparación lazy futura.
  if (
    _anthropicCreditDepletedUntil !== null &&
    Date.now() >= _anthropicCreditDepletedUntil
  ) {
    _anthropicCreditDepletedUntil = null;
  }
}

/**
 * Post-call inspection: si el error capturado matchea un patrón
 * credit-depleted, abre el circuit breaker.
 */
function _maybeTripAnthropicCircuit(err: unknown): void {
  const msg =
    err instanceof Error
      ? err.message
      : typeof err === "string"
        ? err
        : JSON.stringify(err);
  const matches = ANTHROPIC_CREDIT_DEPLETED_PATTERNS.some((re) => re.test(msg));
  if (matches) {
    _anthropicCreditDepletedUntil = Date.now() + CIRCUIT_BREAKER_COOLDOWN_MS;
    const until = new Date(_anthropicCreditDepletedUntil).toISOString();
    console.error(
      "[la-forja:anthropic_credit_depleted] circuit breaker triggered",
      { cooldownUntil: until, originalError: msg },
    );
  }
}

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
  if (_cached) {return _cached;}
  const env = loadEnv();
  _cached = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });
  return _cached;
}

export function _resetAnthropicCache(): void {
  _cached = null;
  _cachedProvider = null;
  _resetAnthropicCircuitBreaker();
}

/**
 * Invoca Claude Opus 4.7 en modo Adaptive (tutor del Cliente Cero T1-Padre).
 * Retorna respuesta + tokens reales para post-call commit del budget.
 *
 * SPRINT D6: circuit breaker pre-call. Si Anthropic rechazó por
 * credit-depleted en últimos 5min, fail-fast con
 * [la-forja:anthropic_credit_depleted] sin tocar el API.
 */
export async function invokeTutor(
  req: AnthropicTutorRequest,
): Promise<AnthropicTutorResponse> {
  _assertAnthropicCircuitClosed();

  const client = getClient();
  try {
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
  } catch (err) {
    _maybeTripAnthropicCircuit(err);
    throw err;
  }
}

// ----------------------------------------------------------------------------
// Streaming client (D3.2 — DSC-LF-005) — Vercel AI SDK 6 + @ai-sdk/anthropic
// ----------------------------------------------------------------------------

type AnthropicProviderFactory = ReturnType<typeof createAnthropic>;

let _cachedProvider: AnthropicProviderFactory | null = null;

function getTutorProvider(): AnthropicProviderFactory {
  if (_cachedProvider) {return _cachedProvider;}
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
    /** Texto agregado del assistant. Disponible en D5.2 para persistir
     * en forja_messages.content. Puede ser '' si el stream no produjo texto. */
    text: string;
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
 *
 * SPRINT D6: circuit breaker pre-call. Si circuit está abierto, throw
 * [la-forja:anthropic_credit_depleted] antes de iniciar el stream.
 * El handler onError también captura credit-depleted detectado mid-stream
 * y trip el circuit para invocaciones subsiguientes.
 */
export function buildTutorStream(
  opts: BuildTutorStreamOptions,
): TutorStreamResult {
  // Pre-call check: si circuit abierto, throw síncrono antes de streamText().
  // Esto NO tira el process; el caller (route /api/tutor/chat) hace catch.
  _assertAnthropicCircuitClosed();

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
        text: event.text ?? "",
      });
    },
    onError: async ({ error }) => {
      // SPRINT D6: detecta credit-depleted en errores mid-stream y trip
      // circuit breaker para invocaciones subsiguientes.
      _maybeTripAnthropicCircuit(error);

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
