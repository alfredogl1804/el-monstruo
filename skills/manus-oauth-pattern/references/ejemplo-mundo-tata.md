# Ejemplo: Manus-Oauth en Mundo Tata (web-db-user scaffold)

> Mundo Tata es una app de tracking familiar/personal. Stack scaffold web-db-user (Vite + React + Drizzle + MySQL/TiDB + Manus-Oauth).

---

## Diferencia vs Command Center

| Aspecto | Command Center | Mundo Tata |
|---|---|---|
| Stack | Next.js 15 App Router | Vite + React Router 7 |
| Backend | Edge functions Next | Hono separado en Railway |
| DB | TiDB Cloud | MySQL 8 self-hosted |
| Auth | Cookie HTTP-only | Cookie HTTP-only (igual) |
| **Pattern Manus-Oauth** | **Idéntico** | **Idéntico** |

El skill funciona para ambos stacks. La diferencia está en cómo se monta el endpoint, no en la lógica.

---

## Estructura

```
apps/mundo-tata/
├── client/                              ← Vite + React
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.tsx                ← SignInWithManusButton
│   │   │   └── Dashboard.tsx            ← protected
│   │   ├── lib/
│   │   │   └── api.ts                   ← cliente HTTP que envía cookie
│   │   └── App.tsx
│   └── vite.config.ts
└── server/                              ← Hono backend
    ├── src/
    │   ├── routes/
    │   │   └── auth/
    │   │       ├── callback.ts
    │   │       ├── logout.ts
    │   │       └── me.ts
    │   ├── lib/
    │   │   └── auth/
    │   │       ├── middleware.ts
    │   │       └── crypto.ts
    │   └── index.ts
    └── drizzle/
        └── schema.ts
```

---

## `server/src/routes/auth/callback.ts` (Hono)

```typescript
import { Hono } from "hono";
import { setCookie } from "hono/cookie";
import { handleAuthCallback } from "../../lib/auth/callback-handler";

export const authCallback = new Hono();

authCallback.get("/", async (c) => {
  const code = c.req.query("code");
  const state = c.req.query("state");
  
  if (!code || !state) {
    return c.json(
      { error: "auth_callback_invalid_request" },
      400,
    );
  }
  
  const ip = c.req.header("x-forwarded-for")?.split(",")[0] ?? "unknown";
  const userAgent = c.req.header("user-agent") ?? "unknown";
  
  try {
    const result = await handleAuthCallback(
      { code, state, ip, userAgent },
      c.get("authDeps"),
    );
    
    setCookie(c, "monstruo_session", result.cookieValue, {
      httpOnly: true,
      secure: true,
      sameSite: "Lax",
      expires: result.cookieExpiresAt,
      path: "/",
      domain: ".tu-app.com",
    });
    
    return c.redirect(result.redirectTo);
  } catch (err: any) {
    return c.redirect(`/login?error=auth_callback_failed`);
  }
});
```

---

## `client/src/lib/api.ts`

```typescript
const API_BASE = import.meta.env.VITE_API_BASE_URL;

export const api = {
  async getMe() {
    const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
      credentials: "include", // ← clave para mandar cookie cross-origin
    });
    if (res.status === 401) throw new Error("auth_session_invalid");
    return res.json();
  },
  
  async logout() {
    await fetch(`${API_BASE}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
  },
};
```

---

## CORS (importante para split client/server)

Cuando el client está en `mundo-tata.com` y el server en `api.mundo-tata.com`, hay que configurar CORS estrictamente:

```typescript
import { cors } from "hono/cors";

app.use("/*", cors({
  origin: process.env.CLIENT_ORIGIN, // p.ej. https://mundo-tata.com
  credentials: true, // permite cookies
  allowMethods: ["GET", "POST", "PUT", "DELETE"],
  allowHeaders: ["Content-Type", "Authorization"],
}));
```

Y la cookie debe tener `domain: ".tu-app.com"` (con dot inicial) para que el browser la envíe en sub-dominios.

---

## Cuándo usar este pattern vs el de Command Center

| Caso | Recomendación |
|---|---|
| App Next.js full-stack en una sola URL | Pattern Command Center |
| Client SPA + Backend separado | Pattern Mundo Tata |
| Mobile app | Patrón distinto: deep-link OAuth (no cubierto en estos ejemplos) |
| Bot Telegram | Pattern linking (`ejemplo-bot-telegram.md`) |

---

— Hilo Catastro, Sprint Catastro-B 2026-05-06
