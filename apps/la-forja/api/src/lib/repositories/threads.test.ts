/**
 * La Forja — Tests repository forja_threads + forja_messages + forja_validations.
 *
 * Sprint LA-FORJA-001 v3.2 — D5.2.
 *
 * Validación binaria:
 *   1. ensureThread retorna id existente si profile_id matches
 *   2. ensureThread crea nuevo thread si desiredThreadId no existe (anti-IDOR)
 *   3. ensureThread crea nuevo si no se pasa desiredThreadId
 *   4. appendUserMessage retorna message id
 *   5. appendAssistantMessage acumula counters en forja_threads
 *   6. recordValidation persiste citation_count materializado
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  ensureThread,
  appendUserMessage,
  appendAssistantMessage,
  recordValidation,
} from "./threads";

// Setup builder genérico de mock-chains. Cada test re-declara según necesidad.
const mockSingle = vi.fn();
const mockMaybeSingle = vi.fn();
const mockEqProfile = vi.fn(() => ({ maybeSingle: mockMaybeSingle }));
const mockEqId = vi.fn(() => ({ eq: mockEqProfile, maybeSingle: mockMaybeSingle }));
const mockSelectChain = vi.fn(() => ({
  eq: mockEqId,
  single: mockSingle,
}));
const mockInsertSelect = vi.fn(() => ({ single: mockSingle }));
const mockInsert = vi.fn(() => ({ select: mockInsertSelect }));
const mockUpdateEq = vi.fn(() => Promise.resolve({ error: null }));
const mockUpdate = vi.fn(() => ({ eq: mockUpdateEq }));

const mockFrom = vi.fn(() => ({
  select: mockSelectChain,
  insert: mockInsert,
  update: mockUpdate,
}));

vi.mock("../supabase", () => ({
  getSupabase: () => ({ from: mockFrom }),
  _resetSupabaseCache: () => undefined,
}));

const PROFILE_ID = "aaaa1111-2222-3333-4444-555555555555";
const THREAD_ID = "tttt1111-2222-3333-4444-555555555555";
const MSG_ID = "mmmm1111-2222-3333-4444-555555555555";

beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("ensureThread", () => {
  it("retorna id existente si desiredThreadId pertenece al profile", async () => {
    mockMaybeSingle.mockResolvedValueOnce({
      data: { id: THREAD_ID },
      error: null,
    });

    const result = await ensureThread(PROFILE_ID, THREAD_ID);
    expect(result).toBe(THREAD_ID);
    expect(mockInsert).not.toHaveBeenCalled();
  });

  it("crea nuevo thread si desiredThreadId NO existe (anti-IDOR)", async () => {
    mockMaybeSingle.mockResolvedValueOnce({ data: null, error: null });
    mockSingle.mockResolvedValueOnce({
      data: { id: "new-thread-id" },
      error: null,
    });

    const result = await ensureThread(PROFILE_ID, "fake-id-from-client");
    expect(result).toBe("new-thread-id");
    expect(mockInsert).toHaveBeenCalledOnce();
    const row = mockInsert.mock.calls[0]![0] as { profile_id: string; title: string };
    expect(row.profile_id).toBe(PROFILE_ID);
    expect(row.title).toBe("Hilo sin título");
  });

  it("crea nuevo thread si no se pasa desiredThreadId", async () => {
    mockSingle.mockResolvedValueOnce({
      data: { id: "fresh-thread-id" },
      error: null,
    });

    const result = await ensureThread(PROFILE_ID);
    expect(result).toBe("fresh-thread-id");
    expect(mockInsert).toHaveBeenCalledOnce();
  });
});

describe("appendUserMessage", () => {
  it("INSERT en forja_messages con role=user y retorna id", async () => {
    mockSingle.mockResolvedValueOnce({ data: { id: MSG_ID }, error: null });

    const result = await appendUserMessage(THREAD_ID, "Hola tutor");
    expect(result).toBe(MSG_ID);

    const row = mockInsert.mock.calls[0]![0] as {
      thread_id: string;
      role: string;
      content: string;
    };
    expect(row.thread_id).toBe(THREAD_ID);
    expect(row.role).toBe("user");
    expect(row.content).toBe("Hola tutor");
  });

  it("fail-loud con error de Supabase", async () => {
    mockSingle.mockResolvedValueOnce({
      data: null,
      error: { message: "RLS denied" },
    });

    await expect(
      appendUserMessage(THREAD_ID, "test"),
    ).rejects.toThrow(/\[la-forja:messages_user_insert_failed\]/);
  });
});

describe("appendAssistantMessage", () => {
  it("INSERT message + UPDATE counters del thread", async () => {
    // 1ª llamada: INSERT message
    mockSingle.mockResolvedValueOnce({ data: { id: MSG_ID }, error: null });
    // 2ª llamada: SELECT counters actuales
    mockMaybeSingle.mockResolvedValueOnce({
      data: {
        message_count: 4,
        total_tokens_in: "100",
        total_tokens_out: "200",
        total_usd: "0.05",
      },
      error: null,
    });

    const result = await appendAssistantMessage(THREAD_ID, {
      content: "Respuesta",
      model: "claude-opus-4-7",
      tokensIn: 50,
      tokensOut: 75,
      costUsd: 0.01,
      requireValidation: true,
      citations: ["https://example.com/a", "https://example.com/b"],
      latencyMs: 1234,
    });

    expect(result).toBe(MSG_ID);

    const insertRow = mockInsert.mock.calls[0]![0] as {
      role: string;
      model: string;
      tokens_in: number;
      tokens_out: number;
      latency_ms: number;
      require_validation: boolean;
      citations: string[];
    };
    expect(insertRow.role).toBe("assistant");
    expect(insertRow.model).toBe("claude-opus-4-7");
    expect(insertRow.tokens_in).toBe(50);
    expect(insertRow.tokens_out).toBe(75);
    expect(insertRow.latency_ms).toBe(1234);
    expect(insertRow.require_validation).toBe(true);
    expect(insertRow.citations).toEqual([
      "https://example.com/a",
      "https://example.com/b",
    ]);

    const updateRow = mockUpdate.mock.calls[0]![0] as {
      message_count: number;
      total_tokens_in: number;
      total_tokens_out: number;
      total_usd: number;
    };
    // 4 + (user+assistant) = 6
    expect(updateRow.message_count).toBe(6);
    expect(updateRow.total_tokens_in).toBe(150);
    expect(updateRow.total_tokens_out).toBe(275);
    expect(updateRow.total_usd).toBeCloseTo(0.06, 6);
  });
});

describe("recordValidation", () => {
  it("INSERT en forja_validations con citation_count materializado", async () => {
    mockSingle.mockResolvedValueOnce({
      data: { id: "vvvv-1111" },
      error: null,
    });

    const result = await recordValidation(THREAD_ID, PROFILE_ID, {
      messageId: MSG_ID,
      topic: "TypeScript generics",
      query: "How do generic type constraints work?",
      model: "perplexity-sonar-reasoning-pro",
      citations: [
        "https://typescript.dev/a",
        "https://typescript.dev/b",
        "https://typescript.dev/c",
      ],
      costUsd: 0.005,
      latencyMs: 800,
    });

    expect(result).toBe("vvvv-1111");
    const row = mockInsert.mock.calls[0]![0] as {
      thread_id: string;
      profile_id: string;
      provider: string;
      citation_count: number;
      status: string;
    };
    expect(row.thread_id).toBe(THREAD_ID);
    expect(row.profile_id).toBe(PROFILE_ID);
    expect(row.provider).toBe("perplexity");
    expect(row.citation_count).toBe(3);
    expect(row.status).toBe("completed");
  });
});
