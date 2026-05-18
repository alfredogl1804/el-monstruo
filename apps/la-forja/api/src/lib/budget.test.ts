/**
 * La Forja — Tests motor budget LF-RATE-LIMIT-001 + DSC-LF-003 (D2.3).
 *
 * Validación binaria:
 *   - estimateCost determinista para cada misión §2.4
 *   - preCallCheck bloquea con ForjaBudgetExceededError si supera $50
 *   - postCallCommit ajusta delta correctamente
 *   - reserveSpent + adjustSpent llamados en orden correcto
 */

import { describe, expect, it, vi } from "vitest";
import {
  type BudgetClient,
  FORJA_BUDGET_CAP_USD,
  ForjaBudgetExceededError,
  estimateCost,
  postCallCommit,
  preCallCheck,
  realCost,
} from "./budget.js";

describe("estimateCost (§2.4 SPEC v3.2)", () => {
  it("tutor: 1000 input + 500 output = $0.0175", () => {
    // 1000/1M × $5 + 500/1M × $25 = 0.005 + 0.0125 = 0.0175
    expect(estimateCost(1000, 500, "tutor")).toBeCloseTo(0.0175, 6);
  });

  it("classifier: 1000 input + 100 output = $0.000105 (más barato)", () => {
    // 1000/1M × $0.075 + 100/1M × $0.3 = 0.000075 + 0.00003 = 0.000105
    expect(estimateCost(1000, 100, "classifier")).toBeCloseTo(0.000105, 8);
  });

  it("sprint_copilot: 4000 input + 2000 output = $0.08", () => {
    // 4000/1M × $5 + 2000/1M × $30 = 0.02 + 0.06 = 0.08
    expect(estimateCost(4000, 2000, "sprint_copilot")).toBeCloseTo(0.08, 6);
  });

  it("rag: 10000 input + 1000 output = $0.032", () => {
    // 10000/1M × $2 + 1000/1M × $12 = 0.02 + 0.012 = 0.032
    expect(estimateCost(10000, 1000, "rag")).toBeCloseTo(0.032, 6);
  });

  it("magna_validation: 500 input + 500 output = $0.005", () => {
    // 500/1M × $2 + 500/1M × $8 = 0.001 + 0.004 = 0.005
    expect(estimateCost(500, 500, "magna_validation")).toBeCloseTo(0.005, 6);
  });

  it("realCost == estimateCost con tokens reales", () => {
    expect(realCost(800, 300, "tutor")).toBe(estimateCost(800, 300, "tutor"));
  });
});

describe("preCallCheck", () => {
  function mockClient(currentSpent: number): BudgetClient & {
    reserve: ReturnType<typeof vi.fn>;
    adjust: ReturnType<typeof vi.fn>;
  } {
    const reserve = vi.fn(async () => undefined);
    const adjust = vi.fn(async () => undefined);
    return {
      readSpent: async () => currentSpent,
      reserveSpent: reserve,
      adjustSpent: adjust,
      reserve,
      adjust,
    };
  }

  it("retorna estimated y reserva atómicamente cuando hay budget", async () => {
    const client = mockClient(10.0);
    const estimated = await preCallCheck(
      client,
      "user-1",
      "tutor",
      1000,
      500,
    );
    expect(estimated).toBeCloseTo(0.0175, 6);
    expect(client.reserve).toHaveBeenCalledWith("user-1", estimated);
    expect(client.adjust).not.toHaveBeenCalled();
  });

  it("lanza ForjaBudgetExceededError si excede cap $50", async () => {
    const client = mockClient(49.99);
    await expect(
      preCallCheck(client, "user-1", "sprint_copilot", 100_000, 50_000),
    ).rejects.toThrow(ForjaBudgetExceededError);
  });

  it("permite exactamente igual a cap (boundary)", async () => {
    const client = mockClient(FORJA_BUDGET_CAP_USD - 0.0175);
    await expect(
      preCallCheck(client, "user-1", "tutor", 1000, 500),
    ).resolves.toBeCloseTo(0.0175, 6);
  });

  it("rechaza al pasar el cap por 1 cent", async () => {
    const client = mockClient(FORJA_BUDGET_CAP_USD - 0.0001);
    await expect(
      preCallCheck(client, "user-1", "tutor", 1000, 500),
    ).rejects.toThrow(/budget_cap_exceeded/);
  });

  it("primer uso del mes: spent=0", async () => {
    const client = mockClient(0);
    const est = await preCallCheck(client, "u", "classifier", 100, 50);
    expect(est).toBeCloseTo(0.0000225, 8);
    expect(client.reserve).toHaveBeenCalledWith("u", est);
  });
});

describe("postCallCommit", () => {
  it("ajusta delta cuando los reales son menores a la estimación", async () => {
    const adjust = vi.fn(async () => undefined);
    const client: BudgetClient = {
      readSpent: async () => 0,
      reserveSpent: async () => undefined,
      adjustSpent: adjust,
    };
    const estimated = estimateCost(1000, 500, "tutor"); // 0.0175
    const result = await postCallCommit(
      client,
      "u",
      "tutor",
      800,
      300,
      estimated,
    );
    // real = 800/1M × $5 + 300/1M × $25 = 0.004 + 0.0075 = 0.0115
    expect(result.realCost).toBeCloseTo(0.0115, 6);
    expect(result.delta).toBeCloseTo(0.0115 - 0.0175, 6);
    expect(adjust).toHaveBeenCalledWith("u", result.delta);
  });

  it("ajusta delta positivo cuando los reales son MAYORES (improbable pero posible)", async () => {
    const adjust = vi.fn(async () => undefined);
    const client: BudgetClient = {
      readSpent: async () => 0,
      reserveSpent: async () => undefined,
      adjustSpent: adjust,
    };
    const estimated = estimateCost(500, 100, "tutor"); // 0.005
    const result = await postCallCommit(
      client,
      "u",
      "tutor",
      1000,
      500,
      estimated,
    );
    expect(result.delta).toBeGreaterThan(0);
    expect(adjust).toHaveBeenCalledWith("u", result.delta);
  });
});

describe("ForjaBudgetExceededError", () => {
  it("incluye userId, current y estimated en mensaje", () => {
    const e = new ForjaBudgetExceededError("u-123", 49.99, 0.5);
    expect(e.message).toContain("budget_cap_exceeded");
    expect(e.message).toContain("u-123");
    expect(e.message).toContain("49.9900");
    expect(e.message).toContain("0.5000");
  });
});
