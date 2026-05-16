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
import { loadEnv, type User, type UserRole } from "../lib/env";

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
