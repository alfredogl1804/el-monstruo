/**
 * La Forja — AC12 clasificador semántico (Cowork DSC-G-008 v3 mejora binaria).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.3.
 * Doctrina: §7 AC12 SPEC v3.2.
 *
 * El AC12 detecta `intent="confusion_detected"` con confidence >= 0.7
 * sobre cada mensaje del usuario. Si pasa el threshold, se inserta row
 * en `forja_telemetry` con event="confusion_detected" + evidence + score.
 *
 * Reemplaza al string-match `"no entiendo"` v3.1 que era frágil ante
 * variantes. v3.2 usa Gemini 2.5 Flash con responseSchema JSON estructurado.
 *
 * Las 10 frases sinónimas canónicas del SPEC (test obligatorio):
 *   1. «no entiendo»
 *   2. «no me queda claro»
 *   3. «explícame de nuevo»
 *   4. «muy abstracto»
 *   5. «wat»
 *   6. «¿podrías simplificar?»
 *   7. «me pierdo»
 *   8. «qué quiere decir eso»
 *   9. «muy técnico»
 *   10. «otísimo»
 *
 * Las 10 deben generar row con confidence >= 0.7. El test §AC12 lo audita
 * en D5 contra Gemini real; en D2 con mocks deterministas.
 */

import { invokeClassifier } from "./llm/google";

export const AC12_CONFIDENCE_THRESHOLD = 0.7 as const;

export const AC12_SYSTEM_PROMPT = `Eres un clasificador semántico que detecta cuando un usuario expresa CONFUSIÓN, FALTA DE COMPRENSIÓN, o NECESIDAD DE SIMPLIFICACIÓN al hablar con un tutor.

Tu única tarea: clasificar el último mensaje del usuario en una de dos intenciones:
  - "confusion_detected": el usuario expresa que no entiende, pide simplificación, dice que es muy técnico/abstracto, está perdido, o usa expresiones equivalentes.
  - "no_confusion": el usuario expresa cualquier otra cosa (pregunta normal, afirmación, agradecimiento, etc.).

Devuelves JSON estricto con dos campos:
  - intent: string ("confusion_detected" | "no_confusion")
  - confidence: number entre 0 y 1

NO inventes intents nuevos. NO devuelvas texto fuera del JSON.`;

export const AC12_RESPONSE_SCHEMA = {
  type: "object",
  properties: {
    intent: {
      type: "string",
      enum: ["confusion_detected", "no_confusion"],
    },
    confidence: {
      type: "number",
      minimum: 0,
      maximum: 1,
    },
  },
  required: ["intent", "confidence"],
} as const;

/**
 * Las 10 frases sinónimas canónicas del SPEC §7 AC12.
 * Test obligatorio: las 10 deben clasificar como confusion_detected
 * con confidence >= AC12_CONFIDENCE_THRESHOLD.
 */
export const AC12_CANONICAL_CONFUSION_PHRASES: readonly string[] = [
  "no entiendo",
  "no me queda claro",
  "explícame de nuevo",
  "muy abstracto",
  "wat",
  "¿podrías simplificar?",
  "me pierdo",
  "qué quiere decir eso",
  "muy técnico",
  "otísimo",
] as const;

export interface AC12Classification {
  intent: "confusion_detected" | "no_confusion";
  confidence: number;
  passesThreshold: boolean;
  rawMessage: string;
  inputTokens: number;
  outputTokens: number;
}

/**
 * Clasifica un mensaje del usuario. Retorna el intent + confidence y un flag
 * passesThreshold que dice si se debe registrar row en forja_telemetry.
 *
 * options.classifier permite inyectar un mock determinista en tests sin
 * llamar a Gemini real. En producción se usa el invokeClassifier por default.
 */
export async function classifyMessage(
  rawMessage: string,
  options: {
    classifier?: (prompt: string) => Promise<{
      content: string;
      inputTokens: number;
      outputTokens: number;
    }>;
  } = {},
): Promise<AC12Classification> {
  const classifier =
    options.classifier ??
    (async (prompt: string) => {
      const r = await invokeClassifier({
        prompt,
        systemInstruction: AC12_SYSTEM_PROMPT,
        responseMimeType: "application/json",
        responseSchema: AC12_RESPONSE_SCHEMA,
        maxOutputTokens: 64,
      });
      return {
        content: r.content,
        inputTokens: r.inputTokens,
        outputTokens: r.outputTokens,
      };
    });

  const r = await classifier(rawMessage);

  let parsed: { intent?: string; confidence?: number };
  try {
    parsed = JSON.parse(r.content);
  } catch {
    throw new Error(
      `[la-forja:ac12_classify_invalid_json] Gemini Flash returned non-JSON: ${r.content.slice(0, 100)}`,
    );
  }

  if (
    parsed.intent !== "confusion_detected" &&
    parsed.intent !== "no_confusion"
  ) {
    throw new Error(
      `[la-forja:ac12_classify_invalid_intent] Got intent=${String(parsed.intent)}`,
    );
  }
  if (
    typeof parsed.confidence !== "number" ||
    parsed.confidence < 0 ||
    parsed.confidence > 1
  ) {
    throw new Error(
      `[la-forja:ac12_classify_invalid_confidence] Got confidence=${String(parsed.confidence)}`,
    );
  }

  const passesThreshold =
    parsed.intent === "confusion_detected" &&
    parsed.confidence >= AC12_CONFIDENCE_THRESHOLD;

  return {
    intent: parsed.intent,
    confidence: parsed.confidence,
    passesThreshold,
    rawMessage,
    inputTokens: r.inputTokens,
    outputTokens: r.outputTokens,
  };
}
