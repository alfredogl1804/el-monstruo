// El Monstruo — Auth middleware canónico para Manus-Oauth
// Template agnóstico de framework. Adaptar a Next.js / Hono / Express / Fastify.
// Generado por skill manus-oauth-pattern v0.1.0
//
// Naming inviolable per DSC-G-004:
//   Errores con formato `auth_{action}_{failure_type}` (NUNCA "internal server error")
//   Cookie `monstruo_session` (NUNCA `session_id` o `auth_token`)
//   Logs con namespace `monstruo.auth.manus_oauth.*`

import { z } from "zod"; // o tu validator preferido

// ── Tipos canónicos ─────────────────────────────────────────────────
export interface MonstruoUser {
  id: string;                      // = manus user_id
  email: string;
  emailVerified: boolean;
  name: string | null;
  avatarUrl: string | null;
}

export interface AuthError extends Error {
  code:
    | "auth_session_missing"
    | "auth_session_invalid"
    | "auth_session_expired"
    | "auth_introspection_failed"
    | "auth_user_suspended"
    | "auth_user_deleted";
  status: number;
}

// ── Validator del cookie firmado ────────────────────────────────────
const SessionCookieSchema = z.object({
  sid: z.string().min(32),         // session_id
  uid: z.string().min(8),          // user_id
  exp: z.number().int(),           // unix timestamp expiración
  iat: z.number().int(),           // issued at
  sig: z.string().min(32),         // HMAC signature
});

// ── Función principal: hidratar req.user desde cookie ──────────────
export async function authenticate(
  cookieValue: string | undefined,
  deps: AuthDeps,
): Promise<MonstruoUser> {
  if (!cookieValue) {
    throw makeAuthError("auth_session_missing", 401, "no cookie monstruo_session presente");
  }

  let parsed;
  try {
    parsed = SessionCookieSchema.parse(JSON.parse(cookieValue));
  } catch {
    throw makeAuthError("auth_session_invalid", 401, "cookie malformado o firma inválida");
  }

  // Verificar firma HMAC
  const expectedSig = await deps.signSession({
    sid: parsed.sid,
    uid: parsed.uid,
    exp: parsed.exp,
    iat: parsed.iat,
  });
  if (parsed.sig !== expectedSig) {
    throw makeAuthError("auth_session_invalid", 401, "firma de cookie no coincide");
  }

  // Verificar expiración
  if (Date.now() / 1000 > parsed.exp) {
    throw makeAuthError("auth_session_expired", 401, "cookie expirado");
  }

  // Verificar sesión existe y no está revocada en DB
  const session = await deps.db.findSession(parsed.sid);
  if (!session || session.revokedAt) {
    throw makeAuthError("auth_session_invalid", 401, "sesión no existe o fue revocada");
  }

  // Hidratar user desde DB
  const user = await deps.db.findUser(parsed.uid);
  if (!user) {
    throw makeAuthError("auth_session_invalid", 401, "usuario no existe");
  }
  if (user.status === "suspended") {
    throw makeAuthError("auth_user_suspended", 403, `cuenta suspendida: ${user.suspendedReason}`);
  }
  if (user.status === "deleted") {
    throw makeAuthError("auth_user_deleted", 410, "cuenta eliminada");
  }

  // Si el manus_token está cerca de expirar, refrescar (background)
  if (user.manusTokenExpiresAt && user.manusTokenExpiresAt.getTime() - Date.now() < 5 * 60 * 1000) {
    // Fire and forget — refresh en background
    deps.refreshManusToken(user.id).catch((err) => {
      deps.log.warn("auth_token_refresh_background_failed", { user_id: user.id, error: err.message });
    });
  }

  deps.log.debug("auth_session_validated", { user_id: user.id });

  return {
    id: user.id,
    email: user.email,
    emailVerified: user.emailVerified,
    name: user.name,
    avatarUrl: user.avatarUrl,
  };
}

// ── Dependencias inyectables ────────────────────────────────────────
export interface AuthDeps {
  db: {
    findUser(id: string): Promise<UserRecord | null>;
    findSession(id: string): Promise<SessionRecord | null>;
  };
  signSession(payload: SignablePayload): Promise<string>;
  refreshManusToken(userId: string): Promise<void>;
  log: {
    debug(event: string, data?: object): void;
    warn(event: string, data?: object): void;
    error(event: string, data?: object): void;
  };
}

interface UserRecord {
  id: string;
  email: string;
  emailVerified: boolean;
  name: string | null;
  avatarUrl: string | null;
  status: "active" | "suspended" | "deleted";
  suspendedReason: string | null;
  manusTokenExpiresAt: Date | null;
}

interface SessionRecord {
  id: string;
  userId: string;
  expiresAt: Date;
  revokedAt: Date | null;
}

interface SignablePayload {
  sid: string;
  uid: string;
  exp: number;
  iat: number;
}

// ── Helper para errores on-brand ────────────────────────────────────
function makeAuthError(code: AuthError["code"], status: number, message: string): AuthError {
  const err = new Error(message) as AuthError;
  err.code = code;
  err.status = status;
  return err;
}
