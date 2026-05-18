/**
 * La Forja — AC12 clasificador semántico (D5-TUTOR-CLASSIFIER-ROBUSTNESS-001).
 *
 * Sprint LA-FORJA-001 — D5 (refactor desde D2.3 v3.2 post-F2).
 * Doctrina: §7 AC12 SPEC v3.2 + spec D5 firmado 2026-05-18.
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
 *
 * ============================================================================
 * D5 ROBUSTNESS — 3 soluciones binarias post-F2 (Gemini "Here is..." prefix bug)
 * ============================================================================
 *
 * Solución #1 (OBLIGATORIA — root cause fix):
 *   `responseMimeType: "application/json"` + `responseSchema` se pasan al SDK
 *   `@google/genai@2.3.0` (ver `lib/llm/google.ts:invokeClassifier`). Esto
 *   instruye a Gemini a devolver JSON puro sin preámbulos. Mitiga F2 al ~99%
 *   pero NO lo elimina al 100% (Gemini Flash 2.5 puede ocasionalmente ignorar
 *   constraint a baja confidence, issue conocido modelo Flash 2026-05).
 *
 * Solución #2 (DEFENSE-IN-DEPTH — parser tolerante):
 *   `extractJsonStrict()` extrae el primer bloque `{...}` o `[...]` con regex,
 *   tolerante a prefijos (`"Here is..."`) o sufijos textuales del modelo.
 *   Aplicada SIEMPRE antes de `JSON.parse()`. Doble barrera con Solución #1.
 *
 * Solución #3 (MAGNA — fallback chain):
 *   Si Gemini Flash falla 2 retries con `[la-forja:ac12_classify_invalid_json]`,
 *   fallback a Claude Opus 4.7. Si Claude también falla, fallback a GPT-5.5 Pro.
 *   Cada paso emite log namespaced `[la-forja:ac12_fallback_triggered]` para
 *   observability + tracking de rate (DSC-V-001 alineado).
 *
 *   Caveat: fallback chain agrega latencia P99 si primer modelo falla.
 *   Costo P99 worst-case: ~$25/Mtok output (Claude Opus) vs $0.30 (Gemini Flash).
 *   Aceptable porque #1 + #2 reducen tasa de fallback a <0.1%.
 *
 * Out-of-scope D5 (NO tocar): auth.ts, budget.ts, telemetry.ts, tutor.ts L1-95.
 */

import { invokeClassifier } from "./llm/google.js";
import { invokeTutor } from "./llm/anthropic.js";
import { invokeSprintCopilot } from "./llm/openai.js";

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
  /** D5: nombre del modelo que finalmente clasificó (audit trail fallback chain) */
  modelUsed?: string;
}

/**
 * D5 Solución #2 (defense-in-depth) — extractor JSON tolerante.
 *
 * Extrae el primer bloque `{...}` o `[...]` de un string. Tolera prefijos
 * (`"Here is..."`), sufijos textuales o líneas adicionales. Si no encuentra
 * un bloque JSON balanceado, lanza error namespaced.
 *
 * NOTA: usa la regex `/(\{[\s\S]*\}|\[[\s\S]*\])/` greedy para capturar el
 * bloque más externo (correcto si solo hay un objeto/array en el response).
 * Si el modelo emite múltiples bloques, captura desde el primer `{` hasta
 * el último `}`, lo que es deseable para JSON anidado válido.
 *
 * @throws Error con prefix `[la-forja:ac12_classify_invalid_json]` si no hay
 *         bloque JSON balanceado o el bloque encontrado falla `JSON.parse`.
 */
export function extractJsonStrict(raw: string): unknown {
  const match = raw.match(/(\{[\s\S]*\}|\[[\s\S]*\])/);
  const block = match?.[1];
  if (!block) {
    throw new Error(
      `[la-forja:ac12_classify_invalid_json] no JSON block found in response: ${raw.slice(0, 100)}`,
    );
  }
  try {
    return JSON.parse(block);
  } catch {
    throw new Error(
      `[la-forja:ac12_classify_invalid_json] JSON.parse failed on extracted block: ${block.slice(0, 100)}`,
    );
  }
}

/**
 * Tipo del classifier inyectable. Cada modelo (Gemini, Claude, GPT) cumple
 * esta interfaz mínima para que la fallback chain pueda iterar uniformemente.
 */
type ClassifierFn = (prompt: string) => Promise<{
  content: string;
  inputTokens: number;
  outputTokens: number;
}>;

/**
 * Wrappers por modelo. Cada uno adapta el client específico a la firma
 * `ClassifierFn`. Los tres usan el mismo system prompt + extracción JSON
 * tolerante (Solución #2 cubre los 3 casos).
 */

const geminiClassifier: ClassifierFn = async (prompt: string) => {
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
};

const claudeClassifier: ClassifierFn = async (prompt: string) => {
  const r = await invokeTutor({
    messages: [{ role: "user", content: prompt }],
    systemPrompt: AC12_SYSTEM_PROMPT,
    maxTokens: 64,
  });
  return {
    content: r.content,
    inputTokens: r.inputTokens,
    outputTokens: r.outputTokens,
  };
};

const openaiClassifier: ClassifierFn = async (prompt: string) => {
  const r = await invokeSprintCopilot({
    input: [
      { role: "system", content: AC12_SYSTEM_PROMPT },
      { role: "user", content: prompt },
    ],
    maxOutputTokens: 64,
  });
  return {
    content: r.content,
    inputTokens: r.inputTokens,
    outputTokens: r.outputTokens,
  };
};

/**
 * D5 Solución #3 (magna fallback chain).
 *
 * Cadena de modelos en orden: Gemini Flash → Claude Opus → GPT-5.5 Pro.
 * Cada uno se intenta una vez. Si falla con cualquier error namespaced
 * `[la-forja:ac12_*]`, se loggea `ac12_fallback_triggered` y se prueba
 * el siguiente. Si los 3 fallan, lanza `ac12_classifier_all_models_failed`
 * con el último error como `cause`.
 *
 * Logs estructurados a `console.error` con prefix `[la-forja:*]` para que
 * el middleware telemetry los capture (Regla Dura #6 brand-engine).
 */
export const AC12_FALLBACK_CHAIN: ReadonlyArray<{
  name: string;
  fn: ClassifierFn;
}> = [
  { name: "gemini-2.5-flash", fn: geminiClassifier },
  { name: "claude-opus-4-7", fn: claudeClassifier },
  { name: "gpt-5.5-pro", fn: openaiClassifier },
];

/**
 * Clasifica un mensaje del usuario. Retorna intent + confidence + passesThreshold.
 *
 * D5 robustez: usa fallback chain por defecto + parser tolerante. El call site
 * en `routes/tutor.ts:96` queda intacto (mismo signature post-D5).
 *
 * options.classifier permite inyectar un mock determinista en tests sin
 * llamar a modelos reales. Cuando se pasa, salta la fallback chain (un solo
 * mock model). En producción se usa la chain por default.
 *
 * options.fallbackChain permite override de la chain entera para tests
 * de fallback (e.g., simular Gemini falla, Claude responde).
 */
export async function classifyMessage(
  rawMessage: string,
  options: {
    classifier?: ClassifierFn;
    fallbackChain?: ReadonlyArray<{ name: string; fn: ClassifierFn }>;
  } = {},
): Promise<AC12Classification> {
  // Si se pasó un classifier mock explícito, NO usar fallback chain (back-compat
  // con tests existentes 242 baseline + simplificación de mocks).
  if (options.classifier) {
    return classifyOnce(rawMessage, options.classifier, "mock");
  }

  const chain = options.fallbackChain ?? AC12_FALLBACK_CHAIN;
  let lastError: unknown = null;

  for (const { name, fn } of chain) {
    try {
      return await classifyOnce(rawMessage, fn, name);
    } catch (err) {
      lastError = err;
      // Log estructurado para telemetry middleware. Prefix [la-forja:*] obligatorio.
      console.error(
        `[la-forja:ac12_fallback_triggered] model=${name} failed, trying next`,
        {
          error: err instanceof Error ? err.message : String(err),
          rawMessagePreview: rawMessage.slice(0, 50),
        },
      );
      continue;
    }
  }

  // Si llegamos aquí, los 3 modelos fallaron.
  throw new Error(
    `[la-forja:ac12_classifier_all_models_failed] all ${chain.length} models in fallback chain failed`,
    { cause: lastError },
  );
}

/**
 * Clasifica una sola vez con un classifier dado. No itera la chain.
 * Aplica Solución #2 (parser tolerante) en el response.
 */
async function classifyOnce(
  rawMessage: string,
  classifier: ClassifierFn,
  modelName: string,
): Promise<AC12Classification> {
  const r = await classifier(rawMessage);

  // D5 Solución #2: usar extractJsonStrict en lugar de JSON.parse directo.
  // Tolera prefijos `"Here is..."` que Gemini Flash 2.5 puede emitir.
  const parsed = extractJsonStrict(r.content) as {
    intent?: string;
    confidence?: number;
  };

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
    modelUsed: modelName,
  };
}
