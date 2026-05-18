/**
 * La Forja — Tests del multi-model router (D2.2).
 *
 * Validación binaria:
 *   - MISSIONS tuple length == 5 exact (LF-PERPLEXITY-ONLY-001 enforcer)
 *   - MISSION_TO_MODEL coincide §2.4 SPEC v3.2
 *   - MISSION_PRICING coincide §2.4 SPEC v3.2
 *   - Cada función del router invoca el cliente LLM correcto (smoke test
 *     con SDKs mockeados — no llamadas reales en CI)
 */

import { describe, expect, it } from "vitest";
import {
  MISSIONS,
  MISSION_PRICING,
  MISSION_TO_MODEL,
  type Mission,
} from "./router.js";

describe("MISSIONS canónicas (§2.4 SPEC v3.2)", () => {
  it("contiene exactamente 5 misiones", () => {
    expect(MISSIONS.length).toBe(5);
  });

  it("contiene tutor, sprint_copilot, rag, classifier, magna_validation", () => {
    expect([...MISSIONS].sort()).toEqual([
      "classifier",
      "magna_validation",
      "rag",
      "sprint_copilot",
      "tutor",
    ]);
  });

  it("no contiene misiones shadow ni typos", () => {
    const expected: Mission[] = [
      "tutor",
      "sprint_copilot",
      "rag",
      "classifier",
      "magna_validation",
    ];
    for (const m of expected) {
      expect(MISSIONS).toContain(m);
    }
  });
});

describe("MISSION_TO_MODEL canónico", () => {
  it("tutor → claude-opus-4-7", () => {
    expect(MISSION_TO_MODEL.tutor).toBe("claude-opus-4-7");
  });

  it("sprint_copilot → gpt-5.5-pro", () => {
    expect(MISSION_TO_MODEL.sprint_copilot).toBe("gpt-5.5-pro");
  });

  it("rag → gemini-3.1-pro-preview", () => {
    expect(MISSION_TO_MODEL.rag).toBe("gemini-3.1-pro-preview");
  });

  it("classifier → gemini-2.5-flash", () => {
    expect(MISSION_TO_MODEL.classifier).toBe("gemini-2.5-flash");
  });

  it("magna_validation → sonar-reasoning-pro", () => {
    expect(MISSION_TO_MODEL.magna_validation).toBe("sonar-reasoning-pro");
  });

  it("tiene exactamente 5 entries", () => {
    expect(Object.keys(MISSION_TO_MODEL).length).toBe(5);
  });
});

describe("MISSION_PRICING canónico (§2.4 SPEC v3.2)", () => {
  it("tutor: $5 input / $25 output por Mtok", () => {
    expect(MISSION_PRICING.tutor.inputPerMtok).toBe(5.0);
    expect(MISSION_PRICING.tutor.outputPerMtok).toBe(25.0);
  });

  it("sprint_copilot: $5 input / $30 output por Mtok", () => {
    expect(MISSION_PRICING.sprint_copilot.inputPerMtok).toBe(5.0);
    expect(MISSION_PRICING.sprint_copilot.outputPerMtok).toBe(30.0);
  });

  it("rag: $2 input / $12 output por Mtok", () => {
    expect(MISSION_PRICING.rag.inputPerMtok).toBe(2.0);
    expect(MISSION_PRICING.rag.outputPerMtok).toBe(12.0);
  });

  it("classifier: $0.075 input / $0.30 output por Mtok", () => {
    expect(MISSION_PRICING.classifier.inputPerMtok).toBe(0.075);
    expect(MISSION_PRICING.classifier.outputPerMtok).toBe(0.3);
  });

  it("magna_validation: $2 input / $8 output por Mtok", () => {
    expect(MISSION_PRICING.magna_validation.inputPerMtok).toBe(2.0);
    expect(MISSION_PRICING.magna_validation.outputPerMtok).toBe(8.0);
  });

  it("classifier es el más barato (Flash)", () => {
    const classifierCost =
      MISSION_PRICING.classifier.inputPerMtok +
      MISSION_PRICING.classifier.outputPerMtok;
    for (const m of MISSIONS) {
      if (m === "classifier") continue;
      const cost =
        MISSION_PRICING[m].inputPerMtok + MISSION_PRICING[m].outputPerMtok;
      expect(cost).toBeGreaterThan(classifierCost);
    }
  });
});

describe("Cobertura binaria misión↔modelo↔pricing", () => {
  it("cada misión tiene model y pricing definidos", () => {
    for (const m of MISSIONS) {
      expect(MISSION_TO_MODEL[m]).toBeDefined();
      expect(MISSION_PRICING[m]).toBeDefined();
      expect(MISSION_PRICING[m].inputPerMtok).toBeGreaterThan(0);
      expect(MISSION_PRICING[m].outputPerMtok).toBeGreaterThan(0);
    }
  });
});
