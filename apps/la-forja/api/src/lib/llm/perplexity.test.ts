/**
 * La Forja — Tests Perplexity client (D2.2).
 *
 * Validación binaria:
 *   - URL exacto api.perplexity.ai/chat/completions
 *   - Modelo sonar-reasoning-pro hardcoded
 *   - Header Authorization Bearer correcto
 *   - Citations array preservado en respuesta
 *   - Errores HTTP wrap con prefix la-forja:perplexity_*
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { _resetEnvCache } from "../env";
import {
  PERPLEXITY_API_URL,
  PERPLEXITY_MAGNA_MODEL,
  invokeMagnaValidation,
} from "./perplexity";

const VALID_ENV: Record<string, string> = {
  MANUS_API_KEY_GOOGLE: "x",
  MANUS_API_KEY_APPLE: "x",
  ANTHROPIC_API_KEY: "x",
  OPENAI_API_KEY: "x",
  GEMINI_API_KEY: "x",
  SONAR_API_KEY: "test-sonar-magna-key",
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

const buildResponse = (body: object, status = 200): Response =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });

describe("invokeMagnaValidation", () => {
  it("invoca POST al endpoint canónico con modelo Sonar Reasoning Pro", async () => {
    const fetchSpy = vi.fn(async (url: string, init: RequestInit) => {
      expect(url).toBe(PERPLEXITY_API_URL);
      expect(init.method).toBe("POST");
      expect((init.headers as Record<string, string>)["Authorization"]).toBe(
        "Bearer test-sonar-magna-key",
      );
      expect((init.headers as Record<string, string>)["Content-Type"]).toBe(
        "application/json",
      );
      const body = JSON.parse(init.body as string);
      expect(body.model).toBe(PERPLEXITY_MAGNA_MODEL);
      expect(body.model).toBe("sonar-reasoning-pro");
      return buildResponse({
        id: "abc",
        model: PERPLEXITY_MAGNA_MODEL,
        citations: ["https://example.com/source1", "https://example.com/source2"],
        choices: [
          {
            message: {
              role: "assistant",
              content: "Next.js latest is 16.2 [1][2].",
            },
            finish_reason: "stop",
          },
        ],
        usage: {
          prompt_tokens: 50,
          completion_tokens: 20,
          total_tokens: 70,
        },
      });
    });

    const res = await invokeMagnaValidation(
      {
        messages: [
          { role: "user", content: "What is the current Next.js version?" },
        ],
      },
      { fetchImpl: fetchSpy as unknown as typeof fetch },
    );

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(res.content).toBe("Next.js latest is 16.2 [1][2].");
    expect(res.citations).toEqual([
      "https://example.com/source1",
      "https://example.com/source2",
    ]);
    expect(res.inputTokens).toBe(50);
    expect(res.outputTokens).toBe(20);
    expect(res.model).toBe(PERPLEXITY_MAGNA_MODEL);
  });

  it("retorna citations vacío si la API no las incluye", async () => {
    const fetchSpy = vi.fn(async () =>
      buildResponse({
        id: "abc",
        model: PERPLEXITY_MAGNA_MODEL,
        choices: [
          {
            message: { role: "assistant", content: "no sources cited" },
            finish_reason: "stop",
          },
        ],
        usage: { prompt_tokens: 5, completion_tokens: 5, total_tokens: 10 },
      }),
    );

    const res = await invokeMagnaValidation(
      { messages: [{ role: "user", content: "x" }] },
      { fetchImpl: fetchSpy as unknown as typeof fetch },
    );

    expect(res.citations).toEqual([]);
  });

  it("lanza error tipado en HTTP non-2xx", async () => {
    const fetchSpy = vi.fn(async () =>
      buildResponse({ error: "rate_limited" }, 429),
    );
    await expect(
      invokeMagnaValidation(
        { messages: [{ role: "user", content: "x" }] },
        { fetchImpl: fetchSpy as unknown as typeof fetch },
      ),
    ).rejects.toThrow(/perplexity_validation_http_failed/);
  });

  it("lanza error tipado si choices está vacío", async () => {
    const fetchSpy = vi.fn(async () =>
      buildResponse({
        id: "abc",
        model: PERPLEXITY_MAGNA_MODEL,
        choices: [],
        usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
      }),
    );
    await expect(
      invokeMagnaValidation(
        { messages: [{ role: "user", content: "x" }] },
        { fetchImpl: fetchSpy as unknown as typeof fetch },
      ),
    ).rejects.toThrow(/perplexity_validation_empty_response/);
  });
});
