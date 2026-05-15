/**
 * La Forja — Multi-model router.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.2.
 * Despacha cada misión al modelo correcto según §2.4 SPEC v3.2.
 *
 * Misiones canónicas (5):
 *   - tutor              → Anthropic Claude Opus 4.7 (modo Adaptive obligatorio)
 *   - sprint_copilot     → OpenAI GPT-5.5 Pro (/v1/responses con input array)
 *   - rag                → Google Gemini 3.1 Pro preview
 *   - classifier         → Google Gemini 2.5 Flash (AC12 con threshold 0.7)
 *   - magna_validation   → Perplexity Sonar Reasoning Pro (DSC-LF-004 única)
 *
 * Doctrina: una misión = un modelo. Sin fallbacks silenciosos cross-model
 * porque cambia el costo/latencia/cualidades — los fallbacks se manejan
 * a nivel manus_bridge.ts (retry con backoff exponencial) o a nivel ruta
 * (degradación documentada en respuesta al usuario).
 */

import {
  invokeTutor,
  type AnthropicTutorRequest,
  type AnthropicTutorResponse,
} from "./anthropic";
import {
  invokeRag,
  invokeClassifier,
  type GeminiRequest,
  type GeminiResponse,
} from "./google";
import {
  invokeSprintCopilot,
  type OpenAISprintRequest,
  type OpenAISprintResponse,
} from "./openai";
import {
  invokeMagnaValidation,
  type PerplexityMagnaRequest,
  type PerplexityMagnaResponse,
} from "./perplexity";

export type Mission =
  | "tutor"
  | "sprint_copilot"
  | "rag"
  | "classifier"
  | "magna_validation";

export const MISSIONS: readonly Mission[] = [
  "tutor",
  "sprint_copilot",
  "rag",
  "classifier",
  "magna_validation",
] as const;

/**
 * Map binario misión → modelo declarado canónicamente. Un test asegura que
 * siempre coincide con §2.4 del SPEC y que no se introducen modelos shadow.
 */
export const MISSION_TO_MODEL: Record<Mission, string> = {
  tutor: "claude-opus-4-7",
  sprint_copilot: "gpt-5.5-pro",
  rag: "gemini-3.1-pro-preview",
  classifier: "gemini-2.5-flash",
  magna_validation: "sonar-reasoning-pro",
};

/**
 * Pricing canónico USD por 1M tokens. Fuente: §2.4 SPEC v3.2 verificada
 * magna 15-may-2026. Usado por motor budget para estimación pre-call.
 */
export const MISSION_PRICING: Record<
  Mission,
  { inputPerMtok: number; outputPerMtok: number }
> = {
  tutor: { inputPerMtok: 5.0, outputPerMtok: 25.0 },
  sprint_copilot: { inputPerMtok: 5.0, outputPerMtok: 30.0 },
  rag: { inputPerMtok: 2.0, outputPerMtok: 12.0 },
  classifier: { inputPerMtok: 0.075, outputPerMtok: 0.3 },
  magna_validation: { inputPerMtok: 2.0, outputPerMtok: 8.0 },
};

/**
 * Type-safe dispatcher por misión. Cada misión tiene su shape de request/response
 * propia — no intentamos unificar superficies para mantener tipos exactos.
 */
export const router = {
  tutor: (req: AnthropicTutorRequest): Promise<AnthropicTutorResponse> =>
    invokeTutor(req),

  sprintCopilot: (req: OpenAISprintRequest): Promise<OpenAISprintResponse> =>
    invokeSprintCopilot(req),

  rag: (req: GeminiRequest): Promise<GeminiResponse> => invokeRag(req),

  classifier: (req: GeminiRequest): Promise<GeminiResponse> =>
    invokeClassifier(req),

  magnaValidation: (
    req: PerplexityMagnaRequest,
  ): Promise<PerplexityMagnaResponse> => invokeMagnaValidation(req),
};
