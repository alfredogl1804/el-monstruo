/**
 * La Forja — Tests routes/auth.ts (D4).
 *
 * Cobertura binaria:
 *   - GET /google                  → 503 sin secrets / 302 con secrets
 *   - GET /google/callback         → 503 sin JWT_SECRET, 502 si Google no devuelve user,
 *                                     302 + cookie con secrets + user-google populado
 *   - POST /logout                 → 200 + cookie clear
 *   - resolveRole + setRoleWhitelist
 */

import { Hono } from "hono";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { _resetEnvCache } from "../lib/env.js";
import { verifySession } from "../lib/jwt.js";
import { SESSION_COOKIE_NAME } from "../middleware/auth.js";

// Mock googleAuth ANTES de importar authRoutes (vi.mock es hoisted).
// Estrategia: capturamos la URL del redirect_uri que pasaría el handler real,
// y simulamos el comportamiento (302 si no hay code, populate user-google si hay).
vi.mock("@hono/oauth-providers/google", () => {
  return {
    googleAuth: (opts: { client_id: string; redirect_uri: string }) => {
      return async (
        c: import("hono").Context,
        next: import("hono").Next,
      ) => {
        const code = c.req.query("code");
        // Si no viene code, simulamos el redirect 302 a Google.
        if (!code) {
          const url = new URL("https://accounts.google.com/o/oauth2/v2/auth");
          url.searchParams.set("client_id", opts.client_id);
          url.searchParams.set("redirect_uri", opts.redirect_uri);
          url.searchParams.set("response_type", "code");
          url.searchParams.set("scope", "openid email profile");
          return c.redirect(url.toString(), 302);
        }
        // Si viene code, simulamos el intercambio populando user-google.
        // Tests que necesiten controlar el user lo hacen via header de prueba.
        const mockUserHeader = c.req.header("x-test-google-user");
        if (mockUserHeader === "no-user") {
          c.set("user-google", undefined);
        } else if (mockUserHeader === "no-id") {
          c.set("user-google", { email: "x@y.com" });
        } else {
          c.set("user-google", {
            id: "google-sub-test-12345",
            email: "alfredo@example.com",
            name: "Alfredo Test",
            picture: "https://lh3.googleusercontent.com/test",
          });
        }
        await next();
      };
    },
  };
});

import {
  authRoutes,
  setRoleWhitelist,
  _resetRoleWhitelist,
  _testHelpers,
} from "./auth.js";

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
  GOOGLE_OAUTH_CLIENT_ID: "test-client-id.apps.googleusercontent.com",
  GOOGLE_OAUTH_CLIENT_SECRET: "GOCSPX-test-secret",
  JWT_SECRET: "forja-test-jwt-secret-must-be-at-least-32-chars-long",
  OAUTH_REDIRECT_BASE_URL: "http://localhost:8081",
  FRONTEND_URL: "http://localhost:3000",
};

let savedEnv: NodeJS.ProcessEnv;

beforeEach(() => {
  savedEnv = { ...process.env };
  _resetEnvCache();
  _resetRoleWhitelist();
  // Limpiamos posibles vars de la env actual del shell que choquen.
  for (const k of Object.keys(VALID_ENV)) {
    delete process.env[k];
  }
  Object.assign(process.env, VALID_ENV);
});

afterEach(() => {
  process.env = savedEnv;
  _resetEnvCache();
  _resetRoleWhitelist();
});

function buildApp() {
  const app = new Hono();
  app.route("/api/auth", authRoutes());
  return app;
}

describe("authRoutes — GET /api/auth/google", () => {
  it("retorna 503 cuando GOOGLE_OAUTH_CLIENT_ID falta", async () => {
    delete process.env.GOOGLE_OAUTH_CLIENT_ID;
    _resetEnvCache();
    const app = buildApp();
    const res = await app.request("/api/auth/google");
    expect(res.status).toBe(503);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("oauth_not_configured");
  });

  it("retorna 503 cuando GOOGLE_OAUTH_CLIENT_SECRET falta", async () => {
    delete process.env.GOOGLE_OAUTH_CLIENT_SECRET;
    _resetEnvCache();
    const app = buildApp();
    const res = await app.request("/api/auth/google");
    expect(res.status).toBe(503);
  });

  it("emite 302 a Google con client_id y redirect_uri correctos", async () => {
    const app = buildApp();
    const res = await app.request("/api/auth/google");
    expect(res.status).toBe(302);
    const location = res.headers.get("location");
    expect(location).toBeTruthy();
    expect(location).toContain("accounts.google.com/o/oauth2/v2/auth");
    expect(location).toContain(
      "client_id=test-client-id.apps.googleusercontent.com",
    );
    expect(location).toContain(
      encodeURIComponent(
        "http://localhost:8081/api/auth/google/callback",
      ),
    );
  });
});

describe("authRoutes — GET /api/auth/google/callback", () => {
  it("retorna 503 sin GOOGLE_OAUTH_CLIENT_ID", async () => {
    delete process.env.GOOGLE_OAUTH_CLIENT_ID;
    _resetEnvCache();
    const app = buildApp();
    const res = await app.request("/api/auth/google/callback?code=abc");
    expect(res.status).toBe(503);
  });

  it("retorna 503 sin JWT_SECRET", async () => {
    delete process.env.JWT_SECRET;
    _resetEnvCache();
    const app = buildApp();
    const res = await app.request("/api/auth/google/callback?code=abc");
    // El guard oauth retorna primero si oauth está OK pero JWT falta.
    // Aquí ambos están OK excepto JWT, así que el callback handler retorna 503.
    expect(res.status).toBe(503);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("jwt_secret_missing");
  });

  it("retorna 502 si Google no devuelve user", async () => {
    const app = buildApp();
    const res = await app.request("/api/auth/google/callback?code=abc", {
      headers: { "x-test-google-user": "no-user" },
    });
    expect(res.status).toBe(502);
    const body = (await res.json()) as { error: string };
    expect(body.error).toContain("oauth_callback_no_user");
  });

  it("retorna 502 si Google devuelve user sin id", async () => {
    const app = buildApp();
    const res = await app.request("/api/auth/google/callback?code=abc", {
      headers: { "x-test-google-user": "no-id" },
    });
    expect(res.status).toBe(502);
  });

  it("emite 302 a FRONTEND_URL/post-login con cookie la-forja:session HttpOnly", async () => {
    const app = buildApp();
    const res = await app.request("/api/auth/google/callback?code=abc");
    expect(res.status).toBe(302);

    const location = res.headers.get("location");
    expect(location).toBe("http://localhost:3000/post-login");

    const setCookie = res.headers.get("set-cookie");
    expect(setCookie).toBeTruthy();
    expect(setCookie).toContain(`${SESSION_COOKIE_NAME}=`);
    expect(setCookie).toContain("HttpOnly");
    expect(setCookie).toContain("SameSite=Lax");
    expect(setCookie).toContain("Path=/");
  });

  it("la cookie contiene un JWT firmado válido con claims correctos", async () => {
    const app = buildApp();
    const res = await app.request("/api/auth/google/callback?code=abc");
    expect(res.status).toBe(302);

    const setCookie = res.headers.get("set-cookie") ?? "";
    const match = setCookie.match(
      new RegExp(`${SESSION_COOKIE_NAME}=([^;]+)`),
    );
    expect(match).toBeTruthy();
    const token = decodeURIComponent(match![1]);

    const claims = await verifySession(token, VALID_ENV.JWT_SECRET);
    expect(claims.sub).toBe("google-sub-test-12345");
    expect(claims.email).toBe("alfredo@example.com");
    expect(claims.name).toBe("Alfredo Test");
    expect(claims.role).toBe("user"); // sin whitelist → default user
  });

  it("respeta whitelist de roles cuando está configurada", async () => {
    setRoleWhitelist({
      "alfredo@example.com": "t1_alfredo",
    });

    const app = buildApp();
    const res = await app.request("/api/auth/google/callback?code=abc");
    expect(res.status).toBe(302);

    const setCookie = res.headers.get("set-cookie") ?? "";
    const match = setCookie.match(
      new RegExp(`${SESSION_COOKIE_NAME}=([^;]+)`),
    );
    const token = decodeURIComponent(match![1]);
    const claims = await verifySession(token, VALID_ENV.JWT_SECRET);
    expect(claims.role).toBe("t1_alfredo");
  });

  it("cookie NO usa Secure en NODE_ENV != production", async () => {
    process.env.NODE_ENV = "development";
    _resetEnvCache();
    const app = buildApp();
    const res = await app.request("/api/auth/google/callback?code=abc");
    const setCookie = res.headers.get("set-cookie") ?? "";
    expect(setCookie).not.toMatch(/;\s*Secure/i);
  });

  it("cookie usa Secure en NODE_ENV=production", async () => {
    process.env.NODE_ENV = "production";
    _resetEnvCache();
    const app = buildApp();
    const res = await app.request("/api/auth/google/callback?code=abc");
    const setCookie = res.headers.get("set-cookie") ?? "";
    expect(setCookie).toMatch(/Secure/);
  });
});

describe("authRoutes — POST /api/auth/logout", () => {
  it("clear la cookie y retorna 200", async () => {
    const app = buildApp();
    const res = await app.request("/api/auth/logout", {
      method: "POST",
    });
    expect(res.status).toBe(200);
    const setCookie = res.headers.get("set-cookie") ?? "";
    expect(setCookie).toContain(`${SESSION_COOKIE_NAME}=`);
    // deleteCookie escribe Max-Age=0 o expires en el pasado
    expect(
      /Max-Age=0/.test(setCookie) ||
        /expires=Thu, 01 Jan 1970/i.test(setCookie),
    ).toBe(true);
    const body = (await res.json()) as { ok: boolean };
    expect(body.ok).toBe(true);
  });
});

describe("authRoutes — internals", () => {
  it("resolveRole default 'user' cuando email no está en whitelist", () => {
    expect(_testHelpers.resolveRole("random@example.com")).toBe("user");
  });

  it("resolveRole respeta whitelist case-insensitive", () => {
    setRoleWhitelist({ "boss@forja.com": "t1_alfredo" });
    expect(_testHelpers.resolveRole("BOSS@FORJA.COM")).toBe("t1_alfredo");
    expect(_testHelpers.resolveRole("boss@forja.com")).toBe("t1_alfredo");
  });

  it("SESSION_MAX_AGE_SECONDS = 7 días", () => {
    expect(_testHelpers.SESSION_MAX_AGE_SECONDS).toBe(60 * 60 * 24 * 7);
  });

  it("POST_LOGIN_PATH = /post-login", () => {
    expect(_testHelpers.POST_LOGIN_PATH).toBe("/post-login");
  });
});
