/**
 * La Forja — Tests JWT helpers.
 * Sprint LA-FORJA-001 v3.2 — D4.1.
 */
import { describe, it, expect } from "vitest";
import { signSession, verifySession, type SessionClaims } from "./jwt.js";

const SECRET = "forja-test-jwt-secret-must-be-at-least-32-chars-long";
const SECRET_B = "forja-test-jwt-secret-DIFFERENT-must-be-at-least-32-chars";

const VALID_CLAIMS: SessionClaims = {
  sub: "google-sub-1234567890",
  email: "alfredo@example.com",
  name: "Alfredo Góngora",
  picture: "https://lh3.googleusercontent.com/x",
  role: "t1_alfredo",
};

describe("jwt.signSession + verifySession", () => {
  it("firma y verifica round-trip preservando claims", async () => {
    const token = await signSession(VALID_CLAIMS, SECRET);
    expect(typeof token).toBe("string");
    expect(token.split(".").length).toBe(3); // header.payload.signature

    const verified = await verifySession(token, SECRET);
    expect(verified.sub).toBe(VALID_CLAIMS.sub);
    expect(verified.email).toBe(VALID_CLAIMS.email);
    expect(verified.name).toBe(VALID_CLAIMS.name);
    expect(verified.picture).toBe(VALID_CLAIMS.picture);
    expect(verified.role).toBe(VALID_CLAIMS.role);
  });

  it("rechaza si secret < 32 chars al firmar", async () => {
    await expect(signSession(VALID_CLAIMS, "too-short")).rejects.toThrow(
      /jwt_secret_too_short/,
    );
  });

  it("rechaza si firma con secret distinto al verificar", async () => {
    const token = await signSession(VALID_CLAIMS, SECRET);
    await expect(verifySession(token, SECRET_B)).rejects.toThrow();
  });

  it("rechaza tokens malformados", async () => {
    await expect(verifySession("not.a.jwt", SECRET)).rejects.toThrow();
    await expect(verifySession("", SECRET)).rejects.toThrow();
  });

  it("rechaza JWT con role inválido", async () => {
    // forzamos un JWT con role inválido firmado correctamente
    const { SignJWT } = await import("jose");
    const badJwt = await new SignJWT({
      email: "x@y.com",
      role: "hacker",
    })
      .setProtectedHeader({ alg: "HS256" })
      .setSubject("sub-bad")
      .setIssuer("la-forja")
      .setAudience("la-forja-api")
      .setIssuedAt()
      .setExpirationTime("7d")
      .sign(new TextEncoder().encode(SECRET));
    await expect(verifySession(badJwt, SECRET)).rejects.toThrow(
      /jwt_invalid_role/,
    );
  });

  it("rechaza JWT con issuer incorrecto", async () => {
    const { SignJWT } = await import("jose");
    const wrongIss = await new SignJWT({
      email: VALID_CLAIMS.email,
      role: VALID_CLAIMS.role,
    })
      .setProtectedHeader({ alg: "HS256" })
      .setSubject(VALID_CLAIMS.sub)
      .setIssuer("evil-issuer")
      .setAudience("la-forja-api")
      .setIssuedAt()
      .setExpirationTime("7d")
      .sign(new TextEncoder().encode(SECRET));
    await expect(verifySession(wrongIss, SECRET)).rejects.toThrow();
  });

  it("rechaza JWT con audience incorrecto", async () => {
    const { SignJWT } = await import("jose");
    const wrongAud = await new SignJWT({
      email: VALID_CLAIMS.email,
      role: VALID_CLAIMS.role,
    })
      .setProtectedHeader({ alg: "HS256" })
      .setSubject(VALID_CLAIMS.sub)
      .setIssuer("la-forja")
      .setAudience("evil-audience")
      .setIssuedAt()
      .setExpirationTime("7d")
      .sign(new TextEncoder().encode(SECRET));
    await expect(verifySession(wrongAud, SECRET)).rejects.toThrow();
  });

  it("rechaza JWT expirado", async () => {
    const { SignJWT } = await import("jose");
    const expired = await new SignJWT({
      email: VALID_CLAIMS.email,
      role: VALID_CLAIMS.role,
    })
      .setProtectedHeader({ alg: "HS256" })
      .setSubject(VALID_CLAIMS.sub)
      .setIssuer("la-forja")
      .setAudience("la-forja-api")
      .setIssuedAt(Math.floor(Date.now() / 1000) - 86400) // ayer
      .setExpirationTime(Math.floor(Date.now() / 1000) - 3600) // hace 1h
      .sign(new TextEncoder().encode(SECRET));
    await expect(verifySession(expired, SECRET)).rejects.toThrow();
  });

  it("permite role t1_padre y user (no solo t1_alfredo)", async () => {
    for (const role of ["t1_padre", "user"] as const) {
      const token = await signSession({ ...VALID_CLAIMS, role }, SECRET);
      const verified = await verifySession(token, SECRET);
      expect(verified.role).toBe(role);
    }
  });

  it("permite claims con name/picture undefined", async () => {
    const minimal: SessionClaims = {
      sub: "g-sub-min",
      email: "min@example.com",
      role: "user",
    };
    const token = await signSession(minimal, SECRET);
    const verified = await verifySession(token, SECRET);
    expect(verified.name).toBeUndefined();
    expect(verified.picture).toBeUndefined();
  });
});
