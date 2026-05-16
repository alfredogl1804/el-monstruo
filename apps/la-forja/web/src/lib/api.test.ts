/**
 * La Forja — tests para buildForjaApi (D3.0).
 * Mockea fetch global para verificar shape sin pegarle al backend.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { buildForjaApi, ForjaApiError } from "./api";

describe("buildForjaApi (D3.0)", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("health() retorna data en 200 OK con shape backend Hono", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          status: "ok",
          service: "la-forja-api",
          version: "0.1.0",
          timestamp: "2026-05-15T23:55:00Z",
        }),
        { status: 200, headers: { "content-type": "application/json" } },
      ),
    );
    const api = buildForjaApi({ apiUrl: "http://localhost:3000" });
    const out = await api.health();
    expect(out.status).toBe("ok");
    expect(out.service).toBe("la-forja-api");
    expect(out.version).toBe("0.1.0");
    expect(out.timestamp).toBe("2026-05-15T23:55:00Z");
  });

  it("health() lanza ForjaApiError en non-2xx con shape de error de marca", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(JSON.stringify({ error: "down" }), {
        status: 503,
        headers: { "content-type": "application/json" },
      }),
    );
    const api = buildForjaApi({ apiUrl: "http://localhost:3000" });
    let caught: unknown;
    try {
      await api.health();
    } catch (e) {
      caught = e;
    }
    expect(caught).toBeInstanceOf(ForjaApiError);
    expect((caught as ForjaApiError).status).toBe(503);
    expect((caught as ForjaApiError).message).toMatch(
      /\[la-forja:web_api_request_failed\]/,
    );
  });

  it("envía header x-request-id en cada request", async () => {
    const mockFetch = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          status: "ok",
          commit: "test",
          ts: "2026-01-01T00:00:00Z",
        }),
        { status: 200 },
      ),
    );
    vi.stubGlobal("fetch", mockFetch);
    const api = buildForjaApi({ apiUrl: "http://localhost:3000" });
    await api.health();
    const init = mockFetch.mock.calls[0]?.[1];
    expect(init?.headers).toHaveProperty("x-request-id");
    expect(typeof init.headers["x-request-id"]).toBe("string");
  });
});
