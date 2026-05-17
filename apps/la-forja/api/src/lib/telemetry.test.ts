/**
 * La Forja — Tests telemetry stub (LF-TELEMETRY-MANDATORY-001, D2.3).
 *
 * Validación binaria:
 *   - 8 tipos de eventos canónicos del SPEC §7
 *   - interface estable (recordEvent retorna Promise<void>)
 *   - inyectabilidad de cliente vía _setTelemetryClient (D5 swap)
 *   - structured logging legible
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  StdoutTelemetryClient,
  type TelemetryClient,
  type TelemetryEvent,
  _setTelemetryClient,
  getTelemetryClient,
  recordEvent,
} from "./telemetry";

beforeEach(() => {
  _setTelemetryClient(null);
});

afterEach(() => {
  vi.restoreAllMocks();
  _setTelemetryClient(null);
});

describe("StdoutTelemetryClient", () => {
  it("emite a stdout con prefix la-forja:telemetry", async () => {
    const logSpy = vi.spyOn(console, "log").mockImplementation(() => undefined);
    const client = new StdoutTelemetryClient();
    await client.recordEvent({
      userId: "u-123",
      type: "confusion_detected",
      confidence: 0.85,
    });
    expect(logSpy).toHaveBeenCalledTimes(1);
    const line = logSpy.mock.calls[0]![0] as string;
    expect(line).toMatch(/^\[la-forja:telemetry\] /);
    const json = JSON.parse(line.replace("[la-forja:telemetry] ", ""));
    expect(json.app).toBe("la-forja");
    expect(json.userId).toBe("u-123");
    expect(json.type).toBe("confusion_detected");
    expect(json.confidence).toBe(0.85);
    expect(typeof json.ts).toBe("string");
  });
});

describe("getTelemetryClient", () => {
  it("retorna singleton consistente", () => {
    const a = getTelemetryClient();
    const b = getTelemetryClient();
    expect(a).toBe(b);
  });

  it("permite inyectar cliente custom para D5 swap", async () => {
    const custom: TelemetryClient = {
      recordEvent: vi.fn(async () => undefined),
    };
    _setTelemetryClient(custom);
    expect(getTelemetryClient()).toBe(custom);
    await recordEvent({ userId: "u", type: "sprint_started" });
    expect(custom.recordEvent).toHaveBeenCalledOnce();
  });
});

describe("recordEvent — los 8 tipos canónicos del SPEC §7", () => {
  const canonicalTypes: TelemetryEvent["type"][] = [
    "simplification_requested",
    "confusion_detected",
    "turn_abandoned",
    "sprint_completed",
    "sprint_started",
    "puerta_invoked",
    "budget_exceeded",
    "magna_validation_used",
  ];

  for (const type of canonicalTypes) {
    it(`acepta type='${type}'`, async () => {
      const captured: TelemetryEvent[] = [];
      _setTelemetryClient({
        recordEvent: async (e) => {
          captured.push(e);
        },
      });
      await recordEvent({ userId: "u", type });
      expect(captured.length).toBe(1);
      expect(captured[0]!.type).toBe(type);
    });
  }
});
