/**
 * La Forja — Tests repository forja_budget (SupabaseBudgetClient real).
 *
 * Sprint LA-FORJA-001 v3.2 — D5.2.
 *
 * Validación binaria:
 *   1. readSpent retorna 0 cuando no hay row (mes nuevo)
 *   2. readSpent parsea NUMERIC string a number (precisión preservada)
 *   3. reserveSpent UPSERT con onConflict=profile_id,period_start
 *   4. adjustSpent clampea a 0 cuando delta haría negativo (CHECK constraint)
 *   5. period_start es siempre día 1 del mes UTC (CHECK constraint)
 *   6. resolveUser=null lanza error explícito [la-forja:budget_unknown_user]
 *   7. errores Supabase propagan con namespace canónico
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { User } from "../env.js";
import {
  SupabaseBudgetClient,
  currentPeriodStart,
} from "./budget.js";
import { _resetProfileIdCache } from "./profiles.js";

const mockMaybeSingle = vi.fn();
const mockEqProfile = vi.fn(() => ({ maybeSingle: mockMaybeSingle }));
const mockEqPeriod = vi.fn(() => ({ eq: mockEqProfile }));
const mockSelect = vi.fn(() => ({ eq: mockEqPeriod }));
const mockUpsertResult = vi.fn();
const mockUpsert = vi.fn(() => mockUpsertResult());
const mockSingleProfile = vi.fn();
const mockSelectProfile = vi.fn(() => ({ single: mockSingleProfile }));
const mockUpsertProfile = vi.fn(() => ({ select: mockSelectProfile }));

const mockFrom = vi.fn((table: string) => {
  if (table === "forja_profiles") {
    return { upsert: mockUpsertProfile };
  }
  // forja_budget
  return {
    select: mockSelect,
    upsert: mockUpsert,
  };
});

vi.mock("../supabase", () => ({
  getSupabase: () => ({ from: mockFrom }),
  _resetSupabaseCache: () => undefined,
}));

const VALID_USER: User = {
  id: "11111111-2222-3333-4444-555555555555",
  email: "alfredo@stub.la-forja.local",
  role: "t1_alfredo",
};

const PROFILE_ID = "aaaa1111-2222-3333-4444-555555555555";

beforeEach(() => {
  vi.clearAllMocks();
  _resetProfileIdCache();
  mockSingleProfile.mockResolvedValue({
    data: { id: PROFILE_ID },
    error: null,
  });
  mockUpsertResult.mockResolvedValue({ error: null });
});

afterEach(() => {
  vi.restoreAllMocks();
});

function makeClient(resolveUser: (id: string) => User | null = () => VALID_USER) {
  return new SupabaseBudgetClient({
    resolveUser,
    nodeEnv: "development",
  });
}

describe("currentPeriodStart()", () => {
  it("retorna día 1 del mes UTC en formato YYYY-MM-DD", () => {
    const fixed = new Date(Date.UTC(2026, 4, 17)); // mayo (idx 4)
    expect(currentPeriodStart(fixed)).toBe("2026-05-01");
  });

  it("zero-pads meses single-digit", () => {
    const fixed = new Date(Date.UTC(2026, 0, 31)); // enero
    expect(currentPeriodStart(fixed)).toBe("2026-01-01");
  });
});

describe("SupabaseBudgetClient.readSpent", () => {
  it("retorna 0 cuando no hay row para el período", async () => {
    mockMaybeSingle.mockResolvedValueOnce({ data: null, error: null });
    const client = makeClient();
    const result = await client.readSpent(VALID_USER.id);
    expect(result).toBe(0);
    expect(mockFrom).toHaveBeenCalledWith("forja_budget");
  });

  it("parsea NUMERIC string a number", async () => {
    mockMaybeSingle.mockResolvedValueOnce({
      data: { spent_usd: "12.345678" },
      error: null,
    });
    const client = makeClient();
    const result = await client.readSpent(VALID_USER.id);
    expect(result).toBeCloseTo(12.345678, 6);
  });

  it("fail-loud con error de Supabase", async () => {
    mockMaybeSingle.mockResolvedValueOnce({
      data: null,
      error: { message: "connection refused" },
    });
    const client = makeClient();
    await expect(client.readSpent(VALID_USER.id)).rejects.toThrow(
      /\[la-forja:budget_read_failed\]/,
    );
  });

  it("rechaza userId no resuelto con error explícito", async () => {
    const client = makeClient(() => null);
    await expect(client.readSpent("unknown")).rejects.toThrow(
      /\[la-forja:budget_unknown_user\]/,
    );
  });
});

describe("SupabaseBudgetClient.reserveSpent", () => {
  it("UPSERT con onConflict=profile_id,period_start", async () => {
    mockMaybeSingle.mockResolvedValueOnce({
      data: { spent_usd: "5.00" },
      error: null,
    });

    const client = makeClient();
    await client.reserveSpent(VALID_USER.id, 0.5);

    expect(mockUpsert).toHaveBeenCalledOnce();
    const [row, opts] = mockUpsert.mock.calls[0]!;
    expect(row).toMatchObject({
      profile_id: PROFILE_ID,
      spent_usd: 5.5,
    });
    expect((row as { period_start: string }).period_start).toMatch(
      /^\d{4}-\d{2}-01$/,
    );
    expect(opts).toEqual({ onConflict: "profile_id,period_start" });
  });
});

describe("SupabaseBudgetClient.adjustSpent", () => {
  it("aplica delta positivo correctamente", async () => {
    mockMaybeSingle.mockResolvedValueOnce({
      data: { spent_usd: "10.00" },
      error: null,
    });
    const client = makeClient();
    await client.adjustSpent(VALID_USER.id, 0.25);
    const row = mockUpsert.mock.calls[0]![0] as { spent_usd: number };
    expect(row.spent_usd).toBeCloseTo(10.25, 6);
  });

  it("clampea a 0 cuando delta haría negativo (CHECK constraint)", async () => {
    mockMaybeSingle.mockResolvedValueOnce({
      data: { spent_usd: "0.10" },
      error: null,
    });
    const client = makeClient();
    await client.adjustSpent(VALID_USER.id, -1.0);
    const row = mockUpsert.mock.calls[0]![0] as { spent_usd: number };
    expect(row.spent_usd).toBe(0);
  });

  it("fail-loud con error en UPSERT", async () => {
    mockMaybeSingle.mockResolvedValueOnce({
      data: { spent_usd: "1.00" },
      error: null,
    });
    mockUpsertResult.mockResolvedValueOnce({
      error: { message: "constraint chk_forja_budget_metrics violated" },
    });
    const client = makeClient();
    await expect(
      client.adjustSpent(VALID_USER.id, 0.5),
    ).rejects.toThrow(/\[la-forja:budget_adjust_failed\]/);
  });
});
