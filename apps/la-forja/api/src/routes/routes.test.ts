/**
 * La Forja — Tests rutas Hono D2.6.
 *
 * Validación binaria por ruta:
 *   - tutor: 400 si messages vacío, 200 con AC12 + tutor mockeados
 *   - sprints: 400 si objective vacío, 200 con propuesta + GET /states
 *   - manus: 200 con bridge mockeado, 429 si type=rate_limit
 *   - puertas: GET enumerator length 5, 404 puerta no existe
 *   - telemetry: 400 si type inválido, 200 con type canónico
 */

import { Hono } from "hono";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { _resetEnvCache } from "../lib/env";
import { _setTelemetryClient, type TelemetryEvent } from "../lib/telemetry";
import type { BudgetClient } from "../lib/budget";
import { forjaAuthStub, type ForjaAuthContext } from "../middleware/auth";
import { forjaBudgetGuard, type ForjaBudgetContext } from "../middleware/budget";
import { tutorRoutes } from "./tutor";
import { sprintsRoutes, SPRINT_STATES } from "./sprints";
import { manusRoutes } from "./manus";
import { puertasRoutes } from "./puertas";
import { telemetryRoutes } from "./telemetry";

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
const AUTH_HEADERS = { "x-user-id": VALID_UUID };

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

function mockBudgetClient(spent = 0): BudgetClient {
  return {
    readSpent: async () => spent,
    reserveSpent: async () => undefined,
    adjustSpent: async () => undefined,
  };
}

// Mock del SDK Anthropic vía vi.mock (módulo entero)
vi.mock("../lib/llm/anthropic", () => ({
  invokeTutor: vi.fn(async () => ({
    content: "Mock tutor reply",
    inputTokens: 100,
    outputTokens: 50,
    model: "claude-opus-4-7",
    stopReason: "end_turn",
  })),
}));
vi.mock("../lib/llm/openai", () => ({
  invokeSprintCopilot: vi.fn(async () => ({
    content: '{"title":"Sprint mock","objective":"x","deliverables":[],"acceptance_criteria":[],"eta_days":3}',
    inputTokens: 200,
    outputTokens: 80,
    model: "gpt-5.5-pro",
    status: "completed",
  })),
}));
vi.mock("../lib/llm/perplexity", () => ({
  invokeMagnaValidation: vi.fn(async () => ({
    content: "Validación mock",
    citations: ["https://example.com/source-a", "https://example.com/source-b"],
    inputTokens: 50,
    outputTokens: 30,
    model: "sonar-reasoning-pro",
  })),
}));
vi.mock("../lib/manus_bridge", async () => {
  const actual = await vi.importActual<typeof import("../lib/manus_bridge")>(
    "../lib/manus_bridge",
  );
  return {
    ...actual,
    handleManusBridge: vi.fn(async (params: { action?: string }) => {
      if (params.action === "rate_limit_test") {
        return { error: "Rate limit", type: "rate_limit" };
      }
      return { task_id: "task-mock-123", status: "queued", output: null };
    }),
  };
});

describe("/api/tutor/chat", () => {
  function makeApp() {
    const app = new Hono<ForjaAuthContext & ForjaBudgetContext>();
    app.use("*", forjaAuthStub());
    app.use(
      "*",
      forjaBudgetGuard({
        client: mockBudgetClient(0),
        missionFor: () => "tutor",
      }),
    );
    app.route(
      "/api/tutor",
      tutorRoutes({
        budgetClient: mockBudgetClient(0),
        classifier: {
          intent: "no_confusion",
          confidence: 0.2,
          passesThreshold: false,
          rawMessage: "test",
          inputTokens: 10,
          outputTokens: 5,
        },
      }),
    );
    return app;
  }

  it("400 si messages está vacío", async () => {
    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({ messages: [] }),
    });
    expect(res.status).toBe(400);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("tutor_missing_messages");
  });

  it("400 si no hay user message", async () => {
    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "assistant", content: "hi" }],
      }),
    });
    expect(res.status).toBe(400);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("tutor_no_user_message");
  });

  it("200 con tutor mockeado y AC12 inyectado", async () => {
    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "Explícame el SOP" }],
      }),
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as {
      ok: boolean;
      content: string;
      model: string;
      intent: string;
      confidence: number;
      citations: string[];
      validationModel: string | null;
      costUsd: number;
    };
    expect(body.ok).toBe(true);
    expect(body.content).toBe("Mock tutor reply");
    expect(body.model).toBe("claude-opus-4-7");
    expect(body.intent).toBe("no_confusion");
    expect(body.citations).toEqual([]);
    expect(body.validationModel).toBeNull();
    expect(body.costUsd).toBeGreaterThan(0);
  });

  it("incluye citations cuando requireValidation=true", async () => {
    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "¿Cuál fue el último sprint?" }],
        requireValidation: true,
      }),
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as {
      citations: string[];
      validationModel: string | null;
    };
    expect(body.citations.length).toBeGreaterThan(0);
    expect(body.validationModel).toBe("sonar-reasoning-pro");
  });
});

describe("/api/sprints", () => {
  function makeApp() {
    const app = new Hono<ForjaAuthContext & ForjaBudgetContext>();
    app.use("*", forjaAuthStub());
    app.use(
      "*",
      forjaBudgetGuard({
        client: mockBudgetClient(0),
        missionFor: () => "sprint_copilot",
      }),
    );
    app.route(
      "/api/sprints",
      sprintsRoutes({ budgetClient: mockBudgetClient(0) }),
    );
    return app;
  }

  it("400 si objective vacío", async () => {
    const res = await makeApp().request("/api/sprints", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({ objective: "" }),
    });
    expect(res.status).toBe(400);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("sprints_missing_objective");
  });

  it("200 con propuesta del co-piloto y state=proposed (D2.5 H-4 SPEC §4:130)", async () => {
    const res = await makeApp().request("/api/sprints", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        objective: "Reconciliar SPEC v3.2 con D1 no-SQL",
      }),
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as {
      ok: boolean;
      proposal: string;
      state: string;
      model: string;
      costUsd: number;
    };
    expect(body.ok).toBe(true);
    expect(body.state).toBe("proposed");
    expect(body.model).toBe("gpt-5.5-pro");
    expect(body.proposal).toContain("Sprint mock");
    expect(body.costUsd).toBeGreaterThan(0);
  });

  it("GET /states retorna las 8 states canónicas", async () => {
    const res = await makeApp().request("/api/sprints/states", {
      method: "GET",
      headers: AUTH_HEADERS,
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { states: string[] };
    expect(body.states).toEqual([...SPRINT_STATES]);
    expect(body.states.length).toBe(8);
  });
});

describe("/api/manus/task", () => {
  function makeApp() {
    const app = new Hono<ForjaAuthContext>();
    app.use("*", forjaAuthStub());
    app.route("/api/manus", manusRoutes());
    return app;
  }

  it("200 con bridge mockeado", async () => {
    const res = await makeApp().request("/api/manus/task", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "create_task",
        prompt: "Investiga X",
        account: "google",
      }),
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as {
      ok: boolean;
      taskId: string;
      status: string;
    };
    expect(body.ok).toBe(true);
    expect(body.taskId).toBe("task-mock-123");
  });

  it("429 si type=rate_limit del bridge", async () => {
    const res = await makeApp().request("/api/manus/task", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({ action: "rate_limit_test" }),
    });
    expect(res.status).toBe(429);
    const body = (await res.json()) as {
      ok: boolean;
      type: string;
    };
    expect(body.ok).toBe(false);
    expect(body.type).toBe("rate_limit");
  });
});

describe("/api/puertas", () => {
  function makeApp() {
    const app = new Hono<ForjaAuthContext>();
    app.use("*", forjaAuthStub());
    app.route("/api/puertas", puertasRoutes());
    return app;
  }

  it("GET / enumerator length 5", async () => {
    const res = await makeApp().request("/api/puertas", {
      method: "GET",
      headers: AUTH_HEADERS,
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { puertas: string[] };
    expect(body.puertas.length).toBe(5);
  });

  it("404 si nombre no es puerta canónica", async () => {
    const res = await makeApp().request("/api/puertas/inexistente", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    expect(res.status).toBe(404);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("puerta_not_found");
  });
});

describe("/api/telemetry", () => {
  function makeApp() {
    const app = new Hono<ForjaAuthContext>();
    app.use("*", forjaAuthStub());
    app.route("/api/telemetry", telemetryRoutes());
    return app;
  }

  it("400 si type no es canónico", async () => {
    const res = await makeApp().request("/api/telemetry", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({ type: "invalid_event" }),
    });
    expect(res.status).toBe(400);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("telemetry_invalid_type");
  });

  it("200 con type canónico simplification_requested", async () => {
    const captured: TelemetryEvent[] = [];
    _setTelemetryClient({
      recordEvent: async (e) => {
        captured.push(e);
      },
    });
    const res = await makeApp().request("/api/telemetry", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        type: "simplification_requested",
        confidence: 0.85,
      }),
    });
    expect(res.status).toBe(200);
    expect(captured.length).toBe(1);
    expect(captured[0]!.type).toBe("simplification_requested");
    expect(captured[0]!.confidence).toBe(0.85);
    expect(captured[0]!.userId).toBe(VALID_UUID);
  });
});


// ============================================================================
// D2.5 — Tests de hardening adversarial (audit Perplexity 15-may-2026)
// ============================================================================
//
// H-2: budget leak en error path
//   Si el LLM (tutor o magna) lanza, debe llamarse adjustSpent(-estimated)
//   para liberar la reserva. Sin esto, el cap $50/mes se "agotaba" con errores.
//
// H-3: multi-mission gate
//   classifier (Gemini Flash) y magna_validation (Sonar) son llamadas LLM
//   adicionales que también pasan por preCallCheck/postCallCommit. Antes de
//   D2.5 sólo el tutor cobraba al cap, dejando hueco para abuso.

describe("D2.5 hardening — /api/tutor/chat (H-2 budget rollback + H-3 multi-mission gate)", () => {
  function spyBudgetClient(): BudgetClient & {
    reserveSpent: ReturnType<typeof vi.fn>;
    adjustSpent: ReturnType<typeof vi.fn>;
  } {
    const reserveSpent = vi.fn(async () => undefined);
    const adjustSpent = vi.fn(async () => undefined);
    return {
      readSpent: async () => 0,
      reserveSpent,
      adjustSpent,
    };
  }

  function makeAppWithClient(
    client: BudgetClient,
  ) {
    const app = new Hono<ForjaAuthContext & ForjaBudgetContext>();
    app.use("*", forjaAuthStub());
    app.use(
      "*",
      forjaBudgetGuard({
        client,
        missionFor: () => "tutor",
      }),
    );
    app.route(
      "/api/tutor",
      tutorRoutes({
        budgetClient: client,
        classifier: {
          intent: "no_confusion",
          confidence: 0.2,
          passesThreshold: false,
          rawMessage: "test",
          inputTokens: 10,
          outputTokens: 5,
        },
      }),
    );
    return app;
  }

  it("H-3: classifier mission llama reserveSpent con estimateCost > 0 (preCallCheck)", async () => {
    const client = spyBudgetClient();
    const app = makeAppWithClient(client);
    const res = await app.request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "Explícame el SOP" }],
      }),
    });
    expect(res.status).toBe(200);
    // Esperamos al menos 2 reserveSpent: 1 del middleware (tutor) + 1 del classifier
    // (preCallCheck dentro de la ruta, H-3). Sin H-3 esto sería 1.
    expect(client.reserveSpent.mock.calls.length).toBeGreaterThanOrEqual(2);
    // Los montos reservados deben ser todos > 0 (estimateCost real, no zero)
    for (const call of client.reserveSpent.mock.calls) {
      const amount = call[1] as number;
      expect(amount).toBeGreaterThan(0);
    }
  });

  it("H-3: requireValidation=true agrega reserveSpent para magna_validation", async () => {
    const client = spyBudgetClient();
    const app = makeAppWithClient(client);
    const res = await app.request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "¿Último sprint?" }],
        requireValidation: true,
      }),
    });
    expect(res.status).toBe(200);
    // Esperamos 3 reservas: tutor (middleware) + classifier + magna_validation (H-3)
    expect(client.reserveSpent.mock.calls.length).toBeGreaterThanOrEqual(3);
  });

  it("H-2: si invokeTutor lanza, adjustSpent(-estimated) se llama para rollback (budget leak fix)", async () => {
    // Forzamos al mock a lanzar para simular fallo de proveedor
    const anthropicMod = await import("../lib/llm/anthropic");
    vi.mocked(anthropicMod.invokeTutor).mockImplementationOnce(async () => {
      throw new Error("simulated upstream 500");
    });

    const client = spyBudgetClient();
    const app = makeAppWithClient(client);
    const res = await app.request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "Hola" }],
      }),
    });
    // Hono onError: la ruta lanza; en handler default → 500.
    // Lo único que importa para H-2 es que se haya hecho rollback.
    expect([500, 502]).toContain(res.status);
    // adjustSpent debe haberse llamado con un valor NEGATIVO para liberar la reserva
    const negativeCalls = client.adjustSpent.mock.calls.filter(
      (call) => (call[1] as number) < 0,
    );
    expect(negativeCalls.length).toBeGreaterThanOrEqual(1);
  });

  it("H-2: si invokeMagnaValidation lanza con requireValidation=true, adjustSpent(-magnaEstimated) ejecuta rollback", async () => {
    const perplexityMod = await import("../lib/llm/perplexity");
    vi.mocked(perplexityMod.invokeMagnaValidation).mockImplementationOnce(
      async () => {
        throw new Error("simulated sonar timeout");
      },
    );

    const client = spyBudgetClient();
    const app = makeAppWithClient(client);
    const res = await app.request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "Verifica esto" }],
        requireValidation: true,
      }),
    });
    expect([500, 502]).toContain(res.status);
    const negativeCalls = client.adjustSpent.mock.calls.filter(
      (call) => (call[1] as number) < 0,
    );
    // Esperamos al menos 1 rollback (magna). Puede haber más si el código rollbackea
    // tutor también, pero el invariante mínimo es 1.
    expect(negativeCalls.length).toBeGreaterThanOrEqual(1);
  });
});
