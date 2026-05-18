/**
 * La Forja — OpenAI GPT-5.5 Pro client (co-piloto sprints).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.2.
 * Modelo verificado magna 15-may-2026: gpt-5.5-pro (lanzado 23-abr-2026).
 * Pricing: $5 input / $30 output por Mtok.
 * SDK: openai@6.38.0 (verificado magna).
 *
 * Doctrina: §2.4 SPEC v3.2 — endpoint /v1/responses requiere `input` como
 * array de messages, NO string. Reasoning Pro NO acepta `temperature`.
 *
 * Este cliente expone invokeSprintCopilot(input) → respuesta + tokens reales.
 */

import OpenAI from "openai";
import { loadEnv } from "../env.js";

export const OPENAI_SPRINT_MODEL = "gpt-5.5-pro" as const;

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
}

/**
 * Invoca GPT-5.5 Pro vía Responses API.
 * Doctrina §2.4: `input` debe ser array (NO string), sin `temperature`.
 */
export async function invokeSprintCopilot(
  req: OpenAISprintRequest,
): Promise<OpenAISprintResponse> {
  const client = getClient();
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
}
