// El Monstruo — Callback handler canónico para Manus-Oauth
// Endpoint: POST /api/v1/auth/callback (NUNCA /api/auth/callback genérico)
// Generado por skill manus-oauth-pattern v0.1.0

import crypto from "node:crypto";

export interface CallbackHandlerDeps {
  env: {
    MANUS_OAUTH_CLIENT_ID: string;
    MANUS_OAUTH_CLIENT_SECRET: string;
    MANUS_OAUTH_REDIRECT_URI: string;
    MANUS_OAUTH_TOKEN_URL: string;
    MANUS_OAUTH_USERINFO_URL: string;
    MONSTRUO_SESSION_SECRET: string;
    MONSTRUO_SESSION_TTL_SECONDS: string;
    MONSTRUO_TOKEN_ENCRYPTION_KEY: string;
  };
  db: {
    upsertUser(input: UpsertUserInput): Promise<{ id: string }>;
    createSession(input: CreateSessionInput): Promise<{ id: string }>;
  };
  log: {
    info(event: string, data?: object): void;
    error(event: string, data?: object): void;
  };
  encrypt(plaintext: string): Promise<string>;
}

export interface UpsertUserInput {
  id: string;
  email: string;
  emailVerified: boolean;
  name: string | null;
  avatarUrl: string | null;
  manusTokenEncrypted: string;
  manusTokenExpiresAt: Date;
  manusRefreshTokenEncrypted: string | null;
  lastLoginIp: string;
  lastLoginUserAgent: string;
}

export interface CreateSessionInput {
  id: string;
  userId: string;
  expiresAt: Date;
  ipAddress: string;
  userAgent: string;
}

export interface CallbackRequest {
  code: string;
  state: string;
  ip: string;
  userAgent: string;
}

export interface CallbackResponse {
  cookieValue: string;
  cookieExpiresAt: Date;
  redirectTo: string;
}

export async function handleAuthCallback(
  req: CallbackRequest,
  deps: CallbackHandlerDeps,
): Promise<CallbackResponse> {
  // ── Paso 1: intercambiar code por token ────────────────────────────
  const tokenResponse = await fetch(deps.env.MANUS_OAUTH_TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code: req.code,
      client_id: deps.env.MANUS_OAUTH_CLIENT_ID,
      client_secret: deps.env.MANUS_OAUTH_CLIENT_SECRET,
      redirect_uri: deps.env.MANUS_OAUTH_REDIRECT_URI,
    }).toString(),
  });

  if (!tokenResponse.ok) {
    const errorBody = await tokenResponse.text();
    deps.log.error("auth_callback_token_exchange_failed", {
      status: tokenResponse.status,
      body: errorBody,
    });
    throw new Error("auth_callback_token_exchange_failed");
  }

  const tokenJson = (await tokenResponse.json()) as {
    access_token: string;
    expires_in: number;
    refresh_token?: string;
    id_token?: string;
  };

  // ── Paso 2: obtener userinfo ───────────────────────────────────────
  const userInfoResponse = await fetch(deps.env.MANUS_OAUTH_USERINFO_URL, {
    headers: { Authorization: `Bearer ${tokenJson.access_token}` },
  });

  if (!userInfoResponse.ok) {
    deps.log.error("auth_callback_userinfo_failed", { status: userInfoResponse.status });
    throw new Error("auth_callback_userinfo_failed");
  }

  const userInfo = (await userInfoResponse.json()) as {
    sub: string;
    email: string;
    email_verified: boolean;
    name?: string;
    picture?: string;
  };

  // ── Paso 3: encrypt tokens at rest ─────────────────────────────────
  const manusTokenEncrypted = await deps.encrypt(tokenJson.access_token);
  const manusRefreshTokenEncrypted = tokenJson.refresh_token
    ? await deps.encrypt(tokenJson.refresh_token)
    : null;

  // ── Paso 4: upsert user ────────────────────────────────────────────
  const user = await deps.db.upsertUser({
    id: userInfo.sub,
    email: userInfo.email,
    emailVerified: userInfo.email_verified,
    name: userInfo.name ?? null,
    avatarUrl: userInfo.picture ?? null,
    manusTokenEncrypted,
    manusTokenExpiresAt: new Date(Date.now() + tokenJson.expires_in * 1000),
    manusRefreshTokenEncrypted,
    lastLoginIp: req.ip,
    lastLoginUserAgent: req.userAgent,
  });

  // ── Paso 5: crear sesión ───────────────────────────────────────────
  const sessionId = crypto.randomBytes(32).toString("hex");
  const ttlSeconds = parseInt(deps.env.MONSTRUO_SESSION_TTL_SECONDS, 10);
  const expiresAt = new Date(Date.now() + ttlSeconds * 1000);

  await deps.db.createSession({
    id: sessionId,
    userId: user.id,
    expiresAt,
    ipAddress: req.ip,
    userAgent: req.userAgent,
  });

  // ── Paso 6: firmar cookie ──────────────────────────────────────────
  const payload = {
    sid: sessionId,
    uid: user.id,
    exp: Math.floor(expiresAt.getTime() / 1000),
    iat: Math.floor(Date.now() / 1000),
  };
  const sig = crypto
    .createHmac("sha256", deps.env.MONSTRUO_SESSION_SECRET)
    .update(JSON.stringify(payload))
    .digest("hex");

  const cookieValue = JSON.stringify({ ...payload, sig });

  // ── Paso 7: log + retornar ─────────────────────────────────────────
  deps.log.info("auth_login_success", { user_id: user.id, ip: req.ip });

  // Decodificar state (que era el returnTo)
  let redirectTo = "/";
  try {
    redirectTo = decodeURIComponent(req.state) || "/";
  } catch {
    redirectTo = "/";
  }

  return {
    cookieValue,
    cookieExpiresAt: expiresAt,
    redirectTo,
  };
}
