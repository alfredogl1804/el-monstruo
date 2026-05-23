/**
 * La Forja — Circuit Breaker pre-call tests (Sprint D6-CREDITS-RESTORE-001).
 *
 * Cobertura binaria de los 4 tests obligatorios del spec D6 §2.4 multiplicado
 * por 2 clientes (Anthropic + OpenAI) = 8 tests dedicados.
 *
 * Estos tests son unit-level puro: invocan los helpers internos del módulo
 * (_maybeTripCircuit, _assertCircuitClosed, _getCircuitState,
 * _resetCircuitBreaker) sin mockear los SDKs Anthropic/OpenAI.
 *
 * Esto valida la LÓGICA del breaker independiente de cualquier llamada al
 * API real, lo cual es la responsabilidad del breaker (decidir si llamar al
 * API o fail-fast).
 *
 * Spec D6 §2.4 — los 4 tests obligatorios:
 *   1. circuit breaker opens on credit_balance_too_low response
 *   2. circuit breaker fails fast within 5min cooldown window
 *   3. circuit breaker auto-resets after 5min
 *   4. circuit breaker does NOT trigger on other errors (rate-limit, timeout)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

// Importamos los helpers internos exportados con prefix `_` (convención de
// "module-private but testable") + las funciones públicas para test 5min cooldown
// vía mock de Date.now().
import {
  _resetAnthropicCircuitBreaker,
  _getAnthropicCircuitState,
} from "./anthropic.js";
import {
  _resetOpenAICircuitBreaker,
  _getOpenAICircuitState,
} from "./openai.js";

// Importamos también los módulos completos para acceder a los helpers privados
// `_maybeTripCircuit` y `_assertCircuitClosed` via dynamic import. Como no
// están exportados, usamos un test indirecto a través de invokeTutor /
// invokeSprintCopilot mockeando solo el cliente SDK underlying.

import * as anthropicModule from "./anthropic.js";
import * as openaiModule from "./openai.js";

// ---------------------------------------------------------------------------
// Mock SDK clients underlying. Este patrón mockea el ESTADO del cliente
// cacheado dentro del módulo, NO el package npm completo. Esto preserva la
// lógica del circuit breaker (que vive en el módulo) y solo simula la
// respuesta API.
// ---------------------------------------------------------------------------

// Mock @anthropic-ai/sdk para invokeTutor — controlamos lo que devuelve
// client.messages.create().
const mockAnthropicCreate = vi.fn();
vi.mock("@anthropic-ai/sdk", () => ({
  default: vi.fn().mockImplementation(() => ({
    messages: {
      create: mockAnthropicCreate,
    },
  })),
}));

// Mock openai para invokeSprintCopilot — controlamos client.responses.create().
const mockOpenAIResponsesCreate = vi.fn();
vi.mock("openai", () => ({
  default: vi.fn().mockImplementation(() => ({
    responses: {
      create: mockOpenAIResponsesCreate,
    },
  })),
}));

// Mock loadEnv para que no intente leer archivos .env reales.
vi.mock("../env.js", () => ({
  loadEnv: vi.fn(() => ({
    ANTHROPIC_API_KEY: "sk-ant-test",
    OPENAI_API_KEY: "sk-test",
  })),
}));

// Mock @ai-sdk/anthropic createAnthropic (usado por buildTutorStream — no lo
// testeamos aquí pero el mock evita que el módulo crashee al importar).
vi.mock("@ai-sdk/anthropic", () => ({
  createAnthropic: vi.fn(() => () => ({})),
}));

// Mock 'ai' streamText — buildTutorStream lo usa. No relevante a estos tests.
vi.mock("ai", async () => {
  const actual = await vi.importActual<typeof import("ai")>("ai");
  return {
    ...actual,
    streamText: vi.fn(() => ({
      toUIMessageStreamResponse: vi.fn(),
      finishReason: "stop",
    })),
  };
});

// ---------------------------------------------------------------------------
// Helper: forzar un estado credit-depleted llamando a una función pública
// que internamente invoca _maybeTripCircuit() vía catch. Esto cubre el
// camino real del código.
// ---------------------------------------------------------------------------

async function tripAnthropicViaError(errorMessage: string): Promise<void> {
  mockAnthropicCreate.mockRejectedValueOnce(new Error(errorMessage));
  try {
    await anthropicModule.invokeTutor({
      messages: [{ role: "user", content: "test" }],
    });
  } catch {
    // Esperado — el invokeTutor re-throw el error después de tripCircuit.
  }
}

async function tripOpenAIViaError(errorMessage: string): Promise<void> {
  mockOpenAIResponsesCreate.mockRejectedValueOnce(new Error(errorMessage));
  try {
    await openaiModule.invokeSprintCopilot({
      input: [{ role: "user", content: "test" }],
    });
  } catch {
    // Esperado — el invokeSprintCopilot re-throw el error después de tripCircuit.
  }
}

// ---------------------------------------------------------------------------
// Suite Anthropic Circuit Breaker
// ---------------------------------------------------------------------------

describe("Anthropic Circuit Breaker (Sprint D6 §2.4)", () => {
  beforeEach(() => {
    _resetAnthropicCircuitBreaker();
    mockAnthropicCreate.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
    _resetAnthropicCircuitBreaker();
  });

  it("Test 1: opens on credit_balance_too_low response", async () => {
    // Estado inicial: cerrado.
    expect(_getAnthropicCircuitState().open).toBe(false);

    // Simular API rechaza con mensaje credit-depleted.
    await tripAnthropicViaError(
      "400 Bad Request: Your credit balance is too low to access the Anthropic API",
    );

    // El circuit DEBE estar abierto.
    const state = _getAnthropicCircuitState();
    expect(state.open).toBe(true);
    expect(state.cooldownUntil).not.toBeNull();
    expect(state.cooldownUntil!).toBeGreaterThan(Date.now());
  });

  it("Test 2: fails fast within 5min cooldown window with [la-forja:anthropic_credit_depleted]", async () => {
    // Trip el circuit primero.
    await tripAnthropicViaError("credit balance is too low");
    expect(_getAnthropicCircuitState().open).toBe(true);

    // Intentar invocar de nuevo: debe throw IMMEDIATAMENTE sin tocar el SDK.
    mockAnthropicCreate.mockClear();
    let thrown: Error | null = null;
    try {
      await anthropicModule.invokeTutor({
        messages: [{ role: "user", content: "test" }],
      });
    } catch (e) {
      thrown = e as Error;
    }

    expect(thrown).not.toBeNull();
    expect(thrown!.message).toContain("[la-forja:anthropic_credit_depleted]");
    expect(thrown!.message).toContain("circuit breaker open until");
    // Confirmación binaria: el SDK NO fue invocado (fail-fast verdadero).
    expect(mockAnthropicCreate).not.toHaveBeenCalled();
  });

  it("Test 3: auto-resets after 5min cooldown", async () => {
    // Trip el circuit.
    const tripStart = Date.now();
    vi.useFakeTimers();
    vi.setSystemTime(tripStart);
    await tripAnthropicViaError("credit balance is too low");
    expect(_getAnthropicCircuitState().open).toBe(true);

    // Reset del spy para que el conteo de invocaciones empiece limpio post-trip.
    // (El trip ya consumió 1 invocación al mock — la rejected con error.)
    mockAnthropicCreate.mockClear();

    // Avanzar el reloj 5 minutos + 1 segundo (cooldown completo + margin).
    vi.setSystemTime(tripStart + 5 * 60 * 1000 + 1000);

    // El circuit DEBE estar cerrado (auto-reset por _assertCircuitClosed).
    // Pero como el flag se limpia lazy, primero invocamos algo que lo verifique.
    mockAnthropicCreate.mockResolvedValueOnce({
      content: [{ type: "text", text: "ok" }],
      usage: { input_tokens: 10, output_tokens: 5 },
      model: "claude-opus-4-7",
      stop_reason: "end_turn",
    });

    const result = await anthropicModule.invokeTutor({
      messages: [{ role: "user", content: "test" }],
    });

    // El SDK SÍ fue invocado (circuit cerrado), y devolvió la respuesta mock.
    expect(mockAnthropicCreate).toHaveBeenCalledOnce();
    expect(result.content).toBe("ok");
    expect(_getAnthropicCircuitState().open).toBe(false);
  });

  it("Test 4: does NOT trigger on other errors (rate-limit, timeout)", async () => {
    // Errores que NO son credit-depleted: rate-limit, timeout, network error.
    const nonCreditErrors = [
      "429 Too Many Requests: rate limit exceeded",
      "ETIMEDOUT: connection timeout",
      "fetch failed: network error",
      "500 Internal Server Error",
      "401 Unauthorized: invalid api key", // NO contiene "credit balance"
    ];

    for (const errMsg of nonCreditErrors) {
      _resetAnthropicCircuitBreaker();
      await tripAnthropicViaError(errMsg);
      // El circuit DEBE seguir cerrado.
      expect(_getAnthropicCircuitState().open).toBe(false);
    }
  });
});

// ---------------------------------------------------------------------------
// Suite OpenAI Circuit Breaker
// ---------------------------------------------------------------------------

describe("OpenAI Circuit Breaker (Sprint D6 §2.4)", () => {
  beforeEach(() => {
    _resetOpenAICircuitBreaker();
    mockOpenAIResponsesCreate.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
    _resetOpenAICircuitBreaker();
  });

  it("Test 1: opens on insufficient_quota response", async () => {
    expect(_getOpenAICircuitState().open).toBe(false);

    await tripOpenAIViaError(
      "429 You exceeded your current quota, please check your plan and billing details. (insufficient_quota)",
    );

    const state = _getOpenAICircuitState();
    expect(state.open).toBe(true);
    expect(state.cooldownUntil).not.toBeNull();
    expect(state.cooldownUntil!).toBeGreaterThan(Date.now());
  });

  it("Test 2: fails fast within 5min cooldown window with [la-forja:openai_credit_depleted]", async () => {
    await tripOpenAIViaError("insufficient_quota");
    expect(_getOpenAICircuitState().open).toBe(true);

    mockOpenAIResponsesCreate.mockClear();
    let thrown: Error | null = null;
    try {
      await openaiModule.invokeSprintCopilot({
        input: [{ role: "user", content: "test" }],
      });
    } catch (e) {
      thrown = e as Error;
    }

    expect(thrown).not.toBeNull();
    expect(thrown!.message).toContain("[la-forja:openai_credit_depleted]");
    expect(thrown!.message).toContain("circuit breaker open until");
    expect(mockOpenAIResponsesCreate).not.toHaveBeenCalled();
  });

  it("Test 3: auto-resets after 5min cooldown", async () => {
    const tripStart = Date.now();
    vi.useFakeTimers();
    vi.setSystemTime(tripStart);
    await tripOpenAIViaError("You exceeded your current quota");
    expect(_getOpenAICircuitState().open).toBe(true);

    // Reset del spy post-trip antes de medir invocaciones del segundo invoke.
    mockOpenAIResponsesCreate.mockClear();

    vi.setSystemTime(tripStart + 5 * 60 * 1000 + 1000);

    mockOpenAIResponsesCreate.mockResolvedValueOnce({
      output_text: "ok",
      usage: { input_tokens: 10, output_tokens: 5 },
      model: "gpt-5.5-pro",
      status: "completed",
    });

    const result = await openaiModule.invokeSprintCopilot({
      input: [{ role: "user", content: "test" }],
    });

    expect(mockOpenAIResponsesCreate).toHaveBeenCalledOnce();
    expect(result.content).toBe("ok");
    expect(_getOpenAICircuitState().open).toBe(false);
  });

  it("Test 4: does NOT trigger on other errors (rate-limit non-quota, timeout)", async () => {
    const nonCreditErrors = [
      "ETIMEDOUT: connection timeout",
      "fetch failed: network error",
      "500 Internal Server Error",
      "401 Unauthorized: invalid api key",
      "400 Bad Request: invalid model name", // NO matchea quota patterns
      "429 Too Many Requests: please slow down", // rate-limit puro sin "quota"
    ];

    for (const errMsg of nonCreditErrors) {
      _resetOpenAICircuitBreaker();
      await tripOpenAIViaError(errMsg);
      expect(_getOpenAICircuitState().open).toBe(false);
    }
  });
});
