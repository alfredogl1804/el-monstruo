/**
 * La Forja — Smoke test D2.7.
 *
 * Valida binariamente el montaje createApp():
 *   - GET /health      200 con service identity
 *   - GET /            200 con endpoints listados
 *   - GET /api/puertas 200 con length 5 (LF-FIVE-DOORS-001)
 *   - GET /api/sprints/states 200 con 8 states
 *   - 401 sin x-user-id en endpoint /api
 *   - InMemoryBudgetClient acumula spent
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { _resetEnvCache } from "./lib/env";
import { _setTelemetryClient } from "./lib/telemetry";
import { InMemoryBudgetClient } from "./lib/budget_clients";
import { createApp } from "./index";

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
});

describe("createApp() — smoke D2.7", () => {
  it("GET /health retorna 200 con service identity", async () => {
    const app = createApp();
    const res = await app.request("/health");
    expect(res.status).toBe(200);
    const body = (await res.json()) as { status: string; service: string };
    expect(body.status).toBe("ok");
    expect(body.service).toBe("la-forja-api");
  });

  it("GET / retorna 200 con endpoints declarados", async () => {
    const app = createApp();
    const res = await app.request("/");
    expect(res.status).toBe(200);
    const body = (await res.json()) as {
      service: string;
      sprint: string;
      endpoints: string[];
    };
    expect(body.service).toBe("la-forja-api");
    expect(body.sprint).toBe("LA-FORJA-001");
    expect(body.endpoints).toContain("POST /api/tutor/chat");
    expect(body.endpoints).toContain("GET /api/puertas");
    expect(body.endpoints.length).toBeGreaterThanOrEqual(8);
  });

  it("GET /api/puertas retorna las 5 puertas canónicas (LF-FIVE-DOORS-001)", async () => {
    const app = createApp();
    const res = await app.request("/api/puertas", {
      headers: { "x-user-id": VALID_UUID },
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { puertas: string[] };
    expect(body.puertas.length).toBe(5);
    expect(body.puertas).toEqual([
      "manus_apple",
      "manus_google",
      "cowork_local",
      "kernel_monstruo",
      "simulador",
    ]);
  });

  it("GET /api/sprints/states retorna las 8 states canónicas", async () => {
    const app = createApp();
    const res = await app.request("/api/sprints/states", {
      headers: { "x-user-id": VALID_UUID },
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { states: string[] };
    expect(body.states.length).toBe(8);
  });

  it("rechaza requests /api sin x-user-id (401 stub auth)", async () => {
    const app = createApp();
    const res = await app.request("/api/puertas");
    // forjaAuthStub debe rechazar sin header
    expect([400, 401]).toContain(res.status);
  });

  it("InMemoryBudgetClient acumula spent entre llamadas", async () => {
    const client = new InMemoryBudgetClient();
    expect(await client.readSpent("u1")).toBe(0);
    await client.reserveSpent("u1", 0.05);
    expect(await client.readSpent("u1")).toBeCloseTo(0.05, 6);
    await client.adjustSpent("u1", -0.01);
    expect(await client.readSpent("u1")).toBeCloseTo(0.04, 6);
  });

  it("createApp con budgetClient inyectado usa el cliente custom", async () => {
    const customClient = new InMemoryBudgetClient();
    await customClient.reserveSpent("seed-user", 1.23);
    const app = createApp({ budgetClient: customClient });
    expect(app).toBeDefined();
    // Verificación binaria: el cliente custom NO se reinicializó
    expect(await customClient.readSpent("seed-user")).toBe(1.23);
  });
});
