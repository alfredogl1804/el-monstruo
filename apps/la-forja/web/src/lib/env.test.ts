/**
 * La Forja — tests para loadForjaWebEnv (D3.0).
 * Cubre fail-loud strict y rejection en production con strict:false.
 */
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { loadForjaWebEnv } from "./env";

// Helpers para evitar que TS rechace mutaciones de process.env (NODE_ENV es
// readonly en types de Next/Node). En runtime sí es escribible.
const env = process.env as Record<string, string | undefined>;
const originalEnv = { ...env };

describe("loadForjaWebEnv (D3.0 fail-loud)", () => {
  beforeEach(() => {
    delete env["NEXT_PUBLIC_API_URL"];
    delete env["NODE_ENV"];
  });

  afterEach(() => {
    for (const k of Object.keys(env)) delete env[k];
    Object.assign(env, originalEnv);
  });

  it("rechaza en strict si NEXT_PUBLIC_API_URL falta", () => {
    expect(() => loadForjaWebEnv({ strict: true })).toThrow(
      /\[la-forja:web_env_load_strict_failed\]/,
    );
  });

  it("rechaza en strict si NEXT_PUBLIC_API_URL no es URL válida", () => {
    process.env["NEXT_PUBLIC_API_URL"] = "no-es-una-url";
    expect(() => loadForjaWebEnv({ strict: true })).toThrow(
      /\[la-forja:web_env_load_strict_failed\]/,
    );
  });

  it("acepta NEXT_PUBLIC_API_URL válida", () => {
    env["NEXT_PUBLIC_API_URL"] = "http://localhost:3000";
    const out = loadForjaWebEnv({ strict: true });
    expect(out.NEXT_PUBLIC_API_URL).toBe("http://localhost:3000");
  });

  it("strict:false en NODE_ENV=production lanza fail-loud (paridad backend)", () => {
    env["NODE_ENV"] = "production";
    expect(() => loadForjaWebEnv({ strict: false })).toThrow(
      /\[la-forja:web_env_load_permissive_blocked_in_production\]/,
    );
  });

  it("strict:false en development retorna placeholder seguro", () => {
    env["NODE_ENV"] = "development";
    const out = loadForjaWebEnv({ strict: false });
    expect(out.NEXT_PUBLIC_API_URL).toBe("http://localhost:3000");
    expect(out.NODE_ENV).toBe("development");
  });
});
