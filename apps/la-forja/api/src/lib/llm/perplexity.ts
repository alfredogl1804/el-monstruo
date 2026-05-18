/**
 * La Forja — Perplexity Sonar Reasoning Pro client.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.2.
 * Modelo verificado magna 15-may-2026: sonar-reasoning-pro.
 * Pricing: $2 input / $8 output por Mtok.
 *
 * SDK: NO existe SDK oficial Perplexity. Usamos fetch directo contra la
 * API REST OpenAI-compatible: https://api.perplexity.ai/chat/completions
 *
 * Doctrina: §2.2 + DSC-LF-004 SPEC v3.2.
 *   - Perplexity Sonar es la ÚNICA capa de validación externa permitida.
 *   - Reemplaza al Consejo de 6 Sabios (decisión T1-Alfredo 15-may-2026).
 *   - Devuelve `citations` array con URLs evidencia inline en respuestas.
 *
 * Uso: cuando el clasificador detecta riesgo de obsolescencia (modelos IA, SDKs,
 * frameworks, precios actuales, eventos recientes) → invokeMagnaValidation()
 * inserta evidencia con citations en la respuesta del tutor.
 */

import { loadEnv } from "../env.js";

export const PERPLEXITY_MAGNA_MODEL = "sonar-reasoning-pro" as const;
export const PERPLEXITY_API_URL =
  "https://api.perplexity.ai/chat/completions" as const;

export interface PerplexityMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface PerplexityMagnaRequest {
  messages: PerplexityMessage[];
  maxTokens?: number;
}

export interface PerplexityMagnaResponse {
  content: string;
  citations: string[];
  inputTokens: number;
  outputTokens: number;
  model: string;
}

interface PerplexityRawResponse {
  id: string;
  model: string;
  citations?: string[];
  choices: Array<{
    message: { role: string; content: string };
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

/**
 * Invoca Perplexity Sonar Reasoning Pro para validación tiempo real.
 * Retorna respuesta + citations URLs para insertar evidencia inline.
 */
export async function invokeMagnaValidation(
  req: PerplexityMagnaRequest,
  options: { fetchImpl?: typeof fetch } = {},
): Promise<PerplexityMagnaResponse> {
  const env = loadEnv();
  const fetchImpl = options.fetchImpl ?? globalThis.fetch;

  const response = await fetchImpl(PERPLEXITY_API_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.SONAR_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: PERPLEXITY_MAGNA_MODEL,
      messages: req.messages,
      max_tokens: req.maxTokens ?? 1024,
    }),
  });

  if (!response.ok) {
    const errBody = await response.text().catch(() => "");
    throw new Error(
      `[la-forja:perplexity_validation_http_failed] HTTP ${response.status}: ${errBody.slice(0, 200)}`,
    );
  }

  const data = (await response.json()) as PerplexityRawResponse;
  const choice = data.choices[0];
  if (!choice) {
    throw new Error(
      "[la-forja:perplexity_validation_empty_response] No choices in response",
    );
  }

  return {
    content: choice.message.content,
    citations: data.citations ?? [],
    inputTokens: data.usage.prompt_tokens,
    outputTokens: data.usage.completion_tokens,
    model: data.model,
  };
}
