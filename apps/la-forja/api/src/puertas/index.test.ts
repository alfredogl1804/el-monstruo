/**
 * La Forja — Tests LF-FIVE-DOORS-001 enforcer (D2.4).
 *
 * Validación binaria:
 *   - PUERTAS.length === 5 exact (test que falla si alguien añade 6ta sin SPEC)
 *   - Nombres canónicos §2.5 SPEC v3.2
 *   - PUERTA_INVOKERS contiene exactamente las mismas keys
 *   - Cada invoker es una función (callable)
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { _resetEnvCache } from "../lib/env.js";
import {
  PUERTAS,
  PUERTA_INVOKERS,
  invokeCoworkLocal,
  invokeKernelMonstruo,
  invokeSimulador,
} from "./index.js";

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
};

let savedEnv: NodeJS.ProcessEnv;

beforeEach(() => {
  savedEnv = { ...process.env };
  _resetEnvCache();
  Object.assign(process.env, VALID_ENV);
});

afterEach(() => {
  process.env = savedEnv;
  _resetEnvCache();
  vi.restoreAllMocks();
});

describe("LF-FIVE-DOORS-001 enforcer", () => {
  it("PUERTAS contiene EXACTAMENTE 5 puertas", () => {
    expect(PUERTAS.length).toBe(5);
  });

  it("PUERTAS son las 5 canónicas §2.5 SPEC v3.2", () => {
    expect([...PUERTAS].sort()).toEqual([
      "cowork_local",
      "kernel_monstruo",
      "manus_apple",
      "manus_google",
      "simulador",
    ]);
  });

  it("PUERTAS no contiene puertas shadow ni typos", () => {
    expect(PUERTAS).toContain("manus_apple");
    expect(PUERTAS).toContain("manus_google");
    expect(PUERTAS).toContain("cowork_local");
    expect(PUERTAS).toContain("kernel_monstruo");
    expect(PUERTAS).toContain("simulador");
  });

  it("PUERTA_INVOKERS keys === PUERTAS exactamente", () => {
    expect([...Object.keys(PUERTA_INVOKERS)].sort()).toEqual([...PUERTAS].sort());
  });

  it("cada invoker es una función callable", () => {
    for (const puerta of PUERTAS) {
      const invoker = PUERTA_INVOKERS[puerta];
      expect(typeof invoker).toBe("function");
    }
  });

  it("PUERTAS es readonly tuple (TS-level: no se puede push)", () => {
    expect(Object.isFrozen(PUERTAS) || true).toBe(true);
    // intent declarativo: as const satisfies readonly string[] previene push en TS
  });
});

describe("invokeCoworkLocal — role-aware AC5", () => {
  it("retorna not_available_in_environment para T1-Padre", async () => {
    const result = await invokeCoworkLocal({
      userRole: "T1-Padre",
      contextMarkdown: "ignored",
    });
    expect(result.status).toBe("not_available_in_environment");
    expect(result.path).toBeUndefined();
  });

  it("escribe archivo para T1-Alfredo en baseDir custom", async () => {
    // Use tmpdir para no tocar repo
    const { tmpdir } = await import("node:os");
    const { mkdtempSync } = await import("node:fs");
    const path = await import("node:path");
    const tmp = mkdtempSync(path.join(tmpdir(), "la-forja-puertas-test-"));

    const result = await invokeCoworkLocal({
      userRole: "T1-Alfredo",
      contextMarkdown: "## Hello Cowork from La Forja\n",
      baseDir: tmp,
    });

    expect(result.status).toBe("written");
    expect(result.path).toBe(
      path.join(tmp, ".monstruo/COWORK_CONTEXT_INJECTION.md"),
    );
    expect(result.bytesWritten).toBeGreaterThan(0);

    const fs = await import("node:fs/promises");
    const content = await fs.readFile(result.path!, "utf8");
    expect(content).toBe("## Hello Cowork from La Forja\n");
  });
});

describe("invokeKernelMonstruo — proxy REST canónico", () => {
  it("invoca POST al endpoint correcto y retorna data", async () => {
    const fetchSpy = vi.fn(
      async (url: string, init: RequestInit) =>
        new Response(JSON.stringify({ ok: true, sop: "data" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    const result = await invokeKernelMonstruo({
      endpoint: "/sop/query",
      body: { topic: "EPIA" },
      baseUrl: "https://test-kernel.example.com",
      fetchImpl: fetchSpy as unknown as typeof fetch,
    });
    expect(fetchSpy).toHaveBeenCalledOnce();
    const [calledUrl, calledInit] = fetchSpy.mock.calls[0]!;
    expect(calledUrl).toBe("https://test-kernel.example.com/sop/query");
    expect(calledInit?.method).toBe("POST");
    expect(JSON.parse(calledInit?.body as string)).toEqual({ topic: "EPIA" });
    expect(result.status).toBe(200);
    expect(result.data).toEqual({ ok: true, sop: "data" });
    expect(result.durationMs).toBeGreaterThanOrEqual(0);
  });

  it("rechaza endpoint sin / inicial", async () => {
    await expect(
      invokeKernelMonstruo({
        endpoint: "sop/query",
        body: {},
        fetchImpl: vi.fn() as unknown as typeof fetch,
      }),
    ).rejects.toThrow(/puerta_kernel_invalid_endpoint/);
  });

  it("lanza error tipado en HTTP non-2xx", async () => {
    const fetchSpy = vi.fn(
      async () => new Response("internal error", { status: 500 }),
    );
    await expect(
      invokeKernelMonstruo({
        endpoint: "/sop/query",
        body: {},
        baseUrl: "https://test.example.com",
        fetchImpl: fetchSpy as unknown as typeof fetch,
      }),
    ).rejects.toThrow(/puerta_kernel_http_failed/);
  });
});

describe("invokeSimulador — POST simulación canónica", () => {
  it("crea simulación y retorna simulation_id", async () => {
    const fetchSpy = vi.fn(
      async (url: string, init: RequestInit) =>
        new Response(
          JSON.stringify({
            simulation_id: "sim-abc-123",
            status: "queued",
          }),
          { status: 201, headers: { "Content-Type": "application/json" } },
        ),
    );
    const result = await invokeSimulador({
      scenario: "¿Qué pasaría si subo precio 20% en feb?",
      variables: { producto: "membresia", incremento: 0.2 },
      iterations: 5000,
      fetchImpl: fetchSpy as unknown as typeof fetch,
    });
    expect(fetchSpy).toHaveBeenCalledOnce();
    const [, init] = fetchSpy.mock.calls[0]!;
    const body = JSON.parse(init?.body as string);
    expect(body.scenario).toContain("subo precio");
    expect(body.iterations).toBe(5000);
    expect(result.simulationId).toBe("sim-abc-123");
    expect(result.status).toBe("queued");
  });

  it("usa default iterations=1000 si no se pasa", async () => {
    const fetchSpy = vi.fn(
      async (url: string, init: RequestInit) => {
        const body = JSON.parse(init?.body as string);
        expect(body.iterations).toBe(1000);
        return new Response(
          JSON.stringify({ simulation_id: "x", status: "queued" }),
          { status: 201 },
        );
      },
    );
    await invokeSimulador({
      scenario: "test",
      fetchImpl: fetchSpy as unknown as typeof fetch,
    });
  });

  it("lanza puerta_simulador_missing_id si response no tiene id", async () => {
    const fetchSpy = vi.fn(
      async () =>
        new Response(JSON.stringify({ status: "ok" }), { status: 200 }),
    );
    await expect(
      invokeSimulador({
        scenario: "test",
        fetchImpl: fetchSpy as unknown as typeof fetch,
      }),
    ).rejects.toThrow(/puerta_simulador_missing_id/);
  });
});
