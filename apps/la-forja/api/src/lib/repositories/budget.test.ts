/**
 * La Forja — Tests repository forja_budget (SupabaseBudgetClient real).
 *
 * Sprint LA-FORJA-001 v3.2 — D5.3 (cierre L_B1 declarada D5.2).
 *
 * Validación binaria:
 *   1. readSpent retorna 0 cuando no hay row (mes nuevo)
 *   2. readSpent parsea NUMERIC string a number (precisión preservada)
 *   3. reserveSpent invoca rpc('rpc_increment_budget') con p_delta=estimated
 *   4. adjustSpent invoca rpc('rpc_increment_budget') con p_delta=delta
 *      (clamp a 0 lo aplica el lado servidor — RPC GREATEST(0, ...))
 *   5. period_start es siempre día 1 del mes UTC (CHECK constraint)
 *   6. resolveUser=null lanza error explícito [la-forja:budget_unknown_user]
 *   7. errores Supabase RPC propagan con namespace canónico
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
const mockRpcResult = vi.fn();
const mockRpc = vi.fn((_name: string, _args: unknown) => mockRpcResult());
const mockSingleProfile = vi.fn();
const mockSelectProfile = vi.fn(() => ({ single: mockSingleProfile }));
const mockUpsertProfile = vi.fn(() => ({ select: mockSelectProfile }));

const mockFrom = vi.fn((table: string) => {
  if (table === "forja_profiles") {
    return { upsert: mockUpsertProfile };
  }
  // forja_budget — solo SELECT (las escrituras van por rpc)
  return {
    select: mockSelect,
  };
});

vi.mock("../supabase", () => ({
  getSupabase: () => ({ from: mockFrom, rpc: mockRpc }),
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
  mockRpcResult.mockResolvedValue({ data: null, error: null });
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

describe("SupabaseBudgetClient.reserveSpent (D5.3 RPC atómico)", () => {
  it("invoca rpc('rpc_increment_budget') con p_delta=estimated", async () => {
    const client = makeClient();
    await client.reserveSpent(VALID_USER.id, 0.5);

    expect(mockRpc).toHaveBeenCalledOnce();
    const [name, args] = mockRpc.mock.calls[0]!;
    expect(name).toBe("rpc_increment_budget");
    expect(args).toMatchObject({
      p_profile_id: PROFILE_ID,
      p_delta: 0.5,
    });
    expect((args as { p_period_start: string }).p_period_start).toMatch(
      /^\d{4}-\d{2}-01$/,
    );
  });

  it("NO invoca readSpent antes de la RPC (atomicidad single-roundtrip)", async () => {
    const client = makeClient();
    await client.reserveSpent(VALID_USER.id, 0.25);

    // SELECT spent_usd no debe invocarse durante reserveSpent: la RPC hace
    // todo en un solo roundtrip atómico.
    expect(mockSelect).not.toHaveBeenCalled();
    expect(mockRpc).toHaveBeenCalledOnce();
  });

  it("fail-loud con error de RPC", async () => {
    mockRpcResult.mockResolvedValueOnce({
      data: null,
      error: { message: "function rpc_increment_budget does not exist" },
    });
    const client = makeClient();
    await expect(client.reserveSpent(VALID_USER.id, 0.5)).rejects.toThrow(
      /\[la-forja:budget_reserve_failed\]/,
    );
  });
});

describe("SupabaseBudgetClient.adjustSpent (D5.3 RPC atómico)", () => {
  it("invoca rpc('rpc_increment_budget') con delta positivo", async () => {
    const client = makeClient();
    await client.adjustSpent(VALID_USER.id, 0.25);

    expect(mockRpc).toHaveBeenCalledOnce();
    const [name, args] = mockRpc.mock.calls[0]!;
    expect(name).toBe("rpc_increment_budget");
    expect(args).toMatchObject({
      p_profile_id: PROFILE_ID,
      p_delta: 0.25,
    });
  });

  it("invoca rpc con delta negativo (rollback)", async () => {
    const client = makeClient();
    await client.adjustSpent(VALID_USER.id, -1.0);

    // Clamp a 0 lo aplica la RPC server-side via GREATEST(0, ...).
    // El cliente solo pasa el delta tal cual.
    expect(mockRpc).toHaveBeenCalledOnce();
    const [, args] = mockRpc.mock.calls[0]!;
    expect((args as { p_delta: number }).p_delta).toBe(-1.0);
  });

  it("fail-loud con error de RPC en adjustSpent", async () => {
    mockRpcResult.mockResolvedValueOnce({
      data: null,
      error: { message: "constraint chk_forja_budget_metrics violated" },
    });
    const client = makeClient();
    await expect(
      client.adjustSpent(VALID_USER.id, 0.5),
    ).rejects.toThrow(/\[la-forja:budget_adjust_failed\]/);
  });
});
