import { describe, expect, it } from "vitest";
import { FORJA_TOUR_STEPS, FORJA_TOUR_STEP_COUNT } from "./steps";

/**
 * La Forja — tests del contrato de pasos del tour.
 * Sprint LA-FORJA-001 D3.1.
 *
 * No tocamos JSX. Probamos solo la data: estabilidad de count, ids
 * únicos, no hay placeholders vacíos, los `highlights` realmente
 * existen literal en `body`, etc.
 */

describe("FORJA_TOUR_STEPS — contrato de data", () => {
  it("tiene exactamente 7 pasos", () => {
    expect(FORJA_TOUR_STEP_COUNT).toBe(7);
    expect(FORJA_TOUR_STEPS).toHaveLength(7);
  });

  it("todos los ids son únicos y no vacíos", () => {
    const ids = FORJA_TOUR_STEPS.map((s) => s.id);
    expect(new Set(ids).size).toBe(ids.length);
    for (const id of ids) {
      expect(id).toMatch(/^[a-z0-9-]+$/);
    }
  });

  it("ningún paso tiene title, eyebrow ni cta vacíos", () => {
    for (const step of FORJA_TOUR_STEPS) {
      expect(step.title.trim().length).toBeGreaterThan(0);
      expect(step.eyebrow.trim().length).toBeGreaterThan(0);
      expect(step.cta.trim().length).toBeGreaterThan(0);
    }
  });

  it("cada paso tiene al menos un párrafo no vacío en body", () => {
    for (const step of FORJA_TOUR_STEPS) {
      expect(step.body.length).toBeGreaterThan(0);
      for (const p of step.body) {
        expect(p.trim().length).toBeGreaterThan(0);
      }
    }
  });

  it("cada highlight aparece literal en algún párrafo del body", () => {
    for (const step of FORJA_TOUR_STEPS) {
      if (!step.highlights) continue;
      for (const hl of step.highlights) {
        const exists = step.body.some((p) => p.includes(hl));
        expect(exists, `highlight "${hl}" no está en body de ${step.id}`).toBe(
          true,
        );
      }
    }
  });

  it("eyebrow declara correctamente el orden 'Paso N de 7'", () => {
    FORJA_TOUR_STEPS.forEach((step, i) => {
      expect(step.eyebrow).toContain(`Paso ${i + 1} de 7`);
    });
  });

  it("el último paso tiene CTA distinto a 'Continuar'", () => {
    const last = FORJA_TOUR_STEPS[FORJA_TOUR_STEPS.length - 1];
    expect(last?.cta.toLowerCase()).not.toBe("continuar");
  });
});
