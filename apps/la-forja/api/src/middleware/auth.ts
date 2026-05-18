/**
 * La Forja — Middleware de autenticación.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.5.
 * Doctrina: §6 + §8 SPEC v3.2 (auth real es D4 — Google OAuth + Supabase Auth).
 *
 * En D2 (stub): lee header `x-user-id` (UUID) y resuelve role desde la env
 *   var `DEV_USER_ROLE`. El email se sintetiza desde el id para el shape User.
 *
 * En D4: este middleware se reemplaza por validación JWT Supabase Auth.
 *   El interface User NO cambia. Las rutas que usan `c.get('user')` no se tocan.
 *
 * Comportamiento binario en D2.5:
 *   - Si NODE_ENV=production → HTTP 503 (stub deshabilitado, requiere D4 OAuth real)
 *   - Si NO viene `x-user-id` header → 401 Unauthorized
 *   - Si viene UUID válido → c.set('user', {id, email, role}) y next()
 *   - El test usa user-id determinista (UUID válido) para evitar randomness
 *
 * Hardening D2.5 (audit adversarial Perplexity 15-may-2026):
 *   - H-1: guard NODE_ENV=production que rechaza con HTTP 503 antes de aceptar UUID.
 *          Cierra la ventana entre D3-deploy-staging y D4-auth-real donde un atacante
 *          con cualquier UUID válido + DEV_USER_ROLE en env podía impersonar T1-Alfredo.
 */

import type { Context, MiddlewareHandler, Next } from "hono";
import { getCookie } from "hono/cookie";
import { loadEnv, type User, type UserRole } from "../lib/env";
import { verifySession } from "../lib/jwt";

/**
 * Nombre canónico de la cookie de sesión (D4).
 *
 * Nota RFC 6265: los nombres de cookie no pueden contener `:` (TOKEN del RFC).
 * Por eso se usa `_` en lugar de `:` aunque la doctrina nombre las cosas
 * con namespace `la-forja:*` en otros contextos (logs, telemetría, etc).
 */
export const SESSION_COOKIE_NAME = "la-forja_session";

// UUID v4-ish: 8-4-4-4-12 hex con versión y variante (validación binaria)
const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export interface ForjaAuthContext {
  Variables: {
    user: User;
  };
}

/**
 * Middleware Hono que rellena `c.var.user`.
 *
 * Uso:
 *   const app = new Hono<ForjaAuthContext>();
 *   app.use("*", forjaAuthStub());
 *   app.get("/protected", (c) => c.json({ user: c.var.user }));
 */
export function forjaAuthStub(): MiddlewareHandler<ForjaAuthContext> {
  return async (c: Context, next: Next) => {
    // Hardening D2.5 H-1: el stub está PROHIBIDO en producción.
    // Cualquier deploy que llegue aquí con NODE_ENV=production rechaza con 503.
    // Sustitución legítima: middleware OAuth real de D4.
    const env = loadEnv();
    if (env.NODE_ENV === "production") {
      return c.json(
        {
          ok: false,
          error:
            "[la-forja:auth_stub_disabled_in_production] D4 Google OAuth + Supabase Auth required",
        },
        503,
      );
    }
    const userId = c.req.header("x-user-id");
    if (!userId) {
      return c.json(
        {
          ok: false,
          error: "[la-forja:auth_missing_user_id] x-user-id header required",
        },
        401,
      );
    }
    if (!UUID_RE.test(userId)) {
      return c.json(
        {
          ok: false,
          error:
            "[la-forja:auth_invalid_user_id] x-user-id must be a valid UUID",
        },
        401,
      );
    }
    const role: UserRole = env.DEV_USER_ROLE;
    const user: User = {
      id: userId,
      email: `${role}@stub.la-forja.local`,
      role,
    };
    c.set("user", user);
    await next();
    return;
  };
}

/**
 * Middleware D4 — valida JWT de sesión (cookie HttpOnly `la-forja:session`).
 *
 * Comportamiento binario:
 *   - Cookie ausente            → 401
 *   - JWT inválido/expirado     → 401 (mensaje canónico)
 *   - JWT válido                → c.set('user', { id, email, role }) y next()
 *
 * Whitelist de roles: por defecto el JWT puede llevar `t1_alfredo|t1_padre|user`.
 * El mapeo googleSub → role real lo hace el callback OAuth (lookup Supabase en D5;
 * en D4 todos los nuevos sign-ins reciben role="user" salvo whitelist hard-coded).
 *
 * Reemplazo binario para `forjaAuthStub()`. Mismo shape `User` → cero ripple
 * en routes que usan `c.var.user`.
 */
export function forjaAuthGoogle(): MiddlewareHandler<ForjaAuthContext> {
  return async (c: Context, next: Next) => {
    const env = loadEnv();
    const token = getCookie(c, SESSION_COOKIE_NAME);
    if (!token) {
      return c.json(
        {
          ok: false,
          error:
            "[la-forja:auth_session_missing] la-forja_session cookie required",
        },
        401,
      );
    }
    if (!env.JWT_SECRET) {
      // Configurado bajo NODE_ENV !== production y secret faltante → fail-loud.
      return c.json(
        {
          ok: false,
          error:
            "[la-forja:auth_jwt_secret_missing] JWT_SECRET not configured",
        },
        503,
      );
    }
    try {
      const claims = await verifySession(token, env.JWT_SECRET);
      const user: User = {
        id: claims.sub,
        email: claims.email,
        role: claims.role,
      };
      c.set("user", user);
      await next();
      return;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : String(err);
      return c.json(
        {
          ok: false,
          error: `[la-forja:auth_session_invalid] ${message}`,
        },
        401,
      );
    }
  };
}

/**
 * Selector binario por NODE_ENV.
 *
 * - production  → forjaAuthGoogle (D4 OAuth real, cookie JWT)
 * - development → forjaAuthStub  (preserva contrato D2 con x-user-id)
 * - test        → forjaAuthStub  (preserva 180/180 tests sin regresión)
 *
 * Justificación: tests existentes usan x-user-id; cambiarlos a JWT requiere
 * tocar 180+ tests y no aporta valor adversarial. El stub ya está endurecido
 * (H-1 D2.5) para rechazar producción con 503.
 */
export function forjaAuthSelector(): MiddlewareHandler<ForjaAuthContext> {
  const env = loadEnv();
  if (env.NODE_ENV === "production") {
    return forjaAuthGoogle();
  }
  return forjaAuthStub();
}
