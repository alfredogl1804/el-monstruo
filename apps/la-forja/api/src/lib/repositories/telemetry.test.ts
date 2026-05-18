/**
 * La Forja — Tests repository forja_telemetry (SupabaseTelemetryClient real).
 *
 * Sprint LA-FORJA-001 v3.2 — D5.2.
 *
 * Validación binaria del mapping vocabulary TS → SQL whitelist (caveat P2):
 *   - simplification_requested → simplification_requested
 *   - confusion_detected       → confusion_detected
 *   - turn_abandoned           → abandonment_detected
 *   - sprint_completed         → completion_signal (subject="sprint")
 *   - sprint_started           → other (subject="sprint_started")
 *   - puerta_invoked           → other (subject="puerta_invoked")
 *   - budget_exceeded          → budget_cap_hit
 *   - magna_validation_used    → other (subject="magna_validation_used")
 *
 * Validación binaria fail-soft:
 *   - resolver retorna null → recordEvent NO throw, log warn
 *   - error en INSERT       → recordEvent NO throw, log warn
 *   - excepción inesperada  → recordEvent NO throw, log warn
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { User } from "../env";
import type { TelemetryEventType } from "../telemetry";
import { SupabaseTelemetryClient } from "./telemetry";
import { _resetProfileIdCache } from "./profiles";

const mockInsertResult = vi.fn();
const mockInsert = vi.fn(() => mockInsertResult());

const mockSingleProfile = vi.fn();
const mockSelectProfile = vi.fn(() => ({ single: mockSingleProfile }));
const mockUpsertProfile = vi.fn(() => ({ select: mockSelectProfile }));

const mockFrom = vi.fn((table: string) => {
  if (table === "forja_profiles") {
    return { upsert: mockUpsertProfile };
  }
  return { insert: mockInsert };
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
  mockInsertResult.mockResolvedValue({ error: null });
});

afterEach(() => {
  vi.restoreAllMocks();
});

function makeClient(resolveUser: (id: string) => User | null = () => VALID_USER) {
  return new SupabaseTelemetryClient({
    resolveUser,
    nodeEnv: "development",
  });
}

describe("SupabaseTelemetryClient — mapping vocabulary TS→SQL (P2)", () => {
  const cases: Array<{
    tsType: TelemetryEventType;
    sqlEvent: string;
    sqlSubject: string | null;
  }> = [
    {
      tsType: "confusion_detected",
      sqlEvent: "confusion_detected",
      sqlSubject: null,
    },
    {
      tsType: "simplification_requested",
      sqlEvent: "simplification_requested",
      sqlSubject: null,
    },
    {
      tsType: "turn_abandoned",
      sqlEvent: "abandonment_detected",
      sqlSubject: null,
    },
    {
      tsType: "sprint_completed",
      sqlEvent: "completion_signal",
      sqlSubject: "sprint",
    },
    {
      tsType: "sprint_started",
      sqlEvent: "other",
      sqlSubject: "sprint_started",
    },
    {
      tsType: "puerta_invoked",
      sqlEvent: "other",
      sqlSubject: "puerta_invoked",
    },
    {
      tsType: "budget_exceeded",
      sqlEvent: "budget_cap_hit",
      sqlSubject: null,
    },
    {
      tsType: "magna_validation_used",
      sqlEvent: "other",
      sqlSubject: "magna_validation_used",
    },
  ];

  for (const { tsType, sqlEvent, sqlSubject } of cases) {
    it(`mapea ${tsType} → event=${sqlEvent} subject=${sqlSubject ?? "null"}`, async () => {
      const client = makeClient();
      await client.recordEvent({ userId: VALID_USER.id, type: tsType });

      expect(mockInsert).toHaveBeenCalledOnce();
      const row = mockInsert.mock.calls[0]![0] as {
        event: string;
        subject: string | null;
        profile_id: string;
        metadata: { ts_type: string };
      };
      expect(row.event).toBe(sqlEvent);
      expect(row.subject).toBe(sqlSubject);
      expect(row.profile_id).toBe(PROFILE_ID);
      expect(row.metadata.ts_type).toBe(tsType);
    });
  }
});

describe("SupabaseTelemetryClient — fail-soft binario", () => {
  it("resolveUser=null no throw, log warn", async () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    const client = makeClient(() => null);

    await expect(
      client.recordEvent({ userId: "ghost", type: "confusion_detected" }),
    ).resolves.toBeUndefined();

    expect(warnSpy).toHaveBeenCalledOnce();
    expect(warnSpy.mock.calls[0]![0]).toMatch(
      /\[la-forja:telemetry_unresolved_user\]/,
    );
  });

  it("error en INSERT no throw, log warn", async () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    mockInsertResult.mockResolvedValueOnce({
      error: { message: "schema drift" },
    });
    const client = makeClient();

    await expect(
      client.recordEvent({ userId: VALID_USER.id, type: "confusion_detected" }),
    ).resolves.toBeUndefined();

    expect(warnSpy).toHaveBeenCalledOnce();
    expect(warnSpy.mock.calls[0]![0]).toMatch(
      /\[la-forja:telemetry_insert_failed\]/,
    );
  });

  it("excepción inesperada no throw, log warn", async () => {
    const warnSpy = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    mockSingleProfile.mockRejectedValueOnce(new Error("network down"));
    const client = makeClient();

    await expect(
      client.recordEvent({ userId: VALID_USER.id, type: "puerta_invoked" }),
    ).resolves.toBeUndefined();

    expect(warnSpy).toHaveBeenCalledOnce();
    expect(warnSpy.mock.calls[0]![0]).toMatch(
      /\[la-forja:telemetry_unexpected_error\]/,
    );
  });
});
