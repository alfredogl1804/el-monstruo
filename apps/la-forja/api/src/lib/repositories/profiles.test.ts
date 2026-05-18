/**
 * La Forja — Tests repository forja_profiles.
 *
 * Sprint LA-FORJA-001 v3.2 — D5.2.
 *
 * Validación binaria del contrato `resolveProfileId`:
 *   1. UPSERT idempotente con ON CONFLICT (google_sub) — sin duplicados
 *   2. Mapping User → google_sub: production usa user.id directo (Google sub),
 *      development|test usa prefijo `dev-stub:<uuid>` para no chocar con subs reales
 *   3. Cache local proceso reduce round-trips (segundo lookup no toca DB)
 *   4. Fail-loud: error de Supabase propaga con mensaje canónico [la-forja:profiles_upsert_failed]
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { User } from "../env";
import { resolveProfileId, _resetProfileIdCache } from "./profiles";

// Mock del cliente Supabase. El singleton lazy lee env la primera vez,
// pero como interceptamos `getSupabase` retornamos un mock con `.from(...)`.
const mockSingle = vi.fn();
const mockSelect = vi.fn(() => ({ single: mockSingle }));
const mockUpsert = vi.fn(() => ({ select: mockSelect }));
const mockFrom = vi.fn(() => ({ upsert: mockUpsert }));

vi.mock("../supabase", () => ({
  getSupabase: () => ({ from: mockFrom }),
  _resetSupabaseCache: () => undefined,
}));

beforeEach(() => {
  vi.clearAllMocks();
  _resetProfileIdCache();
});

afterEach(() => {
  vi.restoreAllMocks();
});

const VALID_USER: User = {
  id: "11111111-2222-3333-4444-555555555555",
  email: "alfredo@stub.la-forja.local",
  role: "t1_alfredo",
};

describe("resolveProfileId", () => {
  it("UPSERT con google_sub prefijado dev-stub: en NODE_ENV=development", async () => {
    mockSingle.mockResolvedValueOnce({
      data: { id: "aaaa1111-2222-3333-4444-555555555555" },
      error: null,
    });

    const result = await resolveProfileId(VALID_USER, "development");

    expect(result).toBe("aaaa1111-2222-3333-4444-555555555555");
    expect(mockFrom).toHaveBeenCalledWith("forja_profiles");
    const upsertArgs = mockUpsert.mock.calls[0]![0] as { google_sub: string };
    expect(upsertArgs.google_sub).toBe(`dev-stub:${VALID_USER.id}`);
    expect(mockUpsert.mock.calls[0]![1]).toEqual({
      onConflict: "google_sub",
      ignoreDuplicates: false,
    });
  });

  it("UPSERT con user.id directo en NODE_ENV=production (Google sub real)", async () => {
    mockSingle.mockResolvedValueOnce({
      data: { id: "bbbb1111-2222-3333-4444-555555555555" },
      error: null,
    });

    await resolveProfileId(VALID_USER, "production");

    const upsertArgs = mockUpsert.mock.calls[0]![0] as { google_sub: string };
    expect(upsertArgs.google_sub).toBe(VALID_USER.id);
  });

  it("cache local evita un segundo round-trip a Supabase", async () => {
    mockSingle.mockResolvedValueOnce({
      data: { id: "cccc1111-2222-3333-4444-555555555555" },
      error: null,
    });

    const a = await resolveProfileId(VALID_USER, "development");
    const b = await resolveProfileId(VALID_USER, "development");

    expect(a).toBe(b);
    expect(mockFrom).toHaveBeenCalledTimes(1);
  });

  it("fail-loud con error de Supabase", async () => {
    mockSingle.mockResolvedValueOnce({
      data: null,
      error: { message: "RLS denied: profile_id mismatch" },
    });

    await expect(
      resolveProfileId(VALID_USER, "development"),
    ).rejects.toThrow(/\[la-forja:profiles_upsert_failed\]/);
  });
});
