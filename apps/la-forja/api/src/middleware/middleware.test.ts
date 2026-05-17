/**
 * La Forja — Tests middleware (D2.5).
 *
 * Validación binaria:
 *   - auth stub: 401 si falta x-user-id, 401 si UUID inválido, 200 si OK
 *   - budget guard: 429 si excede cap $50, setea budgetEstimated si OK
 *   - telemetry: setea x-request-id, propaga si viene del cliente
 */

import { Hono } from "hono";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { _resetEnvCache, type User } from "../lib/env";
import {
  type BudgetClient,
  FORJA_BUDGET_CAP_USD,
} from "../lib/budget";
import {
  _setTelemetryClient,
  type TelemetryClient,
  type TelemetryEvent,
} from "../lib/telemetry";
import { forjaAuthStub, type ForjaAuthContext } from "./auth";
import { forjaBudgetGuard, type ForjaBudgetContext } from "./budget";
import { forjaTelemetry, type ForjaTelemetryContext } from "./telemetry";

const VALID_ENV: Record<string, string> = {
  MANUS_API_KEY_GOOGLE: "x",
  MANUS_API_KEY_APPLE: "x",
  ANTHROPIC_API_KEY: "x",
  OPENAI_API_KEY: "x",
  GEMINI_API_KEY: "x",
  SONAR_API_KEY: "x",
  SUPABASE_URL: "https://test.supabase.co",
  SUPABASE_SERVICE_KEY: "x",
  LANGFUSE_PUBLIC_KEY: "x",
  LANGFUSE_SECRET_KEY: "x",
  DEV_USER_ROLE: "t1_alfredo",
};

const VALID_UUID = "11111111-2222-3333-4444-555555555555";

let savedEnv: NodeJS.ProcessEnv;

beforeEach(() => {
  savedEnv = { ...process.env };
  _resetEnvCache();
  Object.assign(process.env, VALID_ENV);
});

afterEach(() => {
  process.env = savedEnv;
  _resetEnvCache();
  _setTelemetryClient(null);
  vi.restoreAllMocks();
});

describe("forjaAuthStub", () => {
  it("rechaza con 401 si falta x-user-id", async () => {
    const app = new Hono<ForjaAuthContext>();
    app.use("*", forjaAuthStub());
    app.get("/x", (c) => c.json({ user: c.var.user }));

    const res = await app.request("/x");
    expect(res.status).toBe(401);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("auth_missing_user_id");
  });

  it("rechaza con 401 si x-user-id no es UUID", async () => {
    const app = new Hono<ForjaAuthContext>();
    app.use("*", forjaAuthStub());
    app.get("/x", (c) => c.json({ user: c.var.user }));

    const res = await app.request("/x", {
      headers: { "x-user-id": "not-a-uuid" },
    });
    expect(res.status).toBe(401);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("auth_invalid_user_id");
  });

  it("acepta UUID válido y setea c.var.user con role desde DEV_USER_ROLE", async () => {
    const app = new Hono<ForjaAuthContext>();
    app.use("*", forjaAuthStub());
    app.get("/x", (c) => c.json({ user: c.var.user }));

    const res = await app.request("/x", {
      headers: { "x-user-id": VALID_UUID },
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { user: User };
    expect(body.user.id).toBe(VALID_UUID);
    expect(body.user.role).toBe("t1_alfredo");
    expect(body.user.email).toBe("t1_alfredo@stub.la-forja.local");
  });

  it("respeta DEV_USER_ROLE=t1_padre para tests Cliente Cero", async () => {
    process.env.DEV_USER_ROLE = "t1_padre";
    _resetEnvCache();
    const app = new Hono<ForjaAuthContext>();
    app.use("*", forjaAuthStub());
    app.get("/x", (c) => c.json({ user: c.var.user }));

    const res = await app.request("/x", {
      headers: { "x-user-id": VALID_UUID },
    });
    const body = (await res.json()) as { user: User };
    expect(body.user.role).toBe("t1_padre");
  });

  // D2.5 H-1: el stub debe rechazar 503 en NODE_ENV=production aunque el UUID sea válido.
  // Cierra la ventana entre D3-deploy y D4-OAuth donde un atacante con cualquier UUID
  // podía impersonar T1-Alfredo si DEV_USER_ROLE quedaba seteado.
  it("rechaza con 503 cuando NODE_ENV=production aunque el UUID sea válido (D2.5 H-1)", async () => {
    // Se debe usar strict:false friendly setup: production + secrets reales valdrían,
    // pero como reusamos VALID_ENV (con strings 'x') usamos non-strict explícitamente:
    // el middleware llama loadEnv() en strict mode; necesitamos que parse exitoso.
    // VALID_ENV ya cumple shape mínimo (URLs+keys) para strict mode, salvo SUPABASE_URL
    // que es URL válida. Por tanto strict:true funciona.
    process.env.NODE_ENV = "production";
    _resetEnvCache();
    const app = new Hono<ForjaAuthContext>();
    app.use("*", forjaAuthStub());
    app.get("/x", (c) => c.json({ user: c.var.user }));

    const res = await app.request("/x", {
      headers: { "x-user-id": VALID_UUID },
    });
    expect(res.status).toBe(503);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("auth_stub_disabled_in_production");
  });
});

describe("forjaBudgetGuard", () => {
  function mockBudgetClient(currentSpent: number): BudgetClient & {
    reserve: ReturnType<typeof vi.fn>;
  } {
    const reserve = vi.fn(async () => undefined);
    return {
      readSpent: async () => currentSpent,
      reserveSpent: reserve,
      adjustSpent: async () => undefined,
      reserve,
    };
  }

  it("bloquea con 429 si supera cap $50", async () => {
    const client = mockBudgetClient(49.99);
    const app = new Hono<ForjaAuthContext & ForjaBudgetContext>();
    app.use("*", forjaAuthStub());
    app.use(
      "*",
      forjaBudgetGuard({
        client,
        missionFor: () => "sprint_copilot",
        maxInputTokens: 100_000,
        maxOutputTokens: 50_000,
      }),
    );
    app.get("/x", (c) => c.json({ ok: true }));

    const res = await app.request("/x", {
      headers: { "x-user-id": VALID_UUID },
    });
    expect(res.status).toBe(429);
    const body = (await res.json()) as { error: string; cap: number };
    expect(body.error).toContain("budget_cap_exceeded");
    expect(body.cap).toBe(FORJA_BUDGET_CAP_USD);
  });

  it("permite y setea budgetEstimated si está dentro del cap", async () => {
    const client = mockBudgetClient(10.0);
    const app = new Hono<ForjaAuthContext & ForjaBudgetContext>();
    app.use("*", forjaAuthStub());
    app.use(
      "*",
      forjaBudgetGuard({
        client,
        missionFor: () => "tutor",
        maxInputTokens: 1000,
        maxOutputTokens: 500,
      }),
    );
    app.get("/x", (c) =>
      c.json({
        estimated: c.var.budgetEstimated,
        mission: c.var.budgetMission,
      }),
    );

    const res = await app.request("/x", {
      headers: { "x-user-id": VALID_UUID },
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { estimated: number; mission: string };
    // tutor: 1000/1M*5 + 500/1M*25 = 0.0175
    expect(body.estimated).toBeCloseTo(0.0175, 6);
    expect(body.mission).toBe("tutor");
    expect(client.reserve).toHaveBeenCalledOnce();
  });

  it("error 500 si forjaAuthStub no se montó antes", async () => {
    const client = mockBudgetClient(0);
    const app = new Hono<ForjaBudgetContext>();
    app.use(
      "*",
      forjaBudgetGuard({
        client,
        missionFor: () => "tutor",
      }),
    );
    app.get("/x", (c) => c.json({ ok: true }));

    const res = await app.request("/x");
    expect(res.status).toBe(500);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("budget_user_missing");
  });
});

describe("forjaTelemetry", () => {
  it("setea x-request-id en response y emite evento puerta_invoked", async () => {
    const captured: TelemetryEvent[] = [];
    const fakeClient: TelemetryClient = {
      recordEvent: async (e) => {
        captured.push(e);
      },
    };
    _setTelemetryClient(fakeClient);

    const app = new Hono<ForjaAuthContext & ForjaTelemetryContext>();
    app.use("*", forjaAuthStub());
    app.use("*", forjaTelemetry());
    app.get("/x", (c) =>
      c.json({ requestId: c.var.requestId }),
    );

    const res = await app.request("/x", {
      headers: { "x-user-id": VALID_UUID },
    });
    expect(res.status).toBe(200);
    const requestId = res.headers.get("x-request-id");
    expect(requestId).toBeTruthy();
    expect(requestId!.length).toBeGreaterThan(10);

    expect(captured.length).toBe(1);
    expect(captured[0]!.userId).toBe(VALID_UUID);
    expect(captured[0]!.type).toBe("puerta_invoked");
    const meta = captured[0]!.metadata!;
    expect(meta.path).toBe("/x");
    expect(meta.method).toBe("GET");
    expect(meta.status).toBe(200);
    expect(typeof meta.durationMs).toBe("number");
  });

  it("propaga x-request-id si viene del cliente", async () => {
    const captured: TelemetryEvent[] = [];
    _setTelemetryClient({
      recordEvent: async (e) => {
        captured.push(e);
      },
    });

    const app = new Hono<ForjaAuthContext & ForjaTelemetryContext>();
    app.use("*", forjaAuthStub());
    app.use("*", forjaTelemetry());
    app.get("/x", (c) => c.json({ ok: true }));

    const res = await app.request("/x", {
      headers: {
        "x-user-id": VALID_UUID,
        "x-request-id": "client-req-abc-123",
      },
    });
    expect(res.headers.get("x-request-id")).toBe("client-req-abc-123");
    expect(captured[0]!.metadata!.requestId).toBe("client-req-abc-123");
  });

  it("NO emite evento si no hay user (ej. /health)", async () => {
    const captured: TelemetryEvent[] = [];
    _setTelemetryClient({
      recordEvent: async (e) => {
        captured.push(e);
      },
    });

    const app = new Hono<ForjaTelemetryContext>();
    app.use("*", forjaTelemetry());
    app.get("/health", (c) => c.json({ ok: true }));

    const res = await app.request("/health");
    expect(res.status).toBe(200);
    expect(captured.length).toBe(0);
  });
});
