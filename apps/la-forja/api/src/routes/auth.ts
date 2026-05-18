/**
 * La Forja API — rutas de autenticación.
 *
 * Sprint LA-FORJA-001 v3.2 — D4 Google OAuth + JWT.
 *
 * Endpoints:
 *   GET  /api/auth/google           → 302 redirect a Google consent
 *   GET  /api/auth/google/callback  → recibe code, intercambia tokens,
 *                                      genera JWT sesión, set cookie HttpOnly,
 *                                      redirect a FRONTEND_URL/post-login
 *   POST /api/auth/logout           → clear cookie, 200 OK
 *
 * Comportamiento binario:
 *   - Si GOOGLE_OAUTH_CLIENT_ID/SECRET no configurados (dev sin secrets):
 *     /google retorna 503 con mensaje claro.
 *   - En producción (NODE_ENV=production), env.ts.superRefine bloquea el boot
 *     si los secrets faltan (fail-loud doctrina §4).
 *
 * Whitelist de roles (D4):
 *   - Whitelist hard-coded por email para t1_alfredo / t1_padre.
 *   - Cualquier otro email → role="user".
 *   - En D5+ esto se mueve a Supabase tabla `forja_user_roles`.
 *
 * Cookie de sesión:
 *   - Nombre: la-forja_session (RFC 6265: no se permite `:` en cookie name)
 *   - HttpOnly: true (no accesible desde JS)
 *   - Secure: true en producción (HTTPS only)
 *   - SameSite: Lax (necesario para callback OAuth cross-origin)
 *   - Path: /
 *   - Max-Age: 7 días
 */

import { Hono } from "hono";
import type { MiddlewareHandler } from "hono";
import { setCookie, deleteCookie } from "hono/cookie";
import { googleAuth } from "@hono/oauth-providers/google";

import { loadEnv, type User, type UserRole } from "../lib/env.js";
import { signSession } from "../lib/jwt.js";
import { SESSION_COOKIE_NAME } from "../middleware/auth.js";

const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7; // 7 días
const POST_LOGIN_PATH = "/post-login";

/**
 * Whitelist hard-coded D4 (provisional — se mueve a Supabase en D5).
 *
 * Mapping email Google → role La Forja.
 * Default cualquier otro email → "user".
 *
 * Sustituible por `setRoleWhitelist()` en tests sin tocar código de producción.
 */
const DEFAULT_ROLE_WHITELIST: Record<string, UserRole> = {
  // Sustituye con emails reales cuando Alfredo registre los suyos.
  // En D4 la lista vacía es válida → todos los logins reciben role="user".
};

let roleWhitelist: Record<string, UserRole> = { ...DEFAULT_ROLE_WHITELIST };

export function setRoleWhitelist(whitelist: Record<string, UserRole>): void {
  roleWhitelist = { ...whitelist };
}

export function _resetRoleWhitelist(): void {
  roleWhitelist = { ...DEFAULT_ROLE_WHITELIST };
}

function resolveRole(email: string): UserRole {
  return roleWhitelist[email.toLowerCase()] ?? "user";
}

/**
 * Guard middleware — retorna 503 si los secrets OAuth faltan en dev.
 * En producción esto nunca se ejecuta porque env.ts.superRefine bloquea el boot.
 */
function oauthConfiguredGuard(): MiddlewareHandler {
  return async (c, next) => {
    const env = loadEnv();
    if (!env.GOOGLE_OAUTH_CLIENT_ID || !env.GOOGLE_OAUTH_CLIENT_SECRET) {
      return c.json(
        {
          ok: false,
          error:
            "[la-forja:oauth_not_configured] GOOGLE_OAUTH_CLIENT_ID/SECRET missing",
          hint: "Set them in Railway secrets to enable Google OAuth",
        },
        503,
      );
    }
    await next();
    return;
  };
}

/**
 * Middleware factory que construye `googleAuth` con secrets desde env en
 * runtime. Necesario porque los secrets pueden cambiar entre tests sin
 * recargar el módulo.
 */
function buildGoogleAuthMiddleware(): MiddlewareHandler {
  return async (c, next) => {
    const env = loadEnv();
    if (!env.GOOGLE_OAUTH_CLIENT_ID || !env.GOOGLE_OAUTH_CLIENT_SECRET) {
      // Fallback de seguridad — el guard previo ya retornó 503 si llegamos aquí
      // sin secrets, pero defendemos el flujo igual.
      return c.json(
        {
          ok: false,
          error:
            "[la-forja:oauth_not_configured] GOOGLE_OAUTH_CLIENT_ID/SECRET missing",
        },
        503,
      );
    }
    const handler = googleAuth({
      client_id: env.GOOGLE_OAUTH_CLIENT_ID,
      client_secret: env.GOOGLE_OAUTH_CLIENT_SECRET,
      scope: ["openid", "email", "profile"],
      redirect_uri: `${env.OAUTH_REDIRECT_BASE_URL}/api/auth/google/callback`,
    });
    return handler(c, next);
  };
}

export interface AuthRoutesDeps {
  /** Override JWT secret para tests (no usar en producción). */
  jwtSecretOverride?: string;
}

export function authRoutes(deps: AuthRoutesDeps = {}): Hono {
  const router = new Hono();

  // -------- GET /google → 302 a Google consent --------
  // El middleware googleAuth detecta ausencia de `code` query param y emite
  // 302 directo a accounts.google.com. El handler "next" no se ejecuta porque
  // el middleware ya escribió la response.
  router.use("/google", oauthConfiguredGuard());
  router.use("/google", buildGoogleAuthMiddleware());
  router.get("/google", (c) => {
    // Caso defensivo: si el middleware no emitió 302 por alguna razón,
    // este handler no debería alcanzarse. Retornamos error explícito.
    return c.json(
      {
        ok: false,
        error: "[la-forja:oauth_redirect_failed] middleware did not redirect",
      },
      500,
    );
  });

  // -------- GET /google/callback → exchange + cookie + redirect --------
  router.use("/google/callback", oauthConfiguredGuard());
  router.use("/google/callback", buildGoogleAuthMiddleware());
  router.get("/google/callback", async (c) => {
    const env = loadEnv();
    const jwtSecret = deps.jwtSecretOverride ?? env.JWT_SECRET;
    if (!jwtSecret) {
      return c.json(
        {
          ok: false,
          error:
            "[la-forja:jwt_secret_missing] JWT_SECRET not configured for callback",
        },
        503,
      );
    }

    const googleUser = c.get("user-google") as
      | {
          id?: string;
          email?: string;
          name?: string;
          picture?: string;
        }
      | undefined;

    if (!googleUser?.id || !googleUser.email) {
      return c.json(
        {
          ok: false,
          error:
            "[la-forja:oauth_callback_no_user] Google did not return user profile",
        },
        502,
      );
    }

    const role = resolveRole(googleUser.email);
    const _sessionUser: User = {
      id: googleUser.id,
      email: googleUser.email,
      role,
    };

    const token = await signSession(
      {
        sub: googleUser.id,
        email: googleUser.email,
        name: googleUser.name,
        picture: googleUser.picture,
        role,
      },
      jwtSecret,
    );

    const isProduction = env.NODE_ENV === "production";
    setCookie(c, SESSION_COOKIE_NAME, token, {
      httpOnly: true,
      secure: isProduction,
      sameSite: "Lax",
      path: "/",
      maxAge: SESSION_MAX_AGE_SECONDS,
    });

    // Redirect frontend post-login. SPEC v3.2 §4 indica /post-login como
    // landing point; el frontend luego resuelve dashboard/tutor según role.
    const redirectTo = `${env.FRONTEND_URL}${POST_LOGIN_PATH}`;
    return c.redirect(redirectTo, 302);
  });

  // -------- POST /logout → clear cookie --------
  router.post("/logout", (c) => {
    deleteCookie(c, SESSION_COOKIE_NAME, { path: "/" });
    return c.json({ ok: true, message: "Session terminated" });
  });

  return router;
}

/** Export útil para tests. */
export const _testHelpers = {
  resolveRole,
  SESSION_MAX_AGE_SECONDS,
  POST_LOGIN_PATH,
};
