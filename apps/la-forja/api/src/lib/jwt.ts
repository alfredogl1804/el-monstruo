/**
 * La Forja — JWT helpers (session tokens).
 *
 * Sprint LA-FORJA-001 v3.2 — D4 Google OAuth.
 *
 * Doctrina:
 *   - HS256 simétrico (suficiente, single-issuer/audience).
 *   - jose@^6.2.3 (estándar JOSE/JWS, no fork, mantenido).
 *   - Issuer fijo `la-forja`, audience fijo `la-forja-api`.
 *   - Expiración 7 días (cookie max-age idéntico).
 *   - Secret leído desde env.JWT_SECRET (≥ 32 chars). Validación en env.ts.
 *
 * Decisión binaria: JWT propio en lugar de Supabase Auth (cuyas tablas
 * `auth.*` no están provisionadas todavía). Migración a Supabase Auth queda
 * como deuda canónica para D5+ si T1-Alfredo lo decide. El interface User
 * permanece estable cross D2-D4-D5+.
 */

import { SignJWT, jwtVerify, errors as joseErrors } from "jose";
import type { User } from "./env.js";

const ISSUER = "la-forja";
const AUDIENCE = "la-forja-api";
const EXPIRES_IN = "7d";
const ALGORITHM = "HS256";

/**
 * Payload firmado en el JWT de sesión.
 * NOTA: el `sub` es el Google `sub` ID (no nuestro UUID). El campo `id` interno
 * se mapea desde `sub` por estabilidad de contrato `User`.
 */
export interface SessionClaims {
  /** Google subject ID (ID único provisto por Google). */
  sub: string;
  email: string;
  name?: string;
  picture?: string;
  /** Rol La Forja resuelto desde whitelist o default `user`. */
  role: User["role"];
}

/** Convierte el secret string a Uint8Array (formato exigido por jose). */
function secretToKey(secret: string): Uint8Array {
  return new TextEncoder().encode(secret);
}

/**
 * Firma un JWT de sesión con HS256.
 * Setea `iss=la-forja`, `aud=la-forja-api`, `exp=now+7d`, `iat=now`.
 */
export async function signSession(
  claims: SessionClaims,
  secret: string,
): Promise<string> {
  if (!secret || secret.length < 32) {
    throw new Error(
      "[la-forja:jwt_secret_too_short] JWT_SECRET must be ≥ 32 chars",
    );
  }
  const jwt = await new SignJWT({
    email: claims.email,
    name: claims.name,
    picture: claims.picture,
    role: claims.role,
  })
    .setProtectedHeader({ alg: ALGORITHM })
    .setSubject(claims.sub)
    .setIssuer(ISSUER)
    .setAudience(AUDIENCE)
    .setIssuedAt()
    .setExpirationTime(EXPIRES_IN)
    .sign(secretToKey(secret));
  return jwt;
}

/**
 * Verifica un JWT de sesión y retorna el payload tipado.
 * Lanza error si: firma inválida, expirado, issuer/audience mismatch.
 */
export async function verifySession(
  token: string,
  secret: string,
): Promise<SessionClaims> {
  const { payload } = await jwtVerify(token, secretToKey(secret), {
    issuer: ISSUER,
    audience: AUDIENCE,
    algorithms: [ALGORITHM],
  });
  if (typeof payload.sub !== "string" || payload.sub.length === 0) {
    throw new Error("[la-forja:jwt_missing_sub] Session JWT missing sub claim");
  }
  if (typeof payload.email !== "string" || payload.email.length === 0) {
    throw new Error(
      "[la-forja:jwt_missing_email] Session JWT missing email claim",
    );
  }
  const role = payload.role;
  if (role !== "t1_alfredo" && role !== "t1_padre" && role !== "user") {
    throw new Error(
      `[la-forja:jwt_invalid_role] Session JWT role must be one of t1_alfredo|t1_padre|user, got ${String(role)}`,
    );
  }
  return {
    sub: payload.sub,
    email: payload.email,
    name: typeof payload.name === "string" ? payload.name : undefined,
    picture:
      typeof payload.picture === "string" ? payload.picture : undefined,
    role,
  };
}

/** Re-export jose error classes for callers that need to discriminate. */
export const JWTErrors = {
  Expired: joseErrors.JWTExpired,
  InvalidSignature: joseErrors.JWSSignatureVerificationFailed,
  ClaimValidationFailed: joseErrors.JWTClaimValidationFailed,
};
