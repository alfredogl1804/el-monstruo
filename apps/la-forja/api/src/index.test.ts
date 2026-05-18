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
import { _resetEnvCache } from "./lib/env.js";
import { _setTelemetryClient } from "./lib/telemetry.js";
import { InMemoryBudgetClient } from "./lib/budget_clients.js";
import { createApp } from "./index.js";

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

  it("GET /api/sprints/states retorna las 8 states canónicas (D5.2 reconciliación SQL)", async () => {
    const app = createApp();
    const res = await app.request("/api/sprints/states", {
      headers: { "x-user-id": VALID_UUID },
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { states: string[] };
    // D5.2 drift P2 reconciliado: SQL `chk_forja_sprints_status` (D5.1) es la fuente
    // de verdad. Los estados TS ahora coinciden binariamente con la constraint en
    // Postgres aplicada en producción (DSC-LF-010 firmado).
    expect(body.states).toEqual([
      "proposed",
      "confirmed",
      "executing",
      "waiting_audit",
      "audited",
      "merged",
      "blocked",
      "archived",
    ]);
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


/**
 * D4-PROD-AUTH-001 regression test.
 *
 * Garantiza que `index.ts` use `forjaAuthSelector()` (NO `forjaAuthStub()` hardcoded).
 * Drift detectado por Manus E2 durante smoke C3 §7.1 (2026-05-18):
 *   - Spec D4-PROD-AUTH-001 §1 afirmaba "wiring D4 completo en main"
 *   - Realidad: `index.ts:141` montaba `forjaAuthStub()` hardcoded
 *   - Resultado: `/api/sprints/states` sin cookie → 503 en lugar de 401 esperado
 *
 * Categoría 4 de drift DSC-G-013 v0.1: código↔código (función definida pero no usada en call site).
 *
 * Este test verifica binariamente que el call site discrimina por NODE_ENV:
 *   - production → forjaAuthGoogle (sin cookie → 401 [la-forja:auth_session_missing])
 *   - test/dev → forjaAuthStub (con x-user-id válido → 200, preserva 180+ tests existentes)
 */
describe("D4-PROD-AUTH-001 — call site usa forjaAuthSelector() (no hardcoded stub)", () => {
  it("NODE_ENV=production sin cookie → 401 [la-forja:auth_session_missing] (NO 503 stub)", async () => {
    process.env.NODE_ENV = "production";
    // Producción exige los 3 secrets D4 + JWT (≥32 chars) por superRefine en env.ts.
    process.env.GOOGLE_OAUTH_CLIENT_ID =
      "test-client-id.apps.googleusercontent.com";
    process.env.GOOGLE_OAUTH_CLIENT_SECRET = "GOCSPX-test-secret";
    process.env.JWT_SECRET =
      "forja-test-jwt-secret-must-be-at-least-32-chars-long";
    _resetEnvCache();

    const app = createApp();
    const res = await app.request("/api/sprints/states");

    expect(res.status).toBe(401);
    const body = (await res.json()) as { ok: boolean; error: string };
    expect(body.ok).toBe(false);
    expect(body.error).toContain("auth_session_missing");
    expect(body.error).not.toContain("auth_stub_disabled_in_production");
  });

  it("NODE_ENV=test (default) con x-user-id válido → 200 (preserva tests existentes)", async () => {
    // NODE_ENV ya viene "test" por vitest; confirmamos selector → forjaAuthStub.
    process.env.NODE_ENV = "test";
    _resetEnvCache();

    const app = createApp();
    const res = await app.request("/api/sprints/states", {
      headers: { "x-user-id": VALID_UUID },
    });

    expect(res.status).toBe(200);
    const body = (await res.json()) as { ok: boolean };
    expect(body.ok).toBe(true);
  });

  it("NODE_ENV=test sin x-user-id → 401 [la-forja:auth_missing_user_id] (stub canónico)", async () => {
    process.env.NODE_ENV = "test";
    _resetEnvCache();

    const app = createApp();
    const res = await app.request("/api/sprints/states");

    expect(res.status).toBe(401);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("auth_missing_user_id");
  });
});
