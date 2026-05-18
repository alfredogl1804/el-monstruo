/**
 * La Forja — Tests AC12 clasificador semántico (D2.3 + D5).
 *
 * Validación binaria:
 *   - threshold canónico 0.7
 *   - 10 frases sinónimas listadas binariamente del SPEC §7
 *   - parsing JSON estructurado tolerante a prefijos (D5 #2)
 *   - fallback chain Gemini → Claude → GPT-5.5 (D5 #3)
 *   - errores tipados con prefix la-forja:ac12_*
 *   - regresión binaria F2 (Gemini "Here is..." prefix)
 */

import { describe, expect, it, vi } from "vitest";
import {
  AC12_CANONICAL_CONFUSION_PHRASES,
  AC12_CONFIDENCE_THRESHOLD,
  classifyMessage,
  extractJsonStrict,
} from "./ac12.js";

function mockClassifier(intent: string, confidence: number) {
  return vi.fn(async (_prompt: string) => ({
    content: JSON.stringify({ intent, confidence }),
    inputTokens: 50,
    outputTokens: 10,
  }));
}

describe("AC12 constantes canónicas (§7 SPEC v3.2)", () => {
  it("threshold es exactamente 0.7", () => {
    expect(AC12_CONFIDENCE_THRESHOLD).toBe(0.7);
  });

  it("hay exactamente 10 frases sinónimas canónicas", () => {
    expect(AC12_CANONICAL_CONFUSION_PHRASES.length).toBe(10);
  });

  it("incluye 'no entiendo' (string match v3.1 retrocompat)", () => {
    expect(AC12_CANONICAL_CONFUSION_PHRASES).toContain("no entiendo");
  });
});

describe("classifyMessage", () => {
  it("retorna passesThreshold=true si confusion_detected con 0.85", async () => {
    const classifier = mockClassifier("confusion_detected", 0.85);
    const r = await classifyMessage("no entiendo", { classifier });
    expect(r.intent).toBe("confusion_detected");
    expect(r.confidence).toBe(0.85);
    expect(r.passesThreshold).toBe(true);
  });

  it("retorna passesThreshold=false si confidence < 0.7", async () => {
    const classifier = mockClassifier("confusion_detected", 0.5);
    const r = await classifyMessage("texto ambiguo", { classifier });
    expect(r.passesThreshold).toBe(false);
  });

  it("retorna passesThreshold=true en boundary 0.7", async () => {
    const classifier = mockClassifier("confusion_detected", 0.7);
    const r = await classifyMessage("muy abstracto", { classifier });
    expect(r.passesThreshold).toBe(true);
  });

  it("retorna passesThreshold=false si intent es no_confusion", async () => {
    const classifier = mockClassifier("no_confusion", 0.99);
    const r = await classifyMessage("Gracias por la respuesta", { classifier });
    expect(r.passesThreshold).toBe(false);
  });

  it("propaga inputTokens y outputTokens del classifier", async () => {
    const classifier = mockClassifier("confusion_detected", 0.8);
    const r = await classifyMessage("wat", { classifier });
    expect(r.inputTokens).toBe(50);
    expect(r.outputTokens).toBe(10);
  });

  it("incluye rawMessage en el resultado para auditoría telemetry", async () => {
    const classifier = mockClassifier("confusion_detected", 0.9);
    const r = await classifyMessage("explícame de nuevo", { classifier });
    expect(r.rawMessage).toBe("explícame de nuevo");
  });
});

describe("classifyMessage — errores tipados", () => {
  it("falla con ac12_classify_invalid_json en respuesta no-JSON", async () => {
    const classifier = vi.fn(async () => ({
      content: "this is not json",
      inputTokens: 5,
      outputTokens: 5,
    }));
    await expect(
      classifyMessage("test", { classifier }),
    ).rejects.toThrow(/ac12_classify_invalid_json/);
  });

  it("falla con ac12_classify_invalid_intent en intent fuera del enum", async () => {
    const classifier = vi.fn(async () => ({
      content: JSON.stringify({ intent: "maybe_confused", confidence: 0.8 }),
      inputTokens: 5,
      outputTokens: 5,
    }));
    await expect(
      classifyMessage("test", { classifier }),
    ).rejects.toThrow(/ac12_classify_invalid_intent/);
  });

  it("falla con ac12_classify_invalid_confidence si está fuera de [0,1]", async () => {
    const classifier = vi.fn(async () => ({
      content: JSON.stringify({
        intent: "confusion_detected",
        confidence: 1.5,
      }),
      inputTokens: 5,
      outputTokens: 5,
    }));
    await expect(
      classifyMessage("test", { classifier }),
    ).rejects.toThrow(/ac12_classify_invalid_confidence/);
  });
});

describe("AC12 — las 10 frases sinónimas con classifier mock determinista", () => {
  // Mock que SIMULA Gemini respondiendo confidence>=0.7 para las 10 frases canónicas.
  // El test real contra Gemini se hace en D5 con AC12_CANONICAL_CONFUSION_PHRASES
  // como golden set obligatorio (AC §7 SPEC).
  const goldenClassifier = vi.fn(async (prompt: string) => {
    const isConfusion = AC12_CANONICAL_CONFUSION_PHRASES.some((p) =>
      prompt.toLowerCase().includes(p.toLowerCase()),
    );
    return {
      content: JSON.stringify({
        intent: isConfusion ? "confusion_detected" : "no_confusion",
        confidence: isConfusion ? 0.85 : 0.95,
      }),
      inputTokens: 50,
      outputTokens: 10,
    };
  });

  for (const phrase of AC12_CANONICAL_CONFUSION_PHRASES) {
    it(`«${phrase}» → confusion_detected con passesThreshold=true`, async () => {
      const r = await classifyMessage(phrase, { classifier: goldenClassifier });
      expect(r.intent).toBe("confusion_detected");
      expect(r.confidence).toBeGreaterThanOrEqual(0.7);
      expect(r.passesThreshold).toBe(true);
    });
  }
});

// ============================================================================
// D5-TUTOR-CLASSIFIER-ROBUSTNESS-001 — 4 tests nuevos post-F2
// ============================================================================

describe("D5 #2 — extractJsonStrict (parser tolerante a prefijos)", () => {
  it("REGRESIÓN F2: extrae JSON con prefijo 'Here is...' tipo Gemini Flash", () => {
    const raw = 'Here is the classification:\n{"intent":"confusion_detected","confidence":0.95}';
    const parsed = extractJsonStrict(raw) as {
      intent: string;
      confidence: number;
    };
    expect(parsed.intent).toBe("confusion_detected");
    expect(parsed.confidence).toBe(0.95);
  });

  it("extrae JSON con sufijo de texto", () => {
    const raw = '{"intent":"no_confusion","confidence":0.5}\n\nThanks for asking!';
    const parsed = extractJsonStrict(raw) as {
      intent: string;
      confidence: number;
    };
    expect(parsed.intent).toBe("no_confusion");
  });

  it("extrae JSON con markdown code fence ```json ... ```", () => {
    const raw = '```json\n{"intent":"confusion_detected","confidence":0.8}\n```';
    const parsed = extractJsonStrict(raw) as {
      intent: string;
      confidence: number;
    };
    expect(parsed.intent).toBe("confusion_detected");
    expect(parsed.confidence).toBe(0.8);
  });

  it("falla con ac12_classify_invalid_json si no hay bloque JSON", () => {
    expect(() => extractJsonStrict("plain text without any braces")).toThrow(
      /ac12_classify_invalid_json/,
    );
  });

  it("falla con ac12_classify_invalid_json si el bloque encontrado no es JSON válido", () => {
    expect(() => extractJsonStrict("Result: {esto no es json}")).toThrow(
      /ac12_classify_invalid_json/,
    );
  });
});

describe("D5 #2 — classifyMessage con respuestas Gemini ruidosas (regresión F2)", () => {
  it("REGRESIÓN F2 binaria: prefijo 'Here is' + JSON válido → clasifica OK", async () => {
    // Reproduce literalmente lo que Gemini Flash 2.5 emitió en producción 2026-05-18.
    const noisyClassifier = vi.fn(async () => ({
      content:
        'Here is the classification:\n{"intent":"confusion_detected","confidence":0.92}',
      inputTokens: 60,
      outputTokens: 20,
    }));
    const r = await classifyMessage("no entiendo", { classifier: noisyClassifier });
    expect(r.intent).toBe("confusion_detected");
    expect(r.confidence).toBe(0.92);
    expect(r.passesThreshold).toBe(true);
  });

  it("clasifica OK con respuesta envuelta en code fence", async () => {
    const fencedClassifier = vi.fn(async () => ({
      content: '```json\n{"intent":"no_confusion","confidence":0.6}\n```',
      inputTokens: 55,
      outputTokens: 18,
    }));
    const r = await classifyMessage("Gracias", { classifier: fencedClassifier });
    expect(r.intent).toBe("no_confusion");
    expect(r.confidence).toBe(0.6);
    expect(r.passesThreshold).toBe(false);
  });
});

describe("D5 #3 — fallback chain Gemini → Claude → GPT-5.5", () => {
  it("usa el primer modelo de la chain si responde OK", async () => {
    const geminiOk = vi.fn(async () => ({
      content: JSON.stringify({ intent: "confusion_detected", confidence: 0.9 }),
      inputTokens: 50,
      outputTokens: 12,
    }));
    const claudeNeverCalled = vi.fn(async () => {
      throw new Error("Claude debería NO ser llamado");
    });
    const gptNeverCalled = vi.fn(async () => {
      throw new Error("GPT debería NO ser llamado");
    });

    const r = await classifyMessage("test", {
      fallbackChain: [
        { name: "gemini-mock", fn: geminiOk },
        { name: "claude-mock", fn: claudeNeverCalled },
        { name: "gpt-mock", fn: gptNeverCalled },
      ],
    });

    expect(r.intent).toBe("confusion_detected");
    expect(r.modelUsed).toBe("gemini-mock");
    expect(geminiOk).toHaveBeenCalledTimes(1);
    expect(claudeNeverCalled).not.toHaveBeenCalled();
    expect(gptNeverCalled).not.toHaveBeenCalled();
  });

  it("salta a Claude si Gemini falla con ac12_classify_invalid_json", async () => {
    const geminiFails = vi.fn(async () => ({
      content: "Here is, but no JSON at all",
      inputTokens: 30,
      outputTokens: 10,
    }));
    const claudeOk = vi.fn(async () => ({
      content: JSON.stringify({ intent: "confusion_detected", confidence: 0.88 }),
      inputTokens: 40,
      outputTokens: 15,
    }));
    const gptNeverCalled = vi.fn(async () => {
      throw new Error("GPT debería NO ser llamado");
    });

    const r = await classifyMessage("test", {
      fallbackChain: [
        { name: "gemini-fail", fn: geminiFails },
        { name: "claude-ok", fn: claudeOk },
        { name: "gpt-never", fn: gptNeverCalled },
      ],
    });

    expect(r.intent).toBe("confusion_detected");
    expect(r.confidence).toBe(0.88);
    expect(r.modelUsed).toBe("claude-ok");
    expect(geminiFails).toHaveBeenCalledTimes(1);
    expect(claudeOk).toHaveBeenCalledTimes(1);
    expect(gptNeverCalled).not.toHaveBeenCalled();
  });

  it("salta hasta GPT-5.5 si Gemini Y Claude fallan", async () => {
    const geminiFails = vi.fn(async () => ({
      content: "garbage no json",
      inputTokens: 30,
      outputTokens: 10,
    }));
    const claudeFails = vi.fn(async () => ({
      content: JSON.stringify({ intent: "invalid_intent", confidence: 0.5 }),
      inputTokens: 35,
      outputTokens: 12,
    }));
    const gptOk = vi.fn(async () => ({
      content: JSON.stringify({ intent: "no_confusion", confidence: 0.95 }),
      inputTokens: 45,
      outputTokens: 14,
    }));

    const r = await classifyMessage("test", {
      fallbackChain: [
        { name: "gemini-fail", fn: geminiFails },
        { name: "claude-fail", fn: claudeFails },
        { name: "gpt-ok", fn: gptOk },
      ],
    });

    expect(r.intent).toBe("no_confusion");
    expect(r.modelUsed).toBe("gpt-ok");
    expect(geminiFails).toHaveBeenCalledTimes(1);
    expect(claudeFails).toHaveBeenCalledTimes(1);
    expect(gptOk).toHaveBeenCalledTimes(1);
  });

  it("falla con ac12_classifier_all_models_failed si los 3 modelos fallan", async () => {
    const allFail = vi.fn(async () => ({
      content: "no json en absoluto",
      inputTokens: 20,
      outputTokens: 8,
    }));

    await expect(
      classifyMessage("test", {
        fallbackChain: [
          { name: "gemini-fail", fn: allFail },
          { name: "claude-fail", fn: allFail },
          { name: "gpt-fail", fn: allFail },
        ],
      }),
    ).rejects.toThrow(/ac12_classifier_all_models_failed/);

    expect(allFail).toHaveBeenCalledTimes(3);
  });
});
