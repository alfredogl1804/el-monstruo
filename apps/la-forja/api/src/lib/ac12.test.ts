/**
 * La Forja — Tests AC12 clasificador semántico (D2.3).
 *
 * Validación binaria:
 *   - threshold canónico 0.7
 *   - 10 frases sinónimas listadas binariamente del SPEC §7
 *   - parsing JSON estructurado
 *   - errores tipados con prefix la-forja:ac12_*
 */

import { describe, expect, it, vi } from "vitest";
import {
  AC12_CANONICAL_CONFUSION_PHRASES,
  AC12_CONFIDENCE_THRESHOLD,
  classifyMessage,
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
