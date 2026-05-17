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
import {
  FORJA_TUTOR_HEADER_KEYS,
  FORJA_CITATIONS_HEADER_MAX_BYTES,
} from "../shared/headers";
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

// ----------------------------------------------------------------------------
// Mocks de LLM providers
//
// D3.2: el mock del módulo anthropic provee tanto `invokeTutor` (legacy,
// usado en otros tests / paths no-stream) como `buildTutorStream`. El stream
// builder devuelve un objeto compatible con `result.toUIMessageStreamResponse`
// que retorna un Response SSE simulado y dispara el callback `onFinish`
// inmediatamente con tokens canónicos. Si `mockTutorStreamShouldThrow` es
// true, dispara `onError` antes de devolver el Response (simula fallo del
// proveedor mid-stream).
// ----------------------------------------------------------------------------

let mockTutorStreamShouldThrow = false;
export function _setTutorStreamShouldThrow(v: boolean) {
  mockTutorStreamShouldThrow = v;
}

function makeMockStreamResult(opts: {
  onFinish: (e: {
    inputTokens: number;
    outputTokens: number;
    model: string;
    finishReason: string | undefined;
  }) => Promise<void> | void;
  onError: (err: unknown) => Promise<void> | void;
}) {
  return {
    toUIMessageStreamResponse: (
      init?: { headers?: Record<string, string> },
    ): Response => {
      // Si el stream está marcado para fallar, dispara onError de forma
      // sincrónica antes de devolver el Response (rollback del budget se ve
      // en el spy del adjustSpent).
      if (mockTutorStreamShouldThrow) {
        // Fire-and-forget: el rollback se ejecuta en el siguiente tick.
        Promise.resolve().then(() =>
          opts.onError(new Error("simulated upstream stream error")),
        );
        return new Response(
          "event: error\ndata: {\"error\":\"upstream\"}\n\n",
          {
            status: 500,
            headers: {
              "content-type": "text/event-stream",
              ...(init?.headers ?? {}),
            },
          },
        );
      }
      // Stream feliz: dispara onFinish con tokens canónicos antes de devolver
      // el Response, así postCallCommit corre en el mismo tick que el test.
      const finishPromise = Promise.resolve(
        opts.onFinish({
          inputTokens: 100,
          outputTokens: 50,
          model: "claude-opus-4-7",
          finishReason: "stop",
        }),
      );
      // Construye un cuerpo SSE mínimo válido v1 con un text-delta y finish.
      const body =
        `data: {"type":"start","messageId":"m_mock"}\n\n` +
        `data: {"type":"text-start","id":"t1"}\n\n` +
        `data: {"type":"text-delta","id":"t1","delta":"Mock tutor reply"}\n\n` +
        `data: {"type":"text-end","id":"t1"}\n\n` +
        `data: {"type":"finish"}\n\n` +
        `data: [DONE]\n\n`;
      // Espera el commit antes de cerrar el body para que el test que
      // verifica adjustSpent vea la llamada cuando lee el body.
      const stream = new ReadableStream<Uint8Array>({
        async start(controller) {
          await finishPromise;
          controller.enqueue(new TextEncoder().encode(body));
          controller.close();
        },
      });
      return new Response(stream, {
        status: 200,
        headers: {
          "content-type": "text/event-stream",
          ...(init?.headers ?? {}),
        },
      });
    },
  };
}

vi.mock("../lib/llm/anthropic", () => ({
  // Legacy blocking path (preservado para compat aunque /api/tutor/chat no lo usa
  // desde D3.2). Sigue mockeado por si otros tests lo invocan en el futuro.
  invokeTutor: vi.fn(async () => ({
    content: "Mock tutor reply",
    inputTokens: 100,
    outputTokens: 50,
    model: "claude-opus-4-7",
    stopReason: "end_turn",
  })),
  // D3.2 SSE streaming builder.
  buildTutorStream: vi.fn((opts: Parameters<typeof makeMockStreamResult>[0]) =>
    makeMockStreamResult(opts),
  ),
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

// D3.2 (DSC-LF-005): /api/tutor/chat ahora retorna text/event-stream construido
// por toUIMessageStreamResponse() de Vercel AI SDK 6. Los tests asseritan:
//   - 400 JSON sigue funcionando para errores de shape (pre-stream)
//   - 200 retorna content-type: text/event-stream + headers x-la-forja-*
//   - intent / confidence / model / validation-model viajan en headers
//   - citations viajan en x-la-forja-citations (JSON string)
describe("/api/tutor/chat (D3.2 SSE)", () => {
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

  beforeEach(() => {
    _setTutorStreamShouldThrow(false);
  });

  it("400 JSON si messages está vacío (validación pre-stream)", async () => {
    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({ messages: [] }),
    });
    expect(res.status).toBe(400);
    expect(res.headers.get("content-type")).toContain("application/json");
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("tutor_missing_messages");
  });

  it("400 JSON si no hay user message (validación pre-stream)", async () => {
    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "assistant", content: "hi" }],
      }),
    });
    expect(res.status).toBe(400);
    expect(res.headers.get("content-type")).toContain("application/json");
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("tutor_no_user_message");
  });

  it("200 SSE: content-type=text/event-stream + headers metadata x-la-forja-*", async () => {
    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "Explícame el SOP" }],
      }),
    });
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toContain("text/event-stream");
    expect(res.headers.get(FORJA_TUTOR_HEADER_KEYS.protocolVersion)).toBe("v1");
    expect(res.headers.get(FORJA_TUTOR_HEADER_KEYS.intent)).toBe(
      "no_confusion",
    );
    expect(res.headers.get(FORJA_TUTOR_HEADER_KEYS.model)).toBe(
      "claude-opus-4-7",
    );
    expect(
      Number(res.headers.get(FORJA_TUTOR_HEADER_KEYS.confidence)),
    ).toBeCloseTo(0.2);
    expect(res.headers.get(FORJA_TUTOR_HEADER_KEYS.citationsB64)).toBeNull();
    expect(
      res.headers.get(FORJA_TUTOR_HEADER_KEYS.validationModel),
    ).toBeNull();
    // Drena el body para asegurar que el stream cierra limpio
    const text = await res.text();
    expect(text).toContain("Mock tutor reply");
  });

  it("200 SSE: incluye x-la-forja-citations-b64 + x-la-forja-validation-model con requireValidation=true (F-D3.2-03 base64url)", async () => {
    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "¿Cuál fue el último sprint?" }],
        requireValidation: true,
      }),
    });
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toContain("text/event-stream");
    // F-D3.2-03: el header crudo `x-la-forja-citations` (JSON) ya no existe
    expect(res.headers.get("x-la-forja-citations")).toBeNull();
    // F-D3.2-03: viaja como base64url(JSON.stringify([...]))
    const b64 = res.headers.get(FORJA_TUTOR_HEADER_KEYS.citationsB64);
    expect(b64).not.toBeNull();
    const decoded = JSON.parse(
      Buffer.from(b64!, "base64url").toString("utf-8"),
    ) as string[];
    expect(decoded.length).toBeGreaterThan(0);
    expect(decoded[0]).toMatch(/^https:\/\//);
    expect(res.headers.get(FORJA_TUTOR_HEADER_KEYS.validationModel)).toBe(
      "sonar-reasoning-pro",
    );
  });

  it("F-D3.2-03: citations con UTF-8 (acentos) sobreviven el round-trip via base64url", async () => {
    const perplexityMod = await import("../lib/llm/perplexity");
    vi.mocked(perplexityMod.invokeMagnaValidation).mockImplementationOnce(
      async () => ({
        content: "v\u00e1lido",
        citations: [
          "https://ejemplo.com/fuente-\u00e1rabe",
          "https://ejemplo.com/m\u00e9xico",
        ],
        inputTokens: 50,
        outputTokens: 30,
        model: "sonar-reasoning-pro",
      }),
    );

    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "Verifica" }],
        requireValidation: true,
      }),
    });
    expect(res.status).toBe(200);
    const b64 = res.headers.get(FORJA_TUTOR_HEADER_KEYS.citationsB64);
    expect(b64).not.toBeNull();
    const decoded = JSON.parse(
      Buffer.from(b64!, "base64url").toString("utf-8"),
    ) as string[];
    expect(decoded).toContain("https://ejemplo.com/fuente-\u00e1rabe");
    expect(decoded).toContain("https://ejemplo.com/m\u00e9xico");
  });

  it("F-D3.2-04 + F-D3.2.1-01: payload excede el cap → se trunca por CITATION COMPLETA y el JSON sobrevive round-trip", async () => {
    const huge = Array.from(
      { length: 200 },
      (_, i) => `https://example.com/source-${i.toString().padStart(4, "0")}áéíóú`,
    );
    const perplexityMod = await import("../lib/llm/perplexity");
    vi.mocked(perplexityMod.invokeMagnaValidation).mockImplementationOnce(
      async () => ({
        content: "x",
        citations: huge,
        inputTokens: 50,
        outputTokens: 30,
        model: "sonar-reasoning-pro",
      }),
    );

    const res = await makeApp().request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "x" }],
        requireValidation: true,
      }),
    });
    expect(res.status).toBe(200);
    const b64 = res.headers.get(FORJA_TUTOR_HEADER_KEYS.citationsB64);
    expect(b64).not.toBeNull();

    // F-D3.2.1-01: el truncado por CITATION COMPLETA garantiza que el JSON
    // resultante es siempre parseable. El test anterior solo verificaba
    // longitud de base64, no la integridad del JSON → no detectaba el bug
    // donde el truncado por bytes ciegos rompe codepoints UTF-8.
    const decoded = Buffer.from(b64!, "base64url").toString("utf-8");
    const decodedBytes = Buffer.byteLength(decoded, "utf-8");
    expect(decodedBytes).toBeLessThanOrEqual(FORJA_CITATIONS_HEADER_MAX_BYTES);

    // Round-trip: JSON.parse no debe lanzar.
    const parsed = JSON.parse(decoded) as string[];
    expect(Array.isArray(parsed)).toBe(true);
    // Al menos UNA citation debe sobrevivir (cap binario, no cero-cita).
    expect(parsed.length).toBeGreaterThan(0);
    // Cada citation que sobrevivió mantiene su forma URL completa
    // (no fragmentos cortados a la mitad).
    for (const url of parsed) {
      expect(url.startsWith("https://example.com/source-")).toBe(true);
      expect(url.endsWith("áéíóú")).toBe(true);
    }
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

  beforeEach(() => {
    _setTutorStreamShouldThrow(false);
  });

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
    // Drena el body para esperar el onFinish
    await res.text();
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
    await res.text();
    // Esperamos 3 reservas: tutor (middleware) + classifier + magna_validation (H-3)
    expect(client.reserveSpent.mock.calls.length).toBeGreaterThanOrEqual(3);
  });

  it("H-2 (D3.2): si el stream del tutor falla mid-stream, adjustSpent(-estimated) ejecuta rollback vía onError (budget leak fix)", async () => {
    // D3.2: invokeTutor ya no se llama directo desde la ruta. El builder
    // del stream dispara el callback onError con un error simulado, lo que
    // hace que la ruta corra adjustSpent con valor negativo.
    _setTutorStreamShouldThrow(true);

    const client = spyBudgetClient();
    const app = makeAppWithClient(client);
    const res = await app.request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "Hola" }],
      }),
    });
    // El mock devuelve 500 con SSE error frame; el rollback corre antes.
    expect(res.status).toBe(500);
    // Drena el body para asegurar que onError ya se disparo
    await res.text();
    // Espera un microtask más para que el callback onError se complete
    await new Promise((r) => setTimeout(r, 10));
    // adjustSpent debe haberse llamado con un valor NEGATIVO para liberar reserva
    const negativeCalls = client.adjustSpent.mock.calls.filter(
      (call) => (call[1] as number) < 0,
    );
    expect(negativeCalls.length).toBeGreaterThanOrEqual(1);
  });

  it("H-2 + R-D3.2-01 (F-D3.2-01): si invokeMagnaValidation lanza con requireValidation=true, adjustSpent rollbackea AMBAS reservas (magna + tutor)", async () => {
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
    // F-D3.2-01: cuando magna falla, el código DEBE revertir DOS reservas
    // (magna_validation + tutor reservado por el middleware) para evitar
    // leak permanente del cap. Si solo aparece 1 rollback, el bug está vivo.
    expect(negativeCalls.length).toBeGreaterThanOrEqual(2);
    // El throw debe llevar el namespace canónico
    const body = await res.json().catch(() => ({}));
    if (body && typeof body === "object" && "error" in body) {
      expect(String(body.error)).toMatch(/la-forja:tutor_(magna|stream)/);
    }
  });

  it("R-D3.2-01b (F-D3.2-01): si classifier lanza, rollbackea AMBAS reservas (classifier + tutor)", async () => {
    const ac12Mod = await import("../lib/ac12");
    vi.spyOn(ac12Mod, "classifyMessage").mockImplementationOnce(async () => {
      throw new Error("simulated classifier timeout");
    });

    const client = spyBudgetClient();
    // Usar app sin classifier deps inyectado para que use classifyMessage real
    const app = new Hono<ForjaAuthContext & ForjaBudgetContext>();
    app.use("*", forjaAuthStub());
    app.use(
      "*",
      forjaBudgetGuard({ client, missionFor: () => "tutor" }),
    );
    app.route(
      "/api/tutor",
      tutorRoutes({ budgetClient: client }),
    );

    const res = await app.request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "Hola" }],
      }),
    });
    expect([500, 502]).toContain(res.status);
    const negativeCalls = client.adjustSpent.mock.calls.filter(
      (call) => (call[1] as number) < 0,
    );
    // F-D3.2-01: classifier-fail debe revertir classifier + tutor.
    expect(negativeCalls.length).toBeGreaterThanOrEqual(2);
  });

  it("F-D3.2-02: si onError del stream lanza al tocar el budget client, el error queda log fail-loud (no silencia)", async () => {
    _setTutorStreamShouldThrow(true);

    // Cliente que SOLO lanza en rollback (delta < 0). Los postCallCommit
    // del classifier (delta > 0) deben pasar para que el flujo llegue al
    // stream tutor; ahí onError dispara el rollback negativo y nuestra
    // captura fail-loud (F-D3.2-02) loguea el namespace canónico.
    const failingClient: BudgetClient = {
      readSpent: async () => 0,
      reserveSpent: async () => undefined,
      adjustSpent: async (_user, delta) => {
        if (delta < 0) {
          throw new Error("simulated supabase ledger down");
        }
      },
    };

    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    const app = new Hono<ForjaAuthContext & ForjaBudgetContext>();
    app.use("*", forjaAuthStub());
    app.use(
      "*",
      forjaBudgetGuard({ client: failingClient, missionFor: () => "tutor" }),
    );
    app.route(
      "/api/tutor",
      tutorRoutes({
        budgetClient: failingClient,
        classifier: {
          intent: "no_confusion",
          confidence: 0.2,
          passesThreshold: false,
          rawMessage: "x",
          inputTokens: 10,
          outputTokens: 5,
        },
      }),
    );

    const res = await app.request("/api/tutor/chat", {
      method: "POST",
      headers: { ...AUTH_HEADERS, "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: [{ role: "user", content: "x" }],
      }),
    });
    // El stream cierra; el rollback fallido quedó logueado
    await res.text();
    await new Promise((r) => setTimeout(r, 10));

    // F-D3.2-02: el error namespace canónico debe aparecer en el log
    const calls = errorSpy.mock.calls
      .map((c) => c.map((v) => String(v)).join(" "))
      .join("\n");
    expect(calls).toMatch(/la-forja:tutor_rollback_failed/);
    errorSpy.mockRestore();
  });
});
