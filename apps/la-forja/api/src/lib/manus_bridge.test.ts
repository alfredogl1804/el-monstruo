/**
 * manus_bridge — vitest specs (paridad con tools/manus_bridge.py).
 * Sprint LA-FORJA-001 v3.2 — D1 no-SQL.
 *
 * Cubre:
 *   - Resolución de API key con .trim() defensivo
 *   - Rate limiter (5 calls/hora)
 *   - F-pattern #11: UUID 22-char vs etiqueta lógica
 *   - Response unwrapping {ok:true, data:{...}}
 *   - Retry con backoff exponencial
 *   - Dispatcher handleManusBridge
 *   - Excepciones tipadas
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  _resetRateLimit,
  createTask,
  getTaskStatus,
  handleManusBridge,
  ManusBridgeError,
  ManusRateLimitError,
  ManusTaskFailedError,
  ManusTimeoutError,
  setAntiDoryBrokerFactory,
  waitForCompletion,
} from "./manus_bridge.js";

const ORIGINAL_ENV = { ...process.env };

beforeEach(() => {
  process.env["MANUS_API_KEY_GOOGLE"] = "test-google-key";
  process.env["MANUS_API_KEY_APPLE"] = "test-apple-key";
  process.env["MANUS_API_BASE_URL"] = "https://api.manus.test";
  _resetRateLimit();
  setAntiDoryBrokerFactory(null);
});

afterEach(() => {
  process.env = { ...ORIGINAL_ENV };
  _resetRateLimit();
  setAntiDoryBrokerFactory(null);
  vi.restoreAllMocks();
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mockJsonResponse(body: unknown, init: { ok?: boolean; status?: number } = {}) {
  return {
    ok: init.ok ?? true,
    status: init.status ?? 200,
    statusText: "OK",
    json: async () => body,
    text: async () => JSON.stringify(body),
  } as unknown as Response;
}

// ---------------------------------------------------------------------------
// createTask
// ---------------------------------------------------------------------------

describe("createTask", () => {
  it("creates a task and unwraps {ok, data} response envelope", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({
        ok: true,
        data: { task_id: "abc123", status: "running" },
      }),
    );

    const result = await createTask("hola", { fetchImpl });

    expect(result.task_id).toBe("abc123");
    expect(result.status).toBe("running");
    expect(fetchImpl).toHaveBeenCalledTimes(1);
    const callArgs = fetchImpl.mock.calls[0]!;
    expect(callArgs[0]).toContain("/v2/task.create");
    const init = callArgs[1] as RequestInit;
    expect(init.method).toBe("POST");
    const headers = init.headers as Record<string, string>;
    expect(headers["x-manus-api-key"]).toBe("test-google-key");
    expect(headers["Authorization"]).toBeUndefined();
  });

  it("forwards 22-char UUID project_id to payload", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({ data: { task_id: "t1", status: "ok" } }),
    );

    const validUuid = "ABC123def456GHI789jkl0"; // 22 alphanumeric chars
    expect(validUuid).toHaveLength(22);
    await createTask("test", { fetchImpl, project_id: validUuid });

    const init = fetchImpl.mock.calls[0]![1] as RequestInit;
    const body = JSON.parse(init.body as string) as Record<string, unknown>;
    expect(body["project_id"]).toBe(validUuid);
  });

  it("does NOT forward logical-label project_id (F-pattern #11 mitigation)", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({ data: { task_id: "t2", status: "ok" } }),
    );

    await createTask("test", { fetchImpl, project_id: "el_monstruo" });

    const init = fetchImpl.mock.calls[0]![1] as RequestInit;
    const body = JSON.parse(init.body as string) as Record<string, unknown>;
    expect(body["project_id"]).toBeUndefined();
    expect(body["message"]).toEqual({ content: "test" });
  });

  it("uses 'apple' account when specified", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({ data: { task_id: "t3", status: "ok" } }),
    );

    await createTask("test", { fetchImpl, account: "apple" });

    const init = fetchImpl.mock.calls[0]![1] as RequestInit;
    const headers = init.headers as Record<string, string>;
    expect(headers["x-manus-api-key"]).toBe("test-apple-key");
  });

  it("auto-trims whitespace in API key (incidente 2026-05-12)", async () => {
    process.env["MANUS_API_KEY_GOOGLE"] = "  whitespace-key  \n";
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({ data: { task_id: "t4", status: "ok" } }),
    );

    await createTask("test", { fetchImpl });

    const init = fetchImpl.mock.calls[0]![1] as RequestInit;
    const headers = init.headers as Record<string, string>;
    expect(headers["x-manus-api-key"]).toBe("whitespace-key");
  });

  it("raises if API key env var is missing", async () => {
    delete process.env["MANUS_API_KEY_GOOGLE"];
    const fetchImpl = vi.fn();

    await expect(createTask("test", { fetchImpl })).rejects.toThrow(
      /MANUS_API_KEY_GOOGLE is not set/,
    );
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("enforces rate limit: 5 calls/hour", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({ data: { task_id: "t", status: "ok" } }),
    );

    for (let i = 0; i < 5; i += 1) {
      await createTask(`call-${i}`, { fetchImpl });
    }

    await expect(createTask("call-6", { fetchImpl })).rejects.toThrow(
      ManusRateLimitError,
    );
  });
});

// ---------------------------------------------------------------------------
// getTaskStatus
// ---------------------------------------------------------------------------

describe("getTaskStatus", () => {
  it("queries v2/task.get with task_id query param", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({
        ok: true,
        data: { task_id: "xyz", status: "running" },
      }),
    );

    const result = await getTaskStatus("xyz", { fetchImpl });

    expect(result.status).toBe("running");
    const url = fetchImpl.mock.calls[0]![0] as string;
    expect(url).toContain("/v2/task.get");
    expect(url).toContain("task_id=xyz");
  });

  it("handles unwrapped responses (no {ok, data} envelope)", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({ task_id: "raw", status: "running" }),
    );

    const result = await getTaskStatus("raw", { fetchImpl });
    expect(result.task_id).toBe("raw");
  });
});

// ---------------------------------------------------------------------------
// Retry logic
// ---------------------------------------------------------------------------

describe("retry with exponential backoff", () => {
  it("retries up to 3 times then throws ManusBridgeError", async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new Error("network down"));
    const sleep = vi.fn().mockResolvedValue(undefined);

    await expect(
      createTask("retry-test", { fetchImpl, sleep }),
    ).rejects.toThrow(ManusBridgeError);

    expect(fetchImpl).toHaveBeenCalledTimes(3);
    // Sleep solo entre attempts (no después del último).
    // Backoff: 2^attempt * 1000 → 2000ms (entre 1⁢2) y 4000ms (entre 2⁢3).
    expect(sleep).toHaveBeenCalledTimes(2);
    expect(sleep).toHaveBeenNthCalledWith(1, 2_000);
    expect(sleep).toHaveBeenNthCalledWith(2, 4_000);
  });

  it("returns success if a retry attempt succeeds", async () => {
    const fetchImpl = vi
      .fn()
      .mockRejectedValueOnce(new Error("transient"))
      .mockResolvedValueOnce(
        mockJsonResponse({ data: { task_id: "ok-after-retry", status: "ok" } }),
      );
    const sleep = vi.fn().mockResolvedValue(undefined);

    const result = await createTask("retry-recover", { fetchImpl, sleep });

    expect(result.task_id).toBe("ok-after-retry");
    expect(fetchImpl).toHaveBeenCalledTimes(2);
    expect(sleep).toHaveBeenCalledTimes(1);
  });
});

// ---------------------------------------------------------------------------
// waitForCompletion
// ---------------------------------------------------------------------------

describe("waitForCompletion", () => {
  it("resolves when status becomes 'completed'", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(
        mockJsonResponse({ data: { task_id: "w1", status: "running" } }),
      )
      .mockResolvedValueOnce(
        mockJsonResponse({ data: { task_id: "w1", status: "completed", output: "done" } }),
      );
    const sleep = vi.fn().mockResolvedValue(undefined);

    const result = await waitForCompletion("w1", {
      fetchImpl,
      sleep,
      pollInterval: 100,
      timeout: 10_000,
    });

    expect(result.status).toBe("completed");
    expect(result.output).toBe("done");
  });

  it("throws ManusTaskFailedError when status is 'failed'", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({ data: { task_id: "w2", status: "failed", output: "boom" } }),
    );
    const sleep = vi.fn().mockResolvedValue(undefined);

    await expect(
      waitForCompletion("w2", { fetchImpl, sleep, pollInterval: 10, timeout: 5_000 }),
    ).rejects.toThrow(ManusTaskFailedError);
  });

  it("throws ManusTimeoutError when timeout is exceeded", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({ data: { task_id: "w3", status: "running" } }),
    );
    const sleep = vi.fn().mockResolvedValue(undefined);

    await expect(
      waitForCompletion("w3", {
        fetchImpl,
        sleep,
        pollInterval: 10,
        timeout: 1, // 1ms — guaranteed timeout on first poll
      }),
    ).rejects.toThrow(ManusTimeoutError);
  });
});

// ---------------------------------------------------------------------------
// handleManusBridge dispatcher
// ---------------------------------------------------------------------------

describe("handleManusBridge", () => {
  it("returns error when prompt is missing for create_task", async () => {
    const result = await handleManusBridge({ action: "create_task" });
    expect(result.error).toMatch(/Missing 'prompt'/);
  });

  it("returns error when task_id is missing for get_status", async () => {
    const result = await handleManusBridge({ action: "get_status" });
    expect(result.error).toMatch(/Missing 'task_id'/);
  });

  it("returns error for unknown action", async () => {
    const result = await handleManusBridge({
      // @ts-expect-error testing runtime guard
      action: "wat",
    });
    expect(result.error).toMatch(/Unknown action/);
  });

  it("wraps ManusRateLimitError with type='rate_limit'", async () => {
    // Pre-fill rate limit
    for (let i = 0; i < 5; i += 1) {
      // @ts-expect-error accessing internal for test setup
      const _ = i;
    }
    // Use a stub fetch that succeeds, then exhaust rate limit
    const fetchImpl = vi.fn().mockResolvedValue(
      mockJsonResponse({ data: { task_id: "x", status: "ok" } }),
    );
    // Monkey-patch global fetch for handleManusBridge (which uses default fetch)
    const originalFetch = globalThis.fetch;
    globalThis.fetch = fetchImpl as unknown as typeof fetch;

    try {
      for (let i = 0; i < 5; i += 1) {
        await handleManusBridge({ action: "create_task", prompt: `p-${i}` });
      }
      const result = await handleManusBridge({
        action: "create_task",
        prompt: "blocked",
      });
      expect(result.type).toBe("rate_limit");
      expect(result.error).toMatch(/Rate limit reached/);
    } finally {
      globalThis.fetch = originalFetch;
    }
  });
});

// ---------------------------------------------------------------------------
// Exception inheritance
// ---------------------------------------------------------------------------

describe("typed exceptions", () => {
  it("ManusTimeoutError extends ManusBridgeError", () => {
    const err = new ManusTimeoutError("t");
    expect(err).toBeInstanceOf(ManusBridgeError);
    expect(err).toBeInstanceOf(Error);
    expect(err.name).toBe("ManusTimeoutError");
  });

  it("ManusTaskFailedError extends ManusBridgeError", () => {
    const err = new ManusTaskFailedError("t");
    expect(err).toBeInstanceOf(ManusBridgeError);
    expect(err.name).toBe("ManusTaskFailedError");
  });

  it("ManusRateLimitError extends ManusBridgeError", () => {
    const err = new ManusRateLimitError("t");
    expect(err).toBeInstanceOf(ManusBridgeError);
    expect(err.name).toBe("ManusRateLimitError");
  });
});
