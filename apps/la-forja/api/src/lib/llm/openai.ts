/**
 * La Forja — OpenAI GPT-5.5 Pro client (co-piloto sprints).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.2 + D6 (DSC-LF-D6 circuit breaker pre-call).
 * Modelo verificado magna 15-may-2026: gpt-5.5-pro (lanzado 23-abr-2026).
 * Pricing: $5 input / $30 output por Mtok.
 * SDK: openai@6.38.0 (verificado magna).
 *
 * Doctrina: §2.4 SPEC v3.2 — endpoint /v1/responses requiere `input` como
 * array de messages, NO string. Reasoning Pro NO acepta `temperature`.
 *
 * SPRINT D6: circuit breaker pre-call detecta credit-depleted / quota
 * exceeded del API OpenAI y abre cooldown 5min para fail-fast.
 *
 * Este cliente expone invokeSprintCopilot(input) → respuesta + tokens reales.
 */

import OpenAI from "openai";
import { loadEnv } from "../env.js";

export const OPENAI_SPRINT_MODEL = "gpt-5.5-pro" as const;

// ----------------------------------------------------------------------------
// Circuit breaker pre-call (Sprint D6 — DSC-LF-D6).
//
// Detecta proactivamente respuestas credit-depleted del API OpenAI y abre un
// cooldown de 5min durante el cual cualquier invocación posterior falla
// rápido en <1ms.
//
// Patrones cubiertos (verbatim mensajes oficiales OpenAI):
//   - "You exceeded your current quota"
//   - "insufficient_quota"
//   - "Your account has been deactivated"
//
// Observabilidad: log namespaced [la-forja:openai_credit_depleted] aparece en
// stdout y telemetry para alerts operacionales.
// ----------------------------------------------------------------------------

const CIRCUIT_BREAKER_COOLDOWN_MS = 5 * 60 * 1000; // 5 min

/**
 * Patrones binarios que disparan el circuit breaker para OpenAI.
 * Cubren mensajes oficiales del API en HTTP 429 quota_exceeded y
 * HTTP 401 account_deactivated.
 */
const OPENAI_CREDIT_DEPLETED_PATTERNS = [
  /exceeded your current quota/i,
  /insufficient[_\s-]+quota/i,
  /quota[_\s-]+exceeded/i,
  /account[_\s-]+has[_\s-]+been[_\s-]+deactivated/i,
  /credit[_\s-]+balance[_\s-]+too[_\s-]+low/i,
] as const;

let _openaiCreditDepletedUntil: number | null = null;

/**
 * @internal — uso solo en tests. Resetea el flag del circuit breaker.
 */
export function _resetOpenAICircuitBreaker(): void {
  _openaiCreditDepletedUntil = null;
}

/**
 * @internal — uso solo en tests. Devuelve el estado actual del circuit.
 */
export function _getOpenAICircuitState(): {
  open: boolean;
  cooldownUntil: number | null;
} {
  const open =
    _openaiCreditDepletedUntil !== null &&
    Date.now() < _openaiCreditDepletedUntil;
  return { open, cooldownUntil: _openaiCreditDepletedUntil };
}

/**
 * Pre-call check: si el circuit breaker está abierto (cooldown vigente),
 * lanza error namespaced sin invocar el API.
 *
 * @throws Error con prefix `[la-forja:openai_credit_depleted]`
 */
function _assertOpenAICircuitClosed(): void {
  if (
    _openaiCreditDepletedUntil !== null &&
    Date.now() < _openaiCreditDepletedUntil
  ) {
    const until = new Date(_openaiCreditDepletedUntil).toISOString();
    throw new Error(
      `[la-forja:openai_credit_depleted] circuit breaker open until ${until}`,
    );
  }
  // Auto-reset post-cooldown.
  if (
    _openaiCreditDepletedUntil !== null &&
    Date.now() >= _openaiCreditDepletedUntil
  ) {
    _openaiCreditDepletedUntil = null;
  }
}

/**
 * Post-call inspection: si el error capturado matchea un patrón
 * credit-depleted, abre el circuit breaker.
 */
function _maybeTripOpenAICircuit(err: unknown): void {
  const msg =
    err instanceof Error
      ? err.message
      : typeof err === "string"
        ? err
        : JSON.stringify(err);
  const matches = OPENAI_CREDIT_DEPLETED_PATTERNS.some((re) => re.test(msg));
  if (matches) {
    _openaiCreditDepletedUntil = Date.now() + CIRCUIT_BREAKER_COOLDOWN_MS;
    const until = new Date(_openaiCreditDepletedUntil).toISOString();
    console.error(
      "[la-forja:openai_credit_depleted] circuit breaker triggered",
      { cooldownUntil: until, originalError: msg },
    );
  }
}

export interface OpenAIInputMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface OpenAISprintRequest {
  input: OpenAIInputMessage[];
  maxOutputTokens?: number;
}

export interface OpenAISprintResponse {
  content: string;
  inputTokens: number;
  outputTokens: number;
  model: string;
  status: string;
}

let _cached: OpenAI | null = null;

function getClient(): OpenAI {
  if (_cached) {return _cached;}
  const env = loadEnv();
  _cached = new OpenAI({ apiKey: env.OPENAI_API_KEY });
  return _cached;
}

export function _resetOpenAICache(): void {
  _cached = null;
  _resetOpenAICircuitBreaker();
}

/**
 * Invoca GPT-5.5 Pro vía Responses API.
 * Doctrina §2.4: `input` debe ser array (NO string), sin `temperature`.
 *
 * SPRINT D6: circuit breaker pre-call. Si OpenAI rechazó por credit-depleted /
 * quota_exceeded en últimos 5min, fail-fast con
 * [la-forja:openai_credit_depleted] sin tocar el API.
 */
export async function invokeSprintCopilot(
  req: OpenAISprintRequest,
): Promise<OpenAISprintResponse> {
  _assertOpenAICircuitClosed();

  const client = getClient();
  try {
    const response = await client.responses.create({
      model: OPENAI_SPRINT_MODEL,
      input: req.input,
      max_output_tokens: req.maxOutputTokens ?? 4096,
    });

    // SDK v6 expone helper output_text que concatena los text blocks.
    const content = response.output_text ?? "";
    const usage = response.usage;

    return {
      content,
      inputTokens: usage?.input_tokens ?? 0,
      outputTokens: usage?.output_tokens ?? 0,
      model: response.model ?? OPENAI_SPRINT_MODEL,
      status: response.status ?? "completed",
    };
  } catch (err) {
    _maybeTripOpenAICircuit(err);
    throw err;
  }
}
