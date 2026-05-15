/**
 * La Forja — Anthropic Claude Opus 4.7 client (tutor adaptativo).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.2.
 * Modelo verificado magna 15-may-2026: claude-opus-4-7 (lanzado 16-abr-2026).
 * Pricing: $5 input / $25 output por Mtok.
 * SDK: @anthropic-ai/sdk@0.96.0 (verificado magna).
 *
 * Doctrina: §2.4 SPEC v3.2 — modo `adaptive` thinking obligatorio.
 * Restricción: temperature puede usarse pero NO junto con thinking activo.
 *
 * Este cliente expone una superficie minimal: invokeTutor(messages) → respuesta
 * tipada con tokens reales para commit del budget post-call (LF-RATE-LIMIT-001).
 */

import Anthropic from "@anthropic-ai/sdk";
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

let _cached: Anthropic | null = null;

function getClient(): Anthropic {
  if (_cached) return _cached;
  const env = loadEnv();
  _cached = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });
  return _cached;
}

export function _resetAnthropicCache(): void {
  _cached = null;
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
