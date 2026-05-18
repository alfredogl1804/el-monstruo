/**
 * La Forja — Google Gemini clients (RAG + clasificador AC12).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.2.
 * Modelos verificados magna 15-may-2026:
 *   - gemini-3.1-pro-preview (RAG corpus): $2 input / $12 output por Mtok ≤200K
 *   - gemini-2.5-flash       (clasificador AC12): $0.075 input / $0.30 output
 *
 * SDK: @google/genai@2.3.0 (verificado magna). NOTA: el SDK legacy
 * @google/generative-ai@0.24.1 está deprecated, NO usar.
 *
 * Doctrina: §2.4 SPEC v3.2.
 *   - Pro 3.1 preview tiene 1,048,576 input + 65,536 output tokens.
 *   - Flash usado para AC12 con threshold confidence ≥ 0.7.
 */

import { GoogleGenAI } from "@google/genai";
import { loadEnv } from "../env";

export const GEMINI_RAG_MODEL = "gemini-3.1-pro-preview" as const;
export const GEMINI_CLASSIFIER_MODEL = "gemini-2.5-flash" as const;

export interface GeminiRequest {
  prompt: string;
  systemInstruction?: string;
  maxOutputTokens?: number;
  responseMimeType?: "text/plain" | "application/json";
  responseSchema?: object;
}

export interface GeminiResponse {
  content: string;
  inputTokens: number;
  outputTokens: number;
  model: string;
  finishReason: string | null;
}

let _cached: GoogleGenAI | null = null;

function getClient(): GoogleGenAI {
  if (_cached) {return _cached;}
  const env = loadEnv();
  _cached = new GoogleGenAI({ apiKey: env.GEMINI_API_KEY });
  return _cached;
}

export function _resetGoogleCache(): void {
  _cached = null;
}

/**
 * Invoca un modelo Gemini específico. Internamente usado por:
 *   - invokeRag()         → Pro 3.1 preview para RAG corpus
 *   - invokeClassifier()  → 2.5 Flash para AC12 con structured JSON output
 */
async function invokeGemini(
  model: string,
  req: GeminiRequest,
): Promise<GeminiResponse> {
  const client = getClient();
  const response = await client.models.generateContent({
    model,
    contents: req.prompt,
    config: {
      systemInstruction: req.systemInstruction,
      maxOutputTokens: req.maxOutputTokens ?? 2048,
      responseMimeType: req.responseMimeType,
      responseSchema: req.responseSchema,
    },
  });

  const content = response.text ?? "";
  const usage = response.usageMetadata;
  const finishReason = response.candidates?.[0]?.finishReason ?? null;

  return {
    content,
    inputTokens: usage?.promptTokenCount ?? 0,
    outputTokens: usage?.candidatesTokenCount ?? 0,
    model,
    finishReason,
  };
}

/** RAG sobre corpus del Monstruo (Pro 3.1 preview). */
export function invokeRag(req: GeminiRequest): Promise<GeminiResponse> {
  return invokeGemini(GEMINI_RAG_MODEL, req);
}

/** Clasificador AC12 con JSON estructurado (Flash). */
export function invokeClassifier(req: GeminiRequest): Promise<GeminiResponse> {
  return invokeGemini(GEMINI_CLASSIFIER_MODEL, req);
}
