/**
 * La Forja — Tests para env.ts y supabase.ts (D2.1).
 *
 * Validación binaria:
 *   - strict mode falla loud si falta cualquiera de los 11 envs requeridos
 *   - non-strict mode permite arranque /health con placeholders
 *   - default URLs se aplican cuando no se sobreescriben
 *   - Supabase client se construye con configuración válida
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { _resetEnvCache, loadEnv } from "./env";
import { _resetSupabaseCache, getSupabase } from "./supabase";

const REQUIRED_ENVS = [
  "MANUS_API_KEY_GOOGLE",
  "MANUS_API_KEY_APPLE",
  "ANTHROPIC_API_KEY",
  "OPENAI_API_KEY",
  "GEMINI_API_KEY",
  "SONAR_API_KEY",
  "SUPABASE_URL",
  "SUPABASE_SERVICE_KEY",
  "LANGFUSE_PUBLIC_KEY",
  "LANGFUSE_SECRET_KEY",
] as const;

const VALID_ENV: Record<string, string> = {
  MANUS_API_KEY_GOOGLE: "test-manus-google-key",
  MANUS_API_KEY_APPLE: "test-manus-apple-key",
  ANTHROPIC_API_KEY: "test-anthropic-key",
  OPENAI_API_KEY: "test-openai-key",
  GEMINI_API_KEY: "test-gemini-key",
  SONAR_API_KEY: "test-sonar-key",
  SUPABASE_URL: "https://test-project.supabase.co",
  SUPABASE_SERVICE_KEY: "test-service-key",
  LANGFUSE_PUBLIC_KEY: "test-langfuse-public",
  LANGFUSE_SECRET_KEY: "test-langfuse-secret",
};

let savedEnv: NodeJS.ProcessEnv;

beforeEach(() => {
  savedEnv = { ...process.env };
  _resetEnvCache();
  _resetSupabaseCache();
  // Limpiar todas las envs requeridas para empezar de cero
  for (const key of REQUIRED_ENVS) {
    delete process.env[key];
  }
  delete process.env.MANUS_API_BASE_URL;
  delete process.env.LANGFUSE_HOST;
  delete process.env.KERNEL_MONSTRUO_BASE_URL;
  delete process.env.SIMULADOR_BASE_URL;
  delete process.env.DEV_USER_ROLE;
});

afterEach(() => {
  process.env = savedEnv;
  _resetEnvCache();
  _resetSupabaseCache();
});

describe("loadEnv strict mode", () => {
  it("loads successfully with all required envs", () => {
    Object.assign(process.env, VALID_ENV);
    const env = loadEnv({ strict: true });
    expect(env.MANUS_API_KEY_GOOGLE).toBe("test-manus-google-key");
    expect(env.SUPABASE_URL).toBe("https://test-project.supabase.co");
    expect(env.LANGFUSE_PUBLIC_KEY).toBe("test-langfuse-public");
  });

  it("applies default URLs when env vars are absent", () => {
    Object.assign(process.env, VALID_ENV);
    const env = loadEnv({ strict: true });
    expect(env.MANUS_API_BASE_URL).toBe("https://api.manus.ai");
    expect(env.LANGFUSE_HOST).toBe("https://cloud.langfuse.com");
    expect(env.KERNEL_MONSTRUO_BASE_URL).toBe(
      "https://el-monstruo-kernel-production.up.railway.app",
    );
    expect(env.SIMULADOR_BASE_URL).toBe(
      "https://simulador-api-production.up.railway.app",
    );
  });

  it("respects override of default URLs", () => {
    Object.assign(process.env, VALID_ENV, {
      KERNEL_MONSTRUO_BASE_URL: "http://localhost:8080",
      SIMULADOR_BASE_URL: "http://localhost:9090",
    });
    const env = loadEnv({ strict: true });
    expect(env.KERNEL_MONSTRUO_BASE_URL).toBe("http://localhost:8080");
    expect(env.SIMULADOR_BASE_URL).toBe("http://localhost:9090");
  });

  it("defaults DEV_USER_ROLE to t1_alfredo when absent", () => {
    Object.assign(process.env, VALID_ENV);
    const env = loadEnv({ strict: true });
    expect(env.DEV_USER_ROLE).toBe("t1_alfredo");
  });

  it("accepts t1_padre and user as DEV_USER_ROLE", () => {
    Object.assign(process.env, VALID_ENV, { DEV_USER_ROLE: "t1_padre" });
    const env = loadEnv({ strict: true });
    expect(env.DEV_USER_ROLE).toBe("t1_padre");

    _resetEnvCache();
    Object.assign(process.env, { DEV_USER_ROLE: "user" });
    const env2 = loadEnv({ strict: true });
    expect(env2.DEV_USER_ROLE).toBe("user");
  });

  it("rejects invalid DEV_USER_ROLE values", () => {
    Object.assign(process.env, VALID_ENV, { DEV_USER_ROLE: "admin" });
    expect(() => loadEnv({ strict: true })).toThrow(/env_load_strict_failed/);
  });

  it("rejects invalid SUPABASE_URL", () => {
    Object.assign(process.env, VALID_ENV, { SUPABASE_URL: "not-a-url" });
    expect(() => loadEnv({ strict: true })).toThrow(/env_load_strict_failed/);
  });
});

describe("loadEnv strict mode — fail loud on missing required", () => {
  for (const key of REQUIRED_ENVS) {
    it(`fails loud when ${key} is missing`, () => {
      Object.assign(process.env, VALID_ENV);
      delete process.env[key];
      _resetEnvCache();
      expect(() => loadEnv({ strict: true })).toThrow(
        /env_load_strict_failed/,
      );
    });
  }
});

describe("loadEnv non-strict mode (D1 /health boot)", () => {
  it("loads with placeholders when secrets are absent", () => {
    process.env.NODE_ENV = "production";
    const env = loadEnv({ strict: false });
    expect(env.MANUS_API_KEY_GOOGLE).toBe("");
    expect(env.SUPABASE_URL).toBe("https://placeholder.supabase.co");
    expect(env.PORT).toBe(8080);
  });

  it("respects PORT override", () => {
    process.env.PORT = "3000";
    const env = loadEnv({ strict: false });
    expect(env.PORT).toBe(3000);
  });
});

describe("getSupabase", () => {
  it("constructs client with valid env", () => {
    Object.assign(process.env, VALID_ENV);
    const client = getSupabase();
    expect(client).toBeDefined();
    expect(typeof client.from).toBe("function");
  });

  it("returns the same singleton across calls", () => {
    Object.assign(process.env, VALID_ENV);
    const a = getSupabase();
    const b = getSupabase();
    expect(a).toBe(b);
  });

  it("propagates env validation error if strict envs missing", () => {
    delete process.env.SUPABASE_URL;
    expect(() => getSupabase()).toThrow(/env_load_strict_failed/);
  });
});
